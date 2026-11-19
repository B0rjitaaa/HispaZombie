"""Personaje con sprite animado al estilo RPG Maker (3 frames x 4 direcciones)."""

from __future__ import annotations

import pygame

from world.movement import GridMovement

# Fila de la hoja de sprites para cada dirección (orden de RPG Maker).
ROWS = {"down": 0, "left": 1, "right": 2, "up": 3}


class Character:
    def __init__(
        self,
        sheet: pygame.Surface,
        x: int,
        y: int,
        frame_width: int = 16,
        frame_height: int = 24,
        speed: float = 4.0,
    ) -> None:
        self.sheet = sheet
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.movement = GridMovement(x, y, speed)

    def current_frame(self) -> int:
        """Frame 1 = quieto. Al andar: pie izquierdo (0) o derecho (2) en la primera mitad
        del paso, alternando en cada paso, y vuelta a 1 en la segunda mitad."""
        if not self.movement.moving or self.movement.progress >= 0.5:
            return 1
        return 0 if self.movement.steps % 2 == 0 else 2

    def draw(self, screen: pygame.Surface, cam_x: int, cam_y: int, tile: int) -> None:
        vx, vy = self.movement.visual_position()
        source = pygame.Rect(
            self.current_frame() * self.frame_width,
            ROWS[self.movement.facing] * self.frame_height,
            self.frame_width,
            self.frame_height,
        )
        # Los pies quedan en la parte de abajo de la casilla; la cabeza sobresale por arriba.
        px = round(vx * tile) + (tile - self.frame_width) // 2 - cam_x
        py = round(vy * tile) + tile - self.frame_height - cam_y
        screen.blit(self.sheet, (px, py), source)

    def center_px(self, tile: int) -> tuple[float, float]:
        vx, vy = self.movement.visual_position()
        return vx * tile + tile / 2, vy * tile + tile / 2
