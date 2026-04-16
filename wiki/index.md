---
title: "Index"
type: index
updated: 2026-04-17
---

# Wiki Index

Start here. This is the catalog of every page in the wiki, organized by category. When you're looking for something, skim this page first — every entry is a wikilink plus a one-line summary.

> **Maintainer note (for the LLM):** Update this file on every ingest. Keep summaries to one line. Keep categories alphabetical within each section.

---

## Sources

One page per raw document. Naming: `YYYY-MM-DD-slug` where the date is the ingest date.

- [[sources/2026-04-11-karpathy-llm-wiki]] — Karpathy's gist proposing the LLM Wiki pattern: an LLM-maintained, persistent, interlinked markdown knowledge base that compounds over time.

---

## Concepts

Abstract topics, patterns, ideas. No date prefix.

- [[concepts/llm-wiki-pattern]] — an LLM maintains a persistent, interlinked markdown wiki between the user and their raw sources; the knowledge is compiled once and kept current rather than re-derived on every query.
- [[concepts/rag]] — retrieval-augmented generation; fetch relevant chunks at query time and generate an answer. The baseline the LLM Wiki pattern is positioned against.
- [[concepts/memex]] — Vannevar Bush's 1945 vision of a personal, curated knowledge store with associative trails — a conceptual ancestor of the LLM Wiki pattern.

---

## Entities

People, tools, organizations, places.

- [[entities/andrej-karpathy]] — co-founder of OpenAI; author of the LLM Wiki gist.
- [[entities/obsidian]] — markdown-based note app used as the wiki "IDE": graph view, wikilinks, Dataview, Web Clipper.
- [[entities/qmd]] — local markdown search engine with hybrid BM25 + vector search and LLM re-ranking; usable as CLI or MCP server.

---

## How to extend this index

When you add a new page, add it to the right section above in alphabetical order. If a new category emerges (e.g. `comparisons/`, `questions/`, `timelines/`), add a new `##` section. If the index grows past ~200 entries, consider splitting it into per-category index files and making this one a directory of indexes.
