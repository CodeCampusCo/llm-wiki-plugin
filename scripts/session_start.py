#!/usr/bin/env python3
"""SessionStart hook: tell the model where the plugin and the wiki live, and what happened last.

Plain stdout is added to the session context. Never fails the session.

Usage: session_start.py <data_dir>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

LOG_ENTRIES = 5


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
    plugin_root = Path(__file__).resolve().parent.parent
    print(context(wikiconf.resolve(data_dir), plugin_root, data_dir))


if __name__ == "__main__":
    try:
        main(sys.argv)
    except Exception:  # context is optional: never break session start
        pass
