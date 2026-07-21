# Comet Croft: cooking mods guide (for Kathi)

Hey Kathi! This is the full rundown of every cooking-related mod in the pack. The idea is for you to play through it, cook a bunch, and tell us what feels good, what's annoying, and what's missing. You're basically the target player here, so your read on it matters more than ours.

## The vibe we're going for

Cozy, not hardcore. The fun should come from unlocking and mastering recipes: filling out cookbooks, discovering crops, leveling up your kitchen. Not from getting punished. Nothing in here should ever kill you from routine neglect (no hunger death spirals, no temperature system, no dying of thirst). If any mechanic feels like a chore or a punishment instead of a reward, that's exactly the kind of thing we want flagged.

One heads-up: everything is running on **default config right now**. Nothing has been tuned yet. So if a number feels off (a drop that's too rare, a mechanic that's too aggressive or too weak), that's probably just a dial we can turn. Note it and we'll adjust.

---

## The mods, by what they do

### The foundation

**Farmer's Delight (Refabricated)** is the base everything else builds on. It adds the cooking pot, cutting board, skillet, stove, and a whole farm-to-table workflow: grow tomatoes, onions, cabbage and rice, chop ingredients on the cutting board, then simmer meals in the cooking pot. Most meals give you a comfort/well-fed buff. This is the core loop. If you only test one thing deeply, test this.

**Delight Lib** is invisible. It's a shared library the other "Delight" addons need to run. Nothing to test directly, just don't be surprised it's in the list.

### Recipe and cuisine expansions (the grind fuel)

These all pile more recipes and ingredients onto the Farmer's Delight base. This is where the "fill the cookbook" grind lives.

**Crop & Kettle** is the biggest single expansion. Over 100 recipes from snacks to feasts, seven new crops to find in the world, extra cooking stations for chopping and mixing, and a wine-aging system where wines develop effects over time. It also has its own discovery cookbook that unlocks as you find ingredients, plus an NPC trader who swaps home-cooked meals for rewards. Lots to explore, so it's worth spending real time on.

**Ube's Delight** is Filipino cuisine. New crops (ube, garlic, ginger, lemongrass) and dishes like lumpia, arroz caldo, halo-halo, leche flan, ube cake, and ube milk tea. It adds a *kalan* (heat source), rolling pins in five tiers, and a baking mat with 27 recipes. Big dessert and drink selection.

**Spanish Delight** is Spanish cuisine: Spanish tortilla, gazpacho, paella-style dishes, and new ingredients that spawn in the world.

**Rustic Delight** adds pancakes in five flavors (each with a buff), coffee for speed and haste, stuffed bell peppers, spring rolls, fried chicken, and calamari (squid now drop it). It also brings bell pepper and cotton crops. It's styled to blend in with vanilla.

**More Delight** is a smaller top-up: extra sandwiches, crispy toast, wooden and stone knives, and a few more ingredients for the base mod.

### The core mechanic: variety matters

**Spice of Fabric** is the mechanic that makes cooking *matter* instead of being decorative. As you eat, repeated foods give you less and less nutrition. It looks at your last ~20 meals, so eating the same steak over and over stops paying off and you get pushed toward variety. This is meant to be the reward loop that ties all the recipe mods together.

Please test this one carefully and tell us how it feels. On default settings it might be too punishing (annoying to keep track of) or too weak (you never notice it). The sweet spot we want: it gently nudges you toward variety and makes discovering new recipes feel worth it, without ever feeling like a food-management job. It also adds carry containers (paper bag, lunch box, picnic basket) that hold multiple food stacks, which help you keep variety on hand.

### Kitchen quality-of-life

**Cooking for Blockheads** is the kitchen-UX mod. You build a connected kitchen (fridge, counters, sink, oven, toaster) and get a Cooking Table with a cookbook that shows every recipe you can make right now from the ingredients in your connected storage, and lets you craft them in one click. This is what makes the huge recipe roster browsable instead of overwhelming. See whether building and using the kitchen feels smooth.

**AppleSkin** is small but important. It shows exact hunger and saturation values on food tooltips and in the HUD, so you can see what each dish is actually worth. It helps a lot when you're judging whether Spice of Fabric is behaving.

**JEI (Just Enough Items)** is recipe lookup. Hover an item and hit the recipe key to see how to make it, or what it makes. Not cooking-specific, but it's how you'll look up all these new recipes. If a recipe seems missing or broken, JEI is the first place to check.

### Farming and ingredient supply

**Farming for Blockheads** adds a Market where you can buy seeds, saplings, and animals. That makes it much easier to start a crop instead of hunting the whole world for every seed. See whether it makes ramping up a farm feel good or too easy.

**Serene Seasons + Seasonal Integration** make crops grow (or not) depending on the season, and the seasons change over time. This adds a light rhythm to farming, since some crops are out of season sometimes. Worth noting how it interacts with the cooking grind: is it a nice texture, or annoying when you can't grow what a recipe needs?

### New this round: drinks, brewing, and food that goes off

Four additions since your first playthrough. The theme is drinks and preservation, and all of it is tuned gentle. Nothing here can realistically kill you.

**Homeostatic** adds a thirst bar and an ambient temperature readout. We set thirst decay to the mod's minimum, so a full bar lasts hours even if you ignore it. The point is that drinks now do something: plain water works, purified water and proper drinks fill you up three times faster. Cold and heat show on the HUD but we defanged the damage, so treat the thermometer as scenery. If thirst ever feels like a chore instead of a nice excuse to brew tea, that's exactly the feedback we need.

**Spoiled** makes food go off, eventually. A meal takes about eight in-game days to spoil, and hovering over it shows a freshness percentage. The fridge from Cooking for Blockheads stops spoilage completely, and cabinets, counters and baskets slow it way down. You now have an actual reason to build that fridge. If you ever feel pressured to eat something before it turns, tell us, because that would mean we tuned it wrong.

**AlcoCraft+** is brewing: beers, wines and spirits with their own gear and small buffs. It pairs nicely with the wine aging in Crop & Kettle. Fair warning that drinking a lot has visual effects.

**Easter's Delight** is a small seasonal addon for Farmer's Delight, mostly egg dishes and springtime treats. A little extra grind fuel.

### Cozy / decorative (food as decoration)

Not gameplay-critical, but a big part of the cozy feel. Worth a look for whether they're fun and worth keeping.

- **Display Delight** lets you place cooked meals on shelves and displays to show them off.
- **3D Placeable Food** makes food sit in the world as actual 3D models instead of flat sprites.
- **Storage Delight** adds food-themed storage blocks.
- **Crate Delight** adds crates for storing crops and produce in bulk.
- **Farmhouse Decorations** adds farm and kitchen decoration blocks for building out a cozy homestead.

---

## Suggested testing path

A rough order that builds up naturally. Feel free to wander off it.

1. **Start a Farmer's Delight kitchen.** Grow a couple crops, build a cooking pot and cutting board, make a few basic meals. Does the core loop feel good?
2. **Build a Cooking for Blockheads kitchen.** Connect a fridge, counters and oven, then open the cookbook. Is it intuitive? Does it make the recipe list feel manageable?
3. **Chase one cuisine.** Pick Ube's, Spanish, or Crop & Kettle and try to cook through its recipe list. Is discovery fun? Do you hit dead-ends (a missing ingredient, an unclear recipe)?
4. **Live with Spice of Fabric for a few in-game days.** Eat repetitively on purpose, then eat varied. Do you actually feel the difference? Is it motivating or annoying?
5. **Try the extras.** The Farming for Blockheads market, the wine-aging in Crop & Kettle, decorating with Display Delight and placeable food.
6. **Notice the seasons.** Over a longer session, does seasonal crop growth add nice rhythm or get in the way?
7. **Build the fridge and stock it.** Cook a batch of meals, keep half in the fridge and half in a chest, and check the freshness numbers a few days later. Does spoilage read as a fun reason to preserve, or as homework?
8. **Keep a drink on you.** Live with the thirst bar for a session. Brew something from AlcoCraft or make tea and juices where you find them. Does drinking feel like part of the cozy loop or like a second hunger bar?

---

## What we'd love feedback on

For each mod, or overall, anything along these lines helps:

- **Fun factor.** Is cooking this something you'd actually want to grind, or does it get old?
- **Friction.** Anything tedious, confusing, or that made you go "ugh"? Missing recipes, unclear ingredients, clunky UI, hard-to-find crops.
- **Balance.** Anything too easy and pointless, or too grindy and punishing? Especially Spice of Fabric: too harsh, too weak, or about right?
- **Overlap.** Do any mods feel redundant with each other, or do they layer nicely?
- **Missing.** Any cuisine, dish, mechanic, or convenience you kept wishing was there?
- **Keep or cut.** For the decorative ones especially, are they worth having?

No need to be formal. Bullet points, voice notes, "this thing sucked," whatever works. Rough reactions are more useful than polished ones.

---

## Quick reference: versions

Everything is Fabric on Minecraft 26.1.2.

| Mod | Version | Role |
|---|---|---|
| Farmer's Delight Refabricated | 3.6.7 | Core cooking base |
| Delight Lib | 26.05.18 | Library (invisible) |
| Crop & Kettle | 1.3.11 | Big recipe/crop expansion + wine |
| Ube's Delight | 0.4.14 | Filipino cuisine |
| Spanish Delight | 1.0.10 | Spanish cuisine |
| Rustic Delight | 1.6.0 | Pancakes, coffee, fried foods |
| More Delight | 26.05.26 | Sandwiches, knives, extras |
| Spice of Fabric | 1.6.3-beta.2 | Variety-reward mechanic |
| Cooking for Blockheads | 26.1.2.3 | Kitchen + cookbook UX |
| Farming for Blockheads | 26.1.2.2 | Seed/animal market |
| AlcoCraft+ | 2.1.3 | Brewing: beers, wines, spirits |
| Homeostatic | 2.13.0.2 | Thirst (tuned very gentle) |
| Spoiled | 12.1.0 | Food spoilage (8-day timers, fridge pauses it) |
| Easter's Delight | 1.2.0 | Seasonal egg dishes |
| AppleSkin | 3.0.10 | Food value HUD |
| Display Delight | 1.8.3 | Food display blocks |
| 3D Placeable Food | 3.0.2 | 3D food models |
| Storage Delight | 26.07.01 | Food storage blocks |
| Crate Delight | 26.07.01 | Crop crates |
| Farmhouse Decorations | 26.4.0 | Decoration blocks |

Thanks for testing!
