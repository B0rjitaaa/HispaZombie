"""Comprueba que los mapas reales del juego se cargan y son coherentes."""

import os

import pytest

from engine import recursos
from mundo.mapa import Mapa

MAPAS = ["bunker", "afueras_cartuja"]


def cargar(nombre: str) -> Mapa:
    return Mapa(recursos.ruta("mapas", f"{nombre}.tmj"))


@pytest.mark.parametrize("nombre", MAPAS)
def test_carga_y_dimensiones(nombre):
    mapa = cargar(nombre)
    assert mapa.ancho > 0 and mapa.alto > 0
    assert mapa.tile == 16
    assert {c.nombre for c in mapa.capas} >= {"suelo", "objetos", "encima"}
    for ts in mapa.tilesets:
        assert os.path.exists(ts.imagen)


@pytest.mark.parametrize("nombre", MAPAS)
def test_puertas_llevan_a_casillas_libres(nombre):
    mapa = cargar(nombre)
    for puerta in mapa.eventos_de_tipo("puerta"):
        destino = cargar(puerta.props["mapa"])
        x, y = puerta.props["destino_x"], puerta.props["destino_y"]
        assert destino.dentro(x, y)
        assert not destino.tile_solido(x, y), f"{nombre} -> destino sólido en {x},{y}"
        # No se debe aparecer encima de otra puerta (provocaría un bucle de teletransportes).
        assert not [e for e in destino.eventos_en(x, y) if e.tipo == "puerta"]


def test_inicio_del_bunker_libre():
    mapa = cargar("bunker")
    (inicio,) = mapa.eventos_de_tipo("inicio")
    assert not mapa.tile_solido(inicio.x, inicio.y)


def test_tiles_solidos_y_texto_choque():
    mapa = cargar("afueras_cartuja")
    assert mapa.tile_solido(-1, 0)  # fuera del mapa
    # El centro del cráter es cristal radiactivo: sólido y con texto al chocar.
    assert mapa.tile_solido(36, 16)
    assert mapa.texto_choque(36, 16)


def test_objetos_tile_se_anclan_por_abajo():
    mapa = cargar("bunker")
    crisalida = [e for e in mapa.eventos if e.gid and e.tipo == "cartel"][0]
    # En el generador la crisálida está en la casilla (8, 6).
    assert (crisalida.x, crisalida.y) == (8, 6)
