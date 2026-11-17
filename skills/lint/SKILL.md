---
name: lint
description: Use to health-check the LLM Wiki - mechanical checks plus judgment checks, one merged report. Triggers - "lint the wiki", "wiki health check", "/llm-wiki:lint".
---

# Lint LLM Wiki

Take `<plugin_root>` and `<data_dir>` from this session's context: the lines that start
`Plugin root:` and `Plugin data dir:`. Always quote paths in shell commands (they may contain spaces).

## Before starting

1. Run `python3 "<plugin_root>/scripts/wikiconf.py" show "<data_dir>"`. It prints `root`, `raw_dir`,
   `archive_dir`, `qmd_collection`, `schema_version` and `plugin_schema_version`. If the wiki is not
   configured, tell the user to run `/llm-wiki:init` and stop.
2. Read `<plugin_root>/schema/schema.md` (section "Operation: Lint"), then `<root>/CONVENTIONS.md`.
3. Use absolute paths under `<root>` for everything. Relative paths in the schema (`wiki/`, `raw/`,
   `archive/`) are relative to `<root>`, never the current working directory.
4. Never commit or push in the wiki without the user's approval.

## Steps

1. Run the mechanical checks. Both scripts only report; they exit 0.

   ```sh
   python3 "<plugin_root>/scripts/lint_wiki.py" "<data_dir>"
   python3 "<plugin_root>/scripts/keywords_report.py" "<data_dir>" --days 30
   ```

   `lint_wiki.py` flags: missing frontmatter fields, broken wikilinks, orphans, unparsable `keywords`,
   secret-like strings and emails, and an older `schema_version` (see `<plugin_root>/schema/CHANGELOG.md`).
   `keywords_report.py` reads the user's recent Claude Code prompts locally and lists keywords that never
   matched and frequent words that no page lists. Do not quote prompts in the report.
2. Do the judgment checks from the schema's "Operation: Lint": contradictions, stale claims, missing pages,
   missing cross-references, data gaps. Read the pages under `<root>/wiki/` as needed.
3. Merge everything into one report, grouped by check, each item with the page and a proposed fix.
   If a `secret` finding appears, tell the user to rotate it and do not repeat the value.
4. Edit nothing without approval. Wait for the user to choose which proposals to apply, then apply only those.
   Never commit without approval.
5. After approval, append `## [YYYY-MM-DD] lint | {summary}` to `<root>/wiki/log.md`.
