"""Rutas y caché de recursos (imágenes, fuentes).

Funciona igual en desarrollo, en el navegador (pygbag) y en el ejecutable de PyInstaller.
"""

from __future__ import annotations

import os
import sys

import pygame

# Carpeta raíz del juego (la que contiene main.py y assets/).
if hasattr(sys, "_MEIPASS"):  # ejecutable de PyInstaller
    ROOT = sys._MEIPASS
else:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS = os.path.join(ROOT, "assets")

_images: dict[str, pygame.Surface] = {}
_fonts: dict[tuple[str | None, int], pygame.font.Font] = {}


def path(*parts: str) -> str:
    """Ruta absoluta a un archivo dentro de assets/."""
    return os.path.join(ASSETS, *parts)


def image(absolute_path: str) -> pygame.Surface:
    """Carga una imagen (una sola vez) conservando la transparencia."""
    img = _images.get(absolute_path)
    if img is None:
        img = pygame.image.load(absolute_path)
        if pygame.display.get_surface() is not None:
            img = img.convert_alpha()
        _images[absolute_path] = img
    return img


def optional_image(absolute_path: str) -> pygame.Surface | None:
    return image(absolute_path) if os.path.exists(absolute_path) else None


def font(size: int, filename: str | None = None) -> pygame.font.Font:
    """Fuente de assets/fonts/ (o la de pygame si filename es None), guardada en caché."""
    key = (filename, size)
    f = _fonts.get(key)
    if f is None:
        f = pygame.font.Font(path("fonts", filename) if filename else None, size)
        _fonts[key] = f
    return f
