"""Plan v2 de "La mitad de mi vida": catálogo de 12 escenas, paleta amarillo + compañero.

Cada colocación (PLACEMENTS) es un clip de render independiente y cacheado:
cambiar una fila solo re-renderiza ese clip (y el siguiente, que funde desde él).
Tiempos en segundos de la grabación. La letra son solo acentos de gancho,
verificados contra la alineación Whisper (lyrics/alineado.json).
"""

TAIL = 60.0          # cola holdable de amanecer tras el final de la grabación
XFADE_BARS = 1.0     # fundido entre escenas, en compases

YELLOW = "#ffd23a"
INK = "#1c0418"
PARTNERS = {
    "coral": "#ff3b5c",
    "magenta": "#e0168a",
    "morado": "#7a2bd9",
    "naranja": "#ff7a1a",
    "turquesa": "#12b8c4",
}

# id de escena -> índice en el shader
SCENES = {
    "sol": 1, "tunel": 2, "acordeon": 3, "ondas": 4, "warhol": 5, "britto": 6,
    "caleido": 7, "paisaje": 8, "haces": 9, "confeti": 10, "tiko": 11, "estrellas": 12,
    "bombillas": 13, "zebra": 14, "liquido": 15, "fachada": 16, "cubos": 17,
}

# (inicio, escena, color compañero, energía 0.5-1.6, extras)
PLACEMENTS = [
    (0.0, "sol", "coral", 0.5, {"logo": True}),
    (17.508, "paisaje", "coral", 0.8, {}),
    (31.0, "caleido", "morado", 0.8, {}),
    (44.861, "tunel", "magenta", 1.0, {}),
    (49.55, "sol", "coral", 1.2, {}),
    (55.565, "warhol", "magenta", 1.2, {}),
    (70.891, "liquido", "naranja", 1.1, {}),
    (84.265, "bombillas", "magenta", 1.3, {}),
    (99.776, "acordeon", "coral", 1.3, {}),
    (113.0, "zebra", "turquesa", 1.4, {}),
    (126.0, "britto", "turquesa", 1.3, {}),
    (139.0, "haces", "magenta", 1.4, {}),
    (152.0, "cubos", "magenta", 1.4, {}),
    (165.0, "tiko", "naranja", 1.5, {}),
    (178.0, "tunel", "naranja", 1.6, {}),
    (191.0, "caleido", "coral", 1.4, {}),
    (209.328, "estrellas", "morado", 0.6, {}),
    (222.0, "fachada", "morado", 0.8, {}),
    (234.127, "tunel", "coral", 1.1, {}),
    (236.35, "sol", "coral", 1.2, {}),
    (244.111, "warhol", "coral", 1.2, {}),
    (255.721, "ondas", "magenta", 1.3, {}),
    (270.559, "confeti", "morado", 1.3, {}),
    (283.771, "bombillas", "naranja", 1.5, {}),
    (291.8, "acordeon", "naranja", 1.5, {}),
    (299.862, "sol", "coral", 1.4, {}),
    (318.973, "sol", "coral", 0.8, {"logo": True, "photo": True}),
    (332.371, "sol", "coral", 0.5, {"logo": True}),
]

# Acentos de letra: (inicio, fin, texto, estilo). Solo ganchos oídos con claridad.
LYRICS = [
    (49.5, 52.6, "la mitad de mi vida", "hero"),
    (56.0, 59.4, "Déjame solo darte un beso", "k"),
    (84.1, 87.0, "¡Ay, ay, ay, mi amor!", "k"),
    (236.4, 239.6, "la mitad de mi vida", "hero"),
    (244.0, 247.4, "Déjame solo darte un beso", "k"),
    (284.0, 287.0, "¡Ay, ay, ay, mi amor!", "k"),
]
