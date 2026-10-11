"""Show v2: clips por escena, render en caché, unión sin recodificar.

Desde la raíz del repo (PATH con Node 22 y ffmpeg):
    .venv/bin/python projects/la-mitad-de-mi-vida/hyperframes/src2/build2.py fotos 20,52,60,110
        -> fotos de esos instantes de la canción (segundos)
    .venv/bin/python .../build2.py clip 95 20
        -> clip con audio de 95 s a 115 s (renderiza solo los clips que falten)
    .venv/bin/python .../build2.py show [--check] [--master]
        -> show completo + copia de revisión con audio; --master añade H.264 y ProRes sin audio

Caché: renders/v2/clips/<n>_<hash>.mp4. Cambiar una colocación de plan2.py solo
re-renderiza su clip y el siguiente (que funde desde ella).
"""

import argparse
import hashlib
import html
import json
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import plan2 as P  # noqa: E402

HF = HERE.parent
PROJ = HF.parent
ROOT = PROJ.parents[1]
WSDIR = HF / "v2"
OUT = PROJ / "renders" / "v2"
CACHE = OUT / "clips"
TRACK = ROOT / "_audio_fuera_del_repo/La Mitad De Mi Vida - TIKO DURAN.wav"
FPS = 30
JOBS = 2          # renders simultáneos
WORKERS = 6       # Chrome por render


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise RuntimeError(f"{cmd[:3]} -> {(r.stdout + r.stderr)[-1500:]}")
    return r


# ---------------------------------------------------------------- datos

def load():
    sm = json.loads((PROJ / "song_map/la-mitad-de-mi-vida.json").read_text(encoding="utf-8"))
    audio = json.loads((PROJ / "audio_data/full_30fps.json").read_text(encoding="utf-8"))
    return sm, audio


def energy(audio):
    import numpy as np
    b = np.array([f["bands"] for f in audio["frames"]], dtype=float)

    def smooth(x, w):
        k = np.ones(w) / w
        return np.convolve(np.pad(x, (w // 2, w - w // 2 - 1), mode="edge"), k, mode="valid")

    def norm(x):
        lo, hi = np.percentile(x, 5), np.percentile(x, 97)
        return np.clip((x - lo) / max(1e-9, hi - lo), 0, 1)

    bands = np.stack([norm(smooth(b[:, k], 3)) for k in range(16)], 1)
    low, high = norm(smooth(b[:, 0:4].mean(1), 30)), norm(smooth(b[:, 10:16].mean(1), 30))
    return {"fps": audio["fps"], "bands": bands.round(3), "low": low.round(3), "high": high.round(3)}


def placements(sm):
    """Colocaciones con límites exactos al frame."""
    song_end = sm["duration_seconds"]
    total_f = round((song_end + P.TAIL) * FPS)
    rows = []
    for i, (t0, sc, partner, en, extra) in enumerate(P.PLACEMENTS):
        f0 = round(t0 * FPS)
        f1 = round(P.PLACEMENTS[i + 1][0] * FPS) if i + 1 < len(P.PLACEMENTS) else total_f
        rows.append({"i": i, "f0": f0, "f1": f1, "t0": f0 / FPS, "scene": P.SCENES[sc], "name": sc,
                     "partner": P.PARTNERS[partner], "energy": en,
                     "logo": bool(extra.get("logo")), "photo": bool(extra.get("photo"))})
    return rows


# ---------------------------------------------------------------- imágenes

def bake_images():
    """Silueta (máscara), tinta Warhol y foto de perfil, precocinadas una vez."""
    img_dir = HF / "v2_images"
    if (img_dir / "bw_face.png").exists():
        return img_dir
    import numpy as np
    from PIL import Image
    img_dir.mkdir(parents=True, exist_ok=True)
    stage = Image.open(PROJ / "assets/images/tiko_01_cut.png").convert("RGBA")
    stage = stage.resize((287 * 2, 520 * 2), Image.LANCZOS)
    a = np.asarray(stage, dtype=float) / 255
    alpha = a[..., 3]
    lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    sil = np.zeros(a.shape)
    sil[..., :3] = 1
    sil[..., 3] = alpha
    Image.fromarray((sil * 255).astype("uint8")).save(img_dir / "sil.png")
    ink_a = np.clip((0.62 - lum) * 4.0, 0, 1) * alpha
    ink = np.zeros(a.shape)
    ink[..., 0], ink[..., 1], ink[..., 2] = 0x1c / 255, 0x04 / 255, 0x18 / 255
    ink[..., 3] = ink_a
    Image.fromarray((ink * 255).astype("uint8")).save(img_dir / "ink.png")
    prof = Image.open(PROJ / "assets/images/tiko_02_cut.png").convert("RGBA")
    prof.resize((780, round(780 * prof.height / prof.width)), Image.LANCZOS).save(img_dir / "photo.png")
    return img_dir


# ---------------------------------------------------------------- workspaces

PHOTOS = ["bw_portrait", "bw_03", "bw_05", "bw_04", "bw_stage"]
SILS = ["sil", "sil_03", "sil_05"]


def frame_imgs(i, n=3):
    """Varias fotos en un marco; el JS muestra una cada 8 beats (rota según la colocación)."""
    pool = [PHOTOS[(i + j) % len(PHOTOS)] for j in range(n)]
    return "".join(f'<img class="fp" src="images/{p}.png" alt="" />' for p in pool)


def overlay_html(prev, cur, lyrics):
    parts = []
    for k, pl in (("A", prev), ("C", cur)):
        n, col = pl["name"], pl["partner"]
        if n == "mono":
            parts.append(f'        <div class="ov" data-k="{k}" data-kind="mono"><div data-smear="v" class="frame bt" style="left:690px;top:150px;width:540px;height:780px;'
                         f'border:10px solid #fff">{frame_imgs(pl["i"])}</div></div>')
        elif n == "arcos":
            parts.append(f'        <div class="ov" data-k="{k}" data-kind="arcos"><div data-smear="v" class="frame" style="left:657px;top:292px;width:606px;height:788px;'
                         f'border-radius:303px 303px 0 0;background:#222">{frame_imgs(pl["i"] + 1)}</div></div>')
        elif n == "marco":
            parts.append(f'        <div class="ov" data-k="{k}" data-kind="marco"><div data-smear="v" class="frame bt" style="left:770px;top:290px;width:380px;height:500px;'
                         f'border:6px solid {col}">{frame_imgs(pl["i"] + 2)}</div></div>')
        elif n == "tvs":
            tvs = "".join(f'<div class="tv" style="left:{x + 25.6:.1f}px;top:{y + 32.4:.1f}px;width:268.8px;height:205.2px;'
                          f'background-position:{640 - x - 25.6:.1f}px {270 - y - 32.4:.1f}px"></div>'
                          for x in (640, 960) for y in (270, 540))
            parts.append(f'        <div class="ov" data-k="{k}" data-kind="tvs">{tvs}</div>')
        elif n == "collage":
            rows = "".join(f'<span data-layout-ignore class="cw" style="top:{230 + i * 190}px;color:{"#ffffff" if i % 2 == 0 else P.INK}">'
                           f'{"LA MITAD" if i % 2 == 0 else "DE MI VIDA"}</span>' for i in range(4))
            parts.append(f'        <div class="ov" data-k="{k}" data-kind="collage"><img src="images/{["bw_stage", "bw_05", "bw_03"][pl["i"] % 3]}.png" alt="" '
                         f'style="position:absolute;left:150px;top:120px;width:540px;height:840px;object-fit:contain;object-position:bottom;display:block" />{rows}</div>')
        elif n == "nombre":
            parts.append(f'        <div class="ov" data-k="{k}" data-kind="nombre">'
                         f'<div data-smear="h" class="big" style="top:150px"><span data-layout-ignore style="font-size:420px">TIKO</span></div>'
                         f'<div data-smear="h" class="big" style="top:540px"><span data-layout-ignore style="font-size:330px;color:{P.YELLOW}">DURÁN</span></div></div>')
        elif n == "warhol":
            pal = [P.YELLOW, "#39e639", col, "#8a2be2", "#1f4bff", "#ffffff", "#ff2d8a"]
            cells = []
            for i in range(4 * 9):
                r, c = divmod(i, 9)
                kind = (i * 7 + r * 3) % 4
                bg = pal[(i * 3 + r) % len(pal)]
                if kind == 0:
                    inner = f'<img src="images/{PHOTOS[(i // 4) % len(PHOTOS)]}.png" alt="" />'
                elif kind == 1:
                    sil = SILS[(i // 4) % len(SILS)]
                    inner = (f'<div class="s" style="background:{"#1c0418" if i % 2 else "#ff2d8a"};-webkit-mask-image:url(images/{sil}.png);'
                             f'mask-image:url(images/{sil}.png)"></div>')
                elif kind == 2:
                    inner = '<span data-layout-ignore class="nm">TIKO<br />DURÁN</span>'
                    bg = col
                else:
                    inner = f'<img src="images/{PHOTOS[(i // 4 + 2) % len(PHOTOS)]}.png" alt="" />'
                cells.append(f'<div class="wcell" style="left:{c * 470 + (r % 2) * 120}px;top:{r * 450}px;background:{bg};'
                             f'border:6px solid #1c0418">{inner}</div>')
            parts.append(f'        <div class="ov" data-k="{k}" data-kind="warhol"><div class="wall">{"".join(cells)}</div></div>')
        elif n == "stack":
            rows = "".join(f'<span data-layout-ignore style="color:{"#ffffff" if i % 2 == 0 else "rgba(40,0,10,0.55)"}">TIKO DURÁN</span>'
                           for i in range(8))
            st = ('<div class="stk-s" style="left:1440px;top:620px;width:60px;height:300px;background:#fff;border-radius:30px"></div>'
                  '<div class="stk-s" style="left:280px;top:180px;width:220px;height:220px;border:44px solid #fff;border-radius:50%;box-sizing:border-box"></div>'
                  '<div class="stk-s" style="left:1500px;top:160px;width:240px;height:240px">'
                  '<div style="position:absolute;left:90px;top:0;width:60px;height:240px;background:#fff;border-radius:30px;transform:rotate(45deg)"></div>'
                  '<div style="position:absolute;left:90px;top:0;width:60px;height:240px;background:#fff;border-radius:30px;transform:rotate(-45deg)"></div></div>')
            parts.append(f'        <div class="ov" data-k="{k}" data-kind="stack"><div class="stk">{rows}</div>{st}</div>')
        elif n == "palabra":
            word = "LA MITAD DE MI VIDA · " * 4
            parts.append(f'        <div class="ov" data-k="{k}" data-kind="palabra">'
                         f'<span data-smear="h" data-layout-ignore class="pw" style="top:250px;font-size:520px;line-height:560px;color:rgba(10,0,40,0.55)">{word}</span></div>')
        elif n == "diana":
            parts.append(f'        <div class="ov" data-k="{k}" data-kind="diana"><span data-smear="h" data-layout-ignore class="dw">Tiko Durán</span></div>')
    if prev["logo"] or cur["logo"]:
        parts.append('        <img id="logo" src="images/logo.png" alt="" style="position:absolute;left:110px;top:170px;width:860px;opacity:0;display:block" />')
    if prev["photo"] or cur["photo"]:
        parts.append('        <img id="photo" src="images/photo.png" alt="" />')
    for j, (a, b, text, style) in enumerate(lyrics):
        parts.append(f'        <div class="lyr {style}" data-t0="{a}" data-t1="{b}"><span>{html.escape(text)}</span></div>')
    return "\n".join(parts)


def build_clip(pl, prev, sm, en, img_dir, xfade):
    f0, f1 = pl["f0"], pl["f1"]
    start, dur = f0 / FPS, (f1 - f0) / FPS
    song_end = sm["duration_seconds"]
    if start >= song_end - 1e-6:          # cola: reutiliza los últimos 16 s
        e0, e1 = round((song_end - 16) * FPS), round(song_end * FPS)
    else:
        e0, e1 = max(0, f0 - 2), min(len(en["low"]), f1 + 2)
    lyrics = [l for l in P.LYRICS if l[1] > start and l[0] < start + dur]
    show = {
        "start": start, "duration": dur, "songEnd": song_end, "xfade": min(xfade, 0.9 * dur),
        "beats": [b["time_seconds"] for b in sm["beats"]], "barSeconds": sm["bar_seconds"],
        "yellow": P.YELLOW, "ink": P.INK, "isFirst": pl["i"] == 0,
        "prev": prev, "cur": pl, "wipe": pl["i"] % 5,
        "energy": {"fps": en["fps"], "t0": e0 / en["fps"], "n": e1 - e0,
                   "bands": en["bands"][e0:e1].tolist(), "low": en["low"][e0:e1].tolist(),
                   "high": en["high"][e0:e1].tolist()},
    }
    s = (HERE / "clip.template.html").read_text(encoding="utf-8")
    s = (s.replace("__DURATION__", f"{dur:.4f}").replace("__OVERLAYS__", overlay_html(prev, pl, lyrics))
          .replace("__SHOW__", json.dumps(show, ensure_ascii=False)))
    ws = WSDIR / f"clip_{pl['i']:02d}"
    if ws.exists():
        shutil.rmtree(ws)
    ws.mkdir(parents=True)
    for sub in ("fonts", "vendor"):
        shutil.copytree(HF / "look_test_v3" / sub, ws / sub)
    shutil.copytree(img_dir, ws / "images")
    (ws / "index.html").write_text(s, encoding="utf-8")
    h = hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]
    return {"ws": ws, "hash": h, "out": CACHE / f"{pl['i']:02d}_{h}.mp4", "start": start, "dur": dur, "pl": pl}


def build_all():
    sm, audio = load()
    en = energy(audio)
    img_dir = bake_images()
    rows = placements(sm)
    xfade = P.XFADE_BARS * sm["bar_seconds"]
    clips = [build_clip(pl, rows[max(0, k - 1)], sm, en, img_dir, xfade) for k, pl in enumerate(rows)]
    return sm, clips


# ---------------------------------------------------------------- render

def render_clip(c):
    if c["out"].exists():
        return c, 0.0
    t0 = time.time()
    tmp = c["out"].with_suffix(".tmp.mp4")
    run(["npx", "--yes", "hyperframes@0.8.145", "render", "--output", str(tmp), "--fps", str(FPS), "--quality", "draft",
         "--crf", "12", "--workers", str(WORKERS), "--quiet"], cwd=c["ws"])
    tmp.rename(c["out"])
    return c, time.time() - t0


def check_clip(c):
    r = subprocess.run(["npx", "--yes", "hyperframes@0.8.145", "check"], cwd=c["ws"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    bad = [l.strip() for l in r.stdout.splitlines() if "✗" in l]
    return c, ("Check failed" in r.stdout or r.returncode != 0), bad


def render_many(clips):
    CACHE.mkdir(parents=True, exist_ok=True)
    todo = [c for c in clips if not c["out"].exists()]
    log(f"{len(clips)} clips, {len(clips) - len(todo)} en caché, {len(todo)} por renderizar")
    t0 = time.time()
    with ThreadPoolExecutor(JOBS) as ex:
        for c, dt in ex.map(render_clip, todo):
            log(f"clip {c['pl']['i']:02d} {c['pl']['name']:<12} {c['dur']:5.1f} s -> {dt:5.1f} s")
    if todo:
        log(f"render: {time.time() - t0:.0f} s")


def concat(clips, out):
    lst = out.with_suffix(".txt")
    lst.write_text("".join(f"file '{c['out'].resolve()}'\n" for c in clips), encoding="utf-8")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", str(out)])
    lst.unlink()


def mux(video, out, start=0.0, dur=None):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{start}", "-i", str(video),
           "-ss", f"{start}", "-i", str(TRACK)]
    if dur:
        cmd += ["-t", f"{dur}"]
    cmd += ["-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", str(out)]
    run(cmd)


# ---------------------------------------------------------------- modos

def clip_for(clips, t):
    for c in clips:
        if c["start"] <= t < c["start"] + c["dur"]:
            return c
    return clips[-1]


def mode_fotos(clips, times):
    shot = OUT / "fotos"
    shutil.rmtree(shot, ignore_errors=True)
    groups = {}
    for t in times:
        groups.setdefault(clip_for(clips, t)["pl"]["i"], []).append(t)

    def snap(item):
        i, ts = item
        c = clips[i]
        d = shot / f"c{i:02d}"
        run(["npx", "--yes", "hyperframes@0.8.145", "snapshot", "--at", ",".join(f"{t - c['start']:.3f}" for t in ts), "--no-end",
             "--output", str(d)], cwd=c["ws"])
        return list(zip(ts, sorted(d.glob("*.png"))))

    with ThreadPoolExecutor(4) as ex:
        pairs = sorted(sum(ex.map(snap, groups.items()), []))
    n = len(pairs)
    cols = 1 if n == 1 else (2 if n <= 4 else 3)
    rows = (n + cols - 1) // cols
    inputs = sum((["-i", str(p)] for _, p in pairs), [])
    fc = "".join(f"[{i}:v]scale=640:-1,drawtext=text='{t:.1f} s  {clip_for(clips, t)['pl']['name']}':x=12:y=12:"
                 f"fontsize=26:fontcolor=white:box=1:boxcolor=black@0.6[v{i}];" for i, (t, _) in enumerate(pairs))
    if n == 1:
        fc = fc.rstrip(";").replace("[v0]", "")
    else:
        layout = "|".join(f"{(i % cols) * 640}_{(i // cols) * 360}" for i in range(n))
        fc += "".join(f"[v{i}]" for i in range(n)) + f"xstack=inputs={n}:layout={layout}" + \
            (":fill=black" if n < cols * rows else "")
    sheet = OUT / "fotos.jpg"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs, "-filter_complex", fc,
         "-frames:v", "1", "-q:v", "3", str(sheet)])
    return sheet


def mode_clip(clips, start, dur):
    sel = [c for c in clips if c["start"] + c["dur"] > start and c["start"] < start + dur]
    render_many(sel)
    tmp = OUT / "clip_tmp.mp4"
    concat(sel, tmp)
    out = OUT / f"clip_{start:g}s_{dur:g}s.mp4"
    off = start - sel[0]["start"]
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{off}", "-i", str(tmp), "-ss", f"{start}",
         "-i", str(TRACK), "-t", f"{dur}", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(out)])
    tmp.unlink()
    return out


def mode_show(clips, sm, check, master):
    if check:
        with ThreadPoolExecutor(4) as ex:
            fails = [(c, bad) for c, failed, bad in ex.map(check_clip, clips) if failed]
        for c, bad in fails:
            log(f"CHECK clip {c['pl']['i']:02d} {c['pl']['name']}: " + " | ".join(bad[:3]))
        if fails:
            raise SystemExit(1)
        log("check: todos OK")
    render_many(clips)
    full = OUT / "show_v2.mp4"
    concat(clips, full)
    review = OUT / "01_la-mitad-de-mi-vida_v2_review.mp4"
    mux(full, review)
    log(f"revisión: {review}")
    if master:
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(full), "-c:v", "libx264", "-preset", "slow",
             "-crf", "12", "-pix_fmt", "yuv420p", "-an", str(OUT / "01_la-mitad-de-mi-vida_v2_1920x1080_30p_h264.mp4")])
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(full), "-c:v", "prores_ks", "-profile:v", "3",
             "-pix_fmt", "yuv422p10le", "-an", str(OUT / "01_la-mitad-de-mi-vida_v2_1920x1080_30p_prores422hq.mov")])
        log("masters listos")
    return review


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    sub.add_parser("fotos").add_argument("times")
    c = sub.add_parser("clip")
    c.add_argument("start", type=float)
    c.add_argument("dur", type=float)
    s = sub.add_parser("show")
    s.add_argument("--check", action="store_true")
    s.add_argument("--master", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    sm, clips = build_all()
    if a.mode == "fotos":
        res = mode_fotos(clips, [float(x) for x in a.times.split(",")])
    elif a.mode == "clip":
        res = mode_clip(clips, a.start, a.dur)
    else:
        res = mode_show(clips, sm, a.check, a.master)
    log(f"{res}  (total {time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
