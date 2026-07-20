"""Screen capture: grim stills + a frame-loop video recorder (ffmpeg mp4).

grim captures a whole Wayland output or a region; regions let us crop to
the game window using geometry from hypr.window_geometry().
"""

import os
import subprocess
import threading
import time
from pathlib import Path

from . import hypr


def _grim_env():
    return dict(os.environ, HYPRLAND_INSTANCE_SIGNATURE=hypr._signature())


def screenshot(
    path: str | Path,
    region: tuple | None = None,
    output: str | None = None,
    jpeg: bool = False,
):
    """Capture a still. region=(x,y,w,h) in global coords, else full output."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["grim"]
    if jpeg:
        cmd += ["-t", "jpeg", "-q", "85"]
    if region:
        x, y, w, h = region
        cmd += ["-g", f"{x},{y} {w}x{h}"]
    elif output:
        cmd += ["-o", output]
    else:
        cmd += ["-o", hypr.focused_monitor()["name"]]
    cmd.append(str(path))
    subprocess.run(cmd, env=_grim_env(), check=True, timeout=15)
    return path


def shot_window(path: str | Path, client: dict, jpeg: bool = False):
    return screenshot(path, region=hypr.window_geometry(client), jpeg=jpeg)


class Recorder:
    """Poor-man's screen recorder: grim frames at ~fps, assembled by ffmpeg.

    Frame-accurate enough for gameplay analysis; not meant to be smooth.
    """

    def __init__(self, run_dir: Path, name: str = "session", fps: float = 2.0):
        self.frames_dir = Path(run_dir) / f"frames_{name}"
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self.out = Path(run_dir) / f"{name}.mp4"
        self.fps = fps
        self._stop = threading.Event()
        self._thread = None
        self._client = None
        self._n = 0

    def start(self, client: dict | None = None):
        self._client = client
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        interval = 1.0 / self.fps
        while not self._stop.is_set():
            t0 = time.time()
            frame = self.frames_dir / f"{self._n:05d}.jpg"
            try:
                if self._client:
                    shot_window(frame, self._client, jpeg=True)
                else:
                    screenshot(frame, jpeg=True)
                self._n += 1
            except Exception:
                pass  # window may be mid-teardown; keep rolling
            dt = time.time() - t0
            self._stop.wait(max(0.0, interval - dt))

    def stop(self) -> Path | None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=10)
        if self._n == 0:
            return None
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-framerate",
                str(self.fps),
                "-i",
                str(self.frames_dir / "%05d.jpg"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-vf",
                "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                str(self.out),
            ],
            check=True,
            timeout=300,
        )
        return self.out
