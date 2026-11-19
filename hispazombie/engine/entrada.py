"""Traduce teclas a acciones del juego.

El resto del código pregunta por acciones ("aceptar", "arriba"...) y no por teclas,
así se pueden añadir mando o controles táctiles sin tocar las escenas.
"""

from __future__ import annotations

import pygame

ARRIBA = "arriba"
ABAJO = "abajo"
IZQUIERDA = "izquierda"
DERECHA = "derecha"
ACEPTAR = "aceptar"
CANCELAR = "cancelar"

DIRECCIONES = (ARRIBA, ABAJO, IZQUIERDA, DERECHA)

MAPA_TECLAS: dict[int, str] = {
    pygame.K_UP: ARRIBA,
    pygame.K_w: ARRIBA,
    pygame.K_DOWN: ABAJO,
    pygame.K_s: ABAJO,
    pygame.K_LEFT: IZQUIERDA,
    pygame.K_a: IZQUIERDA,
    pygame.K_RIGHT: DERECHA,
    pygame.K_d: DERECHA,
    pygame.K_z: ACEPTAR,
    pygame.K_RETURN: ACEPTAR,
    pygame.K_SPACE: ACEPTAR,
    pygame.K_x: CANCELAR,
    pygame.K_ESCAPE: CANCELAR,
}


def accion_de_tecla(tecla: int) -> str | None:
    return MAPA_TECLAS.get(tecla)


class Entrada:
    """Estado de las acciones en el frame actual."""

    def __init__(self) -> None:
        self.mantenidas: set[str] = set()
        self.pulsadas: set[str] = set()
        # Orden en que se pulsaron las direcciones: la última manda (como en RPG Maker).
        self._orden_direcciones: list[str] = []

    def nuevo_frame(self) -> None:
        """Se llama al principio de cada frame, antes de procesar eventos."""
        self.pulsadas.clear()

    def procesar(self, evento: pygame.event.Event) -> None:
        if evento.type == pygame.KEYDOWN:
            accion = accion_de_tecla(evento.key)
            if accion:
                self.pulsar(accion)
        elif evento.type == pygame.KEYUP:
            accion = accion_de_tecla(evento.key)
            if accion:
                self.soltar(accion)

    def pulsar(self, accion: str) -> None:
        if accion not in self.mantenidas:
            self.pulsadas.add(accion)
        self.mantenidas.add(accion)
        if accion in DIRECCIONES:
            if accion in self._orden_direcciones:
                self._orden_direcciones.remove(accion)
            self._orden_direcciones.append(accion)

    def soltar(self, accion: str) -> None:
        self.mantenidas.discard(accion)
        if accion in self._orden_direcciones:
            self._orden_direcciones.remove(accion)

    def soltar_todo(self) -> None:
        """Al perder el foco la ventana, para que el personaje no siga andando solo."""
        self.mantenidas.clear()
        self._orden_direcciones.clear()

    def direccion(self) -> str | None:
        """Dirección mantenida más reciente, o None."""
        return self._orden_direcciones[-1] if self._orden_direcciones else None
