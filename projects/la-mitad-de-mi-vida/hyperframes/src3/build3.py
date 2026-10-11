"""Show v6 (mundo continuo): tramos de 12 s cacheados, unión sin recodificar.

Desde la raíz del repo (PATH con Node 22 y ffmpeg):
    .venv/bin/python projects/la-mitad-de-mi-vida/hyperframes/src3/build3.py fotos 20,52,60
    .venv/bin/python projects/la-mitad-de-mi-vida/hyperframes/src3/build3.py clip 40 30
    .venv/bin/python projects/la-mitad-de-mi-vida/hyperframes/src3/build3.py show [--master]

Todo es función del tiempo de canción, así que los tramos empalman sin costura.
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
import plan3 as P  # noqa: E402

HF = HERE.parent
PROJ = HF.parent
ROOT = PROJ.parents[1]
IMG = HF / "v3_images"
WSDIR = HF / "v3"
OUT = PROJ / "renders" / "v3"
CACHE = OUT / "clips"
TRACK = ROOT / "_audio_fuera_del_repo/La Mitad De Mi Vida - TIKO DURAN.wav"
FPS = 30
CHUNK = 12.0
JOBS = 3
WORKERS = 4
HF_CLI = ["npx", "--yes", "hyperframes@0.8.145"]

SHAPES = {
    "heart": "M0,35 C-30,12 -48,-2 -48,-20 C-48,-36 -34,-46 -22,-46 C-10,-46 -3,-38 0,-30 C3,-38 10,-46 22,-46 C34,-46 48,-36 48,-20 C48,-2 30,12 0,35 Z",
    "circle": "M0,-46 A46,46 0 1 1 0,46 A46,46 0 1 1 0,-46 Z",
    "star": "M0,-48 L11,-15 L46,-15 L18,6 L29,40 L0,19 L-29,40 L-18,6 L-46,-15 L-11,-15 Z",
    "blob": "M-40,10 C-50,-20 -30,-45 -5,-42 C15,-50 45,-35 42,-10 C50,15 30,45 0,40 C-25,48 -45,30 -40,10 Z",
    "xbox": "M-48,-32 L48,-32 L48,32 L-48,32 Z M-48,-32 L48,32 M48,-32 L-48,32",
    "scribble": "M-48,10 C-30,-30 -20,40 0,0 S30,-40 48,-10",
    "arch": "M-40,45 L-40,0 A40,40 0 0 1 40,0 L40,45",
}


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise RuntimeError(f"{cmd[:4]} -> {(r.stdout + r.stderr)[-1500:]}")
    return r


# ---------------------------------------------------------------- HTML de elementos

def el_html(e):
    k = e["k"]
    w, h = e.get("w"), e.get("h") or e.get("w")
    size = f"width:{w:.0f}px;height:{h:.0f}px;" if w else ""
    p = {key: e[key] for key in e if key not in ("txt", "src", "tiles")}
    attrs = f'class="el {k}" data-p="{html.escape(json.dumps(p))}"'
    z = f'z-index:{13 if e.get("hook") and e["k"] == "cut" else e.get("z", 10)};'
    imgs = set()
    if k == "fill":
        inner = f'<svg viewBox="-50 -50 100 100" width="100" height="100" style="overflow:visible"><path d="{SHAPES[e["shape"]]}" fill="{e["c"]}"/></svg>'
        out = f'<div {attrs} style="width:100px;height:100px;{z}">{inner}</div>'
    elif k == "line":
        out = (f'<svg {attrs} viewBox="-50 -50 100 100" style="{size}{z}overflow:visible"><path d="{SHAPES[e["shape"]]}" fill="none" '
               f'stroke="{e["col"]}" stroke-width="{e["sw"]}" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke" '
               f'pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/></svg>')
    elif k in ("star", "heart"):
        out = f'<svg {attrs} viewBox="-50 -50 100 100" style="{size}{z}"><path d="{SHAPES[k]}" fill="{e["c"]}"/></svg>'
    elif k == "sun":
        rays = "".join(f'<polygon points="0,0 {70 * __import__("math").cos(a):.2f},{70 * __import__("math").sin(a):.2f} '
                       f'{70 * __import__("math").cos(a + 0.2):.2f},{70 * __import__("math").sin(a + 0.2):.2f}" fill="{e["c"]}"/>'
                       for a in [i * 6.2832 / 18 for i in range(18)])
        out = (f'<svg {attrs} viewBox="-50 -50 100 100" style="{size}{z}overflow:visible"><g class="rays" style="transform-origin:0 0">{rays}</g>'
               f'<circle r="15" fill="#fff3b8"/><circle r="19" fill="none" stroke="#fff3b8" stroke-width="1.2"/></svg>')
    elif k == "img":
        imgs.add(e["src"])
        out = f'<img {attrs} src="images/{e["src"]}.png" alt="" style="{size}{z}" />'
    elif k == "card":
        imgs.add(e["src"])
        out = f'<div {attrs} style="{size}{z}background:{e["bg"]}"><img src="images/{e["src"]}.png" alt="" /></div>'
    elif k == "cut":
        s = e["src"]
        imgs.update({s, f"{s}_sil"})
        m = f'-webkit-mask-image:url(images/{s}_sil.png);mask-image:url(images/{s}_sil.png);'
        out = (f'<div {attrs} style="{size}{z}"><div class="echo" style="{m}background:{e["c2"]}"></div>'
               f'<div class="echo" style="{m}background:{e["c1"]}"></div><img src="images/{s}.png" alt="" /></div>')
    elif k == "st":
        out = (f'<div {attrs} data-layout-ignore style="{z}background:{e["bg"]};color:{e["col"]};font-size:{e["fs"]}px">'
               f'{html.escape(e["txt"])}</div>')
    elif k == "bt":
        out = f'<span {attrs} data-layout-ignore style="{z}color:{e["col"]};font-size:{e["fs"]}px">{html.escape(e["txt"])}</span>'
    elif k == "sc":
        rows = "".join(f'<span data-layout-ignore style="height:{e["rowh"]}px;font-size:{e["fs"]}px;color:{e["col"] if r % 2 == 0 else e["col2"]}">'
                       f'{html.escape(e["txt"])}</span>' for r in range(e["rows"]))
        out = f'<div {attrs} style="{size}{z}background:{e["bg"]}"><div class="in">{rows}</div></div>'
    elif k in ("rt", "br"):
        chars = "".join('<span class="ch">' + ("&nbsp;" if ch == " " else html.escape(ch)) + "</span>" for ch in e["txt"])
        out = f'<div {attrs} data-layout-ignore style="{z}color:{e["col"]};font-size:{e["fs"]}px">{chars}</div>'
    elif k == "lk":
        big1, small, big2 = e["parts"]
        rows = "".join(f'<div class="row" style="height:{e["rowh"]}px;font-size:{e["fs"]}px;color:{e["col"] if r % 2 == 0 else e["col2"]};'
                       f'transform:translateX({(30 if r % 2 else -30)}px)"><span data-layout-ignore>{html.escape(big1)}</span>'
                       f'<span data-layout-ignore class="sm">{html.escape(small)}</span><span data-layout-ignore>{html.escape(big2)}</span></div>'
                       for r in range(e["rows"]))
        out = f'<div {attrs} style="{size}{z}background:{e["bg"]}"><div class="in">{rows}</div></div>'
    elif k == "vt":
        out = (f'<div {attrs} data-layout-ignore style="{z}color:{e["col"]};font-size:{e["fs"]}px">{html.escape(e["l1"])}<br />'
               f'{html.escape(e["l2"])}</div>')
    elif k == "tp":
        out = (f'<div {attrs} data-layout-ignore style="{z}background:{e["bg"]};color:{e["col"]};font-size:{e["fs"]}px">'
               f'{html.escape(e["txt"])}</div>')
    elif k == "hl":
        l1, sup, l2 = e["parts"]
        sp = f'<span class="sup" style="color:{e["csup"]}">{html.escape(sup)}</span>' if sup else ""
        out = (f'<div {attrs} data-layout-ignore style="{z}font-size:{e["fs"]}px">'
               f'<div class="ln"><div class="in" style="color:{e["c1"]}"><span>{html.escape(l1)}</span>{sp}</div></div>'
               f'<div class="ln"><div class="in" style="color:{e["c2"]}"><span>{html.escape(l2)}</span></div></div></div>')
    elif k == "bx":
        out = f'<div {attrs} style="{size}{z}background:{e["c"]}"></div>'
    elif k == "ht":
        out = (f'<div {attrs} style="{size}{z}background-image:radial-gradient({e["c"]} 28%, rgba(0,0,0,0) 31%);'
               f'background-size:26px 26px"></div>')
    elif k == "chain":
        n, hh = e["n"], e["h"]
        items = "".join(
            f'<div class="ci" style="left:{i * (w - hh) / (n - 1):.1f}px;top:0;width:{hh}px;height:{hh}px">'
            f'<svg viewBox="-50 -50 100 100"><path d="{SHAPES["circle"]}" fill="{e["c"]}"/></svg>'
            f'<svg viewBox="-50 -50 100 100"><path d="{SHAPES["heart"]}" fill="{e["c2"]}"/></svg></div>' for i in range(n))
        out = f'<div {attrs} style="{size}{z}">{items}</div>'
    elif k == "mos":
        duo = P.DUO.get(e["c"], "red")
        tw, th, gap, cols = 300, 380, 16, 26
        tiles = []
        for i, ph in enumerate(e["tiles"]):
            r, c = divmod(i, cols)
            src = f"{ph}_{duo}"
            imgs.add(src)
            tiles.append(f'<img src="images/{src}.png" alt="" style="left:{c * (tw + gap) + (r % 2) * 150}px;top:{r * (th + gap)}px;'
                         f'width:{tw}px;height:{th}px;background:{e["c"]}" />')
        out = f'<div {attrs} style="{size}{z}overflow:hidden;background:{P.INK}"><div class="in">{"".join(tiles)}</div></div>'
    else:
        raise ValueError(k)
    if k in ("card",):
        imgs.add(e["src"])
    return out, imgs


# ---------------------------------------------------------------- tramos

def load():
    sm = json.loads((PROJ / "song_map/la-mitad-de-mi-vida.json").read_text(encoding="utf-8"))
    aspects = json.loads((IMG / "aspects.json").read_text())
    return sm, aspects


def build_all():
    sm, aspects = load()
    E, BASE, CAM = P.make(sm, aspects)
    total_f = round((sm["duration_seconds"] + P.TAIL) * FPS)
    step = round(CHUNK * FPS)
    rendered = [el_html(e) for e in E]
    tmpl = (HERE / "world.template.html").read_text(encoding="utf-8")
    beats = [b["time_seconds"] for b in sm["beats"]]
    chunks = []
    for i, f0 in enumerate(range(0, total_f, step)):
        f1 = min(total_f, f0 + step)
        start, dur = f0 / FPS, (f1 - f0) / FPS
        sel = [(h, im) for e, (h, im) in zip(E, rendered) if e["t1"] > start - 0.05 and e["t0"] < start + dur + 0.05]
        imgs = set().union(*[im for _, im in sel]) if sel else set()
        show = {"start": start, "duration": dur, "beats": beats, "barSeconds": sm["bar_seconds"], "base": BASE, "cam": CAM}
        s = (tmpl.replace("__DURATION__", f"{dur:.4f}").replace("__ELEMENTS__", "\n".join("          " + h for h, _ in sel))
             .replace("__SHOW__", json.dumps(show)))
        ws = WSDIR / f"t{i:02d}"
        if ws.exists():
            shutil.rmtree(ws)
        (ws / "images").mkdir(parents=True)
        for sub in ("fonts", "vendor"):
            shutil.copytree(HF / "look_test_v3" / sub, ws / sub)
        for f in (HF / "v3_fonts").glob("*.ttf"):
            shutil.copy2(f, ws / "fonts" / f.name)
        for im in imgs:
            shutil.copy2(IMG / f"{im}.png", ws / "images" / f"{im}.png")
        (ws / "index.html").write_text(s, encoding="utf-8")
        hsh = hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]
        chunks.append({"i": i, "ws": ws, "start": start, "dur": dur, "n": len(sel), "out": CACHE / f"{i:02d}_{hsh}.mp4"})
    log(f"{len(E)} elementos, {len(chunks)} tramos")
    return sm, chunks


def render_one(c):
    if c["out"].exists():
        return c, 0.0
    t0 = time.time()
    tmp = c["out"].with_suffix(".tmp.mp4")
    run(HF_CLI + ["render", "--output", str(tmp), "--fps", str(FPS), "--quality", "draft", "--crf", "12",
                  "--workers", str(WORKERS), "--quiet"], cwd=c["ws"])
    tmp.rename(c["out"])
    return c, time.time() - t0


def render_many(chunks):
    CACHE.mkdir(parents=True, exist_ok=True)
    todo = [c for c in chunks if not c["out"].exists()]
    log(f"{len(chunks)} tramos, {len(chunks) - len(todo)} en caché, {len(todo)} por renderizar")
    t0 = time.time()
    with ThreadPoolExecutor(JOBS) as ex:
        for c, dt in ex.map(render_one, todo):
            log(f"tramo {c['i']:02d} ({c['n']} elementos) -> {dt:5.1f} s")
    if todo:
        log(f"render: {time.time() - t0:.0f} s")


def concat(chunks, out):
    lst = out.with_suffix(".txt")
    lst.write_text("".join(f"file '{c['out'].resolve()}'\n" for c in chunks), encoding="utf-8")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
    lst.unlink()


def chunk_for(chunks, t):
    for c in chunks:
        if c["start"] <= t < c["start"] + c["dur"]:
            return c
    return chunks[-1]


def mode_fotos(chunks, times):
    shot = OUT / "fotos"
    shutil.rmtree(shot, ignore_errors=True)
    groups = {}
    for t in times:
        groups.setdefault(chunk_for(chunks, t)["i"], []).append(t)

    def snap(item):
        i, ts = item
        c = chunks[i]
        d = shot / f"c{i:02d}"
        run(HF_CLI + ["snapshot", "--at", ",".join(f"{t - c['start']:.3f}" for t in ts), "--no-end", "--output", str(d)], cwd=c["ws"])
        return list(zip(ts, sorted(d.glob("*.png"))))

    with ThreadPoolExecutor(4) as ex:
        pairs = sorted(sum(ex.map(snap, groups.items()), []))
    n = len(pairs)
    cols = 1 if n == 1 else (2 if n <= 4 else 3)
    rows = (n + cols - 1) // cols
    inputs = sum((["-i", str(p)] for _, p in pairs), [])
    fc = "".join(f"[{i}:v]scale=640:-1,drawtext=text='{t:.1f} s':x=12:y=12:fontsize=26:fontcolor=white:box=1:boxcolor=black@0.6[v{i}];"
                 for i, (t, _) in enumerate(pairs))
    if n == 1:
        fc = fc.rstrip(";").replace("[v0]", "")
    else:
        layout = "|".join(f"{(i % cols) * 640}_{(i // cols) * 360}" for i in range(n))
        fc += "".join(f"[v{i}]" for i in range(n)) + f"xstack=inputs={n}:layout={layout}" + (":fill=black" if n < cols * rows else "")
    sheet = OUT / "fotos.jpg"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs, "-filter_complex", fc, "-frames:v", "1", "-q:v", "3", str(sheet)])
    return sheet


def mode_clip(chunks, start, dur):
    sel = [c for c in chunks if c["start"] + c["dur"] > start and c["start"] < start + dur]
    render_many(sel)
    tmp = OUT / "clip_tmp.mp4"
    concat(sel, tmp)
    out = OUT / f"clip_{start:g}s_{dur:g}s.mp4"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{start - sel[0]['start']}", "-i", str(tmp), "-ss", f"{start}",
         "-i", str(TRACK), "-t", f"{dur}", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(out)])
    tmp.unlink()
    return out


def mode_show(chunks, master):
    render_many(chunks)
    full = OUT / "show_v6.mp4"
    concat(chunks, full)
    review = OUT / "01_la-mitad-de-mi-vida_v6_mundo_review.mp4"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(full), "-i", str(TRACK), "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", str(review)])
    if master:
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(full), "-c:v", "libx264", "-preset", "slow", "-crf", "12",
             "-pix_fmt", "yuv420p", "-an", str(OUT / "01_la-mitad-de-mi-vida_v6_1920x1080_30p_h264.mp4")])
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(full), "-c:v", "prores_ks", "-profile:v", "3",
             "-pix_fmt", "yuv422p10le", "-an", str(OUT / "01_la-mitad-de-mi-vida_v6_1920x1080_30p_prores422hq.mov")])
    return review


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    sub.add_parser("fotos").add_argument("times")
    c = sub.add_parser("clip")
    c.add_argument("start", type=float)
    c.add_argument("dur", type=float)
    sub.add_parser("show").add_argument("--master", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    sm, chunks = build_all()
    if a.mode == "fotos":
        res = mode_fotos(chunks, [float(x) for x in a.times.split(",")])
    elif a.mode == "clip":
        res = mode_clip(chunks, a.start, a.dur)
    else:
        res = mode_show(chunks, a.master)
    log(f"{res}  (total {time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
