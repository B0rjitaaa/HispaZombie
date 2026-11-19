"""Pruebas del intérprete de eventos con un contexto falso (sin pygame)."""

import pytest

from events.interpreter import Choice, Interpreter, ScriptError, check
from state import GameState


class FakeContext:
    """Contexto mínimo: registra lo que pasa y deja elegir opciones desde el test."""

    def __init__(self) -> None:
        self.state = GameState()
        self.log: list[str] = []
        self.pending: list[object] = []  # mensajes/opciones esperando al "jugador"
        self.choices: list[int] = []  # respuestas que dará el jugador, en orden

    def _wait(self, entry: str):
        self.log.append(entry)
        flag = {"done": False}
        self.pending.append(flag)
        return lambda: flag["done"]

    def show_text(self, text):
        return self._wait(f"text:{text}")

    def show_choice(self, prompt, labels, cancel):
        self.log.append(f"choice:{'|'.join(labels)}")
        choice = Choice()
        choice.index = self.choices.pop(0)
        return choice

    def item_obtained(self, item_id, amount):
        return self._wait(f"item:{item_id}x{amount}")

    def coins_obtained(self, amount):
        return self._wait(f"coins:{amount}")

    def move(self, target, route):
        self.log.append(f"move:{target}:{','.join(route)}")
        return lambda: True

    def face(self, target, direction):
        self.log.append(f"face:{target}:{direction}")

    def teleport(self, map_id, x, y, facing):
        self.log.append(f"teleport:{map_id}:{x},{y}")


def run(ctx: FakeContext, script) -> Interpreter:
    """Ejecuta el script cerrando cada mensaje en cuanto aparece."""
    interpreter = Interpreter(ctx, script)
    for _ in range(100):
        interpreter.update()
        if interpreter.done:
            break
        for flag in ctx.pending:
            flag["done"] = True
        ctx.pending.clear()
    return interpreter


def test_text_waits_until_closed():
    ctx = FakeContext()
    interpreter = Interpreter(ctx, [{"cmd": "text", "text": "Uno"}, {"cmd": "text", "text": "Dos"}])
    interpreter.update()
    assert ctx.log == ["text:Uno"]  # el segundo mensaje espera a que se cierre el primero
    interpreter.update()
    assert ctx.log == ["text:Uno"]
    ctx.pending[0]["done"] = True
    interpreter.update()
    assert ctx.log == ["text:Uno", "text:Dos"]


def test_choice_runs_selected_branch():
    ctx = FakeContext()
    ctx.choices = [1]
    script = [
        {
            "cmd": "choice",
            "options": [
                {"label": "Sí", "then": [{"cmd": "text", "text": "dijo sí"}]},
                {"label": "No", "then": [{"cmd": "text", "text": "dijo no"}]},
            ],
        }
    ]
    run(ctx, script)
    assert ctx.log == ["choice:Sí|No", "text:dijo no"]


def test_switches_variables_items_and_coins():
    ctx = FakeContext()
    script = [
        {"cmd": "switch_on", "id": "a"},
        {"cmd": "set_variable", "id": "v", "value": 2},
        {"cmd": "add_variable", "id": "v", "amount": 3},
        {"cmd": "give_item", "id": "water_bottle", "amount": 2},
        {"cmd": "remove_item", "id": "water_bottle"},
        {"cmd": "give_coins", "amount": 7, "silent": True},
        {"cmd": "remove_coins", "amount": 2},
        {"cmd": "switch_off", "id": "a"},
    ]
    assert run(ctx, script).done
    s = ctx.state
    assert not s.is_on("a")
    assert s.get_variable("v") == 5
    assert s.item_count("water_bottle") == 1
    assert s.coins == 5
    assert ctx.log == ["item:water_bottlex2"]  # las fichas eran "silent"


def test_if_and_conditions():
    ctx = FakeContext()
    ctx.state.give_coins(3)
    script = [
        {
            "cmd": "if",
            "cond": {"all": [{"coins_min": 3}, {"not": {"switch": "x"}}]},
            "then": [{"cmd": "text", "text": "rico"}],
            "else": [{"cmd": "text", "text": "pobre"}],
        }
    ]
    run(ctx, script)
    assert ctx.log == ["text:rico"]

    s = GameState()
    s.set_variable("trust", 2)
    assert check({"variable": "trust", "op": ">=", "value": 2}, s)
    assert not check({"variable": "trust", "op": "<", "value": 2}, s)
    assert check({"any": [{"switch": "nope"}, {"switch_off": "nope"}]}, s)
    assert not check({"has_item": "water_bottle"}, s)


def test_end_and_teleport_stop_the_script():
    ctx = FakeContext()
    run(ctx, [{"cmd": "end"}, {"cmd": "text", "text": "nunca"}])
    assert ctx.log == []

    ctx = FakeContext()
    run(ctx, [{"cmd": "teleport", "map": "bunker", "x": 1, "y": 2}, {"cmd": "text", "text": "x"}])
    assert ctx.log == ["teleport:bunker:1,2"]


def test_wait_counts_frames():
    ctx = FakeContext()
    interpreter = Interpreter(ctx, [{"cmd": "wait", "seconds": 0.05}])  # 3 frames
    for _ in range(3):
        assert not interpreter.done
        interpreter.update()
    interpreter.update()
    assert interpreter.done


def test_unknown_command_fails_clearly():
    ctx = FakeContext()
    with pytest.raises(ScriptError):
        run(ctx, [{"cmd": "volar"}])
