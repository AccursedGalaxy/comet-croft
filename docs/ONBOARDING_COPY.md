# Comet Croft — Player Onboarding Copy (draft v2)

Three artifacts, IMPLEMENTATION-READY on 26.1.x with installed mods
(Drippy Loading Screen, FancyMenu, JEI). Two gates remain before ship:
field-guide pages 3+ (the "first things worth doing" signposts) and the
in-game wrap test on every book page. Purpose: teach the "open
inventory, press R" habit and route players into JEI + the world.
Signpost + handoff only — never re-render recipes.

Voice target: understated, warm, lowercase-literary. Matches pack.toml
and the README Robin wrote.

Canonical instruction — a SEMANTIC rule, not fixed wording. Every surface
(tips, panel, book) must express the same inventory-scoped meaning:
  "Open your inventory, hover an item, and press R for its recipe;
   press U for its uses."
Exact phrasing may vary between surfaces for tone/length, but each variant
MUST keep the inventory scope ("in your inventory / open your inventory")
and MUST NOT imply world-targeting. JEI's R/U act on item stacks inside an
inventory/GUI screen — NOT on blocks under your crosshair in the world.

---

## 1. Drippy loading-screen tips

Drippy shows tips from the list in order (or shuffled) with no per-tip
weighting, so the "load-bearing" keybind tips are physically DUPLICATED
into the list to make them recur ~1-in-3 instead of 1-in-12. This IS the
weighting — it's in the list, not in prose. Final ordered list (15 slots):

1.  Open your inventory and hover an item, then press R to see how it's made. Press U to see what it's for.
2.  Crops grow in their season. Plant with the year, not against it.
3.  A varied diet keeps you fed longer here. Try not to eat the same meal twice in a row.
4.  In your inventory, hover any item and press R for its recipe, U for its uses. Nearly everything explains itself this way.
5.  Right-click a waystone to bind it, then travel between any you've visited.
6.  Winter here means it. Put food by while summer lasts.
7.  Hover an item in your inventory and press R (recipe) or U (uses). That's how you learn this pack.
8.  Hold a spyglass and look up at night. The sky has things worth finding.
9.  On an 8GB laptop? Keep render distance near 8 and shaders off. It runs smooth that way.
10. Open your inventory, hover an item, press R for its recipe. Press U to see what it's for.
11. Sometimes the sky sends something down. It's worth walking out to look.
12. The comet keeps its own calendar. Learn to read it.
13. Stuck on how to make something? Hover it in your inventory and press R.
14. New here? Open the Comet Croft Field Guide in your inventory to get started.
15. R and U are the default JEI keys. If they do nothing, check Options → Controls.

(Slots 1,4,7,10,13 = the keybind habit → 5 of 15 ≈ 33% of the rotation.)

---

## 2. FancyMenu "How to Play" panel

PLACEMENT (implementation requirement, not just copy): a persistent
"How to Play" button on the FancyMenu main menu — bottom button bar,
beside Quit — so it's reachable at any launch, not only the first. It is
the only guaranteed pre-world touchpoint, so the R/U handoff must live
here.

Panel copy:

  How to Play

  Comet Croft is a cozy homestead pack. Farm through the seasons, build
  your croft, and keep an eye on the sky.

  Two keys do most of the work. Open your inventory, hover an item, and:

    R:  how is this made?
    U:  what's it used for?

  That's the whole trick. (R and U are the defaults. If they do nothing,
  check Options → Controls.) Nearly everything else you can just try.

  New here? Open the Comet Croft Field Guide in your starting inventory.
  Map, waystone, and backpack keys are in Options → Controls. On a laptop,
  keep render distance near 8 and shaders off for smooth play.

---

## 3. Field guide — spawn written book

The book's INVENTORY ITEM NAME is "Comet Croft Field Guide" (this exact
string is what the panel and loading tip #14 point at).

BOOK PAGE CONSTRAINT (real, not assumed): a vanilla written-book page is
WIDTH-limited to ~19 characters per line, ~14 lines. Line COUNT was not
the only risk — line WIDTH is. The layout below keeps every line under
~19 chars with vertical margin to spare, but it is a TARGET: the exact
wrap MUST be verified in the in-game book UI before shipping, and pages
re-split if anything clips. Do not treat the layout as pixel-verified.

--- PAGE 1 ---   (title + 8 short lines)

  Comet Croft

  A croft is a small
  homestead. This
  one is yours.

  Farm through real
  seasons. Build it
  up, room by room.
  And watch the sky.

              turn the page →

--- PAGE 2 ---   (9 short lines)

  When you meet an
  item you don't
  know: open your
  inventory, hover
  it, press R.

  That shows how
  it's made. And U
  shows its uses.

              turn the page →

Pages 3-7 are the "first things worth doing" signposts, one per branch of
the advancement tree (homestead / turning year / falling sky / wandering /
close). Same width and verify-in-game rules apply to every page below.

--- PAGE 3 ---   (the homestead)

  The homestead

  Grab a hoe and
  till some soil.
  Plant what you
  find and let it
  grow.

  Then build a
  kitchen and cook
  a real meal.

              turn the page →

--- PAGE 4 ---   (the turning year)

  The turning year

  Crops keep to the
  seasons. Plant in
  spring and summer.
  Put food by for
  winter, when
  little grows.

  The leaves and sky
  tell you where you
  are in the year.

              turn the page →

--- PAGE 5 ---   (the falling sky)

  The falling sky

  Some nights the
  sky sends a comet
  down. You'll hear
  it land.

  Walk out to the
  crater to see
  what it left.

  A spyglass helps
  you watch for
  more.

              turn the page →

--- PAGE 6 ---   (finding your way)

  Finding your way

  Bind a waystone
  and you can jump
  back to it from
  any other.

  Keep a map and a
  backpack on you.
  The world is wide
  and worth the walk.

              turn the page →

--- PAGE 7 ---   (close)

  Last thing

  That's enough to
  start. Everything
  else you can learn
  by pressing R on it.

  Your advancements
  track what to try
  next.

  Build the croft up,
  and keep an eye on
  the sky.

Rule: every page's wrap is confirmed in-game, never assumed from here.
No em dashes in any player-facing string (humanized); arrows are UI, kept.
