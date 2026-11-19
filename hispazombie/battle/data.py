"""Carga de los datos de combate: habilidades, enemigos y tablas de encuentros.

Los archivos están en assets/data/ y se pueden editar sin tocar código.

Tipos de daño: physical (Físico), radiation (Radiación), heat (Calor), toxic (Tóxico) y
wit (Labia). Familias de habilidad: innate (siempre disponible, gratis), mutant (se aprende
por nivel y gasta Cafeína), street (se compra con fichas y tiene usos limitados) y enemy.
"""

from __future__ import annotations

import json
from typing import Any

from engine import resources
from i18n import mark, tr

TYPE_NAMES = {
    "physical": mark("Físico"),
    "radiation": mark("Radiación"),
    "heat": mark("Calor"),
    "toxic": mark("Tóxico"),
    "wit": mark("Labia"),
}

_cache: dict[str, dict[str, Any]] = {}


def _load(name: str) -> dict[str, Any]:
    if name not in _cache:
        with open(resources.path("data", f"{name}.json"), encoding="utf-8") as f:
            _cache[name] = json.load(f)
    return _cache[name]


def skills() -> dict[str, dict[str, Any]]:
    return _load("skills")


def skill(skill_id: str) -> dict[str, Any]:
    return skills()[skill_id]


def skill_name(skill_id: str) -> str:
    return tr(skill(skill_id)["name"])


def enemies() -> dict[str, dict[str, Any]]:
    return _load("enemies")


def enemy(enemy_id: str) -> dict[str, Any]:
    return enemies()[enemy_id]


def encounter_table(table_id: str) -> dict[str, Any] | None:
    return _load("encounters").get(table_id)


def type_name(type_id: str) -> str:
    return tr(TYPE_NAMES.get(type_id, type_id))


def mutant_skills_by_level() -> list[tuple[int, str]]:
    """Habilidades mutantes ordenadas por el nivel en el que se aprenden."""
    result = [
        (s["learn_level"], skill_id)
        for skill_id, s in skills().items()
        if s.get("family") == "mutant" and "learn_level" in s
    ]
    return sorted(result)
