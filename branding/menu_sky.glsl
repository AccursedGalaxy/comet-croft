// Comet Croft title-screen background (Shadertoy-style, FancyMenu GLSL background).
// A calm, layered night sky with drifting aurora, crisp stars, distant hills,
// and a cinematic comet pass. Kept texture-free and inexpensive for laptops.
// Source of truth for the inline_shader_source in ssui.titlescreen.txt;
// run branding/encode_shader.py after editing.

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float vnoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash21(i);
    float b = hash21(i + vec2(1.0, 0.0));
    float c = hash21(i + vec2(0.0, 1.0));
    float d = hash21(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float fbm(vec2 p) {
    float n = vnoise(p) * 0.58;
    n += vnoise(p * 2.03 + 7.1) * 0.28;
    n += vnoise(p * 4.01 + 13.7) * 0.14;
    return n;
}

vec3 starLayer(vec2 p, float scale, float threshold, float radius, float speed) {
    vec2 g = p * scale;
    vec2 id = floor(g);
    vec2 q = fract(g) - 0.5;
    float h = hash21(id);
    vec2 offset = (vec2(hash21(id + 17.2), hash21(id + 31.7)) - 0.5) * 0.62;
    q -= offset;
    float present = step(threshold, h);
    float twinkle = 0.72 + 0.28 * sin(iTime * speed * (0.65 + h) + h * 41.0);
    float core = smoothstep(radius, radius * 0.18, length(q));
    float rays = exp(-abs(q.x) * 38.0) * exp(-abs(q.y) * 5.0)
               + exp(-abs(q.y) * 38.0) * exp(-abs(q.x) * 5.0);
    float bright = smoothstep(0.975, 1.0, h);
    float value = present * twinkle * (core + rays * bright * 0.18);
    vec3 tint = mix(vec3(0.62, 0.76, 1.0), vec3(1.0, 0.88, 0.68), hash21(id + 5.4));
    return tint * value;
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;
    float aspect = iResolution.x / iResolution.y;
    vec2 sky = vec2((uv.x - 0.5) * aspect, uv.y);

    // Rich vertical gradient with a restrained horizon glow.
    vec3 horizon = vec3(0.105, 0.145, 0.270);
    vec3 middle = vec3(0.040, 0.065, 0.155);
    vec3 zenith = vec3(0.012, 0.018, 0.060);
    vec3 col = mix(horizon, middle, smoothstep(0.02, 0.48, uv.y));
    col = mix(col, zenith, smoothstep(0.48, 1.0, uv.y));
    col += vec3(0.09, 0.045, 0.12) * pow(1.0 - uv.y, 3.0) * 0.24;

    // A broad diagonal Milky Way: structured enough to read, quiet enough for UI.
    float galaxyAxis = uv.y - (0.68 + 0.10 * sin(sky.x * 0.85 + 0.4));
    float galaxy = exp(-galaxyAxis * galaxyAxis * 34.0);
    float dust = fbm(sky * vec2(2.3, 7.0) + vec2(0.0, iTime * 0.006));
    float darkRift = fbm(sky * vec2(3.2, 10.0) + 19.0);
    col += mix(vec3(0.09, 0.13, 0.24), vec3(0.18, 0.11, 0.25), dust)
         * galaxy * smoothstep(0.25, 0.85, dust) * 0.30;
    col -= vec3(0.025, 0.030, 0.055) * galaxy * smoothstep(0.58, 0.82, darkRift);

    // Two translucent aurora ribbons drift at different rates.
    float ax = sky.x;
    float ribbon1 = 0.78 + 0.035 * sin(ax * 2.8 + iTime * 0.055)
                         + 0.018 * sin(ax * 7.0 - iTime * 0.035);
    float ribbon2 = 0.84 + 0.025 * sin(ax * 3.6 - iTime * 0.042 + 2.0);
    float aurora1 = exp(-abs(uv.y - ribbon1) * 24.0);
    float aurora2 = exp(-abs(uv.y - ribbon2) * 32.0);
    float curtain = 0.35 + 0.65 * fbm(vec2(ax * 3.0 + iTime * 0.025, iTime * 0.018));
    col += vec3(0.055, 0.32, 0.25) * aurora1 * curtain * 0.20;
    col += vec3(0.12, 0.16, 0.42) * aurora2 * (1.0 - curtain * 0.35) * 0.17;

    // Three parallax-like star scales, with rare cross-shaped bright stars.
    float horizonFade = smoothstep(0.12, 0.35, uv.y);
    vec3 stars = starLayer(sky, 28.0, 0.91, 0.105, 1.15) * 0.72;
    stars += starLayer(sky + vec2(8.7, 3.1), 57.0, 0.945, 0.115, 1.75) * 0.60;
    stars += starLayer(sky + vec2(21.3, 9.8), 105.0, 0.968, 0.13, 2.25) * 0.40;
    col += stars * horizonFade;

    // Soft moon/planet glow, placed away from the centered title.
    vec2 moonPos = vec2(-0.39 * aspect, 0.73);
    float moonDist = length(sky - moonPos);
    float moonGlow = exp(-moonDist * 22.0);
    float moonDisc = smoothstep(0.020, 0.015, moonDist);
    col += vec3(0.34, 0.43, 0.68) * moonGlow * 0.12;
    col += vec3(0.82, 0.88, 1.0) * moonDisc * 0.52;

    // Cinematic comet: eased travel, tapered split tail, halo and warm nucleus.
    // It appears after a short calm opening, then returns every 22 seconds.
    float period = 22.0;
    float duration = 5.2;
    float localTime = mod(iTime + period - 2.0, period);
    float cycle = floor((iTime + period - 2.0) / period);
    if (localTime < duration) {
        float t = localTime / duration;
        float eased = t * t * (3.0 - 2.0 * t);
        float seed = hash21(vec2(cycle, 6.4));
        vec2 start = vec2(-0.62 * aspect, 0.86 - seed * 0.06);
        vec2 finish = vec2(0.62 * aspect, 0.55 + seed * 0.12);
        vec2 bend = vec2(0.0, sin(t * 3.14159) * 0.035);
        vec2 pos = mix(start, finish, eased) + bend;
        vec2 velocity = normalize(finish - start + vec2(0.0, cos(t * 3.14159) * 0.08));
        vec2 normal = vec2(-velocity.y, velocity.x);
        vec2 rel = sky - pos;
        float back = -dot(rel, velocity);
        float across = dot(rel, normal);
        float visible = smoothstep(0.0, 0.13, t) * (1.0 - smoothstep(0.82, 1.0, t));
        float taper = smoothstep(0.42, 0.0, back) * step(0.0, back);
        float tailCore = exp(-across * across * 9000.0) * taper;
        float tailGlow = exp(-abs(across) * 78.0) * smoothstep(0.48, 0.0, back) * step(0.0, back);
        float split = exp(-pow(across - back * 0.024, 2.0) * 12500.0)
                    * smoothstep(0.36, 0.04, back) * step(0.03, back);
        float head = exp(-dot(rel, rel) * 12500.0);
        float halo = exp(-length(rel) * 115.0);
        col += vec3(0.30, 0.56, 1.00) * tailGlow * 0.30 * visible;
        col += vec3(0.64, 0.82, 1.00) * (tailCore + split * 0.38) * 0.78 * visible;
        col += vec3(0.62, 0.78, 1.00) * halo * 0.48 * visible;
        col += vec3(1.00, 0.93, 0.72) * head * 2.1 * visible;
    }

    // Layered croft hills anchor the scene without competing with menu controls.
    float farHill = 0.125 + 0.020 * sin(sky.x * 2.1 + 0.6)
                          + 0.012 * sin(sky.x * 5.4 - 1.2);
    float nearHill = 0.070 + 0.027 * sin(sky.x * 2.8 - 0.5)
                           + 0.014 * sin(sky.x * 7.5 + 1.1);
    col = mix(col, vec3(0.026, 0.043, 0.090), smoothstep(farHill + 0.006, farHill - 0.006, uv.y) * 0.82);
    col = mix(col, vec3(0.010, 0.020, 0.047), smoothstep(nearHill + 0.005, nearHill - 0.005, uv.y) * 0.94);

    // Subtle edge vignette and filmic highlight rolloff.
    vec2 vignetteUv = uv * (1.0 - uv.yx);
    float vignette = pow(clamp(vignetteUv.x * vignetteUv.y * 18.0, 0.0, 1.0), 0.13);
    col *= mix(0.72, 1.0, vignette);
    col = col / (1.0 + col * 0.32);
    fragColor = vec4(col, 1.0);
}
