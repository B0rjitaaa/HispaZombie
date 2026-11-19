"""Pila de escenas.

Cada pantalla del juego (título, mapa, diálogo, menú, combate...) es una Escena.
Las escenas se apilan: solo la de arriba recibe la entrada y se actualiza, pero se
dibujan todas de abajo arriba, para que un diálogo o un menú se vean sobre el mapa.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame

    from engine.entrada import Entrada


class Escena:
    """Clase base de todas las escenas. Las subclases sobrescriben lo que necesiten."""

    gestor: GestorEscenas | None = None

    def al_entrar(self) -> None:
        """Se llama cuando la escena se coloca en la pila."""

    def al_salir(self) -> None:
        """Se llama cuando la escena se quita de la pila."""

    def actualizar(self, dt: float, entrada: Entrada) -> None:
        """Lógica de la escena. `dt` son los segundos desde el frame anterior."""

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja la escena en la pantalla virtual de 320x240."""


class GestorEscenas:
    def __init__(self) -> None:
        self._pila: list[Escena] = []

    @property
    def actual(self) -> Escena | None:
        return self._pila[-1] if self._pila else None

    @property
    def vacia(self) -> bool:
        return not self._pila

    def __len__(self) -> int:
        return len(self._pila)

    def __iter__(self):
        return iter(self._pila)

    def apilar(self, escena: Escena) -> None:
        escena.gestor = self
        self._pila.append(escena)
        escena.al_entrar()

    def desapilar(self) -> Escena | None:
        if not self._pila:
            return None
        escena = self._pila.pop()
        escena.al_salir()
        escena.gestor = None
        return escena

    def reemplazar(self, escena: Escena) -> None:
        self.desapilar()
        self.apilar(escena)
