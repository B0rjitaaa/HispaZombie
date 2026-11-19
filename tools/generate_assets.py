"""Genera los gráficos PROVISIONALES del juego (tileset, sprite y retrato del protagonista).

Son pixel art hecho con código para poder avanzar sin depender de arte externo. Cuando haya
arte definitivo se sustituyen los PNG manteniendo el mismo orden de tiles.

Uso:  uv run python tools/generate_assets.py
"""

from __future__ import annotations

import json
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hispazombie", "assets")
T = 16
COLUMNS = 8

# (nombre, sólido). El índice en esta lista es el id del tile en Tiled.
TILES: list[tuple[str, bool]] = [
    ("void", True),  # 0
    ("concrete_floor", False),  # 1
    ("concrete_floor_stained", False),  # 2
    ("concrete_wall", True),  # 3
    ("wall_top", True),  # 4
    ("wall_poster", True),  # 5
    ("wall_panel", True),  # 6
    ("stairs", False),  # 7
    ("dirt", False),  # 8
    ("dirt_cracked", False),  # 9
    ("ash", False),  # 10
    ("dry_grass", False),  # 11
    ("asphalt", False),  # 12
    ("asphalt_line", False),  # 13
    ("rubble", True),  # 14
    ("ruin_brick", True),  # 15
    ("ruin_window", True),  # 16
    ("ruin_roof", True),  # 17
    ("construction_fence", True),  # 18
    ("traffic_cone", True),  # 19
    ("pipe", True),  # 20
    ("radioactive_glass", True),  # 21
    ("crater_edge", True),  # 22
    ("toxic_puddle", True),  # 23
    ("dead_tree", True),  # 24
    ("chest_closed", True),  # 25
    ("chest_open", True),  # 26
    ("signpost", True),  # 27
    ("radiation_sign", True),  # 28
    ("chrysalis", True),  # 29
    ("coffee_tray", True),  # 30
    ("excavator_left", True),  # 31
    ("excavator_right", True),  # 32
    ("bunker_hole", False),  # 33
    ("pebble", False),  # 34
    ("tower_glass", True),  # 35
    ("tower_base", True),  # 36
    ("hard_hat", True),  # 37
]
ID = {name: i for i, (name, _) in enumerate(TILES)}

# Texto que se muestra al chocar contra ciertos tiles (propiedad "texto_choque" en Tiled).
BUMP_TEXTS = {
    "crater_edge": "El borde del cráter. Abajo, todo es cristal verde y brillante.\n\n"
    "@intern\nNo. Ni de broma.",
    "radioactive_glass": "Cristal radiactivo. Brilla bonito. Demasiado bonito.",
    "toxic_puddle": "Un charco verde que burbujea solo.\n\n@intern\nMejor rodearlo.",
}

rnd = random.Random(1966)  # Palomares


def noise(s: pygame.Surface, base, variations, density=0.35) -> None:
    s.fill(base)
    for y in range(T):
        for x in range(T):
            if rnd.random() < density:
                s.set_at((x, y), rnd.choice(variations))


def dirt(s, extra=None):
    noise(s, (122, 98, 70), [(110, 88, 62), (134, 108, 78), (100, 80, 58)])
    if extra:
        extra(s)


def cracks(s):
    dirt(s)
    x, y = rnd.randint(2, 6), rnd.randint(2, 6)
    for _ in range(9):
        s.set_at((x, y), (70, 54, 40))
        x = min(T - 1, x + rnd.choice((0, 1)))
        y = min(T - 1, y + rnd.choice((0, 1, 1)))


def ash(s):
    noise(s, (104, 100, 96), [(92, 88, 86), (118, 114, 110), (84, 80, 78)], 0.45)


def grass(s):
    dirt(s)
    for _ in range(7):
        x, y = rnd.randint(1, 14), rnd.randint(3, 15)
        pygame.draw.line(s, (160, 150, 70), (x, y), (x + rnd.choice((-1, 0, 1)), y - 3))


def concrete(s, stained=False):
    noise(s, (92, 92, 96), [(84, 84, 88), (100, 100, 104)], 0.3)
    pygame.draw.line(s, (78, 78, 82), (0, T - 1), (T - 1, T - 1))
    pygame.draw.line(s, (78, 78, 82), (T - 1, 0), (T - 1, T - 1))
    if stained:
        pygame.draw.ellipse(s, (70, 76, 64), (3, 5, 9, 6))
        pygame.draw.ellipse(s, (60, 66, 54), (5, 6, 5, 3))


def wall(s):
    noise(s, (130, 128, 122), [(120, 118, 112), (140, 138, 132)], 0.3)
    for y in (5, 11):
        pygame.draw.line(s, (104, 102, 98), (0, y), (T - 1, y))
    pygame.draw.line(s, (60, 58, 56), (0, T - 1), (T - 1, T - 1))


def ceiling(s):
    noise(s, (58, 56, 60), [(50, 48, 52), (66, 64, 68)], 0.3)


def poster(s):
    wall(s)
    pygame.draw.rect(s, (196, 170, 120), (3, 1, 10, 12))
    pygame.draw.rect(s, (150, 40, 34), (4, 2, 8, 3))
    pygame.draw.line(s, (60, 50, 40), (5, 7), (10, 7))
    pygame.draw.line(s, (60, 50, 40), (5, 9), (9, 9))
    pygame.draw.line(s, (60, 50, 40), (5, 11), (10, 11))


def panel(s):
    wall(s)
    pygame.draw.rect(s, (70, 80, 72), (3, 2, 10, 11))
    pygame.draw.rect(s, (40, 46, 42), (3, 2, 10, 11), 1)
    s.set_at((6, 5), (220, 40, 30))
    s.set_at((9, 5), (60, 200, 70))
    pygame.draw.line(s, (200, 180, 40), (5, 9), (10, 9))


def stairs(s):
    ceiling(s)
    for i, y in enumerate(range(2, T, 3)):
        c = 90 + i * 14
        pygame.draw.rect(s, (c, c, c + 4), (2, y, 12, 2))


def asphalt(s, line=False):
    noise(s, (62, 62, 66), [(54, 54, 58), (72, 72, 76)], 0.4)
    if line:
        pygame.draw.rect(s, (210, 190, 90), (2, 7, 7, 2))


def rubble(s):
    for _ in range(6):
        x, y = rnd.randint(0, 10), rnd.randint(4, 11)
        c = rnd.choice([(120, 116, 110), (96, 92, 88), (140, 120, 100)])
        pygame.draw.polygon(s, c, [(x, y + 5), (x + 3, y), (x + 6, y + 5)])
        pygame.draw.line(s, (60, 58, 56), (x, y + 5), (x + 6, y + 5))


def brick(s, window=False):
    s.fill((150, 86, 62))
    for row, y in enumerate(range(0, T, 4)):
        pygame.draw.line(s, (110, 64, 48), (0, y), (T - 1, y))
        offset = 0 if row % 2 else 4
        for x in range(offset, T, 8):
            pygame.draw.line(s, (110, 64, 48), (x, y), (x, y + 3))
    for _ in range(4):
        s.set_at((rnd.randint(0, 15), rnd.randint(0, 15)), (90, 50, 40))
    if window:
        pygame.draw.rect(s, (24, 22, 26), (4, 3, 8, 9))
        pygame.draw.line(s, (180, 200, 210), (5, 4), (7, 8))


def ruin_roof(s):
    noise(s, (86, 70, 62), [(76, 62, 56), (96, 80, 70)], 0.4)
    pygame.draw.line(s, (60, 48, 42), (0, rnd.randint(3, 12)), (T - 1, rnd.randint(3, 12)))


def fence(s):
    for x in (1, 14):
        pygame.draw.rect(s, (90, 90, 90), (x, 2, 2, 14))
    for y in (4, 9):
        for x in range(0, T, 4):
            color = (230, 60, 40) if (x // 4) % 2 == 0 else (240, 240, 230)
            pygame.draw.rect(s, color, (x, y, 4, 3))


def cone(s):
    pygame.draw.polygon(s, (240, 110, 30), [(8, 2), (12, 13), (4, 13)])
    pygame.draw.line(s, (250, 250, 240), (6, 9), (10, 9))
    pygame.draw.rect(s, (60, 60, 60), (3, 13, 10, 2))


def pipe(s):
    pygame.draw.rect(s, (110, 120, 128), (0, 4, T, 9))
    pygame.draw.line(s, (160, 170, 178), (0, 5), (T - 1, 5))
    pygame.draw.line(s, (70, 76, 82), (0, 12), (T - 1, 12))


def glass(s):
    noise(s, (60, 170, 90), [(90, 220, 120), (40, 130, 70), (140, 255, 170)], 0.4)
    pygame.draw.line(s, (200, 255, 210), (2, 3), (6, 7))
    pygame.draw.line(s, (200, 255, 210), (10, 10), (13, 12))


def crater_edge(s):
    noise(s, (70, 64, 56), [(54, 50, 44), (90, 86, 70), (60, 120, 70)], 0.5)


def puddle(s):
    dirt(s)
    pygame.draw.ellipse(s, (90, 180, 60), (1, 4, 14, 9))
    pygame.draw.ellipse(s, (140, 230, 90), (4, 6, 5, 3))


def tree(s):
    pygame.draw.line(s, (70, 52, 40), (8, 15), (8, 4))
    pygame.draw.line(s, (70, 52, 40), (8, 8), (4, 4))
    pygame.draw.line(s, (70, 52, 40), (8, 6), (12, 2))
    pygame.draw.line(s, (70, 52, 40), (4, 4), (3, 1))


def chest(s, is_open=False):
    pygame.draw.rect(s, (60, 70, 60), (2, 6, 12, 9))
    pygame.draw.rect(s, (36, 42, 36), (2, 6, 12, 9), 1)
    if is_open:
        pygame.draw.rect(s, (20, 20, 20), (3, 7, 10, 3))
        pygame.draw.rect(s, (80, 92, 80), (2, 2, 12, 4))
    else:
        pygame.draw.rect(s, (80, 92, 80), (2, 4, 12, 4))
        pygame.draw.rect(s, (200, 180, 60), (7, 7, 2, 3))


def signpost(s):
    pygame.draw.rect(s, (90, 66, 44), (7, 8, 2, 8))
    pygame.draw.rect(s, (200, 180, 130), (2, 2, 12, 7))
    pygame.draw.rect(s, (110, 84, 56), (2, 2, 12, 7), 1)
    pygame.draw.line(s, (80, 60, 40), (4, 4), (11, 4))
    pygame.draw.line(s, (80, 60, 40), (4, 6), (9, 6))


def radiation_sign(s):
    pygame.draw.rect(s, (90, 90, 90), (7, 9, 2, 7))
    pygame.draw.polygon(s, (240, 210, 40), [(8, 0), (15, 11), (1, 11)])
    pygame.draw.polygon(s, (20, 20, 20), [(8, 0), (15, 11), (1, 11)], 1)
    pygame.draw.circle(s, (20, 20, 20), (8, 7), 2)


def chrysalis(s):
    pygame.draw.ellipse(s, (150, 160, 110), (1, 5, 14, 10))
    pygame.draw.ellipse(s, (110, 130, 80), (1, 5, 14, 10), 1)
    pygame.draw.polygon(s, (30, 30, 26), [(5, 7), (11, 6), (10, 12), (6, 11)])
    s.set_at((4, 10), (180, 240, 120))
    s.set_at((12, 9), (180, 240, 120))


def coffee_tray(s):
    pygame.draw.ellipse(s, (170, 170, 176), (1, 8, 14, 7))
    for x in (3, 7, 11):
        pygame.draw.rect(s, (240, 236, 226), (x, 6, 3, 5))
        s.set_at((x + 1, 6), (90, 60, 40))


def excavator(s, side):
    if side == "left":
        pygame.draw.rect(s, (230, 170, 30), (4, 5, 12, 8))
        pygame.draw.rect(s, (40, 60, 70), (7, 1, 7, 5))
        pygame.draw.rect(s, (40, 40, 40), (3, 12, 13, 4))
    else:
        pygame.draw.rect(s, (230, 170, 30), (0, 6, 9, 7))
        pygame.draw.line(s, (230, 170, 30), (8, 7), (13, 3), 2)
        pygame.draw.polygon(s, (120, 120, 120), [(11, 3), (15, 3), (15, 9), (12, 7)])
        pygame.draw.rect(s, (40, 40, 40), (0, 12, 10, 4))


def bunker_hole(s):
    dirt(s)
    pygame.draw.ellipse(s, (20, 18, 16), (1, 3, 14, 11))
    pygame.draw.line(s, (130, 130, 130), (5, 4), (5, 12))
    pygame.draw.line(s, (130, 130, 130), (10, 4), (10, 12))
    for y in (6, 9):
        pygame.draw.line(s, (130, 130, 130), (5, y), (10, y))


def pebble(s):
    pygame.draw.polygon(s, (118, 112, 106), [(4, 12), (7, 8), (10, 12)])
    s.set_at((12, 13), (96, 92, 88))


def tower(s, base=False):
    s.fill((46, 58, 70))
    for x in range(1, T, 5):
        pygame.draw.line(s, (80, 100, 120), (x, 0), (x, T - 1))
    pygame.draw.line(s, (24, 30, 36), (0, 7), (T - 1, 7))
    if rnd.random() < 0.5:
        pygame.draw.line(s, (150, 170, 190), (3, 2), (7, 12))
    if base:
        pygame.draw.rect(s, (90, 88, 84), (0, 10, T, 6))


def hard_hat(s):
    pygame.draw.ellipse(s, (240, 200, 40), (3, 6, 10, 8))
    pygame.draw.rect(s, (240, 200, 40), (2, 11, 12, 2))
    pygame.draw.line(s, (200, 160, 30), (8, 6), (8, 12))


PAINTERS = {
    "void": lambda s: s.fill((0, 0, 0)),
    "concrete_floor": concrete,
    "concrete_floor_stained": lambda s: concrete(s, True),
    "concrete_wall": wall,
    "wall_top": ceiling,
    "wall_poster": poster,
    "wall_panel": panel,
    "stairs": stairs,
    "dirt": dirt,
    "dirt_cracked": cracks,
    "ash": ash,
    "dry_grass": grass,
    "asphalt": asphalt,
    "asphalt_line": lambda s: asphalt(s, True),
    "rubble": rubble,
    "ruin_brick": brick,
    "ruin_window": lambda s: brick(s, True),
    "ruin_roof": ruin_roof,
    "construction_fence": fence,
    "traffic_cone": cone,
    "pipe": pipe,
    "radioactive_glass": glass,
    "crater_edge": crater_edge,
    "toxic_puddle": puddle,
    "dead_tree": tree,
    "chest_closed": chest,
    "chest_open": lambda s: chest(s, True),
    "signpost": signpost,
    "radiation_sign": radiation_sign,
    "chrysalis": chrysalis,
    "coffee_tray": coffee_tray,
    "excavator_left": lambda s: excavator(s, "left"),
    "excavator_right": lambda s: excavator(s, "right"),
    "bunker_hole": bunker_hole,
    "pebble": pebble,
    "tower_glass": tower,
    "tower_base": lambda s: tower(s, True),
    "hard_hat": hard_hat,
}


def generate_tileset() -> None:
    rows = (len(TILES) + COLUMNS - 1) // COLUMNS
    sheet = pygame.Surface((COLUMNS * T, rows * T), pygame.SRCALPHA)
    for i, (name, _) in enumerate(TILES):
        tile = pygame.Surface((T, T), pygame.SRCALPHA)
        PAINTERS[name](tile)
        sheet.blit(tile, ((i % COLUMNS) * T, (i // COLUMNS) * T))

    folder = os.path.join(ROOT, "tilesets")
    os.makedirs(folder, exist_ok=True)
    pygame.image.save(sheet, os.path.join(folder, "cartuja.png"))

    tiles_json = []
    for i, (name, solid) in enumerate(TILES):
        props = [{"name": "name", "type": "string", "value": name}]
        if solid:
            props.append({"name": "solid", "type": "bool", "value": True})
        if name in BUMP_TEXTS:
            props.append({"name": "bump_text", "type": "string", "value": BUMP_TEXTS[name]})
        if name == "chest_closed":
            props.append({"name": "open_id", "type": "int", "value": ID["chest_open"]})
        tiles_json.append({"id": i, "properties": props})

    tsj = {
        "type": "tileset",
        "version": "1.10",
        "tiledversion": "1.11.0",
        "name": "cartuja",
        "image": "cartuja.png",
        "imagewidth": sheet.get_width(),
        "imageheight": sheet.get_height(),
        "tilewidth": T,
        "tileheight": T,
        "tilecount": len(TILES),
        "columns": COLUMNS,
        "margin": 0,
        "spacing": 0,
        "tiles": tiles_json,
    }
    with open(os.path.join(folder, "cartuja.tsj"), "w", encoding="utf-8") as f:
        json.dump(tsj, f, ensure_ascii=False, indent=1)


# --- Protagonista: hoja de 3 frames x 4 direcciones (abajo, izquierda, derecha, arriba) ---

CHAR_WIDTH, CHAR_HEIGHT = 16, 24
SKIN = (226, 184, 150)
MUTATED_SKIN = (150, 200, 120)
HAIR = (92, 60, 36)
SHIRT = (236, 236, 228)
TROUSERS = (52, 70, 120)
SHOE = (40, 32, 28)
BADGE = (220, 40, 40)
EYE = (20, 20, 20)


def draw_character(s: pygame.Surface, direction: str, frame: int) -> None:
    # Piernas: el frame 1 es la postura quieta; 0 y 2 alternan las piernas.
    step = {0: -1, 1: 0, 2: 1}[frame]
    if direction in ("down", "up"):
        pygame.draw.rect(s, TROUSERS, (5, 16, 3, 6 + max(0, -step)))
        pygame.draw.rect(s, TROUSERS, (8, 16, 3, 6 + max(0, step)))
        pygame.draw.rect(s, SHOE, (5, 21 + max(0, -step), 3, 2))
        pygame.draw.rect(s, SHOE, (8, 21 + max(0, step), 3, 2))
    else:
        pygame.draw.rect(s, TROUSERS, (6 + step, 16, 3, 6))
        pygame.draw.rect(s, TROUSERS, (7 - step, 16, 3, 6))
        pygame.draw.rect(s, SHOE, (6 + step, 21, 3, 2))
        pygame.draw.rect(s, SHOE, (7 - step, 21, 3, 2))

    # Cuerpo con camisa rota y brazos.
    pygame.draw.rect(s, SHIRT, (4, 10, 8, 7))
    s.set_at((5, 15), (180, 180, 172))
    s.set_at((10, 12), (180, 180, 172))
    arm = step if direction in ("down", "up") else 0
    pygame.draw.rect(s, SKIN, (3, 11 + arm, 1, 4))
    pygame.draw.rect(s, MUTATED_SKIN, (12, 11 - arm, 1, 4))

    # Cabeza.
    pygame.draw.rect(s, SKIN, (4, 2, 8, 8))
    if direction == "up":
        pygame.draw.rect(s, HAIR, (4, 1, 8, 7))
    else:
        pygame.draw.rect(s, HAIR, (4, 1, 8, 3))
        s.set_at((10, 6), MUTATED_SKIN)  # mancha de la mutación
        s.set_at((11, 7), MUTATED_SKIN)
        if direction == "down":
            s.set_at((6, 6), EYE)
            s.set_at((9, 6), EYE)
            # Acreditación de "BECARIO" colgando.
            pygame.draw.line(s, BADGE, (6, 10), (8, 13))
            pygame.draw.rect(s, (250, 250, 250), (7, 13, 3, 3))
        elif direction == "left":
            s.set_at((5, 6), EYE)
            pygame.draw.rect(s, HAIR, (9, 1, 3, 6))
        else:
            s.set_at((10, 6), EYE)
            pygame.draw.rect(s, HAIR, (4, 1, 3, 6))


def generate_protagonist() -> None:
    directions = ("down", "left", "right", "up")
    sheet = pygame.Surface((CHAR_WIDTH * 3, CHAR_HEIGHT * 4), pygame.SRCALPHA)
    for row, direction in enumerate(directions):
        for frame in range(3):
            cell = pygame.Surface((CHAR_WIDTH, CHAR_HEIGHT), pygame.SRCALPHA)
            draw_character(cell, direction, frame)
            sheet.blit(cell, (frame * CHAR_WIDTH, row * CHAR_HEIGHT))
    folder = os.path.join(ROOT, "sprites")
    os.makedirs(folder, exist_ok=True)
    pygame.image.save(sheet, os.path.join(folder, "intern.png"))


def generate_portrait() -> None:
    s = pygame.Surface((48, 48), pygame.SRCALPHA)
    s.fill((40, 44, 52))
    pygame.draw.rect(s, SHIRT, (8, 38, 32, 10))
    pygame.draw.line(s, BADGE, (18, 38), (24, 46), 2)
    pygame.draw.rect(s, SKIN, (14, 12, 20, 26))
    pygame.draw.rect(s, HAIR, (12, 6, 24, 9))
    pygame.draw.rect(s, HAIR, (12, 10, 4, 10))
    pygame.draw.rect(s, HAIR, (31, 9, 5, 6))  # pelo de recién despertado
    pygame.draw.rect(s, (250, 250, 250), (18, 21, 5, 4))
    pygame.draw.rect(s, (250, 250, 250), (26, 21, 5, 4))
    pygame.draw.rect(s, EYE, (20, 22, 2, 2))
    pygame.draw.rect(s, EYE, (28, 22, 2, 2))
    pygame.draw.line(s, (120, 90, 80), (18, 26), (22, 27))  # ojeras
    pygame.draw.line(s, (120, 90, 80), (26, 27), (30, 26))
    pygame.draw.line(s, (150, 80, 70), (21, 32), (27, 32))
    pygame.draw.rect(s, MUTATED_SKIN, (29, 28, 4, 3))
    pygame.draw.rect(s, MUTATED_SKIN, (15, 15, 3, 2))
    pygame.draw.rect(s, (20, 20, 24), (0, 0, 48, 48), 1)
    folder = os.path.join(ROOT, "portraits")
    os.makedirs(folder, exist_ok=True)
    pygame.image.save(s, os.path.join(folder, "intern.png"))


# --- NPC: se generan recoloreando al protagonista y añadiendo algún detalle ---

# Manolo el Chatarrero: chaleco reflectante naranja, pelo canoso, piel sin mutar.
SCRAPPER_COLORS = {
    SHIRT: (236, 120, 40),
    HAIR: (170, 170, 168),
    TROUSERS: (96, 76, 54),
    MUTATED_SKIN: SKIN,
    BADGE: (230, 230, 120),
}


def recolor(surface: pygame.Surface, mapping: dict) -> pygame.Surface:
    result = surface.copy()
    for y in range(result.get_height()):
        for x in range(result.get_width()):
            c = result.get_at((x, y))
            new = mapping.get((c.r, c.g, c.b))
            if new and c.a:
                result.set_at((x, y), (*new, c.a))
    return result


def generate_scrapper() -> None:
    sheet = pygame.image.load(os.path.join(ROOT, "sprites", "intern.png"))
    sheet = recolor(sheet, SCRAPPER_COLORS)
    # Franja reflectante del chaleco en los frames de frente y de espaldas.
    for row in (0, 3):
        for frame in range(3):
            ox, oy = frame * CHAR_WIDTH, row * CHAR_HEIGHT
            pygame.draw.line(sheet, (240, 240, 200), (ox + 4, oy + 14), (ox + 11, oy + 14))
    pygame.image.save(sheet, os.path.join(ROOT, "sprites", "scrapper.png"))

    portrait = pygame.image.load(os.path.join(ROOT, "portraits", "intern.png"))
    portrait = recolor(portrait, SCRAPPER_COLORS)
    pygame.draw.rect(portrait, (240, 240, 200), (8, 42, 32, 2))  # franja del chaleco
    pygame.draw.rect(portrait, (150, 150, 148), (16, 31, 16, 5))  # bigote canoso
    pygame.draw.rect(portrait, (20, 20, 24), (0, 0, 48, 48), 1)
    pygame.image.save(portrait, os.path.join(ROOT, "portraits", "scrapper.png"))


if __name__ == "__main__":
    pygame.init()
    generate_tileset()
    generate_protagonist()
    generate_portrait()
    generate_scrapper()
    print("Assets generados en", os.path.normpath(ROOT))
