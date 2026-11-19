"""Punto de entrada de HispaZombie.

Escritorio:  uv run python hispazombie/main.py
Navegador:   uv run pygbag hispazombie   (y abrir http://localhost:8000)
"""

import asyncio

from config import ALTO, ANCHO, FPS, TITULO
from engine.juego import Juego
from escenas.prueba import EscenaPrueba


async def main() -> None:
    juego = Juego(TITULO, ANCHO, ALTO, FPS)
    await juego.ejecutar(EscenaPrueba())


# pygbag necesita que el juego arranque con asyncio.run(main()) al final de main.py.
asyncio.run(main())
