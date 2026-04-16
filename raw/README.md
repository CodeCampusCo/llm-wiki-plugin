# raw/ (Tier 2 — cloud drive)

This directory holds your **source of truth** — the curated source material you want the LLM to learn from, plus the derived artifacts it produces from video and audio.

## Important: this folder should live in your cloud drive

On a real machine, `raw/` is usually a **symlink** to a folder in Dropbox, iCloud Drive, OneDrive, or similar. It is **not** part of the git repo — the `.gitignore` excludes it. Binary files belong in tools built for binary sync, not in git.

See `README.md` in the template root for setup instructions.

## Subfolder conventions

```
raw/
├── articles/      # HTML/markdown clippings (Obsidian Web Clipper output)
├── images/        # standalone images referenced in wiki pages
├── pdfs/          # papers, reports, long-form documents
└── derived/       # LLM-produced artifacts from video, audio, and OCR
    └── {slug}/
        ├── transcript.md
        ├── keyframes/
        ├── metadata.json
        └── ocr.md         # (for image sources, if applicable)
```

## Rules

- **Read-only for the LLM** (mostly). The agent reads from `articles/`, `images/`, `pdfs/` but never modifies them. If you want a source changed or removed, you do it yourself.
- **`derived/` is write-once.** The LLM creates subfolders here during video/audio ingest. Once written, treat them as read-only — re-ingest the source if you need new artifacts.
- **Immutable by convention.** Don't edit files here after ingest. If the source material changes, re-ingest from scratch.

## Getting sources in

Common ways:

- **Obsidian Web Clipper** — one-click conversion of a web article into a markdown file → drop in `articles/`.
- **Drag and drop** — drop PDFs into `pdfs/`, images into `images/`.
- **Paste a URL into chat** — your LLM agent can fetch and save (you'll need a fetch tool enabled).
- **For video/audio:** just give the LLM a URL or local file path and say "ingest this" — it'll run the workflow in `CLAUDE-video-ingest.md`.

## Naming

Loose convention for articles, images, and PDFs: `YYYY-MM-DD-slug.ext` where the date is when you saved it (or when it was published, if known). For `derived/`, the slug must match the wiki source page slug exactly.
