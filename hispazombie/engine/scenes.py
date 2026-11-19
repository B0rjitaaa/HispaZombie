"""Pila de escenas.

Cada pantalla del juego (título, mapa, diálogo, menú, combate...) es una Scene.
Las escenas se apilan: solo la de arriba recibe la entrada y se actualiza, pero se
dibujan todas de abajo arriba, para que un diálogo o un menú se vean sobre el mapa.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame

    from engine.controls import Controls


class Scene:
    """Clase base de todas las escenas. Las subclases sobrescriben lo que necesiten."""

    manager: SceneManager | None = None

    def on_enter(self) -> None:
        """Se llama cuando la escena se coloca en la pila."""

    def on_exit(self) -> None:
        """Se llama cuando la escena se quita de la pila."""

    def update(self, dt: float, controls: Controls) -> None:
        """Lógica de la escena. `dt` son los segundos desde el frame anterior."""

    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja la escena en la pantalla virtual."""


class SceneManager:
    def __init__(self) -> None:
        self._stack: list[Scene] = []

    @property
    def current(self) -> Scene | None:
        return self._stack[-1] if self._stack else None

    @property
    def empty(self) -> bool:
        return not self._stack

    def __len__(self) -> int:
        return len(self._stack)

    def __iter__(self):
        return iter(self._stack)

    def push(self, scene: Scene) -> None:
        scene.manager = self
        self._stack.append(scene)
        scene.on_enter()

    def pop(self) -> Scene | None:
        if not self._stack:
            return None
        scene = self._stack.pop()
        scene.on_exit()
        scene.manager = None
        return scene

    def replace(self, scene: Scene) -> None:
        self.pop()
        self.push(scene)
