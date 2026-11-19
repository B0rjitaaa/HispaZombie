"""Cámara que sigue al personaje sin salirse de los bordes del mapa."""

from __future__ import annotations


def _axis(center: float, view: int, world: int) -> int:
    if world <= view:
        # Mapa más pequeño que la pantalla: se centra (desplazamiento negativo).
        return -((view - world) // 2)
    return int(round(min(max(center - view / 2, 0), world - view)))


class Camera:
    def __init__(self, view_width: int, view_height: int) -> None:
        self.view_width = view_width
        self.view_height = view_height
        self.x = 0
        self.y = 0

    def follow(self, cx: float, cy: float, world_width: int, world_height: int) -> None:
        """Centra la cámara en (cx, cy), en píxeles, limitada al tamaño del mapa en píxeles."""
        self.x = _axis(cx, self.view_width, world_width)
        self.y = _axis(cy, self.view_height, world_height)
