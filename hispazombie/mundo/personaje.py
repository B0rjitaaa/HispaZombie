"""Personaje con sprite animado al estilo RPG Maker (3 frames x 4 direcciones)."""

from __future__ import annotations

import pygame

from mundo.movimiento import MovimientoCuadricula

FILAS = {"abajo": 0, "izquierda": 1, "derecha": 2, "arriba": 3}


class Personaje:
    def __init__(
        self,
        hoja: pygame.Surface,
        x: int,
        y: int,
        ancho_frame: int = 16,
        alto_frame: int = 24,
        velocidad: float = 4.0,
    ) -> None:
        self.hoja = hoja
        self.ancho_frame = ancho_frame
        self.alto_frame = alto_frame
        self.mov = MovimientoCuadricula(x, y, velocidad)

    def frame_actual(self) -> int:
        """Frame 1 = quieto. Al andar: pie izquierdo (0) o derecho (2) en la primera mitad
        del paso, alternando en cada paso, y vuelta a 1 en la segunda mitad."""
        if not self.mov.moviendose or self.mov.progreso >= 0.5:
            return 1
        return 0 if self.mov.pasos % 2 == 0 else 2

    def dibujar(self, pantalla: pygame.Surface, cam_x: int, cam_y: int, tile: int) -> None:
        vx, vy = self.mov.posicion_visual()
        origen = pygame.Rect(
            self.frame_actual() * self.ancho_frame,
            FILAS[self.mov.mirando] * self.alto_frame,
            self.ancho_frame,
            self.alto_frame,
        )
        # Los pies quedan en la parte de abajo de la casilla; la cabeza sobresale por arriba.
        px = round(vx * tile) + (tile - self.ancho_frame) // 2 - cam_x
        py = round(vy * tile) + tile - self.alto_frame - cam_y
        pantalla.blit(self.hoja, (px, py), origen)

    def centro_px(self, tile: int) -> tuple[float, float]:
        vx, vy = self.mov.posicion_visual()
        return vx * tile + tile / 2, vy * tile + tile / 2
