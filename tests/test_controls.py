import pygame

from engine.controls import CONFIRM, DOWN, RIGHT, UP, Controls, action_for_key
from engine.game import integer_scale


def test_keys_to_actions():
    assert action_for_key(pygame.K_UP) == UP
    assert action_for_key(pygame.K_w) == UP
    assert action_for_key(pygame.K_z) == CONFIRM
    assert action_for_key(pygame.K_q) is None


def test_pressed_only_on_first_frame():
    controls = Controls()
    controls.new_frame()
    controls.press(CONFIRM)
    assert CONFIRM in controls.pressed
    assert CONFIRM in controls.held

    controls.new_frame()
    assert CONFIRM not in controls.pressed
    assert CONFIRM in controls.held


def test_last_direction_wins():
    controls = Controls()
    controls.press(UP)
    controls.press(RIGHT)
    assert controls.direction() == RIGHT

    controls.release(RIGHT)
    assert controls.direction() == UP

    controls.release(UP)
    assert controls.direction() is None


def test_release_all():
    controls = Controls()
    controls.press(DOWN)
    controls.release_all()
    assert controls.direction() is None
    assert not controls.held


def test_window_integer_scale():
    assert integer_scale(320, 240, (1920, 1080)) == 4
    assert integer_scale(320, 240, (1440, 900)) == 3
    assert integer_scale(320, 240, (200, 100)) == 1  # nunca menos de 1
    assert integer_scale(480, 270, (1632, 918)) == 3  # 1920x1080 al 85 %
