#!/usr/bin/env bash
# 漫说GitHub 每日探索入口：创建当日日志并记录开始。
# 实际探索、写稿、发飞书由「加载本 skill 的 Agent」按 SKILL.md 流程执行；
# 本脚本仅初始化日志并记录第一步，便于 cron 统一调用。
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$BASE_DIR/logs/daily"
DRAFT_DIR="$BASE_DIR/drafts/review"

mkdir -p "$LOG_DIR" "$DRAFT_DIR"
"$BASE_DIR/scripts/step_log.sh" "步骤 1：开始探索（run_daily_exploration.sh）"
echo "OK: 日志已创建。请由 Agent 按 SKILL.md 继续执行步骤 2～7（探索 GitHub、写稿、发飞书）。"
