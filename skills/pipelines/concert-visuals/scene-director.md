# Scene Director - Concert Visuals Pipeline

## When To Use

After the script (the song's visual arc) is approved. Break each section into
scenes, define **how each scene reacts to the music**, and prove the look with
an 8-bar look test before anything expensive is generated.

## Prerequisites

- Approved `script`, the `brief` (canvas, mode, world) and the song map JSON.
- Read `.agents/skills/hyperframes-creative/references/audio-reactive.md` and
  `.agents/skills/hyperframes-creative/references/beat-direction.md`.

## Process

> **Caribbean / Latin popular genres: read `continuous-world.md` first.**
> There, "scenes" are *worlds*: elements on a song-time timeline over a
> persistent base, a slow camera, and fills that turn one world into the
> next. Steps 1–5 below still apply (sections, reactivity, stage rules, look
> test), but a scene is not a separate picture joined to the next by a
> transition — the user rejected that approach three times.

### 1. Scenes inside sections

A section of 8-16 bars usually holds 1-4 scenes. Scene boundaries are bar
lines (`song_map.bars`); phrase changes every 4 or 8 bars are the natural
places. Keep the scene count low in quiet sections and higher in peaks.

Scene fields: `type` is `animation` for HTML/GSAP/Three.js worlds, `generated`
for AI clips or stills used as textures, `text_card` for logo or lyric
moments, `transition` for a dedicated hit between sections. Use
`script_section_id`, `hero_moment: true` for the drop entry and the logo hit,
`narrative_role` (`establish_context` intro, `build_tension` pre,
`deliver_payload` drop, `emotional_beat` breakdown, `resolution` outro).

### 2. Define the reaction for every scene

A concert visual without a beat reaction looks like a screensaver. Store one
entry per scene in `scene_plan.metadata.reactivity[<scene_id>]`:

- `on_kick`: what pulses (scale 2-8% on large shapes, exposure lift, camera nudge)
- `on_downbeat`: what changes every bar (a cut, a colour step, a new element)
- `on_phrase`: what changes every 4/8 bars
- `continuous`: what is driven by per-frame bands (bass → swell, highs → sparkle/contrast)
- `hits`: the `enhancement_cues` from the script, with their exact beat times

Beat times come from `song_map.beats` (filter `beat_in_bar == 1` for
downbeats); per-frame bands come from
`.agents/skills/hyperframes-creative/scripts/extract-audio-data.py`. Both are
pre-extracted — never analyse audio at render time.

In `free_run`, drop `on_kick` and `hits` that depend on one beat: keep
`continuous` (bands) and slow `on_phrase` changes only. Audio data from the
recording drives motion intensity but the live band will not match it frame by
frame, so reactions must read as "breathing", not as a sync promise.

Strong `beats[].strength` values mark real accents; on a quiet bar a pulse on
every beat looks mechanical. Scale reaction intensity with section energy.

### 3. Stage rules (write them into each scene's `overlay_notes`)

- **Brightness follows the genre, not a fixed rule.** For electronic,
  rock and cinematic shows, dark by default (black = LEDs off; the artist and
  lighting pop). For Caribbean popular genres (vallenato, champeta, salsa,
  merengue, cumbia) the wall IS a light source: saturated full-wall colour,
  one dominant colour per section. Measured on an approved look: mean luma
  ~20-40% of full range. Decide from the genre research in the idea stage.
- **Full white is a weapon** in any genre, used a handful of times per song.
  Large bright white areas blind the audience and wash out the stage lighting.
- **Photosensitive safety (hard rule):** no more than 3 bright flashes in any
  1-second window, and no saturated red flashing. Fast strobing belongs to the
  lighting desk, not the wall.
- Keep key content out of the safe zones in `brief.metadata.canvas`
  (artist silhouette, floor and truss cut-offs).
- On multi-screen canvases, design across the whole canvas but make each
  screen region read on its own.
- Typography: big, few words, heavy weights; thin type disappears on LED pitch.
  Text goes on the colour field, never in a box; two families (display serif
  for lockups, ultra-condensed sans for the rest); see `continuous-world.md` §4.

### 3b. Speed

Users of this pipeline ask for "more speed / more movement" — the first look
test is almost always too slow. Tie motion to the song's tempo (local BPM from
`song_map`, not the track mean): background layers cycle every 1-2 beats,
pulses every beat, kinetic words stagger at 1/4 beat, a full rotation per
bar for decorative stars. In `free_run` keep it continuous (cosine breathing,
streaming) instead of hard hits — it reads "on tempo" even when the live band
drifts.

### 4. VJ loops

For `vj_loops`, every scene is a loop:

- length is exactly N bars (`song_map.loop_lengths_seconds`), and all motion
  is periodic over that length, so the frame after the last one equals frame 0
  (cyclic easings, rotations of 360°/N, noise sampled on a circle);
- plan 3-6 loops per energy bank so the VJ can vary them, plus 1-2 short
  transition hits (1 bar) per bank;
- loops of the same bank share palette and camera language.

### 5. Look test (sub-stage, mandatory)

Before the asset stage, build a HyperFrames workspace at the full canvas size
for **8 bars of the peak section** (the section entered by `song_map.drops[0]`)
and render it with `hyperframes_compose` (`operation: render_existing`,
`quality: draft`), then mux the track for review:

```
ffmpeg -i look.mp4 -ss <section_start> -i <track> -map 0:v -map 1:a -shortest -c:v copy -c:a aac look_review.mp4
```

The test proves the world, the palette and the beat lock. Present it, checkpoint
the sub-stage with `awaiting_human`, and stop until the user approves.

### 6. Quality gate

- every script section has at least one scene,
- every scene has a reactivity entry,
- loop scenes are exact bar multiples,
- the look test was approved.

## Common Pitfalls

- Pulsing everything on every beat for the whole song.
- Designing on a 16:9 preview and stretching it to the wall.
- Bright gradients that look great on a laptop and wash out on LEDs.
- Skipping the look test and discovering the world does not work after
  generating 40 clips.

---

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review passes:
checkpoint with `status="awaiting_human"`, present the summary (the Backlot board renders
the artifact), and **END YOUR TURN**. Do not start the next stage in the same response.
Approval is per-gate — an earlier "go ahead" does not cover this gate.
