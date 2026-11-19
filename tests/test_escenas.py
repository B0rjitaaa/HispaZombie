from engine.escenas import Escena, GestorEscenas


class EscenaRegistro(Escena):
    def __init__(self, nombre: str, registro: list[str]) -> None:
        self.nombre = nombre
        self.registro = registro

    def al_entrar(self) -> None:
        self.registro.append(f"entra {self.nombre}")

    def al_salir(self) -> None:
        self.registro.append(f"sale {self.nombre}")


def test_apilar_y_desapilar():
    registro: list[str] = []
    gestor = GestorEscenas()
    mapa = EscenaRegistro("mapa", registro)
    dialogo = EscenaRegistro("dialogo", registro)

    gestor.apilar(mapa)
    gestor.apilar(dialogo)
    assert gestor.actual is dialogo
    assert len(gestor) == 2
    assert dialogo.gestor is gestor

    assert gestor.desapilar() is dialogo
    assert gestor.actual is mapa
    assert dialogo.gestor is None
    assert registro == ["entra mapa", "entra dialogo", "sale dialogo"]


def test_reemplazar():
    registro: list[str] = []
    gestor = GestorEscenas()
    gestor.apilar(EscenaRegistro("titulo", registro))
    gestor.reemplazar(EscenaRegistro("mapa", registro))
    assert len(gestor) == 1
    assert registro == ["entra titulo", "sale titulo", "entra mapa"]


def test_desapilar_vacia():
    gestor = GestorEscenas()
    assert gestor.desapilar() is None
    assert gestor.vacia
    assert gestor.actual is None
