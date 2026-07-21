#!/usr/bin/env python
"""Menu layout sweep: one client launch, screenshots of the title screen and
the How to Play panel at several window geometries (instance guiScale as-is).
Run: testing/.venv/bin/python menusweep.py  (from anywhere)"""

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

SIZES = {
    "2000x837": (2000, 837),  # the reported-broken geometry (gui ~500x209 @4)
    "1280x720": (1280, 720),  # small window
    "3440x1400": (3440, 1400),  # near-fullscreen control
}

run_dir = e2e.new_run_dir("menusweep")
results = {"ok": False, "screens": []}
serve, sess, win, rec = e2e.launch_client(run_dir, world=None, rec_name="menusweep")


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
        for label, (w, h) in SIZES.items():
            hypr.dispatch("resizewindowpixel", f"exact {w} {h},{addr}")
            time.sleep(2)
            hypr.focus_window(win)
            shot(f"main_{label}")
            for _ in range(4):
                vi.tap("tab")
            vi.tap("enter")
            time.sleep(1)
            shot(f"help_{label}")
            vi.tap("esc")
            time.sleep(1)
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
