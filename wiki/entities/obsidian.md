---
title: "Obsidian"
type: entity
entity_kind: tool
tags: [tool, markdown, note-taking]
created: 2026-04-11
updated: 2026-04-11
homepage: "https://obsidian.md"
---

# Obsidian

> TL;DR: A local-first markdown editor with bidirectional wikilinks, a graph view, and a rich plugin ecosystem. In the [[concepts/llm-wiki-pattern]], Obsidian plays the role of "IDE" — the human's window into the LLM-maintained wiki.

## Overview

Obsidian stores notes as plain markdown files in a folder (a "vault"). This makes it a natural fit for the LLM Wiki pattern: the LLM can read and write the same files directly, while the human browses them through Obsidian's UI in real time.

## Role in the LLM Wiki workflow

Per [[sources/2026-04-11-karpathy-llm-wiki]], the recommended loop is: LLM agent open on one side, Obsidian open on the other. The LLM makes edits based on conversation; the human browses the results — following links, checking the graph view, reading updated pages.

Useful features for this pattern:

- **Wikilinks** — `[[page-name]]` syntax that the LLM uses for all cross-references.
- **Graph view** — visualizes the shape of the wiki; makes orphan pages and hub pages immediately visible.
- **Web Clipper** — browser extension that converts web articles to markdown. Primary way to get sources into `raw/`.
- **Attachment download hotkey** — bind "Download attachments for current file" to a hotkey; after clipping an article, one keystroke pulls all images down to local disk so the LLM can view them.
- **Dataview plugin** — queries YAML frontmatter across pages. If your pages have `type: concept`, `status: stub`, etc., Dataview can generate dynamic tables ("all stub concept pages sorted by date").
- **Marp plugin** — markdown-based slide decks. Lets the LLM generate presentations directly from wiki content as a query output format.

## Key facts

- Local-first; no account required; free for personal use.
- Vault is just a folder of markdown — fully portable, git-friendly.
- Runs on macOS, Windows, Linux, iOS, Android.

## Appearances in the wiki

- [[sources/2026-04-11-karpathy-llm-wiki]] — recommended as the wiki "IDE."
- [[concepts/llm-wiki-pattern]] — Obsidian's role in the human's side of the loop.

## See also

- [[entities/qmd]] — search tool recommended when index.md stops scaling
- [[concepts/llm-wiki-pattern]]
