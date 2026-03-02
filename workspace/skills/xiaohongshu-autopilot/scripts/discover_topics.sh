#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
XHS_SCRIPTS_DIR="/Users/lukepan/.openclaw/workspace/skills/xiaohongshu/scripts"
NOTIFY="$BASE_DIR/scripts/notify_feishu.sh"
TODAY="$(date +%F)"
DAY="${1:-$TODAY}"
OUT="$BASE_DIR/logs/discovery/$DAY.md"

KEYWORDS=("通勤妆" "早八妆容" "通勤穿搭" "胶囊衣橱" "平价彩妆")

mkdir -p "$(dirname "$OUT")"

send_note() {
  local msg="$1"
  if [[ -x "$NOTIFY" ]]; then
    "$NOTIFY" "$msg" || true
  fi
}

send_note "[小红书自动运营] 开始探索 ${DAY}。动作总数: 1个recommend + ${#KEYWORDS[@]}个search。"

recommend_status="skip"
search_ok=0
search_fail=0

if [[ -x "$XHS_SCRIPTS_DIR/recommend.sh" ]]; then
  send_note "[小红书自动运营] 动作开始: recommend.sh（首页推荐抓取）"
  if (cd "$XHS_SCRIPTS_DIR" && ./recommend.sh >/tmp/xhs-recommend-${DAY}.txt 2>&1); then
    recommend_status="ok"
    send_note "[小红书自动运营] 动作结果: recommend.sh 成功"
  else
    recommend_status="fail"
    send_note "[小红书自动运营] 动作结果: recommend.sh 失败"
  fi
else
  send_note "[小红书自动运营] 动作跳过: recommend.sh 不存在或不可执行"
fi

{
  echo "# Discovery - $DAY"
  echo
  echo "## 推荐流抓取"
  if [[ "$recommend_status" == "ok" ]]; then
    echo '```'
    cat "/tmp/xhs-recommend-${DAY}.txt"
    echo '```'
  elif [[ "$recommend_status" == "fail" ]]; then
    echo '```'
    cat "/tmp/xhs-recommend-${DAY}.txt"
    echo '```'
    echo "- recommend.sh 执行失败"
  else
    echo "- recommend.sh 不存在或不可执行"
  fi

  echo
  echo "## 关键词抓取"
  for kw in "${KEYWORDS[@]}"; do
    echo "### $kw"
    if [[ -x "$XHS_SCRIPTS_DIR/search.sh" ]]; then
      send_note "[小红书自动运营] 动作开始: search.sh 关键词=$kw"
      echo '```'
      if (cd "$XHS_SCRIPTS_DIR" && ./search.sh "$kw"); then
        search_ok=$((search_ok + 1))
        send_note "[小红书自动运营] 动作结果: search.sh 成功 关键词=$kw"
      else
        search_fail=$((search_fail + 1))
        echo "search.sh failed: $kw"
        send_note "[小红书自动运营] 动作结果: search.sh 失败 关键词=$kw"
      fi
      echo '```'
    else
      echo "- search.sh 不存在或不可执行"
      search_fail=$((search_fail + 1))
      send_note "[小红书自动运营] 动作跳过: search.sh 不存在或不可执行 关键词=$kw"
    fi
    echo
  done

  echo "## 选题建议（人工补充）"
  echo "- 候选1："
  echo "- 候选2："
  echo "- 候选3："
} > "$OUT"

send_note "[小红书自动运营] 探索完成 ${DAY}。结果: recommend=${recommend_status}, search_ok=${search_ok}, search_fail=${search_fail}。日志: ${OUT}"

echo "[ok] discovery log generated: $OUT"
