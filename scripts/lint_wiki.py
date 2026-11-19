#!/usr/bin/env python3
"""Mechanical lint for an LLM Wiki: frontmatter, links, orphans, keywords, secrets, schema version.

Usage: lint_wiki.py <data_dir>   (prints a markdown report; always exits 0)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import wiki_hint  # noqa: E402
import wikiconf  # noqa: E402

REQUIRED = ("title", "type", "tags", "created", "updated")
EXEMPT = {"index.md", "log.md"}
LINK = re.compile(r"\[\[([^\]\n]+)\]\]")
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)
SECRETS = (
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("chat API token", re.compile(r"xox[baprs]-")),
    ("GitHub token", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("API secret key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("email address", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b")),
)


def _read(page: Path) -> str:
    return page.read_text(encoding="utf-8", errors="replace")


def _frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    return text[3:].split("\n---", 1)[0]


def _targets(text: str) -> list[str]:
    out = []
    for raw in LINK.findall(CODE.sub("", text)):
        target = raw.split("|", 1)[0].split("#", 1)[0].strip()
        if target:
            out.append(target.removesuffix(".md"))
    return out


def _resolve(target: str, rels: set[str], stems: dict[str, str]) -> str | None:
    if target in rels:
        return target
    return stems.get(target)  # bare slug, as used in `sources:` frontmatter


def _required_fields(rel: str) -> tuple[str, ...]:
    return REQUIRED if rel.startswith("sources/") else REQUIRED + ("sources",)


def _frontmatter_findings(rel: str, text: str) -> list[tuple]:
    head = _frontmatter(text)
    fields = _required_fields(rel)
    return [("frontmatter", rel, f"missing field `{f}`") for f in fields
            if not re.search(rf"^{f}:", head, re.M)]


def _link_findings(texts: dict[str, str]) -> list[tuple]:
    rels = {r.removesuffix(".md") for r in texts}
    stems: dict[str, str] = {}
    for r in rels:
        stems.setdefault(r.rsplit("/", 1)[-1], r)
    inbound: set[str] = set()
    out = []
    for rel, text in texts.items():
        for target in _targets(text):
            hit = _resolve(target, rels, stems)
            if hit is None:
                out.append(("broken-link", rel, f"[[{target}]] does not exist"))
            elif hit != rel.removesuffix(".md"):
                inbound.add(hit)
    for rel in texts:
        if rel not in EXEMPT and rel.removesuffix(".md") not in inbound:
            out.append(("orphan", rel, "no inbound link from any page"))
    return out


def _keyword_findings(wiki: wikiconf.Wiki, texts: dict[str, str]) -> list[tuple]:
    parsed = {rel for rel, _, _ in wiki_hint.pages(wiki.pages_dir)}
    return [("keywords", rel, "keywords line is not a JSON list of strings")
            for rel, text in texts.items()
            if re.search(r"^keywords:", _frontmatter(text), re.M) and rel not in parsed]


def _secret_findings(texts: dict[str, str]) -> list[tuple]:
    return [("secret", rel, f"looks like a {name}")
            for rel, text in texts.items()
            for name, pattern in SECRETS if pattern.search(text)]


def check(wiki: wikiconf.Wiki) -> list[tuple]:
    texts = {p.relative_to(wiki.pages_dir).as_posix(): _read(p)
             for p in sorted(wiki.pages_dir.rglob("*.md"))}
    findings: list[tuple] = []
    if wiki.schema_version < wikiconf.SCHEMA_VERSION:
        findings.append(("schema", ".llm-wiki.json",
                         f"wiki schema_version {wiki.schema_version} is older than plugin "
                         f"{wikiconf.SCHEMA_VERSION}; see schema/CHANGELOG.md"))
    if wiki.schema_version > wikiconf.SCHEMA_VERSION:
        findings.append(("schema", ".llm-wiki.json",
                         f"wiki schema_version {wiki.schema_version} is newer than plugin "
                         f"{wikiconf.SCHEMA_VERSION}; update the plugin"))
    for rel, text in texts.items():
        if rel not in EXEMPT:
            findings += _frontmatter_findings(rel, text)
    findings += _link_findings(texts)
    findings += _keyword_findings(wiki, texts)
    findings += _secret_findings(texts)
    return findings


def render(findings: list[tuple]) -> str:
    if not findings:
        return "# Mechanical lint\n\nNo findings.\n"
    lines = ["# Mechanical lint", "", f"{len(findings)} finding(s).", ""]
    lines += [f"- **{kind}** `{path}`: {detail}" for kind, path, detail in findings]
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    try:
        wiki = wikiconf.resolve(argv[1] if len(argv) > 1 and argv[1] else None)
        if wiki is None:
            print("llm-wiki is not configured; run /llm-wiki:init")
            return 0
        print(render(check(wiki)), end="")
    except Exception as exc:  # a report is optional: never traceback
        print(f"llm-wiki lint could not run: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
