---
description: Answer a question using the wiki
argument-hint: "<question>"
---

Run the **Query** operation defined in `CLAUDE.md` under `## Operation: Query`.

Question: $ARGUMENTS

Steps:

1. **Find candidate pages.**
   - If qmd is configured: use `mcp__plugin_qmd_qmd__query` with the question as `vec` (optionally add `lex` for known exact terms). Scope to the wiki collection.
   - Otherwise: read `wiki/index.md` and scan for candidates.
2. Drill down into the most relevant 3–7 pages. Follow wikilinks as needed.
3. Synthesize an answer. **Cite with wikilinks** (`according to [[concepts/rag]], ...`).
4. **Offer to file the answer** as a new wiki page if it's worth compounding (e.g. `wiki/comparisons/foo-vs-bar.md`). Don't file silently.
5. If relevant info is missing, say so clearly and suggest sources I could add.
6. Append to `wiki/log.md`: `## [YYYY-MM-DD] query | {question}` with one-line summary and any pages created.

Output format is flexible — prose, comparison table, slide deck, chart, canvas — pick what fits the question.
