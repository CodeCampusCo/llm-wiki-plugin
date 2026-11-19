LLM Wiki working rules (from the llm-wiki plugin; "Personal session rules" below, if any, are the user's own and win on conflict):
- When a task could be covered by the wiki (a runbook, convention or known gotcha), check it first: {search}. Pages the wiki-hint hook names in a prompt are a starting point, not the whole search.
- Treat wiki hits as background, not truth: they reflect when the page was written. Verify against the current code, ticket or system, and say when the wiki is out of date.
- Before the session ends, if it produced a reusable method (runbook, convention, gotcha, correction to a page), propose an ingest: list the pages to create or update, one line each. Reusable methods only, no task status or one-off decisions.
- If you read a wiki page the hook did not point to, propose adding the user's words for it to that page's `keywords`, quoting where the user typed each one.
- Never ingest, edit or commit to the wiki without the user's approval; then use /llm-wiki:ingest (or /llm-wiki:prune, /llm-wiki:lint).
