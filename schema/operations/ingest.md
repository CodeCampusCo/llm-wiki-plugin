# Operation: Ingest — full workflow

> High-level contract is in `schema/schema.md` under `## Operation: Ingest`. This file has the detailed workflow including video and image sub-operations.

When the user says "ingest this" or drops a new file into `raw/`, follow this workflow. The steps below apply to **text-based sources** (articles, papers, markdown notes). For **video, audio, or image-heavy sources**, first run the preprocessing flow in the sub-operations below, then return here at step 1 treating the derived artifact as the source.

1. **Read the source in full.** For long documents, read section by section rather than skimming.
2. **Discuss with the user** before writing anything. Summarize what the source contains, what seems important, and ask: "What angle are you reading this from? Anything you want me to emphasize?" This is cheap and prevents wasted work.
3. **Create the source page** in `wiki/sources/YYYY-MM-DD-slug.md` using the source skeleton. Include a TL;DR, key points, and notable quotes with locations.
4. **Identify affected pages.** Walk `wiki/index.md` and list every existing page this source touches. Also identify new concepts or entities that deserve their own page.
5. **Propose changes** before making them. Say: "I'll create `concepts/foo`, update `entities/bar` (adding a new role), and flag a contradiction in `concepts/baz`. OK to proceed?"
6. **Make the edits.** A single ingest commonly touches 10–15 pages. That's normal and correct. A new concept/entity page gets `keywords` (see "Page conventions" in `schema/schema.md`); when an edit adds a topic to an existing page, add the words the user used for it in this session. List the keywords in the step 5 proposal, each with where the user used it.
7. **Update `wiki/index.md`** — add new pages to their category, update one-line summaries if any changed.
8. **Append to `wiki/log.md`** with a consistent prefix: `## [YYYY-MM-DD] ingest | {source title}` followed by a short bulleted list of what changed.
9. **Refresh the search index.** If qmd is configured for this wiki (see "Search (qmd)" in `schema/schema.md`), run `qmd update` so the new/changed pages become searchable. Skip if qmd is not configured.
10. **Report back** — tell the user how many pages changed, surface anything interesting you found, and suggest follow-up sources to look for.

Rule: **never** rewrite large chunks of an existing page silently. If you're replacing more than a paragraph, say so first.

---

## Sub-operation: Video ingestion

Videos are never read directly. You work with derived artifacts — transcript and keyframes — which are produced once and then reused like any other text source. Full step-by-step commands live in `schema/operations/video-ingest.md`; this section is the high-level contract.

**Before any ingest step runs:**

1. **Confirm disk tier.** Ask where the user wants the raw video to live: `archive/videos/` (if they want to keep the raw file) or nowhere (derived artifacts only, raw video discarded after processing). Default to "derived only" unless the user says otherwise — it saves space.
2. **Check tool availability.** `which yt-dlp ffmpeg whisper` — if anything is missing, tell the user and stop.
3. **Pick a slug.** `YYYY-MM-DD-short-kebab-case` based on title. This slug is used for `raw/derived/{slug}/` and `wiki/sources/{slug}.md`.

**Preprocessing steps (produce derived artifacts):**

4. **Download** — use `yt-dlp` to fetch the video and any available captions. If captions exist and look clean, prefer them; skip Whisper.
5. **Transcribe** — if no captions, run Whisper (`whisper.cpp` for local, OpenAI API for cloud). Save to `raw/derived/{slug}/transcript.md` with `mm:ss` timestamps every few lines. Record `transcript_source` in the metadata.
6. **Extract keyframes** — `ffmpeg` at fixed interval (default: every 30 seconds) OR use scene detection for better coverage. Save as `raw/derived/{slug}/keyframes/HH-MM-SS.jpg`.
7. **Write metadata** — `raw/derived/{slug}/metadata.json` with: `url`, `title`, `author`, `duration`, `published_date`, `ingest_date`, `transcript_source`, `language`.
8. **Move or delete the raw video** — based on step 1 decision.

**Main ingest steps (produce the wiki page):**

9. **Read the transcript in full.** Treat it like a long article. If the transcript is auto-generated, note uncertainty — auto captions often mangle names, technical terms, and proper nouns. Cross-check suspicious words against keyframes when possible.
10. **View 3–5 keyframes** to anchor the content visually. Prioritize: title slide, diagrams, chapter transitions, anything the transcript references directly ("as you can see in this chart").
11. **Discuss with the user** — summarize what the video covers and ask for angle/emphasis.
12. **Create the source page** using the video source skeleton below.
13. **Continue with steps 4–9 of the standard Ingest operation.**

**Video source page skeleton:**

```markdown
---
title: "Video title"
type: source
source_kind: video
video_url: "https://..."
video_duration: "12:34"
transcript_path: "raw/derived/{slug}/transcript.md"
transcript_source: whisper | youtube-auto | manual
keyframes_dir: "raw/derived/{slug}/keyframes/"
has_raw_archive: false
language: th
tags: [...]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# {Video title}

> TL;DR: 2-4 sentences.

> ⚠️ Transcript source: {whisper | youtube-auto | manual}. Auto-generated captions may mistranscribe names and technical terms.

## Key points

- ...

## Notable quotes

> "Quoted text." — [[raw/derived/{slug}/transcript.md#02-15|02:15]]

## Visual references

![Chart showing X | 04:30](../../raw/derived/{slug}/keyframes/00-04-30.jpg)

Embed 3-8 keyframes total, never more. Each with a caption and timestamp.

## My reading

...

## Updates to the wiki

- ...

## See also

- [[concepts/...]]
```

**Quote convention for timed media:** Always include `mm:ss` or `hh:mm:ss` after the quote, wikilinked to the transcript when possible.

**What you do NOT do with video:**

- Never embed more than 8 keyframes per page — wiki pages should stay scannable.
- Never quote from auto-captions without flagging uncertainty.
- Never assume a raw video in `archive/videos/` is present on the current machine — check with `test -f` first.
- Never put `.mp4`/`.mov`/`.webm` files under `wiki/` or anywhere inside the git repo.

---

## Sub-operation: Image ingestion

For standalone images (screenshots, diagrams, photos):

1. **Save the raw image** to `raw/images/YYYY-MM-DD-slug.ext`.
2. **View the image** — describe what you see in prose, not just metadata.
3. **(Optional) OCR** — if the image contains text that matters (slides, screenshots of documents, handwritten notes), run OCR and save to `raw/derived/{slug}/ocr.md`.
4. **Create a source page** only if the image is substantive enough to warrant one. For casual screenshots, just embed the image in an existing wiki page instead.
5. **Continue with the standard Ingest flow.**
