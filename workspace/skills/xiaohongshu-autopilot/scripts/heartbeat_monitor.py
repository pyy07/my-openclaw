#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "logs" / "failure_log.json"


def load_failures():
    if not LOG.exists():
        return {}
    with LOG.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def notify(message):
    notify_script = Path(__file__).resolve().parents[1] / "scripts" / "notify_feishu.sh"
    subprocess.run([str(notify_script), message], check=False)


def main():
    failures = load_failures()
    pending = {k: v for k, v in failures.items() if v.get("attempts", 0) < 3}
    if not pending:
        return

    notify("[小红书自动运营] heartbeat 发现未完成步骤，将重试")
    subprocess.run(["./scripts/run_exploration_cycle.sh"], cwd=Path(__file__).resolve().parents[1], check=False)

    for name, info in failures.items():
        if info.get("attempts", 0) >= 3:
            notify(f"[小红书自动运营] Step={name} 已失败 3 次，停止重试：{info.get('reason')}")


if __name__ == "__main__":
    main()
