#!/usr/bin/env python3
"""Encode branding/menu_sky.glsl into the FancyMenu GLSL menu_background
of ssui.titlescreen.txt.

FancyMenu 3.9.8 reality check (decompiled PropertiesParser + GlslShaderRuntime):
  - PropertiesParser.deserializeSetFromFancyString() stores property values RAW.
    stringifyFancyString()/unstringify() ($prop_line_break$ & friends) exist but
    are never called - layout values cannot contain newlines, encoded or not.
  - GlslShaderRuntime requires the entry point to match (?m)^\\s*void\\s+mainImage\\s*\\(
    i.e. `void mainImage(` at the START of a line.
So the shader must be minified onto ONE line that BEGINS with a `void mainImage`
prototype; helper functions and the real definition follow on the same line.
Raw {} braces mid-line are fine (the parser only checks line starts/ends).

Run from repo root after editing the shader; then `packwiz refresh`.
"""

import re

LAYOUT = "config/fancymenu/customization/ssui.titlescreen.txt"
SHADER = "branding/menu_sky.glsl"
BLOCK_ID = "cdfe39f6-f89c-442f-98fe-cd0bd27dacac-1777908548724"
PROTOTYPE = "void mainImage(out vec4 fragColor, in vec2 fragCoord);"

glsl = open(SHADER).read()
assert "/*" not in glsl, "block comments unsupported by this minifier"
assert "#" not in glsl, "preprocessor directives cannot survive single-line form"

# strip // comments, join everything onto one line
lines = [re.sub(r"//.*", "", ln).strip() for ln in glsl.splitlines()]
one_line = " ".join(ln for ln in lines if ln)
one_line = re.sub(r"\s+", " ", one_line).strip()

sig = PROTOTYPE.rstrip(";")
assert sig in one_line, f"definition must match prototype: {sig}"
encoded = f"{PROTOTYPE} {one_line}"

s = open(LAYOUT).read()
start = s.index(BLOCK_ID)
end = s.index("\n}", start)
block = s[start:end]
block = re.sub(r"show_background = \w+", "show_background = true", block, count=1)
block = re.sub(
    r"inline_shader_source = [^\n]*",
    lambda m: "inline_shader_source = " + encoded,
    block,
    count=1,
)
s = s[:start] + block + s[end:]
open(LAYOUT, "w").write(s)

# self-check: emulate FancyMenu's parse (value = text after first '=' on the
# line) + entry-point regex
assert re.search(r"(?m)^\s*void\s+mainImage\s*\(", encoded), "entry-point regex fails"
assert "\n" not in encoded
print(
    f"encoded {len(glsl)} chars of GLSL into {LAYOUT} as one line "
    f"({len(encoded)} chars)"
)
