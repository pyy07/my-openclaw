#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DRAFT_DIR = BASE_DIR / "drafts" / "pending"
DATA_DIR = BASE_DIR / "data"
DRAFT_REGISTRY = DATA_DIR / "draft_registry.csv"
CONTENT_STRATEGY = DATA_DIR / "content_strategy.json"
NOTIFY = BASE_DIR / "scripts" / "notify_feishu.sh"
QWEN_IMAGE_SCRIPT = Path("/Users/lukepan/.openclaw/workspace/skills/qwen-image/scripts/generate_image.py")
IMAGE_DIR = Path("/Users/lukepan/.openclaw/workspace/media/xhs-assets")
OPENCLAW_ENV = Path("/Users/lukepan/.openclaw/.env")


def parse_args():
    p = argparse.ArgumentParser(description="Generate Xiaohongshu draft for manual review")
    p.add_argument("--date", help="date YYYY-MM-DD, default=today")
    p.add_argument("--goal", default="验证问题式标题对收藏率影响")
    p.add_argument("--theme", default=None, help="content theme; default from data/content_strategy.json")
    p.add_argument("--generate-images", action="store_true", dest="generate_images", help="Generate images via qwen-image (default)")
    p.add_argument("--no-generate-images", action="store_false", dest="generate_images", help="Disable image generation")
    p.add_argument("--image-size", default="720*1280", choices=["1664*928", "1024*1024", "720*1280", "1280*720"])
    p.add_argument("--no-notify", action="store_true")
    p.set_defaults(generate_images=True)
    return p.parse_args()


def load_content_strategy() -> dict:
    """从 data/content_strategy.json 加载运营策略下的内容配置（按主题）。"""
    if not CONTENT_STRATEGY.exists():
        raise FileNotFoundError(
            f"内容策略文件不存在: {CONTENT_STRATEGY}\n"
            "请创建 data/content_strategy.json，参考 SKILL.md 或现有 themes 结构。"
        )
    raw = json.loads(CONTENT_STRATEGY.read_text(encoding="utf-8"))
    return raw


def get_theme_content(strategy: dict, theme: str) -> dict:
    """按主题取内容配置；若无该主题则用 default_theme。"""
    themes = strategy.get("themes") or {}
    if theme in themes:
        return themes[theme]
    default = strategy.get("default_theme") or "通勤妆"
    if default in themes:
        return themes[default]
    if themes:
        return next(iter(themes.values()))
    raise KeyError(f"content_strategy.json 中无主题 '{theme}' 且无 default_theme 或 themes 为空")


def substitute_theme(value, theme: str):
    """对字符串做 {theme} 替换；对 list/dict 递归处理。"""
    if isinstance(value, str):
        return value.replace("{theme}", theme)
    if isinstance(value, list):
        return [substitute_theme(x, theme) for x in value]
    if isinstance(value, dict):
        return {k: substitute_theme(v, theme) for k, v in value.items()}
    return value


def make_titles(theme: str, content: dict) -> list[str]:
    """由运营策略中的 titles 模板生成标题列表（支持 {theme}）。"""
    raw = content.get("titles") or []
    return substitute_theme(raw, theme)


def make_content(theme: str, content: dict) -> tuple[str, list[str]]:
    """由运营策略中的 body、tags 生成正文与标签（支持 {theme}）。"""
    body = content.get("body") or ""
    tags = content.get("tags") or []
    return substitute_theme(body, theme), substitute_theme(tags, theme)


def make_assets(theme: str, content: dict) -> dict:
    """由运营策略中的 assets 生成素材方案（支持 {theme}）。"""
    assets = content.get("assets") or {}
    return substitute_theme(assets, theme)


def write_registry(row: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    exists = DRAFT_REGISTRY.exists()
    with DRAFT_REGISTRY.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "draft_id",
                "date",
                "theme",
                "goal",
                "title",
                "status",
                "draft_file",
                "note_id",
                "published_at",
                "last_metrics_at",
                "north_star",
                "image_prompts",
                "image_files",
                "image_generation_status",
            ],
        )
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def split_text(text: str, chunk_size: int = 1200):
    chunks = []
    s = text.strip()
    while s:
        if len(s) <= chunk_size:
            chunks.append(s)
            break
        cut = s.rfind("\n", 0, chunk_size)
        if cut <= 0:
            cut = chunk_size
        chunks.append(s[:cut].strip())
        s = s[cut:].strip()
    return chunks


def notify(text: str):
    if not NOTIFY.exists():
        return
    subprocess.run([str(NOTIFY), text], check=False)


def notify_with_media(text: str, media: str):
    if not NOTIFY.exists():
        return
    subprocess.run([str(NOTIFY), "--media", media, text], check=False)


def load_env_file(path: Path, env: dict):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        k, v = raw.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in env:
            env[k] = v


def generate_images(draft_id: str, prompts: list[str], size: str) -> tuple[list[str], str]:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not QWEN_IMAGE_SCRIPT.exists():
        return [], "qwen-image-script-missing"

    image_files = []
    env = os.environ.copy()
    load_env_file(OPENCLAW_ENV, env)

    for idx, prompt in enumerate(prompts, start=1):
        filename = IMAGE_DIR / f"{draft_id}-{idx}.png"
        if shutil.which("uv"):
            cmd = ["uv", "run", str(QWEN_IMAGE_SCRIPT), "--prompt", prompt, "--filename", str(filename), "--size", size]
        else:
            cmd = [sys.executable, str(QWEN_IMAGE_SCRIPT), "--prompt", prompt, "--filename", str(filename), "--size", size]

        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if result.returncode == 0 and filename.exists():
            image_files.append(str(filename))

    if not image_files:
        return [], "failed"
    if len(image_files) < len(prompts):
        return image_files, "partial"
    return image_files, "generated"


def main():
    args = parse_args()
    strategy = load_content_strategy()
    theme = args.theme or strategy.get("default_theme") or "通勤妆"
    content = get_theme_content(strategy, theme)

    now = dt.datetime.now()
    date_str = args.date or now.date().isoformat()
    draft_id = f"xhs-draft-{now.strftime('%Y%m%d-%H%M%S')}"
    should_generate_images = args.generate_images

    titles = make_titles(theme, content)
    body, tags = make_content(theme, content)
    assets = make_assets(theme, content)
    image_prompts = assets.get("image_prompts") or []
    image_files: list[str] = []
    image_generation_status = "not_requested"
    if should_generate_images:
        image_files, image_generation_status = generate_images(draft_id, image_prompts, args.image_size)

    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    draft_file = DRAFT_DIR / f"{draft_id}.md"

    draft_md = f"""# 小红书发布草稿（待审核）

- Draft ID: {draft_id}
- 日期: {date_str}
- 主题: {theme}
- 实验目标: {args.goal}
- 状态: 待审核（未发布）

## 标题候选
{chr(10).join(f"{i+1}. {t}" for i, t in enumerate(titles))}

## 正文（建议稿）
{body}

## 标签（发布时单独填写）
{' '.join('#'+t for t in tags)}

## 素材方案
- 封面文案: {assets['cover_text']}
- 封面样式: {assets['cover_style']}

### 图文镜头清单
{chr(10).join('- ' + s for s in assets.get('shot_list', []))}

### 素材生成提示词（可给生图工具）
{chr(10).join('- ' + p for p in image_prompts)}

### 素材文件
{chr(10).join('- ' + (image_files[i] if i < len(image_files) else '待生成') for i in range(len(image_prompts)))}

## 审核通过后登记（手动发布后执行）
```bash
cd /Users/lukepan/.openclaw/workspace/skills/xiaohongshu-autopilot
./scripts/register_published_note.py --draft-id {draft_id} --note-id <小红书笔记ID>
```
"""

    draft_file.write_text(draft_md, encoding="utf-8")

    write_registry(
        {
            "draft_id": draft_id,
            "date": date_str,
            "theme": theme,
            "goal": args.goal,
            "title": titles[0] if titles else "",
            "status": "pending_review",
            "draft_file": str(draft_file),
            "note_id": "",
            "published_at": "",
            "last_metrics_at": "",
            "north_star": "",
            "image_prompts": " || ".join(image_prompts),
            "image_files": " || ".join(image_files),
            "image_generation_status": image_generation_status,
        }
    )

    if not args.no_notify:
        notify(
            "[小红书自动运营] 新草稿待你审核\n"
            f"Draft ID: {draft_id}\n"
            f"主题: {theme}\n"
            f"目标: {args.goal}\n"
            f"文件: {draft_file}\n"
            f"图片生成状态: {image_generation_status}"
        )
        for idx, chunk in enumerate(split_text(draft_md), start=1):
            notify(f"[草稿内容 {idx}]\n{chunk}")
        for idx, image in enumerate(image_files, start=1):
            notify_with_media(f"[草稿素材图 {idx}] Draft ID: {draft_id}", image)

    print(f"[ok] draft created: {draft_file}")
    print(f"[ok] draft id: {draft_id}")


if __name__ == "__main__":
    main()
