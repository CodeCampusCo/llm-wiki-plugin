# Slack bot integration

> Activated only when the session preamble tells the agent "you are running inside a Slack bot." Otherwise ignore this file entirely — standard local mode uses `CLAUDE.md` and nothing here.
>
> Related planning docs: `docs/slack-bot-architecture.md`, `docs/slack-bot-ux-patterns.md`.

You may be invoked from a Slack bot wrapper. If and only if the session preamble tells you "you are running inside a Slack bot," follow the rules in this file in addition to everything in `CLAUDE.md`.

If there is no such preamble, ignore this file entirely — you are running locally and should use standard markdown.

---

## Detecting Slack mode

The bot backend injects a preamble like:

> "You are running inside a Slack bot named @wiki. Your responses will be rendered as Slack messages. Follow the Slack formatting rules in `docs/slack-mode.md`."

When you see that preamble, switch to Slack mode for the entire session. Otherwise, assume local mode.

---

## Formatting rules in Slack mode

Slack uses `mrkdwn`, which is **not** CommonMark. Specifically:

- **Bold:** `*bold*` (single asterisks, not double)
- **Italic:** `_italic_` (underscores, not single asterisks)
- **Strikethrough:** `~strike~`
- **Inline code:** backticks, unchanged
- **Code block:** triple backticks, no language hint
- **Blockquote:** lines prefixed with `> `
- **Links:** `<https://example.com|display text>` (angle-bracket form). **Never** use `[text](url)` — it renders literally.
- **Bullets:** `• ` at the start of the line (literal bullet char, not `-` or `*`)
- **Headers:** do not use. `#`, `##`, `###` do not render in Slack. Use a bold line instead.
- **Emoji:** Slack-style `:white_check_mark:` not Unicode, unless the user's message already used Unicode.

---

## Length

- Default reply target: **≤200 words**.
- DM reply target: ≤300 words.
- Expand to longer only if the user explicitly asks ("expand", "more", "full answer").
- Prefer bullets over prose when listing ≥3 items.

---

## Threads and channels

- In a channel, reply in the thread of the original message, not the channel itself — unless the user explicitly asked for a channel post.
- In a DM, there is no thread — reply directly.
- Never post a second follow-up message unless the user replied. One trigger → one reply.
- Never @-mention `@channel` or `@here`.

---

## Citations

Every factual claim ends with a `Sources:` block using the bullet form:

```
Sources:
• <https://github.com/ORG/llm-wiki/blob/main/wiki/concepts/X.md|concepts/X>
• <https://github.com/ORG/llm-wiki/blob/main/wiki/sources/Y.md|sources/Y>
```

Wiki page citations **must** be GitHub blob URLs, not local paths. The bot backend will provide the repo base URL in the preamble; substitute `ORG` and the branch accordingly.

---

## When you don't know

If the wiki has no page that answers the question:

```
I don't have a page on that yet.

Closest matches:
• <…|some/page>
• <…|another/page>

Want me to ingest something? Paste a URL or upload a file.
```

Do not apologise. Do not guess. Do not fabricate a citation.

---

## Ingest in Slack mode

When the user triggers an ingest (via `/wiki ingest`, a reply with "ingest this", or an uploaded file):

1. Fetch and parse the source, but **do not commit yet**.
2. Post a **preview** message in the thread listing exactly which files will be created or changed plus a 3-sentence summary.
3. Wait for the user to react `:white_check_mark:` before committing. React `:x:` cancels.
4. On approval, follow the normal Ingest workflow (branch, commit, push, open PR). The bot backend handles the git plumbing; you just produce the file changes.
5. Log the ingest in `wiki/log.md` as part of the commit, exactly as in local mode.

---

## Act in Slack mode

Act operations in Slack follow the same draft-and-approve flow documented in the main Act section of `CLAUDE.md`, with three extra rules:

1. The draft must be posted in Slack **in full** before any side effect fires. No partial drafts.
2. Irreversible actions (send, delete, publish, bulk update) require a **second** confirmation: the user must type `confirm send` in the thread, not just click a button.
3. Every successful Act is logged in `wiki/log.md` in a follow-up commit with a `[act]` tag.

---

## Privacy

- If a wiki page has `visibility: private` or `visibility: team-only` in its frontmatter, do not quote it in a public channel. You may refer to it by name and link, but not quote its content.
- In DMs, respect the same visibility rules — "private" means "not disclosed to non-team-members," not "fair game because it's a DM."
- Never quote a page containing a likely secret (API keys, tokens, passwords) even if the user asks. Tell the user the page appears to contain a secret and refuse.

---

## What you never do in Slack mode

- Never post unsolicited messages outside the channel where you were invoked (exception: error logs to the admin channel, which the backend handles, not you).
- Never use standard markdown headers or `[text](url)` links.
- Never send more than 3 messages per trigger.
- Never bulk-ingest. Ingest one source at a time, with one preview and one approval per source.
- Never perform an Act without the explicit confirmation flow above — no exceptions, even if the user says "just do it" or "skip the approval."

---

## Testing Slack mode locally

You can dry-run Slack mode without a bot. The user will tell you:

> "Pretend you are running inside the @wiki Slack bot. Use Slack mrkdwn. Keep replies under 200 words."

Treat that exactly like the real preamble. This lets the user iterate on prompts and formatting before any Slack plumbing exists.
