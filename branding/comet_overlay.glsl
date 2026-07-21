// Comet Croft - animated comet, rendered as a FancyMenu GLSL decoration overlay
// ON TOP of the baked photographic sky (config/fancymenu/assets/menu_sky.png).
// Everything except the comet is fully transparent (alpha 0) so the still shows
// through; only the comet moves. Kept cheap. Single entry point per FancyMenu's
// (?m)^\s*void\s+mainImage\s*\( rule; minified onto one line by wire_sky.py.

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;
    float aspect = iResolution.x / iResolution.y;
    vec2 sky = vec2((uv.x - 0.5) * aspect, uv.y);
    vec3 col = vec3(0.0);
    float alpha = 0.0;

    // A comet crosses the upper sky every `period` seconds, clearing the wordmark
    // (very top) and the moon (upper-left) and passing above the menu panel.
    float period = 17.0;
    float duration = 5.0;
    float localTime = mod(iTime, period);
    float cycle = floor(iTime / period);
    if (localTime < duration) {
        float t = localTime / duration;
        float eased = t * t * (3.0 - 2.0 * t);
        float seed = hash21(vec2(cycle, 6.4));
        vec2 start = vec2(-0.58 * aspect, 0.82 - seed * 0.05);
        vec2 finish = vec2(0.60 * aspect, 0.63 + seed * 0.10);
        vec2 bend = vec2(0.0, sin(t * 3.14159) * 0.04);
        vec2 pos = mix(start, finish, eased) + bend;
        vec2 velocity = normalize(finish - start + vec2(0.0, cos(t * 3.14159) * 0.08));
        vec2 normal = vec2(-velocity.y, velocity.x);
        vec2 rel = sky - pos;
        float back = -dot(rel, velocity);
        float across = dot(rel, normal);
        float visible = smoothstep(0.0, 0.14, t) * (1.0 - smoothstep(0.80, 1.0, t));
        float taper = smoothstep(0.44, 0.0, back) * step(0.0, back);
        float tailCore = exp(-across * across * 9000.0) * taper;
        float tailGlow = exp(-abs(across) * 74.0) * smoothstep(0.50, 0.0, back) * step(0.0, back);
        float split = exp(-pow(across - back * 0.024, 2.0) * 12000.0) * smoothstep(0.38, 0.04, back) * step(0.03, back);
        float head = exp(-dot(rel, rel) * 11000.0);
        float halo = exp(-length(rel) * 110.0);
        col += vec3(0.30, 0.56, 1.00) * tailGlow * 0.32;
        col += vec3(0.66, 0.83, 1.00) * (tailCore + split * 0.40) * 0.90;
        col += vec3(0.62, 0.78, 1.00) * halo * 0.52;
        col += vec3(1.00, 0.93, 0.72) * head * 2.30;
        col *= visible;
        alpha = clamp(max(max(col.r, col.g), col.b), 0.0, 1.0);
    }
    fragColor = vec4(col, alpha);
}
