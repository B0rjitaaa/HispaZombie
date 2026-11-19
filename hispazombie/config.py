"""Constantes globales del juego."""

TITLE = "HispaZombie"

# Resolución interna del pixel art (16:9). Se escala a la ventana con un factor entero:
# x2 = 960x540, x3 = 1440x810, x4 = 1920x1080. Los textos se dibujan aparte en HD.
WIDTH = 480
HEIGHT = 270

# Tamaño de cada casilla del mapa, en píxeles. 480x270 -> 30x17 casillas en pantalla.
TILE = 16

FPS = 60

# Idioma del juego. Los textos se escriben en español; otros idiomas usan assets/i18n/<idioma>.json.
LANGUAGE = "es"
