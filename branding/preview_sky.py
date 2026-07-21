#!/usr/bin/env python3
"""Offline numpy renderer for branding/menu_sky.glsl.

Faithful CPU port of the FancyMenu title-screen shader so sky changes can be
eyeballed as PNGs without launching the modded client. Not a substitute for the
final in-engine `testing/e2e.py client` check, just a fast iteration loop.

Usage:
  python3 branding/preview_sky.py [--time T ...] [--w W] [--h H] [--out DIR]

Renders one PNG per --time value (default a spread incl. a comet frame).
"""

import argparse
import os
import numpy as np
from PIL import Image

TAU = 6.28318530718


def fract(x):
    return x - np.floor(x)


def clamp(x, a, b):
    return np.minimum(np.maximum(x, a), b)


def smoothstep(e0, e1, x):
    t = clamp((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def step(edge, x):
    return (x >= edge).astype(np.float64)


def hash21(px, py):
    px = fract(px * 123.34)
    py = fract(py * 456.21)
    d = px * (px + 45.32) + py * (py + 45.32)
    px = px + d
    py = py + d
    return fract(px * py)


def vnoise(px, py):
    ix, iy = np.floor(px), np.floor(py)
    fx, fy = px - ix, py - iy
    fx = fx * fx * (3.0 - 2.0 * fx)
    fy = fy * fy * (3.0 - 2.0 * fy)
    a = hash21(ix, iy)
    b = hash21(ix + 1.0, iy)
    c = hash21(ix, iy + 1.0)
    d = hash21(ix + 1.0, iy + 1.0)
    return (a + (b - a) * fx) * (1 - fy) + (c + (d - c) * fx) * fy


def fbm(px, py):
    n = vnoise(px, py) * 0.58
    n += vnoise(px * 2.03 + 7.1, py * 2.03 + 7.1) * 0.28
    n += vnoise(px * 4.01 + 13.7, py * 4.01 + 13.7) * 0.14
    return n


def length2(x, y):
    return np.sqrt(x * x + y * y)


def star_layer(px, py, scale, threshold, radius, speed, itime):
    gx, gy = px * scale, py * scale
    idx, idy = np.floor(gx), np.floor(gy)
    qx, qy = gx - idx - 0.5, gy - idy - 0.5
    h = hash21(idx, idy)
    offx = (hash21(idx + 17.2, idy + 17.2) - 0.5) * 0.62
    offy = (hash21(idx + 31.7, idy + 31.7) - 0.5) * 0.62
    qx = qx - offx
    qy = qy - offy
    present = step(threshold, h)
    twinkle = 0.72 + 0.28 * np.sin(itime * speed * (0.65 + h) + h * 41.0)
    core = smoothstep(radius, radius * 0.18, length2(qx, qy))
    rays = np.exp(-np.abs(qx) * 38.0) * np.exp(-np.abs(qy) * 5.0) + np.exp(
        -np.abs(qy) * 38.0
    ) * np.exp(-np.abs(qx) * 5.0)
    bright = smoothstep(0.975, 1.0, h)
    value = present * twinkle * (core + rays * bright * 0.18)
    t = hash21(idx + 5.4, idy + 5.4)
    tr = 0.62 + (1.0 - 0.62) * t
    tg = 0.76 + (0.88 - 0.76) * t
    tb = 1.0 + (0.68 - 1.0) * t
    return tr * value, tg * value, tb * value


def render(itime, W, H):
    # fragCoord: origin bottom-left (row 0 of image is top => uv.y flips)
    xs = np.arange(W) + 0.5
    ys = np.arange(H) + 0.5
    fx = np.tile(xs, (H, 1))
    fy = np.tile(ys[:, None], (1, W))
    uvx = fx / W
    uvy = fy / H  # 0..1 bottom..top in shader space
    # image row 0 should be top => build so that top row has uvy~1
    uvy = 1.0 - uvy
    aspect = W / H
    skyx = (uvx - 0.5) * aspect
    skyy = uvy

    horizon = np.array([0.105, 0.145, 0.270])
    middle = np.array([0.040, 0.065, 0.155])
    zenith = np.array([0.012, 0.018, 0.060])
    t1 = smoothstep(0.02, 0.48, uvy)[..., None]
    col = horizon * (1 - t1) + middle * t1
    t2 = smoothstep(0.48, 1.0, uvy)[..., None]
    col = col * (1 - t2) + zenith * t2
    col = (
        col
        + np.array([0.09, 0.045, 0.12]) * (np.power(1.0 - uvy, 3.0) * 0.24)[..., None]
    )

    galaxy_axis = uvy - (0.60 + 0.11 * np.sin(skyx * 0.85 + 0.4))
    galaxy = np.exp(-galaxy_axis * galaxy_axis * 30.0)
    dust = fbm(skyx * 2.3, skyy * 7.0 + itime * 0.006)
    dark_rift = fbm(skyx * 3.2 + 19.0, skyy * 10.0 + 19.0)
    gcol = (
        np.array([0.10, 0.15, 0.27]) * (1 - dust)[..., None]
        + np.array([0.21, 0.13, 0.29]) * dust[..., None]
    )
    col = col + gcol * (galaxy * smoothstep(0.22, 0.85, dust) * 0.40)[..., None]
    col = (
        col
        - np.array([0.025, 0.030, 0.055])
        * (galaxy * smoothstep(0.58, 0.82, dark_rift))[..., None]
    )

    ax = skyx
    ribbon1 = (
        0.78
        + 0.035 * np.sin(ax * 2.8 + itime * 0.055)
        + 0.018 * np.sin(ax * 7.0 - itime * 0.035)
    )
    ribbon2 = 0.84 + 0.025 * np.sin(ax * 3.6 - itime * 0.042 + 2.0)
    aurora1 = np.exp(-np.abs(uvy - ribbon1) * 24.0)
    aurora2 = np.exp(-np.abs(uvy - ribbon2) * 32.0)
    curtain = 0.35 + 0.65 * fbm(
        ax * 3.0 + itime * 0.025, np.full_like(ax, itime * 0.018)
    )
    col = col + np.array([0.055, 0.32, 0.25]) * (aurora1 * curtain * 0.24)[..., None]
    col = (
        col
        + np.array([0.12, 0.16, 0.42])
        * (aurora2 * (1.0 - curtain * 0.35) * 0.19)[..., None]
    )

    horizon_fade = smoothstep(0.06, 0.24, uvy)
    s0 = star_layer(skyx, skyy, 28.0, 0.91, 0.105, 1.15, itime)
    s1 = star_layer(skyx + 8.7, skyy + 3.1, 57.0, 0.945, 0.115, 1.75, itime)
    s2 = star_layer(skyx + 21.3, skyy + 9.8, 105.0, 0.968, 0.13, 2.25, itime)
    stars = np.stack(
        [
            s0[0] * 0.84 + s1[0] * 0.70 + s2[0] * 0.48,
            s0[1] * 0.84 + s1[1] * 0.70 + s2[1] * 0.48,
            s0[2] * 0.84 + s1[2] * 0.70 + s2[2] * 0.48,
        ],
        axis=-1,
    )
    col = col + stars * horizon_fade[..., None]

    moonx, moony = -0.39 * aspect, 0.73
    moon_dist = length2(skyx - moonx, skyy - moony)
    moon_glow = np.exp(-moon_dist * 22.0)
    moon_disc = smoothstep(0.020, 0.015, moon_dist)
    col = col + np.array([0.34, 0.43, 0.68]) * (moon_glow * 0.12)[..., None]
    col = col + np.array([0.82, 0.88, 1.0]) * (moon_disc * 0.52)[..., None]

    # Comet
    period, duration = 22.0, 5.2
    local_time = (itime + period - 2.0) % period
    cycle = np.floor((itime + period - 2.0) / period)
    if local_time < duration:
        t = local_time / duration
        eased = t * t * (3.0 - 2.0 * t)
        seed = float(hash21(np.array(cycle), np.array(6.4)))
        sx, sy = -0.62 * aspect, 0.86 - seed * 0.06
        ex, ey = 0.62 * aspect, 0.55 + seed * 0.12
        bendy = np.sin(t * np.pi) * 0.035
        posx = sx + (ex - sx) * eased
        posy = sy + (ey - sy) * eased + bendy
        vx, vy = ex - sx, ey - sy + np.cos(t * np.pi) * 0.08
        vlen = np.hypot(vx, vy)
        vx, vy = vx / vlen, vy / vlen
        nx, ny = -vy, vx
        relx, rely = skyx - posx, skyy - posy
        back = -(relx * vx + rely * vy)
        across = relx * nx + rely * ny
        visible = smoothstep(0.0, 0.13, t) * (1.0 - smoothstep(0.82, 1.0, t))
        taper = smoothstep(0.42, 0.0, back) * step(0.0, back)
        tail_core = np.exp(-across * across * 9000.0) * taper
        tail_glow = (
            np.exp(-np.abs(across) * 78.0)
            * smoothstep(0.48, 0.0, back)
            * step(0.0, back)
        )
        split = (
            np.exp(-np.power(across - back * 0.024, 2.0) * 12500.0)
            * smoothstep(0.36, 0.04, back)
            * step(0.03, back)
        )
        head = np.exp(-(relx * relx + rely * rely) * 12500.0)
        halo = np.exp(-length2(relx, rely) * 115.0)
        col = (
            col + np.array([0.30, 0.56, 1.00]) * (tail_glow * 0.30 * visible)[..., None]
        )
        col = (
            col
            + np.array([0.64, 0.82, 1.00])
            * ((tail_core + split * 0.38) * 0.78 * visible)[..., None]
        )
        col = col + np.array([0.62, 0.78, 1.00]) * (halo * 0.48 * visible)[..., None]
        col = col + np.array([1.00, 0.93, 0.72]) * (head * 2.1 * visible)[..., None]

    far_hill = (
        0.125 + 0.020 * np.sin(skyx * 2.1 + 0.6) + 0.012 * np.sin(skyx * 5.4 - 1.2)
    )
    near_hill = (
        0.070 + 0.027 * np.sin(skyx * 2.8 - 0.5) + 0.014 * np.sin(skyx * 7.5 + 1.1)
    )
    m1 = smoothstep(far_hill + 0.006, far_hill - 0.006, uvy) * 0.82
    col = col * (1 - m1[..., None]) + np.array([0.026, 0.043, 0.090]) * m1[..., None]
    m2 = smoothstep(near_hill + 0.005, near_hill - 0.005, uvy) * 0.94
    col = col * (1 - m2[..., None]) + np.array([0.010, 0.020, 0.047]) * m2[..., None]

    # The croft: a single warm lit window on the near hill.
    win_x = 0.34 * aspect
    near_hill_at_win = (
        0.070 + 0.027 * np.sin(win_x * 2.8 - 0.5) + 0.014 * np.sin(win_x * 7.5 + 1.1)
    )
    win_px, win_py = win_x, near_hill_at_win - 0.028
    wdx, wdy = skyx - win_px, skyy - win_py
    flicker = 0.92 + 0.08 * np.sin(itime * 1.3) * np.sin(itime * 0.7 + 1.0)
    window_pane = smoothstep(
        0.011, 0.004, np.maximum(np.abs(wdx) * 1.9, np.abs(wdy) * 3.0)
    )
    window_glow = np.exp(-(wdx * wdx + wdy * wdy) * 300.0)
    window_haze = np.exp(-length2(wdx, wdy) * 24.0) * smoothstep(
        -0.03, 0.09, skyy - win_py
    )
    col = col + np.array([1.00, 0.63, 0.29]) * (window_glow * 0.42 * flicker)[..., None]
    col = col + np.array([1.00, 0.80, 0.52]) * (window_pane * 0.85 * flicker)[..., None]
    col = (
        col + np.array([1.00, 0.66, 0.34]) * (window_haze * 0.045 * flicker)[..., None]
    )

    vign_uv_x = uvx * (1.0 - uvy)
    vign_uv_y = uvy * (1.0 - uvx)
    vignette = np.power(clamp(vign_uv_x * vign_uv_y * 18.0, 0.0, 1.0), 0.13)
    col = col * (0.72 + (1.0 - 0.72) * vignette)[..., None]
    col = col / (1.0 + col * 0.32)
    out = (clamp(col, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
    return Image.fromarray(out, "RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--time", type=float, nargs="*", default=[6.0, 15.0, 21.5])
    ap.add_argument("--w", type=int, default=1690)
    ap.add_argument("--h", type=int, default=1352)
    ap.add_argument(
        "--out",
        default="/tmp/claude-1000/-home-aki-dev-comet-croft/28ffd7b6-6597-4dec-8266-9dd5e9baafbe/scratchpad",
    )
    ap.add_argument("--tag", default="cur")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for t in args.time:
        img = render(t, args.w, args.h)
        p = os.path.join(args.out, f"sky_{args.tag}_t{t:g}.png")
        img.save(p)
        print(p)


if __name__ == "__main__":
    main()
