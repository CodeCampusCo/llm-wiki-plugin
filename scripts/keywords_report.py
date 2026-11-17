#!/usr/bin/env python3
"""Report on wiki `keywords` against recent Claude Code prompts.

never_matched: page keywords that matched none of the recent prompts.
frequent_unmatched: common words in prompts that no page lists as a keyword.

Usage: keywords_report.py <data_dir> [--days N]   (report only; reads ~/.claude/projects/*/*.jsonl)
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import wiki_hint  # noqa: E402
import wikiconf  # noqa: E402

MIN_PROMPTS, TOP = 5, 20
TOKEN = re.compile(r"[a-z][a-z0-9_\-]{2,}|[฀-๿]+")
STOPWORDS = frozenset("""
the and for are but not you your with this that these those from have has had was were will would could should
can cannot just now then than them they their there here what when where which who whom why how into onto out off
over under again also any all each few more most other some such only own same too very about after before
because been being both does did doing done get got going let make made need one two use used using want yes
please thanks thank like see look check run add fix new old its our his her him she let's don't it's i'm
""".split())


def _prompt_text(message: object) -> str:
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, str):
        return "" if content.lstrip().startswith("<") else content
    if isinstance(content, list):
        return "\n".join(b["text"] for b in content
                         if isinstance(b, dict) and b.get("type") == "text"
                         and isinstance(b.get("text"), str)
                         and not b["text"].lstrip().startswith("<"))
    return ""


def prompts(transcripts: Iterable[Path]) -> list[str]:
    out = []
    for path in transcripts:
        try:
            lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            if isinstance(obj, dict) and obj.get("type") == "user" \
                    and not obj.get("isMeta") and not obj.get("isSidechain"):
                text = _prompt_text(obj.get("message")).strip()
                if text:
                    out.append(text)
    return out


def recent_transcripts(days: int, root: Path | None = None) -> list[Path]:
    root = root or Path.home() / ".claude" / "projects"
    cutoff = time.time() - days * 86400
    found = []
    for path in root.glob("*/*.jsonl"):
        try:
            if path.stat().st_mtime >= cutoff:
                found.append(path)
        except OSError:
            continue
    return sorted(found)


def report(wiki: wikiconf.Wiki, transcripts: Iterable[Path], days: int = 30) -> dict:
    texts = [p.lower() for p in prompts(transcripts)]
    pages = wiki_hint.pages(wiki.pages_dir)
    never = [(rel, w) for rel, _, words in pages for w in words
             if not any(wiki_hint.matches(w, t) for t in texts)]
    known = {tok for _, _, words in pages for w in words for tok in TOKEN.findall(w.lower())}
    counts: Counter = Counter()
    for text in texts:
        counts.update(set(TOKEN.findall(text)))
    frequent = [(w, n) for w, n in counts.most_common()
                if n >= MIN_PROMPTS and w not in STOPWORDS and w not in known][:TOP]
    return {"never_matched": never, "frequent_unmatched": frequent,
            "prompts": len(texts), "days": days}


def render(result: dict) -> str:
    lines = [f"# Keywords report ({result['prompts']} prompts, last {result['days']} days)", "",
             "## Keywords that never matched", ""]
    lines += [f"- `{page}`: {word}" for page, word in result["never_matched"]] or ["- none"]
    lines += ["", "## Frequent words in no page's keywords", ""]
    lines += [f"- {word} ({n})" for word, n in result["frequent_unmatched"]] or ["- none"]
    return "\n".join(lines) + "\n"


def _parse_days(args: list[str]) -> int:
    if "--days" not in args:
        return 30
    i = args.index("--days")
    days = int(args[i + 1])  # IndexError or ValueError on a missing or non-numeric value
    if days < 1:
        raise ValueError(days)
    del args[i:i + 2]
    return days


def main(argv: list[str]) -> int:
    args = argv[1:]
    try:
        days = _parse_days(args)
    except (ValueError, IndexError):
        print("usage: keywords_report.py <data_dir> [--days N]   (N is a positive integer)")
        return 0
    try:
        wiki = wikiconf.resolve(args[0] if args and args[0] else None)
        if wiki is None:
            print("llm-wiki is not configured; run /llm-wiki:init")
            return 0
        print(render(report(wiki, recent_transcripts(days), days)), end="")
    except Exception as exc:  # a report is optional: never traceback
        print(f"llm-wiki keywords report could not run: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
