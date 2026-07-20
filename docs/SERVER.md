# Comet Croft — Dedicated Server Guide

The pack is server-ready out of the box: every mod carries correct
side metadata, so a packwiz server install pulls exactly the server set
(no Sodium/Iris/FancyMenu on the server), plus two server-only tools —
**LuckPerms** (permissions) and **Chunky** (pre-generation) — that never
ship to clients.

## Quick start (the whole thing)

```bash
git clone <repo> comet-croft && cd comet-croft/server
./setup.sh --accept-eula        # local test; add the raw pack URL for remote hosts
./start.sh
```

For a remote host, upload only `server/setup.sh` and run:

```bash
./setup.sh --accept-eula https://raw.githubusercontent.com/AccursedGalaxy/comet-croft/master/pack.toml
```

`start.sh` re-syncs the pack from that URL on every boot, so shipping a
pack update to the server = push to the repo + restart the server.

What setup gives you: Fabric server (MC 26.1.2 / loader 0.19.3), the
server-side mod set, `server.properties` with the pack's defaults
(view 8 / sim 8, whitelist ON, `sync-chunk-writes=false`), and a
`start.sh` with the pack's G1GC flags at 4G heap (6G for >8 players).

## First boot checklist

1. `whitelist add <player>` for everyone joining (whitelist is on by
   default — flip `white-list=false` in server.properties if you truly
   want it open).
2. Pre-generate the spawn region so nobody eats Terralith+Tectonic gen
   cost live: `chunky radius 3000` then `chunky start`. This is THE
   biggest server-smoothness lever in this pack (see PERFORMANCE.md —
   all our worldgen cost is gen-time). /rtp reaches out to 10k blocks
   and generates lazily; that's fine, it's async (FastRTP).
3. Set the sky calendar to match seasons: `/sga:admin yearlength set 24`
   (see CONFIG.md Tier 5).

## Permissions (LuckPerms)

LuckPerms is installed server-side only — singleplayer falls back to
vanilla op rules and never sees it. Two-tier model, matching the pack's
cozy intent:

**Everyone (default group)** — the homestead QoL kit. Melius Essentials
player commands generally work for non-ops out of the box; if any
refuse, grant explicitly (paste into the server console):

```
lp group default permission set fabric-essentials.command.home true
lp group default permission set fabric-essentials.command.sethome true
lp group default permission set fabric-essentials.command.deletehome true
lp group default permission set fabric-essentials.command.homes true
lp group default permission set fabric-essentials.command.warp true
lp group default permission set fabric-essentials.command.warps true
lp group default permission set fabric-essentials.command.tpa true
lp group default permission set fabric-essentials.command.tpaccept true
lp group default permission set fabric-essentials.command.tpdeny true
lp group default permission set fabric-essentials.command.back true
lp group default permission set fabric-essentials.command.enderchest true
lp group default permission set fabric-essentials.command.workbench true
```

`/rtp` needs nothing: `config/fast-rtp.json` ships
`requirePermission=false` (the 30s cooldown is the limiter).

**Trusted group** — flight and the cheatier conveniences. Deliberately
NOT default: on a survival homestead server, free flight deflates the
game. Create once, then add people:

```
lp creategroup trusted
lp group trusted permission set fabric-essentials.command.fly true
lp group trusted permission set fabric-essentials.command.flyspeed true
lp group trusted permission set fabric-essentials.command.walkspeed true
lp group trusted permission set fabric-essentials.command.heal true
lp group trusted permission set fabric-essentials.command.feed true
lp user <name> parent add trusted
```

Admin commands (`/setwarp`, `/broadcast`, `/invulnerable`, Chunky,
Structurify reloads) stay op-only; `op <name>` as usual. The LuckPerms
web editor (`lp editor`) is the comfortable way to manage all of this
once the server is live.

## Server-side notes already handled by the pack

- `config/fabric-essentials.json` — 5 homes, no teleport warmup.
- `config/fast-rtp.json` — 500–10k block band, ocean/river landings
  blocked, 30s cooldown.
- Structure density (Structurify 1.3x), worldgen stack, and season/sky
  pacing are all pack-level and identical on server and client.
- C2ME runs server-side too (alpha channel — pin bumps deliberately,
  see CONFIG.md Tier 6 warts).
- Serene Seasons syncs seasons to clients automatically; Lunar events,
  meteors, and the sky layer are all server-driven and multiplayer-safe.

## What we deliberately did NOT add

- No Discord bridge, no tab-list/chat-format mods, no anti-cheat, no
  sleep-voting — add by real need, not speculatively (THEME: QoL
  infrastructure only when it earns its place). Sleep-vote note: with
  Serene Seasons day-length pacing, majority-sleep default
  (`playersSleepingPercentage`) is usually enough.
