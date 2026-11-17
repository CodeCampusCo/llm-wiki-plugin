# LLM Wiki

A Claude Code plugin for keeping a personal LLM Wiki in the style proposed by Andrej Karpathy ([original gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)).

The pattern in one sentence: **an LLM agent incrementally builds and maintains a persistent, interlinked markdown wiki between you and your raw source documents, so knowledge compounds instead of being re-derived on every query.**

The plugin ships the schema, the skills and the hooks. Your wiki itself lives in a separate content repo that you own.

## What the plugin gives you

- **Skills:** `/llm-wiki:init`, `/llm-wiki:ingest`, `/llm-wiki:query`, `/llm-wiki:lint`, `/llm-wiki:prune`, `/llm-wiki:act`.
- **Hooks:**
  - `SessionStart` tells the session where your wiki is (or to run `/llm-wiki:init` if none is set up).
  - `UserPromptSubmit` (wiki hint) matches your prompt against the `keywords` in page frontmatter and points at up to 3 matching pages.
  - `PostToolUse` (post-wiki-edit) refreshes the qmd index (`qmd update`) only when the edited file is inside the wiki and the wiki has a qmd collection.
- **Schema:** `schema/schema.md` plus operation playbooks (ingest incl. video, prune), versioned in `schema/CHANGELOG.md`.

## Install

```
/plugin marketplace add CodeCampusCo/llm-wiki-plugin
/plugin install llm-wiki@llm-wiki
/llm-wiki:init
```

`/llm-wiki:init` asks where the wiki folder goes (default `~/llm-wiki`), where `raw/` lives, and optionally the GitHub repo name and the qmd collection name. Nothing is hardcoded: the defaults are only defaults.

### Second machine

Install the plugin as above, clone your own content repo, then attach it:

```
/llm-wiki:init --existing
```

### Update

```
/plugin marketplace update llm-wiki
```

In a shell: `claude plugin marketplace update`. Third-party marketplaces do not auto-update by default; enable `autoUpdate` for this one via `/plugin` > Marketplaces (see the Claude Code plugin docs for the current UI).

## The content repo

`init` creates this layout in the folder you pick:

```
<wiki folder>/
├── wiki/
│   ├── concepts/
│   ├── entities/
│   ├── sources/
│   ├── index.md          # catalog of all pages
│   └── log.md            # append-only operation log
├── CONVENTIONS.md        # your personal rules and connected-tools registry, read after the plugin schema
├── .llm-wiki.json        # schema version, raw/archive paths, qmd collection
├── .obsidian/            # optional Obsidian settings
└── .gitignore
```

`raw/` (default `<wiki>/raw`, git-ignored, set by `raw_dir` in `.llm-wiki.json`) holds tier-2 sources.

It is a git repo from the start. Open the folder as an Obsidian vault if you like; any markdown editor works.

## Privacy: keep the content repo private

A wiki collects notes, quotes and source material that may be personal or confidential. Keep the content repo private.

- `init` offers `gh repo create <name> --private` and warns loudly if you ask for a public repo.
- `/llm-wiki:lint` flags things that look like secrets or email addresses in wiki pages.

## The 3-tier storage model

Text and binary files have different needs, so the wiki spreads over three tiers:

| Tier | Where | In git? | What lives here |
|---|---|---|---|
| **1. `wiki/`** | Your private GitHub repo | **Yes** | Markdown only. Small and diff-friendly. Owned by the LLM. |
| **2. `raw/`** | Dropbox / iCloud / OneDrive (a path you choose) | **No** | Articles, images, PDFs, transcripts, video keyframes: your curated sources plus derived artifacts. |
| **3. `archive/`** | External SSD or an S3/R2/B2 bucket | **No** | Raw video and audio. Usually only on your main machine. |

- Git is great for text and bad for binaries; keeping `wiki/` text-only keeps the repo small for years.
- Cloud drives handle images and transcripts well and sync to mobile.
- Videos can be several GB each; they belong on external storage you touch only when you need to rewatch them.

The LLM never reads raw video. During ingest it extracts a transcript and keyframes into `raw/derived/{slug}/` and treats those like any other text source. The raw video can be discarded afterwards.

## Prerequisites

### Required

- [Claude Code](https://code.claude.com) with plugin support.
- `python3` (the hooks and scripts use the standard library only).
- `git`.

### Optional

- [Obsidian](https://obsidian.md) for graph view and wikilink autocomplete.
- [`gh`](https://cli.github.com) if you want `init` to create the GitHub repo.

### Only if you ingest video or audio

- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) to download video and captions.
- [`ffmpeg`](https://ffmpeg.org) to extract keyframes and audio.
- [`whisper.cpp`](https://github.com/ggerganov/whisper.cpp) or OpenAI's `whisper` to transcribe.

On macOS: `brew install yt-dlp ffmpeg whisper-cpp`. On Debian/Ubuntu: `sudo apt install ffmpeg`, `pipx install yt-dlp`, and build whisper.cpp from source.

### Only if you want qmd search (large wikis)

- [`qmd`](https://github.com/tobi/qmd), a local markdown search engine mentioned in Karpathy's gist. It becomes useful once `wiki/index.md` stops scaling (roughly 100+ sources). `init` registers the `wiki/` folder as a qmd collection under the name you choose. Check the qmd documentation for installation and current syntax.

## Repo layout (the plugin)

```
.claude-plugin/   plugin.json, marketplace.json
hooks/hooks.json  SessionStart, UserPromptSubmit, PostToolUse
scripts/          wikiconf, wiki_hint, post_wiki_edit, session_start, init_wiki, lint_wiki, keywords_report
skills/           init, ingest, query, lint, prune, act
schema/           schema.md, operations/, CHANGELOG.md
skeleton/         files copied into a new content repo
tests/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) to work on the plugin.

## Credit

Based on Andrej Karpathy's gist "LLM Wiki" (April 2026): <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

## License

[MIT](LICENSE)
