from world.movement import GridMovement


def always(_x: int, _y: int) -> bool:
    return True


def never(_x: int, _y: int) -> bool:
    return False


def test_full_step():
    movement = GridMovement(5, 5, speed=4.0)
    assert movement.try_move("right", always)
    assert movement.moving

    assert not movement.update(0.125)  # medio paso a 4 casillas/s
    assert movement.visual_position() == (5.5, 5.0)
    assert (movement.x, movement.y) == (5, 5)

    assert movement.update(0.125)  # llega a la casilla
    assert not movement.moving
    assert (movement.x, movement.y) == (6, 5)
    assert movement.steps == 1


def test_walls_block_but_character_turns():
    movement = GridMovement(1, 1)
    assert not movement.try_move("up", never)
    assert movement.facing == "up"
    assert (movement.x, movement.y) == (1, 1)
    assert not movement.moving


def test_no_new_step_while_moving():
    movement = GridMovement(0, 0)
    movement.try_move("down", always)
    assert not movement.try_move("right", always)
    assert movement.facing == "down"


def test_place_and_tile_ahead():
    movement = GridMovement(0, 0)
    movement.place(3, 4, "left")
    assert movement.tile_ahead() == (2, 4)
