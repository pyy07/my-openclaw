---
name: xiaohongshu
description: |
  小红书内容工具。使用场景：
  - 搜索小红书内容
  - 获取首页推荐列表
  - 获取帖子详情（包括互动数据和评论）
  - 发表评论到帖子
  - 获取用户个人主页
  - "跟踪一下小红书上的XX热点"
  - "分析小红书上关于XX的讨论"
  - "小红书XX话题报告"
  - "生成XX的小红书舆情报告"
---

# 小红书 MCP Skill

基于 [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) 封装。

> **完整文档请查看 [README.md](README.md)**

## 优先使用 mcporter 调用 MCP（推荐）

本工作区内 OpenClaw 已启用 **mcporter**，且小红书 MCP 已配置为 mcporter 的 `xiaohongshu-mcp` 服务。**执行小红书相关能力时，优先用 mcporter 直接调用 MCP 工具**，与 Cursor/IDE 侧使用同一套接口和 schema。

- **发布图文**（`publish_content`）：
  ```bash
  mcporter call xiaohongshu-mcp.publish_content title="标题" content="正文（不要带#标签）" images='["/绝对路径/图.jpg"]'
  ```
  必填：`title`（最多 20 字）、`content`、`images`（至少 1 张，本地路径或 HTTP 链接）。可选：`tags='["标签1","标签2"]'`、`is_original=true`、`visibility="公开可见"|"仅自己可见"|"仅互关好友可见"`、`schedule_at="ISO8601 时间"`。
- **查看接口与参数**：`mcporter list xiaohongshu-mcp --schema`。
- 若 mcporter 不可用或调用失败，再退而使用本 skill 的脚本（如 `scripts/mcp-call.sh`、`scripts/publish-content.sh`）。调用前请确保 MCP 服务已启动（`scripts/start-mcp.sh`）。

## 快速参考

| 脚本 | 用途 |
|------|------|
| `install-check.sh` | 检查依赖是否安装 |
| `start-mcp.sh` | 启动 MCP 服务 |
| `stop-mcp.sh` | 停止 MCP 服务 |
| `status.sh` | 检查登录状态 |
| `search.sh <关键词>` | 搜索内容 |
| `recommend.sh` | 获取推荐列表 |
| `post-detail.sh <feed_id> <xsec_token>` | 获取帖子详情 |
| `comment.sh <feed_id> <xsec_token> <内容>` | 发表评论 |
| `user-profile.sh <user_id>` | 获取用户主页 |
| `track-topic.sh <话题> [选项]` | 热点跟踪报告 |
| `export-long-image.sh` | 帖子导出为长图（白底黑字+图片拼接） |
| `mcp-call.sh <tool> [args]` | 通用工具调用 |

## 快速开始

```bash
cd scripts/

# 1. 检查依赖
./install-check.sh

# 2. 启动服务
./start-mcp.sh

# 3. 检查状态
./status.sh

# 4. 搜索内容
./search.sh "春节旅游"
```

## MCP 工具

| 工具名 | 描述 |
|--------|------|
| `check_login_status` | 检查登录状态 |
| `search_feeds` | 搜索内容 |
| `list_feeds` | 获取首页推荐 |
| `get_feed_detail` | 获取帖子详情和评论 |
| `post_comment_to_feed` | 发表评论 |
| `reply_comment_in_feed` | 回复评论 |
| `user_profile` | 获取用户主页 |
| `like_feed` | 点赞/取消 |
| `favorite_feed` | 收藏/取消 |
| `publish_content` | 发布图文笔记（推荐：`mcporter call xiaohongshu-mcp.publish_content title=... content=... images='[...]'`） |
| `publish_with_video` | 发布视频笔记 |

## 发布图文 / 视频时的成功判定（重要）

**禁止在未确认工具明确返回成功时向用户声称「发布成功」。**

- `publish_content` / `publish_with_video` 调用后，**必须根据工具返回的完整内容判断**：
  - 若返回内容中包含 `error`、`panic`、`context deadline exceeded`、`Execution context was destroyed` 等，或请求长时间（如接近 2 分钟）后返回空/异常，**一律视为发布失败**，应向用户说明「发布可能未成功，请到小红书账号或 ~/.xiaohongshu/mcp.log 确认」。
  - 只有工具返回中**明确**包含成功含义（如成功发布、笔记 ID、已发布等）时，才能告知用户「发布成功」。
- 若无法从返回内容判断（如超时无响应、返回被截断），**不要假设成功**，应告知用户「未收到明确成功结果，请自行到小红书查看或查看 MCP 日志」。

## 热点跟踪

```bash
./track-topic.sh "DeepSeek" --limit 5
./track-topic.sh "春节旅游" --limit 10 --output report.md
./track-topic.sh "iPhone 16" --limit 5 --feishu
```

## 长图导出

搜索结果或帖子详情导出为带文字注释的 JPG 长图：

```bash
# 准备 posts.json（搜索+拉详情后整理）
cat > posts.json << 'EOF'
[
  {
    "title": "帖子标题",
    "author": "作者名",
    "stats": "1.3万赞 100收藏",
    "desc": "正文摘要，支持\n换行",
    "images": ["https://...webp", "https://...webp"],
    "per_image_text": {"1": "第2张图的专属说明"}
  }
]
EOF

./export-long-image.sh --posts-file posts.json -o output.jpg
```

样式：白底黑字（模仿小红书原样），每个帖子前有文字块（标题+作者+正文），帖子间有分隔线。

**per_image_text** 可选：如果原帖文字明确指向某张图（如"图7-9是青龙桥"），把说明放在对应图片上方。未指定则所有文字集中在文字块。

**字体**：自动检测系统中文字体（STHeiti > Hiragino > Arial Unicode > Noto CJK）。

## 注意事项

- 首次运行会下载 headless 浏览器（~150MB）
- 同一账号避免多客户端同时使用
- 发布限制：标题≤20字符，正文≤1000字符，日发布≤50条
- Linux 服务器需要从本地获取 cookies，详见 [README.md](README.md)
