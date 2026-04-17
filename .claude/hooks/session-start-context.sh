#!/bin/bash
# SessionStart hook — prints recent wiki activity so the agent starts each
# session with continuity. Output goes into the agent's context.
#
# Prints:
# - the last 5 entries in wiki/log.md (header lines only)
# - whether qmd appears to be configured for this wiki
#
# Keep it short — this runs every session.

set -u

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
LOG="$PROJECT_DIR/wiki/log.md"

if [ -f "$LOG" ]; then
  echo "### Recent wiki activity (last 5 entries)"
  echo ""
  grep "^## \[" "$LOG" | tail -5
  echo ""
  echo "_Read the full entry in \`wiki/log.md\` if any of these are relevant to today's work._"
  echo ""
fi

# qmd status hint — helps the agent decide Query path (qmd vs index.md fallback)
if command -v qmd >/dev/null 2>&1; then
  # List collections scoped inside this project. If any match, qmd is live.
  if qmd collection list 2>/dev/null | grep -q "$PROJECT_DIR"; then
    echo "_qmd is configured for this wiki — prefer \`mcp__plugin_qmd_qmd__query\` during Query ops._"
  else
    echo "_qmd is installed but no collection covers this project — Query falls back to \`wiki/index.md\`._"
  fi
fi

exit 0
