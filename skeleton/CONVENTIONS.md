# Personal Conventions

The agent reads this file after the plugin's schema (`schema/schema.md`). Anything here wins over the schema on conflict.

## Conventions

Add your own rules here as they emerge: naming, tags, page layout tweaks, what to skip when ingesting.

## Session rules

<!-- Rules the plugin adds to every Claude Code session after its own working rules, for example how wiki changes reach the repo. Write them as a bullet list below this comment; keep them short, each line costs context in every session. This comment is not printed. -->

## Connected tools

Register each connected tool (email, chat, tracker, calendar, meeting transcripts) so the agent knows when to use it. Leave empty until you connect one. Template per entry:

```markdown
#### {Tool name}
- **What it accesses:** {brief description of data or actions}
- **Use during Ingest when:** {triggers}
- **Use during Query when:** {triggers}
- **Use during Act when:** {triggers}
- **Do NOT use for:** {anti-patterns specific to this tool}
- **Privacy notes:** {anything sensitive to be careful about}
```
