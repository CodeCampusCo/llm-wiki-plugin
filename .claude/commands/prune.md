---
description: Delete a wiki page (soft prune by default; hard erase on request)
argument-hint: "<page-or-pattern> [hard]"
---

Run the **Prune** operation defined in `CLAUDE.md` under `## Operation: Prune`.

Target: $ARGUMENTS

**First: determine the mode.**

- **Soft prune** (default) — wiki forgets the content, log remembers it existed. Use for superseded sources, merged concepts, abandoned ideas.
- **Hard erase** (explicit opt-in) — treats the content as if it never existed, rewrites `wiki/log.md` to remove references. Use for template seed pages, accidental ingests, test content.

If my input above contains "hard", "erase", or "as if it never existed" → hard mode. Otherwise → soft. **If ambiguous, ask me which mode before proceeding.**

**Workflow (both modes share steps 1–5):**

1. **Find blast radius** — grep all backlinks; check `wiki/index.md`; check `raw/` for related artifacts; check `README.md`, `docs/`, `.obsidian/`.
2. **Propose disposition** for each backlink (remove / replace / inline). List every affected file. Wait for approval.
3. **Apply edits** to backlinking pages.
4. Remove from `wiki/index.md`.
5. Delete the file(s).

**Soft prune:** append `## [YYYY-MM-DD] prune | {what was deleted}` to `wiki/log.md` listing every removed slug.

**Hard erase:** additionally — rewrite `wiki/log.md` to remove every entry referencing the erased content, sweep all non-wiki docs (`README.md`, `docs/HANDOFF.md`, `.obsidian/workspace.json`), run a final repo-wide grep to confirm zero references.

Then (both modes): trigger qmd reindex if applicable and report back.

**Hard rules:**
- **Approval is mandatory.** No deletion without explicit per-operation approval.
- **Bulk deletions** (>5 files) — list each file in the proposal.
- **`raw/` is not touched by default.** Ask before moving to `archive/` or deleting.
- **`bootstrap`/`schema` log entries are never erased,** even in hard mode — they describe structure, not content.
