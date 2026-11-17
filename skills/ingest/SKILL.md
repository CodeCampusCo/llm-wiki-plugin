---
name: ingest
description: Use to bring a source (URL, file, video, image, or notes from this session) into the LLM Wiki. Triggers - "ingest this", "add this to my wiki", "save to wiki", "/llm-wiki:ingest", "ingest เข้า wiki", "เก็บเข้า wiki".
argument-hint: "<url-or-path>"
---

# Ingest into LLM Wiki

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

Operation files: `<plugin_root>/schema/schema.md` section "Operation: Ingest", then
`<plugin_root>/schema/operations/ingest.md`. For video or audio, also
`<plugin_root>/schema/operations/video-ingest.md`.

Source to ingest: $ARGUMENTS

## Steps

1. Get the source into `<raw_dir>` first, never editing the original:
   - A file or download from the current project: copy it into `<raw_dir>/articles/`, `<raw_dir>/pdfs/`
     or `<raw_dir>/images/`, then ingest from the copy.
   - Notes or findings from this session: write them to `<raw_dir>/articles/YYYY-MM-DD-slug.md` as a
     `note` source, stripped of credentials, tokens and customer data.
   - A raw video or audio file goes to `<archive_dir>` (check it exists with `ls` or `test -f`).
2. Read the source in full before writing anything.
3. Discuss with the user first: summarize it and ask for angle and emphasis.
4. Propose every page create or update, then apply only after approval. Never rewrite more than a paragraph
   of an existing page silently.
5. Create `<root>/wiki/sources/YYYY-MM-DD-slug.md`, update `<root>/wiki/index.md`, and append
   `## [YYYY-MM-DD] ingest | {title}` to `<root>/wiki/log.md`. Give new pages `keywords` as the schema describes.
6. If `qmd_collection` is set, the PostToolUse hook runs `qmd update` after edits inside `<root>/wiki/`.
   Edits made through Bash do not trigger it: run `qmd update` yourself then.
7. If `qmd_collection` is set, run `qmd embed` once after all edits (the hook already ran `qmd update`), so vector
   search sees the new pages.
8. Report: pages changed, interesting findings, suggested follow-up sources.
