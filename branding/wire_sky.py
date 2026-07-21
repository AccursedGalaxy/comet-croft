#!/usr/bin/env python3
"""Wire the baked photographic sky + animated comet overlay into the FancyMenu
title and loading layouts.

  Title   : image background (menu_sky.png) + comet GLSL decoration overlay.
  Loading : image background (menu_sky.png) only (transient screen).

Run after re-baking the sky or editing branding/comet_overlay.glsl, then
`packwiz refresh`. Idempotent-ish: safe to re-run.
"""

import re

CUST = "config/fancymenu/customization"
TITLE = f"{CUST}/ssui.titlescreen.txt"
LOAD = f"{CUST}/ssui.loadingscreen.txt"
IMG = "[source:local]/config/fancymenu/assets/menu_sky.png"
PROTOTYPE = "void mainImage(out vec4 fragColor, in vec2 fragCoord);"

GLSL_BG_ID = "cdfe39f6-f89c-442f-98fe-cd0bd27dacac-1777908548724"
IMG_BG_ID = "16e6836b-b632-4e8b-9a77-4270fb85c47e-1777908548723"
OVERLAY_ID = "7a79a822-c0bc-4d0f-a0d1-349b87a8b381-1777908548724"
LOAD_BG_ID = "a3d5f8c1-0e2b-4a77-b6cd-cc0met0load001"


def minify(path):
    glsl = open(path).read()
    assert "/*" not in glsl and "#" not in glsl, "unsupported syntax for one-line form"
    lines = [re.sub(r"//.*", "", ln).strip() for ln in glsl.splitlines()]
    one = re.sub(r"\s+", " ", " ".join(l for l in lines if l)).strip()
    assert PROTOTYPE.rstrip(";") in one, "definition must match prototype"
    encoded = f"{PROTOTYPE} {one}"
    assert re.search(r"(?m)^\s*void\s+mainImage\s*\(", encoded)
    assert "\n" not in encoded
    return encoded


def block_span(s, instance_id, header):
    """Return (start, end) of the `header { ... }` block holding instance_id."""
    idx = s.index(instance_id)
    start = s.rindex(f"{header} {{", 0, idx)
    end = s.index("\n}", idx) + 2
    return start, end


def set_field(block, key, value, insert_after=None):
    """Set key=value in a block; if absent, insert after `insert_after` line."""
    pat = re.compile(rf"(^\s*{re.escape(key)} = )[^\n]*", re.M)
    if pat.search(block):
        return pat.sub(lambda m: m.group(1) + value, block, count=1)
    anchor = re.compile(rf"(^\s*{re.escape(insert_after)} = [^\n]*)", re.M)
    return anchor.sub(lambda m: m.group(1) + f"\n  {key} = {value}", block, count=1)


comet = minify("branding/comet_overlay.glsl")

# ---- title ---------------------------------------------------------------
s = open(TITLE).read()

# 1) disable the procedural glsl background
a, b = block_span(s, GLSL_BG_ID, "menu_background")
blk = set_field(s[a:b], "show_background", "false")
s = s[:a] + blk + s[b:]

# 2) enable the image background pointing at the baked sky
a, b = block_span(s, IMG_BG_ID, "menu_background")
blk = set_field(s[a:b], "show_background", "true")
blk = set_field(blk, "image_path", IMG, insert_after="background_type")
s = s[:a] + blk + s[b:]

# 3) enable the comet decoration overlay with the minified shader
a, b = block_span(s, OVERLAY_ID, "decoration_overlay")
blk = set_field(s[a:b], "show_decoration_overlay", "true")
blk = set_field(blk, "inline_shader_source", comet)
s = s[:a] + blk + s[b:]

open(TITLE, "w").write(s)
print("title: image bg + comet overlay wired")

# ---- loading -------------------------------------------------------------
s = open(LOAD).read()
a, b = block_span(s, LOAD_BG_ID, "menu_background")
image_block = (
    "menu_background {\n"
    f"  instance_identifier = {LOAD_BG_ID}\n"
    "  background_type = image\n"
    "  show_background = true\n"
    f"  image_path = {IMG}\n"
    "  slide = false\n"
    "  repeat_texture = false\n"
    "  parallax = false\n"
    "  parallax_intensity_x = 0.02\n"
    "  parallax_intensity_y = 0.02\n"
    "  invert_parallax = false\n"
    "  restart_animated_on_menu_load = false\n"
    "}"
)
s = s[:a] + image_block + s[b:]
open(LOAD, "w").write(s)
print("loading: image bg wired")
print(f"comet shader: {len(comet)} chars")
