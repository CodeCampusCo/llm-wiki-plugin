"""Resolve the configured LLM Wiki location. Stdlib only."""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

SCHEMA_VERSION = 1
MARKER = ".llm-wiki.json"
POINTER = "config.json"


@dataclass(frozen=True)
class Wiki:
    root: Path
    raw_dir: Path
    archive_dir: Path
    qmd_collection: str | None
    schema_version: int

    @property
    def pages_dir(self) -> Path:
        return self.root / "wiki"


def _read_json(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _candidate_dir(data_dir: str | Path | None,
                   environ: Mapping[str, str]) -> Path | None:
    raw = environ.get("LLM_WIKI_DIR")
    if not raw and data_dir:
        pointer = _read_json(Path(data_dir) / POINTER)
        value = pointer.get("wiki_dir") if pointer else None
        raw = value if isinstance(value, str) else None
    if not raw:
        return None
    return Path(raw).expanduser()


def _sub_dir(root: Path, value: object, default: str) -> Path:
    path = Path(value if isinstance(value, str) and value else default).expanduser()
    return path if path.is_absolute() else root / path


def resolve(data_dir: str | Path | None,
            environ: Mapping[str, str] = os.environ) -> Wiki | None:
    root = _candidate_dir(data_dir, environ)
    if root is None:
        return None
    conf = _read_json(root / MARKER)
    if conf is None:
        return None
    collection = conf.get("qmd_collection")
    version = conf.get("schema_version")
    return Wiki(
        root=root,
        raw_dir=_sub_dir(root, conf.get("raw_dir"), "raw"),
        archive_dir=_sub_dir(root, conf.get("archive_dir"), "archive"),
        qmd_collection=collection if isinstance(collection, str) else None,
        schema_version=version if isinstance(version, int) else SCHEMA_VERSION,
    )


def write_pointer(data_dir: Path, wiki_dir: Path) -> None:
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / POINTER).write_text(
        json.dumps({"wiki_dir": str(wiki_dir)}) + "\n", encoding="utf-8")


def _show(data_dir: str | None) -> dict:
    plugin_root = str(Path(__file__).resolve().parent.parent)
    wiki = resolve(data_dir)
    if wiki is None:
        return {"configured": False, "plugin_root": plugin_root}
    return {
        "configured": True,
        "root": str(wiki.root),
        "raw_dir": str(wiki.raw_dir),
        "archive_dir": str(wiki.archive_dir),
        "qmd_collection": wiki.qmd_collection,
        "schema_version": wiki.schema_version,
        "plugin_schema_version": SCHEMA_VERSION,
        "plugin_root": plugin_root,
    }


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] == "show":
        print(json.dumps(_show(argv[2] if len(argv) > 2 else None)))
        return 0
    print("usage: wikiconf.py show <data_dir>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
