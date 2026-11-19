"""Catálogo de objetos del juego (assets/data/items.json)."""

from __future__ import annotations

import json

from engine import resources
from i18n import tr

_items: dict[str, dict] | None = None


def _load() -> dict[str, dict]:
    global _items
    if _items is None:
        with open(resources.path("data", "items.json"), encoding="utf-8") as f:
            _items = json.load(f)
    return _items


def exists(item_id: str) -> bool:
    return item_id in _load()


def name(item_id: str) -> str:
    """Nombre visible del objeto, traducido al idioma activo."""
    item = _load().get(item_id)
    return tr(item["name"]) if item else item_id


def description(item_id: str) -> str:
    """Descripción del objeto, traducida al idioma activo."""
    item = _load().get(item_id)
    return tr(item.get("description", "")) if item else ""


def use_effect(item_id: str) -> dict:
    """Efecto al usar el objeto ({"heal": n}, {"caffeine": n}, {"cure": [...]}) o {}."""
    item = _load().get(item_id)
    return dict(item.get("use", {})) if item else {}


def is_usable(item_id: str) -> bool:
    return bool(use_effect(item_id))
