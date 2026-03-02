---
name: qwen-image
description: Generate images using Qwen Image API (Alibaba Cloud DashScope). Use when users request image generation with Chinese prompts or need high-quality AI-generated images from text descriptions.
homepage: https://dashscope.aliyuncs.com/
metadata: {"openclaw":{"emoji":"🎨","requires":{"bins":["uv"]},"install":[{"id":"uv-brew","kind":"brew","formula":"uv","bins":["uv"],"label":"Install uv (brew)"}]}}
---

# Qwen Image

Generate high-quality images using Alibaba Cloud's Qwen Image API (通义万相).

## Usage

**必须遵守（否则会覆盖正确 key）：**
- **禁止**在命令前加 `export DASHSCOPE_API_KEY=...`（包括 `sk-xxx` 或任何占位符）。这样会覆盖已在 `~/.openclaw/.env` 或 OpenClaw 中配置的正确 key，导致认证失败。
- **禁止**传 `--api-key` 参数（脚本会从环境或 `~/.openclaw/.env` 读取）。
- **直接**执行 `uv run {baseDir}/scripts/generate_image.py --prompt "..."` 即可，不要加任何 export 或 --api-key。

Generate an image (returns URL only):
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "一副典雅庄重的对联悬挂于厅堂之中" --size "1664*928"
```

Generate and save locally:
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "一副典雅庄重的对联悬挂于厅堂之中" --size "1664*928" --filename output.png
```

**若要发到飞书**：先把图存到 **workspace 目录下**（如 `workspace/media/图名.png`），再发 message，可减少飞书「只发路径不发图」的回退问题。例如：
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "..." --filename workspace/media/生成的图.png
```
脚本会输出 `MEDIA: <workspace 内路径>`，发飞书时用该路径作为附件。

With custom model:
Support `qwen-image-max-2025-12-30` `qwen-image-plus-2026-01-09` `qwen-image-plus`
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "a beautiful sunset over mountains" --model qwen-image-plus-2026-01-09
```

## API Key

- **本机已配置**：Key 写在 `~/.openclaw/.env` 的 `DASHSCOPE_API_KEY`，openclaw.json 通过 `${DASHSCOPE_API_KEY}` 引用。执行脚本时**不要**加 `--api-key`，否则 agent 容易误填占位符 `sk-xxx` 导致失败。
- 若需自行获取：https://dashscope.console.aliyun.com/

## Options
**Sizes:**
- `1664*928` (default) - 16:9 landscape
- `1024*1024` - Square format
- `720*1280` - 9:16 portrait
- `1280*720` - 16:9 landscape (smaller)

**Additional flags:**
- `--negative-prompt "unwanted elements"` - Specify what to avoid
- `--no-prompt-extend` - Disable automatic prompt enhancement
- `--watermark` - Add watermark to generated image
- `--no-verify-ssl` - Disable SSL certificate verification (use when behind corporate proxy)

## Workflow

1. Execute the generate_image.py script with the user's prompt
2. Parse the script output and find the line starting with `MEDIA_URL:`
3. Extract the image URL from that line (format: `MEDIA_URL: https://...`)
4. Display the image to the user using markdown syntax: `![Generated Image](URL)`
5. Do NOT download or save the image unless the user specifically requests it

## Notes

- Supports both Chinese and English prompts
- By default, returns image URL directly without downloading
- The script prints `MEDIA_URL:` in the output - extract this URL and display it using markdown image syntax: `![generated image](URL)`
- Always look for the line starting with `MEDIA_URL:` in the script output and render the image for the user
- Default negative prompt helps avoid common AI artifacts
- Images are hosted on Alibaba Cloud OSS with temporary access URLs
- **飞书发图**：若用户要发到飞书，用 `--filename workspace/media/xxx.png` 把图存到 workspace 下，再发 message，可避免飞书插件上传失败时只发路径文本的问题（详见 workspace/TOOLS.md「飞书发图」）
