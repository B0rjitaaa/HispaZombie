"""Traducción de los textos del juego.

Los textos se escriben directamente en español (en los mapas de Tiled, en los datos y en
el código con tr("...")). El español es el idioma original y no necesita catálogo.

Para otro idioma existe un catálogo assets/i18n/<idioma>.json que asocia cada texto en
español con su traducción. Si falta una traducción, se muestra el texto en español.
El catálogo se genera y actualiza con: uv run python tools/extract_texts.py
"""

from __future__ import annotations

import json
import os

SOURCE_LANGUAGE = "es"

_language = SOURCE_LANGUAGE
_catalog: dict[str, str] = {}


def set_language(language: str, i18n_dir: str) -> None:
    """Activa un idioma cargando su catálogo (si existe)."""
    global _language, _catalog
    _language = language
    _catalog = {}
    if language == SOURCE_LANGUAGE:
        return
    path = os.path.join(i18n_dir, f"{language}.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            _catalog = {k: v for k, v in json.load(f).items() if v}


def current_language() -> str:
    return _language


def tr(text: str) -> str:
    """Devuelve el texto traducido al idioma activo (o el original si no hay traducción)."""
    if not text or _language == SOURCE_LANGUAGE:
        return text
    return _catalog.get(text, text)


def mark(text: str) -> str:
    """Marca un texto para traducir sin traducirlo todavía (se traduce al mostrarlo).

    Sirve para textos que se guardan en datos o scripts antes de mostrarse, para que
    tools/extract_texts.py los encuentre.
    """
    return text
