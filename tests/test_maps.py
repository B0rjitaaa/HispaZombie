"""Comprueba que los mapas reales del juego se cargan y son coherentes."""

import os

import pytest

import items
from engine import resources
from world.tiled_map import TiledMap

MAPS = ["bunker", "cartuja_outskirts"]


def load(map_id: str) -> TiledMap:
    return TiledMap(resources.path("maps", f"{map_id}.tmj"))


@pytest.mark.parametrize("map_id", MAPS)
def test_loads_with_expected_layers(map_id):
    tiled_map = load(map_id)
    assert tiled_map.width > 0 and tiled_map.height > 0
    assert tiled_map.tile == 16
    assert {layer.name for layer in tiled_map.layers} >= {"ground", "objects", "above"}
    for ts in tiled_map.tilesets:
        assert os.path.exists(ts.image)


@pytest.mark.parametrize("map_id", MAPS)
def test_doors_lead_to_free_tiles(map_id):
    tiled_map = load(map_id)
    for door in tiled_map.events_of_kind("door"):
        target = load(door.props["map"])
        x, y = door.props["target_x"], door.props["target_y"]
        assert target.in_bounds(x, y)
        assert not target.is_solid(x, y), f"{map_id} -> destino sólido en {x},{y}"
        # No se debe aparecer encima de otra puerta (provocaría un bucle de teletransportes).
        assert not [e for e in target.events_at(x, y) if e.kind == "door"]


@pytest.mark.parametrize("map_id", MAPS)
def test_chest_items_exist(map_id):
    for chest in load(map_id).events_of_kind("chest"):
        assert items.exists(chest.props["item"]), chest.props["item"]


def test_bunker_spawn_is_free():
    tiled_map = load("bunker")
    (spawn,) = tiled_map.events_of_kind("spawn")
    assert not tiled_map.is_solid(spawn.x, spawn.y)


def test_solid_tiles_and_bump_text():
    tiled_map = load("cartuja_outskirts")
    assert tiled_map.is_solid(-1, 0)  # fuera del mapa
    # El centro del cráter es cristal radiactivo: sólido y con texto al chocar.
    assert tiled_map.is_solid(36, 16)
    assert tiled_map.bump_text(36, 16)


def test_tile_objects_are_anchored_at_the_bottom():
    tiled_map = load("bunker")
    chrysalis = [e for e in tiled_map.events if e.gid and e.kind == "sign"][0]
    # En el generador la crisálida está en la casilla (8, 6).
    assert (chrysalis.x, chrysalis.y) == (8, 6)
