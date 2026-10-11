# Continuous World — the VJ Rauw language for LED visuals

Read this before designing any concert visual for Caribbean / Latin popular
music (vallenato, champeta, salsa, merengue, cumbia, urbano). It is the
distilled result of a full production ("La mitad de mi vida", Tiko Durán,
Oct 2026) that went through **eight rejected versions** before the user said
"me encanta". Each rule below exists because breaking it produced a version
the user rejected, so treat them as binding unless the user says otherwise.

Reference VJ: **VJ Rauw** (@vjrauw — Silvestre Dangond, Ana del Castillo,
Nelson Velásquez, Kvrass, Churo Díaz, Natalia Curvelo…). Study method:
`reference-research.md`. Working engine: `engine/` (this folder).

## 1. A world, not scenes (the core idea)

The single most important lesson. The user rejected — three times — versions
made of separate scenes joined by transitions, however good the scenes or the
wipes were ("siguen siendo cosas sueltas que se transicionan").

What Rauw does, read frame by frame at 12 fps:

- **One big board / collage that the camera travels across.** New elements
  appear because the camera moves over them or because they slide in *over a
  base that stays*. The base layer never changes all at once.
- **Elements enter and leave one at a time**, staggered, never a whole frame
  at once. At any moment something is entering, something is leaving and
  something is holding.
- **Transitions are made by an element of the composition**, not by an
  external wipe: a circle/blob/fist/heart that is already on screen **grows
  until it fills the frame and becomes the next background** (Silvestre intro:
  circles → blobs → fist silhouettes → the fist fills the frame white → red).
  Shapes morph in chains (circles become hearts) before the fill.
- **Layers above the fill persist across the change** (stickers, tags, cards),
  so the eye has continuity while the world changes colour underneath.
- **One colour world per piece**, lit differently per section (Silvestre:
  red/orange/black/white from start to end). Palette changes are re-lighting,
  not scene cuts.
- **Constant tilt** (~-10° to -13°) of the whole composition and a slow camera.

Implementation contract (see `engine/`): everything is a pure function of
**song time** — elements carry `t0/t1`, a base-colour track and a camera track
are global — so render windows join with no seam and a change in one place
re-renders only the windows it touches.

## 2. Camera and motion speed

Rejected: "la cámara se aleja de la acción" and "salen cosas volando rápido".

- Camera drift **8–20 px/s** (×energy). 80 px/s already leaves the action
  behind within a few seconds.
- Zoom only **pushes in** inside a world (≤ +0.25 %/s, cap ~1.12) and resets
  only **under a fill**, where the jump is hidden. Never zoom out on screen.
- Parallax depth factors 0.85–1.15 for foreground; 0.3–0.5 only for big
  background textures. Wider ranges make foreground fly off.
- Entrances: slide **≈500 px over 0.8 s** (expo-out) with a directional blur
  ≤ 16 px, or pop (back-out). Exits: ease-in (cubic) over 0.7 s, same
  distance. 1500 px in 0.5 s reads as "volando".
- Crossing typography 25–140 px/s. Never > 200 px/s.
- Bob/wobble amplitude 5–8 px.

## 3. Density

Rauw keeps **3–5 foreground elements** on screen. More reads as clutter and
kills the text.

- Hard cap: 4 foreground items (cutouts, cards, tapes, lines, stickers) alive
  at once; vertical name tags don't count.
- When a lyric hook is on screen, **clear the foreground** around it (±0.5 s),
  except the hook's own cutout.
- A world also needs **one anchor layer** that lasts the whole section (a
  giant tone-on-tone word drifting, a scrolling lockup card, a halftone field)
  so it never looks empty between entries.

## 4. Typography (the part that took the most iterations)

Rejected in order: plain centred lyric cards ("lyric video de YouTube"),
random words in Brush Script ("parecen Paint"), lyric blocks on black boxes
("no están tan modernos"). What Rauw actually does, read at full resolution:

- **Text sits directly on the colour field. Never in a box/band.** A black
  band behind a lyric = TV lower-third, not stage visual.
- **Two families only**: a heavy **display serif** for the name/hook lockup
  (Ana del Castillo's "ANA DEL CASTILLO" → we use **Ultra**) and an
  **ultra-condensed heavy sans** for everything else ("VÍVALO", "'TA BUENO",
  "SILVESTRE DANGOND" → **Anton**). Both are free Google Fonts, shipped in
  `engine/fonts/`. No Impact, no script/brush fonts for words.
- **Lockups with hierarchy**: BIG word + small superscript word + BIG word
  (`ANA` ^DEL / `CASTILLO`; ours: `LA MITAD` ^DE MI / `VIDA`), tight leading,
  lines slightly overlapping. Line 1 white, line 2 **the base colour
  darkened** (tone-on-tone), superscript in the accent colour.
- **Colour echo**: a duplicate of the lockup a few px behind, in the accent
  colour, entering ~0.1 s later. It is what makes the text feel printed/kinetic.
- Lines **rise from a mask** (each line, or each letter, slides up out of its
  own clip, staggered 0.03–0.11 s), with a slight skew that straightens.
- **Text is interleaved with images**: the artist cutout (or a fist, a
  dancer) passes **in front** of part of the word. Put the hook's cutout one
  z-level above the lockup.
- **Giant tone-on-tone word** (base colour ×0.6–0.8) bleeding off the frame
  as background texture, letters rising one by one.
- **Stacked repeated word inside a card** ('TA BUENO ×8), alternating two
  colours, scrolling slowly, with a scanline texture and a dark text stroke.
- **Vertical two-line name tag** (TIKO / DURÁN rotated -90°) stuck to a
  cutout, like "SILVESTRE DANGOND".
- **Torn tape labels**: condensed sans on white/yellow tape with a jagged
  clip-path, 2 in a short diagonal row, with deliberate copy per world (not
  random words).
- Lyrics are **few** (the 4–6 hooks of the song, verified against the audio
  alignment), short, and sized so the lockup fits ~1250 px wide. The visual
  accompanies the artist; it is never the protagonist.

## 5. Imagery

- Artist photos as **cutouts with colour echo trails** (2 silhouettes in the
  accent colours lagging the movement) — this is how stills read as motion.
  Real cutout video loops (dancers in Ana's show) are better; stills are the
  fallback.
- **Duotone** cards (ink → world colour → near white) with a white border,
  rotated a few degrees, floating at different depths.
- A **mosaic of duotone tiles** for long instrumentals, fixed to the camera
  (depth 0) with its own slow drift so the camera never leaves its edge.
- Line art drawn on and off (heart outlines, envelope-X boxes, scribbles) as
  connective tissue between states.
- The artist's **real logo** at intro and outro over the sun world.

## 6. Palette that worked

Yellow `#ffd23a` + a rotating partner (coral `#ff3b5c`, red `#e3103f`,
magenta `#e0168a`, orange `#ff7a1a`), ink `#1c0418`, white. The user picked
"the yellow with another colour" from the final dawn section of an early
version and it carried the whole show.

## 7. What was rejected (don't repeat)

| Version | Why it failed |
|---|---|
| Dark sea/moon cinematic | "demasiado lento, no es del género" |
| One template recoloured per section | "solo hay 2 tipos de escenas", static |
| 17 shader scenes (liquid, kaleidoscope, zebra waves) | "viaje psicodélico; lo moderno es más geométrico" |
| Equalizer bars | "parece un reproductor de música viejo" |
| 14 geometric Rauw-like scenes + shape wipes | still "cosas sueltas que se transicionan" |
| Lyric cards centred / on black boxes | lyric video / lower thirds, not stage visual |
| Brush Script words | "parecen Paint" |
| Fast camera, 1500 px slides | camera "se aleja"; things "volando" |
