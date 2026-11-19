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


def dim_screen(screen: pygame.Surface, alpha: int = 170) -> None:
    """Oscurece todo lo que hay detrás (para pantallas de menú a pantalla completa)."""
    veil = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    veil.fill((0, 0, 0, alpha))
    screen.blit(veil, (0, 0))


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

    def __init__(
        self,
        labels: list[str],
        enabled: list[bool] | None = None,
        right_labels: list[str] | None = None,
    ) -> None:
        self.labels = labels
        self.enabled = enabled or [True] * len(labels)
        self.right_labels = right_labels  # texto alineado a la derecha (p. ej. el coste)
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
        if self.right_labels:
            widest += max(self.font.size(r)[0] for r in self.right_labels) + 16
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
            if self.right_labels and self.right_labels[i]:
                right = self.right_labels[i]
                rw = self.font.size(right)[0]
                hd_text.layer.draw(right, x + width - PADDING - rw, row_y - 1, TEXT_SIZE, color)


def draw_bar(
    screen: pygame.Surface,
    rect: pygame.Rect,
    value: float,
    maximum: float,
    color: tuple[int, int, int],
) -> None:
    """Barra de vida o cafeína con fondo oscuro y borde."""
    pygame.draw.rect(screen, (30, 30, 36), rect)
    if maximum > 0 and value > 0:
        filled = max(1, round((rect.width - 2) * min(value, maximum) / maximum))
        pygame.draw.rect(screen, color, (rect.x + 1, rect.y + 1, filled, rect.height - 2))
    pygame.draw.rect(screen, (10, 10, 14), rect, 1)


def hp_color(value: float, maximum: float) -> tuple[int, int, int]:
    """Verde, amarillo o rojo según la vida que quede."""
    ratio = value / maximum if maximum else 0
    if ratio > 0.5:
        return (90, 200, 90)
    if ratio > 0.2:
        return (230, 190, 60)
    return (220, 70, 60)
