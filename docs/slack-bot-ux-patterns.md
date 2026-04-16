# Slack bot integration — UX patterns

> **Status:** planning doc — not yet implemented.
> This is the "what does it feel like to use" companion to `slack-bot-architecture.md`. It lists the five interaction patterns the bot should support and gives concrete, copy-pasteable Slack message templates for each. Design the bot to hit these exact shapes — if the UX deviates, push back on the implementation, not the doc.

## Design principles

1. **Threads by default.** Never clutter a channel with long bot replies. The bot posts a one-line summary in-channel and the full content in a thread reply.
2. **Cite or shut up.** Every factual claim links back to a wiki page. Links are GitHub blob URLs so non-technical users can click straight through.
3. **Reactions as verbs.** Use emoji reactions (✅ ❌ 👀) as approval affordances — they're faster than buttons and work on mobile.
4. **Short by default, long on request.** Phase-1 replies fit on one phone screen. If the user wants the full version they ask "more" or "expand."
5. **The bot speaks like a librarian, not a chatbot.** Neutral, precise, no filler phrases. Never apologises for having a wiki. Never adds "let me know if you need anything else!"
6. **Silent on uncertainty.** If the wiki doesn't have an answer, the bot says so and offers to ingest something. It does not guess.

## Pattern 1 — Query via @mention in channel

### When to use

Someone is in a channel discussion and wants a fact from the wiki without leaving the conversation.

### Trigger

```
@wiki how does our team think about LLM Wiki vs RAG?
```

### Expected behaviour

1. Bot acks with an eyes emoji reaction on the original message within 1 second.
2. Bot replies in a thread (not the channel) within ~10 seconds.
3. Reply is <200 words, has at least one citation.

### Response template

```
*LLM Wiki vs RAG* — from `concepts/llm-wiki-pattern` and `concepts/rag`:

LLM Wiki pre-compiles knowledge into a persistent markdown artifact that the
LLM reads each session. RAG retrieves chunks on every query. They're
complementary at different scales — LLM Wiki works well up to ~hundreds of
sources, RAG scales beyond that.

Sources:
• <https://github.com/ORG/llm-wiki/blob/main/wiki/concepts/llm-wiki-pattern.md|concepts/llm-wiki-pattern>
• <https://github.com/ORG/llm-wiki/blob/main/wiki/concepts/rag.md|concepts/rag>

_Want the longer version? Reply `expand`._
```

### Error case — no matching page

```
I don't have a page on that yet.

Closest matches in the wiki:
• <…|concepts/llm-wiki-pattern> — mentions RAG briefly
• <…|sources/2026-04-11-karpathy-llm-wiki> — primary source

Want me to ingest something to answer this properly? Reply with a URL or
upload a file.
```

## Pattern 2 — Ingest with approval flow

### When to use

A user wants to add a new source (article, PDF, video, Slack message) to the wiki.

### Trigger options

- Slash command: `/wiki ingest https://example.com/article`
- File upload to the bot's DM with caption "ingest"
- Reply to any Slack message with "@wiki ingest this"
- Emoji reaction `:wiki:` on any message (if the workspace has a custom emoji for this)

### Expected behaviour

1. Bot acks in thread: "Fetching…"
2. Bot fetches, processes, and produces a **preview** of the wiki changes without committing.
3. User reacts ✅ to approve or ❌ to cancel.
4. On ✅, bot commits to a branch, pushes, opens a PR, and posts the PR URL.

### Preview message

```
*Preview: ingest `2026-04-11-example-article`*

I'll create these pages:
• `sources/2026-04-11-example-article` — new
• `concepts/transformer-architecture` — new
• `entities/jane-smith` — new
• `index.md` — updated (added 3 entries)
• `log.md` — updated (appended ingest entry)

Summary of the source (3 sentences):
> This article argues that transformer architectures are the dominant paradigm
> for sequence modelling as of 2026. It traces the lineage from attention-only
> models through mixture-of-experts variants. Jane Smith is cited as a key
> contributor to recent sparse-attention work.

No discrepancies flagged against existing pages.

React :white_check_mark: to commit, :x: to cancel.
_This preview expires in 5 minutes._
```

### Post-approval message

```
:white_check_mark: Committed to branch `bot/ingest-2026-04-11-example-article`.

PR opened: <https://github.com/ORG/llm-wiki/pull/42|#42>

I'll auto-merge once checks pass (additive, lint-clean).
```

### Cancellation

```
:x: Cancelled. No changes committed. The draft will be discarded.
```

### Error case — fetch failed

```
I couldn't fetch `https://example.com/article` (HTTP 403).

Options:
1. Upload the article as a file (PDF, HTML, or markdown)
2. Paste the article text directly in this thread
3. Try a different URL
```

## Pattern 3 — Act with draft-and-approve

### When to use

A user wants the bot to produce an external side effect using wiki content as input — drafting an email, creating a ticket, posting a message elsewhere, updating a record.

### Requires

- Tier 3 (Maintainer) permissions.
- At least one connected MCP or external tool wired into `CLAUDE.md`'s Connected tools section.

### Trigger

```
/wiki act draft an email to the product team summarising our stance on
LLM Wiki vs NotebookLM, citing concepts/llm-wiki-pattern
```

### Expected behaviour

1. Bot assembles the draft using only wiki content.
2. Bot posts the draft in a thread with three buttons: **Send** / **Edit** / **Cancel**.
3. Irreversible actions show a second confirmation dialog.
4. On send, the bot logs the Act in `wiki/log.md` (via a follow-up commit).

### Draft message

```
*Draft: Email to #product — "LLM Wiki vs NotebookLM"*

*To:* product@company.com
*Subject:* Our stance on LLM Wiki vs NotebookLM

Hi team,

Quick summary of where we landed on LLM Wiki vs NotebookLM, drawn from
the wiki (`concepts/llm-wiki-pattern`, `concepts/rag`):

• NotebookLM re-retrieves at query time; LLM Wiki pre-compiles knowledge
  into a persistent artifact.
• For our scale (~50 sources today, likely <500 within a year), LLM Wiki
  keeps knowledge compounding without per-query retrieval cost.
• We're not blocked on either — the wiki pattern is a layer on top of
  whatever retrieval we add later.

Source pages:
- https://github.com/ORG/llm-wiki/blob/main/wiki/concepts/llm-wiki-pattern.md
- https://github.com/ORG/llm-wiki/blob/main/wiki/concepts/rag.md

Let me know if you want me to dig deeper on any of the tradeoffs.

— via @wiki, on behalf of @bom

---

[ Send ] [ Edit ] [ Cancel ]

_This draft will be discarded in 10 minutes if no action is taken._
```

### Irreversible-action confirmation

```
:warning: *This action is irreversible.*

You're about to send an email to 47 recipients. This cannot be undone.

Type `confirm send` in this thread to proceed, or `cancel` to discard.
```

### Post-send confirmation

```
:white_check_mark: Sent.

Logged in `wiki/log.md`:
> [2026-04-11] act | emailed product@company.com re: LLM Wiki vs NotebookLM (requested by @bom)

Commit: <https://github.com/ORG/llm-wiki/commit/abc123|abc123>
```

## Pattern 4 — Passive weekly digest

### When to use

Give the team visibility into what's growing in the wiki without requiring them to browse it.

### Trigger

Scheduled — every Monday at 09:00 local time, posted to `#wiki-updates`.

### Expected behaviour

- Bot runs a Query operation under the hood: "summarise wiki changes over the last 7 days."
- Posts a single message to the channel — no thread, no mentions.
- Includes counts, notable new pages, discrepancies flagged this week, and unresolved TODOs.

### Digest message template

```
*Wiki digest — week of April 5, 2026*

*Activity*
• 7 new sources ingested
• 3 new concepts created
• 2 entity pages updated
• 1 discrepancy flagged

*New this week*
• <…|sources/2026-04-07-anthropic-research-post> — LLM-assisted research
• <…|concepts/sparse-attention> — new concept, 4 sources link to it
• <…|entities/jane-smith>

*Flagged*
:warning: Discrepancy in <…|sources/2026-04-09-thai-explainer>: the video
says "LLM Wiki replaces RAG" but the primary source (Karpathy gist) says
they are complementary. The discrepancy is documented in the source page.

*Unresolved*
• 3 pages have TODOs older than 14 days — run `/wiki lint` to see them

_Full log: <https://github.com/ORG/llm-wiki/blob/main/wiki/log.md|wiki/log.md>_
```

### Empty-week variant

```
*Wiki digest — week of April 5, 2026*

No new activity this week. The wiki is stable at 23 sources / 15 concepts / 9 entities.

_Want to add something? `/wiki ingest <url>` or upload a file in DM._
```

## Pattern 5 — DM for private queries

### When to use

- The user wants to ask something sensitive they don't want in a channel.
- The user wants to bulk-experiment with queries before posting a summary anywhere.
- The user is Tier 3 and is drafting an Act operation they don't want other team members to see in progress.

### Trigger

Any DM to the bot.

### Expected behaviour

- Identical to channel behaviour for Query and Ingest patterns.
- Act operations are allowed but the bot still logs them to `wiki/log.md` — "private" means "not visible in channels," not "not recorded in the wiki."
- The bot will refuse to quote pages with `visibility: team-only` if the user is DMing from outside the team (configurable via the permission layer).

### First-time DM message

```
Hi @bom — I'm @wiki, the bot for the team wiki.

In a DM I can:
• Answer questions from the wiki (`how does X work?`)
• Ingest new sources (paste a URL or upload a file)
• Draft Act operations (Tier 3 only — you have this)

Everything you do here is private to you, but any ingests or acts are
still logged in `wiki/log.md` for the team's audit trail.

What do you want to do?
```

### Private-query reply format

Identical to Pattern 1, but no thread (DMs don't need them) and the bot adds a footer reminder:

```
*LLM Wiki vs RAG* …

[…full answer…]

_This conversation is private. Commits and act operations are still
recorded in the public wiki log._
```

## Formatting rules the bot must follow in every pattern

These are the Slack-specific formatting rules. They mirror what `CLAUDE.md`'s `## Slack bot integration` section will tell the agent.

### Slack mrkdwn, not standard markdown

Slack's `mrkdwn` is similar to CommonMark but with important differences:

- Bold: `*bold*` (one asterisk, not two)
- Italic: `_italic_` (underscore, not single asterisk)
- Strikethrough: `~strike~`
- Code block: triple backticks, no language hint
- Inline code: single backticks
- Blockquote: lines prefixed with `>`
- Links: `<url|display text>` (angle-bracket form)
- Mentions: `<@U12345>`
- Channels: `<#C12345|channel-name>`
- Bullet lists: `• ` prefix (a literal bullet char, not `-` or `*`)
- Numbered lists: `1. ` / `2. ` works but the bot should prefer bullets
- Headers: not supported — use bold lines instead

### Length targets

- Channel @mention reply: ≤200 words in the thread reply.
- DM query: ≤300 words.
- Ingest preview: ≤150 words of summary + the changes list.
- Act draft: whatever the content requires, but the surrounding chrome must be ≤50 words.
- Digest: ≤250 words total.

### When to use a thread

- Always for @mentions in channels.
- Always for `/wiki ingest` and `/wiki act` (keeps the channel clean).
- Never for DMs (DMs are already a thread).
- Never for the weekly digest (it's a broadcast).

### Link formatting

- GitHub blob URLs for wiki pages: `<https://github.com/ORG/llm-wiki/blob/main/wiki/concepts/X.md|concepts/X>`
- External sources: `<https://example.com|example.com>` (or a short descriptive label).
- Slack messages: `<https://ORG.slack.com/archives/C123/p456|message in #channel>`.

### Citations block

Every factual reply ends with a `Sources:` list using the bullet form above. If the bot made no claim that needs a source (e.g. "I don't know"), omit the block.

### Ephemeral UI expiry

- Ingest previews expire after 5 minutes.
- Act drafts expire after 10 minutes.
- Expired drafts post a one-line "expired, no action taken" message and are discarded.

### What the bot never does in Slack

- Never posts unsolicited messages outside `#wiki-updates`.
- Never DMs a user who hasn't DM'd it first (one exception: the admin on ERROR-level events).
- Never uses headers (`#`, `##`) — they don't render in Slack.
- Never uses standard-markdown link syntax `[text](url)` — it renders literally in Slack.
- Never @-mentions `@channel` or `@here`.
- Never posts more than 3 messages in response to a single trigger.
- Never apologises for not knowing something. It says "no page on that yet."

## Testing the UX before building the bot

You can dry-run all of these patterns with your local LLM agent right now:

1. Start a local session with the wiki.
2. Tell the agent: "Pretend you are the @wiki Slack bot. Use Slack mrkdwn formatting. Keep replies under 200 words."
3. Paste any of the Pattern 1 / Pattern 2 / Pattern 4 trigger examples above.
4. Critique the output against the templates in this doc.

This lets you iterate on prompts and formatting rules against real wiki content before any Slack plumbing exists.
