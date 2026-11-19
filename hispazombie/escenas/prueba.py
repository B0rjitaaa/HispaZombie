"""Escena de prueba de la Fase 0.

Comprueba que funcionan la ventana escalada, el bucle, la entrada y el movimiento en
cuadrícula, en escritorio y en navegador. Se sustituirá por el búnker en la Fase 1.
"""

from __future__ import annotations

import pygame

from config import ALTO, ANCHO, TILE
from engine.entrada import Entrada
from engine.escenas import Escena
from mundo.movimiento import MovimientoCuadricula

COLUMNAS = ANCHO // TILE
FILAS = ALTO // TILE

COLOR_FONDO = (34, 28, 26)
COLOR_REJILLA = (52, 44, 40)
COLOR_MURO = (96, 84, 72)
COLOR_JUGADOR = (120, 200, 90)
COLOR_OJOS = (20, 20, 20)
COLOR_TEXTO = (235, 220, 190)

# Mapa de prueba: '#' muro, '.' suelo. 20x15 casillas.
MAPA = [
    "####################",
    "#..................#",
    "#..................#",
    "#...####......##...#",
    "#...#..........#...#",
    "#...#..........#...#",
    "#..................#",
    "#........##........#",
    "#........##........#",
    "#..................#",
    "#...#..........#...#",
    "#...####......##...#",
    "#..................#",
    "#..................#",
    "####################",
]


def es_transitable(x: int, y: int) -> bool:
    if not (0 <= x < COLUMNAS and 0 <= y < FILAS):
        return False
    return MAPA[y][x] != "#"


class EscenaPrueba(Escena):
    def __init__(self) -> None:
        self.jugador = MovimientoCuadricula(x=2, y=2)
        self.fuente = pygame.font.Font(None, 16)

    def actualizar(self, dt: float, entrada: Entrada) -> None:
        # Primero se termina el paso en curso y luego se encadena el siguiente en el mismo
        # frame, para que andar con la tecla mantenida no dé tirones.
        self.jugador.actualizar(dt)
        direccion = entrada.direccion()
        if direccion:
            self.jugador.intentar_mover(direccion, es_transitable)

    def dibujar(self, pantalla: pygame.Surface) -> None:
        pantalla.fill(COLOR_FONDO)
        for y, fila in enumerate(MAPA):
            for x, celda in enumerate(fila):
                rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                if celda == "#":
                    pygame.draw.rect(pantalla, COLOR_MURO, rect)
                else:
                    pygame.draw.rect(pantalla, COLOR_REJILLA, rect, 1)

        vx, vy = self.jugador.posicion_visual()
        rect = pygame.Rect(round(vx * TILE) + 2, round(vy * TILE) + 2, TILE - 4, TILE - 4)
        pygame.draw.rect(pantalla, COLOR_JUGADOR, rect)
        self._dibujar_ojos(pantalla, rect)

        texto = self.fuente.render("HispaZombie - Fase 0", False, COLOR_TEXTO)
        pantalla.blit(texto, (TILE + 2, 3))

    def _dibujar_ojos(self, pantalla: pygame.Surface, rect: pygame.Rect) -> None:
        """Dos puntos que indican hacia dónde mira el personaje."""
        cx, cy = rect.center
        desplazamientos = {
            "abajo": ((-2, 1), (2, 1)),
            "arriba": ((-2, -3), (2, -3)),
            "izquierda": ((-4, -1), (-4, 2)),
            "derecha": ((3, -1), (3, 2)),
        }
        for ox, oy in desplazamientos[self.jugador.mirando]:
            pantalla.fill(COLOR_OJOS, (cx + ox, cy + oy, 2, 2))
