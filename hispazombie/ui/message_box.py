"""Caja de mensajes estilo RPG Maker: texto letra a letra, retrato opcional y páginas."""

from __future__ import annotations

from collections.abc import Callable

import pygame

from config import HEIGHT, WIDTH
from engine import hd_text, resources
from engine.controls import CANCEL, CONFIRM, Controls
from engine.scenes import Scene
from engine.text import Page, pages_from, wrap

# Medidas en píxeles virtuales. El texto se dibuja en HD (ver engine/hd_text.py).
TEXT_SIZE = 12
LINE_HEIGHT = 15
LINES_PER_PAGE = 4
MARGIN = 6
PADDING = 8
BOX_HEIGHT = 2 * PADDING + LINES_PER_PAGE * LINE_HEIGHT
PORTRAIT_SIZE = 48
LETTERS_PER_SECOND = 45

BACKGROUND_COLOR = (20, 22, 40, 230)
BORDER_COLOR = (230, 220, 190)
TEXT_COLOR = (245, 240, 225)


class MessageScene(Scene):
    """Se apila encima del mapa. Al terminar todas las páginas se quita sola.

    El texto debe llegar ya traducido (ver i18n.tr).
    """

    def __init__(self, text: str, on_finish: Callable[[], None] | None = None) -> None:
        self.font = hd_text.HDFont(TEXT_SIZE)
        self.on_finish = on_finish
        self.pages = self._paginate(pages_from(text))
        self.index = 0
        self.letters = 0.0
        self.time = 0.0

    def _text_width(self, page: Page) -> int:
        width = WIDTH - 2 * MARGIN - 2 * PADDING
        if page.portrait:
            width -= PORTRAIT_SIZE + PADDING
        return width

    def _paginate(self, pages: list[Page]) -> list[tuple[Page, list[str]]]:
        """Parte cada página en líneas y, si no caben en la caja, en varias páginas."""
        result: list[tuple[Page, list[str]]] = []
        for page in pages:
            lines = wrap(page.text, self.font, self._text_width(page))
            for i in range(0, max(len(lines), 1), LINES_PER_PAGE):
                result.append((page, lines[i : i + LINES_PER_PAGE]))
        return result

    @property
    def _total_letters(self) -> int:
        _, lines = self.pages[self.index]
        return sum(len(line) for line in lines)

    def update(self, dt: float, controls: Controls) -> None:
        self.time += dt
        if not self.pages:
            self._close()
            return
        complete = self.letters >= self._total_letters
        if not complete:
            self.letters += LETTERS_PER_SECOND * dt
        if CONFIRM in controls.pressed or CANCEL in controls.pressed:
            if not complete:
                self.letters = self._total_letters  # mostrar la página entera de golpe
            elif self.index + 1 < len(self.pages):
                self.index += 1
                self.letters = 0.0
            else:
                self._close()

    def _close(self) -> None:
        if self.manager:
            self.manager.pop()
        if self.on_finish:
            self.on_finish()

    def draw(self, screen: pygame.Surface) -> None:
        if not self.pages:
            return
        page, lines = self.pages[self.index]
        box = pygame.Rect(MARGIN, HEIGHT - BOX_HEIGHT - MARGIN, WIDTH - 2 * MARGIN, BOX_HEIGHT)

        background = pygame.Surface(box.size, pygame.SRCALPHA)
        background.fill(BACKGROUND_COLOR)
        screen.blit(background, box.topleft)
        pygame.draw.rect(screen, BORDER_COLOR, box, 1)

        x = box.x + PADDING
        if page.portrait:
            img = resources.optional_image(resources.path("portraits", f"{page.portrait}.png"))
            if img:
                screen.blit(img, (x, box.y + (BOX_HEIGHT - PORTRAIT_SIZE) // 2))
            x += PORTRAIT_SIZE + PADDING

        remaining = int(self.letters)
        y = box.y + PADDING - 1
        for line in lines:
            if remaining <= 0:
                break
            hd_text.layer.draw(line[:remaining], x, y, TEXT_SIZE, TEXT_COLOR)
            remaining -= len(line)
            y += LINE_HEIGHT

        # Flechita parpadeante cuando la página está completa.
        if self.letters >= self._total_letters and int(self.time * 3) % 2 == 0:
            ax, ay = box.right - 12, box.bottom - 9
            pygame.draw.polygon(screen, BORDER_COLOR, [(ax, ay), (ax + 6, ay), (ax + 3, ay + 4)])
