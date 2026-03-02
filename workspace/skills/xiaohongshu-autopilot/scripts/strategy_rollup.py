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
DRAFT_REGISTRY = BASE_DIR / "data" / "draft_registry.csv"
NOTIFY = BASE_DIR / "scripts" / "notify_feishu.sh"


def parse_args():
    p = argparse.ArgumentParser(description="Roll up daily ops result into strategy files")
    p.add_argument("--date", help="Target date (YYYY-MM-DD), default=today")
    p.add_argument("--draft-id", default="", help="Draft id in draft_registry.csv")
    p.add_argument("--post-id", default="", help="Post id")
    p.add_argument("--image-prompts", default="", help="Image prompts joined by ' || '")
    p.add_argument("--image-files", default="", help="Image file paths joined by ' || '")
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


def resolve_post_id(args) -> str:
    if args.post_id:
        return args.post_id
    if not args.draft_id:
        return ""
    if not DRAFT_REGISTRY.exists():
        return ""

    with DRAFT_REGISTRY.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("draft_id") == args.draft_id:
                return row.get("note_id", "")
    return ""


def resolve_asset_meta(args) -> tuple[str, str]:
    if args.image_prompts or args.image_files:
        return args.image_prompts, args.image_files
    if not args.draft_id or not DRAFT_REGISTRY.exists():
        return "", ""
    with DRAFT_REGISTRY.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("draft_id") == args.draft_id:
                return row.get("image_prompts", ""), row.get("image_files", "")
    return "", ""


def append_metrics(date_str: str, args, log_file: Path, rate: float, post_id: str, image_prompts: str, image_files: str):
    row = {
        "date": date_str,
        "draft_id": args.draft_id,
        "post_id": post_id,
        "theme": args.theme,
        "goal": args.goal,
        "image_prompts": image_prompts,
        "image_files": image_files,
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
                "draft_id",
                "post_id",
                "theme",
                "goal",
                "image_prompts",
                "image_files",
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


def append_strategy_note(date_str: str, args, rate: float, post_id: str):
    if not STRATEGY.exists():
        STRATEGY.write_text("# 小红书美妆穿搭策略库\n\n", encoding="utf-8")

    label = {
        "keep": "保留",
        "iterate": "迭代",
        "drop": "淘汰",
    }[args.decision]

    note = (
        f"\n- {date_str} | 主题:{args.theme or '-'} | 目标:{args.goal or '-'}"
        f" | NoteID:{post_id or '-'} | 互动率:{rate:.2%} | 结论:{label}"
        f" | 证据: logs/daily/{date_str}.md"
    )

    text = STRATEGY.read_text(encoding="utf-8")
    marker = "## 证据索引"
    if marker in text:
        text = text.replace(marker, marker + note)
    else:
        text = text + "\n## 证据索引" + note + "\n"
    STRATEGY.write_text(text, encoding="utf-8")


def update_draft_registry(args, rate: float):
    if not args.draft_id or not DRAFT_REGISTRY.exists():
        return

    rows = []
    updated = False
    now = dt.datetime.now().isoformat(timespec="seconds")

    with DRAFT_REGISTRY.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row.get("draft_id") == args.draft_id:
                row["last_metrics_at"] = now
                row["north_star"] = f"{rate:.4f}"
                if row.get("status") == "pending_review":
                    row["status"] = "metrics_collected"
                updated = True
            rows.append(row)

    if updated and fieldnames:
        with DRAFT_REGISTRY.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def notify_result(date_str: str, args, rate: float, post_id: str, image_files: str):
    if not NOTIFY.exists():
        return

    decision_zh = {
        "keep": "保留",
        "iterate": "迭代",
        "drop": "淘汰",
    }[args.decision]

    msg = (
        "[小红书自动运营] 北极星指标回收完成\n"
        f"日期: {date_str}\n"
        f"Draft ID: {args.draft_id or '-'}\n"
        f"Note ID: {post_id or '-'}\n"
        f"主题: {args.theme or '-'}\n"
        f"目标: {args.goal or '-'}\n"
        f"数据: 曝光{args.impressions}, 点赞{args.likes}, 收藏{args.favorites}, 评论{args.comments}\n"
        f"北极星(互动率): {rate:.2%}\n"
        f"素材图片: {image_files or '-'}\n"
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
    post_id = resolve_post_id(args)
    image_prompts, image_files = resolve_asset_meta(args)

    append_metrics(today, args, log_file, rate, post_id, image_prompts, image_files)
    append_strategy_note(today, args, rate, post_id)
    update_draft_registry(args, rate)

    if not args.no_notify:
        notify_result(today, args, rate, post_id, image_files)

    print(f"[ok] metrics appended: {METRICS}")
    print(f"[ok] strategy updated: {STRATEGY}")
    if args.draft_id:
        print(f"[ok] draft registry updated: {DRAFT_REGISTRY}")


if __name__ == "__main__":
    main()
