"""Genera los mapas INICIALES de la Fase 1 en formato Tiled (.tmj).

Después de generarlos, lo normal es editarlos directamente con Tiled. Cuidado: volver a
ejecutar este script SOBRESCRIBE los mapas y se perderían los cambios hechos en Tiled.

Uso:  uv run python tools/generar_mapas.py
"""

from __future__ import annotations

import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generar_assets import ID, T  # noqa: E402

CARPETA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "hispazombie", "assets", "mapas"
)


class Mapa:
    def __init__(self, nombre: str, ancho: int, alto: int, relleno: str) -> None:
        self.nombre = nombre
        self.ancho = ancho
        self.alto = alto
        self.suelo = [[ID[relleno]] * ancho for _ in range(alto)]
        self.objetos = [[None] * ancho for _ in range(alto)]
        self.eventos: list[dict] = []

    def dentro(self, x: int, y: int) -> bool:
        return 0 <= x < self.ancho and 0 <= y < self.alto

    def s(self, x: int, y: int, tile: str) -> None:
        if self.dentro(x, y):
            self.suelo[y][x] = ID[tile]

    def o(self, x: int, y: int, tile: str | None) -> None:
        if self.dentro(x, y):
            self.objetos[y][x] = ID[tile] if tile else None

    def rect_s(self, x, y, w, h, tile):
        for j in range(y, y + h):
            for i in range(x, x + w):
                self.s(i, j, tile)

    def rect_o(self, x, y, w, h, tile):
        for j in range(y, y + h):
            for i in range(x, x + w):
                self.o(i, j, tile)

    def evento(self, tipo: str, x: int, y: int, tile: str | None = None, **props) -> None:
        ev = {
            "id": len(self.eventos) + 1,
            "name": props.pop("nombre", ""),
            "type": tipo,
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
        for clave, valor in props.items():
            tipo_prop = (
                "bool" if isinstance(valor, bool) else "int" if isinstance(valor, int) else "string"
            )
            ev["properties"].append({"name": clave, "type": tipo_prop, "value": valor})
        self.eventos.append(ev)

    def guardar(self, propiedades: dict[str, str]) -> None:
        def capa(id_, nombre, filas):
            datos = [0 if t is None else t + 1 for fila in filas for t in fila]
            return {
                "id": id_,
                "name": nombre,
                "type": "tilelayer",
                "width": self.ancho,
                "height": self.alto,
                "x": 0,
                "y": 0,
                "opacity": 1,
                "visible": True,
                "data": datos,
            }

        vacia = [[None] * self.ancho for _ in range(self.alto)]
        tmj = {
            "type": "map",
            "version": "1.10",
            "tiledversion": "1.11.0",
            "orientation": "orthogonal",
            "renderorder": "right-down",
            "infinite": False,
            "width": self.ancho,
            "height": self.alto,
            "tilewidth": T,
            "tileheight": T,
            "nextlayerid": 5,
            "nextobjectid": len(self.eventos) + 1,
            "properties": [
                {"name": k, "type": "string", "value": v} for k, v in propiedades.items()
            ],
            "tilesets": [{"firstgid": 1, "source": "../tilesets/cartuja.tsj"}],
            "layers": [
                capa(1, "suelo", self.suelo),
                capa(2, "objetos", self.objetos),
                {
                    "id": 3,
                    "name": "eventos",
                    "type": "objectgroup",
                    "draworder": "topdown",
                    "x": 0,
                    "y": 0,
                    "opacity": 1,
                    "visible": True,
                    "objects": self.eventos,
                },
                capa(4, "encima", vacia),
            ],
        }
        os.makedirs(CARPETA, exist_ok=True)
        ruta = os.path.join(CARPETA, f"{self.nombre}.tmj")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(tmj, f, ensure_ascii=False, indent=1)
        print("Mapa generado:", os.path.normpath(ruta))


# ---------------------------------------------------------------------------
# Búnker: refugio antiaéreo de la Guerra Civil donde despierta el protagonista.
# ---------------------------------------------------------------------------

INTRO = """@becario
...

@becario
Uf... qué siesta más buena. ¿Qué hora es?

@becario
¡LOS CAFÉS! Los jefes me pidieron cuatro cafés hace... ¿cuánto?

@becario
Me tropecé con algo, me di en la cabeza y... Bueno. Seguro que ni se han dado cuenta.

@becario
...¿Por qué tengo la piel verde?"""


def bunker() -> None:
    m = Mapa("bunker", 20, 15, "negro")
    # Sala de 14x11 (x 3..16, y 1..11).
    m.rect_s(3, 1, 14, 1, "pared_techo")
    m.rect_s(3, 2, 14, 1, "pared_hormigon")
    m.rect_s(3, 2, 1, 11, "pared_techo")
    m.rect_s(16, 2, 1, 11, "pared_techo")
    m.rect_s(3, 12, 14, 1, "pared_techo")
    m.rect_s(4, 3, 12, 9, "suelo_hormigon")
    for x, y in ((9, 3), (5, 5), (13, 8), (6, 10), (11, 6)):
        m.s(x, y, "suelo_hormigon_manchado")
    m.s(5, 2, "pared_poster")
    m.s(14, 2, "pared_poster")
    m.s(12, 2, "pared_panel")
    m.s(9, 2, "escaleras")
    for x, y in ((15, 4), (4, 11), (15, 11)):
        m.o(x, y, "escombros")
    m.o(5, 7, "cascote")
    m.o(13, 10, "cascote")

    m.evento("inicio", 9, 6, direccion="izquierda")
    m.evento("auto", 0, 0, id="intro_despertar", texto=INTRO)
    m.evento(
        "puerta",
        9,
        2,
        mapa="afueras_cartuja",
        destino_x=6,
        destino_y=22,
        direccion="arriba",
    )
    m.evento(
        "cartel",
        8,
        6,
        "crisalida",
        texto="Los restos de una especie de capullo gigante, viscoso y con mi forma exacta.\n\n"
        "@becario\nVale. No pienso preguntar. No quiero saberlo.",
    )
    m.evento(
        "cartel",
        6,
        9,
        "bandeja_cafes",
        texto="La bandeja con los cuatro cafés de los jefes. Están fríos. Muy fríos.\n\n"
        "Tienen una capa de polvo de varios centímetros.\n\n"
        "@becario\nCon un poco de suerte, no notarán la diferencia.",
    )
    m.evento(
        "cartel",
        5,
        2,
        texto='Un cartel antiguo: "REFUGIO ANTIAÉREO NÚMERO 7. AÑO 1937. '
        'Mantenga la calma y no corra por los pasillos."',
    )
    m.evento(
        "cartel",
        14,
        2,
        texto='Otro cartel antiguo: "En caso de bombardeo, '
        'permanezca en el refugio hasta nuevo aviso."\n\n'
        "@becario\nNadie ha venido a avisar. Mala señal.",
    )
    m.evento(
        "cartel",
        12,
        2,
        texto="Un panel moderno atornillado a la pared vieja. Pegatina: "
        '"Obras Línea 3 Metro de Sevilla. Sistema de cierre automático por detección de '
        'radiactividad."\n\n'
        'Debajo, en letra pequeña: "Tiempo de cierre hermético: 30 segundos (aprox.)".\n\n'
        "@becario\nAprox. Ya.",
    )
    m.guardar({"nombre": "Refugio antiaéreo número 7"})


# ---------------------------------------------------------------------------
# Afueras de la Cartuja: zona tutorial.
# ---------------------------------------------------------------------------


def afueras() -> None:
    rnd = random.Random(1992)  # Expo
    m = Mapa("afueras_cartuja", 40, 30, "tierra")
    W, H = m.ancho, m.alto
    cx, cy, radio = 36, 16, 7  # cráter (borde este)

    # Suelo con variaciones; más ceniza cerca del cráter.
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - cx, y - cy)
            r = rnd.random()
            if d < radio + 4 and r < 0.7:
                m.s(x, y, "tierra_ceniza")
            elif r < 0.10:
                m.s(x, y, "tierra_grietas")
            elif r < 0.17:
                m.s(x, y, "tierra_ceniza")
            elif r < 0.22:
                m.s(x, y, "hierba_seca")
            if 0.22 < r < 0.25:
                m.o(x, y, "cascote")

    # Cráter de cristal radiactivo.
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - cx, y - cy)
            if d < radio:
                m.s(x, y, "cristal_radiactivo")
                m.o(x, y, None)
            elif d < radio + 1.2:
                m.s(x, y, "borde_crater")
                m.o(x, y, None)

    # Carreteras.
    m.rect_s(1, 13, 27, 2, "asfalto")
    for x in range(2, 27, 3):
        m.s(x, 13, "asfalto_linea")
    m.rect_s(17, 15, 2, 15, "asfalto")
    m.rect_o(1, 13, 27, 2, None)
    m.rect_o(17, 15, 2, 15, None)

    # Límites del mapa: escombros y ruinas, con salidas al norte (Alamillo) y al sur (río).
    for x in range(W):
        if x not in (10, 11):
            m.o(x, 0, "escombros")
        if x not in (17, 18):
            m.o(x, H - 1, "escombros")
    for y in range(H):
        m.o(0, y, "escombros")
        if math.hypot(W - 1 - cx, y - cy) >= radio + 1.2:
            m.o(W - 1, y, "escombros")

    # Edificios en ruinas: techo arriba, fachada de ladrillo con ventanas abajo.
    def edificio(x, y, w, h):
        m.rect_o(x, y, w, h - 2, "ruina_techo")
        m.rect_o(x, y + h - 2, w, 2, "ruina_ladrillo")
        for i in range(x + 1, x + w - 1, 2):
            m.o(i, y + h - 2, "ruina_ventana")

    edificio(2, 2, 6, 5)
    edificio(13, 2, 5, 4)
    edificio(21, 17, 6, 4)
    edificio(24, 24, 5, 4)
    m.o(8, 5, "escombros")
    m.o(18, 3, "escombros")

    # Torre Pelli (Torre Sevilla), al norte del cráter. Cerrada hasta el final del juego.
    m.rect_o(26, 1, 5, 5, "torre_cristal")
    m.rect_o(26, 6, 5, 1, "torre_base")

    # Zona de obras de la Línea 3, vallada.
    ox, oy, ow, oh = 3, 17, 12, 10
    for x in range(ox, ox + ow):
        if x not in (8, 9):
            m.o(x, oy, "valla_obra")
        m.o(x, oy + oh - 1, "valla_obra")
    for y in range(oy, oy + oh):
        m.o(ox, y, "valla_obra")
        m.o(ox + ow - 1, y, "valla_obra")
    m.rect_o(ox + 1, oy + 1, ow - 2, oh - 2, None)
    m.rect_s(ox + 1, oy + 1, ow - 2, oh - 2, "tierra")
    m.s(6, 23, "hueco_obra")
    m.o(11, 20, "excavadora_izq")
    m.o(12, 20, "excavadora_der")
    for x, y in ((5, 23), (13, 24), (10, 18)):
        m.o(x, y, "cono_obra")
    m.rect_o(4, 25, 3, 1, "tuberia")
    m.o(7, 18, "cono_obra")

    # Árboles muertos y charcos tóxicos.
    for x, y in ((20, 6), (23, 10), (3, 10), (15, 21), (21, 27), (11, 9)):
        m.o(x, y, "arbol_muerto")
    for x, y in ((27, 12), (25, 15), (29, 21)):
        m.o(x, y, "charco_toxico")

    # Señales de radiación en la salida norte.
    m.o(9, 1, "senal_radiacion")
    m.o(12, 1, "senal_radiacion")

    # --- Eventos ---
    m.evento(
        "puerta",
        6,
        23,
        mapa="bunker",
        destino_x=9,
        destino_y=3,
        direccion="abajo",
    )
    m.evento(
        "auto",
        0,
        0,
        id="afueras_llegada",
        texto="@becario\nPero... ¿qué ha pasado aquí?\n\n"
        "@becario\n¿Dónde está la obra? ¿Y los jefes? ¿Y SEVILLA?\n\n"
        "@becario\nVale, respira. Seguro que tiene una explicación lógica.\n\n"
        "@becario\nSeguro que no es culpa mía.",
    )
    m.evento(
        "cartel",
        10,
        16,
        "cartel",
        texto='"OBRAS LÍNEA 3 - METRO DE SEVILLA. Plazo de ejecución: 18 meses."\n\n'
        'Alguien ha tachado "18 meses" y ha escrito encima con rotulador: "JAJAJA".',
    )
    m.evento(
        "cartel",
        11,
        20,
        texto="Una excavadora oxidada. La pala está clavada en el suelo, justo donde empieza "
        "el hueco del refugio.\n\n"
        "@becario\nAsí que de aquí salió todo... Algo tuvo que desenterrar.",
    )
    m.evento(
        "cartel",
        12,
        23,
        "casco_obra",
        texto="Un casco de obra abandonado. Dentro hay una nota arrugada:\n\n"
        '"Paco, si la excavadora encuentra algo raro, NO LO TOQUES. Llama a la oficina. '
        'Firmado: el encargado."\n\n'
        "@becario\nPaco, ¿qué hiciste?",
    )
    m.evento(
        "cofre",
        5,
        19,
        "cofre_cerrado",
        id="cofre_albaran",
        objeto="Albarán de Pickman",
        texto="Dentro hay un papel amarillento con el sello de la fábrica de loza Pickman "
        "de la Cartuja:\n\n"
        '"Recibida 1 caja. Contenido: LOZA - FRÁGIL. Peso: muchísimo. '
        'Procedencia: Base de Morón. NO ABRIR."\n\n'
        "Obtienes: Albarán de Pickman.",
    )
    m.evento(
        "cofre",
        4,
        8,
        "cofre_cerrado",
        id="cofre_periodico",
        objeto="Recorte de periódico (1966)",
        texto='Un recorte de periódico de 1966: "PALOMARES: RECUPERADAS LAS CUATRO BOMBAS. '
        'No hay motivo de preocupación, aseguran las autoridades."\n\n'
        'Alguien ha escrito a boli en el margen: "¿Y la quinta?"\n\n'
        "Obtienes: Recorte de periódico (1966).",
    )
    m.evento(
        "cofre",
        23,
        8,
        "cofre_cerrado",
        id="cofre_agua",
        objeto="Botella de agua",
        texto="Una botella de agua precintada. Fecha de consumo preferente: hace 20 años.\n\n"
        "Obtienes: Botella de agua.",
    )
    m.evento(
        "cartel",
        28,
        7,
        "cartel",
        texto='"TORRE SEVILLA". Todo el mundo la sigue llamando Torre Pelli.\n\n'
        "La entrada está bloqueada por toneladas de escombros y cristal.\n\n"
        "@becario\nDesde arriba se tiene que ver toda Sevilla. Lo que quede de ella.",
    )
    for x in (10, 11):
        m.evento(
            "bloqueo",
            x,
            1,
            texto="Camino hacia el Parque del Alamillo.\n\n"
            "La radiación aquí es tan alta que hasta el aire brilla. "
            "Mejor no pasar sin protección.",
        )
    for x in (17, 18):
        m.evento(
            "bloqueo",
            x,
            28,
            texto="Camino hacia el río y Triana.\n\n"
            "(Este camino se abrirá cuando el resto de Sevilla esté construida. "
            "Que con las obras de aquí ya se sabe...)",
        )
    m.guardar({"nombre": "Afueras de la Cartuja"})


if __name__ == "__main__":
    bunker()
    afueras()
