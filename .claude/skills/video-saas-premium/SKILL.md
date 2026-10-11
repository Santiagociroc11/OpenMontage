---
name: video-saas-premium
description: Crea videos de lanzamiento SaaS / producto con nivel Apple o Figma (motion graphics premium, 1920×1080 renderizado en 4K60) a partir del link del producto y una idea. Extrae la marca de la web, piensa el concepto con un proceso creativo anti "AI slop", pide capturas de la interfaz real y la recrea 1:1, anima con cámara tipo Screen Studio (zoom in/out), 3D real con Three.js (iPhone con la UI viva, logo extruido), tipografía con barridos de movimiento, voz en off de ElevenLabs sincronizada palabra por palabra, música que se abre en la solución y efectos de sonido curados. Usa HyperFrames (HTML + GSAP). Úsala cuando digan "hazme un video saas de <url>", "video de lanzamiento", "promo de mi app", "motion graphics de mi producto", "video estilo Apple / Figma" o "video premium".
---

# Video SaaS premium

Convierte **un link + una idea** en un video de lanzamiento que parece hecho por un estudio:

**marca → concepto → capturas reales → historia → animación (UI + 3D + tipografía) → voz → música → efectos → render 4K**

Habla con la persona en su idioma y en tono cercano. Explica qué vas a hacer antes de cada paso largo.

## Lo que hace premium a un video (y lo que lo vuelve "AI slop")

- **La interfaz es real.** Nunca inventes una UI que existe (la app del cliente, Claude Code, WhatsApp, Slack, un dashboard…). Se recrea **1:1 desde capturas**: mismas medidas, colores muestreados, tipografía, íconos y textos. Una "terminal oscura cualquiera" o un "chat genérico" delatan el video como hecho por IA.
- **La cámara sobre la UI** (estilo Screen Studio): zoom in a cada acción (escribir, clic, resultado) siguiendo al cursor, zoom out para mostrar toda la ventana, paneos, warp líquido entre estados.
- **Una sola idea verdadera sobre ese producto** convierte el video en concepto. Decoración no es creatividad (ver [Proceso creativo](references/proceso-creativo.md)).
- **3D real, no CSS falso**: iPhone con la pantalla dibujada en vivo, logo del cliente extruido, íconos con brillo (`kit/three-stage.js`).
- **Tipografía pequeña y segura** (60–76 px a 1080p), una sola frase de acento por línea, palabras que entran con **barrido direccional** y salen con *whip*.
- **Nunca flashes blancos** ni "cúpulas" de luz para pasar de oscuro a claro: corte de 0.18 s escondido en un movimiento.
- **Sonido en cada beat**, sin que tape la voz.
- **Solo hechos.** Nada de cifras, reseñas o afirmaciones inventadas. Si el gancho es un problema del mercado, verifícalo en la web.

## 0. Requisitos (revísalos la primera vez)

- **Node 22+** (para `npx hyperframes`), **ffmpeg**, **Google Chrome** o Chromium (para extraer la marca), **Python 3** con `numpy` y `Pillow` (`pip3 install numpy pillow`; `matplotlib` opcional).
- HyperFrames se usa con `npx hyperframes …` (no hace falta instalarlo).
- **Opcional: ElevenLabs** para la voz en off y la música. La API key **nunca** se pega en el chat: la persona la guarda en su llavero (ver [Voz y música](references/voz-y-musica.md#la-api-key)).
- **Opcional: un pack de efectos de sonido** propio. `scripts/sfx_curate.py` elige los mejores (ver [Efectos](references/sfx.md)).

Si falta algo, dilo y explica cómo instalarlo; no avances a ciegas.

## 1. La marca (desde el link)

```bash
python3 scripts/brand_from_url.py https://producto.com brand/
```

Saca colores (revisa sus roles a ojo), tipografías (incluye Google Fonts), logo, titulares reales del DOM y capturas de la web. Lee también el resto de la web: precios, comparativas, la sección que más repite el producto. **Ese copy real es tu materia prima.**

## 2. El concepto (antes de cualquier píxel)

Sigue [Proceso creativo](references/proceso-creativo.md): 5–10 observaciones reales → **una** observación que se vuelve concepto ("vi que ___, así que el video ___") → **2–3 conceptos con mecanismos distintos** → recomienda uno y **deja que la persona elija**.

Estructura que funciona para SaaS: **problema real (oscuro) → "ya llegó la solución" → el producto haciendo su trabajo en su UI real → prueba (resultado en el teléfono / el panel) → remate que refleja el problema → logo + CTA**. 30–40 s con voz.

## 3. Pide capturas de referencia (paso obligatorio)

Antes de construir, envía una **lista corta de capturas** (qué pantalla, en qué estado, claro u oscuro) y **espera**. Para la persona es fácil: ⌘⇧4 + Espacio sobre la ventana. Detalle y checklist en [Capturas de UI](references/capturas-ui.md). Toma tú lo público (web, docs) a 2×.

Con las capturas: **mide** (en pt), **muestrea colores** (PIL), identifica la tipografía e íconos, copia los textos exactos (recorta y amplía para leerlos) y recrea 1:1. Simplifica quitando ruido, nunca inventando. No uses datos personales que aparezcan en las capturas.

## 4. Construye

```bash
npx hyperframes init motion --non-interactive --example=blank
cp -R <skill>/kit motion/kit        # premium.js, three-stage.js, motion-kit.js/.css
```

Parte de `examples/starter/index.html`. Reglas de look, gramática de transiciones, cámara y patrón de actos en [Look premium](references/look-premium.md); API completa en [Kit](references/kit.md).

- Un timeline raíz `gsap.timeline({paused:true})` registrado en `window.__timelines.main`; cada acto es un timeline hijo con su tiempo local (`MKP.act()` → `root.add(acto, offset)`).
- Las ventanas viven en un `#cam` (transform-origin 0 0) y la cámara se mueve con `cam(t, [x, y], escala)`.
- El 3D va en un `<canvas>` entre una capa DOM de fondo y otra de frente, con su propio timeline (`bindTimeline`).

Verifica con `npx hyperframes check .` y **muchos snapshots** (`npx hyperframes snapshot . --at …`), incluidos los cuadros a mitad de cada transición. Busca: texto encimado, UI genérica, momentos estáticos, cortes duros, flashes.

## 5. Voz en off, música y efectos

- **Voz** (ElevenLabs): genera la misma frase con 4–6 voces y que **la persona elija escuchando**. El guion dice **exactamente lo que se lee en pantalla** y cada palabra aparece cuando se pronuncia (`MKP.sayIn`). Acrónimos fonéticos ("API" → "ei pi ái"). Ver [Voz y música](references/voz-y-musica.md).
- **Música**: 3 muestras de estilo → la persona elige → se **extiende por compases** (no se regenera), apagada en el problema y abriéndose en un downbeat justo en la solución, con ducking bajo la voz.
- **Efectos**: uno protagonista por movimiento, alineado al pico (`audio_tools.py peaks`). Revisa la mezcla con `audio_tools.py check`. Ver [Efectos](references/sfx.md).

## 6. Render

```bash
npx hyperframes render --resolution 4k --fps 60 --quality delivery -o ../video-4k.mp4
```

Compón a 1920×1080; el render sale a 3840×2160 (el canvas 3D usa `setPixelRatio(2)`). Abre el resultado y cuéntale a la persona qué hay en cada beat.

## Cómo leer las críticas

| Dicen | Significa | Haz |
|---|---|---|
| "se ve AI slop" | Hay UI o componentes genéricos | Pide/usa capturas reales; quita lo que no defienda una razón de esta marca |
| "se ve horrible / barato" | Texto grande, flashes, fades planos, todo estático | Vuelve al look premium: tipografía pequeña, barridos, cámara, 3D |
| "no me convence" | El concepto es débil | Vuelve al paso 2 con otra observación |
| "la voz / música está fea" | Elegiste por ellos | Dales muestras para que elijan escuchando |
| "no está sincronizado" | Colocaste la voz por estimación | Marcas de tiempo por palabra y `sayIn` |
| "me gusta pero…" | Concepto aprobado | Arregla solo lo que piden |

Errores conocidos y soluciones: [Errores comunes](references/errores-comunes.md).
