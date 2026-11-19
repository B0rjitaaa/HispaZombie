"""Caja de mensajes estilo RPG Maker: texto letra a letra, retrato opcional y páginas."""

from __future__ import annotations

from collections.abc import Callable

import pygame

from config import ALTO, ANCHO
from engine import recursos
from engine.entrada import ACEPTAR, CANCELAR, Entrada
from engine.escenas import Escena
from engine.texto import Pagina, envolver, paginas_de

ALTO_CAJA = 72
MARGEN = 6
RELLENO = 8
TAM_RETRATO = 48
LETRAS_POR_SEGUNDO = 45
LINEAS_POR_PAGINA = 4
ALTO_LINEA = 13

COLOR_FONDO = (20, 22, 40, 230)
COLOR_BORDE = (230, 220, 190)
COLOR_TEXTO = (245, 240, 225)


class EscenaMensaje(Escena):
    """Se apila encima del mapa. Al terminar todas las páginas se quita sola."""

    def __init__(self, texto: str, al_terminar: Callable[[], None] | None = None) -> None:
        self.fuente = recursos.fuente(16)
        self.al_terminar = al_terminar
        self.paginas = self._paginar(paginas_de(texto))
        self.indice = 0
        self.letras = 0.0
        self.tiempo = 0.0

    def _ancho_texto(self, pagina: Pagina) -> int:
        ancho = ANCHO - 2 * MARGEN - 2 * RELLENO
        if pagina.retrato:
            ancho -= TAM_RETRATO + RELLENO
        return ancho

    def _paginar(self, paginas: list[Pagina]) -> list[tuple[Pagina, list[str]]]:
        """Parte cada página en líneas y, si no caben en la caja, en varias páginas."""
        resultado: list[tuple[Pagina, list[str]]] = []
        for pagina in paginas:
            lineas = envolver(pagina.texto, self.fuente, self._ancho_texto(pagina))
            for i in range(0, max(len(lineas), 1), LINEAS_POR_PAGINA):
                resultado.append((pagina, lineas[i : i + LINEAS_POR_PAGINA]))
        return resultado

    @property
    def _total_letras(self) -> int:
        _, lineas = self.paginas[self.indice]
        return sum(len(linea) for linea in lineas)

    def actualizar(self, dt: float, entrada: Entrada) -> None:
        self.tiempo += dt
        if not self.paginas:
            self._cerrar()
            return
        completa = self.letras >= self._total_letras
        if not completa:
            self.letras += LETRAS_POR_SEGUNDO * dt
        if ACEPTAR in entrada.pulsadas or CANCELAR in entrada.pulsadas:
            if not completa:
                self.letras = self._total_letras  # mostrar la página entera de golpe
            elif self.indice + 1 < len(self.paginas):
                self.indice += 1
                self.letras = 0.0
            else:
                self._cerrar()

    def _cerrar(self) -> None:
        if self.gestor:
            self.gestor.desapilar()
        if self.al_terminar:
            self.al_terminar()

    def dibujar(self, pantalla: pygame.Surface) -> None:
        if not self.paginas:
            return
        pagina, lineas = self.paginas[self.indice]
        caja = pygame.Rect(MARGEN, ALTO - ALTO_CAJA - MARGEN, ANCHO - 2 * MARGEN, ALTO_CAJA)

        fondo = pygame.Surface(caja.size, pygame.SRCALPHA)
        fondo.fill(COLOR_FONDO)
        pantalla.blit(fondo, caja.topleft)
        pygame.draw.rect(pantalla, COLOR_BORDE, caja, 1)

        x = caja.x + RELLENO
        if pagina.retrato:
            img = recursos.imagen_opcional(recursos.ruta("retratos", f"{pagina.retrato}.png"))
            if img:
                pantalla.blit(img, (x, caja.y + (ALTO_CAJA - TAM_RETRATO) // 2))
            x += TAM_RETRATO + RELLENO

        restantes = int(self.letras)
        y = caja.y + RELLENO - 2
        for linea in lineas:
            if restantes <= 0:
                break
            visible = linea[:restantes]
            restantes -= len(linea)
            pantalla.blit(self.fuente.render(visible, False, COLOR_TEXTO), (x, y))
            y += ALTO_LINEA

        # Flechita parpadeante cuando la página está completa.
        if self.letras >= self._total_letras and int(self.tiempo * 3) % 2 == 0:
            ax, ay = caja.right - 12, caja.bottom - 9
            pygame.draw.polygon(pantalla, COLOR_BORDE, [(ax, ay), (ax + 6, ay), (ax + 3, ay + 4)])
