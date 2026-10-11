# Script Director - Concert Visuals Pipeline

## When To Use

After the brief is approved. There is no narration: the "script" here is the
**visual arc of the song** — one script section per song section, each saying
what the wall does and why. It is the contract that ties every later visual
decision to a time the music actually provides.

## Prerequisites

- Approved `brief` with `metadata.tracks[].song_map_path` on disk.
- Read the song map JSON — do not re-derive times by ear.

## Process

### 1. Name the sections

`song_map.sections` gives boundaries snapped to downbeats, local `tempo_bpm`,
`energy_db` (0 = loudest section) and `most_similar_to`. Turn them into
musical roles: `intro`, `verse`, `pre`, `chorus`, `drop`, `breakdown`,
`bridge`, `outro`.

- High `most_similar_to.similarity` against an earlier section → the same part
  again (chorus 2 of chorus 1). Give it the same role.
- The section entered by `drops[0]` is the peak of the song.
- The algorithm can merge or split parts. Listen-check against the user's
  knowledge of the song ("the drop starts at 1:12?") and **move a boundary
  only to another downbeat from `song_map.bars`** — never to a rounded time.

If the song has lyrics that the visuals will quote, run `transcriber` with word
timestamps on the track (or the vocal stem) and take lyric times from it.

### 2. Shape the visual arc from the energy, not against it

The wall's intensity should track the music's: brightness, scale, cut density,
colour saturation and motion speed go up with `energy_db` and peak at the drop.

| Section role | Wall behaviour |
|---|---|
| intro | sparse, the world revealed quickly (artist logo / song title); often one element |
| verse | the world established, motion on the groove (kick/snare), restrained palette |
| pre / build | tension: things accelerate, tighten, rise; withhold the payoff |
| chorus / drop | the biggest change of the song: palette shift, scale jump, new layer, cut density up |
| breakdown | negative space, slow, near-black; let the artist own the moment |
| bridge | a variation — same world, new angle |
| outro | resolve or dissolve; end on black at the last downbeat (or the final hit) |

When `section_dynamic_range_db` is small (a flat, loud master), the arc still
has to exist — create it with density and palette rather than brightness.

**Repetition is a feature.** Chorus 2 reuses chorus 1's motif and escalates it
(more layers, bigger scale). Audiences read a recurring motif as "this is the
chorus"; a new idea every section reads as random.

### 3. Mode specifics

- `song_sync`: sections cover the whole track, from 0 to `duration_seconds`.
  The first section starts at 0 even when the first beat is later (the video
  starts with the playback).
- `free_run`: sections follow the recording like `song_sync`, plus a final
  `tail` section (30-60 s) holding the closing image. Section times are
  guides: the live band will arrive earlier or later, so each section's
  visual intent must read correctly over a window of several seconds.
- `vj_loops`: each section is an **energy bank** (intro, groove, build, peak,
  breakdown) sourced from a representative song section. Use that song
  section's times for `start_seconds`/`end_seconds`, and put the loop length in
  bars in `label` (e.g. `peak - 8 bars`). Loop lengths come from
  `song_map.loop_lengths_seconds`; 8 bars is the default, 4 for builds.

### 4. Write the script artifact

Each section:

- `id`: the song_map section id (`s01`...) or bank name
- `label`: role (and loop length for `vj_loops`)
- `text`: the visual intent in one or two sentences — what the audience sees
  and how it moves with the music
- `start_seconds` / `end_seconds`: from `song_map`, unchanged
- `enhancement_cues`: hits worth a dedicated moment inside the section
  (`type: "animation"`, `timestamp_seconds` = a beat time from the map) — the
  first downbeat of the drop, a lyric line, a stop

`total_duration_seconds` = track duration (`song_sync`) or the sum of loop
lengths (`vj_loops`). `metadata`: `song_map_ref`, `motifs` (motif name → the
sections that use it), `lyric_moments`.

### 5. Quality gate

- every boundary is a `song_map` downbeat (within one frame at canvas fps),
- the drop gets the biggest visual change,
- repeated sections share motifs,
- the arc has rests — no four-minute peak.

## Common Pitfalls

- Rounding times (`72.0` instead of `71.957`): at 120 BPM a 43 ms error is a
  visible miss on an LED wall.
- Writing scenes, not sections: one section can hold several scenes, which is
  the scene director's job.
- Peak intensity everywhere: if everything flashes, nothing does.

---

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review passes:
checkpoint with `status="awaiting_human"`, present the summary (the Backlot board renders
the artifact), and **END YOUR TURN**. Do not start the next stage in the same response.
Approval is per-gate — an earlier "go ahead" does not cover this gate.
