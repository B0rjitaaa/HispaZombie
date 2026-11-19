from mundo.movimiento import MovimientoCuadricula


def siempre(_x: int, _y: int) -> bool:
    return True


def nunca(_x: int, _y: int) -> bool:
    return False


def test_paso_completo():
    mov = MovimientoCuadricula(5, 5, velocidad=4.0)
    assert mov.intentar_mover("derecha", siempre)
    assert mov.moviendose

    mov.actualizar(0.125)  # medio paso a 4 casillas/s
    assert mov.posicion_visual() == (5.5, 5.0)
    assert (mov.x, mov.y) == (5, 5)

    mov.actualizar(0.125)
    assert not mov.moviendose
    assert (mov.x, mov.y) == (6, 5)


def test_no_atraviesa_muros_pero_se_gira():
    mov = MovimientoCuadricula(1, 1)
    assert not mov.intentar_mover("arriba", nunca)
    assert mov.mirando == "arriba"
    assert (mov.x, mov.y) == (1, 1)
    assert not mov.moviendose


def test_no_empieza_otro_paso_a_mitad():
    mov = MovimientoCuadricula(0, 0)
    mov.intentar_mover("abajo", siempre)
    assert not mov.intentar_mover("derecha", siempre)
    assert mov.mirando == "abajo"
