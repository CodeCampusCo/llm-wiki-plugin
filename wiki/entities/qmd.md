---
title: "qmd"
type: entity
entity_kind: tool
tags: [tool, search, markdown, local-first]
created: 2026-04-11
updated: 2026-04-11
---

# qmd

> TL;DR: A local search engine for a folder of markdown files. Combines BM25 keyword search, embedding-based semantic search, and LLM-based re-ranking. Runs entirely on-device and is usable both as a CLI (for shelling out) and as an MCP server (as a native LLM tool). Recommended in [[sources/2026-04-11-karpathy-llm-wiki]] when `index.md` alone stops scaling.

## Role in the LLM Wiki workflow

At small scale — roughly the ~100 sources / hundreds of pages range mentioned in the gist — `wiki/index.md` is sufficient retrieval. The LLM reads the index, picks candidate pages, and drills down.

As the wiki grows past that, the index becomes too large to scan on every query. A proper search tool becomes necessary. `qmd` is the gist's recommendation because:

- **Hybrid search.** BM25 + vector + LLM re-ranking in one tool, so you don't have to stitch together three systems.
- **Local-first.** Data never leaves the machine.
- **Two interfaces.** CLI for shell-based agents that prefer to shell out; MCP server for agents that use tools natively.

## Key facts

- Target: folders of markdown files.
- Hybrid retrieval: BM25 + semantic + re-ranking.
- Interfaces: CLI + MCP server.
- On-device.

## Appearances in the wiki

- [[sources/2026-04-11-karpathy-llm-wiki]] — recommended search tool for wikis that outgrow `index.md`-only retrieval.

## See also

- [[entities/obsidian]]
- [[concepts/llm-wiki-pattern]]
- [[concepts/rag]] — for context on where search fits in the overall retrieval landscape
