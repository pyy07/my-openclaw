#!/usr/bin/env python3
import json
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.failure_log import clear, log
DISCOVER = BASE_DIR / "scripts" / "discover_topics.sh"
DAILY = BASE_DIR / "scripts" / "daily_cycle.sh"
DRAFT = BASE_DIR / "scripts" / "create_review_draft.py"
LOG_DIR = BASE_DIR / "logs" / "cron"
LOG_FILE = LOG_DIR / f"run_cycle_{int(time.time())}.log"
NOTIFY = BASE_DIR / "scripts" / "notify_feishu.sh"

STEPS = [
    ("discover", [str(DISCOVER)]),
    ("daily", [str(DAILY), "start"]),
    ("draft", ["python3", str(DRAFT)]),
]


def notify(msg: str):
    subprocess.run([str(NOTIFY), msg], check=False)


def run_step(name: str, command) -> bool:
    for attempt in range(1, 4):
        try:
            subprocess.run(command, check=True)
            clear(name)
            return True
        except Exception as exc:
            log(name, str(exc), attempt)
            notify(f"[小红书自动运营] 失败 Step={name} attempt={attempt}: {exc}")
            if attempt >= 3:
                notify(f"[小红书自动运营] Step={name} 失败3次，停止执行：{exc}")
                return False
            time.sleep(5)
    return False


def main() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text(json.dumps({"status": "running"}), encoding="utf-8")

    for name, cmd in STEPS:
        if not run_step(name, cmd):
            LOG_FILE.write_text(json.dumps({"status": "failed", "step": name}), encoding="utf-8")
            return
    notify("[小红书自动运营] 定时任务完成，草稿与日志已生成。")
    LOG_FILE.write_text(json.dumps({"status": "ok"}), encoding="utf-8")


if __name__ == "__main__":
    main()
