"""Escena de exploración: un mapa de Tiled con el protagonista, eventos y cámara.

Tipos de evento soportados en la capa "events" de Tiled (campo Clase del objeto):
  * spawn    -> posición inicial si se entra al mapa sin coordenadas. Props: facing.
  * door     -> al pisarla, cambia de mapa. Props: map, target_x, target_y, facing.
  * sign     -> al pulsar Aceptar delante, muestra un texto. Props: text.
  * chest    -> se abre una vez y da un objeto. Props: id, item (id de items.json), text.
  * blocker  -> casilla infranqueable que muestra un texto al chocar. Props: text.
  * auto     -> texto que se muestra una sola vez al entrar al mapa. Props: id, text.

Valores de "facing": up, down, left, right.
Los textos se escriben en español y se traducen con i18n.tr al mostrarlos.
En la Fase 2 estos tipos se sustituirán por el intérprete de eventos genérico.
"""

from __future__ import annotations

import pygame

import items
from config import HEIGHT, WIDTH
from engine import resources
from engine.controls import CONFIRM, Controls
from engine.scenes import Scene
from i18n import tr
from state import game_state
from ui.message_box import MessageScene
from world.camera import Camera
from world.character import Character
from world.tiled_map import ABOVE_LAYERS, MapEvent, TiledMap

SOLID_KINDS = {"sign", "chest", "blocker"}
FADE_SPEED = 700  # unidades de alfa por segundo
MAP_NAME_DURATION = 2.5  # segundos que se ve el nombre del mapa al entrar


class MapScene(Scene):
    def __init__(
        self,
        map_id: str,
        x: int | None = None,
        y: int | None = None,
        facing: str | None = None,
    ) -> None:
        self.map_id = map_id
        self.map = TiledMap(resources.path("maps", f"{map_id}.tmj"))
        self.tile = self.map.tile
        self.layer_below, self.layer_above = self._prerender()

        if x is None or y is None:
            spawn = next(iter(self.map.events_of_kind("spawn")), None)
            x, y = (spawn.x, spawn.y) if spawn else (0, 0)
            facing = facing or (spawn.props.get("facing") if spawn else None)

        sheet = resources.image(resources.path("sprites", "intern.png"))
        self.player = Character(sheet, x, y)
        self.player.movement.facing = facing or "down"
        self.camera = Camera(WIDTH, HEIGHT)

        self.fade = 255.0  # empieza en negro y aparece poco a poco
        self.fade_direction = -1
        self._pending_door: MapEvent | None = None
        self._last_bump: tuple[int, int] | None = None
        self.time = 0.0
        self.font = resources.font(16)

    # --- Preparación ---

    def _prerender(self) -> tuple[pygame.Surface, pygame.Surface]:
        """Dibuja una sola vez las capas de tiles en dos superficies grandes."""
        size = (self.map.width * self.tile, self.map.height * self.tile)
        below = pygame.Surface(size, pygame.SRCALPHA)
        above = pygame.Surface(size, pygame.SRCALPHA)
        for layer in self.map.layers:
            if not layer.visible:
                continue
            target = above if layer.name in ABOVE_LAYERS else below
            for i, gid in enumerate(layer.data):
                if gid:
                    x = (i % self.map.width) * self.tile
                    y = (i // self.map.width) * self.tile
                    self._draw_tile(target, gid, x, y)
        return below, above

    def _draw_tile(self, target: pygame.Surface, gid: int, x: int, y: int) -> None:
        ts = self.map.tileset_for(gid)
        if ts is None:
            return
        target.blit(resources.image(ts.image), (x, y), ts.source_rect(gid))

    # --- Reglas del mundo ---

    def _chest_switch(self, event: MapEvent) -> str:
        return f"chest:{self.map_id}:{event.props.get('id', event.id)}"

    def _is_solid_event(self, event: MapEvent) -> bool:
        if event.kind in SOLID_KINDS:
            return True
        return bool(event.gid and self.map.tile_props(event.gid).get("solid"))

    def is_walkable(self, x: int, y: int) -> bool:
        if self.map.is_solid(x, y):
            return False
        return not any(self._is_solid_event(e) for e in self.map.events_at(x, y))

    def show(self, text: str) -> None:
        """Muestra un texto (escrito en español) traducido al idioma activo."""
        if self.manager and text:
            self.manager.push(MessageScene(tr(text)))

    # --- Bucle ---

    def update(self, dt: float, controls: Controls) -> None:
        self.time += dt

        if self.fade_direction:
            self.fade += self.fade_direction * FADE_SPEED * dt
            if self.fade <= 0:
                self.fade, self.fade_direction = 0.0, 0
            elif self.fade >= 255:
                self.fade = 255.0
                self._change_map()
            return

        if self._run_auto_events():
            return

        movement = self.player.movement
        if movement.update(dt):
            self._last_bump = None
            if self._on_step(movement.x, movement.y):
                return

        if movement.moving:
            return

        if CONFIRM in controls.pressed:
            self._interact(*movement.tile_ahead())
            return

        direction = controls.direction()
        if direction and not movement.try_move(direction, self.is_walkable):
            target = movement.tile_ahead()
            # Solo se avisa una vez por obstáculo, salvo que se vuelva a pulsar la tecla.
            if direction in controls.pressed or target != self._last_bump:
                self._last_bump = target
                self._on_bump(*target)

    def _run_auto_events(self) -> bool:
        for event in self.map.events_of_kind("auto"):
            switch = f"auto:{self.map_id}:{event.props.get('id', event.id)}"
            if not game_state.is_on(switch):
                game_state.turn_on(switch)
                self.show(event.props.get("text", ""))
                return True
        return False

    def _on_step(self, x: int, y: int) -> bool:
        for event in self.map.events_at(x, y):
            if event.kind == "door":
                self._pending_door = event
                self.fade_direction = 1
                return True
        return False

    def _on_bump(self, x: int, y: int) -> None:
        for event in self.map.events_at(x, y):
            if event.kind == "blocker":
                self.show(event.props.get("text", ""))
                return
        text = self.map.bump_text(x, y)
        if text:
            self.show(text)

    def _interact(self, x: int, y: int) -> None:
        for event in self.map.events_at(x, y):
            if event.kind == "sign":
                self.show(event.props.get("text", ""))
                return
            if event.kind == "chest":
                self._open_chest(event)
                return

    def _open_chest(self, event: MapEvent) -> None:
        switch = self._chest_switch(event)
        if game_state.is_on(switch):
            self.show("Está vacío.")
            return
        game_state.turn_on(switch)
        text = tr(event.props.get("text", ""))
        item_id = event.props.get("item")
        if item_id:
            game_state.give_item(item_id)
            obtained = tr("Obtienes: {item}.").format(item=items.name(item_id))
            text = f"{text}\n\n{obtained}" if text else obtained
        if self.manager:
            self.manager.push(MessageScene(text))

    def _change_map(self) -> None:
        event = self._pending_door
        if event is None or self.manager is None:
            self.fade_direction = -1
            return
        self.manager.replace(
            MapScene(
                event.props["map"],
                event.props.get("target_x"),
                event.props.get("target_y"),
                event.props.get("facing"),
            )
        )

    # --- Dibujo ---

    def draw(self, screen: pygame.Surface) -> None:
        width_px = self.map.width * self.tile
        height_px = self.map.height * self.tile
        self.camera.follow(*self.player.center_px(self.tile), width_px, height_px)
        cx, cy = self.camera.x, self.camera.y

        screen.fill((0, 0, 0))
        screen.blit(self.layer_below, (-cx, -cy))

        # Eventos con gráfico y jugador, ordenados por fila para que se solapen bien.
        player_y = self.player.movement.visual_position()[1]
        drawable = sorted((e for e in self.map.events if e.gid), key=lambda e: e.y)
        for event in drawable:
            if event.y <= player_y:
                self._draw_event(screen, event, cx, cy)
        self.player.draw(screen, cx, cy, self.tile)
        for event in drawable:
            if event.y > player_y:
                self._draw_event(screen, event, cx, cy)

        screen.blit(self.layer_above, (-cx, -cy))
        self._draw_map_name(screen)

        if self.fade > 0:
            veil = pygame.Surface((WIDTH, HEIGHT))
            veil.set_alpha(int(self.fade))
            screen.blit(veil, (0, 0))

    def _draw_event(self, screen: pygame.Surface, event: MapEvent, cx: int, cy: int) -> None:
        gid = event.gid
        if event.kind == "chest" and game_state.is_on(self._chest_switch(event)):
            open_id = self.map.tile_props(gid).get("open_id")
            ts = self.map.tileset_for(gid)
            if open_id is not None and ts:
                gid = ts.firstgid + open_id
        self._draw_tile(screen, gid, event.x * self.tile - cx, event.y * self.tile - cy)

    def _draw_map_name(self, screen: pygame.Surface) -> None:
        if self.time > MAP_NAME_DURATION:
            return
        label = self.font.render(tr(self.map.name), False, (245, 240, 225))
        box = label.get_rect(topleft=(8, 8)).inflate(12, 6)
        background = pygame.Surface(box.size, pygame.SRCALPHA)
        background.fill((20, 22, 40, 200))
        screen.blit(background, box.topleft)
        pygame.draw.rect(screen, (230, 220, 190), box, 1)
        screen.blit(label, (box.x + 6, box.y + 3))
