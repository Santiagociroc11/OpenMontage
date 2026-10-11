"""Prepara las imágenes del mundo continuo a partir de recortes PNG del artista.

Por cada recorte (fondo transparente) genera:
  <k>.png            recorte a color (≤ 820 px)
  <k>_<color>.png    duotono: tinta -> color del mundo -> casi blanco (tarjetas y mosaico)
  <k>_sil.png        silueta blanca (máscara de las estelas de color)
y escribe aspects.json (alto/ancho) que el plan usa para dimensionar.

Uso (desde la raíz del repo):
    .venv/bin/python skills/pipelines/concert-visuals/engine/bake_images.py <salida> k1=ruta1.png k2=ruta2.png [logo=logo.png]

Los recortes se hacen antes con rembg (modelo u2net_human_seg) en un venv aislado:
instalarlo en el .venv del repo sube numpy a 2.x y rompe otras herramientas.
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

INK = np.array([0x1C, 0x04, 0x18]) / 255
COLORS = {"red": "#e3103f", "coral": "#ff3b5c", "magenta": "#e0168a", "orange": "#ff7a1a", "yellow": "#ffd23a"}


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    aspects = {}
    for arg in sys.argv[2:]:
        key, path = arg.split("=", 1)
        im = Image.open(path).convert("RGBA")
        if key == "logo":
            bb = im.getchannel("A").getbbox()
            im = im.crop(bb)
            im.thumbnail((1100, 1100), Image.LANCZOS)
            im.save(out / "logo.png")
            aspects["logo"] = round(im.height / im.width, 4)
            continue
        im.thumbnail((820, 820), Image.LANCZOS)
        aspects[key] = round(im.height / im.width, 4)
        im.save(out / f"{key}.png")
        a = np.asarray(im, dtype=float) / 255
        alpha = a[..., 3]
        lum = np.clip((0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2] - 0.08) * 1.35, 0, 1)[..., None]
        for name, hx in COLORS.items():
            c = hexc(hx)
            hi = c * 0.25 + 0.75
            m = np.where(lum < 0.5, INK + (c - INK) * (lum / 0.5), c + (hi - c) * ((lum - 0.5) / 0.5))
            Image.fromarray((np.dstack([m, alpha]) * 255).astype("uint8")).save(out / f"{key}_{name}.png")
        sil = np.zeros(a.shape)
        sil[..., :3] = 1
        sil[..., 3] = alpha
        Image.fromarray((sil * 255).astype("uint8")).save(out / f"{key}_sil.png")
    (out / "aspects.json").write_text(json.dumps(aspects))
    print(aspects)


if __name__ == "__main__":
    main()
