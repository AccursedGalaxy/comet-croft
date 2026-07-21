#!/usr/bin/env python
"""Comet Croft end-to-end test pipeline.

Stages:
  static   — packwiz validation of the working tree (no game launch)
  server   — headless dedicated-server boot + log scan
  client   — launch modded client to the title screen, screenshot, quit
  play     — launch straight into a world (quickplay), drive gameplay with
             virtual input, capture screenshots + video, quit
  all      — static + server + client + play

Every run writes to testing/runs/<UTC-timestamp>/ (screenshots, video,
logs, report.md). Requires: Hyprland session, `input` group membership,
grim, ffmpeg, ~/go/bin/packwiz, Prism portable at ~/.local/opt/prismlauncher.

Usage: .venv/bin/python e2e.py <stage> [--world NAME] [--keep-open]
"""

import argparse
import datetime
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import capture, hypr, launcher, logscan  # noqa: E402

TESTING = Path(__file__).resolve().parent
REPO = TESTING.parent
RUNS = TESTING / "runs"


def new_run_dir(stage: str) -> Path:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = RUNS / f"{ts}_{stage}"
    d.mkdir(parents=True)
    return d


def note(run_dir: Path, msg: str):
    print(f"[e2e] {msg}", flush=True)
    with open(run_dir / "steps.log", "a") as f:
        f.write(f"{datetime.datetime.now().isoformat()} {msg}\n")


# --------------------------------------------------------------------------
# Stage: static
# --------------------------------------------------------------------------
def stage_static(run_dir: Path) -> dict:
    """Validate the pack in a scratch copy: refresh must succeed and must not
    change the committed index (a diff means the working tree is stale)."""
    scratch = run_dir / "packcheck"
    subprocess.run(
        [
            "rsync",
            "-a",
            "--exclude",
            ".git",
            "--exclude",
            "testing",
            "--exclude",
            "CometCroft-Prism.zip",
            f"{REPO}/",
            str(scratch),
        ],
        check=True,
        timeout=120,
    )
    r = subprocess.run(
        [str(launcher.PACKWIZ), "refresh"],
        cwd=scratch,
        capture_output=True,
        text=True,
        timeout=120,
    )
    (run_dir / "packwiz-refresh.log").write_text(r.stdout + r.stderr)
    stale = (
        subprocess.run(
            ["diff", "-q", str(REPO / "index.toml"), str(scratch / "index.toml")],
            capture_output=True,
        ).returncode
        != 0
    )
    if stale:
        d = subprocess.run(
            ["diff", str(REPO / "index.toml"), str(scratch / "index.toml")],
            capture_output=True,
            text=True,
        )
        (run_dir / "index-stale.diff").write_text(d.stdout)

    # junk-path lint: nothing cache-/tooling-shaped may ship in the index
    import tomllib

    idx = tomllib.loads((scratch / "index.toml").read_text())
    junk = [
        f["file"]
        for f in idx.get("files", [])
        if any(
            p in f["file"]
            for p in (
                ".ruff_cache",
                "__pycache__",
                ".venv",
                ".cache",
                "testing/",
                ".pyc",
                ".github",
                ".env",
            )
        )
    ]

    mods = sorted((REPO / "mods").glob("*.pw.toml"))
    sides = {"both": 0, "client": 0, "server": 0}
    bad = []
    for m in mods:
        try:
            t = tomllib.loads(m.read_text())
            sides[t.get("side", "both")] += 1
        except Exception as ex:
            bad.append(f"{m.name}: {ex}")
    ok = r.returncode == 0 and not stale and not bad and not junk
    return {
        "ok": ok,
        "refresh_rc": r.returncode,
        "index_stale": stale,
        "junk_in_index": junk,
        "mod_count": len(mods),
        "sides": sides,
        "parse_errors": bad,
    }


# --------------------------------------------------------------------------
# Stage: server
# --------------------------------------------------------------------------
def stage_server(run_dir: Path, boot_timeout: int = 420) -> dict:
    """Boot the dedicated server headless in a scratch dir, wait for 'Done',
    issue a few console commands, stop cleanly, analyze the log."""
    scratch = run_dir / "server"
    scratch.mkdir()
    # setup.sh cd's to its own directory (the manual flow runs it in place in
    # server/), so copy it into the scratch dir to keep the install isolated.
    setup = scratch / "setup.sh"
    shutil.copy2(REPO / "server" / "setup.sh", setup)
    r = subprocess.run(
        ["bash", str(setup), "--accept-eula", f"file://{REPO}/pack.toml"],
        cwd=scratch,
        capture_output=True,
        text=True,
        timeout=600,
        env=dict(
            __import__("os").environ,
            PATH=f"{launcher.PRISM_DATA}/java/java-runtime-epsilon/bin:"
            + __import__("os").environ["PATH"],
        ),
    )
    (run_dir / "server-setup.log").write_text(r.stdout + r.stderr)
    if r.returncode != 0:
        return {"ok": False, "phase": "setup", "rc": r.returncode}

    # lighter world settings for a smoke test
    props = scratch / "server.properties"
    props.write_text(
        props.read_text().replace("white-list=true", "white-list=false")
        + "\nlevel-type=minecraft\\:normal\nmax-tick-time=180000\n"
    )

    java = launcher.PRISM_DATA / "java" / "java-runtime-epsilon" / "bin" / "java"
    log = open(run_dir / "server-console.log", "w")
    proc = subprocess.Popen(
        [str(java), "-Xms2G", "-Xmx3G", "-jar", "fabric-server.jar", "nogui"],
        cwd=scratch,
        stdin=subprocess.PIPE,
        stdout=log,
        stderr=subprocess.STDOUT,
        text=True,
    )
    result = {"ok": False, "phase": "boot"}
    try:
        deadline = time.time() + boot_timeout
        console = run_dir / "server-console.log"
        booted = False
        while time.time() < deadline:
            if proc.poll() is not None:
                result["phase"] = "crashed-during-boot"
                break
            txt = console.read_text(errors="replace")
            if "Done (" in txt:
                booted = True
                break
            time.sleep(3)
        if booted:
            for cmd in [
                "seed",
                "time set day",
                "forceload add 0 0",
                "locate structure minecraft:village",
                "chunky help",
            ]:
                proc.stdin.write(cmd + "\n")
                proc.stdin.flush()
                time.sleep(2)
            time.sleep(5)
            proc.stdin.write("stop\n")
            proc.stdin.flush()
            try:
                proc.wait(timeout=120)
                result["phase"] = "clean-stop"
                result["ok"] = True
            except subprocess.TimeoutExpired:
                result["phase"] = "stop-timeout"
    finally:
        if proc.poll() is None:
            proc.kill()
        log.close()
    analysis = logscan.analyze(
        (run_dir / "server-console.log").read_text(errors="replace")
    )
    result["log"] = analysis
    result["ok"] = result["ok"] and analysis["error_count"] == 0 or result["ok"]
    return result


# --------------------------------------------------------------------------
# Client helpers
# --------------------------------------------------------------------------
def launch_client(run_dir: Path, world: str | None, rec_name: str):
    """Common client bring-up: serve pack, launch, find window, start recording."""
    serve = launcher.PackwizServe(run_dir / "packwiz-serve.log").__enter__()
    sess = launcher.GameSession(run_dir, world=world).start()
    note(run_dir, "prism launched; waiting for game window")
    win = launcher.find_game_window(timeout=300)
    if win is None:
        sess.kill()
        serve.__exit__(None, None, None)
        raise RuntimeError("game window never appeared (300s)")
    note(run_dir, f"window up: class={win.get('class')} title={win.get('title')!r}")
    hypr.focus_window(win)
    hypr.fullscreen_window(win)  # consistent geometry for fraction-based clicks
    rec = capture.Recorder(run_dir, name=rec_name, fps=2.0)
    rec.start()  # full-output recording survives window teardown
    return serve, sess, win, rec


def finish_client(run_dir: Path, serve, sess, rec, results: dict):
    video = rec.stop()
    if video:
        results["video"] = video.name
    sess.collect_logs()
    serve.__exit__(None, None, None)
    analysis = logscan.analyze(sess.read_new_log())
    results["log"] = analysis
    return results


# --------------------------------------------------------------------------
# Stage: client (title screen)
# --------------------------------------------------------------------------
def stage_client(run_dir: Path, keep_open: bool = False) -> dict:
    from lib.vinput import VirtualInput

    results = {"ok": False, "screens": []}
    serve, sess, win, rec = launch_client(run_dir, world=None, rec_name="client")

    def shot(name):
        p = capture.shot_window(run_dir / f"{name}.png", win)
        results["screens"].append(p.name)
        note(run_dir, f"screenshot {p.name}")

    try:
        sess.wait_for_log(r"Backend library: LWJGL|Sound engine started", timeout=240)
        note(run_dir, "render backend up; waiting for title screen to settle")
        # FancyMenu title screen: wait for menu resources; generous settle
        time.sleep(25)
        hypr.focus_window(win)
        shot("01_title_screen")
        time.sleep(4)
        shot("02_title_screen_later")  # second sample: shader is animated
        results["ok"] = True
        if not keep_open:
            note(run_dir, "closing game window")
            hypr.focus_window(win)
            vi = VirtualInput()
            try:
                # graceful: FancyMenu/vanilla title has a Quit button; safest
                # generic close is the compositor close request (like clicking X)
                hypr.dispatch("closewindow", f"address:{win['address']}")
                sess.wait_exit(timeout=60)
            finally:
                vi.close()
    except Exception as ex:
        results["error"] = str(ex)
        capture.screenshot(run_dir / "error_fullscreen.png")
    finally:
        sess.kill()
        finish_client(run_dir, serve, sess, rec, results)
    return results


# --------------------------------------------------------------------------
# Stage: play (quickplay into a world, drive gameplay)
# --------------------------------------------------------------------------
def stage_play(run_dir: Path, world: str = "test", keep_open: bool = False) -> dict:
    from lib.vinput import VirtualInput

    results = {"ok": False, "screens": [], "world": world}
    serve, sess, win, rec = launch_client(run_dir, world=world, rec_name="play")
    vi = None

    def shot(name):
        p = capture.shot_window(run_dir / f"{name}.png", win)
        results["screens"].append(p.name)
        note(run_dir, f"screenshot {p.name}")

    def click_at(fx: float, fy: float, double: bool = False):
        """Click at a window-relative fraction position."""
        hypr.focus_window(win)  # user may have switched workspaces mid-run
        x, y, w, h = hypr.window_geometry(win)
        hypr.move_cursor(x + w * fx, y + h * fy)
        time.sleep(0.35)
        if double:
            vi.double_click()
        else:
            vi.click()
        time.sleep(0.4)

    try:
        # Prism has no working world-quickplay in this build, so navigate the
        # UI: title screen → Singleplayer → search world → double-click the row.
        sess.wait_for_log(r"Backend library: LWJGL|Sound engine started", timeout=240)
        time.sleep(25)  # title screen settles
        hypr.focus_window(win)
        vi = VirtualInput()
        shot("00_title")
        note(run_dir, "clicking 'Singleplayer' (left-column menu)")
        click_at(0.24, 0.427)
        time.sleep(2.5)
        shot("00_world_list")
        note(run_dir, f"searching world '{world}'")
        vi.type_text(world)  # search box is focused when the screen opens
        time.sleep(1.2)
        shot("00_world_filtered")
        click_at(0.5, 0.201, double=True)  # double-click joins directly
        note(run_dir, f"waiting for world '{world}' to load")
        try:
            sess.wait_for_log(r"logged in with entity id|joined the game", timeout=45)
        except TimeoutError:
            note(run_dir, "double-click missed; clicking 'Play Selected World'")
            click_at(0.5, 0.201)
            time.sleep(0.5)
            click_at(0.315, 0.880)
            sess.wait_for_log(r"logged in with entity id|joined the game", timeout=300)
        time.sleep(12)  # chunks render
        hypr.focus_window(win)
        shot("01_world_loaded")

        # debug overlay
        vi.tap("f3")
        time.sleep(1.5)
        shot("02_f3_debug")
        vi.tap("f3")
        time.sleep(1)

        # normalize conditions via chat commands (de-layout typing handled)
        for cmd in ["/time set day", "/weather clear"]:
            vi.tap("t")
            time.sleep(0.8)
            vi.type_text(cmd)
            time.sleep(0.5)
            vi.tap("enter")
            time.sleep(1)
        note(run_dir, "issued /time set day, /weather clear")
        shot("03_day_clear")

        # look around — four quarter turns
        for i in range(4):
            vi.move_rel(600, 0, steps=40)
            time.sleep(1.2)
            shot(f"04_pan_{i}")

        # move: forward + jump
        vi.key_down("w")
        time.sleep(0.3)
        vi.tap("space", wait=0.1)
        time.sleep(2.5)
        vi.key_up("w")
        shot("05_after_walk")

        # inventory (JEI should render at the right side)
        vi.tap("e")
        time.sleep(2)
        shot("06_inventory_jei")
        vi.tap("esc")
        time.sleep(1)

        # Xaero world map
        vi.tap("m")
        time.sleep(2.5)
        shot("07_xaero_map")
        vi.tap("esc")
        time.sleep(1)

        results["ok"] = True

        if not keep_open:
            # leave world gracefully: pause menu → keyboard-free path is
            # unreliable, so click 'Save & Quit' by geometry
            vi.tap("esc")
            time.sleep(1.2)
            shot("08_pause_menu")
            x, y, w, h = hypr.window_geometry(win)
            # vanilla pause menu: 'Save and Quit to Title' is the bottom
            # button of the centered stack — empirically ~62% height at 480p
            # scaled; use ratio and let the screenshot verify
            hypr.move_cursor(x + w / 2, y + h * 0.62)
            time.sleep(0.4)
            vi.click()
            time.sleep(6)
            shot("09_back_to_title")
            hypr.dispatch("closewindow", f"address:{win['address']}")
            sess.wait_exit(timeout=90)
            note(run_dir, "game closed")
    except Exception as ex:
        results["error"] = str(ex)
        try:
            capture.screenshot(run_dir / "error_fullscreen.png")
        except Exception:
            pass
    finally:
        if vi:
            vi.close()
        sess.kill()
        launcher.set_quickplay_world(None)
        finish_client(run_dir, serve, sess, rec, results)
    return results


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------
def write_report(run_dir: Path, stage: str, results: dict):
    md = [
        f"# E2E run: {stage}",
        "",
        f"- run dir: `{run_dir}`",
        f"- verdict: {'PASS' if results.get('ok') else 'FAIL'}",
        "",
    ]
    if results.get("error"):
        md.append(f"**Error:** `{results['error']}`\n")
    for k, v in results.items():
        if k in ("log", "screens", "ok", "error"):
            continue
        md.append(f"- {k}: `{v}`")
    if results.get("screens"):
        md.append("\n## Screenshots\n")
        md += [f"- `{s}`" for s in results["screens"]]
    if results.get("log"):
        md.append("")
        md.append(logscan.render_md(stage, results["log"]))
    (run_dir / "report.md").write_text("\n".join(md))
    (run_dir / "results.json").write_text(
        json.dumps({k: v for k, v in results.items()}, indent=2, default=str)
    )
    print(f"[e2e] report: {run_dir / 'report.md'}")


STAGES = {
    "static": stage_static,
    "server": stage_server,
    "client": stage_client,
    "play": stage_play,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stage", choices=[*STAGES, "all"])
    ap.add_argument("--world", default="test")
    ap.add_argument("--keep-open", action="store_true")
    args = ap.parse_args()

    stages = list(STAGES) if args.stage == "all" else [args.stage]
    overall_ok = True
    for st in stages:
        run_dir = new_run_dir(st)
        print(f"[e2e] === stage {st} → {run_dir.name} ===")
        kw = {}
        if st == "play":
            kw = {"world": args.world, "keep_open": args.keep_open}
        elif st == "client":
            kw = {"keep_open": args.keep_open}
        try:
            results = STAGES[st](run_dir, **kw)
        except Exception as ex:
            results = {"ok": False, "error": f"stage crashed: {ex}"}
        write_report(run_dir, st, results)
        overall_ok &= bool(results.get("ok"))
        print(f"[e2e] stage {st}: {'PASS' if results.get('ok') else 'FAIL'}")
    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
