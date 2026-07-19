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
