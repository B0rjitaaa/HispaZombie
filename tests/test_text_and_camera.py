from engine.text import pages_from, wrap
from world.camera import Camera


class FakeFont:
    """Cada letra mide 1 píxel: facilita comprobar el ajuste de líneas."""

    def size(self, text: str) -> tuple[int, int]:
        return len(text), 10


def test_wrap_by_words():
    assert wrap("hola que tal estas", FakeFont(), 9) == ["hola que", "tal estas"]


def test_wrap_keeps_line_breaks():
    assert wrap("uno\ndos", FakeFont(), 100) == ["uno", "dos"]


def test_pages_with_portrait():
    pages = pages_from("Texto normal.\n\n@intern\n¿Qué hora es?")
    assert len(pages) == 2
    assert pages[0].portrait is None
    assert pages[1].portrait == "intern"
    assert pages[1].text == "¿Qué hora es?"


def test_camera_clamped_to_edges():
    cam = Camera(320, 240)
    cam.follow(0, 0, 640, 480)
    assert (cam.x, cam.y) == (0, 0)
    cam.follow(640, 480, 640, 480)
    assert (cam.x, cam.y) == (320, 240)
    cam.follow(320, 240, 640, 480)
    assert (cam.x, cam.y) == (160, 120)


def test_camera_centers_small_maps():
    cam = Camera(320, 240)
    cam.follow(50, 50, 160, 120)
    assert (cam.x, cam.y) == (-80, -60)


def test_hd_text_measures_in_virtual_pixels_and_renders():
    import pygame

    from engine import hd_text

    pygame.init()
    window = pygame.display.set_mode((960, 540))
    font = hd_text.HDFont(12)
    w, h = font.size("Hola")
    assert 10 < w < 60 and 8 < h < 30  # medidas en píxeles virtuales, no de ventana

    layer = hd_text.TextLayer()
    layer.draw("Hola", 10, 10, 12)
    layer.draw("invisible", 10, 30, 12, alpha=0)  # alfa 0: no se encola
    assert len(layer._items) == 1
    layer.render(window, (0, 0), 2)
    assert not layer._items  # la cola se vacía tras dibujar
