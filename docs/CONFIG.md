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

## Tier 4 — Ambience layer

Added: AmbientSounds (+CreativeCore), Sound Physics Remastered, Presence
Footsteps, Falling Leaves, Cool Rain.

**Quiet-biased defaults shipped via YOSBR** (`config/yosbr/config/...`) —
these are player *preferences*, so they apply on first run only and stay
player-adjustable afterwards (unlike the hard-shipped gameplay configs):
- `ambientsounds-client.json`: engine `volume = 0.55` (~45% cut; the only
  global loudness knob the mod has). NOTE: filename inferred from
  CreativeCore convention, not confirmed — verify in-game that the
  AmbientSounds GUI shows volume 55%; if not, find the generated filename
  in the instance's config/ and rename ours.
- `presencefootsteps/userconfig.json` (path confirmed): global volume 55
  (default 70), own steps 70, other players 60, hostile 55, passive 45,
  wet 40, foliage 70. Mob footsteps kept on but under vanilla sounds.
- `fallingleaves2.json` (path confirmed): `leafSpawnRate = 10` (half
  default), light conifer dusting 4 (default 0), snowflakes 18 (default
  30), autumn burst factor kept at 1.8.
- `coolrain.json` (path confirmed): all category volumes cut ~40%
  (vanilla rain 0.12, surfaces 0.1–0.4), storm winds/thunder quieter and
  rarer (winds 0.9/freq 25, thunder 6.0/freq 220).
- Sound Physics Remastered: deliberately NOT shipped — its defaults are
  physically-motivated. If interiors read too echoey in playtests, first
  lever is `reverbGain` 1.0 → ~0.7–0.8.

Ear-check list for playtests: forest day/night, rain on a farmhouse roof
(inside + outside), a storm, walking through crops, winter snowfall
density. Bias: ambience should sit UNDER vanilla sounds; when in doubt,
quieter.

## Tier 5 — Sky layer

Added: Spyglass Astronomy, Skyboxify, Oh My Meteors (+Fzzy Config), Lunar.
Lunar pinned to its 26.1 build via version URL (packwiz refuses auto-add on
26.1.2); boots and runs fine on 26.1.2.

**`config/ohmymeteors/ohmymeteors_config.toml`** (copied from generated,
then tuned — do the same after mod updates):
- `meteor_spawn_chance = 400000` (was 30000). Rolled per tick with a player
  online: ≈1 meteor per ~16 MC days ≈ 1–2 per our 24-day year. An occasion.
- Non-destructive impacts: `meteor_griefing = false`,
  `scatter_meteor_griefing = false`, `only_replace_air = true`,
  `spawn_fire_with_meteor = false`. Crater structure still places (over air
  only), meteor still mineable — the cozy version of a meteor fall.
- Overworld only; spawn distance 15–40 blocks from a player.

**`config/lunar-common.toml`** (TOML, not the json5 some docs claim):
- `lunarEventChance = 0.05` (was 0.4) — one event night per ~20 nights,
  i.e. roughly once per in-game year. Rare means rare.
- Event pool trimmed to mild moods: blood 40 (stat-buffed spawns only, no
  siege mechanic exists in this mod), white 40 (monster-free calm night),
  miner 40 (Haste), hero 40, big 15, eclipse 15.
- **Disabled deliberately:** `crimsonMoonWeight = 0` (wither skeletons/
  ghasts — too hostile), `tinyMoonWeight = 0` (open upstream bug #31: low
  gravity kills farm animals), `badOmenMoonWeight = 0` (can chain into a
  vanilla village raid — the one siege-shaped thing in the mod).
- All events sleep-through-able (defaults kept).

Spyglass Astronomy and Skyboxify ship no pack config: Spyglass is tuned by
in-game `/sga:admin` commands per world (yearlength default 8 days; consider
`/sga:admin yearlength set 24` to match the Serene Seasons year); Skyboxify
is driven by OptiFine-format sky resource packs we author later (this is the
comet/aurora art channel — layers support time-of-day fades and day-loop
scheduling).

**Playtest flags:** (1) Spyglass Astronomy's Iris shader compat PR is
unmerged — verify stars/planets render under Complementary before shipping;
(2) Lunar has no first-event grace period on new worlds; (3) OMM meteors
only spawn near online players — SP pacing matches math above.

## Tier 5 errata (found by Tier 6 boot gate)

**Oh My Meteors migrated its config format TOML → YAML** — the tuned
`config/ohmymeteors/ohmymeteors_config.toml` was silently dead; the mod
regenerated defaults as `ohmymeteors_config.yml`. All Tier 5 tuning
(spawn chance 400000, griefing off, air-only structure placement, no
fire, overworld-only, 15–40 block spawn distance) is now ported into the
`.yml` and the stale `.toml` is deleted. Lesson reinforced: after any mod
update, re-check that the config file the pack ships is the one the mod
actually reads (the boot log line "Config '<name>' is missing, generating
default one" is the tell).

## Tier 6 — Worldgen & structures

Added (20 mods + 4 auto-deps): Tectonic (+Lithostitched), Geophilic,
Continents · Towns & Towers (+Cristel Lib), Moog's Missing Villages
(+Moog's Structure Lib), Improved Village Placement · Structory,
Structory: Towers, Explorify · YUNG's API + Better Mineshafts /
Strongholds / Ocean Monuments / Desert Temples / Jungle Temples / Witch
Huts / Extras · Hopo Better Ruined Portals · Structurify, Structure
Layout Optimizer (+Resourceful Config). Rationale and rejects:
docs/SLOTS.md Slots 7–8; perf constraints: docs/PERFORMANCE.md.

**`config/tectonic.json`** — generated defaults, pinned deliberately so
upstream default drift can't silently reshape worlds between pack
versions. Defaults ARE the theme (huge mountains, deep valleys, vanilla
biomes). Documented playtest knobs if terrain fights the homestead
fantasy: `flat_terrain_skew` (raise for more farmable valleys),
`vertical_scale` 1.125 (lower toward 1.0 to tame peaks),
`continents_scale`/`ocean_offset` (land/ocean balance vs the Continents
datapack). Terrain-affecting changes need a new world to judge fairly.

**`config/structurify.json`** —
- `enable_global_spacing_and_separation_modifier = true`, modifier
  **1.3** — every structure set (vanilla + all Tier 6 additions) spreads
  1.3x apart. THEME: gently lived-in, not theme-park; neighbors should
  be a journey. Also the laptop lever: fewer structure starts per chunk
  = cheaper gen. Raise toward 1.5–2.0 if playtests still feel dense.
- `prevent_structure_overlap = true` — no village/tower mashups.
- Per-structure entries (`structures`/`structure_sets` arrays) stay
  empty until a playtest names an offender.

**`config/structure_layout_optimizer.jsonc`** —
`deduplicateShuffledTemplatePoolElementList = true`: extra jigsaw-gen
speed; the cost (vanilla structure-layout seed parity) is already spent
by Tectonic reshaping all terrain.

**Left at generated defaults on purpose:** YUNG suite (its defaults are
the vanilla+ gold standard), Towns & Towers rarity json5s + Cristel Lib
`vanilla_structures` (Structurify's global modifier already handles
density pack-wide — tuning rarity in two places would fight), Improved
Village Placement, Lithostitched, Geophilic/Continents/Structory/
Explorify (datapacks, no config). **Deliberately NOT shipping
`config/c2me.toml`:** it auto-sizes worker threads per machine; shipping
a laptop-capped value would kneecap desktops. The laptop guidance lives
in docs/PERFORMANCE.md instead.

**Side-metadata fix (client crash + silent singleplayer stripping):**
Modrinth marked Lithostitched *and 10 other worldgen mods* (all YUNG's
Better *, YUNG's Extras, MMV + its lib, Improved Village Placement,
Structure Layout Optimizer) as server-side. For packwiz that means
"exclude from client installs" — the client crashed on Tectonic's
missing Lithostitched dep, and the other ten would have silently
vanished from singleplayer worldgen. All 11 overridden to
`side = "both"`. Rule of thumb going forward: **every worldgen/structure
mod must be `side = "both"`** — Modrinth's "server" label means "not
needed to join a multiplayer server", not "unused by the client".

**Known warts:**
- Six benign `Pack declares support for version newer than 81` warnings
  at boot — the 26.2-tagged Stardust-style jars (Continents, Structory,
  Structory: Towers et al.) declare a future pack format; vanilla's
  fallback reads them fine and all worldgen registers. Goes away when
  upstream republishes proper 26.1 metadata.
- C2ME on 26.1.2 is alpha-channel (0.4.0-alpha line) — pin bumps
  deliberately, never blind-update it with the rest of the pack.
- The default-enabled resourcepacks in `config/yosbr/options.txt` are
  pinned by exact zip filename (`file/...`). Any packwiz update that
  changes a resourcepack's filename must update that line in the same
  change, or fresh installs silently get the pack disabled. YOSBR also
  only seeds fresh installs — existing instances keep their own
  options.txt.

**Playtest flags:** (1) settle the Terralith question (two test worlds,
with/without — see SLOTS.md Slot 7); (2) judge structure density at
modifier 1.3 during real play; (3) gen-speed benchmark on a weak machine
(Tectonic v3 had slow-gen history — PERFORMANCE.md); (4) villages under
Tectonic terrain — Improved Village Placement should handle slopes, but
verify no floating/buried villages.

Boot gate: PASS (200 mods server-side, Done in ~21s, Structurify config
confirmed loaded, OMM yml confirmed read).

## Tier 6b — Terralith (A/B verdict: IN)

Added `terralith` 2.6.2 + `seasonal-integration` 1.6.1 (mod jar — adds
Terralith's biomes to Serene Seasons' tropical/blacklist tags; no config,
no pack datapack needed). A/B on seed `cometcroft` vs the Tectonic-only
control; Robin preferred the Terralith terrain. Terratonic (Tectonic's
built-in Terralith merge via Lithostitched) verified live by headless
probe: `locate biome terralith:alpine_grove` hit at y=188.

- Terralith ships no config; all terrain knobs remain in
  `config/tectonic.json`.
- Perf note (PERFORMANCE.md): Terralith is the heaviest common worldgen
  datapack at GEN time only — the laptop preset's C2ME + render-distance
  guidance is what absorbs it; runtime cost stays flat.
- Boot gate: PASS (202 mods server-side).

**Playtest watch:** Serene Seasons snow behavior in terralith:* cold/
tropical biomes across a season change (seasonal-integration's tags are
the fix under test); structure placement into Terralith biomes (Towns &
Towers advertises Terralith compat; watch for biome-mismatched villages).

## Tier 7 — QoL command layer

Added: **Melius Essentials** (`melius-essentials` — the maintained Fabric
Essentials fork, 26.1.2-exact) + **FastRTP** (`fastrtp`). Both
server-side mods that work in singleplayer; both needed the
`side = "both"` override (same Modrinth "server" label trap as Tier 6 —
now confirmed as the default assumption for any server-utility mod).
Considered and rejected: Essential Commands (26.1.1-only, no
fly/walk-speed commands), DarkRTP (`/trigger darkrtp` + "dark mage"
RPG flavor text — off-theme, no real /rtp), Fabric Essentials original
(dead at 1.21.1).

Command surface: `/home` `/sethome` `/warp` `/setwarp` `/tpa` `/back`
`/fly` `/flyspeed` `/walkspeed` `/heal` `/feed` `/hat` + portable
crafting stations (`/anvil` `/enderchest` `/workbench` …) from Melius;
`/rtp` `/rtpback` from FastRTP.

**`config/fabric-essentials.json`** — defaults except
`homes.defaultLimit` 3 → **5** (a homestead pack lives in its homes).
Teleport waiting period is 0 by default (kept — no artificial delay in a
cozy pack).

**`config/fast-rtp.json`** — defaults except:
- `radius = 10000`, `minRadius = 500` (was unlimited/0): keeps /rtp
  inside a sane band — far enough to be a fresh start, bounded so it
  doesn't force-generate chunks tens of thousands of blocks out
  (PERFORMANCE.md: chunk gen is our one real cost).
- Kept: 30s cooldown, overworld-only default dimension, and the biome
  blacklist (no ocean/beach/river landings — vanilla tags, which
  Terralith biomes also carry).

**Permissions caveat:** both mods gate player commands via
fabric-permissions-api. In singleplayer everything works with cheats ON;
without cheats some Melius commands (fly/speed/heal) resolve to op-level
and will refuse. On a shared server, LuckPerms (`luckperms`, on-version)
is the tool if per-player gating is ever wanted — deliberately NOT added
until there's a real server to admin.

Boot gate: PASS (208 mods server-side).

## Tier 8 — Server readiness

Added: **LuckPerms** 5.5.57 + **Chunky** 1.5.3, both `side = "server"`
ON PURPOSE — they exist only in server installs; singleplayer falls back
to vanilla op rules and never carries them. (The inverse of the Tier 6/7
side fixes: for genuinely server-only admin tooling, "server" is
correct.)

Side hygiene pass for lean servers: FancyMenu, Konkrete, Melody, and
Cool Rain were mismarked `both` (client-only UI/audio) → flipped to
`client`. Server install verified to contain zero client mods.

Server bootstrap: `server/setup.sh` (packwiz-ignored, never ships to
clients) — one command produces a ready server: Fabric 26.1.2/0.19.3,
server-side pack install, whitelisted server.properties (view 8/sim 8,
sync-chunk-writes off), start.sh with the PERFORMANCE.md G1 flags at 4G
and a pack re-sync on every boot (pack update = git push + server
restart). Full admin guide incl. the two-tier LuckPerms model (default =
homes/warps/tpa/back; trusted = fly/speed/heal — free flight is
deliberately not default) lives in **docs/SERVER.md**.

Verified end-to-end: setup.sh run in a clean directory against the local
pack → 204 server mods, Done in ~7s, LuckPerms + Chunky active,
FancyMenu family absent.

## Menu video (FancyMenu + WaterMedia) — SUPERSEDED

**Dead section, kept as history (2026-07-21).** The FancyMenu video title
screen was replaced by the bespoke `menu-mod/` Fabric mod
(`mods/comet-croft-menu.jar` takes over the title screen via mixin); the
FancyMenu `ssui.titlescreen` layout is disabled and WaterMedia +
WaterMedia Binaries were removed from the pack. Do NOT re-add them from
the instructions that used to live here. The FancyMenu layer itself
(loading screen role, remaining assets) is being reworked separately.

## Post-Tier-8 hygiene pass (2026-07-21)

Fixes from a critical review of the pack. Root cause of all three: the
Lootr/Trinkets/elytra/graves commits after Tier 8 skipped the tier
discipline (no CONFIG.md entry, no boot gate) and re-imported known traps.

- **Side-metadata regression fixed (the Tier 6 trap, again):** eight mods
  added post-Tier 8 shipped `side = "server"`, i.e. silently absent from
  client installs — in singleplayer that meant no Moog's Voyager/Nether/
  End/Soaring structures, no Easy Elytra Takeoff, no dragon elytra drop,
  and **no graves at all** (Universal Graves + Polymer). All eight flipped
  to `side = "both"`. Standing rule restated: only genuinely
  server-admin-only tooling (LuckPerms, Chunky) is ever `"server"`.
- **`pack.toml` `acceptable-game-versions`** was one malformed string
  (`"26.1,26.1.1"`) that matched nothing, so packwiz refused mods
  published only for 26.1/26.1.1 → fixed to `["26.1", "26.1.1"]`.
- **menu-mod `fabric.mod.json` pinned `minecraft = "~26.1.2"`** (was
  `"*"`). It mixin-patches `TitleScreen` against deobfuscated 26.1.2 names
  with no refmap — on an MC bump it must fail loud at the loader, not load
  and crash mid-render. Jar rebuilt + reinstalled via
  `menu-mod/build-and-install.sh`. Remember to widen/re-pin alongside any
  MC version bump.
- **Docs gap (open):** the post-Tier-8 additions themselves (Lootr,
  Trinkets + elytra suite, Universal Graves, OPAC, Spice of Fabric tuning,
  Waystones/veinminer/Explorer's Compass batch) still have no tier
  entries recording their config rationale — backfill when each area next
  gets touched, and boot-gate them.
- **Playtest flag:** with graves now client-visible, verify a
  trinket-slot elytra actually lands in the grave on death.

## Cooking Tier 2 — drinks, spoilage, seasonal (2026-07-21)

Second increment of the cooking system (Tier 1 = the Delight ring + Spice
of Fabric, already in). Design line unchanged: mechanics may create gentle
reasons to engage (drink variety, preservation), never routine-neglect
deaths. All four `side = "both"`.

- **AlcoCraft+ 2.1.3** — brewing/wine content. Pulled in **Architectury
  API 20.0.9** (new dep, library). No config shipped; defaults are pure
  content.
- **Easter's Delight 1.2.0** — seasonal FD addon. No config shipped.
- **Spoiled 12.1.0** — food spoilage, tuned long via
  `config/yosbr/config/spoiled-common.toml`: total spoil time
  120 s × 80 updates = **8 in-game days** (mod default: 1 day);
  CFB fridge pauses spoilage entirely (`containerModifier` rate 0);
  CFB/FD cabinets, counters and baskets slow it to 25%; golden apple,
  cake, honey bottle and milk added to the blacklist;
  `mergeSpoilingFood = true`. Client config shows freshness as a
  percentage. Notes: config is cached at server start (world restart to
  apply changes); `itemContainerModifier` is dead code on Fabric; FD food
  spoils via `#c:foods` (verified in the pinned jar).
- **Homeostatic 2.13.0.2** — temperature + thirst. The only gameplay
  config knob is passive thirst decay: `randomWaterLoss = 0.01` (minimum;
  default 0.15) via `config/yosbr/config/homeostatic-common.toml`. All
  damage is HARDCODED in the mod, so the cozy line is enforced by the
  `homeostatic-cozy` datapack (`global_packs/required_data/`):
  - Dirty water / suspicious stew / poisonous potato no longer roll the
    Thirst debuff (`effect_chance` 0) — purified water and drinks stay
    strictly better (3 water vs 1), just never punitive.
  - The mod adds its hyperthermia/scalding/dehydration damage types to
    `minecraft:bypasses_invulnerability` and `bypasses_armor`; the
    datapack overrides both tags with `replace: true` + vanilla 26.1.2
    contents (extracted from the client jar), restoring i-frames and
    armor — dehydration drops from ~10 dmg/s to ~1 dmg/s worst case.
    **Trap:** `replace: true` clobbers ANY other mod's additions to these
    two tags; re-check on every mod addition/bump that touches damage
    types, and re-extract vanilla contents on MC bumps.
  - `cozy_rules.mcfunction` on the load tag sets `freeze_damage false`
    (gamerules are snake_case since 26.x; camelCase fails to parse) —
    Homeostatic's hypothermia damage rides entirely on vanilla freezing,
    so cold becomes visual only.
  - Residual risk accepted: hyperthermia/scalding damage can't be zeroed
    without a mixin; thresholds are Nether-extreme, armor now absorbs it.
- **Boot gate:** pending — needs a server + client boot before commit.
