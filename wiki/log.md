# Log

Append-only chronological record of wiki activity. Every entry starts with `## [YYYY-MM-DD] {op} | {label}` so it's parseable with simple shell tools:

```bash
grep "^## \[" wiki/log.md | tail -5          # recent 5 entries
grep "^## \[.*\] ingest" wiki/log.md         # all ingests
grep "^## \[2026-04" wiki/log.md             # everything in April 2026
```

Append-only by default. If an entry needs correction, add a new entry that references it. The only sanctioned exception is the **hard erase** mode of the Prune operation in `CLAUDE.md`, which removes entries referencing fully-erased content.

---

## [2026-04-11] bootstrap | initialize wiki from template

- Created `CLAUDE.md` schema
- Created `wiki/index.md`, `wiki/log.md`
- Created placeholder `raw/assets/` for downloaded images

## [2026-04-11] ingest | Karpathy, "LLM Wiki" (gist)

- Source: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Created [[sources/2026-04-11-karpathy-llm-wiki]]
- Created [[concepts/llm-wiki-pattern]] — the core pattern
- Created [[concepts/rag]] — baseline being contrasted
- Created [[concepts/memex]] — historical ancestor cited at the end of the gist
- Created [[entities/andrej-karpathy]]
- Created [[entities/obsidian]]
- Created [[entities/qmd]]
- Updated [[index]] with all new pages
- Notable: the gist explicitly says LLM Wiki is complementary to RAG at scale, not a replacement. Flag any future source that frames this as a RAG-killer.

## [2026-04-11] query | how is LLM Wiki different from NotebookLM?

- Pulled from [[concepts/llm-wiki-pattern]] and [[concepts/rag]]
- Key distinction: NotebookLM re-retrieves at query time; LLM Wiki pre-compiles knowledge into a persistent artifact.
- Did not file back as a new page yet — a dedicated comparison page may be worth creating after 1-2 more sources on NotebookLM arrive.

## [2026-04-17] schema | wired qmd into Ingest/Query workflows

- Added a new step 9 to the Ingest workflow: `qmd update` after writing changes (renumbered "Report back" to step 10)
- Updated Query operation step 1 to prefer `mcp__plugin_qmd_qmd__query` over reading `wiki/index.md` when qmd is configured (with index.md as fallback)
- Added new `### Search (qmd)` subsection under "## Index and log" describing the qmd integration contract: scope to `wiki/` only, add collection-level context, conventions for refreshing
- Reasoning: qmd MCP is now configured with collection `llm-wiki` (scoped to `wiki/` subfolder, embedded, MCP-queryable from any session). Schema needed to make the integration explicit so future sessions use it consistently rather than re-discovering each time.

## [2026-04-17] schema | added Prune operation (soft + hard erase modes)

- Codified deletion workflow into `CLAUDE.md` after first hard-erase use case (a template-seed test page that the user wanted gone with no historical trace)
- Added `prune` and `schema` to the list of valid log op types
- Updated `wiki/log.md` preamble and "What you do NOT do" section in `CLAUDE.md` to reflect the hard-erase exception to append-only
- Reasoning: the wiki will be used personally with real content (starting from the Karpathy gist onward), but the template ships with seed/test content that the user may want erased without polluting the historical record

