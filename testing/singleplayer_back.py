#!/usr/bin/env python
"""Repro/verify: title -> Singleplayer -> back must return to the CUSTOM menu.

Bug: any setScreen(null) with no world loaded made vanilla build a fresh
TitleScreen inside setScreen, past the takeover mixin's head injection —
so backing out of the Singleplayer flow could resurrect the vanilla menu.

Drives: Enter (hero Singleplayer holds initial focus) -> ESC -> screenshot.
Run: testing/.venv/bin/python singleplayer_back.py  (from anywhere)"""

import sys
import time
from pathlib import Path

TESTING = Path("/home/aki/dev/comet-croft/testing")
sys.path.insert(0, str(TESTING))
import os

os.chdir(TESTING)

from lib import hypr, capture  # noqa: E402
from lib.vinput import VirtualInput  # noqa: E402
import e2e  # noqa: E402

run_dir = e2e.new_run_dir("spback")
results = {"ok": False, "screens": []}
serve, sess, win, rec = e2e.launch_client(run_dir, world=None, rec_name="spback")


def shot(name):
    w = hypr.get_window(win["address"])
    p = capture.shot_window(run_dir / f"{name}.png", w)
    results["screens"].append(p.name)
    e2e.note(run_dir, f"screenshot {p.name}")


try:
    sess.wait_for_log(r"Backend library: LWJGL|Sound engine started", timeout=240)
    e2e.note(run_dir, "render backend up; settling")
    time.sleep(25)
    addr = f"address:{win['address']}"
    hypr.dispatch("setfloating", addr)
    hypr.dispatch("movewindowpixel", f"exact 0 20,{addr}")
    vi = VirtualInput()
    try:
        hypr.focus_window(win)
        shot("1_title_custom")
        vi.tap("enter")  # hero Singleplayer has initial focus
        time.sleep(2)
        shot("2_world_list")
        vi.tap("esc")  # SelectWorldScreen.onClose
        time.sleep(2)
        shot("3_back_on_title")
        results["ok"] = True
    finally:
        e2e.note(run_dir, "closing game window")
        hypr.dispatch("closewindow", addr)
        sess.wait_exit(timeout=60)
        vi.close()
except Exception as ex:
    results["error"] = str(ex)
    capture.screenshot(run_dir / "error_fullscreen.png")
finally:
    sess.kill()
    e2e.finish_client(run_dir, serve, sess, rec, results)
print(f"run dir: {run_dir}")
print("PASS" if results.get("ok") else f"FAIL: {results.get('error')}")
sys.exit(0 if results.get("ok") else 1)
