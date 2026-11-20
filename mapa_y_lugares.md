# HispaZombie: mapa, lugares y conexiones

**Para quién es este documento:** un asistente de IA (Gemini u otro) que vaya a diseñar o programar contenido del mapa de HispaZombie. Explica qué lugares existen, cómo se conectan, qué bloquea cada paso, en qué orden se recorren y cómo se representa todo en el motor del juego.

**Fuentes:** resume y concreta `contexto_completo_gdd_rpg_sevilla_postapocal_ptica.md` (el GDD), `plan_tecnico.md` y el código del repositorio. Si este documento y el GDD no coinciden, manda el GDD.

**Cómo leer las etiquetas:**
- **[DECIDIDO]**: lo ha decidido el autor del juego. No cambiarlo sin preguntarle.
- **[PROPUESTO]**: sugerencia razonable, todavía sin confirmar. Se puede usar, pero indicando que es provisional.
- **[PENDIENTE]**: no está decidido. No inventarlo como si fuera un hecho: preguntar o proponerlo como opción.

---

## 1. Contexto mínimo del juego

- **Género:** RPG 2D cenital al estilo RPG Maker 2000, con combate por turnos uno contra uno. **[DECIDIDO]**
- **Tono:** humor, ironía y sarcasmo; divertido y sencillo. Sevilla postapocalíptica. **[DECIDIDO]**
- **Premisa:** las obras eternas de la Línea 3 del Metro desentierran bajo la Cartuja la "quinta bomba de Palomares", que explota. El protagonista, un becario que había caído en un refugio de la Guerra Civil, muta, hiberna 20-25 años y despierta en un mundo arrasado. **[DECIDIDO]**
- **Objetivo:** fundar una ciudad con personas limpias (no contaminadas) en el **Parque del Alamillo**. Para limpiar Sevilla hay que encontrar a un científico, fabricar una bomba descontaminadora y activarla en lo alto de la **Torre Pelli**. **[DECIDIDO]**
- **El protagonista viaja solo**, sin grupo. **[DECIDIDO]**

---

## 2. Los lugares del mapa general

El mundo es un **grafo de zonas**. Cada zona es uno o varios mapas de tiles. Hay 11 zonas en el juego base y 1 de ampliación.

| ID propuesto | Zona | Papel en el juego | Estado |
|---|---|---|---|
| `cartuja` | **Cartuja** (Zona Cero) | Inicio (búnker y afueras: tutorial) y final (Torre Pelli) | **Implementada en parte** |
| `alamillo_park` | **Parque del Alamillo** | La ciudad del jugador (asentamiento) | Diseñada |
| `triana` | **Triana** | Barrio subterráneo; campamento provisional de supervivientes | Diseñada |
| `los_remedios` | **Los Remedios** | Zona intermedia temprana | Solo nombre |
| `river` | **Río / Torre del Oro / Arenal** | Primer jefe obligatorio (jefe de la Torre del Oro) | Diseñada |
| `old_town` | **Casco Antiguo** | Contiene la Giralda, el Alcázar y las Setas | Diseñada |
| `macarena` | **Macarena** | Nudo de conexiones del norte y el este | Solo nombre |
| `noble_zone` | **Zona Noble** (nombre provisional: Santa Justa) | Callejón sin salida: rescate del científico | Diseñada |
| `nervion` | **Nervión** | Zona intermedia del este | Solo nombre |
| `plaza_de_espana` | **Plaza de España** | Arena neutral de combates y comercio | Diseñada |
| `heliopolis` | **Heliópolis** | Zona del sur | Solo nombre |
| `los_pueblos` | **Los Pueblos** | Ampliación futura, fuera del juego base | **[PENDIENTE]** |

Los **ID** siguen la convención del código (en inglés, `snake_case`) y son **[PROPUESTO]**: todavía no existen en el código, salvo los mapas de la Cartuja (ver sección 6).

### 2.1. Detalle de cada lugar

**Cartuja (Zona Cero)** **[DECIDIDO]**
- **Partes:**
  1. **Búnker:** el refugio antiaéreo número 7, donde despierta el protagonista.
  2. **Afueras:** la zona tutorial, con la obra de la Línea 3, ruinas y cofres con pistas sobre la bomba.
  3. **Cráter:** de cristal radiactivo, infranqueable.
  4. **Torre Pelli:** la zona final, cerrada hasta el final del juego.
- **Lugar seguro inicial:** la crisálida del búnker (descansar allí recupera todo y fija el punto donde se despierta tras perder un combate).
- **NPC:** Manolo el Chatarrero (vende agua y enseña técnicas callejeras).
- **Jefe opcional:** la Rata del Metro.

**Parque del Alamillo** **[DECIDIDO]**
- Solo conecta con la Cartuja.
- **Bloqueado por radiación** al principio.
- Se abre **a mitad de partida**: otro NPC (propuesta: un chatarrero de Triana, con instrucciones del científico) fabrica un *prototipo de descontaminador* que limpia solo el parque.
- Desde entonces es la ciudad del jugador: los supervivientes del campamento provisional se mudan aquí y cada NPC reclutado abre un servicio (tienda, herrero, posada…). Se puede cultivar.

**Triana** **[DECIDIDO]**
- Aislada por el río tóxico. La gente vive bajo tierra: bodegas, alfares, criptas y alcantarillas.
- Mercado negro. Aquí está el **campamento provisional** donde esperan los supervivientes hasta que se abre el Alamillo.
- Facción asociada (en pausa): la Resistencia de Triana.

**Río / Torre del Oro / Arenal** **[DECIDIDO]**
- El Guadalquivir es una ciénaga ácida. Los puentes están semidestruidos: se cruzan por pasarelas de chatarra, tirolinas o barcazas.
- La Torre del Oro es una aduana fortificada. Facción asociada (en pausa): los Hidro-Monjes.
- **Jefe de la Torre del Oro:** primer jefe obligatorio. Se le derrota sin más, pero vuelve **por sorpresa como jefe final** en lo alto de la Torre Pelli. Mientras tanto tiene secuestrado al científico.
- **[PENDIENTE]** Si la zona del río y el Arenal se puede recorrer antes de luchar contra el jefe (propuesta: sí, con la fortaleza cerrada hasta que toque).

**Casco Antiguo** **[DECIDIDO]**
- Contiene tres ubicaciones internas:
  - **Giralda de Hierro:** la Catedral fortificada. Facción asociada (en pausa): la Orden de la Giralda.
  - **Laberinto Verde:** el Alcázar, convertido en jungla bioluminiscente y tóxica. Zona de sigilo y exploración.
  - **La Anomalía:** las Setas (Metropol Parasol), asentamiento elevado con pasarelas.

**Plaza de España** **[DECIDIDO]**
- Campamento nómada neutral y arena de combates clandestinos (el "Coliseo de las Cenizas").

**Zona Noble** (provisional: Santa Justa) **[DECIDIDO]**
- Callejón sin salida: solo conecta con Macarena.
- Allí se **rescata al científico**, custodiado por los secuaces del jefe de la Torre del Oro.

**Los Remedios, Macarena, Nervión, Heliópolis**
- **[PENDIENTE]** Contenido, misiones y enemigos.

**Los Pueblos** **[PENDIENTE]**
- Ampliación futura, fuera del juego base.

---

## 3. Conexiones entre lugares

**Todas las conexiones son bidireccionales.** **[DECIDIDO]**

```
Parque del Alamillo ── Cartuja              (bloqueada por radiación al inicio)
Cartuja ──────────── Río / Torre del Oro / Arenal
Cartuja ──────────── Macarena
Triana ───────────── Río / Torre del Oro / Arenal
Triana ───────────── Los Remedios
Triana ───────────── Heliópolis
Los Remedios ─────── Heliópolis
Río ──────────────── Casco Antiguo
Río ──────────────── Plaza de España
Plaza de España ──── Heliópolis
Plaza de España ──── Nervión
Casco Antiguo ────── Macarena
Casco Antiguo ────── Nervión
Macarena ─────────── Nervión
Macarena ─────────── Zona Noble
[Ampliación] Los Pueblos ── Cartuja
[Ampliación] Los Pueblos ── Triana
```

**Lista de vecinos por zona** (útil para comprobar caminos):

| Zona | Vecinos |
|---|---|
| Cartuja | Alamillo, Río, Macarena, (Los Pueblos) |
| Parque del Alamillo | Cartuja |
| Triana | Río, Los Remedios, Heliópolis, (Los Pueblos) |
| Los Remedios | Triana, Heliópolis |
| Río / Torre del Oro / Arenal | Cartuja, Triana, Casco Antiguo, Plaza de España |
| Casco Antiguo | Río, Macarena, Nervión |
| Macarena | Cartuja, Casco Antiguo, Nervión, Zona Noble |
| Zona Noble | Macarena |
| Nervión | Plaza de España, Casco Antiguo, Macarena |
| Plaza de España | Río, Heliópolis, Nervión |
| Heliópolis | Plaza de España, Los Remedios, Triana |

**Callejones sin salida:** Parque del Alamillo (solo Cartuja) y Zona Noble (solo Macarena).

---

## 4. Restricciones y bloqueos

| Paso o lugar | Bloqueo | Cuándo se abre | Estado |
|---|---|---|---|
| Cartuja ↔ Alamillo | Radiación | A mitad de partida, con el prototipo de descontaminador | **[DECIDIDO]** |
| Torre Pelli (dentro de la Cartuja) | Cerrada (escombros y radiación) | Al final del juego, con la bomba descontaminadora | **[DECIDIDO]** |
| Cráter (dentro de la Cartuja) | Infranqueable (cristal radiactivo) | Nunca: es decorado | Implementado |
| **Ruta sur:** Triana / Los Remedios → Heliópolis → Plaza de España → Nervión | Bloqueada al principio para que no se pueda evitar la Torre del Oro | Tras el **primer combate** contra el jefe de la Torre del Oro | **[DECIDIDO]**. El mecanismo concreto (puente caído, zona infestada, peaje…) está **[PENDIENTE]** |
| Fortaleza de la Torre del Oro | Cerrada hasta el combate contra el primer jefe | Al llegar ese punto de la historia | **[PROPUESTO]** |
| Cartuja ↔ Macarena | **Sin definir.** Si estuviera abierta desde el principio, el jugador podría ir de la Cartuja a Macarena y saltarse la Torre del Oro | — | **[PENDIENTE]**. Propuesta: bloquearla hasta el tramo final |
| Zona Noble | Custodiada por los secuaces del jefe | Al llegar a esa parte de la historia | **[DECIDIDO]** (el mecanismo, **[PENDIENTE]**) |
| Los Pueblos ↔ Triana / Cartuja | Fuera del juego base; no debe permitir saltarse la progresión | — | **[PENDIENTE]** |

**Regla general para cualquier bloqueo nuevo:** comprobar con la tabla de vecinos que no exista un camino alternativo que se salte un jefe o un punto de la historia.

---

## 5. Orden de progresión

**[PROPUESTO]** como orden completo. Los hitos 1, 4, 8 y 9 (inicio en la Cartuja, primer jefe en la Torre del Oro, rescate en la Zona Noble y final en la Torre Pelli) están **[DECIDIDOS]**. El orden de las zonas intermedias es una propuesta del GDD que el autor no ha cambiado.

1. **Cartuja:** búnker y afueras (tutorial).
2. **Triana.** Ojo: desde la Cartuja no hay conexión directa con Triana. Se llega cruzando la zona del **Río**, así que esa zona tiene que poder atravesarse antes de luchar contra el jefe (ver sección 4).
3. **Los Remedios.**
4. **Río / Torre del Oro:** **primer jefe**. Al vencerlo se abre la ruta sur.
5. **Casco Antiguo.**
6. **Plaza de España / Heliópolis.**
7. **Macarena / Nervión.**
8. **Zona Noble:** rescate del científico.
9. **Torre Pelli** (Cartuja): el jefe de la Torre del Oro reaparece por sorpresa como jefe final; después se activa la bomba descontaminadora.

**En paralelo:** a mitad de partida, después del primer jefe, se abre el **Parque del Alamillo** y la ciudad empieza a crecer. **[DECIDIDO]**

---

## 6. Cómo se representa en el motor

El juego está hecho en **Python con pygame-ce**. Los mapas se editan con **Tiled** y se guardan como **Tiled JSON (`.tmj`)**.

**Convenciones de idioma** **[DECIDIDO]**:
- **Código en inglés:** identificadores, propiedades de Tiled, tipos de evento y nombres de archivo.
- **Comentarios y documentación en español.**
- **Textos del juego en español**, preparados para traducir.

### 6.1. Estado actual

| Mapa (archivo) | Zona | Tamaño |
|---|---|---|
| `hispazombie/assets/maps/bunker.tmj` | Cartuja: búnker | 20×15 casillas de 16 px |
| `hispazombie/assets/maps/cartuja_outskirts.tmj` | Cartuja: afueras | 40×30 casillas de 16 px |

- **Viajar entre mapas:** hoy se hace con eventos `door` (puertas).
- **[PROPUESTO]** en la Fase 4 del plan técnico: una **pantalla de viaje sobre el mapa de pergamino**. El jugador elige una zona vecina del grafo; las conexiones bloqueadas dependen de interruptores.
- **Salidas actuales de las afueras de la Cartuja:**
  - Norte, casillas (10,1) y (11,1): evento `blocker` "Camino hacia el Parque del Alamillo" (radiación).
  - Sur, casillas (17,28) y (18,28): evento `blocker` "Camino hacia el río y Triana" (de momento cerrado, porque aún no hay más mapas).

### 6.2. Estructura de un mapa de Tiled

- **Capas de tiles:** `ground` y `objects` (se dibujan debajo del personaje) y `above` (encima).
- **Capa de objetos:** `events`.
- **Propiedades de tile:** `solid` (no se atraviesa) y `bump_text` (texto al chocar).
- **Propiedad del mapa:** `name`, el nombre visible del mapa.

**Tipos de evento** (campo *Clase* del objeto en Tiled):

| Tipo | Qué hace | Propiedades |
|---|---|---|
| `spawn` | Posición inicial al entrar sin coordenadas | `facing` |
| `door` | Al pisarlo, cambia de mapa | `map`, `target_x`, `target_y`, `facing` |
| `sign` | Texto al pulsar Aceptar delante | `text` |
| `chest` | Se abre una vez y da un objeto | `id`, `item`, `text` |
| `blocker` | Casilla infranqueable con texto al chocar | `text` |
| `auto` | Se ejecuta una sola vez al entrar al mapa | `id`, `text` o `script` |
| `npc` | Personaje con sprite; se habla con él | `sprite`, `facing`, `script` o `text` |
| `encounters` | Zona rectangular de combates aleatorios | `table` |

**Propiedades comunes:**
- `script`: script JSON en `hispazombie/assets/events/<script>.json`.
- `show_if` / `hide_if`: el evento solo aparece si un interruptor está encendido / apagado.

Los valores de `facing` son `up`, `down`, `left` y `right`.

### 6.3. Cómo implementar un bloqueo entre zonas

1. Poner eventos `blocker` en la salida, con `hide_if: "<interruptor>"` y un texto que explique por qué no se puede pasar.
2. Poner el evento `door` de la salida con `show_if: "<interruptor>"`.
3. Encender el interruptor desde un script con `{"cmd": "switch_on", "id": "<interruptor>"}`, por ejemplo en `on_win` del comando `battle` de un jefe.

**Interruptores propuestos** **[PROPUESTO]**:

| Interruptor | Qué desbloquea |
|---|---|
| `torre_del_oro_boss_defeated` | La ruta sur |
| `alamillo_decontaminated` | El Parque del Alamillo |
| `scientist_rescued` | El tramo final |
| `torre_pelli_open` | La Torre Pelli |

Los scripts de eventos admiten estos comandos: `text`, `choice`, `if`, `switch_on`, `switch_off`, `set_variable`, `add_variable`, `give_item`, `remove_item`, `give_coins`, `remove_coins`, `move`, `face`, `wait`, `teleport`, `battle`, `learn_skill`, `rest` y `end`. La referencia completa está en `hispazombie/events/interpreter.py`.

### 6.4. Grafo en formato de datos

Este JSON es **[PROPUESTO]** como formato para la futura pantalla de viaje. Recoge las conexiones decididas y los bloqueos con los interruptores propuestos. `requires: null` significa que no hay bloqueo decidido; `requires: "PENDIENTE"`, que el bloqueo está por decidir.

```json
{
  "zones": {
    "cartuja":         {"name": "Cartuja",                      "maps": ["bunker", "cartuja_outskirts"]},
    "alamillo_park":   {"name": "Parque del Alamillo",          "maps": []},
    "triana":          {"name": "Triana",                       "maps": []},
    "los_remedios":    {"name": "Los Remedios",                 "maps": []},
    "river":           {"name": "Río / Torre del Oro / Arenal", "maps": []},
    "old_town":        {"name": "Casco Antiguo",                "maps": []},
    "macarena":        {"name": "Macarena",                     "maps": []},
    "noble_zone":      {"name": "Zona Noble",                   "maps": []},
    "nervion":         {"name": "Nervión",                      "maps": []},
    "plaza_de_espana": {"name": "Plaza de España",              "maps": []},
    "heliopolis":      {"name": "Heliópolis",                   "maps": []}
  },
  "connections": [
    {"a": "cartuja",         "b": "alamillo_park",   "requires": "alamillo_decontaminated"},
    {"a": "cartuja",         "b": "river",           "requires": null},
    {"a": "cartuja",         "b": "macarena",        "requires": "PENDIENTE"},
    {"a": "triana",          "b": "river",           "requires": null},
    {"a": "triana",          "b": "los_remedios",    "requires": null},
    {"a": "triana",          "b": "heliopolis",      "requires": "torre_del_oro_boss_defeated"},
    {"a": "los_remedios",    "b": "heliopolis",      "requires": "torre_del_oro_boss_defeated"},
    {"a": "river",           "b": "old_town",        "requires": "torre_del_oro_boss_defeated"},
    {"a": "river",           "b": "plaza_de_espana", "requires": "torre_del_oro_boss_defeated"},
    {"a": "plaza_de_espana", "b": "heliopolis",      "requires": null},
    {"a": "plaza_de_espana", "b": "nervion",         "requires": null},
    {"a": "old_town",        "b": "macarena",        "requires": null},
    {"a": "old_town",        "b": "nervion",         "requires": null},
    {"a": "macarena",        "b": "nervion",         "requires": null},
    {"a": "macarena",        "b": "noble_zone",      "requires": "PENDIENTE"}
  ],
  "expansion": {
    "los_pueblos": {"connects_to": ["cartuja", "triana"], "status": "PENDIENTE"}
  }
}
```

**Aviso:** los bloqueos de `river ↔ old_town` y `river ↔ plaza_de_espana` son una **interpretación propuesta**. El GDD dice que el progreso pasa por la Torre del Oro antes del Casco Antiguo, pero no fija el mecanismo. Confírmalo con el autor antes de darlo por bueno.

---

## 7. Reglas para generar contenido nuevo

1. **No añadir ni quitar conexiones** del grafo sin confirmarlo con el autor.
2. **Respetar el orden de progresión** (sección 5). Antes de abrir un paso, comprueba que no permite saltarse el primer jefe, el rescate del científico ni el final.
3. **Las decisiones [DECIDIDO] no se cambian.** Lo [PENDIENTE] se propone como opción, no se presenta como hecho.
4. **Mantener la geografía real de Sevilla** como referencia (el río separa la Cartuja y Triana, al oeste, del Casco Antiguo y el resto, al este), salvo cuando el grafo diga otra cosa: **el grafo manda**.
5. **Tono de humor sevillano** en textos y nombres. **Nada de marcas ni clubes reales:** por ejemplo, la rivalidad Heliópolis contra Nervión, con nombres inventados.
6. **Convenciones de código** (sección 6): identificadores en inglés, textos en español.
7. **Las facciones están en pausa:** no desarrollarlas sin pedirlo. La Orden de la Giralda, los Hidro-Monjes, la Resistencia de Triana y los Hijos de la Ceniza existen solo como base.
