---
name: init
description: Use to set up the LLM Wiki plugin - create a new wiki content repo or attach an existing one. Triggers - "set up llm wiki", "init wiki", "/llm-wiki:init".
argument-hint: "[--existing]"
---

# Init LLM Wiki

Creates a new wiki content repo, or attaches one that already exists, and records where it lives.

Take `<plugin_root>` and `<data_dir>` from this session's context: the lines that start
`Plugin root:` and `Plugin data dir:`. Every command below is:

```sh
python3 "<plugin_root>/scripts/init_wiki.py" "<data_dir>" <subcommand> ...
```

Always quote paths in shell commands (they may contain spaces).

The script exits 2 with a message when it refuses (non-empty target, missing or corrupt
`.llm-wiki.json`). Report that message and stop; never work around it.

If `$ARGUMENTS` contains `--existing`, follow "Existing wiki". Otherwise follow "New wiki".

## Existing wiki

1. Ask for the path to the wiki folder.
2. Run `... existing --wiki-dir <path>`.
3. Register qmd (see "qmd" below), unless `.llm-wiki.json` already has a `qmd_collection` (then skip asking). Then run `... existing --wiki-dir <path> --qmd-collection <name>`.
4. Print the snippet (see "Snippet").

## New wiki

1. Ask for the wiki path (default `~/llm-wiki`).
2. Ask for the raw path (default `<wiki>/raw`). A cloud-drive folder is a good choice; it is not tracked in git.
3. Run `... new --wiki-dir <wiki> --raw-dir <raw>`. Optional: `--archive-dir <path>`.
4. The new wiki has no commits yet. Show the user the files (`git -C "<wiki>" status --short`) and ask approval
   for the initial commit `chore: initialize wiki from llm-wiki skeleton`; commit only after a yes.
5. Ask for the repo name (default: basename of the wiki dir). Only after an approved commit, offer (and run only after
   a yes): `gh repo create <name> --private --source "<wiki>" --push`. If the user declined the commit, offer
   `gh repo create <name> --private` without `--source` or `--push`.
   If the user asks for a public repo, warn loudly that wiki content becomes world-readable and get explicit confirmation.
6. Register qmd (see "qmd").
7. Print the snippet (see "Snippet").

## qmd

Only if `qmd` is installed (`command -v qmd`).

1. Ask for the collection name (default: basename of the wiki dir).
2. Run `qmd collection add "<wiki>/wiki" --name "<collection>"` (syntax from `qmd skill show`: `qmd collection add "<path>" --name "<name>"`). Index the `wiki/` folder only, not the repo root.
3. Record it: `... existing --wiki-dir <wiki> --qmd-collection <collection>`.

## Snippet

Run `... snippet`, show the output, and tell the user to paste it into their own
`~/.claude/CLAUDE.md`. Never edit that file yourself.
