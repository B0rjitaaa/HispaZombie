"""Caja de mensajes estilo RPG Maker: texto letra a letra, retrato opcional y páginas."""

from __future__ import annotations

from collections.abc import Callable

import pygame

from config import HEIGHT, WIDTH
from engine import hd_text, resources
from engine.controls import CANCEL, CONFIRM, Controls
from engine.scenes import Scene
from engine.text import Page, pages_from, wrap
from ui.widgets import BORDER_COLOR, LINE_HEIGHT, PADDING, TEXT_COLOR, TEXT_SIZE, draw_panel

# Medidas en píxeles virtuales. El texto se dibuja en HD (ver engine/hd_text.py).
LINES_PER_PAGE = 4
MARGIN = 6
BOX_HEIGHT = 2 * PADDING + LINES_PER_PAGE * LINE_HEIGHT
PORTRAIT_SIZE = 48
LETTERS_PER_SECOND = 45


def box_rect() -> pygame.Rect:
    return pygame.Rect(MARGIN, HEIGHT - BOX_HEIGHT - MARGIN, WIDTH - 2 * MARGIN, BOX_HEIGHT)


def text_width(portrait: str | None) -> int:
    width = WIDTH - 2 * MARGIN - 2 * PADDING
    if portrait:
        width -= PORTRAIT_SIZE + PADDING
    return width


def paginate(text: str, font: hd_text.HDFont) -> list[tuple[Page, list[str]]]:
    """Parte el texto en páginas de como mucho LINES_PER_PAGE líneas."""
    result: list[tuple[Page, list[str]]] = []
    for page in pages_from(text):
        lines = wrap(page.text, font, text_width(page.portrait))
        for i in range(0, max(len(lines), 1), LINES_PER_PAGE):
            result.append((page, lines[i : i + LINES_PER_PAGE]))
    return result


def draw_page(
    screen: pygame.Surface, page: Page, lines: list[str], letters: int | None = None
) -> pygame.Rect:
    """Dibuja la caja con una página. `letters` limita las letras visibles (efecto máquina)."""
    box = box_rect()
    draw_panel(screen, box)
    x = box.x + PADDING
    if page.portrait:
        img = resources.optional_image(resources.path("portraits", f"{page.portrait}.png"))
        if img:
            screen.blit(img, (x, box.y + (BOX_HEIGHT - PORTRAIT_SIZE) // 2))
        x += PORTRAIT_SIZE + PADDING

    remaining = letters if letters is not None else sum(len(line) for line in lines)
    y = box.y + PADDING - 1
    for line in lines:
        if remaining <= 0:
            break
        hd_text.layer.draw(line[:remaining], x, y, TEXT_SIZE, TEXT_COLOR)
        remaining -= len(line)
        y += LINE_HEIGHT
    return box


class MessageScene(Scene):
    """Se apila encima del mapa. Al terminar todas las páginas se quita sola.

    El texto debe llegar ya traducido (ver i18n.tr).
    """

    def __init__(self, text: str, on_finish: Callable[[], None] | None = None) -> None:
        self.font = hd_text.HDFont(TEXT_SIZE)
        self.on_finish = on_finish
        self.pages = paginate(text, self.font)
        self.index = 0
        self.letters = 0.0
        self.time = 0.0
        self.finished = False

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
        self.finished = True
        if self.manager:
            self.manager.pop()
        if self.on_finish:
            self.on_finish()

    def draw(self, screen: pygame.Surface) -> None:
        if not self.pages:
            return
        page, lines = self.pages[self.index]
        box = draw_page(screen, page, lines, int(self.letters))

        # Flechita parpadeante cuando la página está completa.
        if self.letters >= self._total_letters and int(self.time * 3) % 2 == 0:
            ax, ay = box.right - 12, box.bottom - 9
            pygame.draw.polygon(screen, BORDER_COLOR, [(ax, ay), (ax + 6, ay), (ax + 3, ay + 4)])
