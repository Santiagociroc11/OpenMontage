# Publish Director - Concert Visuals Pipeline

## When To Use

After compose passes its checks. Nothing is uploaded: "publishing" a concert
visual means handing the show operator a package they can load and run
without calling you at soundcheck.

## Prerequisites

- `render_report`, `final_review` (status `pass`), the `brief`.

## Process

### 1. Show folder layout

```
projects/<p>/show/
  01_<song-slug>/
    masters/   01_<song>_<WxH>_<fps>p_<codec>.mov        (silent)
    review/    01_<song>_review.mp4                       (audio + timecode)
    loops/     01_<song>_<bank>_<NN>_<bars>bars_<bpm>bpm_<codec>.mov   (vj_loops)
  CUE_SHEET.md
  LOOP_INDEX.md      (vj_loops)
```

Names carry setlist position, resolution, fps, codec — and for loops, bank,
length in bars and BPM. An operator should know what a file is from its name.

### 2. Cue sheet

`CUE_SHEET.md`, one row per song in setlist order:

- file name, duration, resolution, fps, codec,
- **how to start it**: the sync source from `brief.metadata.sync_source`
  (`click` → triggered by the playback rig at bar 1 / sample 0; `timecode` →
  the LTC start time; `manual_go` → the cue the operator hits and where in the
  song),
- the canvas map: each screen region's x/y/w/h on the canvas,
- notes: the drop time, any blackout, the last frame (holds black or cuts).

### 3. Loop index (`vj_loops`)

`LOOP_INDEX.md`: per song, the banks (intro / groove / build / peak /
breakdown), each loop's file, bars, BPM and a one-line description, plus a
contact sheet of one frame per loop (`frame_sampler`). Suggest how to load
them: one Resolume layer per bank, clips in BPM-sync mode.

### 4. Publish log

One `entries[]` item per delivered file or package with `platform` =
the playback system (`resolume`, `media_server`, `qlab`, `usb_player`),
`status: "exported"`, `export_path`, `timestamp`, and `metadata_used` holding
resolution, fps, codec and duration.

### 5. Quality gate

- every song in the setlist has a master and a review copy,
- names follow the convention,
- the cue sheet explains the start of every file,
- the package was listed from disk (do not report files you did not check).

## Common Pitfalls

- Handing over only the review copies (wrong codec, audio inside).
- A cue sheet that says "press play" for a frame-locked song.

---

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review passes:
checkpoint with `status="awaiting_human"`, present the summary (the Backlot board renders
the artifact), and **END YOUR TURN**. Do not start the next stage in the same response.
Approval is per-gate — an earlier "go ahead" does not cover this gate.
