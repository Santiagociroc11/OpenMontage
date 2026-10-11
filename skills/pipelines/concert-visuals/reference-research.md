# Reference Research — how to study real stage visuals

The user expects the agent to look at **many** real references before
designing, and to look at them **as video**, not as a handful of thumbnails.
"Saca de cada historia unos 20–30 screenshots… quiero que veas como si fuera
el video." This is the method that worked.

## 1. Sources

- **YouTube** concert footage of the genre: `yt-dlp "ytsearch8:<artista> en vivo concierto 2025"`
  (`--flat-playlist --print "%(id)s | %(duration_string)s | %(title)s"` to list),
  then download at ≤360p video-only. Some return HTTP 403 — skip them.
  `--download-sections` needs ffmpeg the way yt-dlp expects; if it fails,
  download whole and cut locally.
- **The VJ's Instagram** — the gold. Reels download without login
  (`yt-dlp https://www.instagram.com/<user>/reel/<code>/`). The profile listing
  and the **story highlights** need the user's logged-in browser:
  - Use **Claude in Chrome** (the user's session). Collect post links by
    scrolling the profile and reading `a[href*="/reel/"], a[href*="/p/"]`.
  - Highlights: on the profile, read `a[href*="/stories/highlights/"]` for
    their ids. The private API (`/api/v1/feed/reels_media`) returns 500/429;
    instead **patch `window.fetch` and `XMLHttpRequest` to capture responses
    containing `video_versions`**, then click a highlight; the page loads the
    whole tray of highlights in a few responses. Walk the parsed JSON for
    objects with `video_versions` and group them by the highlight `title`.
  - Download each story video with `fetch(url) → blob → <a download>`; files
    land in `~/Downloads`.
  - Don't hammer the API: one 429 locks it for minutes; scrolling the profile
    still works.
- VJs show their best work in highlights where they film **their own
  After Effects / Resolume screen** — those are the most useful frames (the
  pure composition, no stage noise).

## 2. Seeing it as video

- Overview: 30 frames per story (`fps=30/<duration>`, tile 6×5).
- **Mechanics**: around every change, extract **12 fps** for 2 s and tile 6×4.
  That is the only way to see *how* a transition is made (which element grows,
  what persists, how text enters). Cropping matters: crop to the monitor/LED
  area so the frames aren't mostly room.
- **Typography**: pull single full-resolution frames of text moments and look
  at the letterforms, leading, colours and layering. Thumbnails hide that the
  text has no box, has an echo, and is behind a subject.
- Write down, per reference, **only what is on the LED** (VJ reels add
  overlays/frames that are not part of the show).

## 3. Record

Append findings to `projects/<p>/research/referencias_visuales.md` as a table
"show → what the wall shows", and keep contact sheets in
`research/ronda<N>/`. The conclusions that generalise belong in
`continuous-world.md`.
