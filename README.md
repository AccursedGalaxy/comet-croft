# Comet Croft

A performance- and building-oriented Vanilla++ modpack for Minecraft **26.1.2** on **Fabric**.

> A croft is a small homestead. This one sits under a sky where comets fall.

## Layout

- `pack.toml` — pack metadata (name, versions). **The pack name lives only here** — renaming the pack = edit `name` here + rename this repo dir. Nothing else hardcodes it.
- `mods/*.pw.toml` — one pinned mod per file (exact version + hash). Managed via `packwiz`, never by hand-downloading jars.
- `config/`, `kubejs/`, `resourcepacks/` — shipped as-is inside the exported pack (added as the pack grows).

## Dev workflow

```sh
export PATH="$HOME/go/bin:$PATH"   # packwiz lives here

packwiz modrinth add <slug>        # add a mod
packwiz update --all               # bump all pinned mods
packwiz serve --port 8081     # 8080 is taken by the qwen36 llama.cpp server
packwiz refresh                    # re-hash index after manual file edits
```

Testing: launch the **Comet Croft (dev)** Prism instance while `packwiz serve` runs — its pre-launch hook (packwiz-installer-bootstrap) syncs the instance to the current repo state on every launch.

## UI system (one coherent layer)

- **Resourcify** — in-game browser/updater for resource packs, shaders, datapacks (the "pack explorer").
- **Pack Manager** + **Async Pack Scan** — folder organization + fast scanning on the vanilla pack screen.
- **FancyMenu + Drippy Loading Screen** (same author, one framework) — custom main menu and loading screen. Design them **in-game** with FancyMenu's editor (Mod Menu → FancyMenu, or right-click a menu); layouts land in `config/fancymenu/` and `config/drippyloadingscreen/` → commit them here.
- **YOSBR** — `config/yosbr/options.txt` holds first-run defaults (auto-jump off, no tutorial, 260 fps cap). Applied once, never overrides user changes after.
- **Iris** — `config/iris.properties` ships shaders OFF with Complementary Reimagined preselected (one click to enable).
- **Mod Menu** — `config/modmenu.json`: libraries excluded from mod count.

Config semantics: packwiz-installer syncs shipped configs but leaves user-modified files alone — ship opinionated defaults freely.

## Version bumps

MC now ships quarterly drops (26.1 → 26.2 → …). To bump: edit `[versions]` in `pack.toml`, run `packwiz update --all`, fix stragglers, smoke test.

Currently held on **26.1.2** (not 26.2) because FTB Quests and KubeJS haven't shipped 26.2 builds yet. Re-check every few weeks.

## Watch list

- **ModernFix** — no Fabric build past 1.21.1; add if/when ported.
- **26.2/26.3 port status** for: FTB Quests, KubeJS, YUNG's suite, Exordium.
- **Supplementaries / Amendments / Handcrafted / EMI / Effortless** — stuck on 1.21.1, likely never coming; don't wait on them.

## Export

```sh
packwiz modrinth export            # → .mrpack for Modrinth / Prism import
```
