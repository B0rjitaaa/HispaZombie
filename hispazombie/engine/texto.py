"""Utilidades de texto: partir en líneas y en páginas de diálogo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class FuenteMedible(Protocol):
    def size(self, texto: str) -> tuple[int, int]: ...


def envolver(texto: str, fuente: FuenteMedible, ancho_max: int) -> list[str]:
    """Parte el texto en líneas que caben en `ancho_max` píxeles. Respeta los saltos de línea."""
    lineas: list[str] = []
    for parrafo in texto.split("\n"):
        palabras = parrafo.split()
        if not palabras:
            lineas.append("")
            continue
        actual = palabras[0]
        for palabra in palabras[1:]:
            prueba = f"{actual} {palabra}"
            if fuente.size(prueba)[0] <= ancho_max:
                actual = prueba
            else:
                lineas.append(actual)
                actual = palabra
        lineas.append(actual)
    return lineas


@dataclass
class Pagina:
    texto: str
    retrato: str | None = None


def paginas_de(texto: str) -> list[Pagina]:
    """Convierte el texto de un evento en páginas de diálogo.

    Formato (pensado para escribirlo cómodamente en Tiled):
      * Una línea en blanco separa páginas.
      * Si una página empieza por "@nombre", se muestra el retrato assets/retratos/nombre.png.
    """
    paginas: list[Pagina] = []
    for bloque in texto.replace("\r\n", "\n").split("\n\n"):
        bloque = bloque.strip("\n")
        if not bloque.strip():
            continue
        retrato = None
        if bloque.startswith("@"):
            primera, _, resto = bloque.partition("\n")
            retrato = primera[1:].strip() or None
            bloque = resto
        paginas.append(Pagina(bloque.strip(), retrato))
    return paginas
