# <img src="assets/logo.svg" width="32" height="32" alt="EchoMemory"> EchoMemory

**给 AI Agent 团队用的共享大脑。pip install 即用，自带身份认证，中文原生。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## 解决什么问题

你的 AI Agent 每次新会话都失忆。昨天做的决策今天忘了，这台机器上的经验那台机器不知道，A Agent 踩过的坑 B Agent 还会再踩一遍。

EchoMemory 是一个轻量级的共享知识库。所有 Agent（和人）通过 API 读写同一份结构化知识。决策、教训、规则、洞察——写一次，所有人都能用。

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Kiro    │   │  Codex   │   │  Cursor  │   │   你     │
│  Agent   │   │  Agent   │   │  Agent   │   │  (CLI)   │
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │              │
     └──────────────┴──────────────┴──────────────┘
                         │
              ┌──────────▼──────────┐
              │    EchoMemory       │
              │  共享知识库 (SQLite) │
              └─────────────────────┘
```

---

## 设计亮点

### 零依赖部署

不需要 Docker，不需要 PostgreSQL，不需要 Node.js。一行 `pip install` 搞定。SQLite 单文件存储，任何有 Python 的机器都能跑。

### Agent 身份认证

每个 Agent 有独立账号。PBKDF2-SHA256 密码哈希（100000 轮）+ HMAC-SHA256 JWT Token（72h 过期）+ Ed25519 密钥对。你能追踪每条知识是谁写的，能随时撤销任何 Agent 的访问权。

### 七种知识类型 + rejected 字段

不只是存"我们选了什么"，还存"什么被否决了以及为什么"。Agent 不会再建议已经被否决的方案。

| 类型 | 用途 |
|------|------|
| `decision` | 技术选型、架构决策（必须包含 rejected） |
| `lesson` | 踩坑经验、故障复盘 |
| `process` | 操作流程、部署步骤 |
| `insight` | 行业观察、趋势判断 |
| `rule` | 团队规范、安全策略 |
| `reference` | 有用的链接和资源 |
| `contact` | 人脉和专家信息 |

### 三种接入方式

- **REST API** — 跨设备、跨网络访问，任何能发 HTTP 请求的工具都能用
- **MCP Server** — Kiro / Claude Code / Cursor 原生集成，Agent 直接调用
- **CLI** — 人工操作，快速查询和录入

### 数据安全

- 数据存在 `~/.echomemory/`（用户 home 目录），不在项目代码里
- `.gitignore` 排除所有 `.db` 文件
- 开源分享零泄露风险

---

## 快速开始

### 安装

```bash
git clone https://github.com/EastSword/EchoMemory.git
cd EchoMemory
pip install -e .
```

### 启动服务

```bash
echomemory serve --port 9090
```

首次启动自动创建 admin 账号，控制台会打印凭证（只显示一次，请保存）。

### 创建 Agent 账号

用 admin 登录后创建：

```bash
# 先登录拿 token
TOKEN=$(curl -s -X POST http://localhost:9090/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"admin的agent_id","secret":"admin的secret"}' \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['token'])")

# 创建新 agent
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:9090/api/agents/create \
  -d '{"name":"my-codex-agent","role":"agent"}'
```

返回 agent_id 和 secret，交给对应的 Agent 使用。

### Agent 接入

把 [Agent 使用指南](docs/AGENT_GUIDE.md) 和账号信息给你的 Agent。它需要做的事：

1. 用 agent_id + secret 调用 `/api/auth/login` 获取 JWT token
2. 开始任务前调用 `/api/search` 或 `/api/context` 查看相关知识
3. 做完决策后调用 `POST /api/knowledge` 写入新知识

### 人工使用（CLI）

```bash
# 添加知识
echomemory add --type decision \
  --title "选择 FastAPI 做后端" \
  --content "性能好，类型提示友好，生态成熟" \
  --rejected "Flask:太简陋" "Django:太重" \
  --tags "架构,后端"

# 搜索
echomemory search "后端框架"

# 查看统计
echomemory stats

# 导出为 Markdown
echomemory export --format md --days 30
```

---

## 谁可以使用

| 使用者 | 怎么接入 | 场景 |
|--------|---------|------|
| AI Agent（Kiro/Claude Code/Cursor） | MCP Server 或 REST API | 自动读写知识，跨会话记忆 |
| AI Agent（Codex/其他） | REST API（curl） | 任务前查知识，任务后写知识 |
| 开发者（你） | CLI 工具 | 手动录入决策、查询历史 |
| 团队成员 | REST API 或 CLI | 共享团队规范和经验 |
| CI/CD 流水线 | REST API | 自动记录部署决策和变更 |
| 自动化脚本 | REST API | 定期同步外部知识源 |

---

## 和同类项目的对比

| 维度 | EchoMemory | RoBrain | Mem0 | Zep |
|------|-----------|---------|------|-----|
| 部署复杂度 | pip install | Docker+Postgres+Node | pip install | Docker+Postgres |
| 知识类型 | 7 种 | 仅 decision | 事实 | 对话+实体 |
| rejected 字段 | ✅ 一等公民 | ✅ | ❌ | ❌ |
| 身份认证 | ✅ PBKDF2+JWT+Ed25519 | ❌ | ❌ | ❌ |
| 中文支持 | ✅ 原生 | ❌ | ❌ | ❌ |
| 多设备共享 | ✅ REST API | 需要 Postgres | 云服务 | 需要 Postgres |
| 开源协议 | MIT | Apache 2.0 | Apache 2.0 | Apache 2.0 |

---

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                    EchoMemory Server                      │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ REST API │  │ MCP API  │  │   Auth Engine        │  │
│  │ (HTTP)   │  │ (stdio)  │  │                      │  │
│  └────┬─────┘  └────┬─────┘  │  - PBKDF2 密码哈希  │  │
│       │              │        │  - JWT Token 签发    │  │
│       └──────┬───────┘        │  - Ed25519 签名验证  │  │
│              │                └──────────┬───────────┘  │
│              ▼                           │              │
│  ┌───────────────────────────────────────┐              │
│  │         SQLite + FTS5                 │              │
│  │  knowledge 表 + relations 表          │              │
│  │  全文搜索索引自动同步                  │              │
│  └───────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

---

## API 概览

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/auth/login` | 登录获取 token | 公开 |
| GET | `/api/health` | 健康检查 | 公开 |
| GET | `/api/search?q=` | 全文搜索知识 | agent |
| GET | `/api/context?q=` | 获取任务上下文 | agent |
| GET | `/api/knowledge` | 列出知识（支持筛选） | agent |
| POST | `/api/knowledge` | 添加知识 | agent |
| PUT | `/api/knowledge/:id/status` | 更新状态 | agent |
| GET | `/api/tags` | 所有标签 | agent |
| GET | `/api/stats` | 统计信息 | agent |
| POST | `/api/agents/create` | 创建 agent 账号 | admin |
| POST | `/api/agents/revoke` | 撤销 agent | admin |
| GET | `/api/agents` | 列出所有 agent | admin |

完整 API 文档见 [Agent 使用指南](docs/AGENT_GUIDE.md)。

---

## 文档

- [Agent 使用指南](docs/AGENT_GUIDE.md) — 给 AI Agent 看的接入文档（直接发给你的 Agent）
- [架构设计](DESIGN.md) — 技术架构和设计决策
- [Codex 接入示例](examples/codex-instructions.md) — Codex/Claude Code 接入配置
- [客户端脚本](examples/echomem-client.sh) — Shell 快捷命令

---

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ECHOMEMORY_DB` | `~/.echomemory/memory.db` | 知识库路径 |
| `ECHOMEMORY_PORT` | `9090` | 服务端口 |

---

## Roadmap

- [x] 核心存储层（SQLite + FTS5）
- [x] REST API Server
- [x] MCP Server
- [x] CLI 工具
- [x] Agent 身份认证（PBKDF2 + JWT + Ed25519）
- [ ] 语义向量搜索（embedding）
- [ ] 自动知识提取（接 LLM）
- [ ] 矛盾检测（知识冲突告警）
- [ ] Web UI 看板
- [ ] Kiro Hook 自动捕获
- [ ] 知识过期和清理策略

---

## 贡献

欢迎 PR。优先方向：
- 新的 Agent 集成（Windsurf、Zed、VS Code）
- 语义搜索后端
- 多语言文档
- 测试用例

---

## License

MIT — 随便用，不用问。
