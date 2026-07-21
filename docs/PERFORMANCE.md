# Comet Croft — Performance & Laptop Viability

Research pass 2026-07-20, focused on what adding worldgen/structure mods
costs and how the pack stays playable on laptops (iGPU Windows/Linux
machines and MacBooks, including 8GB machines). Perf-mod baseline already
in the pack: Sodium (+Extra), Lithium, C2ME, FerriteCore, Krypton,
ImmediatelyFast, EntityCulling, MoreCulling, BadOptimizations, Dynamic
FPS, Async Pack Scan, Iris.

Caveat: 26.1.x-specific perf evidence is thin; interaction findings below
extrapolate from well-documented 1.20–1.21-era behavior plus current
changelogs.

## The one rule that keeps us laptop-viable

**Datapack-technology worldgen only in the default experience.**
Stardust-style packs (Tectonic, Geophilic, Continents, Terralith) are
datapacks in a jar: vanilla blocks, no runtime hooks. All their cost is
paid once, at chunk-generation time, and C2ME parallelizes exactly that.
Once chunks exist, standing FPS/memory is flat. Code mods with new
entities/particles/tickers (e.g. Wilder Wild) pay forever — wrong class
for this pack.

Corollaries:
1. Everything we add must have a real 26.1.2 Fabric build (verified, not
   assumed).
2. No TerraBlender-based biome mods (historical C2ME conflict cluster).
3. Structure mods must expose spacing/separation config (Structurify
   covers this pack-wide) so the laptop preset can thin them.
4. The pack must look good with shaders OFF and Distant Horizons OFF —
   those two are what break 8GB / thermally-limited machines.

## Known interactions

- **C2ME on 26.1.2 is alpha-channel** (0.4.0-alpha line, weekly
  releases). Keep it, pin a known-good build ≥1 week old, and never add
  the c2me-opencl module — its own page documents crashes with complex
  worldgen datapacks like Terralith (and it would fight the iGPU for the
  same silicon).
- C2ME is a net positive with Terralith/Tectonic — users have *fixed*
  Terralith TPS collapse by installing it. On ~4-core thermally limited
  chips, cap C2ME worldgen parallelism to (physical cores − 2, min 2) so
  gen threads don't starve the render thread.
- Tectonic v3 had documented slow-gen complaints (GH #423, fixed
  Oct 2025; #395 open on Forge only). Benchmark gen in-pack once before
  committing; pre-gen with `chunky` (on-version) is the server-side answer.
- **Distant Horizons** (3.2.0-b for 26.1.2 exists): CPU-hungry during LOD
  builds (sustained all-core — exactly what throttles MacBooks), wants
  +2–4GB RAM, and LODs render untextured under Iris shaders on 3.2.0.
  Verdict: **optional, default OFF**. Making DH default-on is the one
  decision that would exclude 8GB machines.
- If DH is enabled, strip `-XX:+DisableExplicitGC` from any copy-pasted
  JVM flags — DH 3.2.0 explicitly warns it causes memory leaks.

## Laptop preset

The in-game half of this preset ships as pack defaults via YOSBR
(`config/yosbr/options.txt`): render distance 10, sim distance 8, fast
leaves/clouds, entity shadows off, biome blend 2, smooth lighting on.
YOSBR only seeds fresh installs — existing instances keep their settings
and need the values applied by hand. The JVM half can't ship in the pack;
it lives in each player's launcher instance settings.

In-game:
- Render distance 8 (10 on 16GB), simulation distance 6–8 (sim distance
  is the tick-cost knob).
- Sodium: Graphics Fast, smooth lighting on, clouds/weather Fast,
  entity shadows OFF, biome blend 1–2. Fullscreen beats windowed on iGPU.
- Shaders off (Iris ships, packs optional; on macOS flag shaders
  "unsupported" — Iris has a track record of macOS-specific crashes and
  macOS is capped at OpenGL 4.1).
- Dynamic FPS already handles background/battery throttling.

JVM:
- 8GB machine (iGPU steals 1–2GB of it): `-Xms3G -Xmx3G`. Never >4G —
  a 6G heap on 8GB total thrashes.
- 16GB machine: `-Xmx6G` (8G only if DH is enabled).
- Flags: brucethemoose G1GC baseline:
  `-XX:+UseG1GC -XX:MaxGCPauseMillis=37 -XX:+PerfDisableSharedMem
  -XX:G1HeapRegionSize=16M -XX:G1NewSizePercent=23 -XX:G1ReservePercent=20
  -XX:SurvivorRatio=32 -XX:G1MixedGCCountTarget=3 -XX:G1HeapWastePercent=20
  -XX:InitiatingHeapOccupancyPercent=10 -XX:G1RSetUpdatingPauseTimePercent=0
  -XX:MaxTenuringThreshold=1 -XX:+ParallelRefProcEnabled`
- ZGC: wrong trade on 8GB (needs extra RAM, loses compressed oops);
  only worth testing on 16GB machines.
- Apple Silicon: ARM64-native JDK is mandatory (Rosetta Java roughly
  halves performance). Modern launchers do this; document the check.

Memory floor: a ~90-mod Fabric+Sodium pack with datapack worldgen runs at
3GB allocated, 4GB comfortable (FerriteCore does a lot of lifting). 8GB
machines stay viable as long as DH and shaders stay off.

## Runtime-cost ambience: Sound Physics Remastered

The one ambience mod with real per-event runtime cost: it raytraces every
sound for occlusion/reverb on the client. Fine on most machines, but it is
the first thing to disable on a struggling laptop (Mod Menu → Sound
Physics Remastered → Enabled: off — no restart needed), ahead of touching
render distance. AmbientSounds/Presence Footsteps/Falling Leaves/Cool Rain
are near-free by comparison and not worth disabling.

## Sources

brucethemoose Minecraft-Performance-Flags-Benchmarks · Stardust Labs
wiki/FAQ · C2ME GH issues #134/#314, c2me-ocl page · Tectonic GH
#423/#395 · DH 3.2.0 changelog + CurseForge DH FAQ · Enigmatica memory
guide · Iris GH #2555/#2572/#2623 (macOS) · Admincraft threads on
Terralith gen cost.
