"""Texto en alta resolución (HD) por encima del pixel art.

El pixel art se dibuja en la pantalla virtual (p. ej. 480x270) y se escala. El texto, en
cambio, se dibuja a la resolución real de la ventana para que se lea nítido y suave.

Uso desde una escena (coordenadas y tamaños en píxeles VIRTUALES, como el resto):
    hd_text.layer.draw("Hola", x=10, y=20, size=12)

El motor llama a layer.render() al final de cada frame, después de escalar la pantalla.
Consecuencia: el texto HD siempre queda por encima de todo el pixel art del frame.
"""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from engine import resources

# Fuente de la interfaz: Atkinson Hyperlegible (licencia SIL OFL, ver assets/fonts/).
UI_FONT = "AtkinsonHyperlegible-Regular.ttf"
UI_FONT_BOLD = "AtkinsonHyperlegible-Bold.ttf"

# Las medidas se calculan con la fuente a este múltiplo del tamaño virtual, para que el
# ajuste de líneas sea el mismo sea cual sea el tamaño de la ventana.
_MEASURE_SCALE = 4


def _font_px(size: float, scale: float) -> int:
    return max(1, round(size * scale))


class HDFont:
    """Fuente HD medida en píxeles virtuales (compatible con engine.text.wrap)."""

    def __init__(self, size: float, filename: str = UI_FONT) -> None:
        self.size_px = size
        self.filename = filename
        self._measure = resources.font(_font_px(size, _MEASURE_SCALE), filename)

    def size(self, text: str) -> tuple[float, float]:
        w, h = self._measure.size(text)
        return w / _MEASURE_SCALE, h / _MEASURE_SCALE


@dataclass
class _TextItem:
    text: str
    x: float
    y: float
    size: float
    color: tuple[int, int, int]
    alpha: int
    filename: str


class TextLayer:
    def __init__(self) -> None:
        self._items: list[_TextItem] = []

    def draw(
        self,
        text: str,
        x: float,
        y: float,
        size: float,
        color: tuple[int, int, int] = (255, 255, 255),
        alpha: int = 255,
        filename: str = UI_FONT,
    ) -> None:
        if text and alpha > 0:
            self._items.append(_TextItem(text, x, y, size, color, alpha, filename))

    def clear(self) -> None:
        self._items.clear()

    def render(self, window: pygame.Surface, offset: tuple[int, int], scale: float) -> None:
        """Dibuja los textos encolados en la ventana real y vacía la cola."""
        ox, oy = offset
        for item in self._items:
            font = resources.font(_font_px(item.size, scale), item.filename)
            surface = font.render(item.text, True, item.color)
            if item.alpha < 255:
                surface.set_alpha(item.alpha)
            window.blit(surface, (ox + round(item.x * scale), oy + round(item.y * scale)))
        self.clear()


layer = TextLayer()
