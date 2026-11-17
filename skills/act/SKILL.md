---
name: act
description: Use to act in an external system (email, chat, tracker, calendar) using LLM Wiki pages as context, always draft first and send only after approval. Triggers - "draft an email from my wiki", "file an issue from wiki notes", "act on", "/llm-wiki:act", "ใช้ wiki ทำ".
argument-hint: "<what-to-do>"
---

# Act from LLM Wiki context

Take `<plugin_root>` and `<data_dir>` from this session's context: the lines that start
`Plugin root:` and `Plugin data dir:`. Always quote paths in shell commands (they may contain spaces).

## Before starting

1. Run `python3 "<plugin_root>/scripts/wikiconf.py" show "<data_dir>"`. It prints `root`, `raw_dir`,
   `archive_dir`, `qmd_collection`, `schema_version` and `plugin_schema_version`. If the wiki is not
   configured, tell the user to run `/llm-wiki:init` and stop.
2. Read `<plugin_root>/schema/schema.md`, then `<root>/CONVENTIONS.md`, then the operation file named below.
3. Use absolute paths under `<root>` for everything. Relative paths in the schema (`wiki/`, `raw/`,
   `archive/`) are relative to `<root>`, never the current working directory.
4. Never commit or push in the wiki without the user's approval.

Operation file: `<plugin_root>/schema/schema.md` section "Operation: Act" (complete there), including the
"Connected tools" registry guidance.

Requested action: $ARGUMENTS

## Steps (all mandatory, never skip the approval gate)

1. Identify the target tool. Check the connected tools registry in the schema and `<root>/CONVENTIONS.md`.
   If no connected tool matches, tell the user and stop.
2. Read the relevant wiki pages under `<root>/wiki/` and keep track of which pages informed the output.
3. Draft the output (email body, issue, chat message). Stay faithful to the wiki and invent nothing.
4. Show the draft and wait for approval, in this form:
   > Here's the draft {output type} based on [[page-a]] and [[page-b]]. Review and confirm before I {send/create/post}.

   Flag irreversible actions (send, delete, publish) loudly.
5. Execute only after explicit approval for that specific operation.
6. Append `## [YYYY-MM-DD] act | {what happened via what tool}` to `<root>/wiki/log.md`, with the wiki pages
   used and any external reference (URL, message ID).
7. Optionally offer to file a high-value output back into the wiki. Ask first.

## Hard rules

- No silent side effects, no bulk Act: one draft-and-approve cycle per action.
- Keep sensitive data (`visibility: private`, secrets, personal details) out of drafts unless the user asks.
- If a tool returns an auth error, stop and tell the user. Do not work around it.
