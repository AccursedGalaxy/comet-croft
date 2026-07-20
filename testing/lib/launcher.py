"""Launch orchestration: packwiz serve + Prism Launcher + readiness probes.

The CometCroftDev instance has a pre-launch hook that syncs mods from
http://localhost:8081/pack.toml, so `packwiz serve` must be running with
the repo's working tree before the client starts.
"""

import re
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACKWIZ = Path.home() / "go" / "bin" / "packwiz"
PRISM = Path.home() / ".local" / "bin" / "prismlauncher"
PRISM_DATA = Path.home() / ".local" / "opt" / "prismlauncher"
INSTANCE = "CometCroftDev"
INSTANCE_DIR = PRISM_DATA / "instances" / INSTANCE
GAME_DIR = INSTANCE_DIR / ".minecraft"
LATEST_LOG = GAME_DIR / "logs" / "latest.log"
SERVE_PORT = 8081


def game_java_pids() -> set[int]:
    """PIDs of java processes running this instance's Minecraft client."""
    pids = set()
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            cmd = (p / "cmdline").read_bytes().replace(b"\0", b" ")
        except OSError:
            continue
        if b"instances/" + INSTANCE.encode() in cmd and b"java" in cmd:
            pids.add(int(p.name))
    return pids


def find_game_window(timeout: float = 300):
    """Find the game window by owning PID (title/class are pack-customized)."""
    from . import hypr

    deadline = time.time() + timeout
    while time.time() < deadline:
        pids = game_java_pids()
        for c in hypr.clients():
            if c.get("pid") in pids:
                return c
        time.sleep(2)
    return None


class PackwizServe:
    def __init__(self, log_path: Path):
        self.log = open(log_path, "w")
        self.proc = None

    def __enter__(self):
        # a stale `packwiz serve` (e.g. left from manual testing) would serve
        # outdated content and shadow ours — clear the port first
        subprocess.run(["pkill", "-f", "packwiz serve"], capture_output=True)
        time.sleep(1)
        self.proc = subprocess.Popen(
            [str(PACKWIZ), "serve", "--port", str(SERVE_PORT)],
            cwd=REPO,
            stdout=self.log,
            stderr=subprocess.STDOUT,
        )
        deadline = time.time() + 15
        url = f"http://localhost:{SERVE_PORT}/pack.toml"
        while time.time() < deadline:
            if self.proc.poll() is not None:
                raise RuntimeError(
                    "packwiz serve exited early — port busy? see its log"
                )
            try:
                with urllib.request.urlopen(url, timeout=2) as r:
                    if r.status == 200:
                        return self
            except Exception:
                time.sleep(0.5)
        raise RuntimeError("packwiz serve did not come up on :8081")

    def __exit__(self, *exc):
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.log.close()


def set_quickplay_world(world: str | None):
    """Set/clear JoinWorldOnLaunch in instance.cfg (Prism singleplayer quickplay)."""
    cfg = INSTANCE_DIR / "instance.cfg"
    text = cfg.read_text()
    new = re.sub(
        r"^JoinWorldOnLaunch=.*$", f"JoinWorldOnLaunch={world or ''}", text, flags=re.M
    )
    cfg.write_text(new)


class GameSession:
    """A running modded-client session launched through Prism."""

    def __init__(self, run_dir: Path, world: str | None = None):
        self.run_dir = Path(run_dir)
        self.world = world
        self.proc = None
        self.log_offset = 0

    def start(self):
        # clean slate: a leftover game from an earlier (interrupted) run would
        # be matched as "our" window and shadow this launch
        for pid in game_java_pids():
            subprocess.run(["kill", str(pid)], capture_output=True)
        deadline = time.time() + 20
        while game_java_pids() and time.time() < deadline:
            time.sleep(1)
        # also close any lingering Prism launcher UI: it would tile next to
        # the game (changing its geometry) and absorb --launch via IPC
        subprocess.run(
            ["pkill", "-f", str(PRISM_DATA / "bin" / "prismlauncher")],
            capture_output=True,
        )
        time.sleep(2)
        # truncate marker: remember where latest.log ends before this run
        self.log_offset = LATEST_LOG.stat().st_size if LATEST_LOG.exists() else 0
        set_quickplay_world(self.world)
        out = open(self.run_dir / "prism.log", "w")
        self.proc = subprocess.Popen(
            [str(PRISM), "--launch", INSTANCE], stdout=out, stderr=subprocess.STDOUT
        )
        return self

    def read_new_log(self) -> str:
        if not LATEST_LOG.exists():
            return ""
        with open(LATEST_LOG, errors="replace") as f:
            f.seek(
                self.log_offset if LATEST_LOG.stat().st_size >= self.log_offset else 0
            )
            return f.read()

    def wait_for_log(self, pattern: str, timeout: float, interval: float = 2.0):
        """Wait until regex `pattern` appears in this session's log output."""
        rx = re.compile(pattern)
        deadline = time.time() + timeout
        while time.time() < deadline:
            m = rx.search(self.read_new_log())
            if m:
                return m
            # Prism is single-instance: our Popen may exit after handing the
            # launch to an existing launcher process, so only treat proc exit
            # as fatal when no instance java is alive either.
            if self.proc and self.proc.poll() is not None and not game_java_pids():
                raise RuntimeError(
                    f"game process exited (rc={self.proc.returncode}) while "
                    f"waiting for /{pattern}/ — check prism.log"
                )
            time.sleep(interval)
        raise TimeoutError(f"log marker /{pattern}/ not seen in {timeout}s")

    def running(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def wait_exit(self, timeout: float = 120):
        if self.proc:
            self.proc.wait(timeout=timeout)

    def kill(self):
        proc = self.proc
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
        # Prism may hand the launch off to an existing launcher process, so
        # terminating our Popen does not reliably end the game — kill the
        # instance's java directly if it survived.
        for pid in game_java_pids():
            subprocess.run(["kill", str(pid)], capture_output=True)

    def collect_logs(self):
        """Copy this run's game log slice + prism log into the run dir."""
        (self.run_dir / "latest.log").write_text(self.read_new_log())
        crash_dir = GAME_DIR / "crash-reports"
        if crash_dir.exists():
            for c in sorted(crash_dir.iterdir(), reverse=True)[:1]:
                if c.stat().st_mtime > time.time() - 3600:
                    shutil.copy(c, self.run_dir / c.name)
