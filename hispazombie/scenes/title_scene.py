"""Pantalla de título: Nueva partida, Continuar y Salir."""

from __future__ import annotations

import pygame

import saves
from config import HEIGHT, TITLE, WIDTH
from engine import hd_text
from engine.controls import Controls
from engine.game import IN_BROWSER
from engine.scenes import Scene
from i18n import tr
from scenes.map_scene import MapScene
from state import game_state
from ui.message_box import MessageScene
from ui.widgets import ACCENT_COLOR, TEXT_COLOR, MenuList, draw_panel

FIRST_MAP = "bunker"


class TitleScene(Scene):
    def __init__(self) -> None:
        self.time = 0.0
        self.options = [(tr("Nueva partida"), self._new_game), (tr("Continuar"), self._continue)]
        if not IN_BROWSER:  # en el navegador no se puede cerrar la pestaña desde el juego
            self.options.append((tr("Salir"), self._quit))
        enabled = [True, saves.has_save()] + [True] * (len(self.options) - 2)
        self.menu = MenuList([label for label, _ in self.options], enabled)
        if enabled[1]:
            self.menu.index = 1  # si hay partida, el cursor empieza en Continuar

    def update(self, dt: float, controls: Controls) -> None:
        self.time += dt
        result = self.menu.update(controls)
        if result is not None and result != MenuList.CANCELLED:
            self.options[result][1]()

    def _new_game(self) -> None:
        game_state.reset()
        if self.manager:
            self.manager.replace(MapScene(FIRST_MAP))

    def _continue(self) -> None:
        if not saves.load_game():
            if self.manager:
                self.manager.push(MessageScene(tr("No se ha podido cargar la partida.")))
            return
        if self.manager:
            self.manager.replace(
                MapScene(
                    game_state.map_id,
                    game_state.player_x,
                    game_state.player_y,
                    game_state.player_facing,
                )
            )

    def _quit(self) -> None:
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((14, 12, 18))
        # Resplandor verde del cráter, que late despacio.
        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        radius = 120 + int(8 * pygame.math.Vector2(1, 0).rotate(self.time * 40).x)
        pygame.draw.circle(glow, (60, 170, 90, 40), (WIDTH // 2, HEIGHT + 40), radius)
        pygame.draw.circle(glow, (90, 220, 120, 40), (WIDTH // 2, HEIGHT + 40), radius // 2)
        screen.blit(glow, (0, 0))

        title_font = hd_text.HDFont(34, hd_text.UI_FONT_BOLD)
        tw, _ = title_font.size(TITLE)
        hd_text.layer.draw(
            TITLE, (WIDTH - tw) / 2, 50, 34, ACCENT_COLOR, filename=hd_text.UI_FONT_BOLD
        )
        subtitle = tr("Sevilla, después de una siesta muy larga")
        sw, _ = hd_text.HDFont(12).size(subtitle)
        hd_text.layer.draw(subtitle, (WIDTH - sw) / 2, 96, 12, TEXT_COLOR)

        width = max(self.menu.width(), 140)
        rect = pygame.Rect((WIDTH - width) // 2, 140, width, self.menu.height())
        draw_panel(screen, rect)
        self.menu.draw(screen, rect.x, rect.y, rect.width)
