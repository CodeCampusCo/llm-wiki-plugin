#!/usr/bin/env python3
"""UserPromptSubmit hook: point the model at wiki pages whose `keywords` occur in the prompt.

Each concept/entity page in the wiki may list `keywords: [...]` in its frontmatter: words the user actually
types for that topic. A Latin keyword matches as a whole word or identifier; a Thai one as a substring (Thai has
no spaces to split on). Pages are ranked by how many of their keywords match. Injects at most MAX_HITS pages as
one TL;DR line each, each page once per session. Prints nothing when there is no match; never fails the prompt.

Full-text search (qmd BM25 on every Latin word) was tried first and dropped: it fired on 72% of real prompts, often on
unrelated pages, through common words such as "session", "update" or "note".

Usage: wiki_hint.py <data_dir>   (UserPromptSubmit JSON on stdin)
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

MAX_HITS, TLDR_CHARS = 3, 220
THAI = re.compile("[฀-๿]")
WORD = r"a-z0-9_\-"  # regex class body: characters that continue a word or identifier


def state_dir():
    return Path(os.environ.get("TMPDIR", "/tmp")) / "llm-wiki-hint"


def matches(keyword, text):
    """keyword occurs in lowercased text: Thai as a substring, Latin not inside a longer word or identifier."""
    k = keyword.lower()
    if not k:
        return False
    if THAI.search(k):
        return k in text
    before = f"(?<![{WORD}/])" if re.match(f"[{WORD}]", k) else ""
    after = f"(?![{WORD}])" if re.search(f"[{WORD}]$", k) and not k.endswith(("_", "-")) else ""
    return re.search(before + re.escape(k) + after, text) is not None


def pages(pages_dir):
    """(relative path, title, keywords) for every page that declares keywords."""
    out = []
    for page in sorted(Path(pages_dir).glob("*/*.md")):
        try:
            head = page.read_text(encoding="utf-8", errors="replace").split("\n---", 1)[0]
        except OSError:
            continue
        kw = re.search(r"^keywords:\s*(\[.*\])\s*$", head, re.M)
        if not kw:
            continue
        try:
            words = [w for w in json.loads(kw.group(1)) if isinstance(w, str)]
        except json.JSONDecodeError:
            continue
        title = re.search(r'^title:\s*"?(.*?)"?\s*$', head, re.M)
        rel = page.relative_to(pages_dir).as_posix()
        out.append((rel, title.group(1) if title else rel, words))
    return out


def rank(prompt, pages_dir):
    """Pages with at least one keyword in the prompt, most matched keywords first."""
    text = prompt.lower()
    scored = [(sum(matches(w, text) for w in words), rel, title) for rel, title, words in pages(pages_dir)]
    return [(rel, title) for n, rel, title in sorted(scored, key=lambda s: (-s[0], s[1])) if n]


def tldr(pages_dir, rel):
    try:
        for line in (Path(pages_dir) / rel).read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("> TL;DR:"):
                text = line.removeprefix("> TL;DR:").strip()
                return text if len(text) <= TLDR_CHARS else text[:TLDR_CHARS].rsplit(" ", 1)[0] + " ..."
    except OSError:
        pass
    return ""


def header(wiki):
    if wiki.qmd_collection:
        how = f"qmd get qmd://{wiki.qmd_collection}/<path>"
    else:
        how = f"Read {wiki.pages_dir}/<path>"
    return f"llm-wiki pages match this prompt. Read the relevant ones ({how}) before acting:"


def hint(prompt, shown, wiki):
    """The context to inject (or ""), and the pages it names."""
    # top pages first, then drop the ones already shown: a repeat prompt adds nothing rather than weaker pages
    found = [(rel, t) for rel, t in rank(prompt, wiki.pages_dir)[:MAX_HITS] if rel not in shown]
    if not found:
        return "", []
    lines = [header(wiki)]
    lines += [f"- {rel}: {t}. {tldr(wiki.pages_dir, rel)}".rstrip() for rel, t in found]
    return "\n".join(lines), [rel for rel, _ in found]


def main(argv):
    import wikiconf

    data = json.load(sys.stdin)
    wiki = wikiconf.resolve(argv[1] if len(argv) > 1 and argv[1] else None)
    if wiki is None:
        return
    session = re.sub(r"[^A-Za-z0-9_-]", "", data.get("session_id", "")) or "none"
    state = state_dir() / session
    shown = set(state.read_text().split()) if state.exists() else set()
    text, found = hint(data.get("prompt", ""), shown, wiki)
    if not text:
        return
    state_dir().mkdir(parents=True, exist_ok=True)
    state.write_text("\n".join(sorted(shown | set(found))))
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": text}}))


if __name__ == "__main__":
    try:
        main(sys.argv)
    except Exception:  # a hint is optional: never block or break the prompt
        pass
