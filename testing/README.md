# Comet Croft E2E test pipeline

Full end-to-end testing for the modpack on this machine: it validates the
pack, boots the dedicated server headless, launches the real modded client
through Prism Launcher, plays the game with a virtual keyboard/mouse, and
captures screenshots, video, and logs for analysis.

## How it works

| Piece | Mechanism |
|---|---|
| Pack sync | `packwiz serve` on :8081 — the `CometCroftDev` Prism instance's pre-launch hook syncs the working tree into the instance on every launch |
| Game launch | `prismlauncher --launch CometCroftDev` (portable install at `~/.local/opt/prismlauncher`) |
| Into a world | Prism singleplayer quickplay (`JoinWorldOnLaunch` in instance.cfg, set/cleared by the pipeline) |
| Input | Virtual uinput keyboard + mouse (`/dev/uinput`, needs `input` group). Kernel-level, works natively on Wayland. Typing maps through the German layout. |
| Window control | `hyprctl` (focus, cursor position, geometry, close) |
| Screenshots | `grim`, cropped to the game window |
| Video | grim frame loop (2 fps JPEG) assembled to mp4 by ffmpeg |
| Readiness | Tailing the instance's `logs/latest.log` for markers (LWJGL up, player logged in, …) |
| Analysis | `lib/logscan.py` — errors/warnings/stacktraces/milestones per run |

## Usage

```sh
cd testing
uv venv .venv && uv pip install --python .venv/bin/python evdev   # once
.venv/bin/python e2e.py static          # pack validation, no launch
.venv/bin/python e2e.py server         # headless dedicated-server boot test
.venv/bin/python e2e.py client        # client → title screen → screenshots
.venv/bin/python e2e.py play --world test   # quickplay into a world and play
.venv/bin/python e2e.py all
```

Each run writes `testing/runs/<UTC>_<stage>/` with `report.md`,
`results.json`, screenshots, `*.mp4`, the run's slice of `latest.log`,
prism/packwiz logs, and `steps.log`.

## Stages

- **static** — mirrors the repo to a scratch dir, runs `packwiz refresh`,
  fails if the committed `index.toml` is stale or contains junk paths
  (`.ruff_cache`, `__pycache__`, …); lints every `mods/*.pw.toml` and
  reports the client/server/both side split.
- **server** — runs `server/setup.sh` against the local working tree in a
  scratch dir, boots the Fabric server, waits for `Done`, issues console
  commands (`seed`, `locate structure …`, `chunky help`), stops cleanly,
  and fails on log errors.
- **client** — launches the client with no quickplay target, waits for the
  render backend, screenshots the FancyMenu title screen twice (the GLSL
  sky shader is animated), then closes the window gracefully.
- **play** — quickplays into a world, then: F3 overlay, `/time set day`,
  `/weather clear`, four camera quarter-turns, walking + jumping,
  inventory + JEI, Xaero world map, pause menu, Save & Quit — with a
  screenshot at every step and a full-session video.

## Caveats

- The client stages run on the live Hyprland session and take over
  focus/input while the game is up — don't fight the mouse during a run.
- The virtual-input charmap is de-layout specific (`lib/vinput.py`).
- Screenshots are the ground truth: the agent (or you) should eyeball them;
  pixel-perfect UI assertions are deliberately out of scope.
