"""Cámara que sigue al personaje sin salirse de los bordes del mapa."""

from __future__ import annotations


def _eje(centro: float, vista: int, mapa: int) -> int:
    if mapa <= vista:
        # Mapa más pequeño que la pantalla: se centra (desplazamiento negativo).
        return -((vista - mapa) // 2)
    return int(round(min(max(centro - vista / 2, 0), mapa - vista)))


class Camara:
    def __init__(self, ancho_vista: int, alto_vista: int) -> None:
        self.ancho_vista = ancho_vista
        self.alto_vista = alto_vista
        self.x = 0
        self.y = 0

    def seguir(self, cx: float, cy: float, ancho_mapa: int, alto_mapa: int) -> None:
        """Centra la cámara en (cx, cy), en píxeles, limitada al tamaño del mapa en píxeles."""
        self.x = _eje(cx, self.ancho_vista, ancho_mapa)
        self.y = _eje(cy, self.alto_vista, alto_mapa)
