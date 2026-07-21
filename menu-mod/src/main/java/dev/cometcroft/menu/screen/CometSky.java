package dev.cometcroft.menu.screen;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import net.minecraft.client.gui.GuiGraphicsExtractor;
import org.joml.Matrix3x2fStack;

/**
 * The living night sky + horizon scene, shared by every Comet Croft screen
 * (title screen, loading overlay). Owns its own animation clock, parallax
 * easing, star field, constellations, periodic comet, sparse meteors, the
 * procedural pixel moon, and the croft silhouette on the horizon.
 *
 * <p>Usage per frame: {@link #tick(int, int, int, int)} then
 * {@link #render(GuiGraphicsExtractor, int, int)}. {@link #time()} exposes the
 * scene clock so host screens can sync their own pulses (splash, toasts) to it.
 */
public final class CometSky {

    // --- palette (design tokens, ARGB) ---
    private static final int NIGHT_TOP = 0xFF070C18;
    private static final int NIGHT_MID = 0xFF0D1730;
    private static final int NIGHT_LOW = 0xFF16264A;
    private static final int HORIZON_BACK = 0xFF0E1830;
    private static final int HORIZON_FRONT = 0xFF0A1322;
    private static final int WINDOW = 0xFFFFCF87;
    private static final int STAR_COOL = 0xFFDFE8FF;
    private static final int STAR_WARM = 0xFFFFE6C0;

    // constellation point sets (normalized sky coords)
    private static final float[][][] CONSTELLATIONS = {
        {{0.62f, 0.14f}, {0.68f, 0.22f}, {0.60f, 0.28f}, {0.72f, 0.30f}},
        {{0.44f, 0.10f}, {0.50f, 0.16f}, {0.43f, 0.22f}, {0.54f, 0.24f}},
    };

    private static final class Meteor {
        float x, y, vx, vy, life, max;
    }

    // star field, generated once per instance (stable across resizes)
    private final float[] starX, starY, starR, starPh, starTw;
    private final boolean[] starWarm;

    // procedural pixel moon: 22x22 palette indices, -1 = transparent
    private static final int MOON_N = 22;
    private static final int[] MOON_PALETTE = {
        0xFFF6EAD0, 0xFFE8D6AE, 0xFFD6C193, 0xFFBFA87B, 0xFFA48F63, 0xFF84714D
    };
    private final byte[] moonPixels = new byte[MOON_N * MOON_N];

    // animation clock
    private long lastFrameNanos = System.nanoTime();
    private float t; // seconds since creation

    // eased mouse (normalized 0..1), for smooth parallax
    private float mouseEx = 0.5f, mouseEy = 0.5f;

    // comet + meteors
    private float cometNext = 3.5f;
    private float cometT = -1f; // <0 idle
    private final List<Meteor> meteors = new ArrayList<>();
    private final Random anim = new Random();

    public CometSky() {
        int n = 200;
        starX = new float[n]; starY = new float[n]; starR = new float[n];
        starPh = new float[n]; starTw = new float[n]; starWarm = new boolean[n];
        Random stars = new Random(0xC0FFEE);
        for (int i = 0; i < n; i++) {
            starX[i] = stars.nextFloat();
            starY[i] = stars.nextFloat() * 0.80f;
            starR[i] = 0.6f + stars.nextFloat() * 1.7f;
            starPh[i] = stars.nextFloat() * 6.28f;
            starTw[i] = 0.5f + stars.nextFloat() * 1.6f;
            starWarm[i] = stars.nextFloat() < 0.12f;
        }
        bakeMoon();
    }

    /** Scene clock, in seconds since this sky was created. */
    public float time() {
        return t;
    }

    /** Advance the clock, ease the parallax target, spawn/retire comet + meteors. */
    public void tick(int mouseX, int mouseY, int w, int h) {
        long now = System.nanoTime();
        float dt = Math.min(0.05f, (now - lastFrameNanos) / 1_000_000_000f);
        lastFrameNanos = now;
        t += dt;

        // ease the mouse toward its target; frame-rate independent
        float k = 1f - (float) Math.pow(0.002, dt); // ~full settle in ~1s
        mouseEx += (mouseX / (float) Math.max(1, w) - mouseEx) * k;
        mouseEy += (mouseY / (float) Math.max(1, h) - mouseEy) * k;

        // comet
        if (cometT < 0f) {
            cometNext -= dt;
            if (cometNext <= 0f) cometT = 0f;
        } else {
            cometT += dt / 6.5f;
            if (cometT >= 1f) {
                cometT = -1f;
                cometNext = 14f + anim.nextFloat() * 13f;
            }
        }

        // meteors: sparse spawns
        if (anim.nextFloat() < dt * 0.5f) {
            Meteor m = new Meteor();
            double a = Math.PI * (0.72 + anim.nextFloat() * 0.12);
            m.x = 0.2f + anim.nextFloat() * 0.7f;
            m.y = anim.nextFloat() * 0.4f;
            m.vx = (float) Math.cos(a) * 0.9f;
            m.vy = (float) Math.sin(a) * 0.9f;
            m.max = 0.45f + anim.nextFloat() * 0.3f;
            meteors.add(m);
        }
        meteors.removeIf(m -> {
            m.life += dt;
            m.x += m.vx * dt;
            m.y += m.vy * dt;
            return m.life >= m.max;
        });
    }

    /** Draw the full scene: gradients, stars, comet, meteors, moon, horizon. */
    public void render(GuiGraphicsExtractor gfx, int w, int h) {
        float px = mouseEx - 0.5f;
        float py = mouseEy - 0.5f;

        // layered night gradient
        gfx.fillGradient(0, 0, w, (int) (h * 0.45f), NIGHT_TOP, NIGHT_MID);
        gfx.fillGradient(0, (int) (h * 0.45f), w, (int) (h * 0.80f), NIGHT_MID, NIGHT_LOW);
        gfx.fillGradient(0, (int) (h * 0.80f), w, h, NIGHT_LOW, 0xFF1B2338);

        // hearth glow rising near the croft (lower-right): one wide, soft gradient
        gfx.fillGradient((int) (w * 0.50f), (int) (h * 0.68f), w, h, 0x00FF963C, 0x1CFF963C);

        drawConstellations(gfx, w, h, px, py);
        drawStars(gfx, w, h, px, py);
        if (cometT >= 0f) drawComet(gfx, w, h);
        drawMeteors(gfx, w, h);
        drawMoon(gfx, w, h, px, py);
        drawHorizon(gfx, w, h);
    }

    /** Bake the 22x22 pixel moon (lit upper-left, cratered) into a palette-index grid. */
    private void bakeMoon() {
        float cx = (MOON_N - 1) / 2f, cy = (MOON_N - 1) / 2f, radius = MOON_N / 2f - 0.4f;
        float[][] craters = {{8, 7, 2.6f}, {13.5f, 12.5f, 3f}, {6, 14, 1.7f}, {15, 6, 1.3f}, {11, 16, 1.4f}};
        for (int y = 0; y < MOON_N; y++) {
            for (int x = 0; x < MOON_N; x++) {
                float dx = x - cx, dy = y - cy;
                float d = (float) Math.hypot(dx, dy);
                if (d > radius) { moonPixels[y * MOON_N + x] = -1; continue; }
                float l = 0.62f - (dx + dy) / (MOON_N * 1.5f) - (d / radius) * (d / radius) * 0.18f;
                float cr = 0;
                for (float[] k : craters) {
                    float cd = (float) Math.hypot(x - k[0], y - k[1]);
                    if (cd < k[2]) cr = Math.max(cr, 1 - cd / k[2]);
                }
                l = Math.max(0f, Math.min(1f, l - cr * 0.34f));
                int idx = Math.min(MOON_PALETTE.length - 1, Math.max(0, Math.round((1 - l) * (MOON_PALETTE.length - 1))));
                moonPixels[y * MOON_N + x] = (byte) idx;
            }
        }
    }

    /** Parallax depths for the three star layers (px of travel across the screen). */
    private static final float[] LAYER_DEPTH = {8f, 16f, 26f};

    private int starLayer(int i) {
        return starR[i] < 1.1f ? 0 : starR[i] < 1.8f ? 1 : 2;
    }

    private void drawStars(GuiGraphicsExtractor gfx, int w, int h, float px, float py) {
        Matrix3x2fStack pose = gfx.pose();
        // one float translate per depth layer → subpixel-smooth parallax
        for (int layer = 0; layer < 3; layer++) {
            pose.pushMatrix();
            pose.translate(-px * LAYER_DEPTH[layer], -py * LAYER_DEPTH[layer] * 0.6f);
            for (int i = 0; i < starX.length; i++) {
                if (starLayer(i) != layer) continue;
                int sx = (int) (starX[i] * w);
                int sy = (int) (starY[i] * h);
                float a = 0.42f + (float) Math.sin(t * starTw[i] + starPh[i]) * 0.35f;
                a = Math.max(0.06f, Math.min(1f, a));
                int argb = ((int) (a * 255) << 24) | ((starWarm[i] ? STAR_WARM : STAR_COOL) & 0xFFFFFF);
                int r = starR[i] > 1.7f ? 2 : 1;
                gfx.fill(sx, sy, sx + r, sy + r, argb);
            }
            pose.popMatrix();
        }
    }

    private void drawConstellations(GuiGraphicsExtractor gfx, int w, int h, float px, float py) {
        Matrix3x2fStack pose = gfx.pose();
        pose.pushMatrix();
        pose.translate(-px * 10f, -py * 8f);
        for (float[][] pts : CONSTELLATIONS) {
            // faint dotted connecting lines
            for (int i = 0; i < pts.length - 1; i++) {
                float x0 = pts[i][0] * w, y0 = pts[i][1] * h;
                float x1 = pts[i + 1][0] * w, y1 = pts[i + 1][1] * h;
                int segs = 9;
                for (int s = 1; s < segs; s += 2) {
                    int lx = (int) (x0 + (x1 - x0) * s / segs);
                    int ly = (int) (y0 + (y1 - y0) * s / segs);
                    gfx.fill(lx, ly, lx + 1, ly + 1, 0x33B4C8FF);
                }
            }
            // anchor stars
            for (float[] p : pts) {
                int sx = (int) (p[0] * w), sy = (int) (p[1] * h);
                gfx.fill(sx - 1, sy, sx + 2, sy + 1, 0xCCDCE6FF);
                gfx.fill(sx, sy - 1, sx + 1, sy + 2, 0xCCDCE6FF);
            }
        }
        pose.popMatrix();
    }

    private void drawComet(GuiGraphicsExtractor gfx, int w, int h) {
        float x0 = 0.9f, y0 = -0.1f, x1 = -0.05f, y1 = 0.55f;
        float x = (x0 + (x1 - x0) * cometT) * w;
        float y = (y0 + (y1 - y0) * cometT) * h;
        float dx = (x1 - x0) * w, dy = (y1 - y0) * h;
        float len = (float) Math.hypot(dx, dy);
        float ux = dx / len, uy = dy / len;
        float tail = (float) Math.sin(cometT * Math.PI) * 150f;

        // float translate to the head → the whole comet glides subpixel-smooth
        Matrix3x2fStack pose = gfx.pose();
        pose.pushMatrix();
        pose.translate(x, y);
        for (int i = 1; i <= 18; i++) {
            float f = i / 18f;
            int tx = Math.round(-ux * tail * f);
            int ty = Math.round(-uy * tail * f);
            int a = (int) (190 * (1 - f) * (1 - f));
            int sz = f < 0.4f ? 2 : 1;
            gfx.fill(tx, ty, tx + sz, ty + sz, (a << 24) | 0xFFECC8);
        }
        gfx.fill(-2, -2, 3, 3, 0xFFFFF6E2);
        gfx.fill(-3, -1, 4, 2, 0x66FFE0B0);
        gfx.fill(-1, -3, 2, 4, 0x66FFE0B0);
        pose.popMatrix();
    }

    private void drawMeteors(GuiGraphicsExtractor gfx, int w, int h) {
        Matrix3x2fStack pose = gfx.pose();
        for (Meteor m : meteors) {
            float fade = (float) Math.sin(Math.min(1f, m.life / m.max) * Math.PI);
            pose.pushMatrix();
            pose.translate(m.x * w, m.y * h);
            for (int i = 0; i < 8; i++) {
                float f = i / 8f;
                int mx = Math.round(-m.vx * 0.03f * f * w);
                int my = Math.round(-m.vy * 0.03f * f * h);
                int a = (int) (200 * fade * (1 - f));
                gfx.fill(mx, my, mx + 1, my + 1, (a << 24) | 0xFFFFF0);
            }
            pose.popMatrix();
        }
    }

    private void drawMoon(GuiGraphicsExtractor gfx, int w, int h, float px, float py) {
        int size = Math.max(2, Math.round(w * 0.052f / MOON_N));
        Matrix3x2fStack pose = gfx.pose();
        pose.pushMatrix();
        pose.translate(w * 0.80f - px * 16f, h * 0.10f - py * 10f);
        for (int y = 0; y < MOON_N; y++) {
            for (int x = 0; x < MOON_N; x++) {
                byte idx = moonPixels[y * MOON_N + x];
                if (idx < 0) continue;
                int cx = x * size, cy = y * size;
                gfx.fill(cx, cy, cx + size, cy + size, MOON_PALETTE[idx]);
            }
        }
        pose.popMatrix();
    }

    private void drawHorizon(GuiGraphicsExtractor gfx, int w, int h) {
        int base = (int) (h * 0.82f);
        // back ridge: taller plateaus
        int stepB = Math.max(50, w / 9);
        for (int x = 0, i = 0; x < w; x += stepB, i++) {
            int rise = switch (i % 4) { case 0 -> (int) (h * 0.045f); case 2 -> (int) (h * 0.028f); default -> 0; };
            gfx.fill(x, base - rise, x + stepB, h, HORIZON_BACK);
        }
        // front ridge: lower, darker
        int stepF = Math.max(36, w / 14);
        int baseF = (int) (h * 0.88f);
        for (int x = 0, i = 0; x < w; x += stepF, i++) {
            int rise = switch (i % 3) { case 1 -> (int) (h * 0.02f); default -> 0; };
            gfx.fill(x, baseF - rise, x + stepF, h, HORIZON_FRONT);
        }

        // the croft: farmhouse silhouette with hearth glow + flickering window
        int hw = Math.max(40, (int) (w * 0.045f));
        int hh = Math.max(34, (int) (h * 0.065f));
        // the croft lives on the open right side of the horizon, clear of the UI,
        // perched on the back ridge so its roofline breaks into the sky
        int hx = (int) (w * 0.70f);
        int hy = base - hh + (int) (h * 0.012f);

        float flick = 0.82f + 0.18f * (float) Math.sin(t * 3.1f) * (float) Math.cos(t * 1.7f);
        // chimney, with a wisp of drifting smoke
        int chX = hx + hw - hw / 4 - hw / 8;
        gfx.fill(chX, hy - hh / 5, chX + hw / 8, hy + hh / 4, 0xFF20345C);
        for (int i = 0; i < 3; i++) {
            float ph = (t * 0.35f + i * 0.33f) % 1f;
            int sx = chX + hw / 16 + (int) (Math.sin((t + i * 2.1f) * 1.3f) * 3);
            int sy = (int) (hy - hh / 5 - 4 - ph * hh * 0.8f);
            int a = (int) (70 * (1 - ph));
            gfx.fill(sx, sy, sx + 2, sy + 2, (a << 24) | 0xB9C2DA);
        }
        // roof (stepped pyramid for a blocky read) — lighter than the ridge behind
        int roofH = (int) (hh * 0.36f);
        for (int i = 0; i < 3; i++) {
            int inset = (2 - i) * (hw / 8);
            gfx.fill(hx + inset - 2, hy + i * roofH / 3, hx + hw - inset + 2, hy + roofH, 0xFF20345C);
        }
        // moonlit roof rim
        gfx.fill(hx + 2 * (hw / 8) - 2, hy, hx + hw - 2 * (hw / 8) + 2, hy + 1, 0x662E4670);
        // wall
        gfx.fill(hx, hy + roofH - 1, hx + hw, hy + hh, 0xFF15223E);
        // window, warm and flickering, with a tight halo (no big box)
        int wa = (int) (Math.max(0.55f, flick) * 255) << 24;
        int wx = hx + (int) (hw * 0.30f), wy = hy + (int) (hh * 0.48f);
        int ww = Math.max(5, (int) (hw * 0.34f)), wh2 = Math.max(5, (int) (hh * 0.30f));
        int haloA = (int) (0x30 * flick);
        gfx.fill(wx - 9, wy - 9, wx + ww + 9, wy + wh2 + 9, ((haloA / 3) << 24) | 0xFFA84A);
        gfx.fill(wx - 5, wy - 5, wx + ww + 5, wy + wh2 + 5, ((haloA * 2 / 3) << 24) | 0xFFA84A);
        gfx.fill(wx - 2, wy - 2, wx + ww + 2, wy + wh2 + 2, (haloA << 24) | 0xFFA84A);
        gfx.fill(wx, wy, wx + ww, wy + wh2, wa | (WINDOW & 0xFFFFFF));
        // cross mullion
        gfx.fill(wx + ww / 2, wy, wx + ww / 2 + 1, wy + wh2, 0x99101B32);
        gfx.fill(wx, wy + wh2 / 2, wx + ww, wy + wh2 / 2 + 1, 0x99101B32);
    }
}
