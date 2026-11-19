"""Caja de opciones: una pregunta (opcional) en la caja de mensajes y la lista de respuestas."""

from __future__ import annotations

from collections.abc import Callable

import pygame

from config import HEIGHT, WIDTH
from engine import hd_text
from engine.controls import Controls
from engine.scenes import Scene
from ui.message_box import MARGIN, box_rect, draw_page, paginate
from ui.widgets import TEXT_SIZE, MenuList, draw_panel


class ChoiceScene(Scene):
    """Los textos deben llegar ya traducidos. Llama a on_select(índice) al elegir."""

    def __init__(
        self,
        prompt: str,
        labels: list[str],
        on_select: Callable[[int], None],
        cancel: int | None = None,
    ) -> None:
        self.menu = MenuList(labels)
        self.on_select = on_select
        self.cancel = cancel
        # Si la pregunta ocupa varias páginas, se muestra la última (la que pregunta).
        pages = paginate(prompt, hd_text.HDFont(TEXT_SIZE)) if prompt else []
        self.prompt_page = pages[-1] if pages else None

    def update(self, dt: float, controls: Controls) -> None:
        result = self.menu.update(controls)
        if result is None:
            return
        if result == MenuList.CANCELLED:
            if self.cancel is None:
                return
            result = self.cancel
        if self.manager:
            self.manager.pop()
        self.on_select(result)

    def draw(self, screen: pygame.Surface) -> None:
        bottom = HEIGHT - MARGIN
        if self.prompt_page:
            draw_page(screen, *self.prompt_page)
            bottom = box_rect().top - 4
        width = self.menu.width()
        height = self.menu.height()
        rect = pygame.Rect(WIDTH - MARGIN - width, bottom - height, width, height)
        draw_panel(screen, rect)
        self.menu.draw(screen, rect.x, rect.y, rect.width)
