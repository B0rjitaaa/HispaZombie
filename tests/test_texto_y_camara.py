from engine.texto import envolver, paginas_de
from mundo.camara import Camara


class FuenteFalsa:
    """Cada letra mide 1 píxel: facilita comprobar el ajuste de líneas."""

    def size(self, texto: str) -> tuple[int, int]:
        return len(texto), 10


def test_envolver_por_palabras():
    assert envolver("hola que tal estas", FuenteFalsa(), 9) == ["hola que", "tal estas"]


def test_envolver_respeta_saltos():
    assert envolver("uno\ndos", FuenteFalsa(), 100) == ["uno", "dos"]


def test_paginas_con_retrato():
    paginas = paginas_de("Texto normal.\n\n@becario\n¿Qué hora es?")
    assert len(paginas) == 2
    assert paginas[0].retrato is None
    assert paginas[1].retrato == "becario"
    assert paginas[1].texto == "¿Qué hora es?"


def test_camara_limitada_a_los_bordes():
    cam = Camara(320, 240)
    cam.seguir(0, 0, 640, 480)
    assert (cam.x, cam.y) == (0, 0)
    cam.seguir(640, 480, 640, 480)
    assert (cam.x, cam.y) == (320, 240)
    cam.seguir(320, 240, 640, 480)
    assert (cam.x, cam.y) == (160, 120)


def test_camara_centra_mapas_pequenos():
    cam = Camara(320, 240)
    cam.seguir(50, 50, 160, 120)
    assert (cam.x, cam.y) == (-80, -60)
