---
name: xiaohongshu-autopilot
description: |
  小红书美妆/服装账号自动运营 skill。使用场景：
  - “帮我运营小红书账号”
  - “按美妆、穿搭博主人设做每日内容实验”
  - “记录今天运营动作并复盘”
  - “持续迭代小红书增长策略”
---

# 小红书自动运营（美妆 + 服装）

此 skill 用于在本机 OpenClaw 环境中，执行“每日探索 + 草稿送审 + 人工发布 + 指标复盘 + 策略沉淀”的闭环运营。

## 0. 目标与边界

- 目标：在 30 天内形成可复制的美妆/服装账号增长策略。
- 方式：每天最少 1 个可验证实验，记录动作和结果，用数据更新策略。
- 边界：前期不自动发布；必须先发飞书给你审核，通过后你人工发布。

## 1. 人设（固定）

默认人设见 [references/persona.md](references/persona.md)。

执行时必须保持：
- 账号定位：`通勤实用型美妆穿搭博主`
- 内容占比：`美妆 60%`、`服装穿搭 40%`
- 语气：真实、可复制、少空话，多步骤与避坑

## 2. 每日执行循环（必须完整执行）

每天按以下顺序执行：

1. 运行探索脚本，产出当天素材池（自动飞书汇报开始+结束）
2. 创建每日日志模板
3. 自动生成“标题+正文+素材方案”草稿，调用 qwen-image 生成图片，并发飞书给你审核
4. 你审核并人工发布后，登记笔记 ID
5. 回收曝光/点赞/收藏/评论，计算北极星指标（互动率）
6. 更新策略库（保留、迭代、淘汰）

## 3. 实操命令

### 3.1 自动探索并送审（不自动发布）

```bash
cd /Users/lukepan/.openclaw/workspace/skills/xiaohongshu-autopilot
./scripts/run_exploration_cycle.sh
```

### 3.2 人工发布后登记笔记ID

```bash
cd /Users/lukepan/.openclaw/workspace/skills/xiaohongshu-autopilot
./scripts/register_published_note.py --draft-id <draft_id> --note-id <小红书笔记ID>
```

### 3.3 回收北极星指标并更新策略

```bash
cd /Users/lukepan/.openclaw/workspace/skills/xiaohongshu-autopilot
./scripts/strategy_rollup.py --date YYYY-MM-DD --draft-id <draft_id> --theme "通勤妆" --goal "验证问题式标题" --impressions 1000 --likes 40 --favorites 20 --comments 10 --decision iterate
```

## 4. 飞书汇报（固定接收人）

默认发送目标：`user:ou_27eafc99a5b351d7df9ca5709e74ea41`

发送脚本：`scripts/notify_feishu.sh`

可选环境变量：

```bash
export XHS_AUTOPILOT_FEISHU_TARGET="user:ou_27eafc99a5b351d7df9ca5709e74ea41"
export XHS_AUTOPILOT_CHANNEL="feishu"
```

若飞书发送失败，消息会进入 `logs/notifications/YYYY-MM-DD-outbox.ndjson`，便于补发。

## 5. 异常/重试机制

- `scripts/run_exploration_cycle.py` 按步骤执行推荐/日志/草稿，单步失败后会写入 `logs/failure_log.json`、重试最多 3 次，并在每次失败时通知你；超过 3 次后才会将“永久失败”消息发到飞书并停止。
- heartbeat 需要配置执行 `python3 scripts/heartbeat_monitor.py`。它会扫 `logs/failure_log.json` 里未完成的步骤、自动再次运行 `./scripts/run_exploration_cycle.sh`，并在达上限后告知失败原因。

## 6. 台账与内容策略

- 草稿台账：`data/draft_registry.csv`
- 指标台账：`data/metrics.csv`
- 策略主文件：`data/strategy.md`
- **内容策略**：`data/content_strategy.json` — 标题、正文、标签、封面文案、镜头清单、生图提示词等均由该文件按**主题**驱动；修改后重新跑 `create_review_draft` 即生效。结构：`default_theme` + `themes.<主题>.titles / body / tags / assets`，正文与字符串中可用 `{theme}` 占位符。

要求：每条指标记录都要能回溯到 `draft_id` 或 `note_id`，并包含素材提示词(`image_prompts`)与图片路径(`image_files`)。

## 7. 记录规范（强制）

每日日志文件：`logs/daily/YYYY-MM-DD.md`

最少包含：
- 今日探索目标
- 草稿 ID 与审核状态
- 人工发布后的笔记 ID
- 北极星指标（互动率）
- 结论（保留/迭代/淘汰）

## 8. 策略迭代规范（强制）

更新原则：
- 同一结论连续 3 天有效才进入“稳定策略”
- 单日异常数据不直接下结论
- 每次更新必须附上证据日期与对应日志文件

## 9. 响应模板（给用户汇报）

对用户每日汇报时，固定输出：

1. 今日目标
2. 草稿与审核状态
3. 已发布笔记 ID 与数据表现
4. 新增结论
5. 明日实验计划

## 10. OpenClaw 消息接口

- 当 Feishu 收到文本 `xiaohongshu-autopilot register draft=<draft_id> note=<note_id>`，请让 OpenClaw 调用 `scripts/register_published_note.py` 完成登记并更新台账。
- 发送示例：

```
openclaw message send --channel feishu --target user:ou_27eafc99a5b351d7df9ca5709e74ea41 \
  --message "xiaohongshu-autopilot register draft=xhs-draft-20260302-221804 note=7032719"
```
