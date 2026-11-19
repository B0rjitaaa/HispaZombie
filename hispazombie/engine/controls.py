"""Traduce teclas a acciones del juego.

El resto del código pregunta por acciones ("confirm", "up"...) y no por teclas,
así se pueden añadir mando o controles táctiles sin tocar las escenas.
"""

from __future__ import annotations

import pygame

UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"
CONFIRM = "confirm"
CANCEL = "cancel"

DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

KEY_MAP: dict[int, str] = {
    pygame.K_UP: UP,
    pygame.K_w: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_s: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_a: LEFT,
    pygame.K_RIGHT: RIGHT,
    pygame.K_d: RIGHT,
    pygame.K_z: CONFIRM,
    pygame.K_RETURN: CONFIRM,
    pygame.K_SPACE: CONFIRM,
    pygame.K_x: CANCEL,
    pygame.K_ESCAPE: CANCEL,
}


def action_for_key(key: int) -> str | None:
    return KEY_MAP.get(key)


class Controls:
    """Estado de las acciones en el frame actual."""

    def __init__(self) -> None:
        self.held: set[str] = set()  # mantenidas
        self.pressed: set[str] = set()  # pulsadas en este frame
        # Orden en que se pulsaron las direcciones: la última manda (como en RPG Maker).
        self._direction_order: list[str] = []

    def new_frame(self) -> None:
        """Se llama al principio de cada frame, antes de procesar eventos."""
        self.pressed.clear()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            action = action_for_key(event.key)
            if action:
                self.press(action)
        elif event.type == pygame.KEYUP:
            action = action_for_key(event.key)
            if action:
                self.release(action)

    def press(self, action: str) -> None:
        if action not in self.held:
            self.pressed.add(action)
        self.held.add(action)
        if action in DIRECTIONS:
            if action in self._direction_order:
                self._direction_order.remove(action)
            self._direction_order.append(action)

    def release(self, action: str) -> None:
        self.held.discard(action)
        if action in self._direction_order:
            self._direction_order.remove(action)

    def release_all(self) -> None:
        """Al perder el foco la ventana, para que el personaje no siga andando solo."""
        self.held.clear()
        self._direction_order.clear()

    def direction(self) -> str | None:
        """Dirección mantenida más reciente, o None."""
        return self._direction_order[-1] if self._direction_order else None
