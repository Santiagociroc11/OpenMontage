# Errores comunes (y cómo se arreglaron)

- **El timeline entero no corre y solo se ve el 3D** → un helper recibió un array de selectores sin resolver y lanzó un error. `MKP` ya los resuelve; si escribes helpers propios, convierte strings a elementos.
- **Un botón salta encima del texto** → un `transform` en un contenedor lo vuelve el bloque contenedor de sus hijos `position:absolute`. Dale al contenedor animado `position:absolute; inset:0`.
- **`filter:url(#…)` aplana el 3D** del elemento → pon la perspectiva en el propio elemento (`transformPerspective`), no en el padre.
- **"GSAP timeline is not registered"** → los timelines hijos y el del 3D se crean con `new gsap.core.Timeline()`, no con `gsap.timeline()`.
- **Dos composiciones raíz** → la plantilla con `data-composition-id` no puede estar en la raíz del proyecto; muévela a `src/`.
- **Al reacomodar un acto** mueve también: tiempos de la pantalla del teléfono, el timeline 3D y los `data-start` del audio. (Una vez unos whooshes quedaron 10 s antes.)
- **Pantalla del teléfono ilegible** → dibuja la UI con zoom (`VW ≈ 330–360` pt) y deja el cristal aditivo con `opacity ≈ 0.12–0.18`.
- **Texto claro sobre fondo claro** → si el escenario cambia, revisa el orden de capas (un wallpaper encima de otro tapa el `cut`).
- **"text_occluded" en `check`** con un canvas 3D transparente encima → falso positivo; márcalo con `data-layout-allow-occlusion`.
- **El render pide otra versión** → usa el script del proyecto (`npm run render -- …`), que fija la versión de HyperFrames.
- **ffmpeg**: reutilizar una entrada en un filtergraph requiere `asplit`; algunos builds no traen `drawtext` (usa matplotlib/PIL para hojas con etiquetas); usa `LC_ALL=C` en scripts (locales con coma decimal rompen el parseo).
- **ElevenLabs**: 403 por formato 192 kbps en el plan básico; 429 con más de 2 peticiones a la vez; los prompts de música con nombres de marca son rechazados.
- **Contadores al hacer seek hacia atrás** no se reinician si usas `onUpdate` sobre un objeto: el render (hacia adelante) está bien, pero revisa los snapshots en orden.
