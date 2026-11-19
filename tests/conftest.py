import os

# Permite crear la ventana de pygame en los tests sin abrir nada en pantalla.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
