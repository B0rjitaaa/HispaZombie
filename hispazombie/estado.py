"""Estado de la partida: interruptores, variables e inventario.

En la Fase 2 se guardará y cargará desde aquí.
"""

from __future__ import annotations


class EstadoJuego:
    def __init__(self) -> None:
        self.interruptores: set[str] = set()
        self.variables: dict[str, int] = {}
        self.inventario: list[str] = []

    def activar(self, interruptor: str) -> None:
        self.interruptores.add(interruptor)

    def activo(self, interruptor: str) -> bool:
        return interruptor in self.interruptores

    def dar_objeto(self, objeto: str) -> None:
        self.inventario.append(objeto)


estado = EstadoJuego()
