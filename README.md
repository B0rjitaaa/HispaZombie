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

Controles: flechas o WASD para moverse. Z / Enter / Espacio para aceptar. X / Esc para cancelar.

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
  --distpath dist --workpath build/pyinstaller --specpath build hispazombie/main.py
```

## Estructura

```
hispazombie/        # Código del juego (esta carpeta es lo que empaqueta pygbag)
  main.py           # Punto de entrada (bucle async)
  config.py         # Resolución, tamaño de casilla, FPS
  engine/           # Motor: bucle, pila de escenas, entrada
  mundo/            # Movimiento en cuadrícula (y más adelante mapas y entidades)
  escenas/          # Escenas del juego
  assets/           # Gráficos, sonido, mapas
tests/              # Tests con pytest
```
