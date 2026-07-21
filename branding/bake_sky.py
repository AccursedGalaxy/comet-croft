#!/usr/bin/env python3
"""Bake the Comet Croft menu sky as a high-resolution photographic still.

The real-time GLSL sky reads soft/mushy at full screen (the loading screen has
no UI to hide it). FancyMenu 3.9.8's GLSL channels can only sample buffer passes
- there is NO way to feed an image texture into a shader - so the photographic
detail has to be BAKED into an image background, with only the fast-moving comet
left to a lightweight GLSL decoration overlay on top.

This script composites that background:
  - a real Moon photo (Wikimedia, CC-BY-SA 3.0, Gregory H. Revera)
  - the real Milky Way band (ESO/S. Brunier, CC-BY 4.0) as a diagonal core band
  - a dense generated starfield with a real point-spread (crisp, not blobs)
  - themed aurora ribbons, layered croft hills, and the warm farmhouse window

Sources live next to this script (downloaded once); output is written to
config/fancymenu/assets/. Attribution belongs in CREDITS.md.
"""

import argparse
import os
import urllib.request
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# Openly-licensed source photos (gitignored; re-fetched on demand). See CREDITS.md.
SOURCES = {
    "moon.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/e1/FullMoon2010.jpg",
    "mw_large.jpg": "https://cdn.eso.org/images/large/eso0932a.jpg",
}


def ensure_sources():
    for name, url in SOURCES.items():
        path = os.path.join(HERE, name)
        if os.path.exists(path):
            continue
        print(f"fetching {name} ...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=90) as r, open(path, "wb") as f:
            f.write(r.read())


def clamp(x, a=0.0, b=1.0):
    return np.minimum(np.maximum(x, a), b)


def smoothstep(e0, e1, x):
    t = clamp((x - e0) / (e1 - e0))
    return t * t * (3.0 - 2.0 * t)


# ---- value noise / fbm (for aurora + hills jitter), vectorised -------------
def _hash2(ix, iy):
    px = np.sin(ix * 127.1 + iy * 311.7) * 43758.5453
    return px - np.floor(px)


def vnoise(px, py):
    ix, iy = np.floor(px), np.floor(py)
    fx, fy = px - ix, py - iy
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    a = _hash2(ix, iy)
    b = _hash2(ix + 1, iy)
    c = _hash2(ix, iy + 1)
    d = _hash2(ix + 1, iy + 1)
    return (a + (b - a) * fx) * (1 - fy) + (c + (d - c) * fx) * fy


def fbm(px, py, oct=5):
    n = np.zeros_like(px)
    amp, freq, norm = 1.0, 1.0, 0.0
    for _ in range(oct):
        n += amp * vnoise(px * freq, py * freq)
        norm += amp
        amp *= 0.5
        freq *= 2.0
    return n / norm


def screen(base, top):
    return 1.0 - (1.0 - base) * (1.0 - top)


# ---- starfield: crisp points with a real point-spread ---------------------
def add_stars(col, rng, count, wgrid):
    H, W, _ = col.shape
    # power-law-ish magnitude: many faint, few bright
    mag = rng.random(count) ** 3.2
    xs = rng.random(count) * W
    ys = rng.random(count) * H
    # colour temperature: mostly cool white, a few warm
    tcol = rng.random(count)
    r = 0.75 + 0.25 * tcol
    g = 0.80 + 0.15 * np.abs(tcol - 0.3)
    b = 1.0 - 0.35 * tcol
    for i in range(count):
        bright = 0.10 + 0.9 * mag[i]
        rad = 0.6 + 3.2 * mag[i]
        x0, y0 = xs[i], ys[i]
        # thin out very low in the sky (near hills)
        if y0 > H * 0.80 and rng.random() < 0.6:
            continue
        R = int(rad * 3) + 2
        xa, xb = max(0, int(x0) - R), min(W, int(x0) + R + 1)
        ya, yb = max(0, int(y0) - R), min(H, int(y0) + R + 1)
        if xa >= xb or ya >= yb:
            continue
        gx = np.arange(xa, xb)[None, :] - x0
        gy = np.arange(ya, yb)[:, None] - y0
        d2 = gx * gx + gy * gy
        core = np.exp(-d2 / (2 * (rad * 0.42) ** 2))
        halo = 0.14 * np.exp(-np.sqrt(d2) / (rad * 1.6))
        s = (core + halo) * bright
        # diffraction spikes on the brightest stars
        if mag[i] > 0.86:
            spike = np.exp(-np.abs(gx) * 0.5) * np.exp(-np.abs(gy) * 6.0) + np.exp(
                -np.abs(gy) * 0.5
            ) * np.exp(-np.abs(gx) * 6.0)
            s = s + spike * bright * 0.5
        col[ya:yb, xa:xb, 0] += s * r[i]
        col[ya:yb, xa:xb, 1] += s * g[i]
        col[ya:yb, xa:xb, 2] += s * b[i]


def load_moon(diam):
    im = Image.open(os.path.join(HERE, "moon.jpg")).convert("RGB")
    a = np.asarray(im).astype(np.float64) / 255.0
    # find disc bbox via luminance threshold
    lum = a.mean(2)
    mask = lum > 0.10
    ys, xs = np.where(mask)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    side = max(y1 - y0, x1 - x0)
    cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
    h = side // 2 + 4
    crop = im.crop((cx - h, cy - h, cx + h, cy + h)).resize((diam, diam), Image.LANCZOS)
    ca = np.asarray(crop).astype(np.float64) / 255.0
    # circular alpha with a soft limb
    gy, gx = np.mgrid[0:diam, 0:diam]
    rr = np.sqrt((gx - diam / 2 + 0.5) ** 2 + (gy - diam / 2 + 0.5) ** 2) / (diam / 2)
    alpha = smoothstep(1.0, 0.94, rr)
    # gentle cool grade + limb darkening so it sits in a night sky
    ca *= np.array([0.94, 0.97, 1.03])
    ca *= (0.82 + 0.18 * smoothstep(1.0, 0.2, rr))[..., None]
    return ca, alpha


def bake(W, H, seed=7):
    aspect = W / H
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    uvx = xx / W
    uvy = 1.0 - yy / H  # 0 bottom .. 1 top
    skyx = (uvx - 0.5) * aspect
    skyy = uvy

    # 1) night gradient (matches the shader palette)
    horizon = np.array([0.085, 0.115, 0.225])
    middle = np.array([0.030, 0.052, 0.130])
    zenith = np.array([0.010, 0.015, 0.052])
    t1 = smoothstep(0.02, 0.46, uvy)[..., None]
    t2 = smoothstep(0.46, 1.0, uvy)[..., None]
    col = horizon * (1 - t1) + middle * t1
    col = col * (1 - t2) + zenith * t2
    col += np.array([0.08, 0.04, 0.11]) * (np.power(1 - uvy, 3.0) * 0.20)[..., None]

    # 2) Milky Way band from the real ESO panorama (galactic core = image centre)
    mw = Image.open(os.path.join(HERE, "mw_large.jpg")).convert("RGB")
    mwa = np.asarray(mw).astype(np.float64) / 255.0
    mh = mwa.shape[0]
    strip = mwa[int(mh * 0.30) : int(mh * 0.70)]  # galactic-plane strip
    strip_im = Image.fromarray((clamp(strip) * 255).astype(np.uint8))
    band_h = int(H * 0.72)
    band = strip_im.resize((int(W * 1.35), band_h), Image.LANCZOS).rotate(
        11, expand=True, resample=Image.BICUBIC
    )
    ba = np.asarray(band).astype(np.float64) / 255.0
    bh, bw, _ = ba.shape
    # place band so its centre sits ~0.66 up the sky
    oy = int(H * (1 - 0.66) - bh / 2)
    ox = int((W - bw) / 2)
    canvas_band = np.zeros((H, W, 3))
    ys0, ys1 = max(0, oy), min(H, oy + bh)
    xs0, xs1 = max(0, ox), min(W, ox + bw)
    by0, by1 = ys0 - oy, ys1 - oy
    bx0, bx1 = xs0 - ox, xs1 - ox
    canvas_band[ys0:ys1, xs0:xs1] = ba[by0:by1, bx0:bx1]
    # cool the panorama toward the night palette, keep dust lanes
    lum = canvas_band.mean(2, keepdims=True)
    graded = canvas_band * np.array([0.55, 0.72, 1.05]) + lum * np.array(
        [0.10, 0.08, 0.06]
    )
    # feather across the band's short axis + fade near horizon
    feather = np.exp(-((uvy - 0.66) ** 2) / (2 * 0.16**2))[..., None]
    band_mask = smoothstep(0.02, 0.14, lum) * feather * 0.85
    col = screen(col, clamp(graded) * band_mask)

    # 3) starfield
    rng = np.random.default_rng(seed)
    add_stars(col, rng, count=5200, wgrid=None)

    # 4) aurora ribbons (soft, themed) high in the sky
    for cy0, amp, colr, spread in [
        (0.78, 0.045, np.array([0.06, 0.34, 0.28]), 0.030),
        (0.86, 0.030, np.array([0.10, 0.16, 0.42]), 0.022),
    ]:
        ribbon = cy0 + amp * np.sin(skyx * 2.6 + 0.4) + 0.5 * amp * np.sin(skyx * 6.0)
        curtain = 0.4 + 0.6 * fbm(skyx * 2.4 + 3, skyy * 2.0)
        glow = np.exp(-((uvy - ribbon) ** 2) / (2 * spread**2))
        # fade the aurora away from the moon so it doesn't read as a halo
        moon_fade = smoothstep(0.16, 0.44, np.abs(skyx - (-0.39 * aspect)))
        col += colr * (glow * curtain * 0.34 * moon_fade)[..., None]

    # 5) moon (real photo) with a soft glow, upper-left
    diam = int(H * 0.135)
    mcol, malpha = load_moon(diam)
    mx = int(W * 0.11)
    my = int(H * 0.20)
    # glow
    gd = np.sqrt((xx - mx) ** 2 + (yy - my) ** 2)
    glow = np.exp(-gd / (diam * 0.85))
    col += np.array([0.35, 0.45, 0.68]) * (glow * 0.16)[..., None]
    # disc
    y0 = my - diam // 2
    x0 = mx - diam // 2
    ys0, ys1 = max(0, y0), min(H, y0 + diam)
    xs0, xs1 = max(0, x0), min(W, x0 + diam)
    a = malpha[ys0 - y0 : ys1 - y0, xs0 - x0 : xs1 - x0][..., None]
    mc = mcol[ys0 - y0 : ys1 - y0, xs0 - x0 : xs1 - x0]
    col[ys0:ys1, xs0:xs1] = col[ys0:ys1, xs0:xs1] * (1 - a) + mc * a * 1.15

    # 6) layered croft hills
    far = 0.125 + 0.020 * np.sin(skyx * 2.1 + 0.6) + 0.012 * np.sin(skyx * 5.4 - 1.2)
    near = 0.070 + 0.027 * np.sin(skyx * 2.8 - 0.5) + 0.014 * np.sin(skyx * 7.5 + 1.1)
    m1 = smoothstep(far + 0.004, far - 0.004, uvy)[..., None] * 0.85
    col = col * (1 - m1) + np.array([0.022, 0.038, 0.082]) * m1
    m2 = smoothstep(near + 0.004, near - 0.004, uvy)[..., None] * 0.95
    col = col * (1 - m2) + np.array([0.008, 0.017, 0.043]) * m2

    # 7) the croft: a warm lit window on the near hill
    winx = 0.34 * aspect
    nh = 0.070 + 0.027 * np.sin(winx * 2.8 - 0.5) + 0.014 * np.sin(winx * 7.5 + 1.1)
    wpx, wpy = winx, nh - 0.028
    wd = np.sqrt((skyx - wpx) ** 2 + (skyy - wpy) ** 2)
    pane = smoothstep(
        0.012, 0.004, np.maximum(np.abs(skyx - wpx) * 1.9, np.abs(skyy - wpy) * 3.0)
    )
    wglow = np.exp(-wd * wd * 300.0)
    haze = np.exp(-wd * 24.0) * smoothstep(-0.03, 0.09, skyy - wpy)
    col += np.array([1.00, 0.63, 0.29]) * (wglow * 0.5)[..., None]
    col += np.array([1.00, 0.80, 0.52]) * (pane * 0.95)[..., None]
    col += np.array([1.00, 0.66, 0.34]) * (haze * 0.05)[..., None]

    # 8) vignette + filmic rolloff
    vu = uvx * (1 - uvx)
    vv = uvy * (1 - uvy)
    vig = np.power(clamp(vu * vv * 16.0), 0.15)
    col *= (0.74 + 0.26 * vig)[..., None]
    col = col / (1.0 + col * 0.30)

    out = (clamp(col) * 255 + 0.5).astype(np.uint8)
    img = Image.fromarray(out, "RGB")
    # a whisper of bloom for the bright points
    bloom = img.filter(ImageFilter.GaussianBlur(3))
    img = Image.blend(img, bloom, 0.12)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=int, default=3440)
    ap.add_argument("--h", type=int, default=1440)
    ap.add_argument(
        "--out", default=os.path.join(REPO, "config/fancymenu/assets/menu_sky.jpg")
    )
    ap.add_argument("--preview", default=None, help="also write a preview copy here")
    args = ap.parse_args()
    ensure_sources()
    img = bake(args.w, args.h)
    img.save(args.out)
    print("wrote", args.out, img.size)
    if args.preview:
        img.save(args.preview)
        print("wrote", args.preview)


if __name__ == "__main__":
    main()
