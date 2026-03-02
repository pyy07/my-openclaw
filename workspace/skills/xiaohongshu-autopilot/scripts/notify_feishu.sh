#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CHANNEL="${XHS_AUTOPILOT_CHANNEL:-feishu}"
TARGET="${XHS_AUTOPILOT_FEISHU_TARGET:-user:ou_27eafc99a5b351d7df9ca5709e74ea41}"
OUTBOX_DIR="$BASE_DIR/logs/notifications"

usage() {
  cat <<USAGE
Usage:
  ./scripts/notify_feishu.sh "message text"
  echo "message text" | ./scripts/notify_feishu.sh

Environment:
  XHS_AUTOPILOT_CHANNEL=feishu
  XHS_AUTOPILOT_FEISHU_TARGET=user:ou_xxx
USAGE
}

queue_message() {
  local msg="$1"
  mkdir -p "$OUTBOX_DIR"
  local outbox_file="$OUTBOX_DIR/$(date +%F)-outbox.ndjson"
  jq -nc \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg channel "$CHANNEL" \
    --arg target "$TARGET" \
    --arg message "$msg" \
    '{ts:$ts,channel:$channel,target:$target,message:$message}' >> "$outbox_file"
  echo "[warn] message queued: $outbox_file" >&2
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -gt 0 ]]; then
  MESSAGE="$*"
else
  MESSAGE="$(cat)"
fi

if [[ -z "${MESSAGE// }" ]]; then
  usage
  exit 1
fi

if ! command -v openclaw >/dev/null 2>&1; then
  queue_message "$MESSAGE"
  exit 1
fi

set +e
send_output="$(openclaw message send --channel "$CHANNEL" --target "$TARGET" --message "$MESSAGE" --json 2>&1)"
rc=$?
set -e

if [[ $rc -ne 0 ]]; then
  echo "[warn] send failed: $send_output" >&2
  queue_message "$MESSAGE"
  exit $rc
fi

echo "[ok] sent to $CHANNEL $TARGET"
