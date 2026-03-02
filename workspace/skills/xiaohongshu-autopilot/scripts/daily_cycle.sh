#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TODAY="$(date +%F)"
LOG_DIR="$BASE_DIR/logs/daily"
NOTIFY="$BASE_DIR/scripts/notify_feishu.sh"

mkdir -p "$LOG_DIR"

send_note() {
  local msg="$1"
  if [[ -x "$NOTIFY" ]]; then
    "$NOTIFY" "$msg" || true
  fi
}

usage() {
  cat <<USAGE
Usage:
  ./scripts/daily_cycle.sh start [YYYY-MM-DD]
USAGE
}

render_template() {
  local day="$1"
  cat > "$LOG_DIR/$day.md" <<TEMPLATE
# Daily Ops - $day

## 今日探索目标
- 

## 人设对齐检查
- 是否符合“通勤实用型美妆穿搭博主”：
- 内容配比（美妆60/服装40）：

## 今日实验设计
- 实验1：
- 实验2（可选）：
- 成功判定阈值：

## 执行动作记录
- 发布时间：
- 内容主题：
- 标题：
- 封面策略：
- 标签：
- 发布工具返回：

## 数据回收
- 曝光：
- 点赞：
- 收藏：
- 评论：
- 互动率：

## 结论
- 保留：
- 迭代：
- 淘汰：

## 明日假设
- 
TEMPLATE
}

cmd="${1:-}"
case "$cmd" in
  start)
    day="${2:-$TODAY}"
    if [[ -f "$LOG_DIR/$day.md" ]]; then
      echo "[skip] 已存在日志: $LOG_DIR/$day.md"
      send_note "[小红书自动运营] 每日计划已存在: $LOG_DIR/$day.md"
      exit 0
    fi
    render_template "$day"
    echo "[ok] 已创建日志: $LOG_DIR/$day.md"
    send_note "[小红书自动运营] 已创建每日探索日志: $LOG_DIR/$day.md"
    ;;
  *)
    usage
    exit 1
    ;;
esac
