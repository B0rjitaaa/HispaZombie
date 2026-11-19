"""Pantalla de habilidades: ver las aprendidas y elegir cuáles van en los 6 huecos."""

from __future__ import annotations

import pygame

from battle import data, progress
from config import HEIGHT, WIDTH
from engine import hd_text
from engine.controls import Controls
from engine.scenes import Scene
from engine.text import wrap
from i18n import mark, tr
from state import game_state
from ui.widgets import (
    ACCENT_COLOR,
    LINE_HEIGHT,
    PADDING,
    TEXT_COLOR,
    TEXT_SIZE,
    MenuList,
    dim_screen,
    draw_panel,
)

MARGIN = 6
FAMILY_NAMES = {"innate": mark("Básica"), "mutant": mark("Mutante"), "street": mark("Callejera")}


class SkillsScene(Scene):
    hides_text_below = True  # ocupa toda la pantalla

    def __init__(self) -> None:
        self.notice = ""
        self._build_menu()

    def _build_menu(self, index: int = 0) -> None:
        self.skill_ids = list(game_state.learned_skills)
        labels = []
        right = []
        for skill_id in self.skill_ids:
            prefix = "[x] " if skill_id in game_state.equipped_skills else "[  ] "
            labels.append(prefix + data.skill_name(skill_id))
            right.append(self._cost(skill_id))
        self.menu = MenuList(labels, right_labels=right)
        self.menu.index = min(index, len(labels) - 1)

    @staticmethod
    def _cost(skill_id: str) -> str:
        s = data.skill(skill_id)
        if s.get("family") == "mutant":
            return tr("{n} Caf").format(n=s.get("caffeine", 0))
        if s.get("family") == "street":
            return f"{progress.skill_uses(game_state, skill_id)}/{s.get('uses', 0)}"
        return ""

    def update(self, dt: float, controls: Controls) -> None:
        result = self.menu.update(controls)
        if result == MenuList.CANCELLED:
            if self.manager:
                self.manager.pop()
        elif result is not None:
            skill_id = self.skill_ids[result]
            if progress.toggle_equipped(game_state, skill_id):
                self.notice = ""
            elif skill_id in game_state.equipped_skills:
                self.notice = tr("Necesitas al menos una habilidad equipada.")
            else:
                self.notice = tr("No quedan huecos libres: quita otra habilidad antes.")
            self._build_menu(result)

    def draw(self, screen: pygame.Surface) -> None:
        dim_screen(screen)
        desc_height = 3 * LINE_HEIGHT + 2 * PADDING
        list_rect = pygame.Rect(
            MARGIN, MARGIN, WIDTH - 2 * MARGIN, HEIGHT - 3 * MARGIN - desc_height
        )
        draw_panel(screen, list_rect)
        equipped = len(game_state.equipped_skills)
        title = tr("Habilidades  (equipadas {n}/{max})").format(
            n=equipped, max=progress.MAX_EQUIPPED
        )
        hd_text.layer.draw(title, list_rect.x + PADDING, list_rect.y + 4, TEXT_SIZE, ACCENT_COLOR)
        self.menu.draw(screen, list_rect.x, list_rect.y + LINE_HEIGHT, list_rect.width)

        desc_rect = pygame.Rect(MARGIN, list_rect.bottom + MARGIN, WIDTH - 2 * MARGIN, desc_height)
        draw_panel(screen, desc_rect)
        x, y = desc_rect.x + PADDING, desc_rect.y + PADDING - 1
        if self.notice:
            hd_text.layer.draw(self.notice, x, y, TEXT_SIZE, ACCENT_COLOR)
            return
        s = data.skill(self.skill_ids[self.menu.index])
        info = f"{tr(FAMILY_NAMES.get(s['family'], ''))}  ·  {data.type_name(s['type'])}"
        if s.get("power"):
            info += "  ·  " + tr("Potencia {n}").format(n=s["power"])
        hd_text.layer.draw(info, x, y, 10, ACCENT_COLOR)
        font = hd_text.HDFont(TEXT_SIZE)
        for i, line in enumerate(
            wrap(tr(s["description"]), font, desc_rect.width - 2 * PADDING)[:2]
        ):
            hd_text.layer.draw(line, x, y + 13 + i * LINE_HEIGHT, TEXT_SIZE, TEXT_COLOR)
