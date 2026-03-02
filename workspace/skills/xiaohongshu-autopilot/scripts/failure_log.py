#!/usr/bin/env python3
import json
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "logs" / "failure_log.json"


def load():
    if not LOG.exists():
        return {}
    try:
        return json.loads(LOG.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save(data):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def log(step, reason, attempt):
    data = load()
    data[step] = {
        "reason": reason,
        "attempts": attempt,
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }
    save(data)


def clear(step):
    data = load()
    if step in data:
        del data[step]
        save(data)


def entries():
    return load()

if __name__ == "__main__":
    import pprint
    pprint.pprint(entries())
