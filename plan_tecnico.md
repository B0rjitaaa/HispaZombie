# Plan Técnico: HispaZombie

**Propósito:** Definir las herramientas, la arquitectura y las fases de desarrollo del juego. El diseño (historia, mapa, mecánicas) está en `contexto_completo_gdd_rpg_sevilla_postapocal_ptica.md`.

---

## 1. Resumen

* **Tipo de juego:** RPG 2D cenital al estilo RPG Maker 2000: movimiento en cuadrícula, cajas de diálogo, eventos, combate por turnos.
* **Lenguaje:** Python 3.12.
* **Plataformas:** Web (navegador, publicado en itch.io) y escritorio (Windows, macOS, Linux).
* **Protagonista único:** no hay grupo, así que el combate es **1 contra N** (más sencillo de programar y equilibrar).

---

## 2. Herramientas

| Necesidad | Herramienta | Notas |
|---|---|---|
| Motor | **pygame-ce** | Fork activo de pygame |
| Versión web | **pygbag** | Compila a WebAssembly. `pygbag carpeta/` prueba en `localhost:8000` |
| Escritorio | **PyInstaller** | Hay que generar el ejecutable en cada sistema operativo |
| Editor de mapas | **Tiled** | Mapas `.tmj` (Tiled JSON), con capas de tiles y una capa de objetos para los eventos |
| Carga de mapas | Cargador propio (`mundo/mapa.py`) | Lee mapas Tiled JSON (`.tmj`) con la biblioteca estándar: sin dependencias y seguro en web |
| Pixel art | **Aseprite** (de pago) o **Pixelorama** (gratis) | |
| Assets provisionales | Packs CC0 de 16×16 (Kenney *Tiny Town*, *Tiny Dungeon*…) | Hasta tener arte propio |
| Fuente | **Atkinson Hyperlegible** (Google Fonts) | Licencia SIL OFL. Se dibuja en HD, por encima del pixel art |
| Música | **BeepBox** o **FamiStudio** | Exportar a `.ogg` |
| Efectos de sonido | **jsfxr** | Exportar a `.ogg` |
| Datos del juego | **JSON** | Biblioteca estándar de Python: funciona seguro en web |
| Entorno y dependencias | **uv** | Instala Python 3.12 y las dependencias (`uv sync`) |
| Control de versiones | **git** + GitHub | Repositorio: https://github.com/B0rjitaaa/HispaZombie |
| Calidad | **pytest** (tests), **ruff** (estilo y errores) | |
| Editor | VS Code + extensión de Python | |

**Restricciones de la versión web (pygbag), a respetar desde el principio:**
* El bucle principal es `async` y cede el control en cada frame con `await asyncio.sleep(0)`.
* Nada de hilos ni librerías con código en C que no estén soportadas: Python puro + pygame-ce.
* Audio en `.ogg`. Assets ligeros (se descargan en el navegador).
* Las partidas guardadas van en el `localStorage` del navegador; en escritorio, en un archivo. Se accede a través de una capa común (`engine/guardado.py`).

**Copyright:** los gráficos y la música de RPG Maker (RTP) solo se pueden usar dentro de RPG Maker. Aquí todo debe ser propio o con licencia libre.

---

## 3. Especificación técnica "estilo RPG Maker 2000"

* **Resolución interna:** 480×270 px (16:9), escalada con un factor entero sin suavizado: ×2 = 960×540, ×3 = 1440×810, ×4 = 1920×1080.
* **Tiles:** 16×16 px → la pantalla muestra 30×17 tiles.
* **Sprites de personaje:** hojas de 3 frames × 4 direcciones (abajo, izquierda, derecha, arriba).
* **Movimiento:** en cuadrícula, casilla a casilla, con interpolación suave entre casillas.
* **Texto:** caja de mensajes con retrato, texto letra a letra, opciones de respuesta. El texto se dibuja en alta resolución (no en pixel art) para que se lea bien.
* **Controles:** flechas/WASD para mover, Z/Enter para aceptar, X/Esc para cancelar o abrir menú. Soporte de mando más adelante.

---

## 4. Arquitectura

```
hispazombie/
  main.py                  # Punto de entrada: bucle async (compatible con pygbag)
  config.py                # Resolución, casilla, FPS, idioma
  state.py                 # Interruptores, variables e inventario de la partida
  items.py                 # Catálogo de objetos (assets/data/items.json)
  i18n.py                  # Traducción de textos: tr("texto en español")
  engine/                  # Motor genérico, sin nada específico del juego
    game.py                # Bucle principal, pantalla virtual y escalado entero
    scenes.py              # Pila de escenas (push / pop / replace)
    controls.py            # Teclado y mando -> acciones (confirm, cancel, up...)
    resources.py           # Carga y caché de imágenes y fuentes
    text.py                # Ajuste de líneas y páginas de diálogo
    audio.py               # (Fase 4) Música y efectos
    storage.py             # Almacenamiento: archivo (escritorio) o localStorage (web)
    hd_text.py             # Texto en alta resolución por encima del pixel art
  world/
    tiled_map.py           # Carga de .tmj, capas, colisiones por tile
    camera.py
    movement.py            # Movimiento en cuadrícula
    character.py           # Personaje con sprite animado
  saves.py                 # Guardar y cargar la partida
  events/
    interpreter.py         # Intérprete de scripts de eventos (comandos y condiciones)
  battle/                  # (Fase 3) Combate por turnos 1 contra N
  ui/
    message_box.py  choice_box.py  pause_menu.py  widgets.py   # (Fase 4) tienda
  scenes/
    map_scene.py  title_scene.py   # (más adelante) mapa del mundo, combate
  settlement/              # (Fase 6) Ciudad del Alamillo
  assets/
    maps/  events/  tilesets/  sprites/  portraits/  fonts/  data/  i18n/  music/  sfx/
tests/
tools/                     # Generadores de assets provisionales y extractor de textos
```

**Idiomas del proyecto:** el código (identificadores, propiedades de Tiled, tipos de evento) va en inglés; los comentarios y la documentación, en español; los textos del juego, en español con catálogos de traducción en `assets/i18n/`.

### Principios

1. **El contenido va en datos, no en código.** Diálogos, objetos, enemigos y eventos se definen en JSON y Tiled. Añadir un NPC no debe requerir tocar Python.
2. **Sistema de eventos como en RPG Maker.** Cada NPC, cofre o puerta tiene una lista de comandos que interpreta el motor. Ejemplo:

```json
[
  {"cmd": "text", "portrait": "scrapper", "text": "¿Agua fresquita, quillo? Solo 5 fichas."},
  {"cmd": "choice", "options": {
    "Comprar": [
      {"cmd": "if", "cond": {"coins_min": 5},
       "then": [{"cmd": "remove_coins", "amount": 5}, {"cmd": "give_item", "id": "water_bottle"}],
       "else": [{"cmd": "text", "text": "Sin fichas no hay agua, miarma."}]}
    ],
    "Pasar": []
  }},
  {"cmd": "switch_on", "id": "talked_to_scrapper"}
]
```

3. **Interruptores y variables** guardan todo el progreso: misiones, NPC reclutados, zonas desbloqueadas (Alamillo, ruta sur, Torre del Oro, Torre Pelli…).
4. **Pila de escenas:** el mapa queda debajo cuando se abre un diálogo, el menú o un combate, y se recupera al cerrarlo.
5. **La lógica no depende del dibujo:** combate, inventario, eventos y asentamiento se pueden probar con `pytest` sin abrir una ventana.

### Mapa del mundo

El mapa general es un **grafo de zonas** (sección 2.1 del GDD). Se presenta como una **pantalla de viaje sobre el mapa de pergamino**: el jugador elige una zona conectada y viaja. Dentro de cada zona, la exploración es con tiles. Las conexiones bloqueadas (Alamillo, ruta sur…) dependen de interruptores.

---

## 5. Fases de desarrollo

Las duraciones son orientativas para una persona a tiempo parcial.

### Fase 0: preparación y publicación (1 semana) ✅ completada
* Repositorio git, entorno virtual, pygame-ce, ruff y pytest.
* Ventana escalada con bucle async.
* Probar en el navegador con pygbag y subir una prueba privada a itch.io.
* Generar un ejecutable de escritorio con PyInstaller.
* **Hito:** el proceso de publicación funciona en web y escritorio antes de crear contenido.

### Fase 1: exploración, el búnker y las afueras de la Cartuja (3-4 semanas) ✅ completada (con gráficos provisionales)
* Carga de mapas de Tiled, colisiones, cámara.
* Movimiento en cuadrícula con animación en 4 direcciones.
* Cambio de mapa por puertas (búnker → afueras).
* Caja de mensajes con retrato y texto letra a letra.
* Cofres y carteles con texto (los documentos de la quinta bomba de Palomares).
* **Hito:** el protagonista despierta, sale del búnker y explora las afueras leyendo pistas.

### Fase 2: eventos, inventario y guardado (2-3 semanas) ✅ completada
* Intérprete de eventos con los comandos básicos (texto, elegir, si, interruptores, variables, dar/quitar objeto, teletransportar, mover NPC).
* Inventario y fichas de cerámica (dinero).
* Guardar y cargar (archivo y localStorage).
* **Hito:** NPC con diálogos ramificados que recuerdan lo que has hecho, y partida guardada.

### Fase 3: combate (3-4 semanas)
* Combate por turnos 1 contra N, vista frontal: Atacar, Habilidad, Objeto, Huir.
* Encuentros aleatorios por zona y combates fijos (jefes).
* Experiencia, niveles, estados alterados.
* Habilidades mutantes del protagonista (cuando se definan en el GDD).
* **Hito:** combatir contra mutantes en las afueras de la Cartuja.

### Fase 4: menús, tiendas y mapa del mundo (2-3 semanas)
* Pantalla de título, menú de pausa (Objetos, Habilidades, Equipo, Estado, Guardar).
* Tiendas y posadas.
* Mapa del mundo sobre el pergamino con zonas bloqueables.
* **Hito:** viajar entre la Cartuja y Triana, comprar y descansar.

### Fase 5: primera demo pública (4-6 semanas)
* Cartuja (tutorial) + Triana (campamento provisional) + Los Remedios + Río / Torre del Oro (primer jefe).
* Música y efectos básicos.
* Publicar en itch.io y recoger opiniones.
* **Hito:** demo de 30-60 minutos jugable en el navegador.

### Fase 6: el resto del juego
* Mecánica de asentamiento (campamento provisional → prototipo de descontaminador a mitad de partida → Parque del Alamillo).
* Una zona por iteración: Río/Arenal, Casco Antiguo, Plaza de España, Heliópolis, Nervión, Macarena, Zona Noble.
* Tramo final: rescate del científico en la Zona Noble → Torre Pelli (combate final sorpresa contra el jefe de la Torre del Oro y bomba descontaminadora).

### Fase 7: pulido y lanzamiento
* Equilibrado, accesibilidad, rendimiento en web.
* Ejecutables de escritorio para Windows, macOS y Linux (se puede automatizar con GitHub Actions).
* Página de itch.io definitiva.

---

## 6. Decisiones de diseño que bloquean fases

| Decisión pendiente (ver GDD) | Bloquea |
|---|---|
| Mecanismo concreto que bloquea la ruta sur | Fase 6 |
| Efectos de la mutación del protagonista | Fase 3 (habilidades) |
| Nombre y aspecto del protagonista | Fase 1 (sprites y retrato; se pueden usar provisionales) |
