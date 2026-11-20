"""Genera el mapa del mundo ESQUEMÁTICO (SVG + PNG de 1920x1080) a partir de los datos.

Lee hispazombie/assets/data/world_map.json (zonas, puntos de interés y conexiones del GDD)
y dibuja un pergamino de estilo cartográfico simplificado, sin nombres de zona: el juego
los pondrá encima en HD para poder traducirlos. Es un mapa PROVISIONAL y una plantilla de
posiciones para el arte definitivo.

Uso:  uv run python tools/generate_world_map.py
"""

from __future__ import annotations

import json
import math
import os
import random

W, H = 1920, 1080
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hispazombie", "assets")
DATA = os.path.join(ROOT, "data", "world_map.json")
OUT_DIR = os.path.join(ROOT, "world")

PARCHMENT = "#e7d6b2"
INK = "#50381e"
INK_SOFT = "#7a5a36"
RADIOACTIVE = "#6fdc6f"
RIVER = "#5a7896"
WOOD = "#3b2a1c"

# Tinte suave de cada zona, para distinguirlas de un vistazo.
ZONE_TINT = {
    "alamillo_park": "#8fae6a",
    "cartuja": "#9fbf7a",
    "triana": "#c98f5a",
    "los_remedios": "#b9a27c",
    "river": "#8aa3b0",
    "old_town": "#c9a86a",
    "macarena": "#b98d6e",
    "noble_zone": "#a59a8a",
    "nervion": "#a0a6b4",
    "plaza_de_espana": "#c97f5a",
    "heliopolis": "#b0b880",
    "los_pueblos": "#cfc0a0",
}

rnd = random.Random(1966)


def px(point) -> tuple[float, float]:
    return point[0] * W / 100, point[1] * H / 100


def box_px(box) -> tuple[float, float, float, float]:
    x0, y0 = px(box[:2])
    x1, y1 = px(box[2:])
    return x0, y0, x1 - x0, y1 - y0


def box_center(box) -> tuple[float, float]:
    x, y, w, h = box_px(box)
    return x + w / 2, y + h / 2


def smooth_path(points: list[tuple[float, float]]) -> str:
    """Curva suave (Catmull-Rom convertida a Bézier) que pasa por todos los puntos."""
    d = f"M{points[0][0]:.1f} {points[0][1]:.1f}"
    for i in range(len(points) - 1):
        p0 = points[max(i - 1, 0)]
        p1, p2 = points[i], points[i + 1]
        p3 = points[min(i + 2, len(points) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d


def ragged_polygon(x0, y0, x1, y1, step=40, jitter=14) -> str:
    """Contorno irregular de papel roto."""
    pts = []
    for x in range(int(x0), int(x1), step):
        pts.append((x, y0 + rnd.uniform(-jitter, jitter)))
    for y in range(int(y0), int(y1), step):
        pts.append((x1 + rnd.uniform(-jitter, jitter), y))
    for x in range(int(x1), int(x0), -step):
        pts.append((x, y1 + rnd.uniform(-jitter, jitter)))
    for y in range(int(y1), int(y0), -step):
        pts.append((x0 + rnd.uniform(-jitter, jitter), y))
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


# --- Dibujos de los puntos de interés (formas simples, legibles a 480x270) ---


def poi_crater(x, y):
    shards = "".join(
        f'<polygon points="{x + dx:.0f},{y + dy - 26:.0f} {x + dx + 12:.0f},{y + dy:.0f} '
        f'{x + dx:.0f},{y + dy + 10:.0f} {x + dx - 12:.0f},{y + dy:.0f}" fill="#bff7bf" '
        f'stroke="#2f7a3a" stroke-width="3"/>'
        for dx, dy in ((-30, 0), (0, -12), (28, 6), (-6, 22))
    )
    return (
        f'<circle cx="{x}" cy="{y}" r="150" fill="{RADIOACTIVE}" fill-opacity="0.18"/>'
        f'<circle cx="{x}" cy="{y}" r="112" fill="#6b5a3e" stroke="{INK}" stroke-width="6"/>'
        f'<circle cx="{x}" cy="{y}" r="88" fill="#3f8f4a"/>'
        f'<circle cx="{x}" cy="{y}" r="62" fill="{RADIOACTIVE}"/>'
        f'<circle cx="{x}" cy="{y}" r="34" fill="#c8ffc8"/>' + shards
    )


def poi_tower_glass(x, y):
    return (
        f'<rect x="{x - 24}" y="{y - 150}" width="48" height="170" fill="#5d7a8c" '
        f'stroke="{INK}" stroke-width="6"/>'
        + "".join(
            f'<line x1="{x - 24}" y1="{y - 150 + i * 24}" x2="{x + 24}" y2="{y - 150 + i * 24}" '
            f'stroke="#9fb7c4" stroke-width="3"/>'
            for i in range(1, 7)
        )
        + f'<polyline points="{x - 8},{y - 140} {x + 6},{y - 100} {x - 4},{y - 70} {x + 10},{y - 30}" '
        f'fill="none" stroke="{INK}" stroke-width="4"/>'
        f'<rect x="{x - 34}" y="{y + 14}" width="68" height="14" fill="#8a1f1f" stroke="{INK}" '
        f'stroke-width="4"/>'  # sello: cerrada hasta el final
    )


def poi_bunker(x, y):
    return (
        f'<path d="M{x - 30} {y + 14} A30 30 0 0 1 {x + 30} {y + 14} Z" fill="#2b2118" '
        f'stroke="{INK}" stroke-width="5"/>'
        f'<rect x="{x + 40}" y="{y - 6}" width="44" height="18" fill="#e3b33a" stroke="{INK}" '
        f'stroke-width="4"/>'  # excavadora de la obra del Metro
        f'<line x1="{x + 84}" y1="{y}" x2="{x + 104}" y2="{y - 22}" stroke="{INK}" stroke-width="6"/>'
    )


def poi_settlement(x, y):
    houses = ""
    for dx in (-60, 0, 60):
        hx = x + dx
        houses += (
            f'<rect x="{hx - 22}" y="{y - 10}" width="44" height="34" fill="#d8b98a" '
            f'stroke="{INK}" stroke-width="5"/>'
            f'<polygon points="{hx - 30},{y - 10} {hx},{y - 38} {hx + 30},{y - 10}" '
            f'fill="#a8553a" stroke="{INK}" stroke-width="5"/>'
        )
    return houses


def poi_tunnels(x, y):
    return "".join(
        f'<path d="M{x + dx - 22} {y + 16} A22 22 0 0 1 {x + dx + 22} {y + 16} Z" fill="#2b2118" '
        f'stroke="{INK}" stroke-width="5"/>'
        for dx in (-60, 0, 60)
    )


def poi_torre_del_oro(x, y):
    merlons = "".join(
        f'<rect x="{x - 30 + i * 15}" y="{y - 92}" width="9" height="12" fill="#d9a441" '
        f'stroke="{INK}" stroke-width="3"/>'
        for i in range(5)
    )
    return (
        f'<rect x="{x - 32}" y="{y - 80}" width="64" height="100" fill="#d9a441" stroke="{INK}" '
        f'stroke-width="6"/>'
        f'<rect x="{x - 18}" y="{y - 120}" width="36" height="40" fill="#e3b85a" stroke="{INK}" '
        f'stroke-width="5"/>' + merlons
    )


def poi_giralda(x, y):
    return (
        f'<polygon points="{x},{y - 110} {x + 150},{y - 170} {x + 150},{y - 110}" '
        f'fill="#fff3a0" fill-opacity="0.4"/>'  # foco que barre el páramo
        f'<rect x="{x - 24}" y="{y - 90}" width="48" height="110" fill="#c8a26a" stroke="{INK}" '
        f'stroke-width="6"/>'
        f'<rect x="{x - 24}" y="{y - 64}" width="48" height="12" fill="#7d7d84" stroke="{INK}" '
        f'stroke-width="3"/>'  # planchas de acero
        f'<rect x="{x - 24}" y="{y - 30}" width="48" height="12" fill="#7d7d84" stroke="{INK}" '
        f'stroke-width="3"/>'
        f'<rect x="{x - 13}" y="{y - 116}" width="26" height="26" fill="#e8d18a" stroke="{INK}" '
        f'stroke-width="5"/>'
    )


def poi_setas(x, y):
    shapes = ""
    for dx in (-70, 0, 70):
        shapes += (
            f'<rect x="{x + dx - 8}" y="{y - 10}" width="16" height="40" fill="#8a6b45" '
            f'stroke="{INK}" stroke-width="4"/>'
            f'<ellipse cx="{x + dx}" cy="{y - 16}" rx="48" ry="18" fill="#9b7a55" stroke="{INK}" '
            f'stroke-width="5"/>'
        )
    return shapes + (
        f'<line x1="{x - 70}" y1="{y - 22}" x2="{x + 70}" y2="{y - 22}" stroke="#2b2118" '
        f'stroke-width="6" stroke-dasharray="14 10"/>'  # partes calcinadas
    )


def poi_alcazar(x, y):
    blobs = "".join(
        f'<circle cx="{x + dx}" cy="{y + dy}" r="{r}" fill="{RADIOACTIVE}" fill-opacity="0.7" '
        f'stroke="#2f7a3a" stroke-width="4"/>'
        for dx, dy, r in ((-70, -10, 30), (70, 0, 34), (-30, 40, 26), (40, 44, 28), (0, -46, 24))
    )
    return (
        f'<rect x="{x - 70}" y="{y - 36}" width="140" height="80" fill="#c9a86a" stroke="{INK}" '
        f'stroke-width="6"/>'
        f'<rect x="{x - 30}" y="{y - 14}" width="60" height="36" fill="#8aa36a" stroke="{INK}" '
        f'stroke-width="4"/>' + blobs
    )


def poi_walls(x, y):
    merlons = "".join(
        f'<rect x="{x - 150 + i * 30}" y="{y - 40}" width="18" height="14" fill="#b98d6e" '
        f'stroke="{INK}" stroke-width="3"/>'
        for i in range(11)
    )
    return (
        f'<rect x="{x - 150}" y="{y - 28}" width="312" height="40" fill="#b98d6e" stroke="{INK}" '
        f'stroke-width="6"/>'
        f'<path d="M{x - 22} {y + 12} L{x - 22} {y - 6} A22 22 0 0 1 {x + 22} {y - 6} L{x + 22} {y + 12} Z" '
        f'fill="#2b2118"/>' + merlons
    )


def poi_station(x, y):
    rails = "".join(
        f'<line x1="{x - 150}" y1="{y + 40 + i * 14}" x2="{x + 150}" y2="{y + 40 + i * 14}" '
        f'stroke="{INK}" stroke-width="4"/>'
        for i in range(2)
    )
    return (
        f'<path d="M{x - 110} {y + 24} L{x - 110} {y - 10} Q{x} {y - 70} {x + 110} {y - 10} '
        f'L{x + 110} {y + 24} Z" fill="#a59a8a" stroke="{INK}" stroke-width="6"/>' + rails
    )


def poi_stadium(x, y):
    return (
        f'<rect x="{x - 90}" y="{y - 55}" width="180" height="110" rx="50" fill="#9a9a9a" '
        f'stroke="{INK}" stroke-width="6"/>'
        f'<rect x="{x - 58}" y="{y - 30}" width="116" height="60" fill="#7aa35a" stroke="{INK}" '
        f'stroke-width="4"/>'
        f'<path d="M{x - 90} {y - 20} L{x - 60} {y - 55}" stroke="{INK}" stroke-width="5"/>'  # grieta
    )


def poi_plaza(x, y):
    r_out, r_in = 170, 120
    arc = (
        f'<path d="M{x - r_out} {y} A{r_out} {r_out} 0 0 1 {x + r_out} {y} L{x + r_in} {y} '
        f'A{r_in} {r_in} 0 0 0 {x - r_in} {y} Z" fill="#c97f5a" stroke="{INK}" stroke-width="6"/>'
    )
    canal = (
        f'<path d="M{x - 100} {y} A100 100 0 0 1 {x + 100} {y}" fill="none" stroke="#9e8f73" '
        f'stroke-width="10"/>'  # canal seco
    )
    spokes = "".join(
        f'<line x1="{x + r_in * math.cos(a):.0f}" y1="{y - r_in * math.sin(a):.0f}" '
        f'x2="{x + r_out * math.cos(a):.0f}" y2="{y - r_out * math.sin(a):.0f}" '
        f'stroke="{INK}" stroke-width="4"/>'
        for a in (math.pi * i / 8 for i in range(1, 8))
    )
    towers = "".join(
        f'<rect x="{x + dx - 16}" y="{y - 60}" width="32" height="66" fill="#d89a6a" '
        f'stroke="{INK}" stroke-width="5"/>'
        for dx in (-r_out + 10, r_out - 10)
    )
    return arc + canal + spokes + towers


POI_PAINTERS = {
    "crater": poi_crater,
    "torre_pelli": poi_tower_glass,
    "bunker": poi_bunker,
    "settlement": poi_settlement,
    "triana_tunnels": poi_tunnels,
    "torre_del_oro": poi_torre_del_oro,
    "giralda": poi_giralda,
    "setas": poi_setas,
    "alcazar": poi_alcazar,
    "macarena_walls": poi_walls,
    "station": poi_station,
    "stadium_nervion": poi_stadium,
    "plaza_semicircle": poi_plaza,
    "stadium_heliopolis": poi_stadium,
}


def rubble(box, count=18) -> str:
    """Manchitas de tinta: ruinas y calles, para que las zonas no queden vacías."""
    x, y, w, h = box_px(box)
    out = ""
    for _ in range(count):
        rx, ry = x + rnd.uniform(0.08, 0.92) * w, y + rnd.uniform(0.1, 0.9) * h
        s = rnd.uniform(10, 22)
        out += (
            f'<rect x="{rx:.0f}" y="{ry:.0f}" width="{s:.0f}" height="{s * 0.7:.0f}" '
            f'fill="none" stroke="{INK_SOFT}" stroke-width="3" stroke-opacity="0.55"/>'
        )
    return out


def connection_path(a, b, mid) -> str:
    """Curva cuadrática de a a b que pasa exactamente por el punto medio indicado."""
    mx, my = mid
    cx, cy = 2 * mx - (a[0] + b[0]) / 2, 2 * my - (a[1] + b[1]) / 2
    return f"M{a[0]:.1f} {a[1]:.1f} Q{cx:.1f} {cy:.1f} {b[0]:.1f} {b[1]:.1f}"


def bridge_mark(mid, a, b) -> str:
    """Tablones perpendiculares al camino: indican un puente sobre el río."""
    angle = math.atan2(b[1] - a[1], b[0] - a[0])
    nx, ny = -math.sin(angle), math.cos(angle)
    out = ""
    for t in (-24, -8, 8, 24):
        cx, cy = mid[0] + math.cos(angle) * t, mid[1] + math.sin(angle) * t
        out += (
            f'<line x1="{cx - nx * 20:.0f}" y1="{cy - ny * 20:.0f}" x2="{cx + nx * 20:.0f}" '
            f'y2="{cy + ny * 20:.0f}" stroke="{INK}" stroke-width="6"/>'
        )
    return out


def compass(x, y) -> str:
    star = []
    for i in range(16):
        r = 80 if i % 4 == 0 else (42 if i % 2 == 0 else 22)
        a = math.pi / 2 - i * math.pi / 8
        star.append(f"{x + r * math.cos(a):.0f},{y - r * math.sin(a):.0f}")
    return (
        f'<circle cx="{x}" cy="{y}" r="62" fill="none" stroke="{INK}" stroke-width="5"/>'
        f'<polygon points="{" ".join(star)}" fill="#d9c49a" stroke="{INK}" stroke-width="5"/>'
        f'<polygon points="{x},{y - 80} {x + 12},{y} {x - 12},{y}" fill="#8a1f1f"/>'
        f'<text x="{x}" y="{y - 92}" font-family="serif" font-size="40" font-weight="bold" '
        f'fill="{INK}" text-anchor="middle">N</text>'
    )


def build_svg(data: dict) -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="{WOOD}"/>',
    ]
    paper = ragged_polygon(40, 34, W - 40, H - 34)
    parts.append(f'<polygon points="{paper}" fill="{PARCHMENT}"/>')
    # Manchas del papel y de café.
    for _ in range(14):
        parts.append(
            f'<ellipse cx="{rnd.uniform(100, W - 100):.0f}" cy="{rnd.uniform(80, H - 80):.0f}" '
            f'rx="{rnd.uniform(60, 200):.0f}" ry="{rnd.uniform(40, 140):.0f}" fill="#d4bd8f" '
            f'fill-opacity="0.35"/>'
        )
    for cx, cy, r in ((1700, 160, 70), (300, 930, 55), (1180, 980, 40)):
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#a77b4a" fill-opacity="0.12" '
            f'stroke="#8a5f33" stroke-opacity="0.35" stroke-width="7"/>'
        )
    # Dobleces del papel.
    for line in ((W / 2, 40, W / 2, H - 40), (40, H / 2, W - 40, H / 2)):
        parts.append(
            f'<line x1="{line[0]}" y1="{line[1]}" x2="{line[2]}" y2="{line[3]}" stroke="#c4ad80" '
            f'stroke-width="4" stroke-opacity="0.7"/>'
        )

    # Río Guadalquivir: de norte a sur, verde de lo tóxico que está.
    river = smooth_path([px(p) for p in data["river"]])
    parts.append(f'<path d="{river}" fill="none" stroke="{INK}" stroke-width="86"/>')
    parts.append(f'<path d="{river}" fill="none" stroke="{RIVER}" stroke-width="74"/>')
    parts.append(
        f'<path d="{river}" fill="none" stroke="#7fae7a" stroke-width="34" stroke-opacity="0.55"/>'
    )

    # Zonas.
    zones = {**data["zones"], **data["expansion_zones"]}
    for zone_id, zone in zones.items():
        x, y, w, h = box_px(zone["box"])
        expansion = zone_id in data["expansion_zones"]
        dash = ' stroke-dasharray="18 12"' if expansion else ""
        opacity = 0.12 if expansion else 0.28
        parts.append(
            f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="22" '
            f'fill="{ZONE_TINT.get(zone_id, "#c0a880")}" fill-opacity="{opacity}" stroke="{INK}" '
            f'stroke-width="6" stroke-opacity="{0.45 if expansion else 0.9}"{dash}/>'
        )
        if not expansion:
            parts.append(rubble(zone["box"]))

    # Conexiones (por debajo de los puntos de interés).
    for conn in data["connections"] + data["expansion_connections"]:
        a, b = box_center(zones[conn["a"]]["box"]), box_center(zones[conn["b"]]["box"])
        mid = px(conn["midpoint"])
        expansion = conn["id"].startswith("x")
        style = 'stroke-dasharray="20 14" stroke-opacity="0.5"' if expansion else ""
        path = connection_path(a, b, mid)
        parts.append(f'<path d="{path}" fill="none" stroke="#f3e7c8" stroke-width="18" {style}/>')
        parts.append(f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="8" {style}/>')
        if conn.get("kind") == "bridge":
            parts.append(bridge_mark(mid, a, b))

    # Puntos de interés.
    for poi_id, poi in data["points_of_interest"].items():
        x, y = px(poi["at"])
        parts.append(POI_PAINTERS[poi_id](x, y))

    parts.append(compass(150, H - 150))
    parts.append(
        f'<text x="{W / 2}" y="{H - 60}" font-family="serif" font-style="italic" font-size="34" '
        f'fill="{INK}" text-anchor="middle">1 siesta = 2 calles</text>'
    )
    parts.append(
        f'<polygon points="{paper}" fill="none" stroke="#5a3a1a" stroke-width="22" stroke-opacity="0.45"/>'
    )
    parts.append(f'<polygon points="{paper}" fill="none" stroke="#2e1c0c" stroke-width="6"/>')
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    os.makedirs(OUT_DIR, exist_ok=True)
    svg_path = os.path.join(OUT_DIR, "world_map_base.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(build_svg(data))

    # PNG con pygame (rasterizador nanosvg: ignora los <text>; el juego dibuja los textos en HD).
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame

    pygame.init()
    png_path = os.path.join(OUT_DIR, "world_map_base.png")
    pygame.image.save(pygame.image.load(svg_path), png_path)
    print("Mapa del mundo generado:", os.path.normpath(svg_path), "y", os.path.normpath(png_path))


if __name__ == "__main__":
    main()
