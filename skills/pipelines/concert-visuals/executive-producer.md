# Executive Producer — Concert Visuals Pipeline

## When to Use

You are the **Executive Producer (EP)** for a live-show visual. You run the
stages serially (idea → script → scene_plan (+ look test) → assets → edit →
compose → publish), review each director's output and send it back when it
fails the cross-stage checks below.

The pipeline has no research or proposal stage: the song is the brief's
backbone, and the look test replaces a written proposal as the proof of
direction.

## Why This Exists

Concert visuals fail in ways a single stage cannot see:

- a visual timed on a different master than the show plays drifts from bar 1,
- a 16:9 design stretched to a 32:9 wall loses everything important,
- a frame-locked video for a band that plays without click desyncs mid-song,
- a beautiful laptop preview washes out on an LED wall,
- strobing frames are a photosensitive-epilepsy risk to the audience,
- one long render times out, and a re-render with a frame miscount drifts.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Pipeline | `pipeline_defs/concert-visuals.yaml` | Stages, review focus, success criteria |
| Skills | The 7 director skills + `meta/reviewer` | Stage execution |
| Tool | `song_map` | Tempo, beats, bars, sections, drops — the clock of every stage |
| Layer 3 | `hyperframes-core`, `hyperframes-animation`, `hyperframes-creative/references/audio-reactive.md` | Composition rules and beat reactivity |

## Cumulative State

```
EP_STATE:
  pipeline: concert-visuals
  production_mode: song_sync | vj_loops
  canvas: {width, height, fps}
  delivery: {playback_system, codec}
  tracks: [{title, audio_path, song_map_path}]
  render_runtime: hyperframes
  look_test_approved: false
  budget_total_usd / budget_spent_usd
  revisions: {<stage>: n}
```

## Cross-Stage Checks

### After IDEA
- `song_map` JSON exists for every track and was made from the show's playback audio.
- Mode matches the answer to "click or no click?"; a `tempo_note` of "drifts" with `song_sync` → send back.
- Canvas is the venue's pixel map or explicitly provisional.

### After SCRIPT
- Section boundaries are song_map downbeats (spot-check 3 against `bars`).
- The drop entered by `song_map.drops[0]` has the biggest visual change; breakdowns have space.
- Repeated sections share motifs.

### After SCENE_PLAN
- Every scene has a `metadata.reactivity` entry.
- Stage rules (brightness per genre, rare white, ≤ 3 flashes/s, safe zones) are in the scene notes.
- The genre research (contact sheet + "what the wall shows" table) exists before any world is proposed.
- **The look test was rendered at full canvas and approved by the user.** No
  asset batch before that.

- For Caribbean / Latin genres the plan is a **continuous world**
  (`continuous-world.md`): sections are worlds of one colour family, changes
  are made by fills, not by scene wipes; ≤ 4 foreground items; lyrics only on
  verified hooks.

### After ASSETS
- Assets hold at canvas resolution; no generated text; one world per song.

### After EDIT
- Every boundary is a song_map time; `song_sync` total = track duration to the frame.
- `render_runtime` unchanged from the brief.

### After COMPOSE
- `final_review.checks` has `format`, `sync`, `loops` (vj_loops), `photosensitive`, `darkness`, all passing.
- Masters silent, review copies with audio and timecode.

## Feedback Templates

**To Script Director:** "Section <id> starts at <t>, which is not a downbeat
in song_map.bars (nearest: <t1>, <t2>). Move it to one of them."

**To Scene Director:** "Scene <id> has no reaction to the music. Define
on_kick / on_downbeat / continuous from the song map."

**To Compose Director:** "Review copy drifts by <n> frames at <t>. Section
frame counts must equal end_frame - start_frame; re-render the section, do not
offset the video."

## Execution Limits

- Max 3 revisions per stage, 3 send-backs in total; then escalate to the user.
- Paid generation only after the look test is approved; announce every paid call.
- Stop at every human gate the manifest declares.

## Common Pitfalls

- Iterating on full renders. Iterate with `engine/build_world.py ... fotos`
  (seconds) and short `clip`s; render the full show only to deliver.
- Defending a version the user called boring/psychedelic/"Paint" instead of
  going back to the references at 12 fps (`reference-research.md`).

- Treating the look test as optional.
- Accepting "it looks in sync" on a preview without audio.
- Letting a director change mode, canvas or runtime without a logged decision.
