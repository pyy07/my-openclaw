#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
NOTIFY="$BASE_DIR/scripts/notify_feishu.sh"
DISCOVER="$BASE_DIR/scripts/discover_topics.sh"
DAILY="$BASE_DIR/scripts/daily_cycle.sh"
LOG_DIR="$BASE_DIR/logs/cron"
STAMP="$(date +%F-%H%M%S)"
RUN_LOG="$LOG_DIR/$STAMP.log"

mkdir -p "$LOG_DIR"

send_note() {
  local msg="$1"
  if [[ -x "$NOTIFY" ]]; then
    "$NOTIFY" "$msg" || true
  fi
}

run_main() {
  echo "[$(date '+%F %T')] run_exploration_cycle start"

  if [[ -x "$DISCOVER" ]]; then
    "$DISCOVER"
  else
    echo "discover script missing: $DISCOVER"
    return 1
  fi

  if [[ -x "$DAILY" ]]; then
    "$DAILY" start
  else
    echo "daily script missing: $DAILY"
    return 1
  fi

  echo "[$(date '+%F %T')] run_exploration_cycle done"
}

set +e
run_main >"$RUN_LOG" 2>&1
rc=$?
set -e

if [[ $rc -eq 0 ]]; then
  send_note "[小红书自动运营] 定时探索任务完成。运行日志: $RUN_LOG"
  echo "[ok] run log: $RUN_LOG"
  exit 0
fi

send_note "[小红书自动运营] 定时探索任务失败(rc=$rc)。请查看日志: $RUN_LOG"
echo "[error] run failed rc=$rc log=$RUN_LOG"
exit "$rc"
