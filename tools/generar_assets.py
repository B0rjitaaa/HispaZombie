"""Genera los gráficos PROVISIONALES del juego (tileset, sprite y retrato del protagonista).

Son pixel art hecho con código para poder avanzar sin depender de arte externo. Cuando haya
arte definitivo se sustituyen los PNG manteniendo el mismo orden de tiles.

Uso:  uv run python tools/generar_assets.py
"""

from __future__ import annotations

import json
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hispazombie", "assets")
T = 16
COLUMNAS = 8

# (nombre, sólido). El índice en esta lista es el id del tile en Tiled.
TILES: list[tuple[str, bool]] = [
    ("negro", True),  # 0
    ("suelo_hormigon", False),  # 1
    ("suelo_hormigon_manchado", False),  # 2
    ("pared_hormigon", True),  # 3
    ("pared_techo", True),  # 4
    ("pared_poster", True),  # 5
    ("pared_panel", True),  # 6
    ("escaleras", False),  # 7
    ("tierra", False),  # 8
    ("tierra_grietas", False),  # 9
    ("tierra_ceniza", False),  # 10
    ("hierba_seca", False),  # 11
    ("asfalto", False),  # 12
    ("asfalto_linea", False),  # 13
    ("escombros", True),  # 14
    ("ruina_ladrillo", True),  # 15
    ("ruina_ventana", True),  # 16
    ("ruina_techo", True),  # 17
    ("valla_obra", True),  # 18
    ("cono_obra", True),  # 19
    ("tuberia", True),  # 20
    ("cristal_radiactivo", True),  # 21
    ("borde_crater", True),  # 22
    ("charco_toxico", True),  # 23
    ("arbol_muerto", True),  # 24
    ("cofre_cerrado", True),  # 25
    ("cofre_abierto", True),  # 26
    ("cartel", True),  # 27
    ("senal_radiacion", True),  # 28
    ("crisalida", True),  # 29
    ("bandeja_cafes", True),  # 30
    ("excavadora_izq", True),  # 31
    ("excavadora_der", True),  # 32
    ("hueco_obra", False),  # 33
    ("cascote", False),  # 34
    ("torre_cristal", True),  # 35
    ("torre_base", True),  # 36
    ("casco_obra", True),  # 37
]
ID = {nombre: i for i, (nombre, _) in enumerate(TILES)}

# Texto que se muestra al chocar contra ciertos tiles (propiedad "texto_choque" en Tiled).
TEXTOS_CHOQUE = {
    "borde_crater": "El borde del cráter. Abajo, todo es cristal verde y brillante.\n\n"
    "@becario\nNo. Ni de broma.",
    "cristal_radiactivo": "Cristal radiactivo. Brilla bonito. Demasiado bonito.",
    "charco_toxico": "Un charco verde que burbujea solo.\n\n@becario\nMejor rodearlo.",
}

rnd = random.Random(1966)  # Palomares


def ruido(s: pygame.Surface, base, variaciones, densidad=0.35) -> None:
    s.fill(base)
    for y in range(T):
        for x in range(T):
            if rnd.random() < densidad:
                s.set_at((x, y), rnd.choice(variaciones))


def tierra(s, extra=None):
    ruido(s, (122, 98, 70), [(110, 88, 62), (134, 108, 78), (100, 80, 58)])
    if extra:
        extra(s)


def grietas(s):
    tierra(s)
    x, y = rnd.randint(2, 6), rnd.randint(2, 6)
    for _ in range(9):
        s.set_at((x, y), (70, 54, 40))
        x = min(T - 1, x + rnd.choice((0, 1)))
        y = min(T - 1, y + rnd.choice((0, 1, 1)))


def ceniza(s):
    ruido(s, (104, 100, 96), [(92, 88, 86), (118, 114, 110), (84, 80, 78)], 0.45)


def hierba(s):
    tierra(s)
    for _ in range(7):
        x, y = rnd.randint(1, 14), rnd.randint(3, 15)
        pygame.draw.line(s, (160, 150, 70), (x, y), (x + rnd.choice((-1, 0, 1)), y - 3))


def hormigon(s, manchado=False):
    ruido(s, (92, 92, 96), [(84, 84, 88), (100, 100, 104)], 0.3)
    pygame.draw.line(s, (78, 78, 82), (0, T - 1), (T - 1, T - 1))
    pygame.draw.line(s, (78, 78, 82), (T - 1, 0), (T - 1, T - 1))
    if manchado:
        pygame.draw.ellipse(s, (70, 76, 64), (3, 5, 9, 6))
        pygame.draw.ellipse(s, (60, 66, 54), (5, 6, 5, 3))


def pared(s):
    ruido(s, (130, 128, 122), [(120, 118, 112), (140, 138, 132)], 0.3)
    for y in (5, 11):
        pygame.draw.line(s, (104, 102, 98), (0, y), (T - 1, y))
    pygame.draw.line(s, (60, 58, 56), (0, T - 1), (T - 1, T - 1))


def techo(s):
    ruido(s, (58, 56, 60), [(50, 48, 52), (66, 64, 68)], 0.3)


def poster(s):
    pared(s)
    pygame.draw.rect(s, (196, 170, 120), (3, 1, 10, 12))
    pygame.draw.rect(s, (150, 40, 34), (4, 2, 8, 3))
    pygame.draw.line(s, (60, 50, 40), (5, 7), (10, 7))
    pygame.draw.line(s, (60, 50, 40), (5, 9), (9, 9))
    pygame.draw.line(s, (60, 50, 40), (5, 11), (10, 11))


def panel(s):
    pared(s)
    pygame.draw.rect(s, (70, 80, 72), (3, 2, 10, 11))
    pygame.draw.rect(s, (40, 46, 42), (3, 2, 10, 11), 1)
    s.set_at((6, 5), (220, 40, 30))
    s.set_at((9, 5), (60, 200, 70))
    pygame.draw.line(s, (200, 180, 40), (5, 9), (10, 9))


def escaleras(s):
    techo(s)
    for i, y in enumerate(range(2, T, 3)):
        c = 90 + i * 14
        pygame.draw.rect(s, (c, c, c + 4), (2, y, 12, 2))


def asfalto(s, linea=False):
    ruido(s, (62, 62, 66), [(54, 54, 58), (72, 72, 76)], 0.4)
    if linea:
        pygame.draw.rect(s, (210, 190, 90), (2, 7, 7, 2))


def escombros(s):
    for _ in range(6):
        x, y = rnd.randint(0, 10), rnd.randint(4, 11)
        c = rnd.choice([(120, 116, 110), (96, 92, 88), (140, 120, 100)])
        pygame.draw.polygon(s, c, [(x, y + 5), (x + 3, y), (x + 6, y + 5)])
        pygame.draw.line(s, (60, 58, 56), (x, y + 5), (x + 6, y + 5))


def ladrillo(s, ventana=False):
    s.fill((150, 86, 62))
    for fila, y in enumerate(range(0, T, 4)):
        pygame.draw.line(s, (110, 64, 48), (0, y), (T - 1, y))
        desp = 0 if fila % 2 else 4
        for x in range(desp, T, 8):
            pygame.draw.line(s, (110, 64, 48), (x, y), (x, y + 3))
    for _ in range(4):
        s.set_at((rnd.randint(0, 15), rnd.randint(0, 15)), (90, 50, 40))
    if ventana:
        pygame.draw.rect(s, (24, 22, 26), (4, 3, 8, 9))
        pygame.draw.line(s, (180, 200, 210), (5, 4), (7, 8))


def techo_ruina(s):
    ruido(s, (86, 70, 62), [(76, 62, 56), (96, 80, 70)], 0.4)
    pygame.draw.line(s, (60, 48, 42), (0, rnd.randint(3, 12)), (T - 1, rnd.randint(3, 12)))


def valla(s):
    for x in (1, 14):
        pygame.draw.rect(s, (90, 90, 90), (x, 2, 2, 14))
    for y in (4, 9):
        for x in range(0, T, 4):
            col = (230, 60, 40) if (x // 4) % 2 == 0 else (240, 240, 230)
            pygame.draw.rect(s, col, (x, y, 4, 3))


def cono(s):
    pygame.draw.polygon(s, (240, 110, 30), [(8, 2), (12, 13), (4, 13)])
    pygame.draw.line(s, (250, 250, 240), (6, 9), (10, 9))
    pygame.draw.rect(s, (60, 60, 60), (3, 13, 10, 2))


def tuberia(s):
    pygame.draw.rect(s, (110, 120, 128), (0, 4, T, 9))
    pygame.draw.line(s, (160, 170, 178), (0, 5), (T - 1, 5))
    pygame.draw.line(s, (70, 76, 82), (0, 12), (T - 1, 12))


def cristal(s):
    ruido(s, (60, 170, 90), [(90, 220, 120), (40, 130, 70), (140, 255, 170)], 0.4)
    pygame.draw.line(s, (200, 255, 210), (2, 3), (6, 7))
    pygame.draw.line(s, (200, 255, 210), (10, 10), (13, 12))


def borde_crater(s):
    ruido(s, (70, 64, 56), [(54, 50, 44), (90, 86, 70), (60, 120, 70)], 0.5)


def charco(s):
    tierra(s)
    pygame.draw.ellipse(s, (90, 180, 60), (1, 4, 14, 9))
    pygame.draw.ellipse(s, (140, 230, 90), (4, 6, 5, 3))


def arbol(s):
    pygame.draw.line(s, (70, 52, 40), (8, 15), (8, 4))
    pygame.draw.line(s, (70, 52, 40), (8, 8), (4, 4))
    pygame.draw.line(s, (70, 52, 40), (8, 6), (12, 2))
    pygame.draw.line(s, (70, 52, 40), (4, 4), (3, 1))


def cofre(s, abierto=False):
    pygame.draw.rect(s, (60, 70, 60), (2, 6, 12, 9))
    pygame.draw.rect(s, (36, 42, 36), (2, 6, 12, 9), 1)
    if abierto:
        pygame.draw.rect(s, (20, 20, 20), (3, 7, 10, 3))
        pygame.draw.rect(s, (80, 92, 80), (2, 2, 12, 4))
    else:
        pygame.draw.rect(s, (80, 92, 80), (2, 4, 12, 4))
        pygame.draw.rect(s, (200, 180, 60), (7, 7, 2, 3))


def cartel(s):
    pygame.draw.rect(s, (90, 66, 44), (7, 8, 2, 8))
    pygame.draw.rect(s, (200, 180, 130), (2, 2, 12, 7))
    pygame.draw.rect(s, (110, 84, 56), (2, 2, 12, 7), 1)
    pygame.draw.line(s, (80, 60, 40), (4, 4), (11, 4))
    pygame.draw.line(s, (80, 60, 40), (4, 6), (9, 6))


def senal(s):
    pygame.draw.rect(s, (90, 90, 90), (7, 9, 2, 7))
    pygame.draw.polygon(s, (240, 210, 40), [(8, 0), (15, 11), (1, 11)])
    pygame.draw.polygon(s, (20, 20, 20), [(8, 0), (15, 11), (1, 11)], 1)
    pygame.draw.circle(s, (20, 20, 20), (8, 7), 2)


def crisalida(s):
    pygame.draw.ellipse(s, (150, 160, 110), (1, 5, 14, 10))
    pygame.draw.ellipse(s, (110, 130, 80), (1, 5, 14, 10), 1)
    pygame.draw.polygon(s, (30, 30, 26), [(5, 7), (11, 6), (10, 12), (6, 11)])
    s.set_at((4, 10), (180, 240, 120))
    s.set_at((12, 9), (180, 240, 120))


def bandeja(s):
    pygame.draw.ellipse(s, (170, 170, 176), (1, 8, 14, 7))
    for x in (3, 7, 11):
        pygame.draw.rect(s, (240, 236, 226), (x, 6, 3, 5))
        s.set_at((x + 1, 6), (90, 60, 40))


def excavadora(s, lado):
    if lado == "izq":
        pygame.draw.rect(s, (230, 170, 30), (4, 5, 12, 8))
        pygame.draw.rect(s, (40, 60, 70), (7, 1, 7, 5))
        pygame.draw.rect(s, (40, 40, 40), (3, 12, 13, 4))
    else:
        pygame.draw.rect(s, (230, 170, 30), (0, 6, 9, 7))
        pygame.draw.line(s, (230, 170, 30), (8, 7), (13, 3), 2)
        pygame.draw.polygon(s, (120, 120, 120), [(11, 3), (15, 3), (15, 9), (12, 7)])
        pygame.draw.rect(s, (40, 40, 40), (0, 12, 10, 4))


def hueco(s):
    tierra(s)
    pygame.draw.ellipse(s, (20, 18, 16), (1, 3, 14, 11))
    pygame.draw.line(s, (130, 130, 130), (5, 4), (5, 12))
    pygame.draw.line(s, (130, 130, 130), (10, 4), (10, 12))
    for y in (6, 9):
        pygame.draw.line(s, (130, 130, 130), (5, y), (10, y))


def cascote(s):
    pygame.draw.polygon(s, (118, 112, 106), [(4, 12), (7, 8), (10, 12)])
    s.set_at((12, 13), (96, 92, 88))


def torre(s, base=False):
    s.fill((46, 58, 70))
    for x in range(1, T, 5):
        pygame.draw.line(s, (80, 100, 120), (x, 0), (x, T - 1))
    pygame.draw.line(s, (24, 30, 36), (0, 7), (T - 1, 7))
    if rnd.random() < 0.5:
        pygame.draw.line(s, (150, 170, 190), (3, 2), (7, 12))
    if base:
        pygame.draw.rect(s, (90, 88, 84), (0, 10, T, 6))


def casco(s):
    pygame.draw.ellipse(s, (240, 200, 40), (3, 6, 10, 8))
    pygame.draw.rect(s, (240, 200, 40), (2, 11, 12, 2))
    pygame.draw.line(s, (200, 160, 30), (8, 6), (8, 12))


DIBUJOS = {
    "negro": lambda s: s.fill((8, 8, 10)),
    "suelo_hormigon": hormigon,
    "suelo_hormigon_manchado": lambda s: hormigon(s, True),
    "pared_hormigon": pared,
    "pared_techo": techo,
    "pared_poster": poster,
    "pared_panel": panel,
    "escaleras": escaleras,
    "tierra": tierra,
    "tierra_grietas": grietas,
    "tierra_ceniza": ceniza,
    "hierba_seca": hierba,
    "asfalto": asfalto,
    "asfalto_linea": lambda s: asfalto(s, True),
    "escombros": escombros,
    "ruina_ladrillo": ladrillo,
    "ruina_ventana": lambda s: ladrillo(s, True),
    "ruina_techo": techo_ruina,
    "valla_obra": valla,
    "cono_obra": cono,
    "tuberia": tuberia,
    "cristal_radiactivo": cristal,
    "borde_crater": borde_crater,
    "charco_toxico": charco,
    "arbol_muerto": arbol,
    "cofre_cerrado": cofre,
    "cofre_abierto": lambda s: cofre(s, True),
    "cartel": cartel,
    "senal_radiacion": senal,
    "crisalida": crisalida,
    "bandeja_cafes": bandeja,
    "excavadora_izq": lambda s: excavadora(s, "izq"),
    "excavadora_der": lambda s: excavadora(s, "der"),
    "hueco_obra": hueco,
    "cascote": cascote,
    "torre_cristal": torre,
    "torre_base": lambda s: torre(s, True),
    "casco_obra": casco,
}


def generar_tileset() -> None:
    filas = (len(TILES) + COLUMNAS - 1) // COLUMNAS
    hoja = pygame.Surface((COLUMNAS * T, filas * T), pygame.SRCALPHA)
    for i, (nombre, _) in enumerate(TILES):
        tile = pygame.Surface((T, T), pygame.SRCALPHA)
        DIBUJOS[nombre](tile)
        hoja.blit(tile, ((i % COLUMNAS) * T, (i // COLUMNAS) * T))

    carpeta = os.path.join(RAIZ, "tilesets")
    os.makedirs(carpeta, exist_ok=True)
    pygame.image.save(hoja, os.path.join(carpeta, "cartuja.png"))

    tiles_json = []
    for i, (nombre, solido) in enumerate(TILES):
        props = [{"name": "nombre", "type": "string", "value": nombre}]
        if solido:
            props.append({"name": "solido", "type": "bool", "value": True})
        if nombre in TEXTOS_CHOQUE:
            props.append({"name": "texto_choque", "type": "string", "value": TEXTOS_CHOQUE[nombre]})
        if nombre == "cofre_cerrado":
            props.append({"name": "abierto_id", "type": "int", "value": ID["cofre_abierto"]})
        tiles_json.append({"id": i, "properties": props})

    tsj = {
        "type": "tileset",
        "version": "1.10",
        "tiledversion": "1.11.0",
        "name": "cartuja",
        "image": "cartuja.png",
        "imagewidth": hoja.get_width(),
        "imageheight": hoja.get_height(),
        "tilewidth": T,
        "tileheight": T,
        "tilecount": len(TILES),
        "columns": COLUMNAS,
        "margin": 0,
        "spacing": 0,
        "tiles": tiles_json,
    }
    with open(os.path.join(carpeta, "cartuja.tsj"), "w", encoding="utf-8") as f:
        json.dump(tsj, f, ensure_ascii=False, indent=1)


# --- Protagonista: hoja de 3 frames x 4 direcciones (abajo, izquierda, derecha, arriba) ---

ANCHO_PJ, ALTO_PJ = 16, 24
PIEL = (226, 184, 150)
PIEL_MUTADA = (150, 200, 120)
PELO = (92, 60, 36)
CAMISA = (236, 236, 228)
PANTALON = (52, 70, 120)
ZAPATO = (40, 32, 28)
ACREDITACION = (220, 40, 40)
OJO = (20, 20, 20)


def dibujar_pj(s: pygame.Surface, direccion: str, frame: int) -> None:
    # Piernas: el frame 1 es la postura quieta; 0 y 2 alternan las piernas.
    paso = {0: -1, 1: 0, 2: 1}[frame]
    if direccion in ("abajo", "arriba"):
        pygame.draw.rect(s, PANTALON, (5, 16, 3, 6 + max(0, -paso)))
        pygame.draw.rect(s, PANTALON, (8, 16, 3, 6 + max(0, paso)))
        pygame.draw.rect(s, ZAPATO, (5, 21 + max(0, -paso), 3, 2))
        pygame.draw.rect(s, ZAPATO, (8, 21 + max(0, paso), 3, 2))
    else:
        pygame.draw.rect(s, PANTALON, (6 + paso, 16, 3, 6))
        pygame.draw.rect(s, PANTALON, (7 - paso, 16, 3, 6))
        pygame.draw.rect(s, ZAPATO, (6 + paso, 21, 3, 2))
        pygame.draw.rect(s, ZAPATO, (7 - paso, 21, 3, 2))

    # Cuerpo con camisa rota y brazos.
    pygame.draw.rect(s, CAMISA, (4, 10, 8, 7))
    s.set_at((5, 15), (180, 180, 172))
    s.set_at((10, 12), (180, 180, 172))
    brazo = paso if direccion in ("abajo", "arriba") else 0
    pygame.draw.rect(s, PIEL, (3, 11 + brazo, 1, 4))
    pygame.draw.rect(s, PIEL_MUTADA, (12, 11 - brazo, 1, 4))

    # Cabeza.
    pygame.draw.rect(s, PIEL, (4, 2, 8, 8))
    if direccion == "arriba":
        pygame.draw.rect(s, PELO, (4, 1, 8, 7))
    else:
        pygame.draw.rect(s, PELO, (4, 1, 8, 3))
        s.set_at((10, 6), PIEL_MUTADA)  # mancha de la mutación
        s.set_at((11, 7), PIEL_MUTADA)
        if direccion == "abajo":
            s.set_at((6, 6), OJO)
            s.set_at((9, 6), OJO)
            # Acreditación de "BECARIO" colgando.
            pygame.draw.line(s, ACREDITACION, (6, 10), (8, 13))
            pygame.draw.rect(s, (250, 250, 250), (7, 13, 3, 3))
        elif direccion == "izquierda":
            s.set_at((5, 6), OJO)
            pygame.draw.rect(s, PELO, (9, 1, 3, 6))
        else:
            s.set_at((10, 6), OJO)
            pygame.draw.rect(s, PELO, (4, 1, 3, 6))


def generar_protagonista() -> None:
    direcciones = ("abajo", "izquierda", "derecha", "arriba")
    hoja = pygame.Surface((ANCHO_PJ * 3, ALTO_PJ * 4), pygame.SRCALPHA)
    for fila, direccion in enumerate(direcciones):
        for frame in range(3):
            celda = pygame.Surface((ANCHO_PJ, ALTO_PJ), pygame.SRCALPHA)
            dibujar_pj(celda, direccion, frame)
            hoja.blit(celda, (frame * ANCHO_PJ, fila * ALTO_PJ))
    carpeta = os.path.join(RAIZ, "sprites")
    os.makedirs(carpeta, exist_ok=True)
    pygame.image.save(hoja, os.path.join(carpeta, "becario.png"))


def generar_retrato() -> None:
    s = pygame.Surface((48, 48), pygame.SRCALPHA)
    s.fill((40, 44, 52))
    pygame.draw.rect(s, CAMISA, (8, 38, 32, 10))
    pygame.draw.line(s, ACREDITACION, (18, 38), (24, 46), 2)
    pygame.draw.rect(s, PIEL, (14, 12, 20, 26))
    pygame.draw.rect(s, PELO, (12, 6, 24, 9))
    pygame.draw.rect(s, PELO, (12, 10, 4, 10))
    pygame.draw.rect(s, PELO, (31, 9, 5, 6))  # pelo de recién despertado
    pygame.draw.rect(s, (250, 250, 250), (18, 21, 5, 4))
    pygame.draw.rect(s, (250, 250, 250), (26, 21, 5, 4))
    pygame.draw.rect(s, OJO, (20, 22, 2, 2))
    pygame.draw.rect(s, OJO, (28, 22, 2, 2))
    pygame.draw.line(s, (120, 90, 80), (18, 26), (22, 27))  # ojeras
    pygame.draw.line(s, (120, 90, 80), (26, 27), (30, 26))
    pygame.draw.line(s, (150, 80, 70), (21, 32), (27, 32))
    pygame.draw.rect(s, PIEL_MUTADA, (29, 28, 4, 3))
    pygame.draw.rect(s, PIEL_MUTADA, (15, 15, 3, 2))
    pygame.draw.rect(s, (20, 20, 24), (0, 0, 48, 48), 1)
    carpeta = os.path.join(RAIZ, "retratos")
    os.makedirs(carpeta, exist_ok=True)
    pygame.image.save(s, os.path.join(carpeta, "becario.png"))


if __name__ == "__main__":
    pygame.init()
    generar_tileset()
    generar_protagonista()
    generar_retrato()
    print("Assets generados en", os.path.normpath(RAIZ))
