# Operation: Prune — full workflow

> High-level contract is in `CLAUDE.md` under `## Operation: Prune`. This file has the detailed workflow for both soft and hard modes.

Use this operation when the user asks you to delete, remove, or "get rid of" a page, raw artifact, or set of pages. Like Act, Prune has cascade effects (broken links, drift between docs and reality), so always propose before executing.

There are **two modes** the user picks per operation:

---

## Soft prune (default)

The wiki forgets the content but the log remembers it existed. Use for real-world deletions: superseded sources, merged concepts, abandoned ideas, content the user no longer endorses.

1. **Find blast radius** — grep all backlinks; check `wiki/index.md`; check `raw/` for related artifacts; check non-wiki docs (`README.md`, `docs/`, `.obsidian/`).
2. **Propose disposition** for each backlink (remove the link / replace with another / inline the content). List every affected file. Wait for approval.
3. **Apply edits** to the backlinking pages.
4. **Remove from `wiki/index.md`.**
5. **Delete the file(s).**
6. **Append a prune entry** to `wiki/log.md`: `## [YYYY-MM-DD] prune | {what was deleted}` — list every removed slug so the historical record is complete.
7. **Trigger qmd reindex** if applicable.
8. **Report back** — what changed, blast radius handled, any stale external references.

---

## Hard erase (explicit opt-in)

Treats the content as if it never existed. Use for content that was never meant to be in the wiki: template seed pages, accidental ingests, test pages, content the user wants no future trace of.

The user must explicitly say "hard erase," "as if it never existed," or equivalent. If unclear, ask which mode.

Steps 1–5 are the same as soft prune. Then:

6. **Rewrite `wiki/log.md`** to remove every entry referencing the erased content. This **overrides** the "append-only" rule for the log — the rule itself notes this exception.
7. **Sweep all non-wiki docs** (`README.md`, `docs/HANDOFF.md`, `.obsidian/workspace.json`, anything else) and remove every reference.
8. **Run a final repo-wide grep** to confirm zero remaining references.
9. **Trigger qmd reindex** if applicable.
10. **Report back** — what was erased, every file touched, that history was rewritten, and that git history (if the wiki is in a git repo) still preserves the deleted content unless the git history is also rewritten (a much heavier operation).

---

## Rules for both modes

- **Approval is mandatory.** No deletion without explicit per-operation approval. No exceptions, no bulk silent deletes.
- **Bulk deletions** (>5 files in one op) — list each file explicitly in the proposal, do not summarize as "12 pages tagged X".
- **`raw/` is not touched by default.** If a `raw/` file is referenced by the page being pruned, ask whether to move to `archive/`, delete, or leave alone. Default: leave alone — `raw/` is the primary evidence and removing it weakens the wiki's trustworthiness.
- **`.obsidian/workspace.json`** can drift after pages are deleted; cleaning references is safe (Obsidian rebuilds it on next launch). Note that Obsidian may re-add deleted entries to its `lastOpenFiles` list while running — close and reopen the vault to fully reset.
- **`wiki/log.md` `bootstrap`/`schema` entries** — never erased, even in hard mode, since they describe the wiki's structure rather than its content.
