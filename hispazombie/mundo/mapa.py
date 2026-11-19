"""Carga de mapas de Tiled en formato JSON (.tmj) con tilesets externos (.tsj).

Se usa JSON (y no .tmx con pytmx) porque solo necesita la biblioteca estándar y funciona
seguro en el navegador. En Tiled: Archivo > Guardar como > "Tiled JSON map files (*.tmj)".

Convenciones del mapa:
  * Capas de tiles "suelo" y "objetos": se dibujan debajo del personaje.
  * Capa de tiles "encima": se dibuja por encima del personaje (copas de árboles, tejados...).
  * Capa de objetos "eventos": puertas, carteles, cofres, bloqueos, inicio...
  * Propiedad de tile "solido" (bool): no se puede atravesar.
  * Propiedad de tile "texto_choque" (string): texto al chocar contra ese tile.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

CAPAS_ENCIMA = {"encima"}

# Bits que usa Tiled en los gid para indicar tiles volteados. Aquí se ignoran.
MASCARA_GID = 0x1FFFFFFF


def _propiedades(datos: dict) -> dict[str, Any]:
    return {p["name"]: p["value"] for p in datos.get("properties", [])}


@dataclass
class Tileset:
    firstgid: int
    imagen: str  # ruta absoluta al PNG
    ancho_tile: int
    alto_tile: int
    columnas: int
    num_tiles: int
    propiedades: dict[int, dict[str, Any]] = field(default_factory=dict)  # por id local

    def contiene(self, gid: int) -> bool:
        return self.firstgid <= gid < self.firstgid + self.num_tiles

    def rect_origen(self, gid: int) -> tuple[int, int, int, int]:
        local = gid - self.firstgid
        return (
            (local % self.columnas) * self.ancho_tile,
            (local // self.columnas) * self.alto_tile,
            self.ancho_tile,
            self.alto_tile,
        )


@dataclass
class Evento:
    id: int
    tipo: str
    nombre: str
    x: int  # en casillas
    y: int
    gid: int  # 0 si no tiene gráfico
    props: dict[str, Any]


@dataclass
class CapaTiles:
    nombre: str
    datos: list[int]  # gid por casilla, fila a fila; 0 = vacío
    visible: bool = True


class Mapa:
    def __init__(self, ruta_archivo: str) -> None:
        self.ruta = ruta_archivo
        with open(ruta_archivo, encoding="utf-8") as f:
            datos = json.load(f)

        if datos.get("infinite"):
            raise ValueError(f"{ruta_archivo}: los mapas infinitos no están soportados")

        self.ancho: int = datos["width"]
        self.alto: int = datos["height"]
        self.tile: int = datos["tilewidth"]
        self.propiedades = _propiedades(datos)
        self.tilesets = [self._cargar_tileset(ts) for ts in datos["tilesets"]]
        self.capas: list[CapaTiles] = []
        self.eventos: list[Evento] = []

        for capa in datos["layers"]:
            if capa["type"] == "tilelayer":
                if not isinstance(capa["data"], list):
                    raise ValueError(
                        f"{ruta_archivo}: la capa '{capa['name']}' debe guardarse en formato CSV"
                    )
                self.capas.append(CapaTiles(capa["name"], capa["data"], capa.get("visible", True)))
            elif capa["type"] == "objectgroup":
                for obj in capa["objects"]:
                    self.eventos.append(self._cargar_evento(obj))

    @property
    def nombre(self) -> str:
        return self.propiedades.get("nombre", os.path.splitext(os.path.basename(self.ruta))[0])

    def _cargar_tileset(self, ref: dict) -> Tileset:
        base = os.path.dirname(self.ruta)
        if "source" in ref:
            ruta_ts = os.path.normpath(os.path.join(base, ref["source"]))
            with open(ruta_ts, encoding="utf-8") as f:
                ts = json.load(f)
            base = os.path.dirname(ruta_ts)
        else:
            ts = ref
        props = {t["id"]: _propiedades(t) for t in ts.get("tiles", [])}
        return Tileset(
            firstgid=ref["firstgid"],
            imagen=os.path.normpath(os.path.join(base, ts["image"])),
            ancho_tile=ts["tilewidth"],
            alto_tile=ts["tileheight"],
            columnas=ts["columns"],
            num_tiles=ts["tilecount"],
            propiedades=props,
        )

    def _cargar_evento(self, obj: dict) -> Evento:
        gid = obj.get("gid", 0) & MASCARA_GID
        x, y = obj["x"], obj["y"]
        if gid:
            y -= obj.get("height", self.tile)  # los objetos-tile se anclan por abajo
        return Evento(
            id=obj["id"],
            tipo=obj.get("type") or obj.get("class") or "",
            nombre=obj.get("name", ""),
            x=int(round(x / self.tile)),
            y=int(round(y / self.tile)),
            gid=gid,
            props=_propiedades(obj),
        )

    # --- Consultas ---

    def tileset_de(self, gid: int) -> Tileset | None:
        for ts in self.tilesets:
            if ts.contiene(gid):
                return ts
        return None

    def props_tile(self, gid: int) -> dict[str, Any]:
        ts = self.tileset_de(gid)
        if ts is None:
            return {}
        return ts.propiedades.get(gid - ts.firstgid, {})

    def dentro(self, x: int, y: int) -> bool:
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def gids_en(self, x: int, y: int) -> list[int]:
        i = y * self.ancho + x
        return [c.datos[i] & MASCARA_GID for c in self.capas if c.datos[i]]

    def tile_solido(self, x: int, y: int) -> bool:
        if not self.dentro(x, y):
            return True
        return any(self.props_tile(g).get("solido") for g in self.gids_en(x, y))

    def texto_choque(self, x: int, y: int) -> str | None:
        if not self.dentro(x, y):
            return None
        for g in reversed(self.gids_en(x, y)):
            texto = self.props_tile(g).get("texto_choque")
            if texto:
                return texto
        return None

    def eventos_en(self, x: int, y: int) -> list[Evento]:
        return [e for e in self.eventos if e.x == x and e.y == y]

    def eventos_de_tipo(self, tipo: str) -> list[Evento]:
        return [e for e in self.eventos if e.tipo == tipo]
