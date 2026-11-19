"""Utilidades de texto: partir en líneas y en páginas de diálogo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class MeasurableFont(Protocol):
    def size(self, text: str) -> tuple[int, int]: ...


def wrap(text: str, font: MeasurableFont, max_width: int) -> list[str]:
    """Parte el texto en líneas que caben en `max_width` píxeles. Respeta los saltos de línea."""
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


@dataclass
class Page:
    text: str
    portrait: str | None = None


def pages_from(text: str) -> list[Page]:
    """Convierte el texto de un evento en páginas de diálogo.

    Formato (pensado para escribirlo cómodamente en Tiled):
      * Una línea en blanco separa páginas.
      * Si una página empieza por "@nombre", se muestra el retrato assets/portraits/nombre.png.
    """
    pages: list[Page] = []
    for block in text.replace("\r\n", "\n").split("\n\n"):
        block = block.strip("\n")
        if not block.strip():
            continue
        portrait = None
        if block.startswith("@"):
            first, _, rest = block.partition("\n")
            portrait = first[1:].strip() or None
            block = rest
        pages.append(Page(block.strip(), portrait))
    return pages
