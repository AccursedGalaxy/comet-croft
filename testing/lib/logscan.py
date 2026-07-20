"""Analyze a Minecraft client/server log slice: errors, warnings, mod count,
startup milestones. Produces a dict; report.py renders it."""

import re


def analyze(text: str) -> dict:
    lines = text.splitlines()
    errors, warns, stacktraces = [], [], 0
    mods_loaded = None
    milestones = {}
    rx_level = re.compile(r"\[[^\]]*\] \[[^\]]*/(ERROR|WARN|FATAL)\]")
    rx_mods = re.compile(r"Loading (\d+) mods")
    for i, ln in enumerate(lines):
        m = rx_level.search(ln)
        if m:
            (errors if m.group(1) in ("ERROR", "FATAL") else warns).append(ln)
        if ln.startswith("\tat ") and i and not lines[i - 1].startswith("\tat "):
            stacktraces += 1
        m = rx_mods.search(ln)
        if m:
            mods_loaded = int(m.group(1))
        for marker, key in [
            ("Backend library: LWJGL version", "lwjgl"),
            ("Sound engine started", "sound_engine"),
            ("Loaded ", None),  # noise guard, ignored
            ("joined the game", "player_joined"),
            ("logged in with entity id", "logged_in"),
            ("Stopping!", "clean_stop"),
        ]:
            if key and marker in ln:
                milestones[key] = ln.strip()

    def dedupe(entries, limit=40):
        seen, out = set(), []
        for e_ in entries:
            body = re.sub(r"^\[[^\]]*\] ", "", e_)[:200]
            if body not in seen:
                seen.add(body)
                out.append(e_)
        return out[:limit]

    return {
        "lines": len(lines),
        "mods_loaded": mods_loaded,
        "error_count": len(errors),
        "warn_count": len(warns),
        "stacktrace_count": stacktraces,
        "unique_errors": dedupe(errors),
        "unique_warns": dedupe(warns),
        "milestones": milestones,
    }


def render_md(name: str, a: dict) -> str:
    out = [f"### Log analysis: {name}", ""]
    out.append(f"- lines: {a['lines']}, mods loaded: {a['mods_loaded']}")
    out.append(
        f"- errors: {a['error_count']}, warnings: {a['warn_count']}, "
        f"stacktraces: {a['stacktrace_count']}"
    )
    for k, v in a["milestones"].items():
        out.append(f"- milestone `{k}`: `{v[:160]}`")
    if a["unique_errors"]:
        out.append(
            f"\n<details><summary>unique errors ({len(a['unique_errors'])})</summary>\n"
        )
        out += [f"```\n" + "\n".join(e[:300] for e in a["unique_errors"]) + "\n```"]
        out.append("</details>")
    if a["unique_warns"]:
        out.append(
            "\n<details><summary>unique warnings "
            f"({len(a['unique_warns'])})</summary>\n"
        )
        out += [f"```\n" + "\n".join(w[:300] for w in a["unique_warns"]) + "\n```"]
        out.append("</details>")
    return "\n".join(out) + "\n"
