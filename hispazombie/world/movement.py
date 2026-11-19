"""Movimiento en cuadrícula, casilla a casilla, como en RPG Maker.

Es lógica pura (sin pygame), así se puede probar con pytest.
"""

from __future__ import annotations

from collections.abc import Callable

VECTORS: dict[str, tuple[int, int]] = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}


class GridMovement:
    """Posición en casillas con desplazamiento suave entre una casilla y la siguiente.

    `speed` está en casillas por segundo (RPG Maker usa unas 4 a velocidad normal).
    """

    def __init__(self, x: int, y: int, speed: float = 4.0) -> None:
        self.x = x
        self.y = y
        self.speed = speed
        self.facing = "down"
        self._target: tuple[int, int] | None = None
        self._progress = 0.0  # 0 -> 1 durante el paso entre casillas
        self.steps = 0  # pasos completados (sirve para alternar la animación)

    @property
    def moving(self) -> bool:
        return self._target is not None

    @property
    def progress(self) -> float:
        return self._progress

    def place(self, x: int, y: int, facing: str | None = None) -> None:
        """Teletransporta a una casilla, cancelando el paso en curso."""
        self.x, self.y = x, y
        self._target = None
        self._progress = 0.0
        if facing:
            self.facing = facing

    def tile_ahead(self) -> tuple[int, int]:
        dx, dy = VECTORS[self.facing]
        return self.x + dx, self.y + dy

    def try_move(self, direction: str, is_walkable: Callable[[int, int], bool]) -> bool:
        """Empieza un paso si está quieto y la casilla destino es transitable.

        Aunque no pueda moverse, se gira hacia esa dirección (como en RPG Maker).
        """
        if self.moving:
            return False
        self.facing = direction
        nx, ny = self.tile_ahead()
        if not is_walkable(nx, ny):
            return False
        self._target = (nx, ny)
        self._progress = 0.0
        return True

    def update(self, dt: float) -> bool:
        """Avanza el paso en curso. Devuelve True en el frame en que llega a la casilla."""
        if self._target is None:
            return False
        self._progress += self.speed * dt
        if self._progress >= 1.0:
            self.x, self.y = self._target
            self._target = None
            self._progress = 0.0
            self.steps += 1
            return True
        return False

    def visual_position(self) -> tuple[float, float]:
        """Posición en casillas (con decimales) para dibujar a mitad de paso."""
        if self._target is None:
            return float(self.x), float(self.y)
        dx = self._target[0] - self.x
        dy = self._target[1] - self.y
        return self.x + dx * self._progress, self.y + dy * self._progress
