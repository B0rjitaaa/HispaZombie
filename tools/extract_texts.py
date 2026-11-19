"""Extrae todos los textos del juego y actualiza los catálogos de traducción.

Busca textos en:
  * Mapas (.tmj): nombre del mapa y propiedad "text" de los eventos.
  * Tilesets (.tsj): propiedad "bump_text" de los tiles.
  * assets/data/items.json: nombres y descripciones de los objetos.
  * Scripts de eventos (assets/events/**/*.json): campos "text" y "label".
  * Código Python: llamadas tr(), mark(), show() y show_text() con un texto literal.

Para cada idioma crea o actualiza assets/i18n/<idioma>.json. Conserva las traducciones ya
hechas, añade los textos nuevos con traducción vacía ("") y avisa de los que ya no se usan.
Un texto sin traducir se muestra en español en el juego.

Uso:  uv run python tools/extract_texts.py [idioma ...]     (por defecto: en)
"""

from __future__ import annotations

import ast
import glob
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hispazombie")
ASSETS = os.path.join(ROOT, "assets")
I18N_DIR = os.path.join(ASSETS, "i18n")

# Funciones del juego que traducen el texto que reciben.
TRANSLATING_FUNCTIONS = {"tr", "mark", "show", "show_text"}


def _props(data: dict) -> dict:
    return {p["name"]: p["value"] for p in data.get("properties", [])}


def texts_from_maps() -> set[str]:
    texts: set[str] = set()
    for path in glob.glob(os.path.join(ASSETS, "maps", "*.tmj")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        name = _props(data).get("name")
        if name:
            texts.add(name)
        for layer in data["layers"]:
            for obj in layer.get("objects", []):
                text = _props(obj).get("text")
                if text:
                    texts.add(text)
    return texts


def texts_from_tilesets() -> set[str]:
    texts: set[str] = set()
    for path in glob.glob(os.path.join(ASSETS, "tilesets", "*.tsj")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for tile in data.get("tiles", []):
            text = _props(tile).get("bump_text")
            if text:
                texts.add(text)
    return texts


def texts_from_items() -> set[str]:
    with open(os.path.join(ASSETS, "data", "items.json"), encoding="utf-8") as f:
        data = json.load(f)
    texts: set[str] = set()
    for item in data.values():
        texts.update(v for k, v in item.items() if k in ("name", "description") and v)
    return texts


def texts_from_events() -> set[str]:
    texts: set[str] = set()

    def walk(node) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ("text", "label") and isinstance(value, str) and value:
                    texts.add(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    for path in glob.glob(os.path.join(ASSETS, "events", "**", "*.json"), recursive=True):
        with open(path, encoding="utf-8") as f:
            walk(json.load(f))
    return texts


def texts_from_code() -> set[str]:
    """Textos literales pasados a tr() o a show() en el código del juego."""
    texts: set[str] = set()
    for path in glob.glob(os.path.join(ROOT, "**", "*.py"), recursive=True):
        if os.sep + "build" + os.sep in path:
            continue
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), path)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
            if (
                name in TRANSLATING_FUNCTIONS
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                texts.add(node.args[0].value)
    return texts


def all_texts() -> set[str]:
    return (
        texts_from_maps()
        | texts_from_tilesets()
        | texts_from_items()
        | texts_from_events()
        | texts_from_code()
    )


def update_catalog(language: str, texts: set[str]) -> None:
    path = os.path.join(I18N_DIR, f"{language}.json")
    old: dict[str, str] = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = json.load(f)

    catalog = {text: old.get(text, "") for text in sorted(texts)}
    unused = sorted(set(old) - texts)
    os.makedirs(I18N_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
        f.write("\n")

    pending = sum(1 for v in catalog.values() if not v)
    print(f"{language}: {len(catalog)} textos, {pending} sin traducir -> {os.path.normpath(path)}")
    for text in unused:
        print(f"  (ya no se usa, eliminado) {text[:60]!r}")


if __name__ == "__main__":
    languages = sys.argv[1:] or ["en"]
    texts = all_texts()
    for lang in languages:
        update_catalog(lang, texts)
