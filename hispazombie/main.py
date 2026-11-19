"""Punto de entrada de HispaZombie.

Escritorio:  uv run python hispazombie/main.py
Navegador:   uv run pygbag hispazombie   (y abrir http://localhost:8000)
"""

import asyncio

import i18n
from config import FPS, HEIGHT, LANGUAGE, TITLE, WIDTH
from engine import resources
from engine.game import Game
from scenes.map_scene import MapScene


async def main() -> None:
    i18n.set_language(LANGUAGE, resources.path("i18n"))
    game = Game(TITLE, WIDTH, HEIGHT, FPS)
    await game.run(MapScene("bunker"))


# pygbag necesita que el juego arranque con asyncio.run(main()) al final de main.py.
asyncio.run(main())
