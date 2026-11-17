#!/usr/bin/env python3
"""PostToolUse hook (Write|Edit): refresh the qmd index after an edit inside the configured wiki's pages.

Only paths under <wiki root>/wiki/ count, so a wiki/ folder of another project never triggers qmd.
Never fails the tool call.

Usage: post_wiki_edit.py <data_dir>   (PostToolUse JSON on stdin)
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def should_reindex(file_path, wiki):
    """True when file_path is inside wiki.pages_dir and the wiki has a qmd collection."""
    if wiki is None or not wiki.qmd_collection or not file_path:
        return False
    try:
        target = Path(file_path).expanduser().resolve()
        return target.is_relative_to(wiki.pages_dir.resolve())
    except (OSError, ValueError):
        return False


def main(argv):
    import wikiconf

    data = json.load(sys.stdin)
    tool_input = data.get("tool_input") if isinstance(data, dict) else None
    file_path = tool_input.get("file_path", "") if isinstance(tool_input, dict) else ""
    wiki = wikiconf.resolve(argv[1] if len(argv) > 1 and argv[1] else None)
    if not should_reindex(file_path, wiki) or not shutil.which("qmd"):
        return
    subprocess.run(["qmd", "update"], timeout=10, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=False)


if __name__ == "__main__":
    try:
        main(sys.argv)
    except Exception:  # an index refresh is optional: never break the tool call
        pass
