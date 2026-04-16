---
title: "LLM Wiki pattern"
type: concept
tags: [pattern, knowledge-management, llm, wiki]
created: 2026-04-11
updated: 2026-04-11
status: draft
sources: ["[[sources/2026-04-11-karpathy-llm-wiki]]"]
related: ["[[concepts/rag]]", "[[concepts/memex]]"]
---

# LLM Wiki pattern

> TL;DR: A pattern in which an LLM agent incrementally builds and maintains a persistent, interlinked markdown wiki sitting between the user and their raw source documents. Knowledge is compiled once at ingest time and kept current, rather than re-derived on every query. The human curates sources and asks questions; the LLM does all reading, summarization, cross-referencing, and maintenance.

## Definition

The LLM Wiki pattern is a knowledge-management architecture with three layers:

1. **Raw sources** — an immutable, user-curated collection of source documents (articles, papers, notes, images).
2. **The wiki** — a directory of LLM-generated, interlinked markdown files. Summaries, entity pages, concept pages, comparisons, an overview. Fully owned by the LLM.
3. **The schema** — a configuration file (e.g. `CLAUDE.md`) that encodes conventions and workflows so the LLM behaves as a disciplined wiki maintainer rather than a generic chatbot.

Three core operations cycle over this structure:

- **Ingest** — read a new source, extract key information, update all affected pages, append to the log.
- **Query** — answer questions against the wiki, optionally filing good answers back as new pages.
- **Lint** — periodically audit the wiki for contradictions, stale claims, orphan pages, missing pages, and data gaps.

## Why it matters

Standard RAG workflows (see [[concepts/rag]]) retrieve raw chunks at query time and generate an answer. Nothing accumulates between queries; the same synthesis work has to be redone every time.

The LLM Wiki pattern flips the location of the compute: **retrieval and synthesis happen at write time**, not read time. The persistent wiki is a compounding artifact — every new source makes it richer, every good query can be filed back into it.

The practical effect is that the maintenance burden of a personal or team knowledge base collapses toward zero. Humans historically abandon wikis because cross-referencing, updating summaries, and flagging contradictions is tedious. LLMs don't get bored, don't forget to update a link, and can touch 15 files in a single pass.

## Key ideas

- **Write-time compilation vs. read-time retrieval.** The wiki is the "compiled" form of the raw sources. Queries read from the compiled form most of the time, falling back to raw sources only when needed.
- **The LLM is the programmer; the wiki is the codebase.** Karpathy's analogy: Obsidian is the IDE, the LLM edits files, the human reviews the graph view in real time.
- **Division of labor.** Human: sourcing, exploration, asking good questions, strategic direction. LLM: summarizing, cross-referencing, filing, bookkeeping, lint maintenance.
- **The schema co-evolves.** `CLAUDE.md` starts minimal and grows as you notice what conventions matter in your domain. Schema updates are themselves a form of knowledge accumulation.
- **Index + log replace infrastructure at moderate scale.** A single `index.md` file is sufficient retrieval at ~100 sources / ~hundreds of pages. Only above that does a proper search engine (e.g. [[entities/qmd]]) become necessary.
- **Queries can compound.** A comparison, a synthesis, or an insight generated during a query is wiki-worthy — file it back as a new page so future questions build on it instead of rediscovering it.
- **The wiki is plain markdown in a git repo.** You get version history, branching, collaboration, diffs, and portability for free. Data is never locked into a vendor format.

## Relationship to RAG

The pattern is **complementary to, not a replacement for,** standard retrieval. Karpathy's gist does not claim RAG is obsolete. A reasonable division of labor:

- **LLM Wiki** — small-to-moderate personal or team knowledge bases; domains where the same material is queried repeatedly and synthesis compounds in value over time.
- **RAG** — very large corpora where compiling every document into wiki pages is prohibitive; one-shot retrieval over material that won't be revisited.

A future source that frames LLM Wiki as "RAG-killer" should be flagged as overstating the claim.

## Open questions / contradictions

- At what scale does the pattern break down? The gist hints at "moderate" (~100 sources) but doesn't quantify failure modes.
- What's the right UX for resolving contradictions surfaced during lint?
- How does this pattern generalize to multi-human team wikis where several people edit alongside the LLM?
- No empirical comparison to NotebookLM, ChatGPT Projects, or other retrieval-first tools exists in sources yet.

## Sources

- [[sources/2026-04-11-karpathy-llm-wiki]] — primary source; introduced the pattern.

## See also

- [[concepts/rag]] — the baseline the pattern is positioned against
- [[concepts/memex]] — 1945 conceptual ancestor
- [[entities/andrej-karpathy]] — author
- [[entities/obsidian]] — recommended IDE
- [[entities/qmd]] — recommended search tool when index.md stops scaling
