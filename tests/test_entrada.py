import pygame

from engine.entrada import ABAJO, ACEPTAR, ARRIBA, DERECHA, Entrada, accion_de_tecla


def test_teclas_a_acciones():
    assert accion_de_tecla(pygame.K_UP) == ARRIBA
    assert accion_de_tecla(pygame.K_w) == ARRIBA
    assert accion_de_tecla(pygame.K_z) == ACEPTAR
    assert accion_de_tecla(pygame.K_q) is None


def test_pulsada_solo_el_primer_frame():
    entrada = Entrada()
    entrada.nuevo_frame()
    entrada.pulsar(ACEPTAR)
    assert ACEPTAR in entrada.pulsadas
    assert ACEPTAR in entrada.mantenidas

    entrada.nuevo_frame()
    assert ACEPTAR not in entrada.pulsadas
    assert ACEPTAR in entrada.mantenidas


def test_manda_la_ultima_direccion():
    entrada = Entrada()
    entrada.pulsar(ARRIBA)
    entrada.pulsar(DERECHA)
    assert entrada.direccion() == DERECHA

    entrada.soltar(DERECHA)
    assert entrada.direccion() == ARRIBA

    entrada.soltar(ARRIBA)
    assert entrada.direccion() is None


def test_soltar_todo():
    entrada = Entrada()
    entrada.pulsar(ABAJO)
    entrada.soltar_todo()
    assert entrada.direccion() is None
    assert not entrada.mantenidas
