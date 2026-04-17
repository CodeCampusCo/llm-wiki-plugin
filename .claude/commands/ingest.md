---
description: Ingest a new source into the wiki
argument-hint: "<url-or-path>"
---

Run the **Ingest** operation defined in `CLAUDE.md` under `## Operation: Ingest`.

Source to ingest: $ARGUMENTS

Key reminders (the full contract is in `CLAUDE.md`, do not skip steps):

1. Read the source in full before writing anything.
2. **Discuss with me first** — summarize what you read and ask for angle/emphasis.
3. Propose every page create/update before applying.
4. Create `wiki/sources/YYYY-MM-DD-slug.md` using the source skeleton.
5. Update `wiki/index.md` and append to `wiki/log.md` as `## [YYYY-MM-DD] ingest | {title}`.
6. If qmd is configured for this wiki (see `CLAUDE.md` → Search (qmd)), run `qmd update` after edits.
7. Report back with: pages changed, interesting findings, suggested follow-up sources.

For **video / audio / image-heavy** sources, first run the preprocessing flow in `CLAUDE-video-ingest.md` (or the image sub-operation in `CLAUDE.md`), then treat the derived artifact as the source and return to step 1.
