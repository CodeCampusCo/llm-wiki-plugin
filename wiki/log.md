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

## [2026-04-18] schema | fixed Python heredoc variable expansion in video-ingest playbook

- Bug: three `python3 - <<'PY'` blocks in `CLAUDE-video-ingest.md` used a single-quoted `'PY'` delimiter, which disables shell variable expansion inside the heredoc. Inline references like `pathlib.Path("$DERIVED")` resolved to the literal string `"$DERIVED"`, and `every = $KEYFRAME_EVERY` was a Python syntax error (unquoted `$` with no substitution). Steps 3, 4, and 5 of the playbook would have failed on first real run.
- Fix: switched to the pattern `VAR="$VAR" python3 - <<'PY'` + `os.environ["VAR"]` inside Python. Keeps the heredoc single-quoted (safer — prevents accidental `$`-expansion of any `$` that should be a Python literal) while still passing shell values in cleanly. Applied at step 3 (SRT→transcript.md), step 4 (keyframe rename), and step 5 (metadata.json write).
- No change to the main `CLAUDE.md` schema — this was a pure playbook bug fix. Caught during a review of the template before first real personal use.

## [2026-04-18] schema | slash commands, Claude Code hooks, CLAUDE.md split

Three additions in one pass, during the same pre-use template review:

- **Slash commands** under `.claude/commands/` — `/ingest`, `/query`, `/lint`, `/act`, `/prune`. Each is a short wrapper that names the operation and delegates to the canonical workflow in `CLAUDE.md` (and for Ingest/Prune, the detail files in `docs/operations/`). Accepts `$ARGUMENTS`. Additive, no schema change — existing prose triggers like "ingest this" still work identically.
- **Claude Code hooks** wired in `.claude/settings.json`:
  - `SessionStart` → runs `.claude/hooks/session-start-context.sh`, which prints the last 5 entries from `wiki/log.md` + qmd status into the agent's context. Purpose: continuity between sessions.
  - `PostToolUse` on `Write|Edit` → runs `.claude/hooks/post-wiki-edit.sh`, which refreshes the qmd index silently (with a 10-second timeout) when the edited file is inside `wiki/`. Purpose: keep search index fresh without manual `qmd update`. Both hook scripts are no-ops when their optional tooling (`jq`, `qmd`) is missing, so they never block the agent.
  - Added `Bash(qmd update*)` to `.claude/settings.local.json` permissions so the hook can run without prompting.
- **`CLAUDE.md` split** — went from 663 lines to ~450 by moving long workflows out:
  - `docs/operations/ingest.md` — full Ingest workflow incl. video and image sub-ops.
  - `docs/operations/prune.md` — full Prune workflow with soft + hard modes.
  - `docs/slack-mode.md` — entire Slack bot integration section (now lives in its own file, activated only when the session preamble announces Slack mode).
  - `CLAUDE.md` keeps high-level contract + pointer for each, plus all the content that was already short (Query, Lint, Act, Connected tools, Index/log/qmd, Style, What-NOT-to-do, Bootstrapping).
- Updated `docs/HANDOFF.md`: new directory map, "What's done" list, "Files to read in order" (now marks on-demand reads separately), changelog entry.
- Reasoning: `CLAUDE.md` loads into every session; trimming it saves context and the long workflows are only consulted during their specific operation. HANDOFF.md explicitly flagged "don't rewrite `CLAUDE.md` silently" so the split was proposed and approved before applying.

