"""Rutas y caché de recursos (imágenes, fuentes).

Funciona igual en desarrollo, en el navegador (pygbag) y en el ejecutable de PyInstaller.
"""

from __future__ import annotations

import os
import sys

import pygame

# Carpeta raíz del juego (la que contiene main.py y assets/).
if hasattr(sys, "_MEIPASS"):  # ejecutable de PyInstaller
    RAIZ = sys._MEIPASS
else:
    RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS = os.path.join(RAIZ, "assets")

_imagenes: dict[str, pygame.Surface] = {}
_fuentes: dict[tuple[str | None, int], pygame.font.Font] = {}


def ruta(*partes: str) -> str:
    """Ruta absoluta a un archivo dentro de assets/."""
    return os.path.join(ASSETS, *partes)


def imagen(ruta_absoluta: str) -> pygame.Surface:
    """Carga una imagen (una sola vez) conservando la transparencia."""
    img = _imagenes.get(ruta_absoluta)
    if img is None:
        img = pygame.image.load(ruta_absoluta)
        if pygame.display.get_surface() is not None:
            img = img.convert_alpha()
        _imagenes[ruta_absoluta] = img
    return img


def imagen_opcional(ruta_absoluta: str) -> pygame.Surface | None:
    return imagen(ruta_absoluta) if os.path.exists(ruta_absoluta) else None


# Fuente pixel art del juego: Jersey 10 (licencia SIL OFL, ver assets/fuentes/OFL-Jersey10.txt).
FUENTE_JUEGO = "Jersey10-Regular.ttf"


def fuente(tam: int = 16, archivo: str | None = FUENTE_JUEGO) -> pygame.font.Font:
    clave = (archivo, tam)
    f = _fuentes.get(clave)
    if f is None:
        f = pygame.font.Font(ruta("fuentes", archivo) if archivo else None, tam)
        _fuentes[clave] = f
    return f
