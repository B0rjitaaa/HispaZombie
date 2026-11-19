"""Escena de exploración: un mapa de Tiled con el protagonista, eventos y cámara.

Tipos de evento soportados en la capa "eventos" de Tiled (campo Clase / Tipo del objeto):
  * inicio   -> posición inicial si se entra al mapa sin coordenadas. Props: direccion.
  * puerta   -> al pisarla, cambia de mapa. Props: mapa, destino_x, destino_y, direccion.
  * cartel   -> al pulsar Aceptar delante, muestra texto. Props: texto.
  * cofre    -> se abre una vez y da un objeto. Props: id, objeto, texto.
  * bloqueo  -> casilla infranqueable que muestra un texto al chocar. Props: texto.
  * auto     -> texto que se muestra una sola vez al entrar al mapa. Props: id, texto.

En la Fase 2 estos tipos se sustituirán por el intérprete de eventos genérico.
"""

from __future__ import annotations

import pygame

from config import ALTO, ANCHO
from engine import recursos
from engine.entrada import ACEPTAR, Entrada
from engine.escenas import Escena
from estado import estado
from mundo.camara import Camara
from mundo.mapa import CAPAS_ENCIMA, Evento, Mapa
from mundo.personaje import Personaje
from ui.caja_mensaje import EscenaMensaje

TIPOS_SOLIDOS = {"cartel", "cofre", "bloqueo"}
VELOCIDAD_FUNDIDO = 700  # unidades de alfa por segundo
DURACION_CARTEL_NOMBRE = 2.5


class EscenaMapa(Escena):
    def __init__(
        self,
        id_mapa: str,
        x: int | None = None,
        y: int | None = None,
        mirando: str | None = None,
    ) -> None:
        self.id_mapa = id_mapa
        self.mapa = Mapa(recursos.ruta("mapas", f"{id_mapa}.tmj"))
        self.tile = self.mapa.tile
        self.capa_debajo, self.capa_encima = self._prerenderizar()

        if x is None or y is None:
            inicio = next(iter(self.mapa.eventos_de_tipo("inicio")), None)
            x, y = (inicio.x, inicio.y) if inicio else (0, 0)
            mirando = mirando or (inicio.props.get("direccion") if inicio else None)

        hoja = recursos.imagen(recursos.ruta("sprites", "becario.png"))
        self.jugador = Personaje(hoja, x, y)
        self.jugador.mov.mirando = mirando or "abajo"
        self.camara = Camara(ANCHO, ALTO)

        self.fundido = 255.0  # empieza en negro y aparece poco a poco
        self.fundido_dir = -1
        self._puerta_pendiente: Evento | None = None
        self._ultimo_choque: tuple[int, int] | None = None
        self.tiempo = 0.0
        self.fuente = recursos.fuente(16)

    # --- Preparación ---

    def _prerenderizar(self) -> tuple[pygame.Surface, pygame.Surface]:
        """Dibuja una sola vez las capas de tiles en dos superficies grandes."""
        tam = (self.mapa.ancho * self.tile, self.mapa.alto * self.tile)
        debajo = pygame.Surface(tam, pygame.SRCALPHA)
        encima = pygame.Surface(tam, pygame.SRCALPHA)
        for capa in self.mapa.capas:
            if not capa.visible:
                continue
            destino = encima if capa.nombre in CAPAS_ENCIMA else debajo
            for i, gid in enumerate(capa.datos):
                if gid:
                    self._dibujar_tile(
                        destino,
                        gid,
                        (i % self.mapa.ancho) * self.tile,
                        (i // self.mapa.ancho) * self.tile,
                    )
        return debajo, encima

    def _dibujar_tile(self, destino: pygame.Surface, gid: int, x: int, y: int) -> None:
        ts = self.mapa.tileset_de(gid)
        if ts is None:
            return
        destino.blit(recursos.imagen(ts.imagen), (x, y), ts.rect_origen(gid))

    # --- Reglas del mundo ---

    def _clave_cofre(self, ev: Evento) -> str:
        return f"cofre:{self.id_mapa}:{ev.props.get('id', ev.id)}"

    def _evento_solido(self, ev: Evento) -> bool:
        if ev.tipo in TIPOS_SOLIDOS:
            return True
        return bool(ev.gid and self.mapa.props_tile(ev.gid).get("solido"))

    def transitable(self, x: int, y: int) -> bool:
        if self.mapa.tile_solido(x, y):
            return False
        return not any(self._evento_solido(e) for e in self.mapa.eventos_en(x, y))

    def mostrar(self, texto: str) -> None:
        if self.gestor and texto:
            self.gestor.apilar(EscenaMensaje(texto))

    # --- Bucle ---

    def actualizar(self, dt: float, entrada: Entrada) -> None:
        self.tiempo += dt

        if self.fundido_dir:
            self.fundido += self.fundido_dir * VELOCIDAD_FUNDIDO * dt
            if self.fundido <= 0:
                self.fundido, self.fundido_dir = 0.0, 0
            elif self.fundido >= 255:
                self.fundido = 255.0
                self._cambiar_de_mapa()
            return

        if self._lanzar_eventos_auto():
            return

        mov = self.jugador.mov
        if mov.actualizar(dt):
            self._ultimo_choque = None
            if self._al_pisar(mov.x, mov.y):
                return

        if mov.moviendose:
            return

        if ACEPTAR in entrada.pulsadas:
            self._interactuar(*mov.casilla_delante())
            return

        direccion = entrada.direccion()
        if direccion and not mov.intentar_mover(direccion, self.transitable):
            destino = mov.casilla_delante()
            if direccion in entrada.pulsadas or destino != self._ultimo_choque:
                self._ultimo_choque = destino
                self._al_chocar(*destino)

    def _lanzar_eventos_auto(self) -> bool:
        for ev in self.mapa.eventos_de_tipo("auto"):
            clave = f"auto:{self.id_mapa}:{ev.props.get('id', ev.id)}"
            if not estado.activo(clave):
                estado.activar(clave)
                self.mostrar(ev.props.get("texto", ""))
                return True
        return False

    def _al_pisar(self, x: int, y: int) -> bool:
        for ev in self.mapa.eventos_en(x, y):
            if ev.tipo == "puerta":
                self._puerta_pendiente = ev
                self.fundido_dir = 1
                return True
        return False

    def _al_chocar(self, x: int, y: int) -> None:
        for ev in self.mapa.eventos_en(x, y):
            if ev.tipo == "bloqueo":
                self.mostrar(ev.props.get("texto", ""))
                return
        texto = self.mapa.texto_choque(x, y)
        if texto:
            self.mostrar(texto)

    def _interactuar(self, x: int, y: int) -> None:
        for ev in self.mapa.eventos_en(x, y):
            if ev.tipo == "cartel":
                self.mostrar(ev.props.get("texto", ""))
                return
            if ev.tipo == "cofre":
                clave = self._clave_cofre(ev)
                if estado.activo(clave):
                    self.mostrar("Está vacío.")
                else:
                    estado.activar(clave)
                    if ev.props.get("objeto"):
                        estado.dar_objeto(ev.props["objeto"])
                    self.mostrar(ev.props.get("texto", "Está vacío."))
                return

    def _cambiar_de_mapa(self) -> None:
        ev = self._puerta_pendiente
        if ev is None or self.gestor is None:
            self.fundido_dir = -1
            return
        self.gestor.reemplazar(
            EscenaMapa(
                ev.props["mapa"],
                ev.props.get("destino_x"),
                ev.props.get("destino_y"),
                ev.props.get("direccion"),
            )
        )

    # --- Dibujo ---

    def dibujar(self, pantalla: pygame.Surface) -> None:
        ancho_px = self.mapa.ancho * self.tile
        alto_px = self.mapa.alto * self.tile
        self.camara.seguir(*self.jugador.centro_px(self.tile), ancho_px, alto_px)
        cx, cy = self.camara.x, self.camara.y

        pantalla.fill((0, 0, 0))
        pantalla.blit(self.capa_debajo, (-cx, -cy))

        # Eventos con gráfico y jugador, ordenados por fila para que se solapen bien.
        jy = self.jugador.mov.posicion_visual()[1]
        dibujables = [e for e in self.mapa.eventos if e.gid]
        for ev in sorted(dibujables, key=lambda e: e.y):
            if ev.y > jy:
                continue
            self._dibujar_evento(pantalla, ev, cx, cy)
        self.jugador.dibujar(pantalla, cx, cy, self.tile)
        for ev in sorted(dibujables, key=lambda e: e.y):
            if ev.y > jy:
                self._dibujar_evento(pantalla, ev, cx, cy)

        pantalla.blit(self.capa_encima, (-cx, -cy))
        self._dibujar_nombre_mapa(pantalla)

        if self.fundido > 0:
            velo = pygame.Surface((ANCHO, ALTO))
            velo.set_alpha(int(self.fundido))
            pantalla.blit(velo, (0, 0))

    def _dibujar_evento(self, pantalla: pygame.Surface, ev: Evento, cx: int, cy: int) -> None:
        gid = ev.gid
        if ev.tipo == "cofre" and estado.activo(self._clave_cofre(ev)):
            abierto = self.mapa.props_tile(gid).get("abierto_id")
            ts = self.mapa.tileset_de(gid)
            if abierto is not None and ts:
                gid = ts.firstgid + abierto
        self._dibujar_tile(pantalla, gid, ev.x * self.tile - cx, ev.y * self.tile - cy)

    def _dibujar_nombre_mapa(self, pantalla: pygame.Surface) -> None:
        if self.tiempo > DURACION_CARTEL_NOMBRE:
            return
        texto = self.fuente.render(self.mapa.nombre, False, (245, 240, 225))
        caja = texto.get_rect(topleft=(8, 8)).inflate(12, 6)
        fondo = pygame.Surface(caja.size, pygame.SRCALPHA)
        fondo.fill((20, 22, 40, 200))
        pantalla.blit(fondo, caja.topleft)
        pygame.draw.rect(pantalla, (230, 220, 190), caja, 1)
        pantalla.blit(texto, (caja.x + 6, caja.y + 3))
