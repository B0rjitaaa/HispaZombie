"""Escena de combate: el enemigo de frente, las barras y el menú de acciones.

La lógica está en battle/engine.py; esta escena solo muestra lo que pasa y recoge las
decisiones del jugador. Al terminar llama a on_end("win" | "lose" | "fled").
"""

from __future__ import annotations

import math
from collections.abc import Callable

import pygame

import items
from battle import data
from battle.engine import STATUS_NAMES, Battle, BattleEvent
from config import HEIGHT, WIDTH
from engine import hd_text, resources
from engine.controls import CANCEL, CONFIRM, Controls
from engine.scenes import Scene
from engine.text import wrap
from i18n import tr
from state import game_state
from ui.message_box import box_rect
from ui.widgets import (
    ACCENT_COLOR,
    LINE_HEIGHT,
    PADDING,
    TEXT_COLOR,
    TEXT_SIZE,
    MenuList,
    draw_bar,
    draw_panel,
    hp_color,
)

AUTO_ADVANCE = 1.4  # segundos que se ve cada mensaje si no se pulsa nada
BAR_SPEED = 40  # puntos por segundo a los que se mueven las barras
FLASH_TIME = 0.35
FADE_SPEED = 600
CAFFEINE_COLOR = (150, 110, 70)


class BattleScene(Scene):
    hides_text_below = True  # el combate ocupa toda la pantalla

    def __init__(
        self,
        enemy_id: str,
        level: int,
        on_end: Callable[[str], None],
        can_flee: bool = True,
        battle: Battle | None = None,
    ) -> None:
        self.battle = battle or Battle(game_state, enemy_id, level, can_flee)
        self.on_end = on_end
        self.enemy_image = resources.image(resources.path("battlers", f"{enemy_id}.png"))
        self.font = hd_text.HDFont(TEXT_SIZE)

        b = self.battle
        self.shown_player_hp = float(b.player.hp)
        self.shown_caffeine = float(b.player.caffeine)
        self.shown_enemy_hp = float(b.enemy.hp)

        self.queue: list[BattleEvent] = [b.start_message()]
        self.current: BattleEvent | None = None
        self.message_time = 0.0
        self.phase = "messages"  # messages | command | skills | items | ending
        self.menu: MenuList | None = None
        self.menu_ids: list[str] = []
        self.flash_enemy = 0.0
        self.shake = 0.0
        self.time = 0.0
        self.fade = 255.0
        self.fade_direction = -1
        self._next_message()

    # --- Flujo ---

    def _next_message(self) -> None:
        if self.queue:
            self.current = self.queue.pop(0)
            self.message_time = 0.0
            if self.current.hit == "enemy":
                self.flash_enemy = FLASH_TIME
            elif self.current.hit == "player":
                self.shake = FLASH_TIME
            self.phase = "messages"
            return
        self.current = None
        if self.battle.outcome:
            self.phase = "ending"
            self.fade_direction = 1
        elif self.battle.player_must_skip:
            self._play(("skip",))
        else:
            self._open_command_menu()

    def _play(self, action: tuple) -> None:
        self.queue = self.battle.play_turn(action)
        self._next_message()

    def _open_command_menu(self) -> None:
        self.phase = "command"
        labels = [tr("Habilidades"), tr("Objetos"), tr("Huir")]
        self.menu = MenuList(labels, [True, True, self.battle.can_flee])

    def _open_skills(self) -> None:
        skills = self.battle.player.skills
        self.phase = "skills"
        self.menu_ids = list(skills)
        self.menu = MenuList(
            [data.skill_name(s) for s in skills],
            [self.battle.can_use_skill(s) for s in skills],
            [self.battle.skill_cost_label(s) for s in skills],
        )

    def _open_items(self) -> None:
        usable = [i for i in sorted(game_state.inventory, key=items.name) if items.is_usable(i)]
        self.phase = "items"
        self.menu_ids = usable
        if usable:
            labels = [items.name(i) for i in usable]
            counts = [f"x{game_state.item_count(i)}" for i in usable]
            self.menu = MenuList(labels, right_labels=counts)
        else:
            self.menu = MenuList([tr("No tienes nada que usar.")], [False])

    def update(self, dt: float, controls: Controls) -> None:
        self.time += dt
        self.flash_enemy = max(0.0, self.flash_enemy - dt)
        self.shake = max(0.0, self.shake - dt)
        self._animate_bars(dt)

        if self.fade_direction:
            self.fade += self.fade_direction * FADE_SPEED * dt
            if self.fade <= 0:
                self.fade, self.fade_direction = 0.0, 0
            elif self.fade >= 255:
                self._finish()
            return

        if self.phase == "messages":
            self.message_time += dt
            bars_done = self._bars_settled()
            pressed = CONFIRM in controls.pressed or CANCEL in controls.pressed
            if bars_done and (pressed or self.message_time >= AUTO_ADVANCE):
                self._next_message()
        elif self.phase == "command":
            choice = self.menu.update(controls)
            if choice == 0:
                self._open_skills()
            elif choice == 1:
                self._open_items()
            elif choice == 2:
                self._play(("flee",))
        elif self.phase == "skills":
            choice = self.menu.update(controls)
            if choice == MenuList.CANCELLED:
                self._open_command_menu()
            elif choice is not None:
                self._play(("skill", self.menu_ids[choice]))
        elif self.phase == "items":
            choice = self.menu.update(controls)
            if choice == MenuList.CANCELLED or (not self.menu_ids and CANCEL in controls.pressed):
                self._open_command_menu()
            elif choice is not None and self.menu_ids:
                self._play(("item", self.menu_ids[choice]))

    def _finish(self) -> None:
        if self.manager:
            self.manager.pop()
        self.on_end(self.battle.outcome or "fled")

    # --- Barras animadas ---

    def _targets(self) -> tuple[float, float, float]:
        event = self.current
        if event is None:
            b = self.battle
            return b.player.hp, b.player.caffeine, b.enemy.hp
        return event.player_hp, event.player_caffeine, event.enemy_hp

    def _animate_bars(self, dt: float) -> None:
        player_hp, caffeine, enemy_hp = self._targets()
        step = BAR_SPEED * dt

        def approach(value: float, target: float) -> float:
            if abs(target - value) <= step:
                return float(target)
            return value + step if target > value else value - step

        self.shown_player_hp = approach(self.shown_player_hp, player_hp)
        self.shown_caffeine = approach(self.shown_caffeine, caffeine)
        self.shown_enemy_hp = approach(self.shown_enemy_hp, enemy_hp)

    def _bars_settled(self) -> bool:
        player_hp, caffeine, enemy_hp = self._targets()
        return (
            self.shown_player_hp == player_hp
            and self.shown_caffeine == caffeine
            and self.shown_enemy_hp == enemy_hp
        )

    # --- Dibujo ---

    def draw(self, screen: pygame.Surface) -> None:
        offset = 0
        if self.shake > 0:
            offset = round(math.sin(self.time * 80) * 3)
        self._draw_background(screen, offset)
        self._draw_enemy(screen, offset)
        self._draw_enemy_hud(screen)
        self._draw_player_hud(screen)
        self._draw_bottom(screen)
        if self.fade > 0:
            veil = pygame.Surface((WIDTH, HEIGHT))
            veil.set_alpha(int(self.fade))
            screen.blit(veil, (0, 0))

    def _draw_background(self, screen: pygame.Surface, offset: int) -> None:
        for y in range(HEIGHT):  # cielo con degradado: de ceniza oscura a verde radiactivo
            t = y / HEIGHT
            color = (int(28 + 30 * t), int(26 + 46 * t), int(34 + 20 * t))
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))
        ground = pygame.Rect(0, 150, WIDTH, HEIGHT - 150)
        pygame.draw.rect(screen, (92, 76, 56), ground)
        pygame.draw.ellipse(screen, (70, 58, 44), (WIDTH // 2 - 90 + offset, 140, 180, 28))

    def _draw_enemy(self, screen: pygame.Surface, offset: int) -> None:
        if self.battle.outcome == "win" and self.current is None:
            return
        image = pygame.transform.scale(self.enemy_image, (128, 128))
        # Parpadeo al recibir daño; desaparece al morir.
        if self.flash_enemy > 0 and int(self.flash_enemy * 20) % 2 == 0:
            return
        if self.shown_enemy_hp <= 0 and self._bars_settled():
            return
        bob = round(math.sin(self.time * 3) * 2)
        screen.blit(image, (WIDTH // 2 - 64 + offset, 30 + bob))

    def _draw_enemy_hud(self, screen: pygame.Surface) -> None:
        enemy = self.battle.enemy
        rect = pygame.Rect(8, 8, 180, 40)
        draw_panel(screen, rect)
        hd_text.layer.draw(enemy.name, rect.x + PADDING, rect.y + 4, TEXT_SIZE, TEXT_COLOR)
        level = tr("Nv {n}").format(n=enemy.level)
        lw = self.font.size(level)[0]
        hd_text.layer.draw(level, rect.right - PADDING - lw, rect.y + 4, TEXT_SIZE, ACCENT_COLOR)
        bar = pygame.Rect(rect.x + PADDING, rect.y + 24, rect.width - 2 * PADDING, 7)
        draw_bar(
            screen,
            bar,
            self.shown_enemy_hp,
            enemy.max_hp,
            hp_color(self.shown_enemy_hp, enemy.max_hp),
        )
        self._draw_statuses(screen, enemy.statuses, rect.x, rect.bottom + 2)

    def _draw_player_hud(self, screen: pygame.Surface) -> None:
        player = self.battle.player
        box = box_rect()
        rect = pygame.Rect(WIDTH - 8 - 200, box.top - 4 - 54, 200, 54)
        draw_panel(screen, rect)
        hd_text.layer.draw(player.name, rect.x + PADDING, rect.y + 3, TEXT_SIZE, TEXT_COLOR)
        level = tr("Nv {n}").format(n=player.level)
        lw = self.font.size(level)[0]
        hd_text.layer.draw(level, rect.right - PADDING - lw, rect.y + 3, TEXT_SIZE, ACCENT_COLOR)

        label_w = 54
        for i, (label, shown, maximum, color) in enumerate(
            (
                (
                    tr("Vida"),
                    self.shown_player_hp,
                    player.max_hp,
                    hp_color(self.shown_player_hp, player.max_hp),
                ),
                (tr("Cafeína"), self.shown_caffeine, player.max_caffeine, CAFFEINE_COLOR),
            )
        ):
            y = rect.y + 20 + i * 15
            hd_text.layer.draw(label, rect.x + PADDING, y - 2, 10, TEXT_COLOR)
            bar = pygame.Rect(rect.x + PADDING + label_w, y + 2, 80, 6)
            draw_bar(screen, bar, shown, maximum, color)
            numbers = f"{round(shown)}/{maximum}"
            hd_text.layer.draw(numbers, bar.right + 6, y - 2, 10, TEXT_COLOR)
        self._draw_statuses(screen, player.statuses, rect.x, rect.top - 16)

    def _draw_statuses(self, screen: pygame.Surface, statuses: dict, x: int, y: int) -> None:
        for status in statuses:
            label = tr(STATUS_NAMES[status])
            w = int(self.font.size(label)[0] * 10 / TEXT_SIZE) + 10
            rect = pygame.Rect(x, y, w, 14)
            pygame.draw.rect(screen, (120, 50, 120), rect)
            pygame.draw.rect(screen, (230, 220, 190), rect, 1)
            hd_text.layer.draw(label, rect.x + 5, rect.y + 1, 10, TEXT_COLOR)
            x += w + 4

    def _draw_bottom(self, screen: pygame.Surface) -> None:
        box = box_rect()
        draw_panel(screen, box)
        x, y = box.x + PADDING, box.y + PADDING - 1

        if self.phase == "messages" and self.current:
            for i, line in enumerate(
                wrap(self.current.text, self.font, box.width - 2 * PADDING)[:4]
            ):
                hd_text.layer.draw(line, x, y + i * LINE_HEIGHT, TEXT_SIZE, TEXT_COLOR)
            return
        if self.menu is None or self.phase == "ending":
            return

        if self.phase == "command":
            hd_text.layer.draw(tr("¿Qué vas a hacer?"), x, y, TEXT_SIZE, TEXT_COLOR)
            width = max(self.menu.width(), 130)
            rect = pygame.Rect(box.right - width, box.y, width, box.height)
            self.menu.draw(screen, rect.x, rect.y - 2, rect.width)
            pygame.draw.line(screen, (230, 220, 190), (rect.x, box.y + 4), (rect.x, box.bottom - 5))
            return

        # Habilidades u objetos: lista a la izquierda, descripción a la derecha.
        list_width = max(self.menu.width(), 200)
        visible = 4
        start = max(0, min(self.menu.index - visible + 1, len(self.menu.labels) - visible))
        sub = MenuList(
            self.menu.labels[start : start + visible],
            self.menu.enabled[start : start + visible],
            self.menu.right_labels[start : start + visible] if self.menu.right_labels else None,
        )
        sub.index = self.menu.index - start
        sub.draw(screen, box.x, box.y - 2, list_width)
        if start + visible < len(self.menu.labels):  # flechita: hay más opciones debajo
            ax, ay = box.x + list_width - 12, box.bottom - 8
            pygame.draw.polygon(screen, ACCENT_COLOR, [(ax, ay), (ax + 6, ay), (ax + 3, ay + 4)])
        sep = box.x + list_width
        pygame.draw.line(screen, (230, 220, 190), (sep, box.y + 4), (sep, box.bottom - 5))
        self._draw_description(box, sep)

    def _draw_description(self, box: pygame.Rect, sep: int) -> None:
        if not self.menu_ids:
            return
        selected = self.menu_ids[self.menu.index]
        x = sep + PADDING
        width = box.right - x - PADDING
        if self.phase == "skills":
            s = data.skill(selected)
            info = data.type_name(s["type"])
            if s.get("power"):
                info += "  ·  " + tr("Potencia {n}").format(n=s["power"])
            hd_text.layer.draw(info, x, box.y + PADDING - 1, 10, ACCENT_COLOR)
            text = tr(s["description"])
        else:
            text = items.description(selected)
        lines = wrap(text, hd_text.HDFont(10), width)[:4]
        for i, line in enumerate(lines):
            hd_text.layer.draw(line, x, box.y + PADDING + 13 + i * 13, 10, TEXT_COLOR)
