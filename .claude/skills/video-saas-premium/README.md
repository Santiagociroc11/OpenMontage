# video-saas-premium

Skill para **Claude Code** y **Codex** que convierte **el link de tu producto + una idea** en un video de lanzamiento con nivel de estudio (estilo Apple / Figma), renderizado en **4K a 60 fps**:

```
tu link → marca → concepto → capturas reales → UI + 3D + tipografía → voz en off → música → efectos → video 4K
```

Guía completa y video de ejemplo: **[rayyan.contapro.lat/skills/video-saas-premium](https://rayyan.contapro.lat/skills/video-saas-premium)**

Le dices *"hazme un video saas de https://tuproducto.com"* y el agente hace el resto, preguntándote en los momentos que importan (qué concepto, qué capturas, qué voz, qué música).

## Qué la hace distinta
- **La interfaz es la real**: te pide capturas de tu producto y las recrea 1:1. Nada de dashboards genéricos ("AI slop").
- **Cámara tipo Screen Studio**: zoom in a cada acción, zoom out para mostrar todo, warp líquido entre estados.
- **3D real con Three.js**: iPhone con tu UI en vivo en la pantalla, tu logo extruido.
- **Tipografía con barridos de movimiento**, palabra por palabra.
- **Voz en off de ElevenLabs sincronizada palabra por palabra** con lo que se lee, y música que se abre justo cuando llega la solución.
- **Un proceso creativo** que busca una idea verdadera sobre tu producto antes de animar nada.

## Qué necesitas
- **Claude Code** o **Codex**.
- **Node 22+**, **ffmpeg**, **Google Chrome** (o Chromium), **Python 3** con `numpy` y `Pillow` (`pip3 install numpy pillow`).
- Opcional: una cuenta de **ElevenLabs** (voz y música) y un **pack de efectos de sonido** propio.

## Instalar

Descarga `video-saas-premium.zip` desde [rayyan.contapro.lat/skills/video-saas-premium](https://rayyan.contapro.lat/skills/video-saas-premium) y descomprímelo en la carpeta de skills de tu agente:

**Claude Code**
```sh
unzip ~/Downloads/video-saas-premium.zip -d ~/.claude/skills/
```

**Codex**
```sh
unzip ~/Downloads/video-saas-premium.zip -d ~/.codex/skills/
```

Debe quedar `~/.claude/skills/video-saas-premium/SKILL.md` (o `~/.codex/skills/...`). Reinicia el agente después de instalar.

## Usar

Abre una carpeta vacía en el agente y escribe:

> hazme un video saas de https://tuproducto.com

El agente:
1. **Saca tu marca** de la web (colores, tipografías, logo, textos reales).
2. **Te propone 2–3 conceptos** distintos y tú eliges.
3. **Te pide capturas** de las pantallas clave (⌘⇧4 + Espacio en Mac) para recrear tu UI tal cual.
4. **Construye y revisa** el video con snapshots de cada escena.
5. **Voz**: te pasa muestras de varias voces y eliges escuchando; luego la sincroniza palabra por palabra.
6. **Música**: te pasa 3 estilos, eliges uno y lo adapta al video.
7. **Efectos**: si tienes un pack, elige los mejores con `scripts/sfx_curate.py`.
8. **Renderiza en 4K** y te abre el archivo.

### ElevenLabs (opcional)
Tu API key **nunca** se pega en el chat. Guárdala una vez en tu llavero:

```sh
# macOS
security add-generic-password -U -a "$USER" -s elevenlabs-api-key -w 'sk_...'
# Linux / Windows
export ELEVENLABS_API_KEY=sk_...
```

### Efectos de sonido (opcional)
La skill no trae sonidos (sus licencias varían). Elige los mejores de tu propio pack:

```sh
python3 ~/.claude/skills/video-saas-premium/scripts/sfx_curate.py --src ~/Downloads/MiPack --out assets/sfx/premium
```

## Qué hay dentro
- `SKILL.md`: el flujo que sigue el agente.
- `references/`: proceso creativo, capturas de UI, look premium, voz y música, efectos, API del kit, errores comunes.
- `kit/`: helpers de animación para [HyperFrames](https://hyperframes.heygen.com) (GSAP + Three.js).
- `scripts/`: extraer la marca, voz con ElevenLabs, post de audio y selección de efectos.
- `examples/starter/`: composición mínima de partida.

## Licencia
Código bajo licencia MIT. Las tipografías, sonidos, voces y música que uses son de sus autores: revisa sus licencias (SF Pro de Apple no se puede redistribuir; Inter y Geist son OFL).

Hecha por [Rayyan](https://rayyan.contapro.lat).
