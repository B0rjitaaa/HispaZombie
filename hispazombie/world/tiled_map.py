"""Carga de mapas de Tiled en formato JSON (.tmj) con tilesets externos (.tsj).

Se usa JSON (y no .tmx con pytmx) porque solo necesita la biblioteca estándar y funciona
seguro en el navegador. En Tiled: Archivo > Guardar como > "Tiled JSON map files (*.tmj)".

Convenciones del mapa:
  * Capas de tiles "ground" y "objects": se dibujan debajo del personaje.
  * Capa de tiles "above": se dibuja por encima del personaje (copas de árboles, tejados...).
  * Capa de objetos "events": puertas, carteles, cofres, bloqueos, inicio...
  * Propiedad de tile "solid" (bool): no se puede atravesar.
  * Propiedad de tile "bump_text" (string): texto que aparece al chocar contra ese tile.
  * Propiedad del mapa "name" (string): nombre visible del mapa.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

ABOVE_LAYERS = {"above"}

# Bits que usa Tiled en los gid para indicar tiles volteados. Aquí se ignoran.
GID_MASK = 0x1FFFFFFF


def _properties(data: dict) -> dict[str, Any]:
    return {p["name"]: p["value"] for p in data.get("properties", [])}


@dataclass
class Tileset:
    firstgid: int
    image: str  # ruta absoluta al PNG
    tile_width: int
    tile_height: int
    columns: int
    tile_count: int
    tile_properties: dict[int, dict[str, Any]] = field(default_factory=dict)  # por id local

    def contains(self, gid: int) -> bool:
        return self.firstgid <= gid < self.firstgid + self.tile_count

    def source_rect(self, gid: int) -> tuple[int, int, int, int]:
        local = gid - self.firstgid
        return (
            (local % self.columns) * self.tile_width,
            (local // self.columns) * self.tile_height,
            self.tile_width,
            self.tile_height,
        )


@dataclass
class MapEvent:
    id: int
    kind: str  # campo "Clase" del objeto en Tiled
    name: str
    x: int  # en casillas
    y: int
    gid: int  # 0 si no tiene gráfico
    props: dict[str, Any]
    width: int = 1  # tamaño en casillas (para zonas rectangulares)
    height: int = 1

    def contains(self, x: int, y: int) -> bool:
        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height


@dataclass
class TileLayer:
    name: str
    data: list[int]  # gid por casilla, fila a fila; 0 = vacío
    visible: bool = True


class TiledMap:
    def __init__(self, file_path: str) -> None:
        self.path = file_path
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        if data.get("infinite"):
            raise ValueError(f"{file_path}: los mapas infinitos no están soportados")

        self.width: int = data["width"]
        self.height: int = data["height"]
        self.tile: int = data["tilewidth"]
        self.properties = _properties(data)
        self.tilesets = [self._load_tileset(ts) for ts in data["tilesets"]]
        self.layers: list[TileLayer] = []
        self.events: list[MapEvent] = []

        for layer in data["layers"]:
            if layer["type"] == "tilelayer":
                if not isinstance(layer["data"], list):
                    raise ValueError(
                        f"{file_path}: la capa '{layer['name']}' debe guardarse en formato CSV"
                    )
                self.layers.append(
                    TileLayer(layer["name"], layer["data"], layer.get("visible", True))
                )
            elif layer["type"] == "objectgroup":
                for obj in layer["objects"]:
                    self.events.append(self._load_event(obj))

    @property
    def name(self) -> str:
        """Nombre visible del mapa (sin traducir)."""
        return self.properties.get("name", os.path.splitext(os.path.basename(self.path))[0])

    def _load_tileset(self, ref: dict) -> Tileset:
        base = os.path.dirname(self.path)
        if "source" in ref:
            ts_path = os.path.normpath(os.path.join(base, ref["source"]))
            with open(ts_path, encoding="utf-8") as f:
                ts = json.load(f)
            base = os.path.dirname(ts_path)
        else:
            ts = ref
        props = {t["id"]: _properties(t) for t in ts.get("tiles", [])}
        return Tileset(
            firstgid=ref["firstgid"],
            image=os.path.normpath(os.path.join(base, ts["image"])),
            tile_width=ts["tilewidth"],
            tile_height=ts["tileheight"],
            columns=ts["columns"],
            tile_count=ts["tilecount"],
            tile_properties=props,
        )

    def _load_event(self, obj: dict) -> MapEvent:
        gid = obj.get("gid", 0) & GID_MASK
        x, y = obj["x"], obj["y"]
        if gid:
            y -= obj.get("height", self.tile)  # los objetos-tile se anclan por abajo
        return MapEvent(
            id=obj["id"],
            kind=obj.get("type") or obj.get("class") or "",
            name=obj.get("name", ""),
            x=int(round(x / self.tile)),
            y=int(round(y / self.tile)),
            gid=gid,
            props=_properties(obj),
            width=max(1, int(round(obj.get("width", self.tile) / self.tile))),
            height=max(1, int(round(obj.get("height", self.tile) / self.tile))),
        )

    # --- Consultas ---

    def tileset_for(self, gid: int) -> Tileset | None:
        for ts in self.tilesets:
            if ts.contains(gid):
                return ts
        return None

    def tile_props(self, gid: int) -> dict[str, Any]:
        ts = self.tileset_for(gid)
        if ts is None:
            return {}
        return ts.tile_properties.get(gid - ts.firstgid, {})

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def gids_at(self, x: int, y: int) -> list[int]:
        i = y * self.width + x
        return [layer.data[i] & GID_MASK for layer in self.layers if layer.data[i]]

    def is_solid(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return True
        return any(self.tile_props(g).get("solid") for g in self.gids_at(x, y))

    def bump_text(self, x: int, y: int) -> str | None:
        if not self.in_bounds(x, y):
            return None
        for g in reversed(self.gids_at(x, y)):
            text = self.tile_props(g).get("bump_text")
            if text:
                return text
        return None

    def events_at(self, x: int, y: int) -> list[MapEvent]:
        return [e for e in self.events if e.x == x and e.y == y]

    def events_of_kind(self, kind: str) -> list[MapEvent]:
        return [e for e in self.events if e.kind == kind]
