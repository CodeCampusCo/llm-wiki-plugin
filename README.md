# LLM Wiki — Starter Template

A ready-to-use template for building a personal LLM Wiki in the style proposed by Andrej Karpathy ([original gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)).

The pattern in one sentence: **an LLM agent incrementally builds and maintains a persistent, interlinked markdown wiki between you and your raw source documents, so knowledge compounds instead of being re-derived on every query.**

## What's in this template

```
llm-wiki-template/
├── CLAUDE.md                                # main schema — read by your LLM agent every session
├── CLAUDE-video-ingest.md                   # playbook for ingesting videos (yt-dlp + ffmpeg + whisper)
├── README.md                                # this file
├── .gitignore
│
├── wiki/                                    # TIER 1 — Git (synced via GitHub)
│   ├── index.md
│   ├── log.md
│   ├── sources/
│   │   └── 2026-04-11-karpathy-llm-wiki.md  # example text source
│   ├── concepts/
│   │   ├── llm-wiki-pattern.md
│   │   ├── rag.md
│   │   └── memex.md
│   └── entities/
│       ├── andrej-karpathy.md
│       ├── obsidian.md
│       └── qmd.md
│
├── raw/                                     # TIER 2 — Cloud drive (Dropbox/iCloud), NOT in git
│   ├── articles/                            # Web Clipper output
│   ├── images/                              # standalone images
│   ├── pdfs/                                # papers, reports
│   └── derived/                             # transcripts + keyframes extracted from video/audio
│       └── {video-slug}/
│
└── archive/                                 # TIER 3 — External drive or cloud bucket, usually NOT synced
    ├── videos/                              # raw .mp4/.mov — too big for Dropbox/git
    └── audio/
```

Everything in `wiki/` is seeded with example pages derived from Karpathy's gist plus one example video source page. You can keep them as a working reference, or delete and start from a clean slate — the `CLAUDE.md` + `CLAUDE-video-ingest.md` schema files are the only ones you really need to carry over.

## The 3-tier storage model

Not every file in a knowledge base wants to live in the same place. Text and binary files have very different needs, and so does your access pattern across devices. This template uses three tiers:

| Tier | Where | Sync everywhere? | In git? | What lives here |
|---|---|---|---|---|
| **1. `wiki/`** | GitHub private repo | Yes | **Yes** | Markdown only. Tiny, diff-friendly. The LLM-owned codebase. |
| **2. `raw/`** | Dropbox / iCloud / OneDrive | Yes | **No** | Articles, images, PDFs, transcripts, video keyframes. All your curated source material plus LLM-derived artifacts. |
| **3. `archive/`** | External SSD or S3/R2/B2 bucket | Optional | **No** | Raw videos and audio. Usually only on your main machine. |

Why three tiers?

- Git is incredible for text, terrible for binaries. Keeping `wiki/` text-only means your repo stays small forever — even after years of use.
- Dropbox is incredible for binaries, fine for text. It handles images and transcripts without bloating history, and syncs seamlessly to mobile.
- Videos are in a league of their own — a 1-hour 4K video can be several GB. Forcing them into Dropbox eats your quota; forcing them into git breaks the repo. They belong on external storage you only access when you actually need to rewatch them.

**Key insight:** the LLM never reads raw video. During ingest it extracts a transcript and keyframes into `raw/derived/{slug}/`, and from then on it treats those artifacts like any other text source. You can throw the raw video away after processing if you want — the wiki is unaffected.

## Prerequisites

### Required

- **A markdown editor** — [Obsidian](https://obsidian.md) recommended. Any editor works (VS Code, Typora, Logseq) but you lose the graph view and wikilink autocomplete.
- **An LLM agent with file access** — Claude Code, Codex, OpenCode, Cursor. For Codex, copy or symlink `CLAUDE.md` to `AGENTS.md`.
- **git** — version control for `wiki/`.
- **A cloud drive** (for Tier 2) — Dropbox, iCloud Drive, Google Drive, OneDrive, or Syncthing for peer-to-peer.

### Required only if you ingest video/audio

- **[`yt-dlp`](https://github.com/yt-dlp/yt-dlp)** — download video + captions from YouTube, Vimeo, Facebook, etc.
- **[`ffmpeg`](https://ffmpeg.org)** — extract keyframes, convert formats, strip audio.
- **[`whisper.cpp`](https://github.com/ggerganov/whisper.cpp)** or OpenAI's `whisper` — transcribe audio to text. `whisper.cpp` runs locally and is free.
- **(Optional)** [`scenedetect`](https://github.com/Breakingwind/PySceneDetect) for smarter keyframe extraction.

Install all of them on macOS with:

```bash
brew install yt-dlp ffmpeg whisper-cpp
```

On Linux (Debian/Ubuntu):

```bash
sudo apt install ffmpeg
pipx install yt-dlp
# whisper.cpp: build from source — see its README
```

### Required only if you want to use qmd search (for large wikis)

- **[`qmd`](https://github.com/qmd/qmd)** — local markdown search engine recommended by Karpathy's gist. Only needed once `wiki/index.md` stops scaling (~100+ sources).

## Quick start

### 1. Set up the three tiers

Pick where each tier lives:

```bash
# Tier 1: wiki in a git-tracked folder
mkdir -p ~/llm-wiki
cd ~/llm-wiki
# (you'll clone/copy this template into ~/llm-wiki/ in a moment)

# Tier 2: raw/ lives in Dropbox (or iCloud, etc.)
mkdir -p ~/Dropbox/llm-wiki-raw/{articles,images,pdfs,derived}

# Tier 3: archive/ lives on an external drive (or skip entirely)
mkdir -p /Volumes/ExternalSSD/llm-wiki-archive/{videos,audio}
```

Copy this template into `~/llm-wiki/`, then replace the real `raw/` and `archive/` folders with symlinks:

```bash
cp -r llm-wiki-template/. ~/llm-wiki/
cd ~/llm-wiki

# Move template's example raw/archive contents into real locations
rsync -av raw/ ~/Dropbox/llm-wiki-raw/
rm -rf raw archive

# Replace with symlinks
ln -s ~/Dropbox/llm-wiki-raw raw
ln -s /Volumes/ExternalSSD/llm-wiki-archive archive
```

The LLM agent, Obsidian, and git all see a single `~/llm-wiki/` folder — the symlinks are transparent to them.

### 2. Initialize git (Tier 1 only)

```bash
cd ~/llm-wiki
git init
git add .
git commit -m "Initialize LLM Wiki from template"

# Create a private repo on GitHub (via web or `gh repo create`)
git remote add origin git@github.com:yourname/my-llm-wiki.git
git push -u origin main
```

The `.gitignore` already excludes `raw/` and `archive/`, so binary files never enter git history.

### 3. Open the folder in Obsidian

`Open folder as vault` → point at `~/llm-wiki/`. Obsidian will index the markdown and wikilinks. Recommended plugins:

- **Dataview** — queries YAML frontmatter
- **Obsidian Web Clipper** (browser extension) — send articles straight into `raw/articles/`
- **Obsidian Git** — auto-commit and push on a schedule so you never forget
- **Marp** — generate slide decks from wiki pages

Then in Obsidian: Settings → Files and links → **Attachment folder path** → `raw/images`. Bind a hotkey to "Download attachments for current file" so clipped articles pull their images locally in one keystroke.

### 4. Point your LLM agent at the folder

Start Claude Code / Codex / OpenCode from `~/llm-wiki/`. On first session it'll read `CLAUDE.md` and understand the conventions.

### 5. Ingest your first source

Drop a file into `raw/articles/` (or paste a URL in chat) and say:

> Please ingest `raw/articles/my-first-article.md` into the wiki.

For a video:

> Please ingest this YouTube video: https://www.youtube.com/watch?v=...

The agent will follow the video workflow in `CLAUDE-video-ingest.md`: download with yt-dlp, extract a transcript with captions or Whisper, pull keyframes with ffmpeg, and create a wiki page that embeds the keyframes and cites quotes with timestamps.

## Syncing to other machines

### Laptop / desktop (full access)

```bash
# Clone the wiki repo
git clone git@github.com:yourname/my-llm-wiki.git ~/llm-wiki

# Symlink the Tier 2 folder (Dropbox handles the actual sync)
ln -s ~/Dropbox/llm-wiki-raw ~/llm-wiki/raw

# Symlink Tier 3 only if this machine has the external drive
ln -s /Volumes/ExternalSSD/llm-wiki-archive ~/llm-wiki/archive
# If not, just leave archive/ missing — the LLM will check before touching it
```

Day-to-day: `git pull` before starting work, `git add . && git commit && git push` when done (or let Obsidian Git automate this).

### Mobile (read-only browsing)

Obsidian Mobile + Dropbox/iCloud works great. You'll see:

- Full wiki markdown (synced via Dropbox if you've put the whole repo there, or via Obsidian Sync)
- All images, PDFs, article clippings, video transcripts, and video keyframes
- **Not** raw video files (they live in Tier 3)

This means on your phone you can still read the transcript and view keyframes of any ingested video, without the video itself ever touching your device.

### Headless server (for scheduled ingests)

If you want a cron job to auto-ingest RSS feeds, YouTube channels, or podcasts: run the agent on a Linux server, symlink `raw/` to a mounted cloud drive, and let git handle `wiki/`.

## Extending with connected tools (MCP, plugins, native integrations)

If your LLM agent has connected tools — Model Context Protocol servers, plugins, or built-in integrations — the wiki extends in three directions:

- **External → Wiki (Ingest):** pull live data (meeting transcripts, chat threads, emails, docs, tickets) directly into the wiki through the standard Ingest flow. The wiki becomes a memory layer on top of your live systems.
- **Wiki → External (Act):** use wiki content as input to produce external side effects — drafting an email, creating a ticket, posting a message, updating a record. `CLAUDE.md` includes a dedicated **Act operation** with mandatory human-in-the-loop approval.
- **Cross-reference:** answer questions that span wiki and live data in a single query — e.g. "which open tickets relate to the roadmap on `concepts/product-roadmap`?"

The template is **tool-agnostic**. It doesn't assume any particular MCP, plugin, or vendor. To wire in the tools you actually use, edit the `## Connected tools` section inside `CLAUDE.md` and add one entry per tool using the template provided there. Each entry tells the LLM:

- What data or actions the tool accesses
- When to use it during Ingest / Query / Act
- What NOT to use it for
- Any privacy considerations (especially important if your wiki is pushed to a shared git remote)

This way the same template works for anyone — a researcher with only web search and a PDF reader, a sales team with CRM and email, an engineer with ticket systems and code search — without the schema being tied to one stack.

**Safety defaults baked into the schema:**

- Act operations always draft-and-approve before executing. No silent side effects.
- No bulk ingest from connected tools — the wiki is a synthesis, not a dump.
- Auth errors stop the operation immediately; no workarounds.
- Sensitive data is summarized, not quoted verbatim, when being committed to a shared remote.

## Customizing the schema

`CLAUDE.md` and `CLAUDE-video-ingest.md` are not sacred. They're living documents you co-evolve with your agent. As your domain-specific needs emerge, add:

- New page types (e.g. `wiki/comparisons/`, `wiki/questions/`, `wiki/timelines/`)
- New frontmatter fields
- Domain-specific workflows (e.g. "when ingesting a legal contract, also flag every clause that references a jurisdiction")
- Tool-specific tricks (e.g. "for academic papers, always run `pdftotext` and save to `raw/derived/{slug}/text.md`")

Ask your agent to propose schema updates when it notices a pattern. Commit the updated schema alongside the wiki changes that motivated it.

## When the template stops fitting

Signals that you're outgrowing `index.md`-only retrieval:

- The index is >500 lines and the agent spends a lot of context just reading it
- You have ~100+ source pages
- Queries regularly need pages the agent didn't guess to open from the index

That's when the gist recommends introducing [qmd](https://github.com/qmd/qmd) — either as a CLI the agent shells out to, or as an MCP server.

Signals that you're outgrowing Dropbox for Tier 2:

- Dropbox quota full
- Sync is slow on slow connections
- You want team access with per-user permissions

Consider moving `raw/` to a self-hosted WebDAV or S3-compatible bucket mounted with `rclone`.

## Where this template came from

Based on Andrej Karpathy's gist "LLM Wiki" (April 2026): <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

The example pages in `wiki/` are derived from that same gist plus the video workflow extension — making the template self-documenting. Your first wiki already contains a wiki about the wiki pattern.
