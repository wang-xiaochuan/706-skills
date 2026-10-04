#!/usr/bin/env bash
set -u

# Run from the harness directory. Customize TARGET_CWD and checks for the task.
TARGET_CWD="{{TARGET_CWD}}"

if [ ! -d "$TARGET_CWD" ]; then
  echo "Target directory does not exist: $TARGET_CWD" >&2
  exit 1
fi

cd "$TARGET_CWD" || exit 1

# Replace these sample checks with objective acceptance checks.
# Examples:
#   npm test
#   npm run build
#   pytest
#   test -f README.md
#   find . -type f | wc -l

{{CHECK_COMMANDS}}
