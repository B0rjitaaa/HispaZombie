"""Bucle principal del juego, compatible con escritorio y con navegador (pygbag)."""

from __future__ import annotations

import asyncio

import pygame

from engine.entrada import Entrada
from engine.escenas import Escena, GestorEscenas


class Juego:
    def __init__(self, titulo: str, ancho: int, alto: int, fps: int) -> None:
        pygame.init()
        pygame.display.set_caption(titulo)
        # SCALED: dibujamos a 320x240 y pygame escala la ventana a un múltiplo entero,
        # sin suavizado (píxeles nítidos). En el navegador, pygbag escala el canvas.
        self.pantalla = pygame.display.set_mode((ancho, alto), pygame.SCALED)
        self.reloj = pygame.time.Clock()
        self.fps = fps
        self.escenas = GestorEscenas()
        self.entrada = Entrada()
        self.activo = True

    def salir(self) -> None:
        self.activo = False

    async def ejecutar(self, escena_inicial: Escena) -> None:
        self.escenas.apilar(escena_inicial)

        while self.activo and not self.escenas.vacia:
            dt = self.reloj.tick(self.fps) / 1000
            # Evita saltos enormes si la ventana estuvo congelada (p. ej. arrastrándola).
            dt = min(dt, 0.1)

            self.entrada.nuevo_frame()
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.salir()
                elif evento.type == pygame.WINDOWFOCUSLOST:
                    self.entrada.soltar_todo()
                else:
                    self.entrada.procesar(evento)

            escena = self.escenas.actual
            if escena is not None:
                escena.actualizar(dt, self.entrada)

            self.pantalla.fill((0, 0, 0))
            for escena in self.escenas:
                escena.dibujar(self.pantalla)
            pygame.display.flip()

            # Imprescindible para pygbag: devuelve el control al navegador cada frame.
            await asyncio.sleep(0)

        pygame.quit()
