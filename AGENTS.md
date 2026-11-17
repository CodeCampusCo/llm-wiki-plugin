# Developing the llm-wiki plugin (agent guide)

This repo is the Claude Code plugin `llm-wiki`, not a wiki. Read `CONTRIBUTING.md` for the release rules.

## Layout

- `.claude-plugin/` - `plugin.json` and `marketplace.json`.
- `hooks/hooks.json` - SessionStart, UserPromptSubmit (wiki hint), PostToolUse (post-wiki-edit).
- `scripts/` - stdlib-only Python behind the hooks and skills (`wikiconf`, `wiki_hint`, `post_wiki_edit`, `session_start`, `init_wiki`, `lint_wiki`, `keywords_report`).
- `skills/` - `init`, `ingest`, `query`, `lint`, `prune`, `act`.
- `schema/` - the wiki schema, operation playbooks and `CHANGELOG.md`.
- `skeleton/` - files copied into a new content repo by `init`.
- `tests/` - unit tests.

## Commands

```sh
python3 -m unittest discover -s tests
claude plugin validate --strict .
claude plugin validate --strict skills
```

## Rules

- The wiki schema lives in `schema/schema.md`, not here. This file is not shipped to users' wikis.
- Python stdlib only. Hooks must never fail a prompt or tool call: on any error print nothing and exit 0.
- No personal names, account names or content-repo names in tracked files (a test checks this). `.github/CODEOWNERS` is the one file allowed to hold an account handle.
- `LLM_WIKI_DIR` overrides the configured wiki location. It is a development and test override; do not document it for end users.
