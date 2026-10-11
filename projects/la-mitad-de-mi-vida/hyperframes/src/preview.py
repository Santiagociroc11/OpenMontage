"""Iteración rápida: fotos sueltas o un clip corto en borrador, en segundos en vez de minutos.

Los tiempos son de la canción (segundos desde el inicio del audio).

    .venv/bin/python projects/la-mitad-de-mi-vida/hyperframes/src/preview.py fotos 51,58,110,231
        -> PNG de cada instante + hoja de contacto (≈10-20 s, sin render de video)
    .venv/bin/python projects/la-mitad-de-mi-vida/hyperframes/src/preview.py clip 95 12
        -> MP4 borrador 15 fps con el audio de ese tramo (≈20-40 s para 12 s)
    ... preview.py clip 95 12 --fps 30      -> mismo clip a 30 fps (para revisar el pulso)

Salida en projects/<p>/renders/preview/. El render final sigue siendo render_show.py.
"""

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_show  # noqa: E402

PROJ = HERE.parents[1]
ROOT = HERE.parents[3]
WS = PROJ / "hyperframes" / "show_preview"
OUT = PROJ / "renders" / "preview"
TRACK = ROOT / "_audio_fuera_del_repo/La Mitad De Mi Vida - TIKO DURAN.wav"


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        sys.exit((r.stdout + r.stderr)[-2000:])
    return r


def build(start, dur):
    sys.argv = ["build_show.py", "preview", str(start), str(dur)]
    build_show.main()


def fotos(times):
    ts = [float(t) for t in times.split(",")]
    sm, _ = build_show.load()
    build(0, round(sm["duration_seconds"] + build_show.P.TAIL, 3))
    shot = OUT / "fotos"
    shutil.rmtree(shot, ignore_errors=True)
    run(["npx", "hyperframes", "snapshot", "--at", ",".join(f"{t:.3f}" for t in ts), "--no-end",
         "--output", str(shot)], cwd=WS)
    pngs = sorted(shot.glob("*.png"))
    cols = min(len(pngs), 3)
    rows = (len(pngs) + cols - 1) // cols
    sheet = OUT / "fotos.jpg"
    inputs = sum((["-i", str(p)] for p in pngs), [])
    labels = "".join(
        f"[{i}:v]scale=640:-1,drawtext=text='{ts[i]:.1f} s':x=12:y=12:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.6[v{i}];"
        for i in range(len(pngs)))
    pad = len(pngs) < cols * rows
    layout = "|".join(f"{(i % cols) * 640}_{(i // cols) * 360}" for i in range(len(pngs)))
    fc = labels + "".join(f"[v{i}]" for i in range(len(pngs))) + \
        f"xstack=inputs={len(pngs)}:layout={layout}" + (":fill=black" if pad else "")
    if len(pngs) == 1:
        fc = labels.rstrip(";").replace("[v0]", "")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs, "-filter_complex", fc,
         "-frames:v", "1", str(sheet)])
    return sheet


def clip(start, dur, fps):
    build(start, dur)
    raw, out = OUT / "clip_raw.mp4", OUT / f"clip_{start:g}s_{dur:g}s.mp4"
    run(["npx", "hyperframes", "render", "--output", str(raw), "--fps", str(fps),
         "--quality", "draft", "--workers", "auto", "--quiet"], cwd=WS)
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw), "-ss", f"{start}", "-t", f"{dur}",
         "-i", str(TRACK), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(out)])
    raw.unlink(missing_ok=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    f = sub.add_parser("fotos")
    f.add_argument("times")
    c = sub.add_parser("clip")
    c.add_argument("start", type=float)
    c.add_argument("dur", type=float)
    c.add_argument("--fps", type=int, default=15)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    res = fotos(a.times) if a.mode == "fotos" else clip(a.start, a.dur, a.fps)
    print(f"{res}  ({time.time() - t0:.0f} s)")
    subprocess.run(["open", str(res)])


if __name__ == "__main__":
    main()
