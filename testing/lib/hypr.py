"""Hyprland control: window discovery, focus, cursor, monitors.

Talks to the live compositor via hyprctl. The instance signature is
auto-detected by probing the socket dirs under $XDG_RUNTIME_DIR/hypr.
"""

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

_RUNTIME = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
_SIG = None


def _signature() -> str:
    global _SIG
    if _SIG:
        return _SIG
    hyprdir = _RUNTIME / "hypr"
    candidates = sorted(
        hyprdir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True
    )
    for c in candidates:
        env = dict(os.environ, HYPRLAND_INSTANCE_SIGNATURE=c.name)
        r = subprocess.run(
            ["hyprctl", "-j", "version"], env=env, capture_output=True, timeout=5
        )
        if r.returncode == 0:
            _SIG = c.name
            return _SIG
    raise RuntimeError("no live Hyprland instance found")


def hyprctl(*args: str, as_json: bool = False) -> "Any":
    env = dict(os.environ, HYPRLAND_INSTANCE_SIGNATURE=_signature())
    cmd = ["hyprctl"] + (["-j"] if as_json else []) + list(args)
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=10)
    if r.returncode != 0:
        raise RuntimeError(f"hyprctl {args} failed: {r.stderr.strip()}")
    return json.loads(r.stdout) if as_json else r.stdout.strip()


def dispatch(*args: str) -> str:
    return hyprctl("dispatch", *args)


def monitors():
    return hyprctl("monitors", as_json=True)


def focused_monitor():
    return next(m for m in monitors() if m["focused"])


def clients():
    return hyprctl("clients", as_json=True)


def find_window(needle: str, timeout: float = 0, interval: float = 1.0):
    """Find a window whose class or title contains `needle` (case-insensitive).

    With timeout > 0, poll until it appears. Returns the client dict or None.
    """
    deadline = time.time() + timeout
    while True:
        for c in clients():
            hay = (c.get("class", "") + " " + c.get("title", "")).lower()
            if needle.lower() in hay:
                return c
        if time.time() >= deadline:
            return None
        time.sleep(interval)


def focus_window(client: dict):
    dispatch("focuswindow", f"address:{client['address']}")
    time.sleep(0.2)


def fullscreen_window(client: dict, on: bool = True):
    cur = get_window(client["address"])
    if cur and bool(cur.get("fullscreen")) != on:
        focus_window(client)
        dispatch("fullscreen", "0")
        time.sleep(0.4)


def get_window(address: str):
    for c in clients():
        if c["address"] == address:
            return c
    return None


def window_geometry(client: dict):
    """Fresh (x, y, w, h) of a window in global layout coordinates."""
    c = get_window(client["address"]) or client
    (x, y), (w, h) = c["at"], c["size"]
    return x, y, w, h


def move_cursor(x: int, y: int):
    dispatch("movecursor", str(int(x)), str(int(y)))


def cursor_pos():
    p = hyprctl("cursorpos", as_json=True)
    return p["x"], p["y"]
