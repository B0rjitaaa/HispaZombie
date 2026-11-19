"""Movimiento en cuadrícula, casilla a casilla, como en RPG Maker.

Es lógica pura (sin pygame), así se puede probar con pytest.
"""

from __future__ import annotations

from collections.abc import Callable

VECTORES: dict[str, tuple[int, int]] = {
    "arriba": (0, -1),
    "abajo": (0, 1),
    "izquierda": (-1, 0),
    "derecha": (1, 0),
}


class MovimientoCuadricula:
    """Posición en casillas con desplazamiento suave entre una casilla y la siguiente.

    `velocidad` está en casillas por segundo (RPG Maker usa unas 4 a velocidad normal).
    """

    def __init__(self, x: int, y: int, velocidad: float = 4.0) -> None:
        self.x = x
        self.y = y
        self.velocidad = velocidad
        self.mirando = "abajo"
        self._destino: tuple[int, int] | None = None
        self._progreso = 0.0  # 0 -> 1 durante el paso entre casillas

    @property
    def moviendose(self) -> bool:
        return self._destino is not None

    def intentar_mover(self, direccion: str, es_transitable: Callable[[int, int], bool]) -> bool:
        """Empieza un paso si está quieto y la casilla destino es transitable.

        Aunque no pueda moverse, se gira hacia esa dirección (como en RPG Maker).
        """
        if self.moviendose:
            return False
        self.mirando = direccion
        dx, dy = VECTORES[direccion]
        nx, ny = self.x + dx, self.y + dy
        if not es_transitable(nx, ny):
            return False
        self._destino = (nx, ny)
        self._progreso = 0.0
        return True

    def actualizar(self, dt: float) -> None:
        if self._destino is None:
            return
        self._progreso += self.velocidad * dt
        if self._progreso >= 1.0:
            self.x, self.y = self._destino
            self._destino = None
            self._progreso = 0.0

    def posicion_visual(self) -> tuple[float, float]:
        """Posición en casillas (con decimales) para dibujar a mitad de paso."""
        if self._destino is None:
            return float(self.x), float(self.y)
        dx = self._destino[0] - self.x
        dy = self._destino[1] - self.y
        return self.x + dx * self._progreso, self.y + dy * self._progreso
