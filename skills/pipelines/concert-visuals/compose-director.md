# Compose Director - Concert Visuals Pipeline

## When To Use

After `edit_decisions` exist. Build the HyperFrames compositions at the real
canvas size, render them, transcode to the show codec, and **prove** sync,
seamless loops and photosensitive safety before presenting.

## Runtime Routing (MANDATORY first step)

Read `edit_decisions.render_runtime`. It must equal
`brief.metadata.render_runtime`; a mismatch is a CRITICAL governance
violation — stop and ask. For `hyperframes`, read
`.agents/skills/hyperframes-core/SKILL.md` and
`.agents/skills/hyperframes-animation/SKILL.md` before writing HTML.

## Process

### 1. Build the workspace by hand

Concert compositions are authored (`index.html` you write), rendered with
`hyperframes_compose` `operation: "render_existing"` — the cut-template
`render` path cannot express beat reactivity.

- Root `data-width`/`data-height` = `brief.metadata.canvas` exactly. The
  renderer takes the size from the composition, so a wrong size here is a
  wrong master.
- Embed the timing data as JS, never analyse audio at runtime:
  - `BEATS` / `BARS` from the song map JSON (only the fields you use),
  - `AUDIO_DATA` from
    `.agents/skills/hyperframes-creative/scripts/extract-audio-data.py <track> --fps <fps> -o audio-data.json`
    for continuous band-driven motion.
- One paused GSAP timeline; beat hits are `tl.call`/`tl.to` at the beat times;
  band-driven motion uses the per-frame sampling pattern from
  `references/audio-reactive.md`. No `Math.random()` (seed a PRNG), no
  `Date.now()`.
- Every scene is a sub-composition (`hyperframes-studio` timeline rules).
- Run `operation: "check"` before every render; fix issues, do not skip.
- Decorative text (a lyric repeated as a background mosaic, outlined type)
  fails the WCAG contrast check by design. Mark those elements with
  `data-layout-ignore` instead of darkening them, and never use a fully
  transparent fill (`color: transparent` + stroke trips `text_not_painted`);
  use a 4% fill.
- Fonts: only families declared with `@font-face` and shipped in the
  workspace (`fonts/`). A CSS fallback like `Impact, sans-serif` fails lint
  (`font_family_without_font_face`). Load gsap/three from a local `vendor/`
  folder (npm-installed pinned versions), not a CDN.
- Long songs: drive everything from **song time**. Build the GSAP timeline in
  absolute song seconds and render windows with
  `main.add(song.tweenFromTo(S0, S0 + D), 0)`; shaders and per-frame
  data take `songStart + time`. Windows cut at exact frame boundaries then
  concatenate with `-c copy`.

### 1b. Continuous-world engine (Caribbean / Latin genres)

`engine/` in this folder is a working implementation of
`continuous-world.md`: `build_world.py --config <world.json> fotos|clip|show`.
It chunks the song in 12 s windows cached by content hash and renders 3 in
parallel with 4 Chrome workers each — the full 6:32 show takes ~2 minutes,
stills take seconds. Iterate with `fotos` at the exact seconds you changed,
including **mid-transition** frames; render `show --master` only to deliver.
Pin HyperFrames (`npx --yes hyperframes@0.8.145`): an automatic update in the
middle of a session broke every render with *Runtime checksum mismatch*.

Speed facts measured on an M3 Pro: draft quality + `--crf 12` is 2× faster
than `quality high` with near-identical output (SSIM 0.97); `--gpu` (VideoToolbox)
is *slower* and 10× bigger; `--no-browser-gpu` is 2.5× slower. Before
blaming the renderer, look at `top`: Spotlight indexing the renders took
~2 cores.

### 2. Render in sections

A 4-minute song at 3840x1080 is long to render and the tool times out at 30
minutes. For `song_sync`, render **one file per script section**: each
section's composition lasts exactly `end_frame - start_frame` frames (from the
song map at canvas fps), so the sections are contiguous. Join them losslessly:

```
ffmpeg -f concat -safe 0 -i sections.txt -c copy master_full.mp4
```

then verify the joined frame count equals `round(duration_seconds * fps)`.
Render `quality: "draft"` while iterating and `"high"` for the master.

For `vj_loops`, render each loop as its own file. Its frame count is
`round(loop_seconds * fps)`; when that is not an integer number of frames, put
the exact BPM in the filename — Resolume's BPM sync stretches the clip to the
tempo.

### 3. Transcode to the show codec

From the high-quality render (dimensions must be divisible by 4 for HAP):

```
# HAP Q (Resolume)
ffmpeg -i in.mp4 -c:v hap -format hap_q -an out_hapq.mov
# ProRes 422 HQ (media servers / QLab)
ffmpeg -i in.mp4 -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le -an out_prores.mov
```

Masters are silent (`-an`). Then the **review copy**: H.264 with the track
muxed and a burned timecode, used for approval only:

```
ffmpeg -i in.mp4 -i <track> -map 0:v -map 1:a -shortest -vf "scale=1920:-2,drawtext=timecode='00\:00\:00\:00':rate=<fps>:x=20:y=20:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.6" -c:v libx264 -crf 20 -c:a aac review.mp4
```

### 4. Verify (all mandatory)

1. **Format:** `ffprobe` each master — resolution equals the canvas, fps
   equals `canvas.fps`, codec as promised, no audio stream.
2. **Sync:** watch the review copy at the drop, at a late chorus and in the
   last 30 s. Drift that grows over time means a frame-count error in a
   section render — fix it, never nudge.
3. **Seamless loops:** for each loop, build a 3x repeat
   (`ffmpeg -stream_loop 2 -i loop.mov -c copy loop_x3.mov`) and check that the
   seams are invisible.
4. **Photosensitive check:** measure per-frame mean luma,
   ```
   ffmpeg -i master -vf "signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=luma.txt" -f null -
   ```
   and count, in every 1-second window, the number of bright flashes — a rise
   and fall of mean luma by 10% of full range or more. More than 3 in any
   window fails. This mean-luma proxy catches full-frame flashes but misses
   small, intense ones, so also scrub the hits by eye.
5. **Brightness vs. genre:** sample frames with `frame_sampler` across the
   song and compare mean luma with what the brief decided (dark genres:
   mostly near black; Caribbean genres: saturated colour, not washed-out
   grey, never large white areas).

Record results in `final_review.checks` (`format`, `sync`, `loops`,
`photosensitive`, `darkness`) and `render_report.verification_notes`. List
every master and review copy in `render_report.outputs` with `codec`, `fps`
and `resolution`.

## Common Pitfalls

- Rendering at 1920x1080 because the default profile was used.
- Muxing the song into the show master (the house doubles the music).
- One giant render that times out at minute 30.
- Accepting a loop because the first and last frames "look close" without
  watching it repeat.
