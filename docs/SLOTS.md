# Comet Croft — Pillar Slots

Phase 1 output: one slot per THEME.md pillar, filled with the best candidate
that *actually supports MC 26.1.x on Fabric* (verified against the Modrinth
API, 2026-07-20). Gaps that no current mod covers are marked **(custom mod)**.
The performance/QoL baseline already in the pack sits underneath all of this
and is not re-litigated here.

Status legend: ✅ filled · 🟡 filled with gaps · 🔴 gap (custom mod candidate)

## Slot 1 — Sky renderer 🟡

**Pick: Spyglass Astronomy** (`spyglass-astronomy`, 2.4M dl) — improved
stars, planets, and interactive constellations you chart yourself through a
spyglass. On-version, Fabric-native, and it hands us the "star-reading as
progression" beat of the theme almost for free.

Supporting: **Skyboxify** (`skyboxify`, 10.1M dl) — OptiFine-format skybox
engine, on-version. Not content by itself, but it means any custom sky art
we want (auroras, a comet backdrop for event nights) can ship as a resource
pack without writing render code.
Optional: **Celestia: Shooting Stars** (`celestia-sky`) — server-synced
meteor showers in the sky; tiny mod (1.8k dl), evaluate in playtest.

Gaps: no comet rendering, no eclipses, no aurora exists anywhere on 26.1.x
(AstroCraft, the flagship astronomy mod with eclipses, is stuck at 1.21.4).
→ folds into the custom mod below.

## Slot 2 — Seasons ✅

**Pick: Serene Seasons** (`serene-seasons`, 5.9M dl) — now native
multiloader with Fabric support on 26.1.1/26.1.2. Foliage color shifts,
crop fertility by season, snow in winter, configurable season length.
Everything the theme's "time is the engine" section asks of the ground.

Notes: Fabric Seasons (8.7M dl) and its whole compat family are dead at
1.21.1 — Serene Seasons is the only real choice, which is fine because it's
the better mod. Verify its crop-fertility config plays well with Farmer's
Delight Refabricated crops (compat addon `seasonal-lets-do` is version-stuck;
we may need fertility datapack entries for modded crops).

## Slot 3 — Ground depth (farming / cooking / animals) 🟡

**Pick: Farmer's Delight Refabricated** (`farmers-delight-refabricated`,
13.2M dl) plus a curated addon ring, all confirmed on-version:
**More Delight**, **Rustic Delight** (cotton, coffee, pancakes — very
homestead), **Ube's Delight**, **Crate Delight** + **Storage Delight**
(pantry/kitchen storage, bridges into Slot 4), **3D Placeable Food** /
**Display Delight** (food on tables — cozy screenshots).
Considering: **Cooking for Blockheads** (kitchen-as-a-place; slightly
gadgety, litmus-test it), **Farming for Blockheads** (seed market).

Gaps: animal husbandry depth. Naturalist and the Let's Do series (Meadow
etc.) are all stuck ≤1.21.1; no husbandry-mechanics mod exists on 26.1.x.
Partial cover: **Cosy Critters & Creepy Crawlies** (ambient birds/bugs,
on-version). Verdict: accept the gap for v1 — vanilla breeding + FD is
enough ground loop; revisit when ports land. Not worth custom work.

## Slot 4 — Cozy build / decor layer ✅

**Pick: the Macaw's suite** — Furniture, Windows, Roofs, Fences & Walls,
Doors, Trapdoors, Stairs, Bridges, Paths & Pavings, Lights & Lamps,
Paintings — all confirmed 26.1.x Fabric, all vanilla-styled cottage
material. Start with Furniture + Windows + Roofs + Fences + Lights and add
the rest by build-need rather than all at once.

Supporting: **Rechiseled** (6.4M dl, block variants — the alive Chipped
alternative), **Additional Lanterns** + **Swinging Lanterns** +
**Lanterns Belong on Walls** (lantern-glow is literally the theme palette),
**Farmhouse Decorations** (small but dead-center theme).

Notes: the classic cozy stack — Supplementaries, Handcrafted, Chipped,
Another Furniture, Adorn — is entirely stuck at 1.21.x. The Macaw's +
Rechiseled combination covers the need; no gap worth custom work.

## Slot 5 — Sky touches the ground 🟡→🔴

**Picks (off-the-shelf part):**
- **Oh My, Meteors!** (`ohmymeteors`, 30k dl) — falling, mineable,
  configurable meteors; actively maintained, on-version. Covers THEME's
  "meteor falls" beat. Tune rarity DOWN hard.
- **Lunar** (`lunar`, 591k dl) — lunar events, the modern successor to
  Enhanced Celestials (which is dead at 1.21.1). Supports 26.1 exactly
  (not yet .1/.2 — watch it; 26.1 is inside our acceptable range).
  Covers blood moons / harvest moons as one-night mood shifts.
  Fallback if Lunar lags: KS Blood Moon or Magic Moon (both smaller).

**Gap (custom mod): the passing comet.** Nothing on Modrinth does
"a comet dominates the sky for a stretch of nights, years apart, and the
world is subtly charged while it hangs there." This is the pack's
signature mechanic and its name. → see Custom mod section.

## Slot 6 — Ambience ✅

**Picks, all confirmed on-version Fabric:**
- **AmbientSounds** (32.9M dl, + CreativeCore dep) — biome nature sounds
- **Sound Physics Remastered** (45.9M dl) — reverb/attenuation
- **Presence Footsteps** (33.3M dl) — per-material footsteps
- **Falling Leaves** (23.9M dl) — the seasonal-drift visual
- **Cool Rain** (6.1M dl) — rain ambience accent

Gaps (minor, accepted): Particular/Effective-style firefly and waterfall
visuals are stuck ≤1.21.4; Reactive Music (dynamic soundtrack) is one
version behind at 1.21.11 — watch for its 26.1 port, it would suit event
nights well.

## Custom mod: "Comet" (working name) 🔴

The one bespoke piece, scoped to exactly what nothing else provides:

1. **The comet itself** — a sky object rendered for a configurable run of
   nights, recurring on a multi-year calendar. (Rendering fallback: a
   Skyboxify sky swap toggled by the mod, if custom rendering is a pain.)
2. **The charged world** — while the comet hangs: subtle crop growth boost
   and shimmer particles, rare wandering-trader oddities, unusual mob
   moods. Small hooks, no new dimensions of gameplay.
3. **The almanac hook** — a way to discover/predict the return (ties into
   Spyglass Astronomy's charting fantasy; could be as simple as a written
   book item the mod fills in).

Explicitly out of scope for it: meteors (Oh My, Meteors!), lunar events
(Lunar), sky rendering in general (Spyglass/Skyboxify). Keep it a small,
single-purpose Fabric mod.

Ship ladder per THEME: v1 can ship without it (slots 1–6 above already
deliver a coherent pack); v1.x adds the comet visually; the charged-world
mechanics follow. Aurora/eclipse ideas fold into this mod's backlog rather
than getting their own.

## Slot 7 — Terrain & biomes ✅ (installed Tier 6; Terralith decided IN)

(Phase 2 research, verified against the Modrinth API 2026-07-20. Guiding
constraint from docs/PERFORMANCE.md: datapack-technology worldgen only —
all cost at chunk-gen time, zero runtime tax, which is what keeps the
laptop/MacBook target viable. C2ME parallelizes exactly this cost.)

**Core pick: Tectonic (mod) + Geophilic + Continents** — all confirmed on
26.1/26.1.1/26.1.2 Fabric, all Stardust-style datapack tech:
- **Tectonic** (`tectonic`, 14.6M dl) — terrain *shaping* only: huge
  mountains, deep valleys, dramatic skylines behind the farmhouse, while
  every biome stays a vanilla biome. Config can tame the scale. This alone
  delivers the theme's "enormous sky over a small croft" screenshots.
- **Geophilic** (`geophilic`, 9.0M dl) — subtle polish of existing vanilla
  biomes; the Vanilla++ archetype, near-zero cost.
- **Continents** (`continents`, 1.1M dl) — landmass/ocean grouping with
  real coastlines; invisible to a vanilla player.

This trio adds **zero new biome IDs**, so it is perfectly transparent to
Serene Seasons — no compat work at all.

**DECIDED (A/B 2026-07-20): Terralith is IN.** (`terralith` 2.6.2 +
`seasonal-integration` 1.6.1 mod jar for the Serene Seasons biome tags —
remove both together if this ever reverses.) A/B on seed `cometcroft`
against the Tectonic-only control; Robin judged the Terralith world
better terrain. Terratonic merge verified live by headless probe
(terralith biomes at Tectonic elevations). Full stack is now
Tectonic + Terralith + Continents + Geophilic. Vanilla blocks only,
but ~100 new biome names stretches "vanilla player recognizes everything",
it's the heaviest common gen-time datapack, and it needs the
`seasonal-integration` datapack (on-version) for correct Serene Seasons
snow/tropical behavior. Verdict: generate two test worlds (with/without)
and judge by screenshots; the pack is coherent without it.

Rejected: Biomes O' Plenty / Terrestria / Traverse (fantasy biome identity
breaks the Vanilla++ promise), Wilder Wild (fine mod, but runtime
entities/particles/sounds make it a content mod — wrong cost class for
laptops), WWOO (credible but 26.1.2-only and drifts "realistic" rather
than "Minecraft"), Regions Unexplored / Terra (off-version anyway).
Underground (Lithosphere, YUNG's Cave Biomes) deferred — not where this
pack's identity lives; revisit on demand.

## Slot 8 — Structures ✅ (installed Tier 6; accents deferred to playtest)

Same restraint rule as everywhere: the world should feel *gently
lived-in*, never like a loot-crawl. Strategy: replace vanilla structures
rather than pile new ones on, keep additions sparse, and ship the tooling
to thin density further.

**Villages:**
- **Towns & Towers** (`towns-and-towers`, 15.0M dl, on-version) —
  biome-themed vanilla-style villages; varies vanilla spawns rather than
  adding density. The on-version village pick (CTOV is stuck at 1.21.11).
- **Moog's Missing Villages** (`mmv-moogs-missing-villages`, 462k dl) —
  surgical: just the missing jungle + swamp villages, vanilla style.
- **Improved Village Placement** (`improved-village-placement`, 1.9M dl) —
  flatter village sites; quiet QoL that matters more under Tectonic
  terrain.

**Wilderness accents (sparse, loot-light):**
- **Structory** + **Structory: Towers** (`structory`/`structory-towers`,
  ~7M dl each) — atmospheric small ruins, cottages, lone towers; the most
  on-brief structure set that exists.
- **Explorify** (`explorify`, 7.9M dl) — explicitly minimal vanilla-
  friendly additions.

**Vanilla glow-up (replace, don't add):** the YUNG suite on 26.1.2 —
Better Mineshafts, Strongholds, Ocean Monuments, Desert Temples, Jungle
Temples, Witch Huts, Extras — plus **Hopo Better Ruined Portals**. All
restrained redesigns of things vanilla already spawns. (No YUNG's
"Better Villages" exists — the suite has no village mod.)

**Restraint & perf tooling:**
- **Structurify** (`structurify`, 2.5M dl) — per-structure spacing/
  separation config; our knob to globally spread structures 1.5–2x if
  playtests feel dense, and the laptop preset's thinning lever.
- **Structure Layout Optimizer** (`structure-layout-optimizer`, 5.8M dl) —
  jigsaw gen perf win, pairs with C2ME.

Considering (accents, decide in playtest): Dungeons & Taverns *splinter
packs only* (pillager-outpost + swamp-hut overhauls — tavern flavor
without the dungeon half), Moog's Voyager Structures (130+ cozy
vanilla-block structures but needs immediate re-raring via its config
pack), WITS (structure-name HUD, trivial).

Rejected: full Dungeons & Taverns (half dungeon content), Legacies &
Legends / ATI Structures (loot-centric), Adorabuild (overlaps Structory,
denser), Guard Villagers (Fabric dead at 1.21.1), When Dungeons Arise
(off-version and the canonical heavy offender anyway). Explorer's Compass
skipped: locating structures by gadget cuts against wandering-under-the-
sky; revisit if playtesters get lost.

Gap note: searched for astronomy/observatory-themed structures
(abandoned observatories, stargazing sites) — nothing exists on 26.1.x.
That's a natural candidate for the custom Comet mod's backlog (a rare
ruined-observatory structure would tie Slots 5/7/8 together).

## Version-watch list

Mods that would upgrade a slot the moment they port to 26.1.x:
Reactive Music (1.21.11) · Supplementaries (1.21.1) · Handcrafted (1.21.1) ·
Naturalist (1.21.1) · Seasonal Let's Do compat (1.21.11) · Moonstone
Meteorites (1.21.11, cozy vanilla-block meteorite craters — the single most
on-theme worldgen mod found; watch closely) · Celestria (1.21.1, shooting
stars + insomnia events) · CTOV (1.21.11, would contend for the village
slot) · Repurposed Structures (has 26.1 and 26.2 builds but skips
26.1.1/26.1.2 — a 26.1.2 jar may just be unpublished; its Farmer's Delight
village compat pack IS on-version) · Better Villages (1.21.11) ·
Additional Structures (1.21.11) · Philip's Ruins (1.21.11) · Moss Ruins /
Campsite Structures (1.21.x, small cozy accents).
