"""Estado de la partida: interruptores, variables e inventario.

En la Fase 2 se guardará y cargará desde aquí.
"""

from __future__ import annotations


class GameState:
    def __init__(self) -> None:
        self.switches: set[str] = set()  # interruptores de RPG Maker
        self.variables: dict[str, int] = {}
        self.inventory: list[str] = []  # ids de objetos (ver assets/data/items.json)

    def reset(self) -> None:
        self.__init__()

    def turn_on(self, switch: str) -> None:
        self.switches.add(switch)

    def is_on(self, switch: str) -> bool:
        return switch in self.switches

    def give_item(self, item_id: str) -> None:
        self.inventory.append(item_id)


game_state = GameState()
