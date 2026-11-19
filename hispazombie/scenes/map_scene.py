"""Escena de exploración: un mapa de Tiled con el protagonista, NPC, eventos y cámara.

Tipos de evento de la capa "events" de Tiled (campo Clase del objeto):
  * spawn    -> posición inicial si se entra al mapa sin coordenadas. Props: facing.
  * door     -> al pisarla, cambia de mapa. Props: map, target_x, target_y, facing.
  * sign     -> al pulsar Aceptar delante, muestra un texto. Props: text.
  * chest    -> se abre una vez y da un objeto. Props: id, item (id de items.json), text.
  * blocker  -> casilla infranqueable que muestra un texto al chocar. Props: text.
  * auto     -> se ejecuta una sola vez al entrar al mapa. Props: id, text o script.
  * npc      -> personaje con sprite. Se habla con él con Aceptar.
                Props: sprite (archivo de assets/sprites/ sin .png), facing, script o text.

Propiedades comunes opcionales:
  * script   -> script de eventos en assets/events/<script>.json (ver events/interpreter.py).
                Sustituye al comportamiento por defecto del tipo.
  * show_if  -> el evento solo existe si este interruptor está encendido.
  * hide_if  -> el evento desaparece si este interruptor está encendido.

Valores de "facing": up, down, left, right.
Los textos se escriben en español y se traducen con i18n.tr al mostrarlos.
"""

from __future__ import annotations

import json
from collections.abc import Callable

import pygame

import items
import saves
from config import HEIGHT, WIDTH
from engine import hd_text, resources
from engine.controls import CANCEL, CONFIRM, Controls
from engine.scenes import Scene
from events.interpreter import Choice, Interpreter, Script, Waiter
from i18n import mark, tr
from state import GameState, game_state
from ui.choice_box import ChoiceScene
from ui.message_box import MessageScene
from ui.pause_menu import PauseMenuScene
from world.camera import Camera
from world.character import Character
from world.movement import VECTORS
from world.tiled_map import ABOVE_LAYERS, MapEvent, TiledMap

SOLID_KINDS = {"sign", "chest", "blocker", "npc"}
ACTION_KINDS = {"sign", "chest", "npc"}  # se activan con Aceptar
FADE_SPEED = 700  # unidades de alfa por segundo
MAP_NAME_DURATION = 2.5  # segundos que se ve el nombre del mapa al entrar
MAP_NAME_SIZE = 11
OPPOSITE = {"up": "down", "down": "up", "left": "right", "right": "left"}


def load_script(name: str) -> Script:
    with open(resources.path("events", f"{name}.json"), encoding="utf-8") as f:
        return json.load(f)


class MapScene(Scene):
    def __init__(
        self,
        map_id: str,
        x: int | None = None,
        y: int | None = None,
        facing: str | None = None,
    ) -> None:
        self.map_id = map_id
        self.state: GameState = game_state  # EventContext
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
        self.actors = self._create_actors()
        self.camera = Camera(WIDTH, HEIGHT)

        self.interpreter: Interpreter | None = None
        self.running_event: MapEvent | None = None
        self.routes: dict[int, list[str]] = {}  # id(Character) -> pasos pendientes
        self._route_owner: dict[int, tuple[Character, MapEvent | None]] = {}

        self.fade = 255.0  # empieza en negro y aparece poco a poco
        self.fade_direction = -1
        self._teleport_target: tuple[str, int, int, str | None] | None = None
        self._last_bump: tuple[int, int] | None = None
        self.time = 0.0
        self.name_font = hd_text.HDFont(MAP_NAME_SIZE, hd_text.UI_FONT_BOLD)

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

    def _create_actors(self) -> dict[int, Character]:
        """Crea un personaje animado por cada evento "npc" (id del evento -> personaje)."""
        actors: dict[int, Character] = {}
        for event in self.map.events_of_kind("npc"):
            sheet = resources.image(resources.path("sprites", f"{event.props['sprite']}.png"))
            actor = Character(sheet, event.x, event.y, speed=3.0)
            actor.movement.facing = event.props.get("facing", "down")
            saved = self.state.event_positions.get(self._event_key(event))
            if saved:
                actor.movement.place(saved[0], saved[1], saved[2])
            actors[event.id] = actor
        return actors

    # --- Consultas sobre eventos ---

    def _event_key(self, event: MapEvent) -> str:
        return f"{self.map_id}:{event.props.get('id', event.id)}"

    def is_visible(self, event: MapEvent) -> bool:
        show_if = event.props.get("show_if")
        hide_if = event.props.get("hide_if")
        if show_if and not self.state.is_on(show_if):
            return False
        return not (hide_if and self.state.is_on(hide_if))

    def event_position(self, event: MapEvent) -> tuple[int, int]:
        actor = self.actors.get(event.id)
        if actor:
            return actor.movement.x, actor.movement.y
        return event.x, event.y

    def events_at(self, x: int, y: int) -> list[MapEvent]:
        return [
            e for e in self.map.events if self.is_visible(e) and self.event_position(e) == (x, y)
        ]

    def _is_solid_event(self, event: MapEvent) -> bool:
        if event.kind in SOLID_KINDS:
            return True
        return bool(event.gid and self.map.tile_props(event.gid).get("solid"))

    def _occupied_by_actor(self, x: int, y: int, ignore: Character | None = None) -> bool:
        """True si un NPC está en esa casilla o caminando hacia ella."""
        for event in self.map.events_of_kind("npc"):
            actor = self.actors[event.id]
            if actor is ignore or not self.is_visible(event):
                continue
            if (actor.movement.x, actor.movement.y) == (x, y):
                return True
            if actor.movement.moving and actor.movement.tile_ahead() == (x, y):
                return True
        return False

    def is_walkable(self, x: int, y: int, mover: Character | None = None) -> bool:
        if self.map.is_solid(x, y):
            return False
        if self._occupied_by_actor(x, y, ignore=mover):
            return False
        if mover is not None and mover is not self.player:
            player = self.player.movement
            if (player.x, player.y) == (x, y) or (player.moving and player.tile_ahead() == (x, y)):
                return False
        return not any(self._is_solid_event(e) for e in self.events_at(x, y) if e.kind != "npc")

    # --- Scripts de los eventos ---

    def script_for(self, event: MapEvent) -> Script:
        """Script que ejecuta un evento: el de su propiedad "script" o el de su tipo."""
        if event.props.get("script"):
            return load_script(event.props["script"])
        text = event.props.get("text", "")
        if event.kind == "chest":
            switch = f"chest:{self._event_key(event)}"
            opened: Script = [{"cmd": "switch_on", "id": switch}]
            if text:
                opened.append({"cmd": "text", "text": text})
            if event.props.get("item"):
                opened.append({"cmd": "give_item", "id": event.props["item"]})
            return [
                {
                    "cmd": "if",
                    "cond": {"switch": switch},
                    "then": [{"cmd": "text", "text": mark("Está vacío.")}],
                    "else": opened,
                }
            ]
        if event.kind == "door":
            p = event.props
            return [
                {
                    "cmd": "teleport",
                    "map": p["map"],
                    "x": p["target_x"],
                    "y": p["target_y"],
                    "facing": p.get("facing"),
                }
            ]
        return [{"cmd": "text", "text": text}] if text else []

    def run_event(self, event: MapEvent) -> None:
        script = self.script_for(event)
        if not script:
            return
        self.running_event = event
        self.interpreter = Interpreter(self, script)
        self.interpreter.update()

    # --- EventContext: lo que los scripts pueden hacer en el juego ---

    def _wait_for_message(self, text: str) -> Waiter:
        message = MessageScene(text)
        if self.manager:
            self.manager.push(message)
        return lambda: message.finished

    def show_text(self, text: str) -> Waiter:
        return self._wait_for_message(tr(text))

    def show_choice(self, prompt: str, labels: list[str], cancel: int | None) -> Choice:
        choice = Choice()

        def selected(index: int) -> None:
            choice.index = index

        if self.manager:
            self.manager.push(
                ChoiceScene(tr(prompt), [tr(label) for label in labels], selected, cancel)
            )
        return choice

    def item_obtained(self, item_id: str, amount: int) -> Waiter:
        if amount > 1:
            text = tr("Obtienes: {item} x{n}.").format(item=items.name(item_id), n=amount)
        else:
            text = tr("Obtienes: {item}.").format(item=items.name(item_id))
        return self._wait_for_message(text)

    def coins_obtained(self, amount: int) -> Waiter:
        return self._wait_for_message(tr("Obtienes {n} fichas.").format(n=amount))

    def _resolve_target(self, target: str) -> tuple[Character, MapEvent | None]:
        if target == "player":
            return self.player, None
        if target == "this":
            event = self.running_event
        else:
            event = next((e for e in self.map.events if e.name == target), None)
        if event is None or event.id not in self.actors:
            raise ValueError(f"No hay ningún NPC '{target}' en el mapa {self.map_id}")
        return self.actors[event.id], event

    def move(self, target: str, route: list[str]) -> Waiter:
        actor, event = self._resolve_target(target)
        self.routes[id(actor)] = list(route)
        self._route_owner[id(actor)] = (actor, event)
        return lambda: not self.routes.get(id(actor)) and not actor.movement.moving

    def face(self, target: str, direction: str) -> None:
        actor, event = self._resolve_target(target)
        if direction == "player":
            direction = self._direction_towards_player(actor)
        actor.movement.facing = direction
        self._remember_position(actor, event)

    def teleport(self, map_id: str, x: int, y: int, facing: str | None) -> None:
        self._teleport_target = (map_id, x, y, facing)
        self.fade_direction = 1

    # --- Movimiento de personajes por scripts ---

    def _direction_towards_player(self, actor: Character) -> str:
        dx = self.player.movement.x - actor.movement.x
        dy = self.player.movement.y - actor.movement.y
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        return "down" if dy > 0 else "up"

    def _remember_position(self, actor: Character, event: MapEvent | None) -> None:
        """Guarda en la partida dónde ha quedado un NPC movido por un script."""
        if event is not None:
            m = actor.movement
            self.state.event_positions[self._event_key(event)] = [m.x, m.y, m.facing]

    def _update_routes(self) -> None:
        for key in list(self.routes):
            actor, event = self._route_owner[key]
            route = self.routes[key]
            if actor.movement.moving:
                continue
            if not route:
                del self.routes[key]
                self._remember_position(actor, event)
                continue
            step = route.pop(0)
            if step in VECTORS:
                # Si el paso está bloqueado, el personaje se gira y se salta ese paso.
                actor.movement.try_move(step, lambda x, y, a=actor: self.is_walkable(x, y, a))

    # --- Bucle ---

    def update(self, dt: float, controls: Controls) -> None:
        self.time += dt
        self.state.play_time += dt

        if self.fade_direction:
            self.fade += self.fade_direction * FADE_SPEED * dt
            if self.fade <= 0:
                self.fade, self.fade_direction = 0.0, 0
            elif self.fade >= 255:
                self.fade = 255.0
                self._change_map()
            return

        for actor in self.actors.values():
            actor.movement.update(dt)
        self._update_routes()

        movement = self.player.movement
        if self.interpreter is not None:
            movement.update(dt)  # termina el paso en curso si lo había
            self.interpreter.update()
            if self.interpreter.done:
                self.interpreter = None
                self.running_event = None
            return

        if self._run_auto_events():
            return

        if movement.update(dt):
            self._last_bump = None
            if self._on_step(movement.x, movement.y):
                return

        if movement.moving:
            return

        if CONFIRM in controls.pressed:
            self._interact(*movement.tile_ahead())
            return

        if CANCEL in controls.pressed:
            self._open_pause_menu()
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
            switch = f"auto:{self._event_key(event)}"
            if self.is_visible(event) and not self.state.is_on(switch):
                self.state.turn_on(switch)
                self.run_event(event)
                return True
        return False

    def _on_step(self, x: int, y: int) -> bool:
        for event in self.events_at(x, y):
            if event.kind == "door":
                self.run_event(event)
                return True
        return False

    def _on_bump(self, x: int, y: int) -> None:
        for event in self.events_at(x, y):
            if event.kind == "blocker":
                self.run_event(event)
                return
        text = self.map.bump_text(x, y)
        if text:
            self.show_text(text)

    def _interact(self, x: int, y: int) -> None:
        for event in self.events_at(x, y):
            if event.kind in ACTION_KINDS:
                actor = self.actors.get(event.id)
                if actor:  # el NPC se gira hacia el jugador, como en RPG Maker
                    actor.movement.facing = OPPOSITE[self.player.movement.facing]
                self.run_event(event)
                return

    def _open_pause_menu(self) -> None:
        if self.manager:
            self.manager.push(PauseMenuScene(self.save, self._quit_to_title))

    def save(self) -> bool:
        m = self.player.movement
        self.state.map_id = self.map_id
        self.state.player_x, self.state.player_y, self.state.player_facing = m.x, m.y, m.facing
        return saves.save_game()

    def _quit_to_title(self) -> None:
        from scenes.title_scene import TitleScene  # import aquí para evitar un ciclo

        manager = self.manager
        if manager is None:
            return
        while len(manager) > 0:
            manager.pop()
        manager.push(TitleScene())

    def _change_map(self) -> None:
        target = self._teleport_target
        if target is None or self.manager is None:
            self.fade_direction = -1
            return
        self.manager.replace(MapScene(*target))

    # --- Dibujo ---

    def draw(self, screen: pygame.Surface) -> None:
        width_px = self.map.width * self.tile
        height_px = self.map.height * self.tile
        self.camera.follow(*self.player.center_px(self.tile), width_px, height_px)
        cx, cy = self.camera.x, self.camera.y

        screen.fill((0, 0, 0))
        screen.blit(self.layer_below, (-cx, -cy))

        # Eventos con gráfico, NPC y jugador, ordenados por fila para que se solapen bien.
        drawables: list[tuple[float, Callable[[], None]]] = []
        for event in self.map.events:
            if not self.is_visible(event):
                continue
            actor = self.actors.get(event.id)
            if actor:
                drawables.append(
                    (
                        actor.movement.visual_position()[1],
                        lambda a=actor: a.draw(screen, cx, cy, self.tile),
                    )
                )
            elif event.gid:
                drawables.append((event.y, lambda e=event: self._draw_event(screen, e, cx, cy)))
        drawables.append(
            (
                self.player.movement.visual_position()[1] + 0.01,
                lambda: self.player.draw(screen, cx, cy, self.tile),
            )
        )
        for _, draw in sorted(drawables, key=lambda d: d[0]):
            draw()

        screen.blit(self.layer_above, (-cx, -cy))
        self._draw_map_name(screen)

        if self.fade > 0:
            veil = pygame.Surface((WIDTH, HEIGHT))
            veil.set_alpha(int(self.fade))
            screen.blit(veil, (0, 0))

    def _draw_event(self, screen: pygame.Surface, event: MapEvent, cx: int, cy: int) -> None:
        gid = event.gid
        if event.kind == "chest" and self.state.is_on(f"chest:{self._event_key(event)}"):
            open_id = self.map.tile_props(gid).get("open_id")
            ts = self.map.tileset_for(gid)
            if open_id is not None and ts:
                gid = ts.firstgid + open_id
        self._draw_tile(screen, gid, event.x * self.tile - cx, event.y * self.tile - cy)

    def _draw_map_name(self, screen: pygame.Surface) -> None:
        if self.time > MAP_NAME_DURATION:
            return
        name = tr(self.map.name)
        w, h = self.name_font.size(name)
        box = pygame.Rect(8, 8, int(w) + 14, int(h) + 6)
        background = pygame.Surface(box.size, pygame.SRCALPHA)
        background.fill((20, 22, 40, 200))
        screen.blit(background, box.topleft)
        pygame.draw.rect(screen, (230, 220, 190), box, 1)
        # El texto HD va por encima de todo: se atenúa a la vez que el fundido de entrada.
        alpha = int(255 - self.fade)
        hd_text.layer.draw(
            name, box.x + 7, box.y + 3, MAP_NAME_SIZE, (245, 240, 225), alpha, hd_text.UI_FONT_BOLD
        )
