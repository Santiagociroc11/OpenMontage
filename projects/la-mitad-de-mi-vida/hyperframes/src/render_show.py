"""Render completo del show: 4 tramos -> unión -> masters -> copia de revisión -> verificación.

Log con hora en projects/<p>/renders/render_show.log. Uso (desde la raíz del repo):
    .venv/bin/python projects/la-mitad-de-mi-vida/hyperframes/src/render_show.py
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_show  # noqa: E402
from tools.tool_registry import registry  # noqa: E402

PROJ = ROOT / "projects/la-mitad-de-mi-vida"
HF = PROJ / "hyperframes"
OUT = PROJ / "renders"
LOG = OUT / "render_show.log"
TRACK = ROOT / "_audio_fuera_del_repo/La Mitad De Mi Vida - TIKO DURAN.wav"
FPS = 30


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def ff(*args, cwd=None):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], capture_output=True, text=True, cwd=cwd)
    if r.returncode:
        raise RuntimeError(r.stderr[-800:])


def frames(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v",
                        "-show_entries", "stream=nb_read_frames,width,height,codec_name",
                        "-of", "json", str(path)], capture_output=True, text=True)
    return json.loads(r.stdout)["streams"][0]


def main():
    OUT.mkdir(exist_ok=True)
    LOG.write_text("", encoding="utf-8")
    sys.argv = ["build_show.py"]
    build_show.main()
    registry.discover()
    hf = registry.get("hyperframes_compose")
    n = len(build_show.CHUNK_FRAMES)
    parts = []
    t_all = time.time()
    # Revisión previa de los 4 tramos (≈10 s cada uno) antes de gastar minutos en render.
    for i in range(1, n + 1):
        c = hf.execute({"operation": "check", "workspace_path": str(HF / f"show_t{i}")})
        if not c.success:
            log(f"tramo {i}/{n}: CHECK FALLO {c.error}")
            raise SystemExit(1)
    log(f"check de los {n} tramos: OK")
    for i in range(1, n + 1):
        ws, part = HF / f"show_t{i}", OUT / f"show_t{i}.mp4"
        log(f"tramo {i}/{n}: render empieza")
        t0 = time.time()
        r = hf.execute({"operation": "render_existing", "workspace_path": str(ws), "output_path": str(part),
                        "fps": FPS, "quality": "high"})
        if not r.success:
            log(f"tramo {i}/{n}: FALLO {r.error}")
            raise SystemExit(1)
        st = frames(part)
        log(f"tramo {i}/{n}: listo en {time.time() - t0:.0f}s, {st['nb_read_frames']} frames")
        parts.append(part)
    lst = OUT / "show_parts.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
    full = OUT / "show_full.mp4"
    ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(full))
    st = frames(full)
    expected = round((json.loads((PROJ / "song_map/la-mitad-de-mi-vida.json").read_text())["duration_seconds"] + 60) * FPS)
    log(f"unión: {st['nb_read_frames']} frames (esperado {expected}) {st['width']}x{st['height']}")

    log("masters: H.264 alta tasa + ProRes 422 HQ (sin audio)")
    master = OUT / "01_la-mitad-de-mi-vida_1920x1080_30p_h264.mp4"
    ff("-i", str(full), "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p", "-an", str(master))
    prores = OUT / "01_la-mitad-de-mi-vida_1920x1080_30p_prores422hq.mov"
    ff("-i", str(full), "-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le", "-an", str(prores))
    log("copia de revisión con audio y timecode")
    review = OUT / "01_la-mitad-de-mi-vida_review.mp4"
    ff("-i", str(full), "-i", str(TRACK), "-map", "0:v", "-map", "1:a", "-vf",
       "drawtext=timecode='00\\:00\\:00\\:00':rate=30:x=24:y=24:fontsize=26:fontcolor=white@0.8:box=1:boxcolor=black@0.5",
       "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", str(review))

    log("verificación fotosensible")
    luma = OUT / "show_luma.txt"
    ff("-i", str(full), "-vf", f"signalstats,metadata=print:key=lavfi.signalstats.YAVG:file={luma.name}", "-f", "null", "-")
    y = [float(m) for m in re.findall(r"YAVG=([0-9.]+)", (Path.cwd() / luma.name).read_text())] \
        if (Path.cwd() / luma.name).exists() else [float(m) for m in re.findall(r"YAVG=([0-9.]+)", luma.read_text())]
    worst, th = 0, 25.5
    for s in range(0, len(y) - FPS):
        w, d, ext, fl = y[s:s + FPS], 0, y[s], 0
        for v in w[1:]:
            if v - ext >= th and d <= 0: d, ext = 1, v
            elif ext - v >= th and d >= 0:
                fl += d == 1; d, ext = -1, v
            elif (d == 1 and v > ext) or (d == -1 and v < ext): ext = v
        worst = max(worst, fl)
    log(f"luma media {min(y):.0f}-{max(y):.0f}; máx destellos en 1 s: {worst} (límite 3)")
    log(f"TODO LISTO en {(time.time() - t_all) / 60:.1f} min")


if __name__ == "__main__":
    main()
