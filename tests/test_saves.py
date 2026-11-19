import pytest

import saves
from engine.storage import FileStorage, MemoryStorage
from state import GameState, game_state


@pytest.fixture(autouse=True)
def memory_storage():
    saves.set_storage(MemoryStorage())
    game_state.reset()
    yield
    saves.set_storage(None)


def test_state_round_trip():
    s = GameState()
    s.turn_on("met")
    s.set_variable("trust", 2)
    s.give_item("water_bottle", 3)
    s.give_coins(9)
    s.event_positions["cartuja_outskirts:scrapper"] = [16, 11, "down"]
    s.map_id, s.player_x, s.player_y, s.player_facing = "cartuja_outskirts", 4, 5, "left"

    copy = GameState()
    copy.load_dict(s.to_dict())
    assert copy.to_dict() == s.to_dict()


def test_inventory_counts():
    s = GameState()
    s.give_item("water_bottle")
    s.give_item("water_bottle")
    assert not s.remove_item("water_bottle", 3)  # no hay suficientes: no se quita nada
    assert s.item_count("water_bottle") == 2
    assert s.remove_item("water_bottle", 2)
    assert "water_bottle" not in s.inventory


def test_save_and_load_game():
    assert not saves.has_save()
    game_state.give_coins(4)
    assert saves.save_game()
    assert saves.has_save()

    game_state.reset()
    assert saves.load_game()
    assert game_state.coins == 4


def test_load_rejects_unknown_version():
    saves.storage().write(saves.SLOT, {"version": 999})
    assert not saves.load_game()


def test_file_storage(tmp_path):
    storage = FileStorage(str(tmp_path / "saves"))
    assert not storage.exists("slot1")
    storage.write("slot1", {"coins": 3, "texto": "ñandú"})
    assert storage.read("slot1") == {"coins": 3, "texto": "ñandú"}
    storage.delete("slot1")
    assert storage.read("slot1") is None
