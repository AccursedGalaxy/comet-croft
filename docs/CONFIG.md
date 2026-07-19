# Comet Croft — Config Decisions

Per-tier record of deliberate config choices and why. The boot-test harness
(headless Fabric server, scratchpad `boottest/boottest.sh`) is the verify
gate for every tier. Requires Java 21+ (mise-installed Temurin 25 on this
machine; system JDK is 17).

## Tier 1 — Serene Seasons + Farmer's Delight Refabricated

**Files:** `config/sereneseasons/seasons.toml`, `config/sereneseasons/fertility.toml`

- **Season pacing:** `sub_season_duration = 2` → 3 sub-seasons × 2 days ×
  20 min = **~2h real play per season, ~8h per in-game year**. Long enough
  that "it's autumn" shapes a session, short enough that a casual week sees
  a full year. Default (8) would be 32h/year — too slow to ever feel the
  cycle.
- **Gentle fertility (THEME: no anxiety):** `out_of_season_crop_behavior = 0`
  — out-of-season crops grow at ~1/6 speed, never break. This is the mod
  default but pinned deliberately; **never set 1 (no growth) or 2 (break)**.
- **Greenhouse escape hatch:** any glass block within 16 blocks above a crop
  makes it fully fertile year-round (`#c:glass_blocks`). Worth surfacing to
  players in pack docs/tips later.
- **FD ↔ SS crop integration ships with FD Refabricated** — it generates
  `sereneseasons:*_crops` tags itself (onion spring+autumn, cabbage
  autumn+winter, tomato summer, rice summer+autumn; mushroom colonies
  untagged = always fertile). No pack datapack needed. Vanilla crops are
  covered by SS's own defaults.
- **FD config left at defaults** (they're sensible; no seasons-related keys
  exist there).
- **Dependency gotcha:** Serene Seasons requires **GlitchCore**, but its
  Modrinth metadata doesn't declare it — packwiz reported "all dependencies
  added" and the boot gate caught the crash. Lesson: never trust packwiz
  dep resolution alone; every tier ends with a boot test.

Winter note: snow generates and persists all winter (melt disabled in
winter sub-seasons by mod default), melts in spring. Purely visual +
slow-growth; nothing destroys farms.

## Tier 2 — Delight addon ring

Added: More Delight, Rustic Delight, Ube's Delight, Crate Delight,
Storage Delight, 3D Placeable Food, Display Delight (+ Delight Lib dep).

- **No season datapack needed:** Rustic Delight and Ube's Delight ship
  their own `sereneseasons` crop tags (cotton spring+summer; bell pepper
  and coffee summer+autumn; ube/lemongrass spring+summer; garlic/ginger
  summer+autumn; everything dormant in winter). The other five addons add
  zero crop blocks. Deliberately NOT mirroring these tags in a pack
  datapack — duplication would drift when upstream updates.
- **All configs left at defaults** for now. Tuning candidates for the
  polish pass: `config/rusticdelight.json` and `config/ubesdelight.json`
  wild-crop spawn chances and trader toggles.
- **Known wart (upstream, open issues):** More Delight × Rustic Delight
  cutting-board collision on diced-potato outputs — one recipe silently
  wins. Harmless; fixable later with a pack recipe override if it bothers
  playtests.
- Boot gate: PASS (36 mods server-side).

## Tier 3 — Decor layer

Added: Macaw's Furniture / Windows / Roofs / Fences & Walls / Lights &
Lamps (rest of the suite by build-need later), Rechiseled (+ SuperMartijn642
Core/Config libs + Fusion), Additional Lanterns, Swinging Lanterns,
Lanterns Belong on Walls, Farmhouse Decorations. Configs at defaults —
decor mods need none.

- **Side-metadata fix:** Modrinth marks Fusion (Connected Textures) as
  client-only, but Rechiseled hard-depends on it on the server too →
  `mods/fusion-connected-textures.pw.toml` overridden to `side = "both"`.
  Boot gate caught the server crash.
- **Harness lesson:** always `packwiz refresh` after edits — a stale index
  hash makes packwiz-installer abort with the misleading message "Update
  cancelled by user!".
- Boot gate: PASS (47 mods server-side).
