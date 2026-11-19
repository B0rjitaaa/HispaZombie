"""Piezas de interfaz reutilizables: paneles y listas con cursor."""

from __future__ import annotations

import pygame

from engine import hd_text
from engine.controls import CANCEL, CONFIRM, DOWN, UP, Controls

PANEL_COLOR = (20, 22, 40, 230)
BORDER_COLOR = (230, 220, 190)
TEXT_COLOR = (245, 240, 225)
DISABLED_COLOR = (130, 128, 140)
HIGHLIGHT_COLOR = (70, 74, 120, 255)
ACCENT_COLOR = (255, 214, 120)

TEXT_SIZE = 12
LINE_HEIGHT = 15
PADDING = 8


def draw_panel(screen: pygame.Surface, rect: pygame.Rect) -> None:
    """Panel semitransparente con borde, estilo RPG Maker."""
    background = pygame.Surface(rect.size, pygame.SRCALPHA)
    background.fill(PANEL_COLOR)
    screen.blit(background, rect.topleft)
    pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class MenuList:
    """Lista vertical de opciones con cursor.

    update() devuelve el índice elegido al pulsar Aceptar, CANCELLED al pulsar Cancelar
    o None si no ha pasado nada. Las opciones deshabilitadas se ven en gris y no se eligen.
    """

    CANCELLED = -1

    def __init__(self, labels: list[str], enabled: list[bool] | None = None) -> None:
        self.labels = labels
        self.enabled = enabled or [True] * len(labels)
        self.index = 0
        self.font = hd_text.HDFont(TEXT_SIZE)
        if not self.enabled[self.index]:
            self._move(1)

    def _move(self, step: int) -> None:
        if not any(self.enabled):
            return
        for _ in range(len(self.labels)):
            self.index = (self.index + step) % len(self.labels)
            if self.enabled[self.index]:
                return

    def update(self, controls: Controls) -> int | None:
        if UP in controls.pressed:
            self._move(-1)
        elif DOWN in controls.pressed:
            self._move(1)
        elif CONFIRM in controls.pressed and self.labels and self.enabled[self.index]:
            return self.index
        elif CANCEL in controls.pressed:
            return self.CANCELLED
        return None

    def width(self) -> int:
        """Ancho necesario (en píxeles virtuales) para la opción más larga."""
        widest = max((self.font.size(label)[0] for label in self.labels), default=0)
        return int(widest) + 2 * PADDING + 10

    def height(self) -> int:
        return len(self.labels) * LINE_HEIGHT + 2 * PADDING

    def draw(self, screen: pygame.Surface, x: int, y: int, width: int) -> None:
        """Dibuja las opciones dentro de un rectángulo que empieza en (x, y)."""
        for i, label in enumerate(self.labels):
            row_y = y + PADDING + i * LINE_HEIGHT
            if i == self.index:
                highlight = pygame.Surface((width - 4, LINE_HEIGHT), pygame.SRCALPHA)
                highlight.fill(HIGHLIGHT_COLOR)
                screen.blit(highlight, (x + 2, row_y - 1))
                cx, cy = x + 5, row_y + LINE_HEIGHT // 2 - 1
                pygame.draw.polygon(
                    screen, ACCENT_COLOR, [(cx, cy - 3), (cx + 4, cy), (cx, cy + 3)]
                )
            color = TEXT_COLOR if self.enabled[i] else DISABLED_COLOR
            hd_text.layer.draw(label, x + PADDING + 6, row_y - 1, TEXT_SIZE, color)
