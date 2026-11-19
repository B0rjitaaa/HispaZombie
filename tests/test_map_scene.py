"""Pruebas de la escena de exploración, con una ventana invisible."""

import pygame
import pytest

import saves
from engine.controls import CANCEL, CONFIRM, DOWN, Controls
from engine.scenes import SceneManager
from engine.storage import MemoryStorage
from scenes.map_scene import MapScene
from scenes.title_scene import TitleScene
from state import game_state
from ui.choice_box import ChoiceScene
from ui.message_box import MessageScene
from ui.pause_menu import InventoryScene, PauseMenuScene

DT = 1 / 60


@pytest.fixture(autouse=True)
def window():
    pygame.init()
    pygame.display.set_mode((480, 270))
    game_state.reset()  # partida limpia en cada test
    saves.set_storage(MemoryStorage())
    yield
    saves.set_storage(None)
    # No se llama a pygame.quit(): invalidaría las fuentes guardadas en caché.


def setup_scene(map_id, x=None, y=None, facing=None):
    manager = SceneManager()
    scene = MapScene(map_id, x, y, facing)
    scene.fade, scene.fade_direction = 0.0, 0  # sin fundido de entrada
    # Se dan por vistos los textos de introducción para que no interrumpan las pruebas.
    game_state.turn_on("auto:bunker:intro_wake_up")
    game_state.turn_on("auto:cartuja_outskirts:outskirts_arrival")
    manager.push(scene)
    return manager, scene


def step(manager, action=None, frames=1):
    """Avanza frames pulsando (opcionalmente) una acción en el primero."""
    controls = Controls()
    if action:
        controls.press(action)
    for _ in range(frames):
        manager.current.update(DT, controls)
        controls.new_frame()
        if action:
            controls.release(action)


def close_messages(manager, limit=40):
    """Cierra mensajes hasta que aparezca otra cosa (una elección o el mapa)."""
    for _ in range(limit):
        if not isinstance(manager.current, MessageScene):
            return
        step(manager, CONFIRM)  # muestra la página entera
        step(manager, CONFIRM)  # pasa de página / cierra
        step(manager, frames=2)


def choose(manager, index):
    assert isinstance(manager.current, ChoiceScene)
    for _ in range(index):
        step(manager, DOWN)
    step(manager, CONFIRM)
    step(manager)


def test_chest_gives_item_only_once():
    # Cofre del periódico en (4, 8); nos ponemos debajo mirando hacia arriba.
    manager, scene = setup_scene("cartuja_outskirts", 4, 9, "up")
    step(manager, CONFIRM)
    assert isinstance(manager.current, MessageScene)
    close_messages(manager)
    assert game_state.inventory == {"newspaper_1966": 1}

    step(manager, CONFIRM)
    close_messages(manager)
    assert game_state.inventory == {"newspaper_1966": 1}  # ya estaba vacío


def test_bumping_a_blocker_shows_text():
    # Salida sur hacia Triana: bloqueos en (17, 28) y (18, 28).
    manager, scene = setup_scene("cartuja_outskirts", 17, 27, "down")
    step(manager, DOWN)
    assert isinstance(manager.current, MessageScene)
    assert (scene.player.movement.x, scene.player.movement.y) == (17, 27)


def test_bumping_the_crater_shows_tile_text():
    # El borde del cráter empieza a 8 casillas del centro (36, 16).
    manager, scene = setup_scene("cartuja_outskirts", 27, 16, "right")
    step(manager, "right")
    assert isinstance(manager.current, MessageScene)


def test_door_changes_map():
    # Escaleras del búnker en (9, 2): desde (9, 3) se sube.
    manager, scene = setup_scene("bunker", 9, 3, "up")
    step(manager, "up", frames=20)  # paso completo: se pisa la puerta
    assert scene.fade_direction == 1
    step(manager, frames=60)
    new_scene = manager.current
    assert isinstance(new_scene, MapScene)
    assert new_scene.map_id == "cartuja_outskirts"
    assert (new_scene.player.movement.x, new_scene.player.movement.y) == (6, 22)


def talk_to_scrapper(manager):
    step(manager, CONFIRM)


def test_scrapper_first_meeting_remembers_and_moves():
    # Manolo está en (14, 11) mirando abajo; nos ponemos debajo mirando arriba.
    manager, scene = setup_scene("cartuja_outskirts", 14, 12, "up")
    talk_to_scrapper(manager)
    scrapper = next(iter(scene.actors.values()))
    assert scrapper.movement.facing == "down"  # se gira hacia el jugador
    close_messages(manager)
    choose(manager, 0)  # "No, soy becario."
    close_messages(manager)
    step(manager, frames=120)  # deja que camine hasta su puesto
    close_messages(manager)
    step(manager, frames=120)

    assert game_state.is_on("scrapper_met")
    assert game_state.get_variable("scrapper_trust") == 1
    assert game_state.coins == 5
    assert (scrapper.movement.x, scrapper.movement.y) == (16, 11)
    assert game_state.event_positions["cartuja_outskirts:scrapper"][:2] == [16, 11]
    assert scene.interpreter is None


def test_scrapper_sells_water_and_remembers_trust():
    game_state.turn_on("scrapper_met")
    game_state.set_variable("scrapper_trust", 1)
    game_state.give_coins(3)
    manager, scene = setup_scene("cartuja_outskirts", 14, 12, "up")
    talk_to_scrapper(manager)
    first = manager.current
    assert isinstance(first, MessageScene)
    assert "becario" in first.pages[0][1][0]  # saludo de confianza
    close_messages(manager)
    choose(manager, 0)  # comprar agua
    close_messages(manager)
    assert game_state.coins == 0
    assert game_state.item_count("water_bottle") == 1


def test_pause_menu_inventory_and_save():
    game_state.give_item("water_bottle")
    manager, scene = setup_scene("cartuja_outskirts", 10, 10, "left")
    step(manager, CANCEL)
    assert isinstance(manager.current, PauseMenuScene)

    step(manager, CONFIRM)  # "Objetos"
    assert isinstance(manager.current, InventoryScene)
    assert manager.current.item_ids == ["water_bottle"]
    step(manager, CANCEL)

    step(manager, DOWN)
    step(manager, CONFIRM)  # "Guardar"
    assert isinstance(manager.current, MessageScene)
    assert saves.has_save()
    data = saves.storage().read(saves.SLOT)
    assert (data["map_id"], data["player_x"], data["player_y"]) == ("cartuja_outskirts", 10, 10)


def test_title_continue_loads_saved_position():
    game_state.give_coins(2)
    game_state.map_id, game_state.player_x, game_state.player_y = "cartuja_outskirts", 10, 10
    saves.save_game()
    game_state.reset()

    manager = SceneManager()
    manager.push(TitleScene())
    assert manager.current.menu.index == 1  # el cursor empieza en "Continuar"
    step(manager, CONFIRM)
    scene = manager.current
    assert isinstance(scene, MapScene)
    assert scene.map_id == "cartuja_outskirts"
    assert (scene.player.movement.x, scene.player.movement.y) == (10, 10)
    assert game_state.coins == 2


def test_title_without_save_disables_continue():
    manager = SceneManager()
    manager.push(TitleScene())
    title = manager.current
    assert title.menu.enabled[1] is False
    step(manager, CONFIRM)  # "Nueva partida"
    assert isinstance(manager.current, MapScene)
    assert manager.current.map_id == "bunker"
