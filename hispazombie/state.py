"""Estado de la partida: interruptores, variables, inventario, fichas y posición.

Todo lo que deba sobrevivir a guardar y cargar vive aquí y se serializa con to_dict().
"""

from __future__ import annotations

from typing import Any

SAVE_VERSION = 1


class GameState:
    def __init__(self) -> None:
        self.switches: set[str] = set()  # interruptores de RPG Maker
        self.variables: dict[str, int] = {}
        self.inventory: dict[str, int] = {}  # id de objeto -> cantidad (ver items.json)
        self.coins = 0  # fichas de cerámica: la moneda del juego
        # Posición de eventos que se han movido con un script: "mapa:id" -> [x, y, facing].
        self.event_positions: dict[str, list] = {}
        # Dónde está el jugador (se actualiza al guardar).
        self.map_id = "bunker"
        self.player_x: int | None = None
        self.player_y: int | None = None
        self.player_facing = "down"
        self.play_time = 0.0  # segundos jugados

    def reset(self) -> None:
        self.__init__()

    # --- Interruptores y variables ---

    def turn_on(self, switch: str) -> None:
        self.switches.add(switch)

    def turn_off(self, switch: str) -> None:
        self.switches.discard(switch)

    def is_on(self, switch: str) -> bool:
        return switch in self.switches

    def get_variable(self, name: str) -> int:
        return self.variables.get(name, 0)

    def set_variable(self, name: str, value: int) -> None:
        self.variables[name] = value

    # --- Inventario ---

    def give_item(self, item_id: str, amount: int = 1) -> None:
        self.inventory[item_id] = self.inventory.get(item_id, 0) + amount

    def remove_item(self, item_id: str, amount: int = 1) -> bool:
        """Quita objetos. Devuelve False (y no quita nada) si no hay suficientes."""
        have = self.inventory.get(item_id, 0)
        if have < amount:
            return False
        if have == amount:
            del self.inventory[item_id]
        else:
            self.inventory[item_id] = have - amount
        return True

    def item_count(self, item_id: str) -> int:
        return self.inventory.get(item_id, 0)

    # --- Fichas ---

    def give_coins(self, amount: int) -> None:
        self.coins += amount

    def remove_coins(self, amount: int) -> bool:
        if self.coins < amount:
            return False
        self.coins -= amount
        return True

    # --- Guardar y cargar ---

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": SAVE_VERSION,
            "switches": sorted(self.switches),
            "variables": dict(self.variables),
            "inventory": dict(self.inventory),
            "coins": self.coins,
            "event_positions": dict(self.event_positions),
            "map_id": self.map_id,
            "player_x": self.player_x,
            "player_y": self.player_y,
            "player_facing": self.player_facing,
            "play_time": self.play_time,
        }

    def load_dict(self, data: dict[str, Any]) -> None:
        if data.get("version") != SAVE_VERSION:
            raise ValueError(f"Versión de partida guardada no soportada: {data.get('version')}")
        self.reset()
        self.switches = set(data["switches"])
        self.variables = dict(data["variables"])
        self.inventory = dict(data["inventory"])
        self.coins = data["coins"]
        self.event_positions = dict(data["event_positions"])
        self.map_id = data["map_id"]
        self.player_x = data["player_x"]
        self.player_y = data["player_y"]
        self.player_facing = data["player_facing"]
        self.play_time = data.get("play_time", 0.0)


game_state = GameState()
