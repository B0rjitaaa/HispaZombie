"""Progresión del protagonista: estadísticas por nivel, experiencia y habilidades.

Trabaja sobre GameState, así que todo lo que cambia aquí se guarda con la partida.
"""

from __future__ import annotations

import random

import items
from battle import data
from i18n import tr
from state import GameState

MAX_LEVEL = 30
MAX_EQUIPPED = 6

# Estadísticas a nivel 1 y cuánto suben por nivel.
PLAYER_BASE = {"hp": 30, "caffeine": 12, "attack": 6, "defense": 5, "mutation": 6, "speed": 5}
PLAYER_GROWTH = {
    "hp": 5,
    "caffeine": 2,
    "attack": 1.5,
    "defense": 1.2,
    "mutation": 1.6,
    "speed": 0.8,
}


def player_stats(level: int) -> dict[str, int]:
    return {k: int(PLAYER_BASE[k] + PLAYER_GROWTH[k] * (level - 1)) for k in PLAYER_BASE}


def xp_for_level(level: int) -> int:
    """Experiencia total necesaria para llegar a `level`."""
    return round(8 * (level - 1) ** 1.6)


def enemy_stats(enemy_id: str, level: int) -> dict[str, int]:
    base = data.enemy(enemy_id)["stats"]
    factor = 1 + 0.12 * (level - 1)
    return {k: max(1, round(v * factor)) for k, v in base.items()}


def enemy_xp(enemy_id: str, level: int) -> int:
    return round(data.enemy(enemy_id)["xp"] * (1 + 0.25 * (level - 1)))


# --- Vida, cafeína y usos ---


def max_hp(state: GameState) -> int:
    return player_stats(state.level)["hp"]


def max_caffeine(state: GameState) -> int:
    return player_stats(state.level)["caffeine"]


def current_hp(state: GameState) -> int:
    return max_hp(state) if state.hp is None else min(state.hp, max_hp(state))


def current_caffeine(state: GameState) -> int:
    return (
        max_caffeine(state) if state.caffeine is None else min(state.caffeine, max_caffeine(state))
    )


def skill_uses(state: GameState, skill_id: str) -> int:
    """Usos que le quedan a una técnica callejera."""
    max_uses = data.skill(skill_id).get("uses", 0)
    return state.skill_uses.get(skill_id, max_uses)


def full_restore(state: GameState) -> None:
    """Descanso completo: vida, cafeína y usos de las técnicas callejeras al máximo."""
    state.hp = None
    state.caffeine = None
    state.skill_uses.clear()


# --- Habilidades ---


def learn_skill(state: GameState, skill_id: str) -> bool:
    """Aprende una habilidad y la equipa si hay hueco. False si ya la sabía."""
    if skill_id in state.learned_skills:
        return False
    state.learned_skills.append(skill_id)
    if len(state.equipped_skills) < MAX_EQUIPPED:
        state.equipped_skills.append(skill_id)
    return True


def toggle_equipped(state: GameState, skill_id: str) -> bool:
    """Equipa o desequipa. Devuelve False si no se puede (sin hueco o última habilidad)."""
    if skill_id in state.equipped_skills:
        if len(state.equipped_skills) == 1:
            return False
        state.equipped_skills.remove(skill_id)
        return True
    if len(state.equipped_skills) >= MAX_EQUIPPED or skill_id not in state.learned_skills:
        return False
    state.equipped_skills.append(skill_id)
    return True


def gain_xp(state: GameState, amount: int) -> list[str]:
    """Suma experiencia. Devuelve los mensajes de subida de nivel y habilidades aprendidas."""
    messages: list[str] = []
    state.xp += amount
    while state.level < MAX_LEVEL and state.xp >= xp_for_level(state.level + 1):
        old_hp, old_caffeine = max_hp(state), max_caffeine(state)
        state.level += 1
        # Al subir de nivel se gana la vida y la cafeína extra (como en los RPG clásicos).
        if state.hp is not None:
            state.hp += max_hp(state) - old_hp
        if state.caffeine is not None:
            state.caffeine += max_caffeine(state) - old_caffeine
        messages.append(tr("¡Subes al nivel {n}!").format(n=state.level))
        for learn_level, skill_id in data.mutant_skills_by_level():
            if learn_level == state.level and learn_skill(state, skill_id):
                text = tr("¡La mutación despierta! Aprendes {skill}.")
                messages.append(text.format(skill=data.skill_name(skill_id)))
                if skill_id not in state.equipped_skills:
                    messages.append(tr("No te quedan huecos: equípala desde el menú."))
    return messages


def apply_victory(
    state: GameState, enemy_id: str, level: int, rng: random.Random | None = None
) -> list[str]:
    """Reparte la recompensa de un combate ganado y devuelve los mensajes."""
    rng = rng or random.Random()
    enemy = data.enemy(enemy_id)
    xp = enemy_xp(enemy_id, level)
    low, high = enemy.get("coins", [0, 0])
    coins = rng.randint(low, high)
    messages = [tr("Ganas {xp} puntos de experiencia.").format(xp=xp)]
    if coins:
        state.give_coins(coins)
        messages.append(tr("Encuentras {n} fichas.").format(n=coins))
    for drop in enemy.get("drops", []):
        if rng.random() < drop["chance"]:
            state.give_item(drop["item"])
            messages.append(tr("Obtienes: {item}.").format(item=items.name(drop["item"])))
    messages += gain_xp(state, xp)
    return messages
