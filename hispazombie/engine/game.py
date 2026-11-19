"""Bucle principal del juego, compatible con escritorio y con navegador (pygbag)."""

from __future__ import annotations

import asyncio
import sys

import pygame

from engine import hd_text
from engine.controls import Controls
from engine.scenes import Scene, SceneManager

IN_BROWSER = sys.platform == "emscripten"

# Fracción máxima del escritorio que puede ocupar la ventana (deja sitio a barras y bordes).
DESKTOP_MARGIN = 0.85


def integer_scale(width: int, height: int, available: tuple[int, int]) -> int:
    """Mayor factor entero que hace caber width x height en el espacio disponible (mínimo 1)."""
    return max(1, min(available[0] // width, available[1] // height))


class Game:
    def __init__(self, title: str, width: int, height: int, fps: int) -> None:
        pygame.init()
        pygame.display.set_caption(title)
        self.width = width
        self.height = height
        self.fps = fps

        # Todo se dibuja en esta pantalla virtual y luego se escala a la ventana con un
        # factor entero y sin suavizado, para que el pixel art se vea nítido.
        self.screen = pygame.Surface((width, height))
        self.fullscreen = False
        self.window = self._create_window()

        self.clock = pygame.time.Clock()
        self.scenes = SceneManager()
        self.controls = Controls()
        self.running = True

    def _create_window(self) -> pygame.Surface:
        if IN_BROWSER:
            # pygbag ajusta el canvas al tamaño de la página.
            return pygame.display.set_mode((self.width * 2, self.height * 2))
        if self.fullscreen:
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        desktop = pygame.display.get_desktop_sizes()[0]
        available = (int(desktop[0] * DESKTOP_MARGIN), int(desktop[1] * DESKTOP_MARGIN))
        scale = integer_scale(self.width, self.height, available)
        return pygame.display.set_mode((self.width * scale, self.height * scale), pygame.RESIZABLE)

    def toggle_fullscreen(self) -> None:
        if IN_BROWSER:
            return
        self.fullscreen = not self.fullscreen
        self.window = self._create_window()

    def quit(self) -> None:
        self.running = False

    def _present(self) -> None:
        """Escala la pantalla virtual a la ventana (centrada, con bandas negras) y dibuja
        encima los textos HD a la resolución real."""
        window_size = self.window.get_size()
        scale = integer_scale(self.width, self.height, window_size)
        size = (self.width * scale, self.height * scale)
        x = (window_size[0] - size[0]) // 2
        y = (window_size[1] - size[1]) // 2
        self.window.fill((0, 0, 0))
        self.window.blit(pygame.transform.scale(self.screen, size), (x, y))
        hd_text.layer.render(self.window, (x, y), scale)
        pygame.display.flip()

    def _is_fullscreen_key(self, event: pygame.event.Event) -> bool:
        return event.type == pygame.KEYDOWN and (
            event.key == pygame.K_F11
            or (event.key == pygame.K_RETURN and bool(event.mod & pygame.KMOD_ALT))
        )

    async def run(self, first_scene: Scene) -> None:
        self.scenes.push(first_scene)

        while self.running and not self.scenes.empty:
            dt = self.clock.tick(self.fps) / 1000
            # Evita saltos enormes si la ventana estuvo congelada (p. ej. arrastrándola).
            dt = min(dt, 0.1)

            self.controls.new_frame()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.WINDOWFOCUSLOST:
                    self.controls.release_all()
                elif self._is_fullscreen_key(event):
                    self.toggle_fullscreen()
                else:
                    self.controls.handle_event(event)

            scene = self.scenes.current
            if scene is not None:
                scene.update(dt, self.controls)

            self.screen.fill((0, 0, 0))
            hd_text.layer.clear()
            for scene in self.scenes:
                if scene.hides_text_below:
                    hd_text.layer.clear()
                scene.draw(self.screen)
            self._present()

            # Imprescindible para pygbag: devuelve el control al navegador cada frame.
            await asyncio.sleep(0)

        pygame.quit()
