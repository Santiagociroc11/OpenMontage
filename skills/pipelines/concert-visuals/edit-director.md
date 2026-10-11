# Edit Director - Concert Visuals Pipeline

## When To Use

After assets are approved. Turn the scene plan into `edit_decisions`: the
exact timeline the compose stage will build, with every time taken from the
song map.

## Prerequisites

- `scene_plan`, `asset_manifest`, `script`, the song map JSON, the `brief`.

## Process

### 1. Cuts on the music

- Every `in_seconds`/`out_seconds` boundary of a cut is a time from
  `song_map.beats` or `song_map.bars` — copy the number, do not round it.
- Scene changes go on downbeats; hits inside a scene go on beats.
- A transition that "lands" on a downbeat **starts before it**: the
  transition's end sits on the beat (`transition_duration` back from it).
- Cut density follows energy: verses change on phrases (4-8 bars), drops can
  change every bar, almost never every beat for more than a few bars.

### 2. Timeline per mode

- `song_sync`: one continuous timeline from 0.000 to the track's
  `duration_seconds`. No gaps — a gap is a black flash on the wall. The last
  cut ends exactly at the track's end.
- `free_run`: like `song_sync` (cuts at the recording's section times from
  the song map) plus the tail; every section change is a dissolve of at least
  2 bars and nothing is a hard cut on a beat. Total = track + tail.
- `vj_loops`: one timeline **per loop**, each starting at 0 and lasting exactly
  N bars (`song_map.loop_lengths_seconds`). Store them as cuts with
  `source` = the loop's scene id and `reason` naming the bank; the compose
  stage renders each loop as its own file.

### 3. Fields

Each cut: `id`, `source` (asset id, or the scene id for authored scenes),
`in_seconds`, `out_seconds`, `layer` (`background` for textures, `primary`
for the world, `overlay` for logo/lyric hits), `transition_in`/`out`,
`reason` (which beat/section it serves).

Top level: `render_runtime` carried unchanged from
`brief.metadata.render_runtime`; `renderer_family = "animation-first"`. No `music`, `subtitles` or narration
`audio`: the show master is silent. Record the track in
`metadata.review_audio` (muxed only into the review copy), plus
`metadata.song_map_ref` and `metadata.reactivity_ref`.

### 4. Quality gate

- every boundary time exists in the song map,
- `song_sync` total duration equals the track to the frame,
- loops are exact bar multiples,
- `render_runtime` unchanged.

## Common Pitfalls

- Re-timing by "what looks right" in a preview without audio — always check
  against the song map.
- Leaving a 1-frame gap between cuts: on a black stage it reads as a flicker.
