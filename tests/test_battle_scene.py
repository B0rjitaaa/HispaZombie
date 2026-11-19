"""Pruebas del combate integrado en el juego (escenas y mapa), con ventana invisible."""

import random

import pygame
import pytest

import saves
from battle import progress
from battle.engine import Battle
from engine.controls import CANCEL, CONFIRM, DOWN, Controls
from engine.scenes import SceneManager
from engine.storage import MemoryStorage
from scenes.battle_scene import BattleScene
from scenes.map_scene import MapScene
from state import game_state
from ui.choice_box import ChoiceScene
from ui.message_box import MessageScene
from ui.skills_menu import SkillsScene

DT = 1 / 60


@pytest.fixture(autouse=True)
def window():
    pygame.init()
    pygame.display.set_mode((480, 270))
    game_state.reset()
    game_state.turn_on("auto:bunker:intro_wake_up")
    game_state.turn_on("auto:cartuja_outskirts:outskirts_arrival")
    saves.set_storage(MemoryStorage())
    yield
    saves.set_storage(None)


def step(manager, action=None, frames=1):
    controls = Controls()
    if action:
        controls.press(action)
    for _ in range(frames):
        manager.current.update(DT, controls)
        controls.new_frame()
        if action:
            controls.release(action)


def map_at(map_id, x, y, facing):
    manager = SceneManager()
    scene = MapScene(map_id, x, y, facing)
    scene.fade, scene.fade_direction = 0.0, 0
    manager.push(scene)
    return manager, scene


def advance_until(manager, condition, limit=3000):
    """Pulsa Aceptar de vez en cuando hasta que se cumpla la condición."""
    for i in range(limit):
        if condition():
            return True
        step(manager, CONFIRM if i % 10 == 0 else None)
    return condition()


def fight(manager, skill_index=0, limit=4000):
    """Juega el combate en curso eligiendo siempre la misma habilidad."""
    for i in range(limit):
        scene = manager.current
        if not isinstance(scene, BattleScene):
            return
        if scene.phase == "command":
            step(manager, CONFIRM)  # Habilidades
        elif scene.phase == "skills":
            for _ in range(skill_index):
                step(manager, DOWN)
            step(manager, CONFIRM)
        else:
            step(manager, CONFIRM if i % 15 == 0 else None)


def test_random_encounter_starts_a_battle():
    # (10, 10) está en la zona de encuentros del norte.
    manager, scene = map_at("cartuja_outskirts", 10, 10, "up")
    scene.rng = random.Random(0)
    scene.steps_to_encounter = 1
    assert scene.encounter_table_at(10, 10) == "cartuja_outskirts"
    step(manager, "up", frames=20)
    assert advance_until(manager, lambda: isinstance(manager.current, BattleScene), 100)


def test_construction_site_is_safe():
    manager, scene = map_at("cartuja_outskirts", 8, 20, "up")
    assert scene.encounter_table_at(8, 20) is None  # dentro de la obra
    assert scene.encounter_table_at(17, 20) is None  # carretera


def test_winning_a_battle_gives_experience():
    manager, scene = map_at("cartuja_outskirts", 10, 10, "up")
    battle = Battle(game_state, "mutant_parrot", 1, rng=random.Random(3))
    result = {}
    manager.push(
        BattleScene("mutant_parrot", 1, lambda o: result.setdefault("o", o), battle=battle)
    )
    fight(manager, skill_index=0)
    assert result["o"] == "win"
    assert game_state.xp > 0
    assert manager.current is scene


def test_losing_wakes_you_up_at_the_safe_place():
    game_state.give_coins(10)
    manager, scene = map_at("cartuja_outskirts", 10, 10, "up")
    game_state.hp = 1
    scene.run_script([{"cmd": "battle", "enemy": "metro_rat", "level": 9, "can_flee": False}])
    battle_scene = manager.current
    assert isinstance(battle_scene, BattleScene)
    battle_scene.battle.rng = random.Random(1)
    fight(manager)
    assert advance_until(
        manager,
        lambda: isinstance(manager.current, MapScene) and manager.current.map_id == "bunker",
    )
    new_scene = manager.current
    assert (new_scene.player.movement.x, new_scene.player.movement.y) == (9, 6)
    assert game_state.coins == 5  # pierde la mitad
    assert progress.current_hp(game_state) == progress.max_hp(game_state)


def test_chrysalis_rest_restores_and_sets_respawn():
    game_state.hp = 3
    game_state.skill_uses["flip_flop"] = 0
    manager, scene = map_at("bunker", 9, 6, "left")  # la crisálida está en (8, 6)
    step(manager, CONFIRM)
    assert advance_until(manager, lambda: isinstance(manager.current, ChoiceScene), 300)
    step(manager, CONFIRM)  # "Una cabezadita"
    step(manager, frames=2)  # el script sigue en el siguiente frame del mapa
    assert game_state.hp is None
    assert game_state.skill_uses == {}
    assert game_state.respawn == ["bunker", 9, 6, "left"]


def test_scrapper_teaches_a_street_skill():
    game_state.turn_on("scrapper_met")
    game_state.give_coins(8)
    manager, scene = map_at("cartuja_outskirts", 14, 12, "up")
    step(manager, CONFIRM)
    assert advance_until(manager, lambda: isinstance(manager.current, ChoiceScene), 300)
    step(manager, DOWN)
    step(manager, CONFIRM)  # "Enséñame algo"
    assert advance_until(manager, lambda: isinstance(manager.current, ChoiceScene), 300)
    step(manager, DOWN)
    step(manager, CONFIRM)  # "Abanico de feria (8 fichas)"
    assert advance_until(
        manager, lambda: manager.current is scene and scene.interpreter is None, 600
    )
    assert "fair_fan" in game_state.learned_skills
    assert "fair_fan" in game_state.equipped_skills
    assert game_state.coins == 0


def test_metro_rat_disappears_after_being_defeated():
    manager, scene = map_at("cartuja_outskirts", 11, 25, "right")
    rat = next(e for e in scene.map.events if e.name == "metro_rat")
    assert scene.is_visible(rat)
    game_state.turn_on("metro_rat_defeated")
    assert not scene.is_visible(rat)
    assert scene.is_walkable(12, 25)  # ya no bloquea el paso al cofre


def test_skills_screen_toggles_equipped_skills():
    progress.learn_skill(game_state, "flip_flop")
    manager = SceneManager()
    manager.push(SkillsScene())
    step(manager, DOWN)
    step(manager, DOWN)  # Chanclazo
    step(manager, CONFIRM)
    assert "flip_flop" not in game_state.equipped_skills
    step(manager, CONFIRM)
    assert "flip_flop" in game_state.equipped_skills
    step(manager, CANCEL)
    assert manager.empty


def test_inventory_use_heals_outside_battle():
    from ui.pause_menu import InventoryScene

    game_state.hp = 5
    game_state.give_item("water_bottle")
    manager = SceneManager()
    manager.push(InventoryScene())
    step(manager, CONFIRM)
    assert isinstance(manager.current, MessageScene)
    assert game_state.hp == 25
    assert game_state.item_count("water_bottle") == 0
