# Writing guides for the Field Guide

Everything in this folder becomes the in-game Comet Croft Field Guide, the
blue book every player starts with. You write normal text files, and a small
build script turns them into book pages. You never have to touch the game
files yourself.

## Where things go

Each folder in `guides/` is a chapter of the book. Each `.md` file inside is
one guide. So this:

    guides/
      getting_started/
        10-welcome.md
        20-cooking.md

becomes a "Getting Started" chapter with two guides in it. The number in
front of the file name sets the order and gets stripped from the name, so
`10-welcome.md` is just "welcome" in the book. Any plain text editor works
for these files. On this machine there's also VS Code, which shows a nice
preview.

## What a guide file looks like

```
---
name: The Cooking Pot
icon: farmersdelight:cooking_pot
description: Your first real kitchen upgrade.
---

# A proper kitchen

Some text about cooking. You can make words **bold** or *italic*,
and a blank line starts a new paragraph.

A line starting with # begins a new page, with that text as its title.
Every heading needs at least one line of text under it before the next
@recipe or @item — the build script will remind you if one is bare.

@recipe farmersdelight:cooking_pot
This paragraph appears under the recipe as a caption.

@item farmersdelight:stuffed_potato | A proper meal
And this one appears under the spotlighted item.
```

The bit between the two `---` lines describes the guide itself: `name` is
what shows in the book's table of contents, `description` appears under it,
and `icon` is the item drawn next to it. Only `name` is required.

## Showing recipes and items

`@recipe` plus an item id puts a real, visual crafting recipe on its own
page. Readers see the ingredients laid out like in a crafting table.

`@item` shows one item nice and big, with your text under it. Use it for
things that aren't crafted, like meals from the cooking pot, or anything
you just want to talk about.

To find an item's id in the game: open your inventory, hover the item, and
press F3+H once (that toggles "advanced tooltips"). The id appears at the
bottom of the tooltip, something like `farmersdelight:stuffed_potato`.

There are also `@smelting`, `@smoking`, `@blasting`, `@campfire`,
`@stonecutting` and `@smithing` for recipes made in those blocks.

Recipes from the cooking pot and the cutting board can't be drawn in the
book (the book only knows the vanilla recipe shapes). For those, spotlight
the finished dish with `@item` and tell readers to hover it and press R.
That opens the real recipe screen, cooking pot and all, right from the
book. The build script checks every id you use and refuses to build if an
item doesn't exist or a recipe is the wrong kind for its page, so a typo
can't quietly ship a broken page.

## Seeing your work in the game

Ask Robin (or Claude) to rebuild the book. The short version:

    python3 tools/build_guides.py
    ~/go/bin/packwiz refresh

Then start the game. If you were already in a world, leave to the title
screen and rejoin; the book updates with the world. The build script checks
your files first and tells you exactly what's wrong if something doesn't
work, with the file name and the reason. A guide that's too long for one
page gets a warning too. Split it with another `# Heading` line.

One thing to know: if a recipe id has a typo, the book still opens fine and
that one page just shows a "recipe not found" error in game. So flipping
through your new pages once in the game is worth it.
