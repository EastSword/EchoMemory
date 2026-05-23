# EchoMemory — 架构设计文档

> AI Agent 共享记忆层：让多个 Agent、多台设备、多个人共享同一份结构化知识
> 状态：设计阶段，待确认后开始编码

## 项目定位

EchoMemory 是一个轻量级的共享知识库，专为 AI Agent 协作场景设计。解决两个核心问题：

1. Agent 没有持久记忆，每次新会话从零开始
2. 多 Agent/多设备之间没有共享状态

## 架构总览

```
┌─────────────────────────────────────────────────────────┐
│                    EchoMemory Server                      │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ REST API │  │ MCP API  │  │   Knowledge Engine   │  │
│  │ (HTTP)   │  │ (stdio)  │  │                      │  │
│  └────┬─────┘  └────┬─────┘  │  - 知识提取          │  │
│       │              │        │  - 全文搜索          │  │
│       └──────┬───────┘        │  - 矛盾检测          │  │
│              │                │  - 知识关联          │  │
│              ▼                └──────────┬───────────┘  │
│  ┌───────────────────────────────────────┐              │
│  │           Storage Layer               │              │
│  │  SQLite + FTS5 (全文搜索)             │              │
│  └───────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────┘
         ▲              ▲              ▲
         │              │              │
    ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
    │ Device A │   │ Device B │   │ Device C │
    │ Kiro     │   │ Claude   │   │ Cursor   │
    └──────────┘   └──────────┘   └──────────┘
```

## 核心数据模型

### Knowledge Item（知识条目）

```json
{
  "id": "km_20260522_001",
  "type": "decision",
  "title": "选择 MiniMax 作为情报分析的 LLM",
  "content": "MiniMax M2.7 用于安全情报的 AI 分析。选择原因：国内直连，成本低，中文能力够用。",
  "context": "搭建 secnews 安全资讯平台时的技术选型",
  "rejected": [
    {"option": "OpenAI GPT-4", "reason": "需要代理，延迟高"},
    {"option": "通义千问", "reason": "API 稳定性不够"}
  ],
  "tags": ["AI", "基础设施", "LLM"],
  "source": {"agent": "kiro", "device": "macbook-qianli"},
  "confidence": 0.95,
  "status": "active",
  "created_at": "2026-05-16T10:00:00Z"
}
```

### Knowledge Types（7种）

- `decision` — 做了什么选择，为什么，否决了什么
- `lesson` — 踩过的坑，学到的教训
- `process` — 怎么做某件事的流程
- `insight` — 观察和洞察
- `contact` — 人脉和资源
- `reference` — 参考资料和链接
- `rule` — 团队规则和约定

### Knowledge Relations

- `supersedes` — A 取代了 B
- `conflicts_with` — A 和 B 矛盾
- `extends` — A 补充 B
- `related_to` — 相关但独立

## 三种交互方式

### 1. REST API（跨设备共享，主要方式）

```bash
# 启动 server（一台机器上跑）
echomemory serve --port 9090 --token YOUR_TOKEN

# 其他设备通过 HTTP 访问
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://192.168.1.100:9090/api/search?q=容器安全
```

### 2. MCP Server（Agent 直接调用）

```json
{
  "mcpServers": {
    "echomemory": {
      "command": "echomemory",
      "args": ["mcp", "--server", "http://192.168.1.100:9090", "--token", "YOUR_TOKEN"]
    }
  }
}
```

MCP 工具：
- `memory_add` — 添加知识
- `memory_search` — 搜索知识
- `memory_context` — 获取当前任务相关上下文
- `memory_update` — 更新/废弃知识
- `memory_history` — 查看决策演变

### 3. CLI（人工操作）

```bash
echomemory add --type decision --title "..." --content "..." --tags "a,b"
echomemory search "容器安全"
echomemory inject --query "secnews" --copy
echomemory list --recent 7d
echomemory export --format md
```

## Agent 集成协议

Agent 通过以下规则使用 EchoMemory：

```markdown
## 何时读取
- 开始新任务前，调用 memory_context 获取背景
- 做技术选型时，调用 memory_search 查看历史决策
- 遇到不确定的问题时，先查知识库

## 何时写入
- 做出重要决策后（技术选型、架构变更）
- 发现经验教训后（踩坑、安全隐患）
- 用户明确要求记录时

## 写入规则
- type 必须准确
- decision 类型必须记录 rejected
- tags 至少 2 个
- content 要具体，不写空泛总结
```

## 多设备同步

推荐方案：中心化 Server。

一台机器跑 `echomemory serve`，其他设备通过 REST API 或 MCP（配置 --server 参数）连接。实时同步，无冲突。

## 技术选型

| 组件 | 选择 | 理由 |
|------|------|------|
| 语言 | Python 3.9+ | 生态好，pip install 即用 |
| 存储 | SQLite + FTS5 | 零依赖，单文件，全文搜索内置 |
| API | 内置 http.server | 零依赖启动 |
| MCP | stdio 协议 | 兼容 Kiro/Claude Code/Cursor |
| 认证 | Bearer Token | 简单有效 |
| 协议 | MIT | 最宽松 |

## 项目结构

```
EchoMemory/
├── README.md
├── DESIGN.md
├── LICENSE (MIT)
├── pyproject.toml
├── echomemory/
│   ├── __init__.py
│   ├── __main__.py      # python -m echomemory
│   ├── cli.py           # CLI 入口
│   ├── server.py        # REST API Server
│   ├── mcp_server.py    # MCP Server
│   ├── storage.py       # SQLite 存储层
│   ├── engine.py        # 搜索/关联/矛盾检测
│   ├── models.py        # 数据模型
│   └── config.py        # 配置
├── tests/
├── docs/
│   ├── quickstart.md
│   ├── agent-integration.md
│   └── api-reference.md
└── examples/
    ├── kiro-steering.md
    ├── mcp-config.json
    └── hook-auto-capture.json
```

## 开发计划

### Phase 1（本次实现）
- 数据模型和 SQLite 存储层
- CLI 工具（add/search/list/inject/export）
- REST API Server（跨设备访问）
- MCP Server（Agent 集成）
- README + 快速开始

### Phase 2（后续）
- LLM 自动知识提取
- 语义向量搜索
- 矛盾检测
- Kiro Hook 自动捕获
- Web UI

## 和 RoBrain 的差异

| 维度 | RoBrain | EchoMemory |
|------|---------|------------|
| 定位 | 代码架构决策 | 通用知识管理 |
| 知识类型 | 只有 decision | 7 种 |
| 部署 | Docker + Postgres + Node.js | pip install，零依赖 |
| 中文 | 无 | 原生中文 |
| 多设备 | 需要 Postgres | Server 模式，SQLite 单文件 |
