"""Intérprete de scripts de eventos.

Un script es una lista de comandos JSON que se ejecutan en orden. Algunos comandos
esperan (a que el jugador cierre un mensaje, elija una opción, termine un movimiento...),
así que el intérprete se ejecuta poco a poco, frame a frame, llamando a update().

Comandos disponibles (los textos se escriben en español y se traducen al mostrarlos):

  {"cmd": "text", "text": "..."}                      Mensaje. "@retrato" al principio de
                                                        una página muestra un retrato.
  {"cmd": "choice", "text": "¿...?",                  Opciones. "text" (pregunta) es opcional.
   "options": [{"label": "Sí", "then": [...]},          Cada opción ejecuta su lista "then".
               {"label": "No", "then": [...]}],         "cancel": índice de la opción que se
   "cancel": 1}                                         elige al pulsar Cancelar (opcional).
  {"cmd": "if", "cond": {...}, "then": [...], "else": [...]}
  {"cmd": "switch_on", "id": "..."} / {"cmd": "switch_off", "id": "..."}
  {"cmd": "set_variable", "id": "...", "value": 3}
  {"cmd": "add_variable", "id": "...", "amount": 1}
  {"cmd": "give_item", "id": "...", "amount": 1, "silent": false}
  {"cmd": "remove_item", "id": "...", "amount": 1}
  {"cmd": "give_coins", "amount": 5, "silent": false}
  {"cmd": "remove_coins", "amount": 5}
  {"cmd": "move", "target": "this", "route": ["left", "left"], "wait": true}
                                                        target: "this", "player" o el nombre
                                                        de un evento del mapa.
  {"cmd": "face", "target": "this", "direction": "down"}  direction también puede ser
                                                        "player" (mirar al jugador).
  {"cmd": "wait", "seconds": 0.5}
  {"cmd": "teleport", "map": "...", "x": 1, "y": 2, "facing": "down"}  Termina el evento.
  {"cmd": "battle", "enemy": "metro_rat", "level": 4, "can_flee": false,
   "on_win": [...], "on_flee": [...]}                  Combate. Si se pierde, el protagonista
                                                        despierta en el último lugar seguro y
                                                        el evento termina.
  {"cmd": "learn_skill", "id": "flip_flop"}            Aprende una habilidad (con mensaje).
  {"cmd": "rest"}                                       Descanso: vida, cafeína y usos al
                                                        máximo; este sitio pasa a ser el lugar
                                                        seguro donde despertar si pierdes.
  {"cmd": "end"}                                        Termina el evento.

Condiciones de "if" (se pueden combinar con "all" y "any"):
  {"switch": "id"}            interruptor encendido
  {"switch_off": "id"}        interruptor apagado
  {"variable": "id", "op": ">=", "value": 3}     op: == != < <= > >=
  {"has_item": "id", "amount": 1}
  {"coins_min": 5}
  {"knows_skill": "id"}
  {"all": [cond, cond]}  /  {"any": [cond, cond]}  /  {"not": cond}
"""

from __future__ import annotations

import operator
from collections.abc import Callable, Generator
from typing import Any, Protocol

from state import GameState

Waiter = Callable[[], bool]  # devuelve True cuando ya se puede continuar
Script = list[dict[str, Any]]

OPERATORS = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}


class EventContext(Protocol):
    """Lo que el intérprete necesita del juego. La escena de mapa lo implementa."""

    state: GameState

    def show_text(self, text: str) -> Waiter: ...

    def show_choice(self, prompt: str, labels: list[str], cancel: int | None) -> Choice: ...

    def item_obtained(self, item_id: str, amount: int) -> Waiter: ...

    def coins_obtained(self, amount: int) -> Waiter: ...

    def move(self, target: str, route: list[str]) -> Waiter: ...

    def face(self, target: str, direction: str) -> None: ...

    def teleport(self, map_id: str, x: int, y: int, facing: str | None) -> None: ...

    def start_battle(self, enemy_id: str, level: int, can_flee: bool) -> BattleResult: ...

    def skill_learned(self, skill_id: str, equipped: bool) -> Waiter: ...

    def rest(self) -> None: ...


class Choice:
    """Resultado de una elección: `index` se rellena cuando el jugador elige."""

    def __init__(self) -> None:
        self.index: int | None = None

    def done(self) -> bool:
        return self.index is not None


class BattleResult:
    """Resultado de un combate: `outcome` se rellena al terminar ("win", "lose", "fled")."""

    def __init__(self) -> None:
        self.outcome: str | None = None

    def done(self) -> bool:
        return self.outcome is not None


class ScriptError(Exception):
    pass


def check(cond: dict[str, Any], state: GameState) -> bool:
    """Evalúa una condición de un comando "if"."""
    if "all" in cond:
        return all(check(c, state) for c in cond["all"])
    if "any" in cond:
        return any(check(c, state) for c in cond["any"])
    if "not" in cond:
        return not check(cond["not"], state)
    if "switch" in cond:
        return state.is_on(cond["switch"])
    if "switch_off" in cond:
        return not state.is_on(cond["switch_off"])
    if "variable" in cond:
        op = OPERATORS[cond.get("op", "==")]
        return op(state.get_variable(cond["variable"]), cond["value"])
    if "has_item" in cond:
        return state.item_count(cond["has_item"]) >= cond.get("amount", 1)
    if "coins_min" in cond:
        return state.coins >= cond["coins_min"]
    if "knows_skill" in cond:
        return cond["knows_skill"] in state.learned_skills
    raise ScriptError(f"Condición desconocida: {cond}")


class Interpreter:
    def __init__(self, context: EventContext, script: Script) -> None:
        self.context = context
        self.done = False
        self._waiting: Waiter | None = None
        self._steps = self._run(script)

    def update(self) -> None:
        """Avanza el script hasta que tenga que esperar o termine."""
        while not self.done:
            if self._waiting is not None:
                if not self._waiting():
                    return
                self._waiting = None
            try:
                self._waiting = next(self._steps)
            except StopIteration:
                self.done = True

    # --- Ejecución ---

    def _run(self, script: Script) -> Generator[Waiter | None, None, None]:
        try:
            yield from self._run_list(script)
        except _EndEvent:
            pass

    def _run_list(self, script: Script) -> Generator[Waiter | None, None, None]:
        for command in script:
            name = command.get("cmd")
            handler = getattr(self, f"_cmd_{name}", None)
            if handler is None:
                raise ScriptError(f"Comando desconocido: {name!r}")
            yield from handler(command)

    # --- Comandos ---

    def _cmd_text(self, c):
        yield self.context.show_text(c["text"])

    def _cmd_choice(self, c):
        options = c["options"]
        choice = self.context.show_choice(
            c.get("text", ""), [o["label"] for o in options], c.get("cancel")
        )
        yield choice.done
        yield from self._run_list(options[choice.index].get("then", []))

    def _cmd_if(self, c):
        branch = c.get("then", []) if check(c["cond"], self.context.state) else c.get("else", [])
        yield from self._run_list(branch)

    def _cmd_switch_on(self, c):
        self.context.state.turn_on(c["id"])
        yield from ()

    def _cmd_switch_off(self, c):
        self.context.state.turn_off(c["id"])
        yield from ()

    def _cmd_set_variable(self, c):
        self.context.state.set_variable(c["id"], c["value"])
        yield from ()

    def _cmd_add_variable(self, c):
        state = self.context.state
        state.set_variable(c["id"], state.get_variable(c["id"]) + c.get("amount", 1))
        yield from ()

    def _cmd_give_item(self, c):
        amount = c.get("amount", 1)
        self.context.state.give_item(c["id"], amount)
        if not c.get("silent"):
            yield self.context.item_obtained(c["id"], amount)

    def _cmd_remove_item(self, c):
        self.context.state.remove_item(c["id"], c.get("amount", 1))
        yield from ()

    def _cmd_give_coins(self, c):
        self.context.state.give_coins(c["amount"])
        if not c.get("silent"):
            yield self.context.coins_obtained(c["amount"])

    def _cmd_remove_coins(self, c):
        self.context.state.remove_coins(c["amount"])
        yield from ()

    def _cmd_move(self, c):
        waiter = self.context.move(c.get("target", "this"), list(c["route"]))
        if c.get("wait", True):
            yield waiter

    def _cmd_face(self, c):
        self.context.face(c.get("target", "this"), c["direction"])
        yield from ()

    def _cmd_wait(self, c):
        # El contexto no lleva el tiempo: se cuenta en frames a 60 FPS.
        frames = [max(1, round(c["seconds"] * 60))]

        def waiter() -> bool:
            frames[0] -= 1
            return frames[0] <= 0

        yield waiter

    def _cmd_teleport(self, c):
        self.context.teleport(c["map"], c["x"], c["y"], c.get("facing"))
        raise _EndEvent

    def _cmd_battle(self, c):
        result = self.context.start_battle(c["enemy"], c.get("level", 1), c.get("can_flee", True))
        yield result.done
        if result.outcome == "win":
            yield from self._run_list(c.get("on_win", []))
        elif result.outcome == "fled":
            yield from self._run_list(c.get("on_flee", []))
        else:  # derrota: el contexto se encarga de despertar al protagonista
            raise _EndEvent

    def _cmd_learn_skill(self, c):
        from battle import progress  # import aquí: el intérprete no depende del combate

        state = self.context.state
        if progress.learn_skill(state, c["id"]):
            yield self.context.skill_learned(c["id"], c["id"] in state.equipped_skills)

    def _cmd_rest(self, c):
        self.context.rest()
        yield from ()

    def _cmd_end(self, c):
        raise _EndEvent
        yield  # pragma: no cover - convierte la función en generador


class _EndEvent(Exception):
    """Termina el script en curso."""
