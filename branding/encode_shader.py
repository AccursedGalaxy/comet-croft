#!/usr/bin/env python3
"""Encode branding/menu_sky.glsl into the FancyMenu GLSL menu_background
(inline_shader_source, %n% newline encoding) of ssui.titlescreen.txt.
Run from the repo root after editing the shader; then packwiz refresh."""

import re
import sys

LAYOUT = "config/fancymenu/customization/ssui.titlescreen.txt"
SHADER = "branding/menu_sky.glsl"
BLOCK_ID = "cdfe39f6-f89c-442f-98fe-cd0bd27dacac-1777908548724"

glsl = open(SHADER).read()
assert "%" not in glsl.replace("%n%", ""), (
    "GLSL must not contain '%' (conflicts with %n% encoding)"
)
encoded = "%n%".join(glsl.splitlines())

s = open(LAYOUT).read()
start = s.index(BLOCK_ID)
end = s.index("}", start)
block = s[start:end]
block = re.sub(r"show_background = \w+", "show_background = true", block, count=1)
block = re.sub(
    r"inline_shader_source = [^\n]*",
    "inline_shader_source = " + encoded.replace("\\", "\\\\"),
    block,
    count=1,
)
s = s[:start] + block + s[end:]
open(LAYOUT, "w").write(s)
print("encoded", len(glsl), "bytes of GLSL into", LAYOUT)
