---
description: Use the wiki as context to act in an external system (email, chat, tracker, etc.)
argument-hint: "<what-to-do>"
---

Run the **Act** operation defined in `CLAUDE.md` under `## Operation: Act`.

Requested action: $ARGUMENTS

Workflow (all 7 steps are mandatory — do not skip the approval gate):

1. **Identify the target tool.** Match against the `## Connected tools` registry in `CLAUDE.md`. If no tool matches, stop and tell me.
2. **Read the relevant wiki pages** for context. Track which pages informed the output.
3. **Draft the output** (email body / issue / chat message / etc.). Stay faithful to the wiki — do not invent facts.
4. **Show me the draft and wait for approval.** Use this format:
   > Here's the draft {output type} based on [[page-a]] and [[page-b]]. Review and confirm before I {send/create/post}.
   - For irreversible actions (send, delete, publish) — flag loudly in the prompt.
5. **Execute only after explicit approval.**
6. Append to `wiki/log.md`: `## [YYYY-MM-DD] act | {what happened via what tool}` with wiki pages cited and any external artifact reference (URL, message ID).
7. (Optional) **File the output back** into the wiki as a new page if it's high-value — ask me first.

**Hard rules:**
- No silent side effects. Ever.
- No bulk Act (one draft-and-approve cycle per action).
- Sensitive data (`visibility: private`, secrets) stays out of drafts unless I say otherwise.
