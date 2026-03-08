# GitHub 认证说明（漫说GitHub）

漫说GitHub 的 **cron 跑在 OpenClaw 环境**，使用 **openclaw-github-assistant**（github skill）探索仓库。需在 OpenClaw 中配置 GitHub 认证，步骤如下。

## 1. 创建 GitHub Personal Access Token (PAT)

1. 打开：<https://github.com/settings/tokens>
2. 点击 **Generate new token** → 选 **Generate new token (classic)**
3. 填写：
   - **Note**：例如 `cursor-github-mcp` 或 `openclaw-manshuo`
   - **Expiration**：选 90 天或 No expiration（按需）
   - **Scopes**：勾选 **`public_repo`**（只搜公开仓库即可）；若需读私有仓库再勾选 **`repo`**
4. 生成后**复制 token**（形如 `ghp_xxxxxxxxxxxx`），只显示一次。

## 2. 在 OpenClaw 里启用 github skill 并配置环境变量

已在 `~/.openclaw/openclaw.json` 的 `skills.entries` 中加入 **github**（openclaw-github-assistant），并注入 `GITHUB_TOKEN`、`GITHUB_USERNAME`。你只需在 **`~/.openclaw/.env`** 中设置：

```bash
GITHUB_TOKEN=ghp_你的token
GITHUB_USERNAME=你的GitHub用户名
```

保存后**重启 OpenClaw gateway**（`openclaw gateway restart` 或重启运行 gateway 的进程），cron 再跑时会使用 github skill 并带上认证。

## 3. 验证

- 手动触发一次漫说GitHub 的 cron，或让 Agent 用 github skill 执行 list_repos / search_repos，能正常返回结果即表示认证成功。
- 若仍报 401/403，检查 token 是否过期、是否勾选 `public_repo`（或 `repo`），以及 `.env` 是否生效、是否重启过 gateway。

## 4. 故障排查：cron 没探索、没报告

- **现象**：cron 跑了但日志里「探索结果」为空、或你没收飞书。
- **原因 1**：Agent 用了 **mcporter 调 Cursor 的 GitHub MCP**，而不是 OpenClaw 的 github skill；Cursor 的 MCP 未配 token 会报 Bad credentials。  
  **处理**：cron 的 message 已写明「不得使用 mcporter 或 Cursor 的 GitHub MCP」。下次跑会用新 prompt。若仍走 mcporter，说明 OpenClaw 的 agent 没有暴露 github 工具，需在 OpenClaw 里确认 github skill 已加载并作为工具可用。
- **原因 2**：飞书通知发的是「失败」内容（如认证失败），可能被折叠或未注意。  
  **处理**：流程已强制「无论成功失败都执行一次 notify_feishu.sh」。可查 `logs/notifications/` 下是否有未发出的队列。
