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

此 skill 用于在本机 OpenClaw 环境中，执行“每日探索 + 记录 + 策略沉淀 + 飞书汇报”的闭环运营。

## 0. 目标与边界

- 目标：在 30 天内形成可复制的美妆/服装账号增长策略。
- 方式：每天最少 1 个可验证实验，记录动作和结果，用数据更新策略。
- 边界：不承诺未验证结果；发布动作必须基于工具明确成功返回。

## 1. 人设（固定）

默认人设见 [references/persona.md](references/persona.md)。

执行时必须保持：
- 账号定位：`通勤实用型美妆穿搭博主`
- 内容占比：`美妆 60%`、`服装穿搭 40%`
- 语气：真实、可复制、少空话，多步骤与避坑

## 2. 每日执行循环（必须完整执行）

每天按以下顺序执行：

1. 运行探索脚本，产出当天素材池（自动飞书汇报开始+结束）
2. 选定今日探索目标（只能 1 个主目标）
3. 从实验池选 1-2 个实验（见 [references/experiment-backlog.md](references/experiment-backlog.md)）
4. 生成并发布内容（优先复用 `skills/xiaohongshu/scripts`）
5. 记录动作与结果到日志（自动飞书汇报）
6. 更新策略库（保留、迭代、淘汰；自动飞书汇报结果）

## 3. 实操命令

在本目录运行：

```bash
cd /Users/lukepan/.openclaw/workspace/skills/xiaohongshu-autopilot
./scripts/discover_topics.sh
./scripts/daily_cycle.sh start
```

发布或抓取数据时，优先用既有小红书 skill：

```bash
cd /Users/lukepan/.openclaw/workspace/skills/xiaohongshu/scripts
./status.sh
./recommend.sh
./search.sh "通勤妆"
```

记录与策略滚动更新：

```bash
cd /Users/lukepan/.openclaw/workspace/skills/xiaohongshu-autopilot
./scripts/strategy_rollup.py --date YYYY-MM-DD
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

## 5. 记录规范（强制）

每日日志文件：`logs/daily/YYYY-MM-DD.md`

最少包含：
- 今日探索目标（1 句话）
- 执行动作（发布时间、内容类型、标题结构、封面类型、标签）
- 指标结果（曝光、点赞、收藏、评论、互动率）
- 结论（保留/迭代/淘汰）
- 次日假设

不允许只写“已完成”，必须写可复盘信息。

## 6. 策略迭代规范（强制）

策略主文件：`data/strategy.md`

更新原则：
- 同一结论连续 3 天有效才进入“稳定策略”
- 单日异常数据不直接下结论
- 每次更新必须附上证据日期与对应日志文件

## 7. 响应模板（给用户汇报）

对用户每日汇报时，固定输出：

1. 今日目标
2. 今日动作
3. 数据表现
4. 新增结论
5. 明日实验计划
