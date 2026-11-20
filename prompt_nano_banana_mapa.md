# Prompt para Nano Banana: mapa del mundo de HispaZombie

## Cómo usarlo

1. Abre Gemini con **Nano Banana** (generación y edición de imágenes).
2. **Adjunta dos imágenes, en este orden:**
   1. `map_draft_1.jpeg`: la **referencia de estilo** (pergamino, tinta, acuarela).
   2. `hispazombie/assets/world/world_map_labeled.png`: la **referencia de composición**, con la posición exacta de cada zona, el río y los caminos.
3. Pega el **prompt principal**. Va en inglés porque el modelo lo sigue mejor; los nombres que aparecen en el mapa van en español.
4. Cuando tengas una imagen que te guste, usa los **prompts de seguimiento** en la misma conversación para sacar las otras versiones.

**Consejos:**
- Si algún nombre sale mal escrito, pídele que corrija solo ese texto ("Fix the label 'Heliópolis', keep everything else").
- Si añade caminos o puentes que no están en la lista, pídele que los borre uno a uno.

---

## Prompt principal (versión con nombres)

```text
Create a hand-drawn fantasy-style world map for a humorous post-apocalyptic RPG set in Seville, Spain.

USE THE TWO ATTACHED IMAGES:
- Image 1 is the STYLE reference: copy its look exactly — a worn parchment map pinned to a wooden table with nails in the corners, ink lines and watercolor, coffee stains, burnt and torn edges, a red wax seal, a compass rose in the bottom-left corner, small illustrated buildings seen from slightly above.
- Image 2 is the LAYOUT reference: keep the exact position of every zone, the course of the river, every road and every bridge. Do not move, add or remove anything from that layout. Only repaint it in the style of image 1.

FORMAT: 16:9 landscape, 1920x1080, top-down map view, the whole parchment visible with some wood around it.

GEOGRAPHY (must match image 2):
- The Guadalquivir river runs from NORTH to SOUTH through the map, slightly left of center. It is a toxic, murky green-blue swamp.
- WEST bank (left of the river): Parque del Alamillo (top-left), Cartuja (left, middle-top), Triana (left, middle-bottom), Los Remedios (bottom-left).
- EAST bank (right of the river): Río / Torre del Oro / Arenal (right next to the river, center), Casco Antiguo (center-right), Macarena (top-center-right), Zona Noble (top-right corner), Nervión (right), Plaza de España (lower center-right), Heliópolis (bottom-right).

WHAT EACH ZONE LOOKS LIKE:
- Cartuja: a big glowing GREEN radioactive glass CRATER (this crater MUST be on the WEST side of the river, inside Cartuja). Next to it, a very tall cracked glass skyscraper (Torre Pelli) with a red seal on its base, twisted ruins, a construction site with a yellow excavator and a small dark bunker entrance.
- Parque del Alamillo: a large park with trees and a few small houses (the future town of the player).
- Triana: old pottery rooftops and arched entrances to underground tunnels.
- Los Remedios: ruined apartment blocks.
- Río / Torre del Oro / Arenal: the golden twelve-sided Torre del Oro turned into a fortified customs tower by the river, half-destroyed bridges, scrap-metal walkways and a barge.
- Casco Antiguo: the Giralda bell tower reinforced with steel plates and a searchlight on top; NORTH of it, the Setas (Metropol Parasol), a giant wooden mushroom-shaped canopy, half burnt; SOUTH of it, the Alcázar palace swallowed by a glowing bioluminescent green jungle.
- Macarena: old city walls with battlements and an arch.
- Zona Noble: an abandoned train station with a curved roof and rails. It is isolated: its only road goes to Macarena.
- Nervión: tall buildings and a generic ruined football stadium (no logos, no club colors).
- Plaza de España: the famous building as a SEMICIRCLE (half circle, never a full round coliseum) with a dry canal and broken tiled benches, used as a fighting arena. Remains of María Luisa park.
- Heliópolis: small houses and another generic ruined stadium (no logos, no club colors).
- Los Pueblos: only a faded hint at the far LEFT edge of the parchment, "unexplored lands".

ROADS — draw EXACTLY these 15 roads, as in image 2, and no others. Roads that cross the river are drawn as bridges:
1. Cartuja – Parque del Alamillo
2. Cartuja – Río / Torre del Oro (bridge)
3. Cartuja – Macarena (bridge, crossing the river to the north-east)
4. Triana – Río / Torre del Oro (bridge)
5. Triana – Los Remedios
6. Triana – Heliópolis (bridge)
7. Los Remedios – Heliópolis (bridge)
8. Río / Torre del Oro – Casco Antiguo
9. Río / Torre del Oro – Plaza de España
10. Plaza de España – Heliópolis
11. Plaza de España – Nervión
12. Casco Antiguo – Macarena
13. Casco Antiguo – Nervión
14. Macarena – Nervión
15. Macarena – Zona Noble
Plus two faint dashed paths from the left edge (Los Pueblos) to Cartuja and to Triana.
Do NOT draw a road between Cartuja and Triana. Do NOT connect Zona Noble to anything except Macarena. Do NOT connect Los Pueblos to the east side.

TEXT (hand-lettered in Spanish, spelled exactly like this, with accents):
- Title in the top-left corner: "SEVILLA"
- Zone names: "Parque del Alamillo", "Cartuja", "Triana", "Los Remedios", "Río / Torre del Oro / Arenal", "Casco Antiguo", "Macarena", "Zona Noble", "Nervión", "Plaza de España", "Heliópolis", and a faded "Los Pueblos" on the left edge.
- A small scale bar that says "1 siesta = 2 calles". No kilometers, no miles.
- No English text anywhere. No legend in English.

TONE AND DETAILS:
- Humorous, never gore or creepy. Tiny funny doodles in the margins: a flock of green parakeets, a coffee cup stain, a little hand-written note "no tocar: brilla" near the crater.
- Palette: parchment ochres and sepias, radioactive green accents, red for danger, murky blue-green water.
- Must stay readable when shrunk to 480x270 pixels: bold shapes, clear contrast, big recognizable landmarks.
- No real brands, logos, coats of arms or football club colors.
```

---

## Prompt de seguimiento 1: versión sin textos (para el juego)

El juego pone los nombres encima para poder traducirlos, así que necesita una versión limpia.

```text
Now make the exact same map with NO text at all: remove the title, all zone names, the scale bar and the hand-written notes. Keep the compass rose. Do not change anything else — same composition, same buildings, same roads, same colors.
```

---

## Prompt de seguimiento 2: versión de "restricciones al inicio de la partida"

Esta versión muestra cómo se ve el mundo al principio del juego, con los bloqueos que ya están decididos en el GDD. Sirve como referencia visual y como arte de presentación. En el juego, estos estados se superponen por separado.

```text
Now make a version of the labeled map that shows the restrictions at the START of the game. Same composition, only add these hand-drawn elements in the same ink and watercolor style:
- Parque del Alamillo covered by a glowing green radioactive cloud, and its road to Cartuja crossed by a red X.
- The Torre Pelli in Cartuja sealed with a big red wax seal and chains.
- The bridge Triana – Heliópolis and the bridge Los Remedios – Heliópolis drawn as broken bridges with a red X.
- The roads Río / Torre del Oro – Casco Antiguo and Río / Torre del Oro – Plaza de España blocked by small wooden barricades with a red X.
- The Torre del Oro fortress with a small closed gate and a skull wearing a construction helmet (the first boss lives there).
- Zona Noble marked with a skull wearing a construction helmet (guarded by the boss's henchmen).
- A pin shaped like a coffee cup on Cartuja with the hand-written words "Estás aquí".
Do not mark the Cartuja – Macarena bridge in any special way. Do not add any other blocks.
```

---

## Prompt de seguimiento 3: hoja de iconos de estado (opcional)

Los iconos sueltos que el juego superpone sobre el mapa base.

```text
Using the same art style as the map, create a sprite sheet on a plain flat light background (one solid color, no texture) with these separate icons, evenly spaced and not touching each other: a patch of grey ink fog for unexplored areas, a glowing green radioactive cloud, a red wax seal, a small padlock, a broken bridge, a small wooden barricade with a red X, a big red X, a skull wearing a yellow construction helmet, a coffee-cup-shaped map pin, a hand-drawn "completed" stamp, and a small cluster of houses for a town. No text.
```
