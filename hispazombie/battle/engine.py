"""Motor de combate por turnos, uno contra uno. Sin gráficos: se puede probar con pytest.

Cada turno:
  1. El jugador elige una acción: ("skill", id), ("item", id), ("flee",) o ("skip",)
     si está dormido o aturdido (ver player_must_skip).
  2. Huir y usar objetos van primero. Las habilidades se ordenan por velocidad.
  3. Al final del turno, los estados alterados hacen su efecto.

play_turn() devuelve una lista de BattleEvent: cada uno es un mensaje para mostrar junto
con la vida y cafeína de ambos tras ese momento, para que la escena anime las barras.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

import items
from battle import data, progress
from i18n import mark, tr
from state import GameState

DAMAGE_SCALE = 0.45
CRIT_CHANCE = 1 / 16
CRIT_MULTIPLIER = 1.5
WEAK_MULTIPLIER = 2.0
RESIST_MULTIPLIER = 0.5
MIN_STAGE, MAX_STAGE = -3, 3

STATUS_NAMES = {
    "radiation": mark("Irradiado"),
    "poison": mark("Envenenado"),
    "heat": mark("Golpe de calor"),
    "stun": mark("Aturdido"),
    "nap": mark("Siestón"),
}
STATUS_TURNS = {"radiation": 4, "poison": 99, "heat": 3, "stun": 1, "nap": 2}
STAT_NAMES = {
    "attack": mark("el ataque"),
    "defense": mark("la defensa"),
    "mutation": mark("la mutación"),
    "speed": mark("la velocidad"),
}


@dataclass
class Combatant:
    name: str
    level: int
    max_hp: int
    hp: int
    max_caffeine: int
    caffeine: int
    attack: int
    defense: int
    mutation: int
    speed: int
    skills: list[str]
    is_player: bool = False
    weak: set[str] = field(default_factory=set)
    resist: set[str] = field(default_factory=set)
    boss: bool = False
    statuses: dict[str, int] = field(default_factory=dict)  # estado -> turnos restantes
    stages: dict[str, int] = field(default_factory=dict)  # estadística -> -3..+3

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def stat(self, name: str) -> float:
        """Estadística con las subidas/bajadas del combate y los estados aplicados."""
        value = getattr(self, name) * (1 + 0.25 * self.stages.get(name, 0))
        if name == "speed" and "heat" in self.statuses:
            value /= 2
        return max(1.0, value)


def player_combatant(state: GameState) -> Combatant:
    stats = progress.player_stats(state.level)
    return Combatant(
        name=tr("Becario"),
        level=state.level,
        max_hp=stats["hp"],
        hp=progress.current_hp(state),
        max_caffeine=stats["caffeine"],
        caffeine=progress.current_caffeine(state),
        attack=stats["attack"],
        defense=stats["defense"],
        mutation=stats["mutation"],
        speed=stats["speed"],
        skills=list(state.equipped_skills),
        is_player=True,
    )


def enemy_combatant(enemy_id: str, level: int) -> Combatant:
    enemy = data.enemy(enemy_id)
    stats = progress.enemy_stats(enemy_id, level)
    return Combatant(
        name=tr(enemy["name"]),
        level=level,
        max_hp=stats["hp"],
        hp=stats["hp"],
        max_caffeine=0,
        caffeine=0,
        attack=stats["attack"],
        defense=stats["defense"],
        mutation=stats["mutation"],
        speed=stats["speed"],
        skills=list(enemy["skills"]),
        weak=set(enemy.get("weak", [])),
        resist=set(enemy.get("resist", [])),
        boss=enemy.get("boss", False),
    )


@dataclass
class BattleEvent:
    text: str
    player_hp: int
    player_caffeine: int
    enemy_hp: int
    hit: str | None = None  # "player" o "enemy" si alguien acaba de recibir daño


class Battle:
    def __init__(
        self,
        state: GameState,
        enemy_id: str,
        level: int,
        can_flee: bool = True,
        rng: random.Random | None = None,
    ) -> None:
        self.state = state
        self.enemy_id = enemy_id
        self.enemy_level = level
        self.rng = rng or random.Random()
        self.player = player_combatant(state)
        self.enemy = enemy_combatant(enemy_id, level)
        self.can_flee = can_flee and not self.enemy.boss
        self.outcome: str | None = None  # "win", "lose" o "fled"
        self._events: list[BattleEvent] = []
        self.flee_attempts = 0

    # --- Consultas para la interfaz ---

    def skill_cost_label(self, skill_id: str) -> str:
        s = data.skill(skill_id)
        if s.get("family") == "mutant":
            return tr("{n} Caf").format(n=s.get("caffeine", 0))
        if s.get("family") == "street":
            return f"{progress.skill_uses(self.state, skill_id)}/{s.get('uses', 0)}"
        return ""

    @property
    def player_must_skip(self) -> bool:
        """El jugador no puede elegir acción este turno (dormido o aturdido)."""
        return "nap" in self.player.statuses or "stun" in self.player.statuses

    def can_use_skill(self, skill_id: str) -> bool:
        s = data.skill(skill_id)
        if s.get("family") == "mutant":
            return self.player.caffeine >= s.get("caffeine", 0)
        if s.get("family") == "street":
            return progress.skill_uses(self.state, skill_id) > 0
        return True

    def start_message(self) -> BattleEvent:
        text = tr("¡Aparece {name}!").format(name=self.enemy.name)
        return BattleEvent(text, self.player.hp, self.player.caffeine, self.enemy.hp)

    # --- Turno ---

    def play_turn(self, action: tuple) -> list[BattleEvent]:
        self._events = []
        kind = action[0]
        enemy_skill = self._choose_enemy_skill()

        if kind == "flee":
            if self._try_flee():
                return self._finish("fled")
            self._act(self.enemy, self.player, enemy_skill)
        elif kind == "item":
            self._use_item(action[1])
            self._act(self.enemy, self.player, enemy_skill)
        elif kind == "skip":  # el jugador está dormido o aturdido
            order = [(self.player, self.enemy, None), (self.enemy, self.player, enemy_skill)]
            if self._goes_second(self.player, self.enemy):
                order.reverse()
            for user, target, skill_id in order:
                if not self.outcome:
                    self._act(user, target, skill_id)
        else:
            order = [(self.player, self.enemy, action[1]), (self.enemy, self.player, enemy_skill)]
            if self._goes_second(self.player, self.enemy):
                order.reverse()
            for user, target, skill_id in order:
                if self.outcome:
                    break
                self._act(user, target, skill_id)

        if not self.outcome:
            self._end_of_turn()
        if self.outcome:
            return self._finish(self.outcome)
        return self._events

    def _goes_second(self, player: Combatant, enemy: Combatant) -> bool:
        ps, es = player.stat("speed"), enemy.stat("speed")
        return es > ps or (es == ps and self.rng.random() < 0.5)

    def _choose_enemy_skill(self) -> str:
        return self.rng.choice(self.enemy.skills)

    # --- Acciones ---

    def _act(self, user: Combatant, target: Combatant, skill_id: str | None) -> None:
        if not user.alive or self.outcome:
            return
        if "nap" in user.statuses:
            # Cada turno de siesta es una acción perdida; al acabar se despierta.
            self._event(tr("{name} está echándose la siesta...").format(name=user.name))
            self._tick_turns(user, "nap")
            if "nap" not in user.statuses:
                self._event(tr("¡{name} se despierta!").format(name=user.name))
            return
        if "stun" in user.statuses:
            del user.statuses["stun"]
            self._event(tr("{name} está aturdido y no puede moverse.").format(name=user.name))
            return
        if skill_id is not None:
            self._use_skill(user, target, skill_id)

    def _use_skill(self, user: Combatant, target: Combatant, skill_id: str) -> None:
        s = data.skill(skill_id)
        effect: dict[str, Any] = s.get("effect", {})
        if user.is_player:
            self._pay_cost(user, skill_id, s)
        self._event(
            tr("{user} usa {skill}.").format(user=user.name, skill=data.skill_name(skill_id))
        )

        affects_target = s.get("power", 0) > 0 or "target_stage" in effect or "status" in effect
        if affects_target and self.rng.random() * 100 >= s.get("accuracy", 100):
            self._event(tr("¡Pero falla!"))
            return

        if s.get("power", 0) > 0:
            self._deal_damage(user, target, s)
            if self.outcome:
                return

        if "hp_cost" in effect:
            cost = max(1, round(user.max_hp * effect["hp_cost"]))
            user.hp = max(1, user.hp - cost)
            self._event(tr("{name} pierde {n} de vida.").format(name=user.name, n=cost))
        if "restore_caffeine" in effect:
            gained = min(effect["restore_caffeine"], user.max_caffeine - user.caffeine)
            user.caffeine += gained
            self._event(tr("{name} recupera {n} de cafeína.").format(name=user.name, n=gained))
        if "heal" in effect:
            self._heal(user, round(user.max_hp * effect["heal"]))
        for stat, amount in effect.get("self_stage", {}).items():
            self._change_stage(user, stat, amount)
        for stat, amount in effect.get("target_stage", {}).items():
            if target.alive:
                self._change_stage(target, stat, amount)
        if "status" in effect and target.alive and self.rng.random() < effect.get("chance", 1.0):
            self._apply_status(target, effect["status"])
        if "self_status" in effect:
            self._apply_status(user, effect["self_status"], effect.get("self_status_turns"))

    def _pay_cost(self, user: Combatant, skill_id: str, s: dict[str, Any]) -> None:
        if s.get("family") == "mutant":
            user.caffeine = max(0, user.caffeine - s.get("caffeine", 0))
        elif s.get("family") == "street":
            uses = progress.skill_uses(self.state, skill_id)
            self.state.skill_uses[skill_id] = max(0, uses - 1)

    def _deal_damage(self, user: Combatant, target: Combatant, s: dict[str, Any]) -> None:
        uses_mutation = s.get("type") == "radiation" or s.get("family") == "mutant"
        attack = user.stat("mutation" if uses_mutation else "attack")
        defense = target.stat("defense")
        multiplier = 1.0
        if s.get("type") in target.weak:
            multiplier = WEAK_MULTIPLIER
        elif s.get("type") in target.resist:
            multiplier = RESIST_MULTIPLIER
        crit = self.rng.random() < CRIT_CHANCE
        variance = self.rng.uniform(0.85, 1.0)
        damage = s["power"] * attack / defense * DAMAGE_SCALE * variance * multiplier
        if crit:
            damage *= CRIT_MULTIPLIER
        damage = max(1, round(damage))
        target.hp = max(0, target.hp - damage)

        hit = "player" if target.is_player else "enemy"
        self._event(tr("{name} recibe {n} de daño.").format(name=target.name, n=damage), hit=hit)
        if crit:
            self._event(tr("¡Golpe crítico!"))
        if multiplier > 1:
            self._event(tr("¡Es muy eficaz!"))
        elif multiplier < 1:
            self._event(tr("No es muy eficaz..."))
        if "nap" in target.statuses and target.alive:
            del target.statuses["nap"]
            self._event(tr("¡{name} se despierta del golpe!").format(name=target.name))
        self._check_end()

    def _heal(self, who: Combatant, amount: int) -> None:
        amount = min(amount, who.max_hp - who.hp)
        who.hp += amount
        self._event(tr("{name} recupera {n} de vida.").format(name=who.name, n=amount))

    def _change_stage(self, who: Combatant, stat: str, amount: int) -> None:
        old = who.stages.get(stat, 0)
        new = max(MIN_STAGE, min(MAX_STAGE, old + amount))
        stat_name = tr(STAT_NAMES[stat])
        if new == old:
            self._event(
                tr("{stat} de {name} no puede cambiar más.").format(
                    stat=stat_name.capitalize(), name=who.name
                )
            )
            return
        who.stages[stat] = new
        text = tr("Sube {stat} de {name}.") if new > old else tr("Baja {stat} de {name}.")
        self._event(text.format(stat=stat_name, name=who.name))

    def _apply_status(self, who: Combatant, status: str, turns: int | None = None) -> None:
        if status in who.statuses:
            return
        if turns is None:
            turns = STATUS_TURNS[status]
            if status == "nap":
                turns = self.rng.randint(1, 3)
        who.statuses[status] = turns
        name = tr(STATUS_NAMES[status])
        self._event(tr("{who}: {status}.").format(who=who.name, status=name))

    def _use_item(self, item_id: str) -> None:
        self.state.remove_item(item_id)
        self._event(tr("Usas {item}.").format(item=items.name(item_id)))
        use = items.use_effect(item_id)
        if "heal" in use:
            self._heal(self.player, use["heal"])
        if "caffeine" in use:
            gained = min(use["caffeine"], self.player.max_caffeine - self.player.caffeine)
            self.player.caffeine += gained
            self._event(
                tr("{name} recupera {n} de cafeína.").format(name=self.player.name, n=gained)
            )
        for status in use.get("cure", []):
            if status in self.player.statuses:
                del self.player.statuses[status]
                self._event(
                    tr("Ya no estás {status}.").format(status=tr(STATUS_NAMES[status]).lower())
                )

    def _try_flee(self) -> bool:
        if not self.can_flee:
            self._event(tr("¡No puedes huir de este combate!"))
            return False
        self.flee_attempts += 1
        chance = 0.5 + 0.08 * (self.player.stat("speed") - self.enemy.stat("speed"))
        chance += 0.15 * (self.flee_attempts - 1)  # cada intento fallido lo hace más fácil
        if self.rng.random() < max(0.1, min(0.95, chance)):
            self._event(tr("¡Sales corriendo como alma que lleva el diablo!"))
            return True
        self._event(tr("¡No consigues escapar!"))
        return False

    # --- Fin de turno y fin de combate ---

    def _end_of_turn(self) -> None:
        for who in (self.player, self.enemy):
            if not who.alive:
                continue
            for status, divisor in (("radiation", 12), ("poison", 10), ("heat", 16)):
                if status in who.statuses:
                    damage = max(1, who.max_hp // divisor)
                    who.hp = max(0, who.hp - damage)
                    text = tr("{name} sufre {n} de daño ({status}).")
                    status_name = tr(STATUS_NAMES[status]).lower()
                    hit = "player" if who.is_player else "enemy"
                    self._event(text.format(name=who.name, n=damage, status=status_name), hit=hit)
                    self._check_end()
                    if self.outcome:
                        return
                    self._tick_turns(who, status)

    def _tick_turns(self, who: Combatant, status: str) -> None:
        who.statuses[status] -= 1
        if who.statuses[status] <= 0:
            del who.statuses[status]

    def _check_end(self) -> None:
        if not self.enemy.alive:
            self.outcome = "win"
        elif not self.player.alive:
            self.outcome = "lose"

    def _finish(self, outcome: str) -> list[BattleEvent]:
        self.outcome = outcome
        if outcome == "win":
            self._event(tr("¡{name} cae derrotado!").format(name=self.enemy.name))
        elif outcome == "lose":
            self._event(tr("{name} cae redondo al suelo...").format(name=self.player.name))
        self._save_player_state()
        if outcome == "win":
            for text in progress.apply_victory(
                self.state, self.enemy_id, self.enemy_level, self.rng
            ):
                self._event(text)
        return self._events

    def _save_player_state(self) -> None:
        """Al acabar, la vida y la cafeína del combate pasan a la partida."""
        self.state.hp = self.player.hp
        self.state.caffeine = self.player.caffeine

    def _event(self, text: str, hit: str | None = None) -> BattleEvent:
        event = BattleEvent(text, self.player.hp, self.player.caffeine, self.enemy.hp, hit)
        self._events.append(event)
        return event
