#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DRAFT_REGISTRY = BASE_DIR / "data" / "draft_registry.csv"
NOTIFY = BASE_DIR / "scripts" / "notify_feishu.sh"


def parse_args():
    p = argparse.ArgumentParser(description="Register approved and published Xiaohongshu note")
    p.add_argument("--draft-id", required=True)
    p.add_argument("--note-id", required=True)
    p.add_argument("--published-at", default="", help="ISO datetime, default now")
    return p.parse_args()


def load_rows():
    if not DRAFT_REGISTRY.exists():
        raise SystemExit(f"draft registry not found: {DRAFT_REGISTRY}")
    with DRAFT_REGISTRY.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save_rows(rows):
    with DRAFT_REGISTRY.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def notify(msg: str):
    if NOTIFY.exists():
        subprocess.run([str(NOTIFY), msg], check=False)


def main():
    args = parse_args()
    rows = load_rows()

    target = None
    for row in rows:
        if row.get("draft_id") == args.draft_id:
            target = row
            break

    if target is None:
        raise SystemExit(f"draft id not found: {args.draft_id}")

    published_at = args.published_at or dt.datetime.now().isoformat(timespec="seconds")
    target["status"] = "published"
    target["note_id"] = args.note_id
    target["published_at"] = published_at

    save_rows(rows)

    notify(
        "[小红书自动运营] 已登记人工审核并发布\n"
        f"Draft ID: {args.draft_id}\n"
        f"Note ID: {args.note_id}\n"
        f"Published At: {published_at}"
    )

    print(f"[ok] registered published note: draft={args.draft_id} note={args.note_id}")


if __name__ == "__main__":
    main()
