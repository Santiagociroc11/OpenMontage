"""Plan v6 — un solo mundo continuo (estilo VJ Rauw) para "La mitad de mi vida".

No hay escenas: hay una lista de ELEMENTOS en tiempo de canción que entran y salen
de uno en uno sobre una base de color, una CÁMARA que viaja sobre un tablero
inclinado, y RELLENOS: una forma de la composición (corazón, círculo, estrella)
que crece hasta cubrir la pantalla y se convierte en el color de base siguiente.

`make(sm, aspects)` devuelve (elementos, base, cámara). Determinista (semilla fija).
"""

import random

YEL, CORAL, RED, MAG, ORA = "#ffd23a", "#ff3b5c", "#e3103f", "#e0168a", "#ff7a1a"
INK, WHITE = "#1c0418", "#ffffff"
DUO = {YEL: "yellow", CORAL: "coral", RED: "red", MAG: "magenta", ORA: "orange"}
PHOTOS = ["t2", "t3", "t5", "t4", "t1"]
TAIL = 60.0


def tone(c, f=0.78):
    if c == INK:
        return "#3d0b33"
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))

# Secciones de la grabación: (inicio, mundo, color base, compañero, energía 0-1)
SECTIONS = [
    (0.0, "sol", YEL, CORAL, 0.35),
    (17.508, "corazones", CORAL, YEL, 0.5),
    (44.861, "cadena", CORAL, YEL, 0.7),
    (49.55, "sol", YEL, RED, 0.8),
    (55.565, "tipo", RED, YEL, 0.85),
    (70.891, "collage", MAG, YEL, 0.75),
    (84.265, "tipo", RED, WHITE, 0.9),
    (99.776, "mosaico", INK, ORA, 0.95),
    (135.0, "tipo", ORA, INK, 0.95),
    (152.0, "collage", RED, YEL, 0.9),
    (170.551, "mosaico", INK, YEL, 1.0),
    (190.0, "corazones", MAG, YEL, 0.85),
    (209.328, "noche", INK, CORAL, 0.35),
    (234.127, "cadena", INK, YEL, 0.7),
    (236.35, "sol", YEL, RED, 0.85),
    (244.111, "tipo", RED, YEL, 0.9),
    (255.721, "collage", MAG, YEL, 0.8),
    (270.559, "tipo", CORAL, INK, 0.9),
    (283.771, "mosaico", INK, CORAL, 1.0),
    (299.862, "sol", YEL, CORAL, 1.0),
    (318.973, "final", YEL, CORAL, 0.5),
    (332.371, "cola", YEL, CORAL, 0.3),
]

HOOKS = [  # acentos de letra (verificados con la alineación), como textura tipográfica
    (49.5, "LA MITAD DE MI VIDA"), (56.0, "DÉJAME SOLO DARTE UN BESO"), (84.1, "¡AY, AY, AY, MI AMOR!"),
    (236.4, "LA MITAD DE MI VIDA"), (244.0, "DÉJAME SOLO DARTE UN BESO"), (284.0, "¡AY, AY, AY, MI AMOR!"),
]
STICKERS = ["¡AY, AY, AY!", "TIKO DURÁN", "LA MITAD", "MI VIDA", "¡ESO!", "DÉJAME", "MI AMOR"]


def make(sm, aspects):
    rnd = random.Random(7)
    beats = [b["time_seconds"] for b in sm["beats"]]
    song_end = sm["duration_seconds"]
    total = song_end + TAIL
    bar = sm["bar_seconds"]
    E, BASE, CAM = [], [(0.0, YEL)], []

    def snap(t):
        for b in beats:
            if b >= t - 1e-6:
                return b
        return t

    def add(k, t0, t1, **p):
        p.update(k=k, t0=round(t0, 3), t1=round(min(t1, total), 3))
        E.append(p)
        return p

    def cam_at(t):  # para colocar elementos donde la cámara está mirando
        if not CAM:
            return 0, 0
        prev = CAM[0]
        for c in CAM:
            if c[0] <= t:
                prev = c
        return prev[1], prev[2]

    def place(t, sx, sy, d):  # coordenada de mundo para que salga en (sx, sy) de pantalla en t
        cx, cy = cam_at(t)
        return sx + cx * d, sy + cy * d

    def photo(t0, t1, ph, color, sx, sy, w, d, r, **kw):
        h = round(w * aspects[ph])
        x, y = place(t0, sx, sy, d)
        return add("card", t0, t1, src=f"{ph}_{DUO[color] if color in DUO else 'red'}", w=w, h=h + 20, bg=color,
                   x=x, y=y, d=d, r=r, smear=1, **kw)

    def cut(t0, t1, ph, sx, sy, w, d, c1, c2, tag=True, **kw):
        h = round(w * aspects[ph])
        x, y = place(t0, sx, sy, d)
        e = add("cut", t0, t1, src=ph, w=w, h=h, x=x, y=y, d=d, c1=c1, c2=c2, **kw)
        if tag:  # etiqueta vertical pegada al recorte (como "SILVESTRE DANGOND")
            vx, vy = place(t0 + 0.3, sx + w * 0.5 + 40, sy - h * 0.15, d)
            add("vt", t0 + 0.3, t1 - 0.2, l1="TIKO", l2="DURÁN", fs=46, col=WHITE if c2 != WHITE else INK, x=vx, y=vy, d=d,
                z=14, r=-90, **{"in": "slide", "out": "slide"}, ang=-90, dist=300, wob=kw.get("wob", 0), ph=kw.get("ph", 0))
        return e

    def tape_row(t, x, y, d, bg, col):  # cinta rasgada con pincel, 2-3 en fila diagonal
        txt = rnd.choice(["¡ay, ay, ay!", "mi vida", "mi amor", "¡eso!", "Tiko Durán"])
        n = rnd.choice([2, 3])
        L = rnd.uniform(3.5, 6.0)
        for j in range(n):
            add("tp", t + j * 0.12, t + L + j * 0.12, txt=txt, bg=bg, col=col, fs=54, x=x + j * 230, y=y + j * 90, d=d, z=16,
                r=-14 + rnd.uniform(-4, 4), **{"in": "pop", "out": "pop"}, din=0.4, dout=0.3, beat=0.03)

    # ---------------- cámara: deriva continua, cambia de rumbo por sección
    cx = cy = 0.0
    rot, zoom = -11.0, 1.0
    for i, (t0, world, base, part, en) in enumerate(SECTIONS):
        t1 = SECTIONS[i + 1][0] if i + 1 < len(SECTIONS) else total
        ang = rnd.uniform(0, 6.283)
        sp = 25 + 55 * en
        CAM.append((t0, round(cx, 1), round(cy, 1), rot, zoom))
        cx += sp * (t1 - t0) * (0.8 if world != "mosaico" else 1.4) * (1 if i % 2 else -1) * 0.9
        cy += sp * (t1 - t0) * 0.35 * (1 if (i // 2) % 2 else -1)
        rot = -11.0 + rnd.uniform(-3.5, 3.5)
        zoom = 1.0 + 0.1 * rnd.random()
    CAM.append((total, round(cx, 1), round(cy, 1), rot, zoom))

    # ---------------- rellenos entre secciones (forma que crece = fondo nuevo)
    shapes = ["heart", "circle", "heart", "star", "circle", "heart", "blob"]
    for i, (t0, world, base, part, en) in enumerate(SECTIONS[1:], 1):
        prev_base = SECTIONS[i - 1][2]
        if base == prev_base:
            continue
        shp = shapes[i % len(shapes)]
        sx, sy = rnd.choice([(960, 540), (720, 620), (1200, 480), (1320, 640), (640, 440)])
        x, y = place(t0 - 0.9, sx, sy, 0.6)
        add("fill", t0 - 0.9, t0, shape=shp, c=base, x=x, y=y, d=0.6, z=5, s=70, r=rnd.uniform(-15, 15))
        BASE.append((round(t0, 3), base))
        # contorno blanco que precede al relleno (tejido conector)
        add("line", t0 - 1.5, t0 + 0.6, shape=shp, w=420, h=420, x=x, y=y, d=0.6, z=6, col=WHITE, sw=6,
            din=0.6, dout=0.5, r=rnd.uniform(-20, 20))

    # ---------------- contenido por mundo
    def stream(t0, t1, every, fn):
        t = t0 + rnd.uniform(0.2, 0.9)
        n = 0
        while t < t1 - 1.0:
            fn(snap(t), n)
            n += 1
            t += every * rnd.uniform(0.75, 1.25)

    for i, (t0, world, base, part, en) in enumerate(SECTIONS):
        t1 = SECTIONS[i + 1][0] if i + 1 < len(SECTIONS) else total
        dens = 0.6 + 0.8 * en
        life = lambda: rnd.uniform(6.5, 11.0) / (0.7 + 0.5 * en)

        if world in ("sol", "final", "cola"):
            x, y = place(t0, 960, 560, 0.25)
            add("sun", t0, t1 + 0.05, x=x, y=y, d=0.25, z=2, c=part, w=1500, h=1500, s=1.0, spin=6 + 10 * en,
                **{"in": "zoom", "out": "fade"}, din=1.0, dout=0.4)
            if world == "final" or (world == "sol" and t0 < 1):
                lw = 900
                x, y = place(t0 + 1.0, 960, 500, 1.0)
                add("img", t0 + 1.0, t1 - 0.6, src="logo", w=lw, h=round(lw * aspects["logo"]), x=x, y=y, d=1.0, z=14,
                    beat=0.025, **{"in": "zoom", "out": "pop"}, din=1.2, smear=1)
            if world == "final":
                cut(t0 + 2.0, t1 - 0.5, "t2", 1500, 640, 640, 1.1, part, INK, **{"in": "slide", "out": "pop"}, ang=180, wob=10)
            if world == "cola":
                pass
            else:
                def sol_fn(t, n):
                    side = 1 if n % 2 else -1
                    ph = PHOTOS[(i + n) % len(PHOTOS)]
                    if n % 3 == 0:
                        cut(t, t + life(), ph, 960 + side * 560, 620, 520, 1.15, part, INK, **{"in": "slide", "out": "slide"},
                            ang=0 if side < 0 else 180, wob=12, beat=0.02)
                    elif n % 3 == 1:
                        x, y = place(t, 960 + side * rnd.uniform(300, 700), rnd.uniform(220, 860), 1.3)
                        tape_row(t, x - 200, y, 1.3, WHITE, INK)
                    else:
                        x, y = place(t, rnd.uniform(300, 1600), rnd.uniform(200, 880), 0.9)
                        add("star", t, t + life() * 0.5, c=WHITE if n % 2 else INK, w=110, h=110, x=x, y=y, d=0.9, z=15,
                            vr=40, **{"in": "pop", "out": "pop"}, beat=0.08)
                stream(t0 + 0.5, t1, 3.2 / dens, sol_fn)

        if world == "corazones":
            def cor_fn(t, n):
                ph = PHOTOS[(n + i) % len(PHOTOS)]
                if n % 4 == 0:
                    photo(t, t + life(), ph, part if part in DUO else RED, rnd.uniform(500, 1400), rnd.uniform(380, 700), 380, 1.0,
                          rnd.uniform(-9, 9), **{"in": "slide", "out": "slide"}, ang=rnd.choice([0, 90, 180, -90]), wob=8)
                elif n % 4 == 1:
                    x, y = place(t, rnd.uniform(250, 1650), rnd.uniform(200, 880), 0.8)
                    add("line", t, t + life(), shape="heart", w=rnd.uniform(180, 340), h=0, x=x, y=y, d=0.8, z=9, col=WHITE,
                        sw=7, r=rnd.uniform(-20, 20), vy=-12, din=1.2, dout=0.9)
                elif n % 4 == 2:
                    x, y = place(t, rnd.uniform(250, 1650), rnd.uniform(200, 880), 1.3)
                    add("heart", t, t + life() * 0.7, c=rnd.choice([YEL, WHITE, INK]), w=130, h=120, x=x, y=y, d=1.3, z=15,
                        r=rnd.uniform(-20, 20), **{"in": "pop", "out": "pop"}, beat=0.1, vy=-20)
                else:
                    x, y = place(t, rnd.uniform(400, 1500), rnd.uniform(250, 830), 1.2)
                    tape_row(t, x - 200, y, 1.2, YEL, INK)
            stream(t0, t1, 1.5 / dens, cor_fn)
            x, y = place(t0, 960, 540, 0.3)
            add("ht", t0, t1 + 0.05, c=part if part != WHITE else YEL, w=2600, h=1700, x=x, y=y, d=0.3, z=1, r=8,
                **{"in": "fade", "out": "fade"}, din=1.5, dout=0.3, op=0.35)

        if world in ("corazones", "collage", "noche"):
            # capa ancla: tipografía gigante tenue que atraviesa todo el mundo, sin cortes
            txt = {"corazones": "LA MITAD DE MI VIDA", "collage": "TIKO DURÁN", "noche": "MI REINA"}[world] + " · "
            x, y = place(t0, 960, 540, 0.45)
            add("bt", t0, t1 + 0.05, txt=txt * 4, fs=420, col=tone(base),
                x=x + 2200, y=y, d=0.45, z=2, sx=-60 - 40 * en, **{"in": "fade", "out": "fade"}, din=1.2, dout=0.2)
            if world != "noche":
                x, y = place(t0, 330, 560, 1.05)
                add("lk", t0 + 1.0, t1 - 0.4, parts=("LA MITAD", "DE MI", "VIDA") if world == "corazones" else ("TIKO", "", "DURÁN"),
                    rows=12, rowh=128, fs=118, bg=YEL if base != YEL else RED, col=INK, col2=WHITE if base != YEL else YEL,
                    w=470, h=840, x=x, y=y, d=1.05, z=10, r=-5, speed=70 + 50 * en, **{"in": "slide", "out": "slide"}, ang=90, smear=1)

        if world == "cadena":
            n = 7
            gap = (t1 - t0 - 1.2) / n
            x, y = place(t0, 960, 560, 1.0)
            add("chain", t0, t1, n=n, gap=round(gap, 3), tm=round(t0 + gap * n * 0.55, 3), c=part, c2=YEL if part != YEL else WHITE,
                w=1500, h=200, x=x, y=y, d=1.0, z=12, r=-4, **{"out": "fade"}, dout=0.3)

        if world == "tipo":
            hook = next((h for h in HOOKS if t0 - 2 <= h[0] < t1), None)
            words = (hook[1] if hook else "TIKO DURÁN") + " · "
            first = (hook[1] if hook else "TIKO DURÁN").split()[0].strip("¡!,")
            x, y = place(t0, 760, 600, 0.6)
            add("rt", t0 + 0.1, t1 + 0.05, txt=first, fs=560, col=tone(base), x=x, y=y, d=0.6, z=3, r=0,
                **{"in": "fade", "out": "fade"}, din=0.6, dout=0.2, stag=0.05, vx=-25)
            x, y = place(t0, 960, 860, 1.25)
            add("bt", t0 + 0.4, t1 + 0.05, txt=words * 3, fs=170, col=WHITE, x=x + 1900, y=y, d=1.25, z=13,
                sx=-(260 + 160 * en), **{"in": "fade", "out": "fade"}, din=0.3, dout=0.2)
            x, y = place(t0, 1440, 560, 1.1)
            add("sc", t0 + 0.8, t1 - 0.3, txt=(hook[1].split()[0] if hook else "TIKO"), rows=10, rowh=150, fs=150,
                bg=INK if part != INK else YEL, col=part if part not in (INK, WHITE) else YEL, col2=WHITE,
                w=560, h=760, x=x, y=y, d=1.1, z=10, r=6, speed=90 + 60 * en, **{"in": "slide", "out": "slide"}, ang=-90, smear=1)

            def tipo_fn(t, n):
                ph = PHOTOS[(n + i) % len(PHOTOS)]
                if n % 3 == 0:
                    cut(t, t + life(), ph, rnd.choice([520, 760]), 640, 560, 1.2, part if part not in (WHITE, INK) else YEL,
                        INK if base != INK else WHITE, **{"in": "slide", "out": "slide"}, ang=rnd.choice([0, 90]), wob=14, beat=0.02)
                elif n % 3 == 1:
                    x, y = place(t, rnd.uniform(300, 1600), rnd.uniform(200, 880), 1.35)
                    tape_row(t, x, y, 1.35, WHITE, RED if base != RED else INK)
                else:
                    x, y = place(t, rnd.uniform(300, 1600), rnd.uniform(200, 880), 1.0)
                    add("line", t, t + life() * 0.7, shape=rnd.choice(["xbox", "scribble", "circle"]), w=rnd.uniform(260, 420), h=0,
                        x=x, y=y, d=1.0, z=13, col=WHITE, sw=6, r=rnd.uniform(-15, 15), din=0.7, dout=0.6)
            stream(t0 + 0.6, t1, 2.4 / dens, tipo_fn)

        if world == "collage":
            x, y = place(t0, 960, 540, 0.35)
            add("ht", t0, t1 + 0.05, c=INK, w=2600, h=1700, x=x, y=y, d=0.35, z=1, r=-6, **{"in": "fade", "out": "fade"}, din=1.0, op=0.25)

            def col_fn(t, n):
                ph = PHOTOS[(n * 2 + i) % len(PHOTOS)]
                c = [part if part in DUO else YEL, RED, ORA, CORAL][n % 4]
                if n % 5 in (0, 2):
                    photo(t, t + life() * 1.2, ph, c, rnd.uniform(380, 1540), rnd.uniform(320, 760), rnd.uniform(300, 420),
                          rnd.uniform(0.8, 1.25), rnd.uniform(-12, 12), **{"in": "slide", "out": "slide"},
                          ang=rnd.choice([0, 90, 180, -90, 45]), wob=6)
                elif n % 5 == 1:
                    x, y = place(t, rnd.uniform(300, 1600), rnd.uniform(200, 880), 1.0)
                    add("line", t, t + life() * 0.7, shape="xbox", w=rnd.uniform(280, 460), h=0, x=x, y=y, d=1.0, z=13, col=WHITE,
                        sw=5, r=rnd.uniform(-15, 15), din=0.6, dout=0.5)
                elif n % 5 == 3:
                    x, y = place(t, rnd.uniform(300, 1600), rnd.uniform(200, 880), 1.3)
                    tape_row(t, x, y, 1.3, YEL, INK)
                else:
                    x, y = place(t, rnd.uniform(300, 1600), rnd.uniform(200, 880), 0.7)
                    add("ht", t, t + life(), c=rnd.choice([YEL, WHITE, ORA]), w=rnd.uniform(300, 520), h=rnd.uniform(220, 420),
                        x=x, y=y, d=0.7, z=7, r=rnd.uniform(-15, 15), **{"in": "slide", "out": "slide"}, ang=rnd.choice([0, 180]), op=1)
            stream(t0 + 0.3, t1, 1.3 / dens, col_fn)

        if world == "mosaico":
            x, y = 960, 540
            add("mos", t0, t1 + 0.05, c=part, w=3000, h=2200, x=x, y=y, d=0.0, z=1, r=0, mx=34 + 20 * en, my=10,
                **{"in": "zoom", "out": "fade"}, din=1.2, dout=0.3, tiles=[PHOTOS[(k * 3 + k // 26) % 5] for k in range(26 * 14)])

            def mos_fn(t, n):
                ph = PHOTOS[(n + i * 3) % len(PHOTOS)]
                if n % 3 == 0:
                    cut(t, t + life(), ph, rnd.choice([560, 960, 1360]), 640, 600, 1.25, part, YEL if part != YEL else WHITE,
                        **{"in": "zoom", "out": "slide"}, ang=rnd.choice([0, 180]), wob=16, beat=0.03, lag=0.16)
                elif n % 3 == 1:
                    tj = t
                    x, y = place(tj, 960, rnd.uniform(200, 880), 1.1)
                    add("bt", tj, tj + 6.0, txt=rnd.choice(["TIKO DURÁN", "LA MITAD DE MI VIDA", "¡AY, AY, AY!"]) + " · ",
                        fs=220, col=WHITE if n % 2 else part, x=x + 1700, y=y, d=1.1, z=11, sx=-520, **{"in": "fade", "out": "fade"},
                        din=0.2, dout=0.2)
                else:
                    x, y = place(t, rnd.uniform(300, 1600), rnd.uniform(200, 880), 1.3)
                    add("star", t, t + life() * 0.5, c=YEL, w=120, h=120, x=x, y=y, d=1.3, z=15, vr=60,
                        **{"in": "pop", "out": "pop"}, beat=0.1)
            stream(t0 + 0.8, t1, 2.2 / dens, mos_fn)

        if world == "noche":
            def no_fn(t, n):
                ph = PHOTOS[(n + 1) % len(PHOTOS)]
                if n % 3 == 0:
                    photo(t, t + 9.0, ph, CORAL, rnd.uniform(560, 1360), 540, 420, 0.9, rnd.uniform(-5, 5),
                          **{"in": "fade", "out": "fade"}, din=1.5, dout=1.5, wob=4)
                elif n % 3 == 1:
                    x, y = place(t, rnd.uniform(300, 1600), rnd.uniform(200, 880), 0.7)
                    add("line", t, t + 8.0, shape=rnd.choice(["heart", "arch", "circle"]), w=rnd.uniform(300, 520), h=0, x=x, y=y,
                        d=0.7, z=8, col=WHITE, sw=4, r=rnd.uniform(-10, 10), din=2.0, dout=1.5)
                else:
                    x, y = place(t, rnd.uniform(200, 1700), rnd.uniform(150, 900), 1.2)
                    add("star", t, t + 6.0, c=WHITE, w=60, h=60, x=x, y=y, d=1.2, z=15, vr=20, vx=-30,
                        **{"in": "pop", "out": "fade"}, beat=0.15)
            stream(t0, t1, 1.6, no_fn)

    # ---------------- pase de texto: ganchos que suben letra a letra + acentos en pincel
    for th, txt in HOOKS:
        sec = max((x for x in SECTIONS if x[0] <= th), key=lambda x: x[0])
        base = sec[2]
        x, y = place(th, 960, 300, 1.15)
        add("rt", th, th + 3.4, txt=txt, fs=150, col=INK if base == YEL else WHITE, x=x, y=y, d=1.15, z=17, r=0,
            **{"in": "fade", "out": "fade"}, din=0.45, dout=0.35, stag=0.03)
    for i, (t0, world, base, part, en) in enumerate(SECTIONS):
        t1 = SECTIONS[i + 1][0] if i + 1 < len(SECTIONS) else total
        if world in ("corazones", "collage", "noche", "sol"):
            t = t0 + 2.0
            while t < t1 - 3:
                x, y = place(t, rnd.uniform(500, 1400), rnd.uniform(250, 820), 1.2)
                add("br", snap(t), snap(t) + 3.2, txt=rnd.choice(["mi vida", "mi amor", "la mitad", "mi reina"]), fs=150,
                    col=WHITE if base != YEL else RED, x=x, y=y, d=1.2, z=17, r=-10, **{"in": "fade", "out": "pop"},
                    din=0.2, dout=0.35, smear=1)
                t += rnd.uniform(7, 11)
        if world == "mosaico":
            t, n = t0 + 1.5, 0
            while t < t1 - 3:
                x, y = place(t, 960, 560, 0.9)
                add("rt", snap(t), snap(t) + 5.5, txt=["TIKO", "DURÁN", "LA MITAD", "MI VIDA"][n % 4], fs=640, col=WHITE if n % 2 else part,
                    x=x, y=y, d=0.9, z=8, r=0, **{"in": "fade", "out": "fade"}, din=0.6, dout=0.45, stag=0.06, vx=-40)
                t += 9.0
                n += 1
    E.sort(key=lambda e: (e.get("z", 10), e["t0"]))
    return E, BASE, CAM
