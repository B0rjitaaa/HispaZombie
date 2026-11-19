# HispaZombie

RPG postapocalíptico de humor ambientado en Sevilla, al estilo de los RPG Maker 2000. Hecho en Python con pygame-ce, jugable en navegador y en escritorio.

* Diseño del juego (historia, mapa, mecánicas): [contexto_completo_gdd_rpg_sevilla_postapocal_ptica.md](contexto_completo_gdd_rpg_sevilla_postapocal_ptica.md)
* Plan técnico (herramientas, arquitectura, fases): [plan_tecnico.md](plan_tecnico.md)

## Requisitos

* [uv](https://docs.astral.sh/uv/): gestiona Python 3.12 y las dependencias.

```bash
uv sync
```

## Jugar

**Escritorio:**

```bash
uv run python hispazombie/main.py
```

**Navegador** (servidor local en http://localhost:8000):

```bash
uv run pygbag hispazombie
```

Controles: flechas o WASD para moverse. Z / Enter / Espacio para aceptar e interactuar. X / Esc para cancelar. F11 (o Alt+Enter) para pantalla completa en escritorio.

## Desarrollo

```bash
uv run pytest              # tests
uv run ruff check .        # errores y estilo
uv run ruff format .       # formatear el código
```

## Publicar

**Web (itch.io):** genera `hispazombie/build/web.zip`, que se sube a itch.io como proyecto HTML.

```bash
uv run pygbag --archive hispazombie
```

**Escritorio:** genera el ejecutable en `dist/`. Hay que ejecutarlo en cada sistema operativo (Windows, macOS, Linux).

```bash
uv run pyinstaller --noconfirm --windowed --name HispaZombie --paths hispazombie \
  --add-data "$(pwd)/hispazombie/assets:assets" \
  --distpath dist --workpath build/pyinstaller --specpath build hispazombie/main.py
```

## Convenciones

* **Código en inglés:** nombres de módulos, clases, funciones, variables, propiedades de Tiled y tipos de evento.
* **Comentarios y documentación en español.**
* **Textos del juego en español**, preparados para traducirse (ver *Traducciones*).

## Mapas y gráficos

Los mapas están en `hispazombie/assets/maps/` en formato **Tiled JSON (.tmj)** y se editan con [Tiled](https://www.mapeditor.org/). Al guardar, usa siempre el formato `.tmj` con las capas en CSV (la opción por defecto).

* Capas de tiles: `ground` y `objects` (debajo del personaje) y `above` (por encima).
* Capa de objetos `events`. Tipos (campo *Clase* del objeto): `spawn`, `door`, `sign`, `chest`, `blocker` y `auto`. Sus propiedades están documentadas en `hispazombie/scenes/map_scene.py`.
* Propiedades de tile: `solid` (no se atraviesa) y `bump_text` (texto al chocar).
* En los textos, una línea en blanco separa páginas y `@intern` al principio de una página muestra el retrato del protagonista.
* Los objetos que dan los cofres se definen en `hispazombie/assets/data/items.json`.

Los gráficos actuales son **provisionales** y están generados con código:

```bash
uv run python tools/generate_assets.py   # tileset, sprite y retrato
uv run python tools/generate_maps.py     # mapas iniciales (¡sobrescribe los .tmj!)
```

El pixel art se dibuja a **480×270** y se escala con un factor entero (×2, ×3, ×4…). Los textos se dibujan aparte, en alta resolución, con la fuente [Atkinson Hyperlegible](https://fonts.google.com/specimen/Atkinson+Hyperlegible) (licencia SIL OFL, `hispazombie/assets/fonts/OFL-AtkinsonHyperlegible.txt`). Ver `hispazombie/engine/hd_text.py`.

## Traducciones

Los textos se escriben en español directamente en los mapas, en `items.json` y en el código con `tr("...")`. Para traducir a otro idioma:

```bash
uv run python tools/extract_texts.py      # crea/actualiza hispazombie/assets/i18n/en.json
```

Se rellenan las traducciones en ese archivo y se cambia `LANGUAGE` en `hispazombie/config.py`. Los textos sin traducir se muestran en español.

## Estructura

```
hispazombie/        # Código del juego (esta carpeta es lo que empaqueta pygbag)
  main.py           # Punto de entrada (bucle async)
  config.py         # Resolución, tamaño de casilla, FPS, idioma
  state.py          # Estado de la partida: interruptores, inventario
  items.py          # Catálogo de objetos
  i18n.py           # Traducción de textos
  engine/           # Motor: bucle, pila de escenas, controles, recursos, texto
  world/            # Mapas de Tiled, cámara, movimiento en cuadrícula, personaje
  scenes/           # Escenas del juego (exploración de mapas)
  ui/               # Caja de mensajes
  assets/           # Mapas, tilesets, sprites, retratos, fuentes, datos, traducciones
tools/              # Scripts: assets provisionales, mapas iniciales, extracción de textos
tests/              # Tests con pytest
```
