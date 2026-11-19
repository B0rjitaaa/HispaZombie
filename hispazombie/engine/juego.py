"""Bucle principal del juego, compatible con escritorio y con navegador (pygbag)."""

from __future__ import annotations

import asyncio
import sys

import pygame

from engine.entrada import Entrada
from engine.escenas import Escena, GestorEscenas

EN_NAVEGADOR = sys.platform == "emscripten"

# Fracción máxima del escritorio que puede ocupar la ventana (deja sitio a barras y bordes).
MARGEN_ESCRITORIO = 0.85


def escala_entera(ancho: int, alto: int, disponible: tuple[int, int]) -> int:
    """Mayor factor entero que hace caber ancho x alto en el espacio disponible (mínimo 1)."""
    return max(1, min(disponible[0] // ancho, disponible[1] // alto))


class Juego:
    def __init__(self, titulo: str, ancho: int, alto: int, fps: int) -> None:
        pygame.init()
        pygame.display.set_caption(titulo)
        self.ancho = ancho
        self.alto = alto
        self.fps = fps

        # Todo se dibuja en esta pantalla virtual de 320x240 y luego se escala a la ventana
        # con un factor entero y sin suavizado, para que el pixel art se vea nítido.
        self.pantalla = pygame.Surface((ancho, alto))
        self.pantalla_completa = False
        self.ventana = self._crear_ventana()

        self.reloj = pygame.time.Clock()
        self.escenas = GestorEscenas()
        self.entrada = Entrada()
        self.activo = True

    def _crear_ventana(self) -> pygame.Surface:
        if EN_NAVEGADOR:
            # pygbag ajusta el canvas al tamaño de la página.
            return pygame.display.set_mode((self.ancho * 3, self.alto * 3))
        if self.pantalla_completa:
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        escritorio = pygame.display.get_desktop_sizes()[0]
        disponible = (
            int(escritorio[0] * MARGEN_ESCRITORIO),
            int(escritorio[1] * MARGEN_ESCRITORIO),
        )
        escala = escala_entera(self.ancho, self.alto, disponible)
        return pygame.display.set_mode((self.ancho * escala, self.alto * escala), pygame.RESIZABLE)

    def alternar_pantalla_completa(self) -> None:
        if EN_NAVEGADOR:
            return
        self.pantalla_completa = not self.pantalla_completa
        self.ventana = self._crear_ventana()

    def salir(self) -> None:
        self.activo = False

    def _presentar(self) -> None:
        """Escala la pantalla virtual a la ventana, centrada y con bandas negras."""
        tam_ventana = self.ventana.get_size()
        escala = escala_entera(self.ancho, self.alto, tam_ventana)
        tam = (self.ancho * escala, self.alto * escala)
        x = (tam_ventana[0] - tam[0]) // 2
        y = (tam_ventana[1] - tam[1]) // 2
        self.ventana.fill((0, 0, 0))
        self.ventana.blit(pygame.transform.scale(self.pantalla, tam), (x, y))
        pygame.display.flip()

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
                elif evento.type == pygame.KEYDOWN and (
                    evento.key == pygame.K_F11
                    or (evento.key == pygame.K_RETURN and evento.mod & pygame.KMOD_ALT)
                ):
                    self.alternar_pantalla_completa()
                else:
                    self.entrada.procesar(evento)

            escena = self.escenas.actual
            if escena is not None:
                escena.actualizar(dt, self.entrada)

            self.pantalla.fill((0, 0, 0))
            for escena in self.escenas:
                escena.dibujar(self.pantalla)
            self._presentar()

            # Imprescindible para pygbag: devuelve el control al navegador cada frame.
            await asyncio.sleep(0)

        pygame.quit()
