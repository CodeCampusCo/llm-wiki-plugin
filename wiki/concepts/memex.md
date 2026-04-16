---
title: "Memex"
type: concept
tags: [history, knowledge-management, hypertext]
created: 2026-04-11
updated: 2026-04-11
status: stub
sources: ["[[sources/2026-04-11-karpathy-llm-wiki]]"]
related: ["[[concepts/llm-wiki-pattern]]"]
---

# Memex

> TL;DR: Vannevar Bush's 1945 proposal for a personal, curated knowledge store in which documents are connected by associative trails built by the user. Bush's vision was closer to a private, actively-curated wiki than to the public web that eventually emerged, and it is cited as a conceptual ancestor of the [[concepts/llm-wiki-pattern]].

## Definition

The Memex (from "memory extender") was a thought experiment described by Vannevar Bush in his 1945 essay "As We May Think." It imagined a desk-sized device that would store a person's books, records, and communications on microfilm and let the user link items together along associative trails — precursor to what later became hypertext.

## Why it matters here

The [[sources/2026-04-11-karpathy-llm-wiki]] gist explicitly frames the LLM Wiki pattern as a descendant of Bush's Memex idea. The relevant quote:

> "The idea is related in spirit to Vannevar Bush's Memex (1945) — a personal, curated knowledge store with associative trails between documents. Bush's vision was closer to this than to what the web became: private, actively curated, with the connections between documents as valuable as the documents themselves. The part he couldn't solve was who does the maintenance. The LLM handles that."

The key insight: Bush identified the right goal (a personal, associatively-linked knowledge store) and the right friction (maintenance is too expensive for humans). LLMs finally make the maintenance cost low enough for the vision to be practical at individual scale.

## Open questions / contradictions

- What other pre-LLM attempts at a personal knowledge management tool failed for maintenance-cost reasons? (Xanadu, early wiki software, etc.) Worth sourcing.

## Sources

- [[sources/2026-04-11-karpathy-llm-wiki]] — cites Memex as a historical precedent.

## See also

- [[concepts/llm-wiki-pattern]]
