"""Pruebas del motor de combate y de la progresión (sin gráficos)."""

import random

from battle import data, progress
from battle.engine import Battle
from state import GameState


def new_battle(enemy="mutant_parrot", level=1, seed=1, state=None, can_flee=True):
    state = state or GameState()
    return Battle(state, enemy, level, can_flee=can_flee, rng=random.Random(seed)), state


def test_player_starts_with_innate_and_first_mutant_skill():
    state = GameState()
    assert state.equipped_skills == ["slap", "green_glow"]
    assert data.skill("green_glow")["family"] == "mutant"
    assert progress.current_hp(state) == progress.player_stats(1)["hp"]


def test_mutant_skill_spends_caffeine_and_street_skill_spends_uses():
    battle, state = new_battle()
    start_caffeine = battle.player.caffeine
    battle.play_turn(("skill", "green_glow"))
    assert battle.player.caffeine == start_caffeine - data.skill("green_glow")["caffeine"]

    progress.learn_skill(state, "flip_flop")
    battle, state = new_battle(state=state)
    battle.play_turn(("skill", "flip_flop"))
    assert progress.skill_uses(state, "flip_flop") == data.skill("flip_flop")["uses"] - 1


def test_cannot_use_mutant_skill_without_caffeine():
    battle, _ = new_battle()
    battle.player.caffeine = 0
    assert not battle.can_use_skill("green_glow")
    assert battle.can_use_skill("slap")  # el manotazo siempre está disponible


def test_type_weakness_does_more_damage():
    state = GameState()
    progress.learn_skill(state, "fair_fan")  # Calor: la cotorra es débil
    weak = []
    neutral = []
    for seed in range(30):
        b, _ = new_battle(seed=seed, state=GameState())
        b.player.skills.append("fair_fan")
        hp = b.enemy.hp
        b._deal_damage(b.player, b.enemy, data.skill("fair_fan"))
        weak.append(hp - b.enemy.hp)
        b2, _ = new_battle("radioactive_pigeon", seed=seed)
        hp2 = b2.enemy.hp
        b2._deal_damage(b2.player, b2.enemy, data.skill("fair_fan"))
        neutral.append(hp2 - b2.enemy.hp)
    assert sum(weak) / len(weak) > sum(neutral) / len(neutral) * 1.5


def test_battle_can_be_won_and_gives_rewards():
    battle, state = new_battle(seed=3)
    for _ in range(30):
        battle.play_turn(("skill", "slap"))
        if battle.outcome:
            break
    assert battle.outcome == "win"
    assert state.xp == progress.enemy_xp("mutant_parrot", 1)
    assert state.hp == battle.player.hp  # la vida tras el combate pasa a la partida


def test_losing_ends_the_battle():
    battle, state = new_battle("metro_rat", level=5, seed=2)
    battle.player.hp = 1
    for _ in range(10):
        battle.play_turn(("skill", "slap"))
        if battle.outcome:
            break
    assert battle.outcome == "lose"
    assert state.hp == 0


def test_cannot_flee_from_bosses():
    battle, _ = new_battle("metro_rat")
    events = battle.play_turn(("flee",))
    assert battle.outcome is None
    assert any("No puedes huir" in e.text for e in events)


def test_flee_eventually_succeeds():
    battle, _ = new_battle(seed=5)
    for _ in range(10):
        battle.play_turn(("flee",))
        if battle.outcome:
            break
    assert battle.outcome == "fled"


def test_healing_nap_heals_and_skips_next_turn():
    state = GameState()
    progress.learn_skill(state, "healing_nap")
    battle, _ = new_battle(state=state, seed=4)
    battle.player.hp = 5
    battle.play_turn(("skill", "healing_nap"))
    assert battle.player.hp > 5
    assert battle.player_must_skip
    battle.play_turn(("skip",))
    assert not battle.player_must_skip


def test_items_in_battle():
    state = GameState()
    state.give_item("water_bottle")
    battle, _ = new_battle(state=state)
    battle.player.hp = 1
    battle.play_turn(("item", "water_bottle"))
    assert state.item_count("water_bottle") == 0
    assert battle.player.hp > 1


def test_level_up_learns_mutant_skills():
    state = GameState()
    messages = progress.gain_xp(state, progress.xp_for_level(3))
    assert state.level == 3
    assert "healing_nap" in state.learned_skills
    assert "healing_nap" in state.equipped_skills
    assert any("nivel 3" in m for m in messages)


def test_equip_limit_and_last_skill():
    state = GameState()
    for skill_id in ["flip_flop", "fair_fan", "squid_sandwich", "artful_insult"]:
        progress.learn_skill(state, skill_id)
    assert len(state.equipped_skills) == progress.MAX_EQUIPPED
    progress.learn_skill(state, "healing_nap")
    assert "healing_nap" not in state.equipped_skills  # sin hueco: aprendida pero no equipada
    assert not progress.toggle_equipped(state, "healing_nap")
    assert progress.toggle_equipped(state, "slap")  # desequipar libera un hueco
    assert progress.toggle_equipped(state, "healing_nap")

    solo = GameState()
    solo.equipped_skills = ["slap"]
    assert not progress.toggle_equipped(solo, "slap")  # nunca se queda sin habilidades


def test_all_data_references_exist():
    """Habilidades de enemigos, objetos que sueltan y tablas de encuentros son válidos."""
    import items

    for enemy_id, enemy in data.enemies().items():
        for skill_id in enemy["skills"]:
            assert skill_id in data.skills(), (enemy_id, skill_id)
        for drop in enemy.get("drops", []):
            assert items.exists(drop["item"]), (enemy_id, drop)
    table = data.encounter_table("cartuja_outskirts")
    for entry in table["enemies"]:
        assert entry["enemy"] in data.enemies()
