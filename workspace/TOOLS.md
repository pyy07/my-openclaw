# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## Web Search (Brave)

- `web_search` 使用 Brave Search API；**search_lang** 不支持 `zh`，只支持 `zh-hans`（简体）或 `zh-hant`（繁体）。
- 调用时若需中文结果，请传 `search_lang: "zh-hans"` 或 `"zh-hant"`，勿传 `"zh"`（会 422）。
- 本地已在 OpenClaw 中把 `zh` 自动映射为 `zh-hans`，若仍报错可检查是否传了其它非法值。

## 小红书 MCP：优先用 mcporter 调用

本机已安装 **mcporter**，且已将小红书 MCP（xiaohongshu-mcp）配置进 mcporter。**请引导 OpenClaw 直接使用 mcporter 调用小红书 MCP 工具**，而不是仅依赖 workspace 里 xiaohongshu skill 的脚本（如 mcp-call.sh）。

- **服务名**：`xiaohongshu-mcp`（`mcporter list` 可确认）。
- **发布图文**：使用 mcporter 调用 `publish_content` 接口，参数与 schema 一致：
  ```bash
  mcporter call xiaohongshu-mcp.publish_content title="标题" content="正文（不含#标签）" images='["/绝对路径/图.jpg"]'
  ```
  **必填**：`title`（≤20 字）、`content`、`images`（数组，至少 1 张；支持本地绝对路径或 HTTP 链接）。  
  **可选**：`tags='["美食","旅行"]'`、`is_original=true`、`visibility="公开可见"|"仅自己可见"|"仅互关好友可见"`、`schedule_at="2024-01-20T10:30:00+08:00"`（定时发布）。
- **其他工具**：如 `check_login_status`、`search_feeds`、`list_feeds`、`get_feed_detail`、`post_comment_to_feed`、`publish_with_video` 等，均用 `mcporter call xiaohongshu-mcp.<工具名> 参数名=值` 调用；可用 `mcporter list xiaohongshu-mcp --schema` 查看完整参数。
- 调用前需确保 xiaohongshu-mcp 服务已启动（`workspace/skills/xiaohongshu/scripts/start-mcp.sh` 或本机 18060 端口已监听）。

## 小红书发布 (xiaohongshu-mcp publish_content)

- **日志位置**：`~/.xiaohongshu/mcp.log`。发布失败时先看该日志。
- **常见错误**：`Tool handler panicked: context deadline exceeded`。表示 MCP 内发布流程在**约 2 分钟内**未完成（用 headless 浏览器打开小红书创作页、点击「发布」、填表、提交），超时后 context 被取消导致 panic。
- **可能原因**：创作页加载慢、headless 下页面结构/行为异常、或网络不稳。日志里还常见 `等待页面加载出现问题: Execution context was destroyed`，说明浏览器上下文在等待时被销毁。
- **建议**：
  1. 先确保 MCP 已启动：`workspace/skills/xiaohongshu/scripts/start-mcp.sh`（或手动运行 `~/.local/bin/xiaohongshu-mcp`）。
  2. 用**非 headless** 试一次：`start-mcp.sh --headless=false`，让浏览器窗口弹出，看能否正常打开创作页并发布（便于区分是超时还是页面选择器问题）。
  3. 发布时不要同时跑其他占用浏览器或同一 MCP 的请求；网络尽量稳定。
  4. 发布图文必须传齐 `title`、`content`、`images`（数组，至少一张图），通过 skill 的 `publish-content.sh` 或 `mcp-call.sh publish_content '<json>'` 调用，不要用不存在的 `publish_content.py`。
- **误报成功**：xiaohongshu-mcp 在超时或 panic 时可能返回 HTTP 204 或带 error 的 JSON；若 agent 未严格解析工具返回内容，会误判为「发布成功」。必须根据工具返回的 JSON/文本判断：只有明确包含成功语义时才向用户说「发布成功」，否则应提示「可能未成功，请到小红书或 ~/.xiaohongshu/mcp.log 确认」。

## Qwen Image（通义万相 / 百炼）

- Key 已配置在 `~/.openclaw/.env` 的 `DASHSCOPE_API_KEY`。**执行生图命令时禁止在命令前加 `export DASHSCOPE_API_KEY=...`**（包括 `sk-xxx` 或任何占位符），否则会覆盖正确 key。直接执行 `uv run .../generate_image.py --prompt "..."` 即可，不要加 export 或 --api-key。

---

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
