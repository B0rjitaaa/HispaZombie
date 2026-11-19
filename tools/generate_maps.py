"""Genera los mapas INICIALES de la Fase 1 en formato Tiled (.tmj).

Después de generarlos, lo normal es editarlos directamente con Tiled. Cuidado: volver a
ejecutar este script SOBRESCRIBE los mapas y se perderían los cambios hechos en Tiled.

Uso:  uv run python tools/generate_maps.py
"""

from __future__ import annotations

import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_assets import ID, T  # noqa: E402

FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "hispazombie", "assets", "maps"
)


class MapBuilder:
    def __init__(self, name: str, width: int, height: int, fill: str) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.ground = [[ID[fill]] * width for _ in range(height)]
        self.objects = [[None] * width for _ in range(height)]
        self.events: list[dict] = []

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def set_ground(self, x: int, y: int, tile: str) -> None:
        if self.in_bounds(x, y):
            self.ground[y][x] = ID[tile]

    def set_object(self, x: int, y: int, tile: str | None) -> None:
        if self.in_bounds(x, y):
            self.objects[y][x] = ID[tile] if tile else None

    def fill_ground(self, x, y, w, h, tile):
        for j in range(y, y + h):
            for i in range(x, x + w):
                self.set_ground(i, j, tile)

    def fill_objects(self, x, y, w, h, tile):
        for j in range(y, y + h):
            for i in range(x, x + w):
                self.set_object(i, j, tile)

    def add_event(self, kind: str, x: int, y: int, tile: str | None = None, **props) -> None:
        ev = {
            "id": len(self.events) + 1,
            "name": props.pop("name", ""),
            "type": kind,
            "x": x * T,
            "y": (y + 1) * T if tile else y * T,  # Tiled ancla los objetos-tile por abajo
            "width": T,
            "height": T,
            "rotation": 0,
            "visible": True,
            "properties": [],
        }
        if tile:
            ev["gid"] = ID[tile] + 1
        for key, value in props.items():
            prop_type = (
                "bool" if isinstance(value, bool) else "int" if isinstance(value, int) else "string"
            )
            ev["properties"].append({"name": key, "type": prop_type, "value": value})
        self.events.append(ev)

    def save(self, properties: dict[str, str]) -> None:
        def layer(id_, name, rows):
            data = [0 if t is None else t + 1 for row in rows for t in row]
            return {
                "id": id_,
                "name": name,
                "type": "tilelayer",
                "width": self.width,
                "height": self.height,
                "x": 0,
                "y": 0,
                "opacity": 1,
                "visible": True,
                "data": data,
            }

        empty = [[None] * self.width for _ in range(self.height)]
        tmj = {
            "type": "map",
            "version": "1.10",
            "tiledversion": "1.11.0",
            "orientation": "orthogonal",
            "renderorder": "right-down",
            "infinite": False,
            "width": self.width,
            "height": self.height,
            "tilewidth": T,
            "tileheight": T,
            "nextlayerid": 5,
            "nextobjectid": len(self.events) + 1,
            "properties": [
                {"name": k, "type": "string", "value": v} for k, v in properties.items()
            ],
            "tilesets": [{"firstgid": 1, "source": "../tilesets/cartuja.tsj"}],
            "layers": [
                layer(1, "ground", self.ground),
                layer(2, "objects", self.objects),
                {
                    "id": 3,
                    "name": "events",
                    "type": "objectgroup",
                    "draworder": "topdown",
                    "x": 0,
                    "y": 0,
                    "opacity": 1,
                    "visible": True,
                    "objects": self.events,
                },
                layer(4, "above", empty),
            ],
        }
        os.makedirs(FOLDER, exist_ok=True)
        path = os.path.join(FOLDER, f"{self.name}.tmj")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tmj, f, ensure_ascii=False, indent=1)
        print("Mapa generado:", os.path.normpath(path))


# ---------------------------------------------------------------------------
# Búnker: refugio antiaéreo de la Guerra Civil donde despierta el protagonista.
# ---------------------------------------------------------------------------

INTRO = """@intern
...

@intern
Uf... qué siesta más buena. ¿Qué hora es?

@intern
¡LOS CAFÉS! Los jefes me pidieron cuatro cafés hace... ¿cuánto?

@intern
Me tropecé con algo, me di en la cabeza y... Bueno. Seguro que ni se han dado cuenta.

@intern
...¿Por qué tengo la piel verde?"""


def build_bunker() -> None:
    m = MapBuilder("bunker", 20, 15, "void")
    # Sala de 14x11 (x 3..16, y 1..11).
    m.fill_ground(3, 1, 14, 1, "wall_top")
    m.fill_ground(3, 2, 14, 1, "concrete_wall")
    m.fill_ground(3, 2, 1, 11, "wall_top")
    m.fill_ground(16, 2, 1, 11, "wall_top")
    m.fill_ground(3, 12, 14, 1, "wall_top")
    m.fill_ground(4, 3, 12, 9, "concrete_floor")
    for x, y in ((9, 3), (5, 5), (13, 8), (6, 10), (11, 6)):
        m.set_ground(x, y, "concrete_floor_stained")
    m.set_ground(5, 2, "wall_poster")
    m.set_ground(14, 2, "wall_poster")
    m.set_ground(12, 2, "wall_panel")
    m.set_ground(9, 2, "stairs")
    for x, y in ((15, 4), (4, 11), (15, 11)):
        m.set_object(x, y, "rubble")
    m.set_object(5, 7, "pebble")
    m.set_object(13, 10, "pebble")

    m.add_event("spawn", 9, 6, facing="left")
    m.add_event("auto", 0, 0, id="intro_wake_up", text=INTRO)
    m.add_event(
        "door",
        9,
        2,
        map="cartuja_outskirts",
        target_x=6,
        target_y=22,
        facing="up",
    )
    m.add_event(
        "sign",
        8,
        6,
        "chrysalis",
        text="Los restos de una especie de capullo gigante, viscoso y con mi forma exacta.\n\n"
        "@intern\nVale. No pienso preguntar. No quiero saberlo.",
    )
    m.add_event(
        "sign",
        6,
        9,
        "coffee_tray",
        text="La bandeja con los cuatro cafés de los jefes. Están fríos. Muy fríos.\n\n"
        "Tienen una capa de polvo de varios centímetros.\n\n"
        "@intern\nCon un poco de suerte, no notarán la diferencia.",
    )
    m.add_event(
        "sign",
        5,
        2,
        text='Un cartel antiguo: "REFUGIO ANTIAÉREO NÚMERO 7. AÑO 1937. '
        'Mantenga la calma y no corra por los pasillos."',
    )
    m.add_event(
        "sign",
        14,
        2,
        text='Otro cartel antiguo: "En caso de bombardeo, '
        'permanezca en el refugio hasta nuevo aviso."\n\n'
        "@intern\nNadie ha venido a avisar. Mala señal.",
    )
    m.add_event(
        "sign",
        12,
        2,
        text="Un panel moderno atornillado a la pared vieja. Pegatina: "
        '"Obras Línea 3 Metro de Sevilla. Sistema de cierre automático por detección de '
        'radiactividad."\n\n'
        'Debajo, en letra pequeña: "Tiempo de cierre hermético: 30 segundos (aprox.)".\n\n'
        "@intern\nAprox. Ya.",
    )
    m.save({"name": "Refugio antiaéreo número 7"})


# ---------------------------------------------------------------------------
# Afueras de la Cartuja: zona tutorial.
# ---------------------------------------------------------------------------


def build_outskirts() -> None:
    rnd = random.Random(1992)  # Expo
    m = MapBuilder("cartuja_outskirts", 40, 30, "dirt")
    W, H = m.width, m.height
    cx, cy, radius = 36, 16, 7  # cráter (borde este)

    # Suelo con variaciones; más ceniza cerca del cráter.
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - cx, y - cy)
            r = rnd.random()
            if d < radius + 4 and r < 0.7:
                m.set_ground(x, y, "ash")
            elif r < 0.10:
                m.set_ground(x, y, "dirt_cracked")
            elif r < 0.17:
                m.set_ground(x, y, "ash")
            elif r < 0.22:
                m.set_ground(x, y, "dry_grass")
            if 0.22 < r < 0.25:
                m.set_object(x, y, "pebble")

    # Cráter de cristal radiactivo.
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - cx, y - cy)
            if d < radius:
                m.set_ground(x, y, "radioactive_glass")
                m.set_object(x, y, None)
            elif d < radius + 1.2:
                m.set_ground(x, y, "crater_edge")
                m.set_object(x, y, None)

    # Carreteras.
    m.fill_ground(1, 13, 27, 2, "asphalt")
    for x in range(2, 27, 3):
        m.set_ground(x, 13, "asphalt_line")
    m.fill_ground(17, 15, 2, 15, "asphalt")
    m.fill_objects(1, 13, 27, 2, None)
    m.fill_objects(17, 15, 2, 15, None)

    # Límites del mapa: escombros y ruinas, con salidas al norte (Alamillo) y al sur (río).
    for x in range(W):
        if x not in (10, 11):
            m.set_object(x, 0, "rubble")
        if x not in (17, 18):
            m.set_object(x, H - 1, "rubble")
    for y in range(H):
        m.set_object(0, y, "rubble")
        if math.hypot(W - 1 - cx, y - cy) >= radius + 1.2:
            m.set_object(W - 1, y, "rubble")

    # Edificios en ruinas: techo arriba, fachada de ladrillo con ventanas abajo.
    def building(x, y, w, h):
        m.fill_objects(x, y, w, h - 2, "ruin_roof")
        m.fill_objects(x, y + h - 2, w, 2, "ruin_brick")
        for i in range(x + 1, x + w - 1, 2):
            m.set_object(i, y + h - 2, "ruin_window")

    building(2, 2, 6, 5)
    building(13, 2, 5, 4)
    building(21, 17, 6, 4)
    building(24, 24, 5, 4)
    m.set_object(8, 5, "rubble")
    m.set_object(18, 3, "rubble")

    # Torre Pelli (Torre Sevilla), al norte del cráter. Cerrada hasta el final del juego.
    m.fill_objects(26, 1, 5, 5, "tower_glass")
    m.fill_objects(26, 6, 5, 1, "tower_base")

    # Zona de obras de la Línea 3, vallada.
    ox, oy, ow, oh = 3, 17, 12, 10
    for x in range(ox, ox + ow):
        if x not in (8, 9):
            m.set_object(x, oy, "construction_fence")
        m.set_object(x, oy + oh - 1, "construction_fence")
    for y in range(oy, oy + oh):
        m.set_object(ox, y, "construction_fence")
        m.set_object(ox + ow - 1, y, "construction_fence")
    m.fill_objects(ox + 1, oy + 1, ow - 2, oh - 2, None)
    m.fill_ground(ox + 1, oy + 1, ow - 2, oh - 2, "dirt")
    m.set_ground(6, 23, "bunker_hole")
    m.set_object(11, 20, "excavator_left")
    m.set_object(12, 20, "excavator_right")
    for x, y in ((5, 23), (13, 24), (10, 18)):
        m.set_object(x, y, "traffic_cone")
    m.fill_objects(4, 25, 3, 1, "pipe")
    m.set_object(7, 18, "traffic_cone")

    # Árboles muertos y charcos tóxicos.
    for x, y in ((20, 6), (23, 10), (3, 10), (15, 21), (21, 27), (11, 9)):
        m.set_object(x, y, "dead_tree")
    for x, y in ((27, 12), (25, 15), (29, 21)):
        m.set_object(x, y, "toxic_puddle")

    # Señales de radiación en la salida norte.
    m.set_object(9, 1, "radiation_sign")
    m.set_object(12, 1, "radiation_sign")

    # --- Eventos ---
    m.add_event(
        "door",
        6,
        23,
        map="bunker",
        target_x=9,
        target_y=3,
        facing="down",
    )
    m.add_event(
        "auto",
        0,
        0,
        id="outskirts_arrival",
        text="@intern\nPero... ¿qué ha pasado aquí?\n\n"
        "@intern\n¿Dónde está la obra? ¿Y los jefes? ¿Y SEVILLA?\n\n"
        "@intern\nVale, respira. Seguro que tiene una explicación lógica.\n\n"
        "@intern\nSeguro que no es culpa mía.",
    )
    m.add_event(
        "sign",
        10,
        16,
        "signpost",
        text='"OBRAS LÍNEA 3 - METRO DE SEVILLA. Plazo de ejecución: 18 meses."\n\n'
        'Alguien ha tachado "18 meses" y ha escrito encima con rotulador: "JAJAJA".',
    )
    m.add_event(
        "sign",
        11,
        20,
        text="Una excavadora oxidada. La pala está clavada en el suelo, justo donde empieza "
        "el hueco del refugio.\n\n"
        "@intern\nAsí que de aquí salió todo... Algo tuvo que desenterrar.",
    )
    m.add_event(
        "sign",
        12,
        23,
        "hard_hat",
        text="Un casco de obra abandonado. Dentro hay una nota arrugada:\n\n"
        '"Paco, si la excavadora encuentra algo raro, NO LO TOQUES. Llama a la oficina. '
        'Firmado: el encargado."\n\n'
        "@intern\nPaco, ¿qué hiciste?",
    )
    m.add_event(
        "chest",
        5,
        19,
        "chest_closed",
        id="chest_delivery_note",
        item="pickman_delivery_note",
        text="Dentro hay un papel amarillento con el sello de la fábrica de loza Pickman "
        "de la Cartuja:\n\n"
        '"Recibida 1 caja. Contenido: LOZA - FRÁGIL. Peso: muchísimo. '
        'Procedencia: Base de Morón. NO ABRIR."',
    )
    m.add_event(
        "chest",
        4,
        8,
        "chest_closed",
        id="chest_newspaper",
        item="newspaper_1966",
        text='Un recorte de periódico de 1966: "PALOMARES: RECUPERADAS LAS CUATRO BOMBAS. '
        'No hay motivo de preocupación, aseguran las autoridades."\n\n'
        'Alguien ha escrito a boli en el margen: "¿Y la quinta?"',
    )
    m.add_event(
        "chest",
        23,
        8,
        "chest_closed",
        id="chest_water",
        item="water_bottle",
        text="Una botella de agua precintada. Fecha de consumo preferente: hace 20 años.",
    )
    m.add_event(
        "sign",
        28,
        7,
        "signpost",
        text='"TORRE SEVILLA". Todo el mundo la sigue llamando Torre Pelli.\n\n'
        "La entrada está bloqueada por toneladas de escombros y cristal.\n\n"
        "@intern\nDesde arriba se tiene que ver toda Sevilla. Lo que quede de ella.",
    )
    for x in (10, 11):
        m.add_event(
            "blocker",
            x,
            1,
            text="Camino hacia el Parque del Alamillo.\n\n"
            "La radiación aquí es tan alta que hasta el aire brilla. "
            "Mejor no pasar sin protección.",
        )
    for x in (17, 18):
        m.add_event(
            "blocker",
            x,
            28,
            text="Camino hacia el río y Triana.\n\n"
            "(Este camino se abrirá cuando el resto de Sevilla esté construida. "
            "Que con las obras de aquí ya se sabe...)",
        )
    m.add_event(
        "npc",
        14,
        11,
        name="scrapper",
        id="scrapper",
        sprite="scrapper",
        facing="down",
        script="cartuja_outskirts/scrapper",
    )
    m.save({"name": "Afueras de la Cartuja"})


if __name__ == "__main__":
    build_bunker()
    build_outskirts()
