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

## Mapas y gráficos

Los mapas están en `hispazombie/assets/mapas/` en formato **Tiled JSON (.tmj)** y se editan con [Tiled](https://www.mapeditor.org/). Al guardar, usa siempre el formato `.tmj` con las capas en CSV (la opción por defecto).

* Capas de tiles: `suelo` y `objetos` (debajo del personaje) y `encima` (por encima).
* Capa de objetos `eventos`. Tipos (campo *Clase* del objeto): `inicio`, `puerta`, `cartel`, `cofre`, `bloqueo` y `auto`. Sus propiedades están documentadas en `hispazombie/escenas/mapa_zona.py`.
* En los textos, una línea en blanco separa páginas y `@becario` al principio de una página muestra el retrato del protagonista.

Los gráficos actuales son **provisionales** y están generados con código:

```bash
uv run python tools/generar_assets.py   # tileset, sprite y retrato
uv run python tools/generar_mapas.py    # mapas iniciales (¡sobrescribe los .tmj!)
```

Fuente: [Jersey 10](https://fonts.google.com/specimen/Jersey+10), licencia SIL OFL (`hispazombie/assets/fuentes/OFL-Jersey10.txt`).

## Estructura

```
hispazombie/        # Código del juego (esta carpeta es lo que empaqueta pygbag)
  main.py           # Punto de entrada (bucle async)
  config.py         # Resolución, tamaño de casilla, FPS
  estado.py         # Estado de la partida: interruptores, inventario
  engine/           # Motor: bucle, pila de escenas, entrada, recursos, texto
  mundo/            # Mapas de Tiled, cámara, movimiento en cuadrícula, personaje
  escenas/          # Escenas del juego (exploración de mapas)
  ui/               # Caja de mensajes
  assets/           # Mapas, tilesets, sprites, retratos, fuentes
tools/              # Scripts que generan los assets provisionales
tests/              # Tests con pytest
```
