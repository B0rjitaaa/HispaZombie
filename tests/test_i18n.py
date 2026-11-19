import json

import i18n
import items
from engine import resources


def test_spanish_is_the_source_language(tmp_path):
    i18n.set_language("es", str(tmp_path))
    assert i18n.tr("Está vacío.") == "Está vacío."


def test_translation_and_fallback(tmp_path):
    catalog = {"Está vacío.": "It's empty.", "Sin traducir": ""}
    (tmp_path / "en.json").write_text(json.dumps(catalog), encoding="utf-8")
    i18n.set_language("en", str(tmp_path))
    try:
        assert i18n.tr("Está vacío.") == "It's empty."
        assert i18n.tr("Sin traducir") == "Sin traducir"  # traducción vacía -> español
        assert i18n.tr("Texto desconocido") == "Texto desconocido"
    finally:
        i18n.set_language("es", str(tmp_path))


def test_catalog_contains_every_game_text():
    """El catálogo en inglés debe estar al día: ejecuta tools/extract_texts.py si falla."""
    with open(resources.path("i18n", "en.json"), encoding="utf-8") as f:
        catalog = json.load(f)
    assert items.name("water_bottle") in catalog
    assert "Está vacío." in catalog
    assert "Obtienes: {item}." in catalog
    assert "Partida guardada." in catalog
    assert "No se ha podido guardar la partida." in catalog
