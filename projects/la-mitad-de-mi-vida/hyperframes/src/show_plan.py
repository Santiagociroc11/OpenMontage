"""Plan visual completo de "La mitad de mi vida" (free_run).

Todo el show son datos: secciones (paleta + patrones del shader + mosaico),
pistas de opacidad de elementos, estados del corazón y tarjetas de letra.
`build_show.py` convierte esto en un index.html por tramo de render.

Tiempos en segundos de la grabación (song_map / alineación de la letra).
"""

TAIL = 60.0  # cola de amanecer tras el final de la grabación

# --- Paletas (top, bottom, rayos) -------------------------------------------
NIGHT = ("#03040f", "#0a1650", "#5a78ff")
BLUE = ("#0a0a3c", "#2142ff", "#7f9cff")
SUNSET = ("#4a0640", "#ff6a1a", "#ffb070")
RED = ("#2a0012", "#e3103f", "#ff5d86")
PURPLE = ("#0c0026", "#6a1bd1", "#d07bff")
POP = ("#14002e", "#ff2d8a", "#ffe24a")
DISCO = ("#08001c", "#b0108f", "#ff7ae6")
WARP = ("#000016", "#0d2cff", "#9fd2ff")
NAVY = ("#010208", "#0b1840", "#3c5a9a")
DAWN = ("#ff2f6a", "#ffc53a", "#fff1b0")


def sec(t0, name, pal, *, stars=0.6, rays=0.6, blocks=0.0, spots=0.0, sun=0.0,
        mist=0.0, speed=2.0, mosaic=None):
    """speed = beats por ciclo del campo de estrellas (menor = más rápido)."""
    return dict(t0=t0, name=name, top=pal[0], bot=pal[1], ray=pal[2], stars=stars,
                rays=rays, blocks=blocks, spots=spots, sun=sun, mist=mist,
                speed=speed, mosaic=mosaic)


SECTIONS = [
    sec(0.0, "intro", NIGHT, stars=0.5, rays=0.25, speed=4),
    sec(17.508, "verso1", BLUE, stars=1, rays=0.8, speed=2),
    sec(44.861, "pre1", BLUE, stars=1, rays=0.9, speed=1.5, mosaic="sentir"),
    sec(49.55, "estribillo1", SUNSET, stars=0.8, rays=1, speed=1.5, mosaic="mitad"),
    sec(55.565, "beso1", RED, stars=0.5, rays=1, spots=0.6, speed=1, mosaic="beso"),
    sec(70.891, "motivos1", PURPLE, stars=0.6, rays=0.3, spots=1, speed=1.5, mosaic="amor"),
    sec(84.265, "beso2", RED, stars=0.5, rays=1, spots=0.6, speed=1, mosaic="beso"),
    sec(99.776, "instr_pop", POP, stars=0.2, rays=0.25, blocks=1, speed=1, mosaic="tiko"),
    sec(134.699, "instr_disco", DISCO, stars=1, rays=0.5, spots=1, speed=1),
    sec(170.551, "instr_warp", WARP, stars=1, rays=1, speed=0.75, mosaic="ay"),
    sec(209.328, "verso2", NAVY, stars=0.5, rays=0.1, mist=1, speed=4),
    sec(222.0, "estrella", BLUE, stars=1, rays=0.4, speed=2),
    sec(234.127, "pre2", BLUE, stars=1, rays=0.9, speed=1.5, mosaic="sentir"),
    sec(236.35, "estribillo2", SUNSET, stars=0.9, rays=1, speed=1.25, mosaic="mitad"),
    sec(244.111, "beso3", RED, stars=0.5, rays=1, spots=0.6, speed=1, mosaic="beso"),
    sec(255.721, "motivos2", PURPLE, stars=0.6, rays=0.3, spots=1, speed=1.5, mosaic="amor"),
    sec(270.559, "beso4", RED, stars=0.5, rays=1, spots=0.6, speed=1, mosaic="beso"),
    sec(283.771, "instr_pop2", POP, stars=0.3, rays=0.4, blocks=1, speed=0.75, mosaic="tiko"),
    sec(299.862, "pico_amanecer", DAWN, stars=0.3, rays=1, sun=1, speed=1, mosaic="mitad"),
    sec(318.973, "aplausos", DAWN, stars=0.2, rays=0.6, sun=1, speed=3),
    sec(332.371, "cola", DAWN, stars=0.15, rays=0.5, sun=1, speed=4),
]

MOSAIC = {
    "sentir": "ES QUE YA YO PUEDO SENTIR",
    "mitad": "LA MITAD DE MI VIDA",
    "beso": "DÉJAME SOLO DARTE UN BESO",
    "amor": "LLENARÉ TU VIDA DE AMOR",
    "tiko": "TIKO DURÁN",
    "ay": "AY AY AY MI AMOR",
}

# Momentos de estallido de chispas (unión del corazón / amanecer).
BURSTS = [49.55, 236.35, 299.862]

# --- Corazón: [t, separación px, rotación°, saturación 0-1, opacidad, escala]
HEART = [
    (0.0, 300, 12, 1, 0, 0.9),
    (17.0, 300, 12, 1, 0, 0.9),
    (18.5, 240, 8, 1, 1, 1.0),
    (44.861, 230, 6, 1, 1, 1.0),
    (49.55, 0, 0, 1, 1, 1.0),
    (98.8, 0, 0, 1, 1, 1.0),
    (99.776, 0, 0, 1, 0, 1.3),
    (208.3, 320, 20, 0.25, 0, 0.9),
    (210.0, 320, 20, 0.25, 1, 0.9),
    (221.0, 300, 16, 0.3, 1, 0.9),
    (222.6, 240, 8, 1, 1, 1.0),
    (234.127, 230, 6, 1, 1, 1.0),
    (236.35, 0, 0, 1, 1, 1.08),
    (283.0, 0, 0, 1, 1, 1.08),
    (283.771, 0, 0, 1, 0, 1.3),
    (299.0, 0, 0, 1, 0, 0.8),
    (299.862, 0, 0, 1, 1, 1.18),
    (318.2, 0, 0, 1, 1, 1.18),
    (318.973, 0, 0, 1, 0, 1.4),
]

# --- Opacidad de elementos: id -> [(t, valor), ...] (interpolación suave)
def pulse(t_in, t_out, fade=0.8, v=1.0):
    return [(t_in - fade, 0), (t_in, v), (t_out - fade, v), (t_out, 0)]


TRACKS = {
    "logo-big": [(0, 0), (2.0, 0), (3.4, 1), (16.0, 1), (17.3, 0), *pulse(319.6, 332.0, 0.9)],
    "logo-c": [(0, 0), *pulse(104.0, 134.4), *pulse(288.2, 299.3), (332.6, 0), (334.6, 0.9), (400, 0.9)],
    "title": pulse(8.2, 17.2),
    "ph-profile": pulse(3.0, 17.2, 1.0) + pulse(135.3, 170.2, 1.2) + pulse(319.5, 332.3, 1.0),
    "ph-stage-l": pulse(100.6, 134.4, 0.9) + pulse(300.4, 318.6, 0.9),
    "ph-stage-r": pulse(100.9, 134.4, 0.9) + pulse(300.7, 318.6, 0.9),
    "ph-stage-c": pulse(171.0, 208.6, 1.0),
    "neon-stars": pulse(50.0, 99.6, 0.5) + pulse(236.8, 283.5, 0.5),
    "ring": pulse(49.8, 99.5, 0.4) + pulse(236.6, 283.4, 0.4) + pulse(300.1, 318.7, 0.4),
    "moon-sun": pulse(228.8, 234.4, 0.8),
    "tag": [(0, 0), (17.5, 0), (18.5, 1), (99.0, 1), (99.8, 0), (209.0, 0), (210.0, 1),
            (283.0, 1), (283.8, 0), (300.5, 0), (301.5, 1), (318.5, 1), (319.0, 0)],
}

# Estrella fugaz: cruza el cielo en "te regalo una estrella".
SHOOTING_STAR = (222.2, 2.4)

# --- Letra en pantalla: (t, texto, estilo) — estilos: k, beso, hero, hero2
LYRICS = [
    (19.5, "He venido esta vez a decirte que", "k"),
    (23.8, "He soñado contigo una vez más", "k"),
    (27.0, "Te veías como siempre tan linda tú", "k"),
    (31.0, "Cuánto diera porque fuera realidad", "k"),
    (33.6, "Pero mi vida es solo un mar de olvido", "k"),
    (38.8, "Mi mejor compañera es la soledad", "k"),
    (41.8, "Yo no puedo rogarte que estés conmigo", "k"),
    (44.6, "Tal vez esta canción te va a conquistar", "k"),
    (47.5, "Es que ya yo puedo sentir que tú eres", "k"),
    (49.45, "la mitad de mi vida", "hero"),
    (53.3, "El amor que vendría", "k"),
    (55.9, "Déjame solo darte un beso, déjame", "beso"),
    (59.4, "Mírame, es que estoy temblando, tócame", "beso"),
    (64.0, "Déjame solo darte un beso, déjame", "beso"),
    (67.0, "Mírame, es que estoy temblando, tócame", "beso"),
    (70.9, "Yo sé que tú has tenido mil motivos", "k"),
    (72.9, "Para decir que no te he querido", "k"),
    (74.8, "Pero esta vez llenaré tu vida de amor", "hero2"),
    (77.8, "Solo el tuyo y el mío, corazones", "k"),
    (80.0, "Que van solitos por esta vida", "k"),
    (82.0, "Dejemos ya la melancolía", "k"),
    (84.1, "¡Ay, ay, ay, mi amor!", "beso"),
    (88.0, "Déjame solo darte un beso, déjame", "beso"),
    (95.3, "Mírame, es que estoy temblando, tócame", "beso"),
    (99.8, "¡Ay, ay, ay, mi amor!", "beso"),
    (208.8, "Cómo me duele, mi amor, que no estés aquí", "k"),
    (211.9, "Y hasta todo lo doy por oír tu voz", "k"),
    (215.1, "Si supieras que a mi corazón las penas", "k"),
    (218.7, "Lo han matado, mi reina, no aguanto más", "k"),
    (221.9, "Si tú quieres, yo te regalo una estrella", "k"),
    (226.0, "Por amarte, te juro que cruzo el mar", "k"),
    (228.8, "En la luna y el sol buscaré tu huella", "k"),
    (231.6, "Nunca voy a rendirme, ya lo verás", "k"),
    (234.4, "Es que ya yo puedo sentir que tú eres", "k"),
    (236.3, "la mitad de mi vida", "hero"),
    (240.0, "El amor que vendría", "k"),
    (243.3, "Déjame solo darte un beso, déjame", "beso"),
    (246.4, "Mírame, es que estoy temblando, tócame", "beso"),
    (250.0, "Déjame solo darte un beso, déjame", "beso"),
    (252.6, "Mírame, es que estoy temblando, tócame", "beso"),
    (256.0, "Yo sé que tú has tenido mil motivos", "k"),
    (258.1, "Para decir que no te he querido", "k"),
    (260.0, "Pero esta vez llenaré tu vida de amor", "hero2"),
    (262.2, "Solo el tuyo y el mío, corazones", "k"),
    (264.9, "Que van solitos por esta vida", "k"),
    (266.9, "Dejemos ya la melancolía", "k"),
    (270.6, "Déjame solo darte un beso, déjame", "beso"),
    (273.4, "Mírame, es que estoy temblando, tócame", "beso"),
    (277.3, "Déjame solo darte un beso, déjame", "beso"),
    (280.0, "Mírame, es que estoy temblando, tócame", "beso"),
    (284.0, "¡Ay, ay, ay, mi amor!", "beso"),
]
MAX_CARD = {"k": 3.6, "beso": 3.4, "hero": 4.2, "hero2": 3.4}
