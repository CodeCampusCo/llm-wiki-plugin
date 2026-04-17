#!/bin/bash
# PostToolUse hook — runs after Write or Edit.
# If the edited file was inside wiki/, refresh the qmd search index silently.
# No-op if qmd isn't installed or jq isn't available — hooks should never
# block Claude from working if their optional tooling is missing.

set -u

# Read the hook payload from stdin (JSON). We only need the edited path.
INPUT=$(cat 2>/dev/null || echo "")

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")

# Only act on edits inside wiki/
case "$FILE_PATH" in
  */wiki/*) ;;
  *) exit 0 ;;
esac

# Only run if qmd is installed
if ! command -v qmd >/dev/null 2>&1; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Bounded — if qmd update hangs for any reason, don't stall the agent.
# Output is suppressed so it doesn't pollute the session transcript.
(cd "$PROJECT_DIR" && timeout 10 qmd update --quiet >/dev/null 2>&1) || true

exit 0
