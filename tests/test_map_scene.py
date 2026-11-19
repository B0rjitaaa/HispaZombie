"""Pruebas de la escena de exploración, con una ventana invisible."""

import pygame
import pytest

from engine.controls import CONFIRM, Controls
from engine.scenes import SceneManager
from scenes.map_scene import MapScene
from state import game_state
from ui.message_box import MessageScene

DT = 1 / 60


@pytest.fixture(autouse=True)
def window():
    pygame.init()
    pygame.display.set_mode((320, 240))
    game_state.reset()  # partida limpia en cada test
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


def press(manager, action, frames=1):
    controls = Controls()
    controls.press(action)
    for _ in range(frames):
        manager.current.update(DT, controls)
        controls.new_frame()


def test_chest_gives_item_only_once():
    # Cofre del periódico en (4, 8); nos ponemos debajo mirando hacia arriba.
    manager, scene = setup_scene("cartuja_outskirts", 4, 9, "up")
    press(manager, CONFIRM)
    assert isinstance(manager.current, MessageScene)
    assert game_state.inventory == ["newspaper_1966"]

    manager.pop()
    press(manager, CONFIRM)
    assert game_state.inventory == ["newspaper_1966"]  # ya estaba vacío


def test_bumping_a_blocker_shows_text():
    # Salida sur hacia Triana: bloqueos en (17, 28) y (18, 28).
    manager, scene = setup_scene("cartuja_outskirts", 17, 27, "down")
    press(manager, "down")
    assert isinstance(manager.current, MessageScene)
    assert (scene.player.movement.x, scene.player.movement.y) == (17, 27)


def test_bumping_the_crater_shows_tile_text():
    # El borde del cráter empieza a 8 casillas del centro (36, 16).
    manager, scene = setup_scene("cartuja_outskirts", 27, 16, "right")
    press(manager, "right")
    assert isinstance(manager.current, MessageScene)


def test_door_changes_map():
    # Escaleras del búnker en (9, 2): desde (9, 3) se sube.
    manager, scene = setup_scene("bunker", 9, 3, "up")
    press(manager, "up", frames=20)  # paso completo: se pisa la puerta
    assert scene.fade_direction == 1
    for _ in range(60):
        manager.current.update(DT, Controls())
    new_scene = manager.current
    assert isinstance(new_scene, MapScene)
    assert new_scene.map_id == "cartuja_outskirts"
    assert (new_scene.player.movement.x, new_scene.player.movement.y) == (6, 22)
