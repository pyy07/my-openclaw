# OpenClaw 本机运行目录 — Agent 规则

本目录（`~/.openclaw`）是本机 **OpenClaw** 的运行时目录。后续所有在此目录或与 OpenClaw 相关的操作，请遵守以下约定。

## 运行环境与参考

- **运行时目录**：当前工作区即本机 OpenClaw 运行根目录（`~/.openclaw`）。
- **配置文档**：OpenClaw 的配置方法以官方文档为准：  
  [Configuration — docs.openclaw.ai](https://docs.openclaw.ai/gateway/configuration)
- **代码仓库**：  
  [openclaw/openclaw — GitHub](https://github.com/openclaw/openclaw)

## 操作须知

1. **配置**：主配置文件为 `openclaw.json`（支持 JSON5），配置结构与字段含义以 [Configuration](https://docs.openclaw.ai/gateway/configuration) 及 [Configuration Reference](https://docs.openclaw.ai/gateway/configuration-reference) 为准。
2. **修改配置**：可编辑 `openclaw.json`、使用 `openclaw config get/set/unset`、或通过 Control UI（如 `http://127.0.0.1:18789` 的 Config 标签）修改；Gateway 会监听配置文件并热加载（见文档中的 Config hot reload）。
3. **校验与排错**：配置需符合 schema，否则 Gateway 可能拒绝启动；使用 `openclaw doctor`（及 `--fix` / `--yes`）进行诊断与修复。
4. **后续操作**：凡涉及 OpenClaw 配置、目录结构、或与官方行为不一致时，以上述文档与仓库为准，并在此目录下谨记本规则。
