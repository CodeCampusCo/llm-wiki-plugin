#!/usr/bin/env python3
"""SessionStart hook: tell the model where the plugin and the wiki live, and what happened last.

Plain stdout is added to the session context. Never fails the session.

Usage: session_start.py <data_dir>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

LOG_ENTRIES = 5
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
RULES_FILE = PLUGIN_ROOT / "schema" / "session-rules.md"
PERSONAL_HEADING = "## Session rules"


def _read(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def personal_rules(wiki):
    """Body of the '## Session rules' section of the wiki's CONVENTIONS.md, or ''."""
    text = _read(wiki.root / "CONVENTIONS.md")
    if PERSONAL_HEADING not in text:
        return ""
    body = text.split(PERSONAL_HEADING, 1)[1]
    return body.split("\n## ", 1)[0].strip()


def session_rules(wiki):
    """Plugin working rules with this wiki's search filled in, plus the user's own, or [] when turned off."""
    if not wiki.session_rules:
        return []
    if wiki.qmd_collection:
        search = f"qmd collection `{wiki.qmd_collection}` (MCP query tool, or `qmd query \"<topic>\" -c {wiki.qmd_collection}`)"
    else:
        search = f"read {wiki.pages_dir / 'index.md'}"
    lines = _read(RULES_FILE).replace("{search}", search).strip().splitlines()
    own = personal_rules(wiki)
    if own:
        lines += ["Personal session rules (CONVENTIONS.md):", *own.splitlines()]
    return lines


def recent_log(wiki):
    try:
        lines = (wiki.pages_dir / "log.md").read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    return [line for line in lines if line.startswith("## [")][-LOG_ENTRIES:]


def context(wiki, plugin_root, data_dir):
    if wiki is None:
        return "\n".join([
            "llm-wiki plugin is installed but no wiki is configured. Run /llm-wiki:init.",
            f"Plugin root: {plugin_root}",
            f"Plugin data dir: {data_dir}",
        ])
    lines = [
        "llm-wiki plugin is active.",
        f"Plugin root: {plugin_root}",
        f"Plugin data dir: {data_dir}",
        f'Resolve the wiki config with: python3 "{plugin_root}/scripts/wikiconf.py" show "{data_dir}"',
        f"Schema: {plugin_root}/schema/schema.md",
        f"Scripts: {plugin_root}/scripts",
        f"Wiki root: {wiki.root}",
    ]
    rules = session_rules(wiki)
    if rules:
        lines += ["", *rules]
    log = recent_log(wiki)
    if log:
        lines += ["", f"Recent wiki activity (last {LOG_ENTRIES} entries of wiki/log.md):", *log]
    return "\n".join(lines)


def main(argv):
    import wikiconf

    if len(argv) < 2 or not argv[1]:
        print("llm-wiki: plugin data dir unavailable; update Claude Code")
        return
    data_dir = Path(argv[1])
    print(context(wikiconf.resolve(data_dir), PLUGIN_ROOT, data_dir))


if __name__ == "__main__":
    try:
        main(sys.argv)
    except Exception:  # context is optional: never break session start
        pass
