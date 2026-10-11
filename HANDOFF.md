# Handoff — sesión 11 oct 2026 (Mac): "La mitad de mi vida" terminado + motor de mundo continuo

> Esta sección es la más reciente; la del 10 oct (Windows) y la del 28 ago siguen debajo.

**Resultado:** después de 8 versiones rechazadas, el usuario aprobó ("me encanta") el
**mundo continuo al estilo VJ Rauw**. Masters en
`projects/la-mitad-de-mi-vida/renders/v3/01_la-mitad-de-mi-vida_FINAL_*`
(review con audio, H.264 y ProRes 422 HQ sin audio, 1920×1080@30, 6:32 con cola de 60 s).

**Qué quedó en el repo (sin commitear):**

| Pieza | Dónde |
|---|---|
| Lenguaje visual aprobado (mundo, cámara, densidad, tipografía, lo rechazado) | `skills/pipelines/concert-visuals/continuous-world.md` |
| Método de investigación de referencias (IG highlights vía Chrome, 30 cuadros/historia, 12 fps en cambios) | `skills/pipelines/concert-visuals/reference-research.md` |
| Motor reutilizable (plantilla DOM, build con caché por tramos de 12 s, bake de fotos, plan de ejemplo, fuentes Anton/Ultra) | `skills/pipelines/concert-visuals/engine/` |
| Skills de idea/escena/assets/compose/productor actualizadas y manifest con las 2 skills nuevas | `skills/pipelines/concert-visuals/*.md`, `pipeline_defs/concert-visuals.yaml` |

**Mac (esta máquina):** Node 22 en `~/.local/node22`, ffmpeg/ffprobe/uv/yt-dlp en
`~/.local/bin` (en `~/.zshrc`), `.venv` Python 3.12 creado con uv. rembg vive en un venv
aislado del scratchpad (no en `.venv`). HyperFrames fijado a `0.8.145` en el motor.

**Cómo retomar:** `projects/la-mitad-de-mi-vida/hyperframes/world.json` apunta al motor del
repo; `.venv/bin/python skills/pipelines/concert-visuals/engine/build_world.py --config
projects/la-mitad-de-mi-vida/hyperframes/world.json fotos 50.5` (segundos) o `show --master`
(~2 min). Fotos del artista: `assets/images/tiko_0[1-5]*` + logo real `logo_tiko_duran.png`.

**Pendiente / siguiente:**
- Tiko **en video recortado** (como las bailarinas de Ana): bajar sus en vivo de YouTube
  (@tikoduran7455, p. ej. `mNHffgjrDyg`, `3_cLzsP7TwY`), recortar loops de 3 s con rembg por
  cuadro y usarlos en lugar de las fotos fijas. El primer intento de descarga falló sin revisar.
- Canvas real del venue (sigue provisional 1920×1080) y prueba en pantalla LED.
- Otras canciones de Tiko en Escritorio/Descargas (Perdido, Obsesión, Materialista, Cásate conmigo…).

**Lecciones no obvias de esta sesión:** ver `continuous-world.md` §7 (qué se rechazó) y
`compose-director.md` §1b (velocidad: draft+crf 12, no `--gpu`, Spotlight, versión fija).

---

# Handoff — sesión 10 oct 2026: pipeline `concert-visuals` + "La mitad de mi vida"

> Esta sección es la más reciente. La sesión del 28 ago (ads webtoon) sigue debajo.

**Qué se construyó (en el repo, sin commitear):**

| Pieza | Dónde | Estado |
|---|---|---|
| Herramienta `song_map` (BPM global y por sección, beats, compases, secciones con energía en dB, drops) | `tools/analysis/song_map.py` + `tests/tools/test_song_map.py` | 4 tests pasan (pista sintética 120 BPM, drop en 16 s) |
| Pipeline `concert-visuals`, 3 modos: `song_sync`, `vj_loops`, `free_run` | `pipeline_defs/concert-visuals.yaml`, `skills/pipelines/concert-visuals/` (8 skills) | 5 tests de contrato pasan |
| Fix UTF-8 en las llamadas al CLI de HyperFrames (Windows cp1252 rompía la lectura y perdía errores) | `tools/video/hyperframes_compose.py` | 55 tests HyperFrames pasan |
| Pipeline registrado en tablas | `AGENT_GUIDE.md`, `PROJECT_CONTEXT.md`, `docs/ARCHITECTURE.md` | — |

**Proyecto en curso: `projects/la-mitad-de-mi-vida/`** (visual de concierto para
Tiko Durán; carpeta `projects/` está en `.gitignore`: **solo viaja si se copia la
carpeta del repo entera, no por git**).

- Audio: `C:\Users\sanci\Desktop\La Mitad De Mi Vida - TIKO DURAN.wav` (5:32,
  grabación en vivo de fiesta privada en Ciénaga, **fuera del repo: copiarlo
  aparte**). Mapa: `song_map/la-mitad-de-mi-vida.json`. Tempo real 137→151 BPM
  (sube a lo largo de la canción).
- Letra oficial (LyricFind, compositor Felipe Peláez; original de Los Betos):
  `lyrics/letra_oficial.txt`. Tiempos de cada verso en la grabación:
  `lyrics/tiempos_versos.json` (alineación Whisper guiada por la letra).
  Instrumental real ≈ 1:40–3:28.
- Checkpoints aprobados: `idea` (modo `free_run`: banda en vivo SIN click y
  SIN operador; canvas 1920×1080@30 **provisional**; entrega MP4 H.264 +
  ProRes sin audio; runtime HyperFrames) y `script` (arco + 9 frases de letra).
- Look tests: v1 (mar/luna oscuro — **rechazado**, "demasiado lento, no es del
  género"), v2 (corazón partido + color saturado — gustó), **v3 = la dirección
  vigente** (más velocidad, mosaico de letra, estrellas de neón):
  `hyperframes/src/look_test_v3.template.html`, render `renders/look_test_v3_review.mp4`.
- Investigación de referencias: `research/referencias_visuales.md` + 3 hojas
  de contacto (≈145 capturas de shows de vallenato/champeta y del trabajo de
  VJ Rauw). Usuario pidió "lo mejor que determines" y **más velocidad**.
- Fotos del artista (descargadas de su Facebook oficial, pedido explícito del
  usuario): `assets/images/tiko_01_tarima_portada.jpg` (1440×1799, tarima,
  puño arriba) y `tiko_02_perfil.jpg` (2048×2048 estudio); recortes sin fondo
  `tiko_0X_cut.png` (rembg u2net_human_seg, revisados: limpios).

**Siguiente paso (donde quedó):** construir la composición de la canción
completa como *motor guiado por datos* (secciones con paleta/modo, tarjetas de
letra desde `tiempos_versos.json`, estados del corazón, bursts en las uniones
49.6 s y 236.4 s, fotos recortadas en duotono, logotipo tipográfico
"Tiko" cursiva + "DURÁN" condensada) y renderizarla en 4 ventanas exactas por
frame (0–100, 100–200, 200–300, 300–392.37 s; cola de 60 s de amanecer en
loop) para no pasar el timeout de 30 min del render. Plan de secciones
(cortes ya ajustados a compás): intro logo/título 0–17.5 · verso azul
17.5–44.9 · pre "es que ya yo puedo" 44.9 · unión estribillo 1 / atardecer
50.2 · gancho "déjame solo darte un beso" rojo 55.6 · "mil motivos" morado
70.9 · gancho 2 84.3 · instrumental (pop-art Britto / disco neón / warp)
99.8–209.3 · verso 2 íntimo corazón roto 209.3 · estrella fugaz 222.6 · luna y
sol 229.2 · estribillo 2 234.1 · gancho 244.1 · mil motivos 255.7 · gancho
270.6 · final 283.8 · amanecer pico 299.9 · aplausos + logo 319.0 · cola.

**Lecciones de la sesión (no obvias):**

- **El usuario quiere ver referencias reales antes de diseñar**, y muchas:
  YouTube + Instagram de VJs del género. Contar **solo lo que sale en la
  pantalla LED del show**, no los overlays/marcos que el VJ pone en sus reels.
- **Géneros caribeños = color saturado a muro completo**, letra protagonista,
  ilustración pop, foto del artista, movimiento constante al tempo. La regla
  "oscuro por defecto" de visuales genéricos era errónea aquí (ya corregido en
  las skills).
- **Velocidad**: el primer look test siempre queda lento. Atarlo al BPM local.
- `song_map`: el BPM por intervalos entre beats se cuantiza a hops (143 BPM se
  leía 136/152); se calcula sobre el **tramo completo** de beats. Las
  constantes de energía se derivan de la propia canción (dB relativos a la
  sección más fuerte), sin umbrales absolutos.
- HyperFrames: texto decorativo → `data-layout-ignore`; nunca
  `color: transparent` (falla `text_not_painted`); solo fuentes con
  `@font-face` locales; `index.template.html` dentro del workspace provoca
  `multiple_root_compositions` (plantillas fuera, en `src/`).
- **rembg en venv aislado** (`%TEMP%\claude\rembg_venv`): instala numpy 2.x y
  rompe chatterbox (numpy 1.26.4) en `.venv`. Se revirtió; `.venv` quedó sano.
- Whisper `large-v3` se colgó descargando (335 MB de ~3 GB); `small` + ventanas
  de 8 s con la **letra oficial como `initial_prompt`** alinea muy bien.
- Descargas desde Chrome (Claude in Chrome) caen en **Escritorio** o
  **Descargas**, según el disparo; buscar con `find -mmin`.
- La API de YouTube del conector Scrape Creators se quedó **sin créditos**;
  `yt-dlp` no está instalado. Se usó el navegador (búsqueda vía `fetch` de
  `/results` y `ytInitialData`).
- Instagram: la API interna `web_profile_info` devuelve **429** tras unas
  cuantas llamadas; leer la grilla del DOM con scroll funciona.
- Se instaló `pytest` en `.venv` (no estaba) y `librosa` en el Python global
  por error (el `.venv` ya la tenía vía chatterbox).

**Reglas de trabajo del usuario (de la memoria de Claude, no viajan solas):**
responder en español; leer `AGENT_GUIDE.md` antes de actuar; `git fetch` y
`pull --ff-only` antes de la primera edición; **commit/push solo si lo pide**,
mensajes en español estilo Conventional Commits; una variable por vez y mirar
la salida (hojas de contacto) antes de reportar; derivar constantes de los
datos; scripts largos con log y contador; el generador de imágenes nunca
escribe texto; en PowerShell nada de `&&`.

---

# Handoff — sesión OpenMontage (28 ago 2026)

Documento de traspaso para continuar en otra máquina. Todo lo que estaba en
`projects/` **no viaja por git** (esa carpeta está en `.gitignore`), así que lo
importante está embebido aquí.

**Objetivo del usuario:** replicar y escalar un ad de Facebook/Instagram que le
funcionó muy bien, al menor costo posible, aceptando formato animado si eso
abarata la producción.

---

## 0. PRIMERA ACCIÓN al abrir esto en el PC nuevo

Instrucción explícita del usuario: **antes de cualquier otra cosa, medir la GPU
de esta máquina.**

```bash
nvidia-smi --query-gpu=name,memory.total,driver_version,power.limit --format=csv
```

Si hay una GPU NVIDIA decente, **todo el problema de la ASUS (sección 4) deja de
importar** y la producción local se monta aquí. Si no, se decide entre CPU lento
o key de fal.ai (~$2.40/ad, sección 2).

Para medir velocidad real hace falta el benchmark, que **no viaja por git**
(vive en `projects/`, gitignored). Baseline de la ASUS para comparar: imagen
SDXL 832×1216 / 30 pasos en caliente = **350 s**. Una GPU sana hace eso en ~20 s.

---

## 1. El ad de referencia (el activo principal)

Archivo original: `C:\Users\SantiagoCiro\Desktop\1605777297927783.mp4`
(no está en el repo — copiarlo aparte si se necesita)

**Producto:** *40 Días de Viaje en Silencio: Escuchando el Susurro de Dios* —
infoproducto devocional / comunicación.

**Ficha técnica medida:**

| | |
|---|---|
| Duración | 135 s (2:15) |
| Formato | 9:16 vertical |
| Cortes | 52 (2.6 s promedio) |
| Idioma | español |
| Visuales | 100% video generado con IA, fotorrealista |
| Personajes | consistentes en todo el ad (Alejandro: canoso, traje; mujer de rojo) |
| Subtítulos | karaoke palabra por palabra, blanco con contorno negro, centrados |
| Narración | diálogo entre personajes, sin narrador en off |

### Estructura — esto es lo replicable

| Bloque | Tiempo | Función |
|---|---|---|
| Demo 1 — fallo | 0:00–0:07 | "Su coche bloquea el nuestro" → *"tal vez en tres horas"* |
| Demo 1 — éxito | 0:11–0:19 | "Alguien golpeó su coche" → *"voy para allá ahora mismo"* |
| Lección | 0:29–0:36 | *"La gente no se mueve por tu problema. Se mueve por lo que cree que puede perder."* |
| Demo 2 — fallo | 0:42–0:58 | Cajero traga tarjeta → banco: *"varios días"* |
| Demo 2 — éxito | 1:03–1:14 | *"El cajero está entregando dinero de más"* → técnico inmediato |
| Remate | 1:19–1:26 | *"No vinieron por tu tarjeta. Vinieron por su dinero."* |
| Principio | 1:30–1:44 | *"La mayoría habla desde su desesperación. Los que entienden a la gente hablan desde el interés del otro."* |
| Producto | 1:48–1:56 | *"Cuándo hablar, qué decir, y cuándo guardar silencio"* |
| Stack | 1:58–2:09 | Para ti / para tu pareja / para tu familia |
| CTA | 2:09–2:15 | *"Oferta por tiempo limitado. Toca el carrito naranja de abajo."* |

### Por qué funciona

1. **Demuestra, no promete.** 90 de 135 segundos son demostración dramatizada.
   El producto aparece al 80% del video.
2. **Doble prueba A/B en vivo.** Cada demo muestra la versión que falla y la que
   funciona ante el mismo problema. El espectador concluye solo.
3. **Hook de curiosidad, no de beneficio.** Arranca en conflicto sin contexto.
   Los primeros 3 segundos no venden nada.
4. **Aforismo portable.** "Se mueve por lo que cree que puede perder" es
   guardable y repetible.
5. **Escalada.** La demo 2 sube la apuesta (dinero > estacionamiento) y su
   remate es más fuerte.
6. **Stack de 3 al cierre** — identidad, pareja, familia. Tres razones de compra
   en 11 segundos.

### Plantilla para producir más

```
[0-20s]   Demo A: mismo problema, dos formas de pedir → una falla, una funciona
[20-35s]  Lección en una frase memorable
[35-90s]  Demo B: mismas reglas, apuesta más alta, remate más fuerte
[90-105s] El principio detrás de las dos demos
[105-120s] El producto como fuente del principio
[120-130s] Stack: para ti / para tu pareja / para tu familia
[130-135s] CTA con urgencia + instrucción física ("toca el carrito naranja")
```

Solo se cambian **los dos escenarios de demostración** y el aforismo. Guion
completo: ~350 palabras.

Escenarios candidatos para el mismo libro: jefe que ignora tu petición, hijo
adolescente que no contesta, cliente que no paga, discusión de pareja que
escala, vecino ruidoso.

### Transcripción completa (faster-whisper local)

```
[  2.10-  4.68] Hola, su coche está bloqueando el nuestro. Necesita venir a moverlo.
[  4.74-  6.58] No estoy cerca. Tal vez en tres horas.
[  6.80-  7.24] ¿Tres horas?
[ 11.41- 14.89] Señor, alguien golpeó su coche y se fue. Le conviene venir ahora.
[ 15.09- 17.35] ¿Qué? Mi coche. Voy para allá ahora mismo.
[ 18.35- 19.21] Ahora sí vendrá.
[ 29.50- 30.50] ¿De verdad vino tan rápido?
[ 30.88- 32.76] La gente no se mueve por tu problema.
[ 33.78- 35.80] Se mueve por lo que cree que puede perder.
[ 42.42- 43.66] ¿Se quedó con mi tarjeta?
[ 49.22- 51.96] La máquina se quedó con mi tarjeta. La necesito hoy, ¿me pueden ayudar?
[ 52.22- 54.44] Tiene que reportarla y esperar una reposición.
[ 54.68- 55.22] ¿Cuánto tarda?
[ 55.22- 56.82] El proceso tarda varios días.
[ 57.06- 58.34] Varios días. La necesito ahora.
[ 63.63- 65.27] Creo que este cajero tiene un problema serio.
[ 66.33- 67.57] Parece que está entregando dinero de más.
[ 67.95- 68.65] ¿Dinero de más?
[ 70.15- 71.41] ¿En qué ubicación está el cajero?
[ 71.85- 73.31] Enviaremos a un técnico de inmediato.
[ 79.49- 80.27] Aquí está su tarjeta.
[ 82.15- 82.65] ¿Tan rápido?
[ 83.13- 84.41] No vinieron por tu tarjeta.
[ 85.53- 86.49] Vinieron por su dinero.
[ 90.20- 94.42] Alejandro, ¿cómo siempre sabes exactamente qué decir?
[ 95.60- 97.62] Porque la mayoría habla desde su desesperación.
[ 97.62-101.08] Los que entienden a la gente hablan desde el interés del otro.
[101.66-103.74] Por eso todo cambia cuando hablas tú.
[104.48-107.68] Todo se vuelve más fácil cuando aprendes a hablar con intención.
[108.48-110.22] Cuarenta días de viaje en silencio.
[110.76-112.12] No es solo un libro para callar.
[112.52-113.96] Te enseña cuándo hablar, qué decir.
[114.80-116.12] Y cuándo guardar silencio.
[118.92-121.42] Para ti, una forma más fuerte de vivir.
[122.00-125.38] Para tu pareja, una comunicación más tranquila y más amorosa.
[126.00-129.44] Para tu familia, menos discusiones y más comprensión.
[129.82-131.92] Ahora está en oferta por tiempo limitado.
[132.34-133.80] Toca el carrito naranja de abajo.
```

> Nota: corregí a mano tres errores de transcripción ("repetición"→"reposición",
> "prendes a asa"→"aprendes a", "desperación"→"desesperación").

---

## 2. Rutas de producción y costos

Precios tomados de `docs/PROVIDERS.md` del repo, para un ad de 135 s.

### Ruta A — imágenes + Remotion (~$1–2)
Imágenes generadas + animación en Remotion (parallax, push-in, spring).
20 imágenes × $0.03 = $0.60 · TTS ~$0.01 · música Pixabay $0 · render local $0.

**Advertencia:** este ad vive de la actuación. Las stills funcionan bien en la
lección, el principio, el producto y el CTA (~60 s de los 135), pero pierden
fuerza en los dos remates de reacción (`0:15` y `1:19`). Si se va full imágenes,
**cortar a 60–75 s** — 135 s de stills se sienten largos.

### Ruta B — híbrido (~$2.40) ← recomendada
20 imágenes ($0.60) + **5 planos animados** por image-to-video en los momentos
que cargan la venta (5 × 5 s × $0.07 Kling = $1.75) + TTS ($0.01).

Clave técnica: el image-to-video parte de la imagen ya generada, así que
**hereda el personaje** y no rompe la consistencia.

### Ruta C — fotorrealista, clon del referente
14 clips de 10 s:

| Proveedor | $/seg | Total 140 s |
|---|---|---|
| Kling 2.5 Turbo Pro | $0.07 | $9.80 |
| MiniMax H3 | $0.10 | $14.00 |
| Seedance 2.5 | $0.134 | $18.76 |
| Veo 3 | $0.40 | $56.00 |

**Una sola key de fal.ai cubre imágenes FLUX + video Kling** → desbloquea las
tres rutas.

### Consistencia de personaje
FLUX.2 acepta hasta 8 imágenes de referencia. Se genera "Alejandro" una vez y
esa imagen se usa como referencia en los ~12 planos restantes. Sin esto salen
12 hombres canosos *parecidos pero distintos*, y se nota.

---

## 3. Estado de las API keys

**`.env` está vacío.** Es la plantilla `.env.example` sin tocar: cada variable
está en blanco y lo que sigue al `=` es el comentario. Verificado ejecutando
`azure_stt` y `dashscope_asr` — ambos responden "not configured".

**Herramientas disponibles sin ninguna key: 37.** Incluyen Remotion,
`subtitle_gen`, `remotion_caption_burn`, todo `video_post` (ffmpeg),
`pixabay_music`, `direct_clip_search`, `transcriber` y `piper_tts`.

**Sin key no hay:** generación de imágenes en la nube (0/16), generación de
video en la nube (0/26), TTS en la nube (solo Piper local).

---

## 4. La ASUS: GPU frenada al 6% — SIN RESOLVER

```
ASUS TUF Gaming F16 (FX608JMR) · BIOS 312 (jun 2026)
RTX 5060 Laptop 8 GB + Intel UHD (Optimus) · i7-14650HX · 32 GB RAM
```

**Síntoma:** bajo carga sostenida al 100%, la GPU se queda en **180 MHz de
3090** (6%), a 51 °C, con `SW Power Cap: Active` y una lectura de potencia
imposible de **430.59 W** (límite real: 115 W).

**Benchmark medido** (SDXL, 832×1216, 30 pasos, `enable_model_cpu_offload`):

```
carga del modelo    161 s
imagen en frío      364 s
imagen en caliente  350 s      ← debería ser ~20 s
pico de VRAM       5.20 GiB de 7.96
```

La **calidad de la imagen es buena y usable**. El problema es solo la velocidad.

### Descartado
- ❌ Térmico (51 °C, `HW Thermal Slowdown: Not Active`)
- ❌ VRAM (sobran 2.7 GB)
- ❌ Plan de energía de Windows (está en **Turbo**, con AC conectada)
- ❌ Driver — se actualizó 610.47 → **616.56** + reinicio. Sin cambio alguno.

### Causa probable
Fallo conocido de la plataforma. En el foro oficial de ROG hay reportes de
RTX 50 de laptop ASUS **clavadas exactamente en 180 MHz reportando 430 W** —
los dos mismos números.

Fixes reportados por otros usuarios:
1. **EC Reset** — el que más funcionó, pero temporal en varios casos
2. DDU + driver validado por ASUS
3. **RMA con cambio de placa** — un técnico lo atribuyó a metal líquido mal
   aplicado

### PENDIENTE: hacer el EC Reset
Procedimiento oficial ASUS: apagar, **dejar el cargador conectado**, mantener
el botón de encendido **40 segundos**, encender. Luego correr:

```bash
.venv/Scripts/python.exe projects/_analysis/gpu_bench.py
```

Ese script trae la línea base incrustada e imprime el multiplicador.
**OJO: está en `projects/`, que es gitignored — no viaja por git.**

### NO usar Ultimate/MUX todavía
El modo Ultimate tiene su propio bug documentado en laptops ASUS con RTX 50:
crashes reproducibles `0x116` / `0x117` (VIDEO_TDR_ERROR) al forzar solo-NVIDIA
por MUX. Dejarlo como último recurso.

### Evidencia para garantía
Notebookcheck probó **el mismo modelo FX608JMR con RTX 5060** en un estrés de
1 hora: **2714 MHz promedio a 110 W, 72 °C**. El de este equipo: **180 MHz a
51 °C**. Quince veces más lento, misma laptop, en frío.

### Atajo que funciona aunque no se arregle
Se usaron 30 pasos de difusión. **SDXL-Turbo y FLUX-schnell generan en 1–4
pasos** (~8× menos trabajo). Incluso con la GPU frenada eso baja la imagen de
350 s a **~45 s**. Lento pero usable: 20 imágenes = 15 min, $0.
**No se llegó a medir — es el siguiente experimento pendiente.**

---

## 5. Qué quedó instalado en la ASUS

```
torch 2.11.0+cu128     CUDA 12.8, sm_120 (Blackwell) reconocido
diffusers 0.40.0       SDXL base descargado en caché HF (~7 GB)
transformers 5.16.1
accelerate 1.14.0
faster-whisper 1.2.1   transcripción local, gratis, sin key
piper-tts 1.6.0        + voces es_MX-claude-high y es_ES-davefx-medium
                       (en .piper_voices/, ~126 MB)
pytest + requirements-dev.txt
remotion-composer      npm install hecho
```

**En el PC nuevo hay que reinstalar todo esto.** `make setup` cubre lo base;
el resto son estos `pip install` sueltos.

Nota: `piper_tts` solo aparece como disponible en el registry si
`.venv/Scripts` está en el `PATH` (el tool busca el comando `piper`).

---

## 6. Cambios del repo sin commitear

```
M  scripts/backlot_simulate_run.py   ← arreglo real, vale PR upstream
M  remotion-composer/package-lock.json
?? scratch_brief.json                ← temporal, borrable
```

**El arreglo de `backlot_simulate_run.py`:** el pull de 128 commits agregó la
etapa `proposal` al pipeline cinematic y la validación de prerrequisitos en
`lib/checkpoint.py`, pero el script de simulación nunca escribía ese checkpoint
y reventaba con `PREREQUISITE VIOLATION`. Se le agregó la etapa con su artefacto
`proposal_packet` (desde `sample_artifact`) y aprobación humana.

---

## 7. Siguiente paso

**Decisión abierta:** el usuario está migrando a un PC nuevo cuya GPU se
desconoce. Si esa máquina tiene una GPU funcional, **el problema de la ASUS deja
de ser bloqueante** y la generación local se muda allá.

**Al retomar:**

1. **Medir la GPU del PC nuevo** — ver sección 0. Es lo primero, antes de nada.
2. Decidir: ¿generación local en el PC nuevo, o key de fal.ai (~$2.40/ad)?
3. Elegir escenario nuevo para el primer ad usando la plantilla de la sección 1
4. **Producir una muestra de 15 s primero** (hook + un remate) antes del ad
   completo — cuesta centavos y valida voz, estilo y ritmo

**Reglas del repo que aplican** (ver `AGENT_GUIDE.md`):
toda producción pasa por un pipeline de `pipeline_defs/`, se lee el stage
director skill antes de cada etapa, y se leen las skills Layer 3
(`agent_skills`) antes de escribir cualquier prompt de generación.

---

## 8. Qué copiar aparte (no viaja por git)

- `1605777297927783.mp4` — el ad original, está en el Escritorio
- `projects/_analysis/gpu_bench.py` — solo si se va a seguir peleando con la ASUS
