"""Guardar y cargar la partida (de momento, una sola ranura)."""

from __future__ import annotations

from engine.storage import create_storage
from state import game_state

SLOT = "slot1"

_storage = None


def storage():
    global _storage
    if _storage is None:
        _storage = create_storage()
    return _storage


def set_storage(new_storage) -> None:
    """Permite usar otro almacenamiento (p. ej. en memoria en los tests)."""
    global _storage
    _storage = new_storage


def has_save() -> bool:
    try:
        return storage().exists(SLOT)
    except OSError:
        return False


def save_game() -> bool:
    """Guarda el estado actual. Devuelve False si no se pudo escribir."""
    try:
        storage().write(SLOT, game_state.to_dict())
        return True
    except OSError:
        return False


def load_game() -> bool:
    """Carga la partida guardada en game_state. Devuelve False si no hay o está dañada."""
    try:
        data = storage().read(SLOT)
        if data is None:
            return False
        game_state.load_dict(data)
        return True
    except (OSError, ValueError, KeyError):
        return False
