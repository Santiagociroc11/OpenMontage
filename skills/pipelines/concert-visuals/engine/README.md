# Motor de mundo continuo (concert-visuals)

Implementación de `../continuous-world.md`, el lenguaje de VJ Rauw: un solo
mundo inclinado que una cámara recorre, elementos que entran y salen de a uno,
cambios de fondo hechos por una forma que crece, y tipografía de lockups. Es
HTML/DOM puro (sin WebGL) renderizado con HyperFrames; el show de 6:32 se
renderiza en unos 2 minutos en un M3 Pro.

## Archivos

| Archivo | Qué es |
|---|---|
| `world.template.html` | Runtime: lee los elementos (`data-p`) y evalúa cada cuadro como función del tiempo de canción. Base de color, cámara, entradas/salidas, ecos, lockups, rellenos. |
| `build_world.py` | Arma los tramos de 12 s, cachea por hash, renderiza en paralelo, une con `concat -c copy`, copia de revisión con audio y masters H.264 / ProRes 422 HQ sin audio. Modos `fotos`, `clip`, `show`. |
| `plan_example_la_mitad.py` | El plan de "La mitad de mi vida": secciones → mundos, ganchos verificados, generador determinista de elementos, límites de densidad. Copiarlo al proyecto y adaptarlo. |
| `bake_images.py` | Duotonos, siluetas y proporciones a partir de recortes PNG. |
| `fonts/` | Anton (OFL) y Ultra (Apache 2.0), las dos únicas familias que usa el lenguaje. |
| `vendor/gsap.min.js` | GSAP 3.14 (solo para el timeline raíz que exige HyperFrames). |

## Nuevo proyecto

1. Recortar fotos del artista con rembg (venv aislado) y correr `bake_images.py`
   hacia `projects/<p>/hyperframes/world_images`.
2. Copiar `plan_example_la_mitad.py` a `projects/<p>/hyperframes/plan.py` y
   cambiar `SECTIONS` (tiempos del `song_map` / letra), `HOOKS` (solo ganchos
   verificados contra la alineación), `PHOTOS` (claves de `bake_images`) y la paleta.
3. Escribir `projects/<p>/hyperframes/world.json`:
   ```json
   {"project": "projects/<p>", "plan": "projects/<p>/hyperframes/plan.py",
    "song_map": "projects/<p>/song_map/<slug>.json", "track": "<audio>",
    "images": "projects/<p>/hyperframes/world_images", "name": "<slug>", "fps": 30}
   ```
4. Iterar con fotos (≈10 s): `build_world.py --config <cfg> fotos 25,50.5,57`.
   Un clip con audio (≈20 s): `... clip 40 30`. Show completo: `... show --master`.

## Velocidad (medido)

- Fotos sueltas: 4–15 s. Clip de 30–50 s: 6–20 s si los tramos están en caché.
- Show completo (33 tramos × 12 s): ~120 s con `JOBS=3`, `WORKERS=4`.
- `--browser-gpu` por defecto; `--no-browser-gpu` es 2,5× más lento.
- HyperFrames fijado en `0.8.145`: una actualización automática a mitad de
  sesión dejó el runtime con *checksum mismatch* y rompió todos los renders.
- Spotlight (`mds_stores`, `mediaanalysisd`) indexando los renders se come
  ~2 núcleos; excluir `projects/` de Spotlight si se nota.
