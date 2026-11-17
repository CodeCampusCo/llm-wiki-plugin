# Contributing

## How changes land

1. Fork (or branch), make the change, and open a pull request against `master`.
2. CI must pass: the unit tests on Linux and macOS, and `claude plugin validate --strict` on the
   marketplace, plugin and skills.

## Working on it

```sh
python3 -m unittest discover -s tests
claude plugin validate --strict .
claude plugin validate --strict skills
claude --plugin-dir .
```

The last line starts a Claude Code session with the plugin from this folder instead of the installed one.

- Python standard library only. Hook scripts must never fail a prompt or tool call: any error prints
  nothing and exits 0.
- Add or update tests with any change to a script.
- Keep files under 300 lines and functions under 50 lines.
- No personal names, account names or content-repo names in tracked files; `tests/test_schema.py` checks this.
  `.github/CODEOWNERS` is the one file allowed to hold an account handle.
- `LLM_WIKI_DIR` overrides the configured wiki location. It is a development and test override, handy for
  pointing the scripts at a temp wiki; tests must also use temp dirs, never your real wiki or plugin data dir.

## Releases

- `plugin.json` sets `version`. While it is set, installed copies stay on that version until it changes,
  so **bump `version` in `.claude-plugin/plugin.json` for every release** that should reach users.
- When the page format of a wiki changes, add an entry to `schema/CHANGELOG.md` and bump
  `SCHEMA_VERSION` in `scripts/wikiconf.py`.

## Commits

Conventional commits in English (`feat(scope): ...`, `fix(scope): ...`, `docs: ...`).
