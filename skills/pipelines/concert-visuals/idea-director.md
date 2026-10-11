# Idea Director - Concert Visuals Pipeline

## When To Use

The deliverable plays **behind a live performance**: LED wall, projection,
side screens, a DJ booth facade. The audience watches the artist; the visual
sets the world around them. This is not a music video (no story, no lip-sync,
no cutaways to the singer) and not a lyric video (lyrics are rare accents).

If the user wants something to post on social media *about* the song, that is
a music video or a promo — route to `cinematic` or `animation` instead.

Your job: turn the request into a schema-valid `brief` whose `metadata` locks
the four things every later stage depends on — **mode, canvas, delivery and
song map**.

## Process

### 1. Get the track(s) and map them first

The music is the input. Ask for the exact audio the show will play (the
playback stem or the mastered track), not a YouTube rip of a different mix —
a different master shifts every beat.

Run `song_map` on every track before writing anything:

```
song_map(input_path=<track>, output_path="projects/<p>/song_map/<slug>.json", fps=<canvas fps>)
```

Read the result and tell the user, in one short block per song:
tempo, `tempo_note`, number of sections, where the biggest drop is, and
`section_dynamic_range_db` (under ~2 dB means a flat, compressed track whose
energy arc must come from the visuals, not from the mix).

### 2. Pick the production mode — ask how the band plays

**Decision question:** *"Does the show play this song to a click / playback
rig, or does the band play it live and free?"*

| Answer | Mode | Why |
|---|---|---|
| Click, backing stems, Ableton, DJ playing a fixed edit, walk-on intro | `song_sync` | The playback starts at a known instant; a frame-locked video can start with it |
| Live band without click, jam sections, improvised lengths | `vj_loops` | Tempo drifts; a fixed-length video desyncs within a minute. A VJ rides loops |
| Live band without click **and nobody operating playback** | `free_run` | One video someone starts with the song; it must survive a different tempo and length every night |
| `song_map` says "tempo drifts" for a supposedly clicked song | ask again | The file may be a live recording rather than the show playback |

`vj_loops` needs someone triggering loops (a VJ, or an operator pressing GO
per section). Ask who will; if nobody, it is `free_run`.

Record in `brief.metadata.production_mode`. Every mode needs `song_map`: in
`vj_loops` it gives loop lengths (`loop_lengths_seconds`) and the energy banks;
in `free_run` it gives the arc (section order, relative lengths, energy) that
the live performance will follow approximately.

**`free_run` rules** (record them in the brief): the live song will differ by
several seconds per section and in total length, so

- transitions between sections are long dissolves (2+ bars) placed at the
  recording's section times — close enough, never a hard cut that "should" hit;
- no flash, cut or lyric that must coincide with a specific beat or word;
- motion can breathe at roughly the song's tempo, but softly (a visibly
  locked pulse drifting off the band looks worse than no pulse);
- the ending is a holdable state (an extra 30-60 s of the final image that
  loops cleanly), so the video never ends before the band does.

### 3. Lock the canvas — never assume 1920x1080

Ask for the venue's **pixel map** (the LED processor's input resolution) or the
projector resolution, and how it is split:

- one wall (e.g. 3840x1080, 7680x2160, 1920x1080),
- centre wall + side screens (one wide canvas sliced into regions),
- odd shapes (columns, a booth facade): render one canvas, document each
  region's x/y/w/h so the media server can map it.

Record `brief.metadata.canvas = {width, height, fps, screens: [...], safe_zones}`.
`fps` is 30 or 60 (the HyperFrames renderer supports 24/30/60); match the
playback system. Safe zones: the artist's silhouette (usually centre, lower
two-thirds), the bottom strip hidden by the stage/monitors and the top hidden
by truss — ask, or default to keeping key content out of the bottom 15%.

If the user has no pixel map yet, propose 3840x1080 for a wide wall or
1920x1080 for a single screen, and **mark it provisional** in the brief.

### 4. Lock the delivery

| Playback system | Codec | Audio in master |
|---|---|---|
| Resolume / VJ software | HAP (HAP Q for gradients, HAP Alpha for overlays) `.mov` | no |
| Media server (disguise, Pixera, Watchout) | ProRes 422 HQ `.mov` (or what the server asks for) | no |
| QLab / laptop playback | ProRes 422 or high-bitrate H.264 | no |
| USB stick into an LED controller | H.264 MP4 at the controller's limits | ask |

Show masters are **silent**: the audio comes from the band's rig. Every master
also gets a **review copy** with the track muxed in, used for approval and
sync checks. Record `brief.metadata.delivery`.

### 5. Runtime selection

Default `render_runtime = "hyperframes"`. Concert visuals need per-frame
determinism (a beat at 83.427 s must land on frame 2503 every render), custom
canvases, Three.js / shaders and audio-reactive sampling — HyperFrames does
all of these from `index.html`. Remotion is viable only for stitching
pre-rendered clips; per AGENT_GUIDE.md present both if both are available,
recommend HyperFrames, and log it in `decision_log` under
`render_runtime_selection`. Mirror the choice into
`brief.metadata.render_runtime`.

### 6. Research the genre's real stage screens FIRST

Do not design from generic "concert visuals" taste. Before proposing worlds,
look at 10+ live shows of the **same genre** (YouTube concert videos, and the
Instagram of the VJs who work that circuit) and write down, per show, **only
what is on the LED wall** — reels from VJs often add their own overlays,
frames and captions on top of the show footage; those are not the stage
visual and must not be copied. Save captures and a contact sheet in
`projects/<p>/research/` and a table "show → what the wall shows".

**How** to research (yt-dlp, the VJ's Instagram highlights through the
user's logged-in Chrome, 30 frames per story, 12 fps around every change,
full-resolution frames for typography): `reference-research.md`. The user
expects many references studied *as video*, not a few thumbnails.

Lesson from the first real run (vallenato / champeta, Oct 2026): a dark,
contemplative, cinematic sea-and-moon look was rejected as too slow and
off-genre. Caribbean popular genres (vallenato, champeta, merengue, salsa,
cumbia) use **saturated full-wall colour** (one colour world per piece,
re-lit per section), **typography as texture and lockups, with lyrics as
rare accents** (the visual accompanies the artist — it is never a lyric
video), **pop illustration** (stickers, hearts, stars,
neon outlines, Britto-style colour blocks), **the artist's photo cut out** in
duotone, and **constant motion at the song's tempo**. Ask the user for
reference artists/VJs if unsure (e.g. VJ Rauw — @vjrauw — Silvestre Dangond's
VJ, is a reference for this circuit).

### 7. Find the visual world

For Caribbean / Latin popular genres, the approved language is the **continuous
world** of VJ Rauw — read `continuous-world.md` before proposing anything.
It lists the eight looks that were rejected on the first real run and why.

Ask about the artist and the song, not about "visuals": genre, album artwork,
the show's lighting colours, what the song is about, any existing show
references. Propose **2-3 worlds** that differ in kind, for example:

- graphic (typography, geometric systems, the artist's logo as architecture),
- material (smoke, liquid metal, ink, fabric under wind),
- place (a desert road at night, an endless tunnel, a city from above).

Read `.agents/skills/hyperframes-creative/references/audio-reactive.md`
before proposing: equalizer bars, spectrum analysers, waveforms, rainbow
cycling and generic particle orbs are banned. The audio drives *behaviour*,
the world comes from the song.

### 8. Build the brief

Schema fields: `title` = song (or show) name, `hook` = the one image the
audience remembers, `key_points` = 3-5 visual pillars, `tone`, `style` = the
chosen world, `target_platform = "generic"`, `target_duration_seconds` = track
duration (`song_sync`) or the loop pack's total running time (`vj_loops`).

`metadata` keys:

- `production_mode`
- `tracks`: `[{title, audio_path, song_map_path, setlist_position}]`
- `canvas`, `delivery`, `render_runtime`
- `sync_source`: `click` | `timecode` | `manual_go` | `none`
- `artist_assets`: logos, fonts, artwork the user supplied
- `lighting_palette`: the show's lighting colours if known (the wall must not fight them)
- `notes_for_script`

### 9. Quality gate

- the mode matches how the song is really played,
- the canvas is the real pixel map or explicitly provisional,
- every track has a `song_map` JSON on disk,
- the world is specific to this artist and song.

## Common Pitfalls

- Making a 16:9 music video when the wall is 32:9 — everything important ends
  up off-wall or tiny.
- Frame-locking a song the band plays without click.
- Mapping a different master than the one the show plays.
- Promising audio inside the show file: the house would double the music.

---

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review passes:
checkpoint with `status="awaiting_human"`, present the summary (the Backlot board renders
the artifact), and **END YOUR TURN**. Do not start the next stage in the same response.
Approval is per-gate — an earlier "go ahead" does not cover this gate.
