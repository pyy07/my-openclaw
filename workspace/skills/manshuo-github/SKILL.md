---
name: manshuo-github
description: |
  公众号「漫说GitHub」系列运营。使用场景：
  - “今天帮我找几个值得写的 GitHub 项目”
  - “跑一下漫说GitHub 每日探索”
  - “按漫说GitHub 流程发我 review”
---

# 漫说GitHub — 公众号系列运营

本 skill 用于**每日探索 GitHub**，筛选 2～3 个值得介绍的仓库，撰写约 100 字介绍 + 2～3 个推荐点（标签），连同仓库地址一并产出，供你审核后用于公众号「漫说GitHub」系列文章。执行过程**每步记录**，**成功或失败均通过飞书通知**。

## 0. 目标与边界

- **系列定位**：漫说GitHub — 以专业人士眼光，向小白用户介绍有趣、有用的 GitHub 项目。
- **每期内容**：2～3 个仓库；每个仓库：约 100 字介绍 + 2～3 个推荐点（标签）+ 仓库地址。
- **边界**：只做探索与草稿，不自动发布；产出必须发飞书给你 review，通过后你自行排版/发布。
- **同日多次探索**：若一天内多次运行本流程，每次再精选 2～3 个**新**仓库，**追加**到当日草稿文件 `drafts/review/YYYY-MM-DD-manshuo-github.md` 末尾（序号接续），飞书 review 须包含**本轮**新增的仓库信息。

## 1. 每日执行流程（必须按序执行并记录）

执行时**每一步**都要写入步骤日志；**结束**时（成功或失败）必须用飞书通知你。

1. **记录开始**  
   在 `logs/daily/YYYY-MM-DD.md` 创建或追加本日运行记录，写下「开始时间」与「步骤 1：开始探索」。

2. **探索 GitHub**  
   使用 **OpenClaw 的 github skill**（openclaw-github-assistant）：调用 `list_repos`、`search_repos` 或 `get_repo`（不要用 mcporter 或 Cursor 的 GitHub MCP）。按「推荐选题标准」（见下）筛选候选仓库。  
   在日志中记录：本步完成时间、使用的接口与参数、候选数量。  
   **若探索失败**（如认证错误、无可用工具）：仍必须完成步骤 6、7，用 `notify_feishu.sh` 发一条失败原因给你。

3. **精选 2～3 个仓库**  
   从候选中挑出 2～3 个最符合「漫说GitHub」调性的仓库（有趣、有料、对小白友好）。  
   在日志中记录：最终入选的 repo 名称与理由（一句话）。

4. **撰写介绍与推荐点**  
   对每个仓库：
   - 写约 **100 字** 介绍（专业人士视角、小白能懂的语言）；
   - 提炼 **2～3 个推荐点**（可作为标签或小标题）。
   - 保留 **仓库地址**（如 `https://github.com/owner/repo`）。  
   在日志中记录：本步完成时间。

5. **写入当日草稿**  
   - 草稿路径**固定**：`drafts/review/YYYY-MM-DD-manshuo-github.md`。日期**必须与当日日志文件完全一致**（即与 `logs/daily/YYYY-MM-DD.md` 同一天，含年份，避免 2025/2026 混用导致草稿缺失）。skill 根目录为 `/Users/lukepan/.openclaw/workspace/skills/manshuo-github`。  
   - **若当日草稿已存在**（例如同日已跑过探索）：将**本轮**撰写的 2～3 个仓库块**追加**到该文件末尾，序号接续**（如已有 ## 1～3，则本轮为 ## 4、## 5、## 6）**，不覆盖原有内容。  
   - **若当日草稿不存在**：新建该文件，写入本轮 2～3 个仓库的完整块。  
   - 本步**不可跳过**：必须把步骤 4 的内容写入上述路径后再进行步骤 6。

6. **飞书发送给你 review**  
   调用 `notify_feishu.sh`，发送内容**必须包含本轮的 GitHub 项目信息**，不得只发「请查收」或路径。至少包含：  
   - 本轮推荐的 2～3 个仓库：**每个仓库的名称（owner/repo）、约一句话介绍、仓库链接**；  
   - 可再附「完整草稿路径：drafts/review/YYYY-MM-DD-manshuo-github.md」。  
   若单条消息过长，可发两条：第一条为「本轮推荐：1. xxx 一句话 + 链接；2. ...」，第二条为草稿路径。

7. **记录结束并飞书通知结果（强制）**  
   - 在 `logs/daily/YYYY-MM-DD.md` 写下「步骤 7：结束」、状态（成功/失败）、简要原因（若失败）。  
   - **无论成功或失败**，都必须执行一次：`/Users/lukepan/.openclaw/workspace/skills/manshuo-github/scripts/notify_feishu.sh "消息"`  
   - 成功：消息为「漫说GitHub 今日探索完成，已发 review（含本轮推荐仓库），请查收。」  
   - 失败：消息为「漫说GitHub 今日探索失败：原因简述」（如认证失败、无仓库数据等），便于你排查或重跑。

## 2. 草稿格式示例

每个仓库占一块，格式如下（可写入 `drafts/review/YYYY-MM-DD-manshuo-github.md`）：

```markdown
## 1. 仓库名 (owner/repo)

**简介**（约 100 字）：用专业人士视角、小白能懂的话说明这是啥、解决什么问题、为啥值得关注。

**推荐点**（2～3 个标签）：如 `开源替代`、`上手简单`、`文档友好`、`适合学习` 等。

**仓库**：https://github.com/owner/repo
```

## 3. 推荐选题标准

- **有趣 / 有用**：能解决实际问题、或技术/产品上有亮点、或适合做「冷门但好用」的科普。
- **对小白友好**：仓库有 README、有清晰用途说明，便于用 100 字讲清楚「这是啥、为啥值得用」。
- **适合公众号**：避免纯学术或过于冷门；可偏工具、效率、开源产品、有意思的 side project。

## 4. 实操命令与脚本

### 4.1 执行每日探索（由 Agent 按 SKILL 流程执行）

由 **Agent** 在加载本 skill 后，按「每日执行流程」执行：  
先创建/追加 `logs/daily/YYYY-MM-DD.md`，再用 **github** skill（openclaw-github-assistant）的 list_repos / search_repos / get_repo 探索仓库、写草稿、调飞书通知。需在 OpenClaw 中启用 github skill 并配置 GITHUB_TOKEN（见 references/github-auth.md）。

若用 cron 触发：在 OpenClaw 的 cron 中配置每日任务，触发一个加载了本 skill 的 agent，让其按本 skill 执行探索 → 写稿 → 发飞书；或先执行 `./scripts/run_daily_exploration.sh` 再在会话中让 agent 继续步骤 2～7。

### 4.2 飞书通知脚本

**注意**：cron 或 Agent 的 cwd 常为 `~/.openclaw/workspace`，此时不要用 `workspace/skills/...`（会变成 workspace/workspace/...）。请用**绝对路径**调用脚本：

```bash
/Users/lukepan/.openclaw/workspace/skills/manshuo-github/scripts/notify_feishu.sh "消息正文"
```

或在 skill 目录下执行：

```bash
cd /Users/lukepan/.openclaw/workspace/skills/manshuo-github
./scripts/notify_feishu.sh "消息正文"
```

环境变量（可选）：

- `MANSHUO_GITHUB_FEISHU_TARGET`：飞书接收人，默认同小红书 skill 的 `user:ou_27eafc99a5b351d7df9ca5709e74ea41`
- `MANSHUO_GITHUB_CHANNEL`：通道，默认 `feishu`

### 4.3 步骤日志与草稿路径（日期一致）

- 每日日志：`logs/daily/YYYY-MM-DD.md`
- 当日草稿：`drafts/review/YYYY-MM-DD-manshuo-github.md`（**与日志用同一天日期**，同日多次探索时**追加**到该文件，不新建文件）

## 5. 步骤记录规范（强制）

`logs/daily/YYYY-MM-DD.md` 至少包含：

- 开始时间、结束时间
- 每一步的序号与完成时间（如：步骤 2：探索 GitHub，完成于 HH:MM）
- 候选/入选仓库简要信息
- 最终状态：成功 / 失败；若失败，原因简述

## 6. 飞书通知规范（强制）

- **步骤 6（review）**：发飞书时必须带**本轮推荐的 2～3 个仓库**的名称、一句话介绍、链接，不得只发「请查收」或草稿路径。
- **步骤 7（结果）**：每次运行结束（无论成功失败）都必须再发一条。成功：告知「探索完成，review 已发」或草稿路径；失败：告知「探索失败」+ 简短原因。

## 7. 响应模板（给用户汇报）

执行完成后向用户汇报时，可固定包含：

1. 今日探索是否成功
2. 入选的 2～3 个仓库名称与链接
3. 草稿路径与飞书是否已发
4. 若失败：原因与建议（如改日再跑、调整选题标准等）
