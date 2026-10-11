# La mitad de mi vida — Tiko Durán (visual LED, free_run)

Proyecto de referencia del pipeline `concert-visuals`. Versión aprobada: **mundo
continuo estilo VJ Rauw** (`hyperframes/src3/`, idéntico al motor del repo en
`skills/pipelines/concert-visuals/engine/`, config `hyperframes/world.json`).

| Carpeta | Qué es |
|---|---|
| `hyperframes/src/` | v1 (Windows): show por tramos con shader, look tests v1–v3 |
| `hyperframes/src2/` | v2–v5: catálogo de escenas (psicodélico → geométrico Rauw) — rechazado: "cosas sueltas" |
| `hyperframes/src3/` | **v6–final**: mundo continuo (aprobado) |
| `song_map/`, `audio_data/` | Mapa de la canción y bandas por cuadro |
| `research/referencias_visuales.md` | Notas de las 6 rondas de investigación de referencias |

No publicados (locales): audio, letra oficial, fotos del artista, capturas de
referencias de terceros y renders (33 GB). Para reconstruir: recortar fotos con
rembg, `engine/bake_images.py`, y `engine/build_world.py --config hyperframes/world.json show --master`.
