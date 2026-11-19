"""Create or attach an LLM Wiki content repo. Stdlib only."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wikiconf  # noqa: E402

SKELETON = Path(__file__).resolve().parent.parent / "skeleton"
PLACEHOLDER = "## [YYYY-MM-DD] bootstrap"


class InitError(Exception):
    pass


def _path(value: str) -> Path:
    return Path(value).expanduser().absolute()


def _stored(wiki: Path, target: Path) -> str:
    """Path as committed in .llm-wiki.json: relative to the wiki, else ~/... under $HOME, else absolute."""
    try:
        return str(target.relative_to(wiki))
    except ValueError:
        pass
    try:
        return "~/" + target.relative_to(Path.home().absolute()).as_posix()
    except ValueError:
        return str(target)


def _check_empty(wiki: Path) -> None:
    if wiki.exists() and (not wiki.is_dir() or any(wiki.iterdir())):
        raise InitError(f"{wiki} exists and is not empty; nothing was written")


def _fill_log(wiki: Path) -> None:
    log = wiki / "wiki" / "log.md"
    text = log.read_text(encoding="utf-8")
    today = f"## [{date.today().isoformat()}] bootstrap"
    log.write_text(text.replace(PLACEHOLDER, today), encoding="utf-8")


def _write_conf(wiki: Path, **changes) -> dict:
    marker = wiki / wikiconf.MARKER
    conf = json.loads(marker.read_text(encoding="utf-8"))
    conf.update(changes)
    marker.write_text(json.dumps(conf, indent=2) + "\n", encoding="utf-8")
    return conf


def _git_init(wiki: Path) -> None:
    try:
        subprocess.run(["git", "init", "-b", "main"], cwd=wiki, check=True,
                       capture_output=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise InitError(f"git init failed: {exc}") from exc


def _precheck_new(wiki: Path, raw: Path) -> None:
    _check_empty(wiki)
    if shutil.which("git") is None:
        raise InitError("git is not installed or not on PATH; nothing was written")
    if raw.exists() and not raw.is_dir():
        raise InitError(f"{raw} exists and is not a directory; nothing was written")


def _build(args, wiki: Path, raw: Path) -> None:
    shutil.copytree(SKELETON, wiki, dirs_exist_ok=True)
    (wiki / "raw-README.md").unlink()
    _fill_log(wiki)
    changes = {"raw_dir": _stored(wiki, raw)}
    if args.archive_dir:
        changes["archive_dir"] = _stored(wiki, _path(args.archive_dir))
    if args.qmd_collection:
        changes["qmd_collection"] = args.qmd_collection
    _write_conf(wiki, **changes)
    raw.mkdir(parents=True, exist_ok=True)
    readme = raw / "README.md"
    if not readme.exists():
        shutil.copyfile(SKELETON / "raw-README.md", readme)
    _git_init(wiki)


def cmd_new(args, data_dir: Path) -> dict:
    wiki, raw = _path(args.wiki_dir), _path(args.raw_dir)
    _precheck_new(wiki, raw)
    existed = wiki.exists()
    try:
        _build(args, wiki, raw)
        wikiconf.write_pointer(data_dir, wiki)
    except (OSError, InitError) as exc:
        if wiki.exists():
            shutil.rmtree(wiki, ignore_errors=True)
            if existed:
                wiki.mkdir(exist_ok=True)
        if isinstance(exc, InitError):
            raise
        raise InitError(f"could not create the wiki: {exc}") from exc
    return {"wiki_dir": str(wiki), "raw_dir": str(raw),
            "qmd_collection": args.qmd_collection}


def cmd_existing(args, data_dir: Path) -> dict:
    wiki = _path(args.wiki_dir)
    marker = wiki / wikiconf.MARKER
    try:
        conf = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise InitError(f"{marker} is missing or not valid JSON") from exc
    if not isinstance(conf, dict):
        raise InitError(f"{marker} must hold a JSON object")
    if args.qmd_collection:
        conf = _write_conf(wiki, qmd_collection=args.qmd_collection)
    wikiconf.write_pointer(data_dir, wiki)
    return {"wiki_dir": str(wiki), "qmd_collection": conf.get("qmd_collection")}


SNIPPET = """## LLM Wiki ({wiki})

My wiki lives at {wiki}.
"""


def cmd_snippet(args, data_dir: Path) -> str:
    wiki = wikiconf.resolve(data_dir, {})
    if wiki is None:
        raise InitError("no wiki configured; run init first")
    return SNIPPET.format(wiki=wiki.root)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="init_wiki.py")
    p.add_argument("data_dir")
    sub = p.add_subparsers(dest="cmd", required=True)
    new = sub.add_parser("new")
    new.add_argument("--wiki-dir", required=True)
    new.add_argument("--raw-dir", required=True)
    new.add_argument("--archive-dir")
    new.add_argument("--qmd-collection")
    ex = sub.add_parser("existing")
    ex.add_argument("--wiki-dir", required=True)
    ex.add_argument("--qmd-collection")
    sub.add_parser("snippet")
    return p


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv[1:])
    if not args.data_dir.strip():
        print("error: plugin data dir is empty or missing; update Claude Code", file=sys.stderr)
        return 2
    data_dir = _path(args.data_dir)
    handlers = {"new": cmd_new, "existing": cmd_existing, "snippet": cmd_snippet}
    try:
        out = handlers[args.cmd](args, data_dir)
    except InitError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(out if isinstance(out, str) else json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
