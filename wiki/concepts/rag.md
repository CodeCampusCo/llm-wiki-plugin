---
title: "RAG (Retrieval-Augmented Generation)"
type: concept
tags: [pattern, llm, retrieval]
created: 2026-04-11
updated: 2026-04-11
status: stub
sources: ["[[sources/2026-04-11-karpathy-llm-wiki]]"]
related: ["[[concepts/llm-wiki-pattern]]"]
---

# RAG (Retrieval-Augmented Generation)

> TL;DR: A pattern where an LLM fetches relevant chunks from a corpus at query time, stuffs them into its context, and generates an answer. It is the baseline approach behind NotebookLM, ChatGPT file uploads, and most production LLM-over-documents stacks.

## Definition

RAG pipelines generally share three steps:

1. **Ingest (index time).** Documents are split into chunks and converted into embeddings stored in a vector database. Optionally paired with keyword (BM25) indexes.
2. **Retrieve (query time).** A user query is embedded and used to fetch the top-k most similar chunks.
3. **Generate (query time).** The retrieved chunks are injected into the LLM's context along with the query, and the model writes the answer.

## Why it matters

RAG is the dominant pattern for grounding LLM responses in a document corpus. It is conceptually simple, scales to very large corpora, and does not require re-training the model.

## Contrast with [[concepts/llm-wiki-pattern]]

The [[sources/2026-04-11-karpathy-llm-wiki]] gist positions the LLM Wiki pattern explicitly against RAG on one axis: **when synthesis happens**.

| | RAG | LLM Wiki |
|---|---|---|
| When synthesis happens | Query time (re-derived each time) | Ingest time (compiled into persistent pages) |
| Accumulation across queries | None — each query starts from raw chunks | Strong — the wiki gets richer with every ingest and every good answer |
| Main artifact | A vector index over raw chunks | A git repo of interlinked markdown pages |
| Scales best at | Large corpora (millions of docs) | Small-to-moderate, frequently-revisited knowledge |
| Human-readable without LLM in the loop | No | Yes — wiki is just markdown |

Karpathy does not claim RAG is obsolete. The two are complementary: RAG remains the right tool for large-corpus, one-shot retrieval, while LLM Wiki suits personal and team knowledge bases where the same material is revisited and refined.

## Open questions / contradictions

- How do hybrid systems (RAG with LLM-maintained summaries as first-tier context) compare empirically to either pure approach? No sources yet.

## Sources

- [[sources/2026-04-11-karpathy-llm-wiki]] — mentioned in the context of contrasting RAG with the LLM Wiki pattern.

## See also

- [[concepts/llm-wiki-pattern]]
