#!/usr/bin/env python3
"""Compile guides/*.md into the Comet Croft Field Guide Modonomicon book.

Source layout (repo root):
    guides/
      _book.md                 book front matter (name, tooltip, model, ...)
      <category>/
        _category.md           category front matter (name, icon, sort)
        <entry>.md             one guide entry per file

Entry markdown:
    ---
    name: Welcome to the Croft        (required — shown in the book index)
    icon: minecraft:campfire          (optional — item id; defaults to book icon)
    description: One-line summary.    (optional — shown under the name)
    sort: 1                           (optional — index order; else filename order)
    ---

    # Page Title
    Paragraph text. **Markdown** works: bold, *italic*, lists, links.
    A new `# Heading` starts a new page.

    @recipe farmersdelight:cooking_pot
    Optional caption paragraph directly under a directive.

    @item farmersdelight:stuffed_potato | A proper meal
    Spotlight caption.

Directives (each renders one page):
    @recipe <id> [+ <id2>]     crafting-table recipe(s)
    @smelting / @smoking / @blasting / @campfire / @stonecutting / @smithing
                               same, for the other vanilla recipe types
    @item <id> [| Title]       item spotlight

Output (overwritten on every run — never hand-edit):
    global_packs/required_data/field-guide-book/data/cometcroft/modonomicon/books/field_guide/
    global_packs/required_resources/field-guide-lang/assets/cometcroft/lang/en_us.json

Run from the repo root:  python3 tools/build_guides.py   (then: packwiz refresh)
"""

import json
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "guides"
NAMESPACE = "cometcroft"
BOOK_ID = "field_guide"
DATA_OUT = (
    REPO
    / "global_packs/required_data/field-guide-book/data"
    / NAMESPACE
    / "modonomicon/books"
    / BOOK_ID
)
LANG_OUT = (
    REPO
    / "global_packs/required_resources/field-guide-lang/assets"
    / NAMESPACE
    / "lang/en_us.json"
)

RECIPE_DIRECTIVES = {
    "@recipe": "modonomicon:crafting_recipe",
    "@smelting": "modonomicon:smelting_recipe",
    "@smoking": "modonomicon:smoking_recipe",
    "@blasting": "modonomicon:blasting_recipe",
    "@campfire": "modonomicon:campfire_cooking_recipe",
    "@stonecutting": "modonomicon:stonecutting_recipe",
    "@smithing": "modonomicon:smithing_recipe",
}

RESLOC = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_./-]+$")
PAGE_TEXT_WARN = 700  # chars; longer than this likely overflows a book page

# Recipe-page types only render recipes of the matching vanilla type; a
# mismatched type shows "recipe not found" in game. Values are accepted
# `"type"` prefixes of the recipe JSON.
EXPECTED_RECIPE_TYPE = {
    "modonomicon:crafting_recipe": ("minecraft:crafting",),
    "modonomicon:smelting_recipe": ("minecraft:smelting",),
    "modonomicon:smoking_recipe": ("minecraft:smoking",),
    "modonomicon:blasting_recipe": ("minecraft:blasting",),
    "modonomicon:campfire_cooking_recipe": ("minecraft:campfire_cooking",),
    "modonomicon:stonecutting_recipe": ("minecraft:stonecutting",),
    "modonomicon:smithing_recipe": ("minecraft:smithing",),
}

# Sources for the id index: every installed mod jar plus the vanilla client
# jar. Missing paths downgrade validation to a warning so the build still
# works on machines without the dev instance (e.g. when Kathi writes guides).
MOD_JAR_DIRS = [
    Path.home() / ".local/opt/prismlauncher/instances/CometCroftDev/.minecraft/mods",
]
VANILLA_JARS = [
    Path.home()
    / ".local/opt/prismlauncher/libraries/com/mojang/minecraft/26.1.2/minecraft-26.1.2-client.jar",
]

ITEM_RE = re.compile(r"^assets/([a-z0-9_.-]+)/items/([a-z0-9_./-]+)\.json$")
RECIPE_RE = re.compile(r"^data/([a-z0-9_.-]+)/recipe/([a-z0-9_./-]+)\.json$")


def load_registry_index() -> tuple[set[str], dict[str, str]] | None:
    """Item ids and recipe id -> recipe type, scanned from the installed jars.

    Returns None (validation skipped) when no jars are found.
    """
    import zipfile

    jars = [j for d in MOD_JAR_DIRS if d.is_dir() for j in sorted(d.glob("*.jar"))]
    jars += [j for j in VANILLA_JARS if j.is_file()]
    if not jars:
        return None
    items: set[str] = set()
    recipes: dict[str, str] = {}
    for jar in jars:
        try:
            with zipfile.ZipFile(jar) as z:
                for n in z.namelist():
                    if m := ITEM_RE.match(n):
                        items.add(f"{m.group(1)}:{m.group(2)}")
                    elif m := RECIPE_RE.match(n):
                        rid = f"{m.group(1)}:{m.group(2)}"
                        try:
                            recipes[rid] = json.loads(z.read(n)).get("type", "")
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            pass
        except zipfile.BadZipFile:
            warn(f"skipping unreadable jar: {jar.name}")
    return items, recipes


def validate_ids(entries: dict, categories: dict) -> None:
    index = load_registry_index()
    if index is None:
        warn("id validation SKIPPED — no mod jars found (dev instance not installed?)")
        return
    items, recipes = index

    def check_item(item_id: str, where: str):
        if item_id.endswith(".png"):
            return  # texture icon, not an item
        if item_id not in items:
            fail(f"{where}: item '{item_id}' does not exist in the installed mods")

    for cid, cat in categories.items():
        check_item(cat["icon"]["id"], f"category '{cid}' icon")
    for (cid, eid), entry in entries.items():
        where = f"{cid}/{eid}"
        check_item(entry["icon"]["id"], f"{where} icon")
        for page in entry["pages"]:
            if page["type"] == "modonomicon:spotlight":
                check_item(page["item"], f"{where} {page['id']} (@item)")
            elif page["type"] in EXPECTED_RECIPE_TYPE:
                for key in ("recipe_id_1", "recipe_id_2"):
                    rid = page.get(key)
                    if rid is None:
                        continue
                    if rid not in recipes:
                        fail(f"{where} {page['id']}: recipe '{rid}' does not exist")
                    elif not recipes[rid].startswith(
                        EXPECTED_RECIPE_TYPE[page["type"]]
                    ):
                        fail(
                            f"{where} {page['id']}: recipe '{rid}' is type"
                            f" '{recipes[rid]}', which this page type cannot render —"
                            f" use @item to spotlight the result instead"
                        )


errors: list[str] = []
warnings: list[str] = []
lang: dict[str, str] = {}


def fail(msg: str):
    errors.append(msg)


def warn(msg: str):
    warnings.append(msg)


def parse_front_matter(path: Path) -> tuple[dict, list[str]]:
    """Returns ({key: value}, body_lines)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, lines
    fm = {}
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return fm, lines[i + 1 :]
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip().lower()] = v.strip()
        elif line.strip():
            fail(f"{path}: bad front matter line (need 'key: value'): {line!r}")
    fail(f"{path}: front matter never closed with '---'")
    return fm, []


def check_resloc(value: str, where: str) -> str:
    v = value if ":" in value else f"minecraft:{value}"
    if not RESLOC.match(v):
        fail(f"{where}: '{value}' is not a valid id (expected e.g. minecraft:apple)")
    return v


def lang_key(*parts: str) -> str:
    return ".".join(["book", NAMESPACE, BOOK_ID, *parts])


def put_lang(key: str, text: str) -> str:
    lang[key] = text
    return key


def compile_entry(path: Path, category_id: str, entry_id: str, sort: int) -> dict:
    fm, body = parse_front_matter(path)
    where = str(path.relative_to(REPO))
    if "name" not in fm:
        fail(f"{where}: front matter needs at least 'name:'")
    kbase = [category_id, entry_id]

    pages: list[dict] = []
    cur_text: list[str] = []  # paragraph lines of the open text page
    cur_title: str | None = None
    pending: dict | None = None  # directive page waiting for its caption

    def key_for_page(n: int, field: str) -> str:
        return lang_key(*kbase, f"page{n}", field)

    def flush_text():
        nonlocal cur_text, cur_title
        text = "\n".join(cur_text).strip()
        if not text and cur_title is None:
            return
        n = len(pages)
        page = {"type": "modonomicon:text", "id": f"page{n}", "sort_number": n}
        if cur_title:
            page["title"] = put_lang(key_for_page(n, "title"), cur_title)
        if text:
            if len(text) > PAGE_TEXT_WARN:
                warn(
                    f"{where}: page {n} has {len(text)} chars; may overflow —"
                    f" split it with another '# Heading'"
                )
            page["text"] = put_lang(key_for_page(n, "text"), text)
        pages.append(page)
        cur_text, cur_title = [], None

    def flush_pending(caption: list[str]):
        nonlocal pending
        if pending is None:
            return
        n = len(pages)
        pending["id"] = f"page{n}"
        pending["sort_number"] = n
        title_text = pending.pop("_title_text", None)
        if title_text:
            pending["title"] = put_lang(key_for_page(n, "title"), title_text)
        text = "\n".join(caption).strip()
        if text:
            pending["text"] = put_lang(key_for_page(n, "text"), text)
        pages.append(pending)
        pending = None

    caption: list[str] = []
    for raw in [*body, ""]:
        line = raw.rstrip()
        stripped = line.strip()
        directive = (
            stripped.split(" ", 1)[0].lower() if stripped.startswith("@") else None
        )

        if directive:
            flush_pending(caption)
            caption = []
            flush_text()
            arg = stripped.split(" ", 1)[1].strip() if " " in stripped else ""
            if directive in RECIPE_DIRECTIVES:
                ids = [a.strip() for a in arg.split("+")] if arg else []
                if not ids or not ids[0]:
                    fail(f"{where}: '{directive}' needs a recipe id")
                    continue
                page = {"type": RECIPE_DIRECTIVES[directive]}
                page["recipe_id_1"] = check_resloc(ids[0], where)
                if len(ids) > 1:
                    page["recipe_id_2"] = check_resloc(ids[1], where)
                if len(ids) > 2:
                    fail(f"{where}: '{directive}' takes at most two ids joined by '+'")
                pending = page
            elif directive == "@item":
                parts = [p.strip() for p in arg.split("|", 1)]
                if not parts or not parts[0]:
                    fail(f"{where}: '@item' needs an item id")
                    continue
                page = {
                    "type": "modonomicon:spotlight",
                    "item": check_resloc(parts[0], where),
                }
                if len(parts) > 1 and parts[1]:
                    page["_title_text"] = parts[1]
                pending = page
            else:
                fail(f"{where}: unknown directive '{directive}'")
            continue

        if pending is not None:
            if stripped:
                caption.append(stripped)
                continue
            flush_pending(caption)
            caption = []
            continue

        if stripped.startswith("#"):
            flush_text()
            cur_title = stripped.lstrip("#").strip()
        else:
            cur_text.append(line)

    flush_pending(caption)
    flush_text()

    if not pages:
        fail(f"{where}: entry has no content")

    icon = check_resloc(fm.get("icon", "modonomicon:modonomicon_blue"), where)
    entry = {
        "type": "modonomicon:content",
        "id": f"{NAMESPACE}:{category_id}/{entry_id}",
        "category": f"{NAMESPACE}:{category_id}",
        "name": put_lang(lang_key(*kbase, "name"), fm["name"]) if "name" in fm else "",
        "icon": {"id": icon},
        "x": sort,
        "y": 0,
        "sort_number": sort,
        "pages": pages,
    }
    if "description" in fm:
        entry["description"] = put_lang(
            lang_key(*kbase, "description"), fm["description"]
        )
    return entry


def sort_and_id(path: Path, fm: dict) -> tuple[int | None, str]:
    """Sort number from front matter or a NN- filename prefix; id from filename."""
    stem = path.stem
    m = re.match(r"^(\d+)-(.+)$", stem)
    eid = m.group(2) if m else stem
    if "sort" in fm:
        try:
            return int(fm["sort"]), eid
        except ValueError:
            fail(f"{path}: 'sort:' must be a number")
    return (int(m.group(1)) if m else None), eid


def main() -> int:
    if not SRC.is_dir():
        print(f"error: {SRC} does not exist", file=sys.stderr)
        return 1

    book_fm, _ = (
        parse_front_matter(SRC / "_book.md")
        if (SRC / "_book.md").exists()
        else ({}, [])
    )
    book = {
        "name": put_lang(
            lang_key("name"), book_fm.get("name", "Comet Croft Field Guide")
        ),
        "tooltip": put_lang(lang_key("tooltip"), book_fm.get("tooltip", "")),
        "display_mode": "index",
        # the guide has no unlock conditions, so the "recently unlocked"
        # section is noise — and clicking it traps navigation until the book
        # is closed (observed in playtest 2026-07-21)
        "show_recently_unlocked": False,
        "generate_book_item": True,
        "model": book_fm.get("model", "modonomicon:modonomicon_blue"),
        "creative_tab": "misc",
    }

    categories = {}
    entries = {}
    for cat_dir in sorted(p for p in SRC.iterdir() if p.is_dir()):
        cat_id = cat_dir.name
        if not re.match(r"^[a-z0-9_]+$", cat_id):
            fail(f"{cat_dir}: category folder must be lowercase_with_underscores")
            continue
        cfm, _ = (
            parse_front_matter(cat_dir / "_category.md")
            if (cat_dir / "_category.md").exists()
            else ({}, [])
        )
        csort, _ = sort_and_id(cat_dir, cfm)
        categories[cat_id] = {
            "name": put_lang(
                lang_key(cat_id, "name"),
                cfm.get("name", cat_id.replace("_", " ").title()),
            ),
            "icon": {
                "id": check_resloc(cfm.get("icon", "minecraft:lantern"), str(cat_dir))
            },
            "display_mode": "index",
            "sort_number": csort if csort is not None else len(categories) + 1,
        }

        cat_entries = []
        md_files = sorted(p for p in cat_dir.glob("*.md") if p.name != "_category.md")
        for i, md in enumerate(md_files, start=1):
            fm, _ = parse_front_matter(md)
            esort, eid = sort_and_id(md, fm)
            cat_entries.append((esort if esort is not None else i, eid, md, fm))
        cat_entries.sort(key=lambda t: (t[0], t[1]))
        for n, (_, eid, md, fm) in enumerate(cat_entries, start=1):
            if not re.match(r"^[a-z0-9_]+$", eid):
                fail(f"{md}: entry file name must be lowercase_with_underscores")
                continue
            entries[(cat_id, eid)] = compile_entry(md, cat_id, eid, n)

    if not errors:
        validate_ids(entries, categories)

    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1

    # write output (wipe generated book dir first — it is fully generated)
    if DATA_OUT.exists():
        shutil.rmtree(DATA_OUT)
    (DATA_OUT / "categories").mkdir(parents=True)
    (DATA_OUT / "book.json").write_text(
        json.dumps(book, indent=2, ensure_ascii=False) + "\n"
    )
    for cid, cat in categories.items():
        (DATA_OUT / "categories" / f"{cid}.json").write_text(
            json.dumps(cat, indent=2, ensure_ascii=False) + "\n"
        )
    for (cid, eid), entry in entries.items():
        d = DATA_OUT / "entries" / cid
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{eid}.json").write_text(
            json.dumps(entry, indent=2, ensure_ascii=False) + "\n"
        )
    LANG_OUT.parent.mkdir(parents=True, exist_ok=True)
    LANG_OUT.write_text(
        json.dumps(dict(sorted(lang.items())), indent=2, ensure_ascii=False) + "\n"
    )

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    print(
        f"built book '{NAMESPACE}:{BOOK_ID}': {len(categories)} categories,"
        f" {len(entries)} entries, {len(lang)} lang strings"
    )
    print("next: packwiz refresh  (packwiz lives in ~/go/bin)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
