"""Menú de pausa (tecla Cancelar en el mapa) e inventario."""

from __future__ import annotations

from collections.abc import Callable

import pygame

import items
from config import HEIGHT, WIDTH
from engine import hd_text
from engine.controls import CANCEL, Controls
from engine.scenes import Scene
from engine.text import wrap
from i18n import tr
from state import game_state
from ui.choice_box import ChoiceScene
from ui.message_box import MessageScene
from ui.widgets import (
    ACCENT_COLOR,
    LINE_HEIGHT,
    PADDING,
    TEXT_COLOR,
    TEXT_SIZE,
    MenuList,
    draw_panel,
)

MARGIN = 6


def format_play_time(seconds: float) -> str:
    minutes = int(seconds) // 60
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


class PauseMenuScene(Scene):
    def __init__(self, on_save: Callable[[], bool], on_quit_to_title: Callable[[], None]) -> None:
        self.on_save = on_save
        self.on_quit_to_title = on_quit_to_title
        self.options = [
            (tr("Objetos"), self._open_inventory),
            (tr("Guardar"), self._save),
            (tr("Volver al título"), self._ask_quit),
            (tr("Cerrar"), self._close),
        ]
        self.menu = MenuList([label for label, _ in self.options])

    def update(self, dt: float, controls: Controls) -> None:
        result = self.menu.update(controls)
        if result == MenuList.CANCELLED:
            self._close()
        elif result is not None:
            self.options[result][1]()

    def _close(self) -> None:
        if self.manager:
            self.manager.pop()

    def _open_inventory(self) -> None:
        if self.manager:
            self.manager.push(InventoryScene())

    def _save(self) -> None:
        if self.on_save():
            text = tr("Partida guardada.")
        else:
            text = tr("No se ha podido guardar la partida.")
        if self.manager:
            self.manager.push(MessageScene(text))

    def _ask_quit(self) -> None:
        def chosen(index: int) -> None:
            if index == 0:
                self.on_quit_to_title()

        if self.manager:
            self.manager.push(
                ChoiceScene(
                    tr("¿Volver al título? Lo que no hayas guardado se perderá."),
                    [tr("Sí"), tr("No")],
                    chosen,
                    cancel=1,
                )
            )

    def draw(self, screen: pygame.Surface) -> None:
        width = max(self.menu.width(), 120)
        menu_rect = pygame.Rect(WIDTH - MARGIN - width, MARGIN, width, self.menu.height())
        draw_panel(screen, menu_rect)
        self.menu.draw(screen, menu_rect.x, menu_rect.y, menu_rect.width)

        info = pygame.Rect(menu_rect.x, menu_rect.bottom + 4, width, 2 * LINE_HEIGHT + 2 * PADDING)
        draw_panel(screen, info)
        x, y = info.x + PADDING, info.y + PADDING - 1
        coins = tr("Fichas: {n}").format(n=game_state.coins)
        time = tr("Tiempo: {t}").format(t=format_play_time(game_state.play_time))
        hd_text.layer.draw(coins, x, y, TEXT_SIZE, ACCENT_COLOR)
        hd_text.layer.draw(time, x, y + LINE_HEIGHT, TEXT_SIZE, TEXT_COLOR)


class InventoryScene(Scene):
    """Lista de objetos con su cantidad y la descripción del seleccionado."""

    hides_text_below = True  # ocupa toda la pantalla

    def __init__(self) -> None:
        self.item_ids = sorted(game_state.inventory, key=items.name)
        labels = [self._label(i) for i in self.item_ids] or [tr("No llevas nada.")]
        self.menu = MenuList(labels, None if self.item_ids else [False])
        self.font = hd_text.HDFont(TEXT_SIZE)

    @staticmethod
    def _label(item_id: str) -> str:
        count = game_state.item_count(item_id)
        return items.name(item_id) + (f"  x{count}" if count > 1 else "")

    def update(self, dt: float, controls: Controls) -> None:
        result = self.menu.update(controls)
        if result == MenuList.CANCELLED or (not self.item_ids and CANCEL in controls.pressed):
            if self.manager:
                self.manager.pop()

    def draw(self, screen: pygame.Surface) -> None:
        desc_height = 3 * LINE_HEIGHT + 2 * PADDING
        list_rect = pygame.Rect(
            MARGIN, MARGIN, WIDTH - 2 * MARGIN, HEIGHT - 3 * MARGIN - desc_height
        )
        draw_panel(screen, list_rect)
        hd_text.layer.draw(
            tr("Objetos"), list_rect.x + PADDING, list_rect.y + 4, TEXT_SIZE, ACCENT_COLOR
        )
        self.menu.draw(screen, list_rect.x, list_rect.y + LINE_HEIGHT, list_rect.width)

        desc_rect = pygame.Rect(MARGIN, list_rect.bottom + MARGIN, WIDTH - 2 * MARGIN, desc_height)
        draw_panel(screen, desc_rect)
        if self.item_ids:
            description = items.description(self.item_ids[self.menu.index])
            lines = wrap(description, self.font, desc_rect.width - 2 * PADDING)[:3]
            for i, line in enumerate(lines):
                hd_text.layer.draw(
                    line,
                    desc_rect.x + PADDING,
                    desc_rect.y + PADDING - 1 + i * LINE_HEIGHT,
                    TEXT_SIZE,
                    TEXT_COLOR,
                )
