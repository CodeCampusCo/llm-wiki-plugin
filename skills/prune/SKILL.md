---
name: prune
description: Use to delete or merge wiki pages from the LLM Wiki, soft prune by default, hard erase only on explicit request. Triggers - "prune the wiki", "delete wiki page", "remove from wiki", "/llm-wiki:prune", "ลบออกจาก wiki".
argument-hint: "<page-or-pattern> [hard]"
---

# Prune LLM Wiki pages

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

Operation files: `<plugin_root>/schema/schema.md` section "Operation: Prune", then
`<plugin_root>/schema/operations/prune.md` (full workflow for both modes).

Target: $ARGUMENTS

## Mode

- Soft prune (default): the wiki forgets the content, `<root>/wiki/log.md` remembers it existed.
- Hard erase: only if the user says "hard", "erase", "as if it never existed" or similar. It rewrites the log
  and sweeps non-wiki docs.
- If the mode is ambiguous, ask the user before doing anything.

## Steps

1. Find the blast radius: grep backlinks, check `<root>/wiki/index.md`, related artifacts in `<raw_dir>`,
   and docs such as `README.md` and `.obsidian/`.
2. Propose a disposition for each backlink (remove, replace, inline) and list every affected file. Wait for approval.
3. Apply the edits, remove the page from `<root>/wiki/index.md`, delete the file(s).
4. Soft: append `## [YYYY-MM-DD] prune | {what was deleted}` listing every removed slug. Hard: follow
   `prune.md` for the log rewrite and the final repo-wide grep.
5. If `qmd_collection` is set, the PostToolUse hook runs `qmd update` for Write/Edit inside `<root>/wiki/`.
   Deletions made through Bash do not trigger it: run `qmd update` yourself then.
6. If `qmd_collection` is set, run `qmd embed` once after all edits (the hook already ran `qmd update`).

## Hard rules

- Approval is mandatory for every prune. No silent deletes.
- For more than 5 files, list each file in the proposal.
- `<raw_dir>` is not touched by default. Ask before moving to `<archive_dir>` or deleting.
- `bootstrap` and `schema` log entries are never erased, even in hard mode.
