# Efectos de sonido

La skill **no trae sonidos** (sus licencias varían). Trae el método para elegir los mejores de **tu propio pack**:

```bash
python3 scripts/sfx_curate.py --src ~/Descargas/MiPackDeSFX --out assets/sfx/premium --per-role 3 --sheet curados.png
```

Mide cada archivo (saturación, ruido de fondo, ataque y cola limpios, forma de la envolvente, estéreo, frecuencia de muestreo), lo clasifica por rol según su carpeta/nombre y su forma, lo puntúa y exporta los mejores **recortados, con fade y normalizados a −1 dBFS** como `<rol>-N.mp3`, con un `manifest.json` que dice de dónde salió cada uno (revisa su licencia antes de compartir). `--sheet` genera espectrogramas para revisarlos a ojo: un buen whoosh tiene forma de "paso" (sube, pico, baja) y banda completa; descarta el ruido plano y los archivos con varias tomas pegadas.

Fuentes libres para uso comercial: Pixabay, Freesound (revisa cada licencia CC), Mixkit, YouTube Audio Library.

## Roles y dónde usarlos
| Rol | Úsalo en |
|---|---|
| `whoosh-soft` | palabras que entran, chips, movimientos pequeños |
| `whoosh-pass` | zooms de cámara, paneos, el teléfono 3D entrando |
| `whoosh-long` | vuelos lentos, el logo llegando, cambios grandes de escena |
| `whip` | salidas en whip |
| `reverse` | succión hacia un corte o el logo (termina en el golpe) |
| `riser` | tensión antes de una revelación (su pico en el cuadro exacto) |
| `subdrop` | cambio oscuro ↔ claro, congelado, la llegada de la solución |
| `impact` | logo que se fija, dato que aterriza |
| `shimmer` | brillos, check de éxito, logo |
| `ui-click`, `ui-pop`, `ui-confirm`, `ui-notify` | clics del cursor, burbujas, confirmaciones, mensajes entrantes |
| `typing` | texto que se escribe en una terminal o input |
| `glitch` | cortes tech (con moderación; no en piezas calmadas) |
| `cash`, `camera` | dinero/precios, capturas |

## Colocación
- **Uno protagonista por movimiento.** No apiles tres whooshes.
- Alinea el **pico** del sonido con el pico del movimiento: `inicio = momento − pico`.
  ```bash
  python3 scripts/audio_tools.py peaks assets/sfx/premium/*.mp3
  ```
  Un riser con pico a 2.2 s que debe golpear en 12.98 empieza en 10.78.
- Volúmenes de partida (archivos normalizados al mismo pico): whooshes 0.2–0.35, UI 0.2–0.45, impactos/sub drops 0.2–0.5.
- Revisa que nada tape la voz:
  ```bash
  python3 scripts/audio_tools.py check index.html --vo assets/audio/vo-mix.mp3 --music assets/audio/music-mix.mp3
  ```
  Baja los efectos que marque.
