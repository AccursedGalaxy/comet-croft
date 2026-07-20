// Comet Croft title-screen background (Shadertoy-style, FancyMenu GLSL background).
// Night sky in the pack palette: deep blues, twinkling stars, faint milky band,
// a whisper of aurora, and a comet pass every ~27 seconds.
// Source of truth for the inline_shader_source in ssui.titlescreen.txt —
// re-encode with branding/encode_shader.py after editing.

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

float starLayer(vec2 suv, float density, float thresh, float size, float twSpeed) {
    vec2 g = suv * density;
    vec2 id = floor(g);
    vec2 f = fract(g) - 0.5;
    float h = hash21(id);
    float star = 0.0;
    if (h > thresh) {
        vec2 off = (vec2(hash21(id + 7.3), hash21(id + 2.9)) - 0.5) * 0.7;
        float d = length(f - off);
        float tw = 0.65 + 0.35 * sin(iTime * twSpeed * (0.5 + h) + h * 50.0);
        star = smoothstep(size, 0.0, d) * tw * (h - thresh) / (1.0 - thresh);
    }
    return star;
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;
    float asp = iResolution.x / iResolution.y;
    vec2 suv = vec2(uv.x * asp, uv.y);

    // sky gradient: warm-less deep blues, slightly lifted at the horizon
    vec3 top = vec3(0.027, 0.035, 0.100);
    vec3 mid = vec3(0.055, 0.078, 0.190);
    vec3 hor = vec3(0.100, 0.140, 0.280);
    vec3 col = mix(hor, mid, smoothstep(0.0, 0.45, uv.y));
    col = mix(col, top, smoothstep(0.45, 1.0, uv.y));

    // faint milky band across the upper sky
    float band = exp(-abs((uv.y - 0.62) - 0.18 * sin(uv.x * 2.2 + 0.7)) * 5.0);
    float n = vnoise(suv * 6.0 + vec2(3.1, 7.7)) * 0.5 + vnoise(suv * 13.0) * 0.5;
    col += vec3(0.10, 0.12, 0.20) * band * n * 0.35;

    // aurora curtain, very subtle, slow drift
    float ay = 0.78 + 0.04 * sin(suv.x * 2.5 + iTime * 0.05)
                    + 0.02 * sin(suv.x * 6.0 - iTime * 0.11);
    float curtain = exp(-abs(uv.y - ay) * 10.0);
    float wave = 0.5 + 0.5 * vnoise(vec2(suv.x * 3.0 + iTime * 0.07, iTime * 0.03));
    vec3 acol = mix(vec3(0.05, 0.35, 0.28), vec3(0.15, 0.20, 0.45),
                    vnoise(vec2(suv.x * 1.5, iTime * 0.02)));
    col += acol * curtain * wave * 0.22;

    // stars, two depths, fading out toward the horizon
    float s = starLayer(suv, 42.0, 0.93, 0.10, 1.6) * 0.9;
    s += starLayer(suv + vec2(11.7, 4.3), 90.0, 0.95, 0.14, 2.4) * 0.5;
    col += vec3(0.85, 0.90, 1.00) * s * smoothstep(0.05, 0.30, uv.y);

    // the comet: one pass every 27s, ~3.5s on screen, varied path per cycle
    float period = 27.0;
    float dur = 3.5;
    float cyc = floor(iTime / period);
    float lt = iTime - cyc * period;
    if (lt < dur) {
        float pr = lt / dur;
        float h1 = hash21(vec2(cyc, 3.7));
        float h2 = hash21(vec2(cyc, 9.2));
        vec2 a = vec2(-0.15 * asp + h1 * 0.25, 0.92 - h2 * 0.10);
        vec2 b = vec2(1.10 * asp, 0.55 + h1 * 0.25);
        vec2 dir = normalize(b - a);
        vec2 pos = mix(a, b, pr);
        vec2 rel = suv - pos;
        float behind = -dot(rel, dir);
        float dperp = abs(dot(rel, vec2(-dir.y, dir.x)));
        float env = sin(pr * 3.14159);
        float tail = exp(-dperp * dperp * 6000.0)
                   * smoothstep(0.30, 0.0, behind) * step(0.0, behind);
        float head = exp(-dot(rel, rel) * 9000.0) * 2.0;
        col += (vec3(0.55, 0.75, 1.00) * tail * 0.55
              + vec3(1.00, 0.98, 0.90) * head) * env;
    }

    // gentle vignette so UI reads on top
    float vig = 1.0 - 0.35 * length(uv - 0.5);
    fragColor = vec4(col * vig, 1.0);
}
