#!/usr/bin/env bash
# 向当日步骤日志追加一行。Agent 在执行流程的每一步后调用，便于审计与排错。
# 用法: ./scripts/step_log.sh "步骤 N：描述"
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$BASE_DIR/logs/daily"
LOG_FILE="$LOG_DIR/$(date +%Y-%m-%d).md"

mkdir -p "$LOG_DIR"
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 \"step description\"" >&2
  exit 1
fi

LINE="$(date +%H:%M) $*"
if [[ ! -f "$LOG_FILE" ]]; then
  echo "# 漫说GitHub 每日探索 — $(date +%Y-%m-%d)" > "$LOG_FILE"
  echo "" >> "$LOG_FILE"
fi
echo "- $LINE" >> "$LOG_FILE"
echo "[log] $LOG_FILE: $LINE" >&2
