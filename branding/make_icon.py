#!/usr/bin/env python3
"""Comet Croft pack icon: 32x32 pixel art, scaled crisply to all sizes.
Scene: a comet arcs over a dark croft; one lantern-lit window answers it."""

from PIL import Image

W = H = 32
# palette
SKY_TOP = (9, 12, 34)
SKY_MID = (14, 20, 48)
SKY_LOW = (22, 32, 68)
SKY_HORIZON = (33, 47, 92)
STAR_BRIGHT = (232, 238, 255)
STAR_DIM = (150, 165, 210)
STAR_FAINT = (90, 105, 155)
COMET_CORE = (255, 255, 250)
COMET_INNER = (190, 235, 255)
COMET_TAIL = (120, 185, 235)
COMET_FADE = (60, 105, 170)
MOUNTAIN = (16, 23, 52)
MOUNTAIN_SNOW = (58, 74, 120)
HILL = (7, 10, 22)
HOUSE = (3, 5, 12)
WINDOW = (255, 176, 58)
WINDOW_GLOW = (120, 72, 30)
SMOKE = (52, 62, 96)
ROOF = (24, 32, 62)

img = Image.new("RGB", (W, H))
px = img.load()

# sky gradient bands
for y in range(H):
    if y < 8:
        c = SKY_TOP
    elif y < 15:
        c = SKY_MID
    elif y < 20:
        c = SKY_LOW
    else:
        c = SKY_HORIZON
    for x in range(W):
        px[x, y] = c

# stars (hand-placed, deterministic)
for x, y in [(2, 3), (6, 9), (11, 2), (17, 12), (28, 14), (30, 3), (21, 16), (4, 17)]:
    px[x, y] = STAR_DIM
for x, y in [(9, 6), (25, 12), (14, 15), (29, 8)]:
    px[x, y] = STAR_FAINT
for x, y in [(4, 12), (19, 4)]:
    px[x, y] = STAR_BRIGHT

# comet: head lower-right of its arc, tail sweeping up-left
tail = [
    (8, 2),
    (9, 2),
    (10, 3),
    (11, 3),
    (12, 4),
    (13, 4),
    (14, 5),
    (15, 5),
    (16, 6),
    (17, 6),
    (18, 7),
]
for i, (x, y) in enumerate(tail):
    px[x, y] = COMET_FADE if i < 4 else COMET_TAIL
# inner tail brightening toward head
for x, y in [(17, 7), (18, 8), (19, 7), (19, 8), (20, 8)]:
    px[x, y] = COMET_TAIL
for x, y in [(20, 9), (21, 8), (21, 9)]:
    px[x, y] = COMET_INNER
# head 2x2 core + glow
for x, y in [(22, 9), (23, 9), (22, 10), (23, 10)]:
    px[x, y] = COMET_CORE
for x, y in [(24, 9), (24, 10), (23, 8), (22, 11), (23, 11), (21, 10)]:
    px[x, y] = COMET_INNER

# distant mountain ridge (Tectonic skyline), rows ~20-25
ridge = [
    22,
    21,
    20,
    21,
    22,
    23,
    22,
    21,
    22,
    23,
    24,
    23,
    22,
    23,
    24,
    24,
    23,
    22,
    23,
    24,
    25,
    24,
    23,
    22,
    23,
    24,
    24,
    23,
    22,
    21,
    22,
    23,
]
for x in range(W):
    top = ridge[x]
    for y in range(top, 26):
        px[x, y] = MOUNTAIN
    # snow cap: peak pixels
    if ridge[x] <= 21:
        px[x, top] = MOUNTAIN_SNOW

# foreground hill, rows 26-31 with gentle slope
hill = [
    27,
    27,
    26,
    26,
    26,
    27,
    27,
    27,
    26,
    26,
    26,
    26,
    27,
    27,
    27,
    27,
    27,
    27,
    26,
    26,
    26,
    26,
    26,
    27,
    27,
    27,
    27,
    28,
    28,
    28,
    28,
    28,
]
for x in range(W):
    for y in range(hill[x], H):
        px[x, y] = HILL

# croft: small house on the hill, left-of-center
# walls x 8-15, y 25-27; roof above; chimney; 2x2 lantern window
for x in range(8, 16):
    for y in range(25, 28):
        px[x, y] = HOUSE
# pitched roof in a slightly lighter tone, with overhang
for x in range(7, 17):
    px[x, 24] = ROOF
for x in range(9, 15):
    px[x, 23] = ROOF
for x in range(11, 13):
    px[x, 22] = ROOF
# chimney rising past the roofline
px[14, 22] = HOUSE
px[14, 21] = HOUSE
# smoke drifting
px[15, 19] = SMOKE
px[16, 18] = SMOKE
# the lantern-lit window, 2x2
for x, y in [(10, 26), (11, 26), (10, 27), (11, 27)]:
    px[x, y] = WINDOW
# warm spill on the wall
for x, y in [(9, 26), (9, 27), (12, 26), (12, 27)]:
    px[x, y] = WINDOW_GLOW

img.save("icon-32.png")
for s in (16, 64, 128, 256, 512):
    img.resize((s, s), Image.NEAREST).save(f"icon-{s}.png")
print("done")
