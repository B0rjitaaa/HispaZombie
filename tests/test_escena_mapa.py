"""Pruebas de la escena de exploración, con una ventana invisible."""

import pygame
import pytest

from engine.entrada import ACEPTAR, Entrada
from engine.escenas import GestorEscenas
from escenas.mapa_zona import EscenaMapa
from estado import estado
from ui.caja_mensaje import EscenaMensaje

DT = 1 / 60


@pytest.fixture(autouse=True)
def ventana():
    pygame.init()
    pygame.display.set_mode((320, 240))
    estado.__init__()  # partida limpia en cada test
    # No se llama a pygame.quit(): invalidaría las fuentes guardadas en caché.


def preparar(id_mapa, x=None, y=None, mirando=None):
    gestor = GestorEscenas()
    escena = EscenaMapa(id_mapa, x, y, mirando)
    escena.fundido, escena.fundido_dir = 0.0, 0  # sin fundido de entrada
    # Se dan por vistos los textos de introducción para que no interrumpan las pruebas.
    estado.activar("auto:bunker:intro_despertar")
    estado.activar("auto:afueras_cartuja:afueras_llegada")
    gestor.apilar(escena)
    return gestor, escena


def pulsar(gestor, accion, frames=1):
    entrada = Entrada()
    entrada.pulsar(accion)
    for _ in range(frames):
        gestor.actual.actualizar(DT, entrada)
        entrada.nuevo_frame()


def test_abrir_cofre_da_objeto_una_sola_vez():
    # Cofre del periódico en (4, 8); nos ponemos debajo mirando hacia arriba.
    gestor, escena = preparar("afueras_cartuja", 4, 9, "arriba")
    pulsar(gestor, ACEPTAR)
    assert isinstance(gestor.actual, EscenaMensaje)
    assert estado.inventario == ["Recorte de periódico (1966)"]

    gestor.desapilar()
    pulsar(gestor, ACEPTAR)
    assert estado.inventario == ["Recorte de periódico (1966)"]  # ya estaba vacío


def test_chocar_con_bloqueo_muestra_texto():
    # Salida sur hacia Triana: bloqueos en (17, 28) y (18, 28).
    gestor, escena = preparar("afueras_cartuja", 17, 27, "abajo")
    pulsar(gestor, "abajo")
    assert isinstance(gestor.actual, EscenaMensaje)
    assert (escena.jugador.mov.x, escena.jugador.mov.y) == (17, 27)


def test_chocar_con_crater_muestra_texto_del_tile():
    # El borde del cráter empieza a 8 casillas del centro (36, 16).
    gestor, escena = preparar("afueras_cartuja", 27, 16, "derecha")
    pulsar(gestor, "derecha")
    assert isinstance(gestor.actual, EscenaMensaje)


def test_puerta_cambia_de_mapa():
    # Escaleras del búnker en (9, 2): desde (9, 3) se sube.
    gestor, escena = preparar("bunker", 9, 3, "arriba")
    pulsar(gestor, "arriba", frames=20)  # paso completo: se pisa la puerta
    assert escena.fundido_dir == 1
    for _ in range(60):
        gestor.actual.actualizar(DT, Entrada())
    nueva = gestor.actual
    assert isinstance(nueva, EscenaMapa)
    assert nueva.id_mapa == "afueras_cartuja"
    assert (nueva.jugador.mov.x, nueva.jugador.mov.y) == (6, 22)
