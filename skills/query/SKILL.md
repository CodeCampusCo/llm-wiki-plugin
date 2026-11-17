---
name: query
description: Use to answer a question from the LLM Wiki, with wikilink citations. Triggers - "what does my wiki say about X", "query the wiki", "/llm-wiki:query", "ถาม wiki".
argument-hint: "<question>"
---

# Query LLM Wiki

Take `<plugin_root>` and `<data_dir>` from this session's context: the lines that start
`Plugin root:` and `Plugin data dir:`. Always quote paths in shell commands (they may contain spaces).

## Before starting

1. Run `python3 "<plugin_root>/scripts/wikiconf.py" show "<data_dir>"`. It prints `root`, `raw_dir`,
   `archive_dir`, `qmd_collection`, `schema_version` and `plugin_schema_version`. If the wiki is not
   configured, tell the user to run `/llm-wiki:init` and stop.
2. Read `<plugin_root>/schema/schema.md`, then `<root>/CONVENTIONS.md`, then the operation file named below.
3. Use absolute paths under `<root>` for everything. Relative paths in the schema (`wiki/`, `raw/`,
   `archive/`) are relative to `<root>`, never the current working directory.
4. Never commit or push in the wiki without the user's approval.

Operation file: `<plugin_root>/schema/schema.md` section "Operation: Query" (complete there).

Question: $ARGUMENTS

## Steps

1. Find candidate pages:
   - If `qmd_collection` is set: call `mcp__plugin_qmd_qmd__query` with the question as a `vec` sub-query,
     optionally a `lex` sub-query for exact terms, and `collections: ["<qmd_collection>"]`. If the MCP tool is
     unavailable, run `qmd query "<question>" -c "<qmd_collection>"`. Read a hit with `qmd get` or by path
     under `<root>/wiki/`.
   - Otherwise: read `<root>/wiki/index.md` and scan for candidates.
2. Drill into the 3 to 7 most relevant pages and follow wikilinks as needed.
3. Synthesize the answer and cite pages with wikilinks, e.g. `according to [[concepts/rag]], ...`.
4. Offer to file the answer as a new wiki page if it is worth keeping. Do not file silently.
5. If information is missing, say so and suggest sources the user could add.
6. Append `## [YYYY-MM-DD] query | {question}` with a one-line summary and any pages created to
   `<root>/wiki/log.md`.
