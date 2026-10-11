# Asset Director - Concert Visuals Pipeline

## When To Use

After the scene plan and its look test are approved. Produce the raw material
the HyperFrames compositions will play: generated clips and stills used as
textures, 3D worlds, cut-out artist assets, fonts and logos.

Most concert scenes are **authored motion** (HTML/GSAP/Three.js/shaders in the
compose stage), so this stage is often light. Generate only what authored
motion cannot make: photographic textures, organic footage (smoke, liquid,
fabric), places.

## Prerequisites

- Approved `scene_plan` (with `metadata.reactivity`) and `brief`.
- Before calling any generation tool, read its Layer 3 skills (`agent_skills`
  in `get_info()`), plus `skills/creative/video-gen-prompting.md` and
  `skills/creative/image-gen-usage.md`.
- Announce tool, provider, model and sample-vs-batch before every paid call
  (AGENT_GUIDE "Decision Communication Contract").

## Process

### 1. Inventory per scene

From `scene_plan.scenes[].required_assets` list what each scene needs and
classify: **authored** (built in compose, no asset), **generated clip**,
**generated still**, **3D**, **user-supplied** (logos, artwork, band photos).

### 2. Generate for the wall, not for a phone

- **Resolution:** generators output ~720p-1080p. A 3840x1080 wall needs
  upscaling (`upscale`) or using the clip as a soft background layer under
  sharp authored graphics. Never stretch a 16:9 clip across a 32:9 wall —
  generate the wide composition (or tile/mirror deliberately).
- **Light level per genre:** dark genres → night, black backgrounds, single
  light sources. Caribbean genres → saturated colour, but still no daylight
  footage (it fights the stage lighting).
- **Artist photos:** low resolution is acceptable once cut out and treated
  (duotone / halftone / glow outline on a colour field). Cut out with
  `rembg` (`u2net_human_seg`, alpha matting) — run it in an **isolated
  venv**: rembg ≥2.0.80 requires numpy ≥2.3 and breaks packages pinned to
  numpy 1.x (chatterbox) in the project venv.
- **Motion for loops:** prompt for continuous, directionless motion (drifting
  smoke, rotating forms, slow push through a tunnel) — it loops more cleanly
  than motion with a start and an end.
- **Duration:** a 4-8 s generated clip covers a long scene by looping
  (ping-pong or crossfade loop) or by slowing it down; record the plan.
- **Text:** the generator never writes text — logos, song titles and lyrics
  are real typography added in compose. Prompts state "no text, no letters".
- **Consistency:** reuse the same style anchor and seeds across a bank; one
  world per song.

Sample first: generate one asset for the hero scene, show it, then batch.

### 3. Artist assets

Logos as SVG or high-res PNG with alpha (`bg_remove` if needed). Band photos
become silhouettes, duotones or textures — not literal portraits that compete
with the real artist on stage.

For the continuous-world engine: cut out every usable photo with rembg
(`u2net_human_seg`) in an **isolated venv** (installing rembg in the repo
`.venv` upgrades numpy to 2.x and breaks other tools), check the cutouts on a
flat colour, then run `engine/bake_images.py` to produce colour cutouts,
duotones per world colour, silhouettes (for the colour echo trails) and
`aspects.json`. Five or more different photos of the artist (different
poses/outfits) make the world feel alive; the user had more in `~/Downloads`
— ask before assuming there are only one or two. Use the artist's real logo
if one exists (its PNG may include a tagline: crop it).

### 4. Write the asset manifest

Each asset: `id`, `type` (`video`, `image`, `3d_world`, `font`, `lut`),
`path`, `source_tool`, `scene_id`, `prompt`, `seed`, `model`, `resolution`,
`duration_seconds`, `cost_usd`. Authored scenes need no entry.
`metadata.loop_plan[<asset_id>]` records how short clips cover long scenes.

### 5. Quality gate

- every non-authored scene has its assets on disk,
- assets survive at canvas resolution (inspect a 100% crop),
- no generated text anywhere,
- the bank reads as one world.

## Common Pitfalls

- Generating 40 clips before the look test is approved.
- Daylight, white-background stock footage on an LED wall.
- Expecting a 5 s clip to fill a 30 s section without a loop plan.

---

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review passes:
checkpoint with `status="awaiting_human"`, present the summary (the Backlot board renders
the artifact), and **END YOUR TURN**. Do not start the next stage in the same response.
Approval is per-gate — an earlier "go ahead" does not cover this gate.
