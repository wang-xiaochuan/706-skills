#!/usr/bin/env bash
set -u

MAX_TURNS="${MAX_TURNS:-5}"
MAX_BUDGET_USD="${MAX_BUDGET_USD:-2}"
PERMISSION_MODE="${PERMISSION_MODE:-acceptEdits}"
GOAL_FILE="${GOAL_FILE:-goal.md}"
CHECK_SCRIPT="${CHECK_SCRIPT:-checks.sh}"
LOG_DIR="${LOG_DIR:-logs}"

if ! command -v claude >/dev/null 2>&1; then
  echo "claude CLI not found. Install Claude Code or adjust PATH." >&2
  exit 127
fi

if [ ! -f "$GOAL_FILE" ]; then
  echo "Missing goal file: $GOAL_FILE" >&2
  exit 1
fi

if [ ! -f "$CHECK_SCRIPT" ]; then
  echo "Missing check script: $CHECK_SCRIPT" >&2
  exit 1
fi

mkdir -p "$LOG_DIR"

turn=1
last_check_summary=""

while [ "$turn" -le "$MAX_TURNS" ]; do
  turn_log="$LOG_DIR/turn-$turn.txt"
  check_log="$LOG_DIR/check-$turn.txt"

  echo "== Turn $turn/$MAX_TURNS =="

  if [ "$turn" -eq 1 ]; then
    prompt="$(cat "$GOAL_FILE")

Work on this goal. Respect every constraint. After making progress, stop and let the harness run checks."
    claude -p "$prompt" \
      --permission-mode "$PERMISSION_MODE" \
      --max-budget-usd "$MAX_BUDGET_USD" \
      --output-format text | tee "$turn_log"
    claude_status="${PIPESTATUS[0]}"
  else
    prompt="Continue working on the goal in $GOAL_FILE.

The previous validation failed. Here is the check output summary:

$last_check_summary

Fix the cause, keep changes scoped, then stop and let the harness run checks again."
    claude --continue -p "$prompt" \
      --permission-mode "$PERMISSION_MODE" \
      --max-budget-usd "$MAX_BUDGET_USD" \
      --output-format text | tee "$turn_log"
    claude_status="${PIPESTATUS[0]}"
  fi

  if [ "$claude_status" -ne 0 ]; then
    echo "Claude command failed with status $claude_status. See $turn_log." >&2
    exit "$claude_status"
  fi

  echo "== Running checks =="
  bash "$CHECK_SCRIPT" >"$check_log" 2>&1
  check_status="$?"

  if [ "$check_status" -eq 0 ]; then
    echo "Checks passed. Goal complete."
    echo "Check log: $check_log"
    exit 0
  fi

  echo "Checks failed with status $check_status. See $check_log."
  last_check_summary="$(tail -n 80 "$check_log")"
  turn=$((turn + 1))
done

echo "Stopped after $MAX_TURNS turns without passing checks." >&2
exit 1
