---
title: "LLM Wiki (gist) — Andrej Karpathy"
type: source
tags: [llm, knowledge-management, pattern, obsidian]
created: 2026-04-11
updated: 2026-04-11
source_url: "https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f"
source_author: "Andrej Karpathy"
source_date: 2026-04
source_kind: note
---

# LLM Wiki (gist) — Andrej Karpathy

> TL;DR: Karpathy proposes a pattern in which an LLM agent incrementally builds and maintains a persistent, interlinked markdown wiki between you and your raw source documents. Knowledge is compiled once and kept current, rather than re-derived on every query as in standard RAG. The human curates sources and asks questions; the LLM does the reading, summarizing, cross-referencing, and upkeep.

## Key points

- **Problem being addressed.** Standard RAG (NotebookLM, ChatGPT file uploads, most production stacks) retrieves chunks at query time and generates an answer. Nothing is accumulated between queries; the LLM rediscovers the same knowledge every time.
- **The pattern.** Between raw sources and the user sits a persistent wiki — a directory of LLM-generated markdown files. When a new source arrives, the LLM reads it, extracts key information, and integrates it into existing pages (updating entities, revising summaries, flagging contradictions). The wiki is a compounding artifact.
- **Division of labor.** The human is in charge of sourcing, exploration, and asking good questions. The LLM does all the grunt work: summarizing, cross-referencing, filing, and bookkeeping. You rarely write the wiki yourself.
- **Three layers.**
  1. **Raw sources** — immutable; the LLM reads but never modifies.
  2. **The wiki** — LLM-owned markdown files. You read; LLM writes.
  3. **The schema** — a config file (`CLAUDE.md` for Claude Code, `AGENTS.md` for Codex, etc.) that tells the LLM the wiki's conventions and workflows. Co-evolved over time.
- **Three operations.** Ingest (add a new source, update affected pages), Query (ask questions, optionally file good answers back as new pages), Lint (health-check the wiki for contradictions, stale claims, orphans, missing pages, data gaps).
- **Two special files.**
  - `index.md` — content-oriented catalog of every page, updated on every ingest. At moderate scale (~100 sources, ~hundreds of pages) this alone replaces the need for embedding-based retrieval infrastructure.
  - `log.md` — chronological append-only record of ingests, queries, and lint passes. Parseable with `grep`.
- **Toolstack.**
  - **Obsidian** — the "IDE" for the wiki. Graph view, Web Clipper for bringing articles in, image download hotkey, Dataview plugin for YAML frontmatter queries, Marp plugin for generating slide decks from wiki content.
  - **qmd** — a local markdown search engine (BM25 + vector + LLM re-ranking) with CLI and MCP server. Recommended when `index.md` alone stops scaling.
  - **git** — the wiki is just a repo of markdown, so version history and branching come for free.
- **Example domains.** Personal (journal, goals, health), research (topic deep-dives over weeks/months), reading books (building a fan-wiki-style companion as you go), internal team wikis fed by Slack and meeting transcripts, competitive analysis, due diligence, trip planning, hobby deep-dives.
- **Historical framing.** Karpathy explicitly connects the idea to Vannevar Bush's **Memex** (1945). Bush's vision was a personal, curated knowledge store with associative trails — the part he couldn't solve was maintenance. LLMs solve that part.
- **Scope and limits (per the gist itself).** The document is intentionally abstract — directory structure, schema details, and tooling all depend on the domain. Everything is optional and modular.
- **What the gist does NOT claim.**
  - It does not claim LLM Wiki replaces RAG. It positions them as complementary — RAG is still the right tool for very large corpora.
  - It does not prescribe a specific token budget or threshold for when the pattern breaks down.
  - It does not compare LLM Wiki to other specific products beyond a passing mention of NotebookLM.

## Notable quotes

> "The knowledge is compiled once and then kept current, not re-derived on every query."

> "Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."

> "The tedious part of maintaining a knowledge base is not the reading or the thinking — it's the bookkeeping… Humans abandon wikis because the maintenance burden grows faster than the value. LLMs don't get bored."

> "The idea is related in spirit to Vannevar Bush's Memex (1945)… The part he couldn't solve was who does the maintenance. The LLM handles that."

## My reading

The most novel move is the explicit claim that **retrieval should happen at write time, not read time** — flipping where the LLM spends its compute. This reframes the "RAG vs fine-tuning" debate by introducing a third option: *compiled knowledge that is neither baked into weights nor re-retrieved each turn*.

Open questions worth seeding future sources on:
- How does this pattern degrade as the wiki gets large? The gist hints at "moderate scale ~100 sources" but doesn't quantify failure modes.
- How do you handle contested ground truth when ingesting sources that contradict each other? Lint catches it; what's the resolution UX?
- What's a good schema pattern for team wikis with multiple humans editing alongside the LLM?

## Updates to the wiki

- Created [[concepts/llm-wiki-pattern]] — the core pattern as a standalone concept page.
- Created [[concepts/rag]] — the baseline being contrasted. Kept short; will grow as more RAG sources arrive.
- Created [[concepts/memex]] — captured the Bush 1945 reference as a standalone page so future sources on pre-LLM knowledge management can link to it.
- Created [[entities/andrej-karpathy]], [[entities/obsidian]], [[entities/qmd]].

## See also

- [[concepts/llm-wiki-pattern]]
- [[concepts/rag]]
- [[concepts/memex]]
- [[entities/andrej-karpathy]]
- [[entities/obsidian]]
- [[entities/qmd]]
