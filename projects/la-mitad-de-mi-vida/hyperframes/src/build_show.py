"""Genera los workspaces de render del show (un index.html por tramo).

Uso:  python build_show.py            -> todos los tramos
      python build_show.py 1          -> solo el tramo 1
      python build_show.py preview 49 14   -> workspace de prueba desde t=49 s, 14 s

Los tramos son contiguos y exactos al frame, para unirlos con concat -c copy.
"""

import html
import json
import shutil
import sys
from pathlib import Path

import show_plan as P

HERE = Path(__file__).resolve().parent
HF = HERE.parent                      # projects/<p>/hyperframes
PROJ = HF.parent
FPS = 30
CHUNK_FRAMES = [0, 3000, 6000, 9000]  # inicio de cada tramo (frames)


def load():
    sm = json.loads((PROJ / "song_map/la-mitad-de-mi-vida.json").read_text(encoding="utf-8"))
    audio = json.loads((PROJ / "audio_data/full_30fps.json").read_text(encoding="utf-8"))
    return sm, audio


def energy(audio):
    import numpy as np
    b = np.array([f["bands"] for f in audio["frames"]])
    def smooth(x, w=30):
        k = np.ones(w) / w
        return np.convolve(np.pad(x, (w // 2, w - w // 2 - 1), mode="edge"), k, mode="valid")
    def norm(x):
        lo, hi = np.percentile(x, 5), np.percentile(x, 95)
        return np.clip((x - lo) / (hi - lo), 0, 1)
    low, high = norm(smooth(b[:, 0:4].mean(1))), norm(smooth(b[:, 10:16].mean(1)))
    return {"fps": audio["fps"], "low": low.round(3).tolist(), "high": high.round(3).tolist()}


def local_beat(sm, t):
    bt = [b["time_seconds"] for b in sm["beats"]]
    near = [x for x in bt if t - 4 <= x <= t + 4]
    if len(near) < 3:
        return sm["bar_seconds"] / 4
    return (near[-1] - near[0]) / (len(near) - 1)


def section_at(t):
    cur = P.SECTIONS[0]
    for s in P.SECTIONS:
        if s["t0"] <= t:
            cur = s
    return cur


def cards(sm):
    out, html_parts = [], []
    L = P.LYRICS
    for i, (t, text, style) in enumerate(L):
        nxt = L[i + 1][0] if i + 1 < len(L) else t + 10
        t1 = min(t + P.MAX_CARD[style], nxt - 0.12)
        cid = f"c{i:02d}"
        words = "".join(f'<span class="w">{html.escape(w)}</span>' for w in text.split())
        glow = section_at(t)["ray"]
        html_parts.append(f'        <div id="{cid}" class="card {style}" style="--glow:{glow}">{words}</div>')
        out.append({"id": cid, "t": t, "t1": round(t1, 3), "style": style, "beat": round(local_beat(sm, t), 4)})
    return out, "\n".join(html_parts)


def mosaics():
    parts = []
    for key, phrase in P.MOSAIC.items():
        rows = "".join(
            f'<span data-layout-ignore class="mrow{" fill" if i % 2 else ""}" style="top:{i * 136}px">'
            + html.escape((phrase + " · ") * 9) + "</span>"
            for i in range(10)
        )
        parts.append(f'        <div class="mosaic" data-key="{key}">{rows}</div>')
    return "\n".join(parts)


STAR = ('<svg class="neon-star" style="left:{x}px;top:{y}px" viewBox="-60 -60 120 120">'
        '<path d="M0,-50 L14,-16 L50,-15 L22,8 L31,44 L0,23 L-31,44 L-22,8 L-50,-15 L-14,-16 Z" fill="none" stroke="#ff4fd8" stroke-width="7" stroke-linejoin="round"/>'
        '<path d="M0,-50 L14,-16 L50,-15 L22,8 L31,44 L0,23 L-31,44 L-22,8 L-50,-15 L-14,-16 Z" fill="none" stroke="#ffd6f6" stroke-width="2.5" stroke-linejoin="round"/></svg>')


def build(name, start, duration, sm, en, card_data, card_html):
    ws = HF / name
    ws.mkdir(parents=True, exist_ok=True)
    for sub in ("fonts", "vendor"):
        if not (ws / sub).exists():
            shutil.copytree(HF / "look_test_v3" / sub, ws / sub)
    (ws / "images").mkdir(exist_ok=True)
    for img in ("tiko_01_cut.png", "tiko_02_cut.png"):
        shutil.copy2(PROJ / "assets/images" / img, ws / "images" / img)
    song_end = sm["duration_seconds"]
    total = round(song_end + P.TAIL, 3)
    show = {
        "start": start, "duration": duration, "total": total, "songEnd": song_end,
        "beats": [b["time_seconds"] for b in sm["beats"]], "barSeconds": sm["bar_seconds"],
        "sections": P.SECTIONS, "tracks": {k: [list(x) for x in v] for k, v in P.TRACKS.items()},
        "heart": [list(h) for h in P.HEART], "bursts": P.BURSTS,
        "shootingStar": list(P.SHOOTING_STAR), "cards": card_data, "energy": en,
    }
    stars = "".join(STAR.format(x=x, y=y) for x, y in [(120, 620), (330, 780), (1440, 780), (1650, 620), (250, 330), (1520, 330)])
    s = (HERE / "show.template.html").read_text(encoding="utf-8")
    s = (s.replace("__DURATION__", f"{duration:.4f}").replace("__MOSAICS__", mosaics())
          .replace("__STARS__", stars).replace("__CARDS__", card_html)
          .replace("__SHOW__", json.dumps(show, ensure_ascii=False)))
    (ws / "index.html").write_text(s, encoding="utf-8")
    return ws


def main():
    sm, audio = load()
    en = energy(audio)
    card_data, card_html = cards(sm)
    total_frames = round((sm["duration_seconds"] + P.TAIL) * FPS)
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        start, dur = float(sys.argv[2]), float(sys.argv[3])
        print(build("show_preview", start, dur, sm, en, card_data, card_html))
        return
    bounds = CHUNK_FRAMES + [total_frames]
    only = int(sys.argv[1]) if len(sys.argv) > 1 else None
    for i in range(len(CHUNK_FRAMES)):
        if only and only != i + 1:
            continue
        f0, f1 = bounds[i], bounds[i + 1]
        ws = build(f"show_t{i + 1}", f0 / FPS, (f1 - f0) / FPS, sm, en, card_data, card_html)
        print(ws, f0, f1, f1 - f0)
    print("total_frames", total_frames)


if __name__ == "__main__":
    main()
