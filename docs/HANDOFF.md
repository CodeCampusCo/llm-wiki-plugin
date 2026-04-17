# Handoff — continuing this template in Claude Code

> **Read this first.** This doc is for the next agent (probably Claude Code) or the next human who picks up the project. It explains what exists, what state it's in, what's been decided, and what to do next. If something in the repo contradicts this doc, the repo wins — update this doc.

## TL;DR

This is an **LLM Wiki template** (Karpathy-style) that's been designed to:

1. Work for one person right now with zero extra setup beyond git + Obsidian + an LLM agent.
2. Be ready to drop a Slack bot in front of later **without changing any existing file shape, frontmatter, or directory layout**.

The template is in a "usable for personal experimentation, Slack integration planned but not built" state. The Slack parts exist only as planning docs in `docs/`.

The owner (Bom) is about to start using it personally to validate the schema before any team/Slack work happens.

## Current state (as of 2026-04-18)

### What's done

- Core template structure (`CLAUDE.md`, `README.md`, `wiki/`, `raw/`, `.gitignore`).
- Three-tier storage model documented and working: `wiki/` (git, markdown-only) → `raw/` (cloud drive, binaries + derived artifacts) → `archive/` (optional external, rarely-accessed originals).
- Video ingestion playbook (`CLAUDE-video-ingest.md`) with actual shell commands for yt-dlp → whisper → ffmpeg keyframes → derived artifacts.
- Image ingestion flow documented in `docs/operations/ingest.md` (moved from inline in `CLAUDE.md` during the 2026-04-18 refactor).
- **Five operations defined**: Ingest / Query / Lint / **Act** / **Prune**. Act and Prune both enforce human-in-the-loop approval.
- Tool-agnostic Connected-tools registry inside `CLAUDE.md` (fill-in-the-blank — no specific MCP vendors hardcoded).
- Slash commands for all five operations under `.claude/commands/` — `/ingest`, `/query`, `/lint`, `/act`, `/prune`. Each delegates to `CLAUDE.md` for the full workflow.
- Claude Code hooks wired in `.claude/settings.json`:
  - `SessionStart` → prints last 5 log entries + qmd status for continuity.
  - `PostToolUse` on `Write|Edit` → auto-runs `qmd update` when wiki/ files are edited.
- `CLAUDE.md` split (2026-04-18): the core-schema file stayed ~450 lines, with the long workflows moved to `docs/operations/ingest.md`, `docs/operations/prune.md`, and `docs/slack-mode.md`. High-level contracts + pointers remain inline in `CLAUDE.md`.
- Two example source pages (one text, one video) showing both patterns. The video page demonstrates the "discrepancies from primary source" pattern.
- Three example concept pages and three example entity pages.
- Bootstrap `index.md` and `log.md`.
- Slack bot architecture + UX patterns documented in `docs/` (planning only, not built).
- Slack mode rules live in `docs/slack-mode.md`, activated only when a bot preamble tells the agent it's running in Slack mode. No effect on local use — `CLAUDE.md` keeps only a ~15-line activation summary.

### What's intentionally not done

- No actual Slack bot code. The user will experiment personally first, then build the bot later using `docs/slack-bot-architecture.md` as a blueprint.
- No CI, no pre-commit hooks. Add when the wiki stabilises.
- No test suite. The "tests" are the lint operation and manual review.
- No automatic deployment / syncing between machines. README describes manual git sync.
- No team onboarding docs. The Google Workspace / non-technical member path was discussed but deferred — revisit when the personal-use phase validates the schema.

## Directory map

```
llm-wiki-template/
├── CLAUDE.md                       # schema (core), read every session — ~450 lines
├── CLAUDE-video-ingest.md          # detailed video workflow (shell commands)
├── README.md                       # human-facing overview, quick start, sync tips
├── .gitignore
├── .claude/
│   ├── settings.json               # project-level config (hooks — committed)
│   ├── settings.local.json         # personal config (permissions — typically git-ignored)
│   ├── commands/                   # slash commands — /ingest, /query, /lint, /act, /prune
│   │   ├── ingest.md
│   │   ├── query.md
│   │   ├── lint.md
│   │   ├── act.md
│   │   └── prune.md
│   └── hooks/
│       ├── session-start-context.sh    # prints recent log entries at session start
│       └── post-wiki-edit.sh           # runs `qmd update` after wiki/ edits
├── docs/
│   ├── HANDOFF.md                  # ← you are here
│   ├── operations/                 # full workflows split out of CLAUDE.md
│   │   ├── ingest.md               # Ingest + video + image sub-ops
│   │   └── prune.md                # soft + hard erase workflows
│   ├── slack-mode.md               # Slack bot rules (loaded only when preamble activates)
│   ├── slack-bot-architecture.md   # planning: components, permissions, phases, risks
│   └── slack-bot-ux-patterns.md    # planning: 5 UX patterns, Slack mrkdwn rules
├── wiki/                           # Tier 1 — git, markdown only
│   ├── index.md
│   ├── log.md
│   ├── sources/
│   │   └── 2026-04-11-karpathy-llm-wiki.md
│   ├── concepts/
│   │   ├── llm-wiki-pattern.md
│   │   ├── rag.md
│   │   └── memex.md
│   └── entities/
│       ├── andrej-karpathy.md
│       ├── obsidian.md
│       └── qmd.md
└── raw/                            # Tier 2 — cloud drive, git-ignored
    └── README.md                   # explains subfolder conventions
```

`archive/` (Tier 3) is not created on disk; it's opt-in and documented only.

## Design decisions and why

These are the invariants. Don't break them without updating this doc and `CLAUDE.md`.

1. **`wiki/` is markdown only.** No binaries. Ever. This is what makes git, diff, blame, and Obsidian Dataview all work together. Binaries live in `raw/` or `archive/`.
2. **Sources are immutable.** Once ingested, `wiki/sources/*.md` is only edited to fix factual errors or add derived references. Interpretation goes in `concepts/` and `entities/`.
3. **Schema before content.** If the agent wants to break a convention (new frontmatter field, new page type, new tag style), it proposes a `CLAUDE.md` edit first, then applies.
4. **Tool-agnostic.** The template must work with any LLM agent that can read `CLAUDE.md` and edit files. No hardcoded vendor names in schema. Connected tools are a fill-in-the-blank registry.
5. **Slack integration is additive.** Any Slack-related feature must be expressible as a new section in `CLAUDE.md` or a new file in `docs/`. It must not require changing `wiki/` shape or existing frontmatter.
6. **Human-in-the-loop for Act.** Every external side effect needs per-operation approval. No bulk acts. Irreversible acts need a second confirmation.
7. **ISO dates everywhere.** `YYYY-MM-DD` in frontmatter, filenames, log entries.
8. **Obsidian wikilinks.** `[[page]]` syntax so Obsidian graph view works without config.

## Open questions (for the next agent to discuss with the user)

These are deliberately unresolved — the user wants to validate personally first before committing to answers.

1. **Per-page visibility.** `docs/slack-bot-architecture.md` mentions a `visibility: private | team-only | public` frontmatter field for the Slack privacy layer. It's **not yet added to the page skeletons in `CLAUDE.md`.** Add when Slack bot work starts; don't add prematurely.
2. **How to mount `raw/` on the bot server.** rclone mount vs S3 vs something else. Defer until phase 1 of the Slack rollout.
3. **Does Lint run automatically?** Right now Lint is a manual operation the user invokes. It could be a git pre-commit hook or a CI check. Revisit when the wiki has >30 pages.
4. **Multiple wikis or one big one?** The template assumes one wiki per domain. If the user ends up with several overlapping domains, a cross-wiki reference scheme will need designing.
5. **Archival policy.** No rule yet for when a source page gets moved from active to archive, or when a `raw/` file gets pushed to `archive/`. Decide after 6 months of use.

## What to work on next (priority order)

These are only guesses — the user will steer. Treat as a menu, not a queue.

### 1. Actually use the template personally (Bom does this)

The single most important next step. Nothing else should ship until the schema survives ~2 weeks of real personal use and at least 10 ingested sources across at least 2 different content types.

Things to watch for during use:
- Does the page skeleton feel too heavy or too thin?
- Are the three page types (sources / concepts / entities) enough, or does the user want a fourth (e.g. "projects" or "decisions")?
- Does the Query operation produce useful cross-links or does it just quote pages verbatim?
- Does the Lint operation catch real problems or just bikeshed formatting?
- Is the video ingest workflow actually used, or does the user skip it and paste transcripts manually?

Update `CLAUDE.md` and the example pages based on what you learn.

### 2. Ingest a few real sources and do a first lint pass

Replace (or keep + add to) the example pages with real content from whatever the user is actually researching. The example pages are illustrative but synthetic; real content will stress-test the schema in ways examples can't.

### 3. Decide whether Obsidian is actually the right UI

The template assumes Obsidian. If the user ends up editing everything in their LLM agent and never opens Obsidian, reconsider — maybe the UI is just the LLM agent itself and `README.md` should stop promising Dataview. Only remove Obsidian-specific conventions after deliberate discussion with the user.

### 4. Pick a first connected tool (if any)

The Connected tools registry in `CLAUDE.md` is empty by design. At some point the user will add their first entry — whatever MCP or integration they try first. Don't proactively add entries; wait for the user to tell you what they want to connect.

### 5. Slack bot (when the schema is stable)

When the user is happy with the schema and wants to share with a team, follow the phased rollout in `docs/slack-bot-architecture.md`. Build Phase 1 first (Query only), dogfood, then proceed. Don't skip phases.

## How to pick up this project in Claude Code

Run this from the project root:

```bash
cd llm-wiki-template
git status              # make sure you're on a clean state
git log --oneline -20   # scan recent history
```

Then tell Claude Code:

> "Read `CLAUDE.md` and `docs/HANDOFF.md` before doing anything. Summarise what the project is, what state it's in, and what's on the open-questions list. Then ask me what I want to work on."

Claude Code will read the schema, this handoff doc, and produce a grounded summary. From there, pick one item from the priority list above or bring your own.

## What Claude Code should NOT do on first contact

- Don't rewrite `CLAUDE.md`. It's been iterated on carefully. Propose edits, don't apply them silently.
- Don't delete the example pages without asking. The user may still be using them as references.
- Don't add `docs/` files proactively. The existing docs (`HANDOFF.md`, `operations/ingest.md`, `operations/prune.md`, `slack-mode.md`, `slack-bot-architecture.md`, `slack-bot-ux-patterns.md`) are sufficient until the user asks for more.
- Don't build the Slack bot without explicit go-ahead. The docs are planning material, not a build spec to execute unprompted.
- Don't wire any connected tools into `CLAUDE.md` without the user choosing which ones. The registry is deliberately empty.
- Don't reformat, re-lint, or "clean up" the example pages as a first action. Ask what the user wants.

## Files to read, in order, to get up to speed

1. `docs/HANDOFF.md` (this file) — context + state + decisions.
2. `CLAUDE.md` — the schema the LLM agent lives inside. Every session starts here. (~450 lines, core schema + operation summaries.)
3. `README.md` — human-facing overview. Useful to understand how a human would onboard.
4. `wiki/index.md` and `wiki/log.md` — see what the wiki actually contains and what's happened to it.
5. One example source page (`wiki/sources/2026-04-11-karpathy-llm-wiki.md`) — understand the page shape in practice.
6. `docs/operations/ingest.md` — only when doing a non-trivial Ingest (video, image, or first ingest of a new content type).
7. `CLAUDE-video-ingest.md` — only if the user is about to ingest a video.
8. `docs/operations/prune.md` — only when about to delete a page.
9. `docs/slack-mode.md` — only when running inside the Slack bot (activated by preamble).
10. `docs/slack-bot-architecture.md` and `docs/slack-bot-ux-patterns.md` — only when Slack bot work actually starts.

Total reading time for items 1–5 (always): ~15 minutes. Items 6–10 are on-demand. Do 1–5 before touching anything.

## Contact / ownership

- **Owner:** Bom (`parintorns@gmail.com`)
- **Status:** single-owner, personal experimentation phase
- **License:** unset — decide before sharing publicly

## Changelog of this handoff doc

- **2026-04-11** — initial handoff doc created. Template state: personal-use ready, Slack docs planned, no bot built yet.
- **2026-04-17** — qmd wired into Ingest/Query; Prune operation codified with soft + hard erase modes (see `wiki/log.md` schema entries).
- **2026-04-18** — template review pass. Added slash commands under `.claude/commands/`, Claude Code hooks under `.claude/hooks/` + `.claude/settings.json` (SessionStart context + PostToolUse qmd auto-update), fixed a Python-heredoc bug in `CLAUDE-video-ingest.md`, and split `CLAUDE.md` into a core file (~450 lines) + `docs/operations/ingest.md` + `docs/operations/prune.md` + `docs/slack-mode.md`.
