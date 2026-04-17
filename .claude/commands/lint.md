---
description: Run a health check on the wiki
argument-hint: "<optional-scope>"
---

Run the **Lint** operation defined in `CLAUDE.md` under `## Operation: Lint`.

Scope (optional): $ARGUMENTS — if empty, lint the whole wiki.

Checks to run:

1. **Contradictions** — pages making conflicting claims. Report with both wikilinks and propose a resolution.
2. **Stale claims** — statements newer sources have superseded. Propose edits.
3. **Orphan pages** — wiki pages with no inbound links. Either link from `index.md` / a parent, or propose deletion.
4. **Missing pages** — concepts/entities referenced inline but with no page yet. List and offer to stub.
5. **Missing cross-references** — pages on the same topic that don't link to each other.
6. **Data gaps** — questions the wiki can't answer yet and what sources would fill them.

**Important:**
- Write a lint **report** — a temporary scratch page or inline in chat. **Do not modify pages during lint.** Propose → wait for approval → edit.
- Append to `wiki/log.md`: `## [YYYY-MM-DD] lint | {summary}` once the report is filed.
