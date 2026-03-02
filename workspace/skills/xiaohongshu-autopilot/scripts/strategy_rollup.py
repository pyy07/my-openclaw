#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = BASE_DIR / "logs" / "daily"
METRICS = BASE_DIR / "data" / "metrics.csv"
STRATEGY = BASE_DIR / "data" / "strategy.md"
NOTIFY = BASE_DIR / "scripts" / "notify_feishu.sh"


def parse_args():
    p = argparse.ArgumentParser(description="Roll up daily ops result into strategy files")
    p.add_argument("--date", help="Target date (YYYY-MM-DD), default=today")
    p.add_argument("--post-id", default="", help="Post id")
    p.add_argument("--theme", default="", help="Content theme")
    p.add_argument("--goal", default="", help="Daily goal")
    p.add_argument("--impressions", type=int, default=0)
    p.add_argument("--likes", type=int, default=0)
    p.add_argument("--favorites", type=int, default=0)
    p.add_argument("--comments", type=int, default=0)
    p.add_argument("--decision", default="iterate", choices=["keep", "iterate", "drop"])
    p.add_argument("--no-notify", action="store_true", help="Disable Feishu notification")
    return p.parse_args()


def engagement_rate(impressions: int, likes: int, favorites: int, comments: int) -> float:
    if impressions <= 0:
        return 0.0
    return (likes + favorites + comments) / impressions


def append_metrics(date_str: str, args, log_file: Path, rate: float):
    row = {
        "date": date_str,
        "post_id": args.post_id,
        "theme": args.theme,
        "goal": args.goal,
        "impressions": args.impressions,
        "likes": args.likes,
        "favorites": args.favorites,
        "comments": args.comments,
        "engagement_rate": f"{rate:.4f}",
        "decision": args.decision,
        "log_file": str(log_file),
    }

    file_exists = METRICS.exists()
    with METRICS.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date",
                "post_id",
                "theme",
                "goal",
                "impressions",
                "likes",
                "favorites",
                "comments",
                "engagement_rate",
                "decision",
                "log_file",
            ],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def append_strategy_note(date_str: str, args, rate: float):
    if not STRATEGY.exists():
        STRATEGY.write_text("# 小红书美妆穿搭策略库\n\n", encoding="utf-8")

    label = {
        "keep": "保留",
        "iterate": "迭代",
        "drop": "淘汰",
    }[args.decision]

    note = (
        f"\n- {date_str} | 主题:{args.theme or '-'} | 目标:{args.goal or '-'}"
        f" | 互动率:{rate:.2%} | 结论:{label}"
        f" | 证据: logs/daily/{date_str}.md"
    )

    text = STRATEGY.read_text(encoding="utf-8")
    marker = "## 证据索引"
    if marker in text:
        text = text.replace(marker, marker + note)
    else:
        text = text + "\n## 证据索引" + note + "\n"
    STRATEGY.write_text(text, encoding="utf-8")


def notify_result(date_str: str, args, rate: float):
    if not NOTIFY.exists():
        return

    decision_zh = {
        "keep": "保留",
        "iterate": "迭代",
        "drop": "淘汰",
    }[args.decision]

    msg = (
        "[小红书自动运营] 结果回收完成\n"
        f"日期: {date_str}\n"
        f"主题: {args.theme or '-'}\n"
        f"目标: {args.goal or '-'}\n"
        f"数据: 曝光{args.impressions}, 点赞{args.likes}, 收藏{args.favorites}, 评论{args.comments}\n"
        f"互动率: {rate:.2%}\n"
        f"结论: {decision_zh}\n"
        f"日志: logs/daily/{date_str}.md"
    )

    result = subprocess.run([str(NOTIFY), msg], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[warn] notify failed: {result.stderr.strip()}")


def main():
    args = parse_args()
    today = args.date or dt.date.today().isoformat()
    log_file = LOG_DIR / f"{today}.md"

    if not log_file.exists():
        raise SystemExit(f"missing daily log: {log_file}")

    rate = engagement_rate(args.impressions, args.likes, args.favorites, args.comments)
    append_metrics(today, args, log_file, rate)
    append_strategy_note(today, args, rate)

    if not args.no_notify:
        notify_result(today, args, rate)

    print(f"[ok] metrics appended: {METRICS}")
    print(f"[ok] strategy updated: {STRATEGY}")


if __name__ == "__main__":
    main()
