# EchoMemory — Codex/Agent 使用指南

## 连接信息

```
Server: http://localhost:9090
Agent ID: agent_2593c909
Secret: -wmGp5iVBJU8m0g9tw2nIPORP4GvCjGk
```

## 认证流程

每次会话开始时，先获取 token：

```bash
TOKEN=$(curl -s -X POST http://localhost:9090/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"agent_2593c909","secret":"-wmGp5iVBJU8m0g9tw2nIPORP4GvCjGk"}' \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['token'])")
```

后续所有请求带上 token：
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:9090/api/...
```

## API 速查

### 搜索知识（开始任务前先查）

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9090/api/search?q=关键词"
```

### 获取上下文

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9090/api/context?q=当前任务主题"
```

### 添加知识（做完决策后记录）

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:9090/api/knowledge \
  -d '{
    "type": "decision",
    "title": "简短标题",
    "content": "详细内容（150-300字）",
    "rejected": [{"option":"被否决的方案","reason":"原因"}],
    "tags": ["标签1","标签2"]
  }'
```

### 列出所有知识

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:9090/api/knowledge?limit=20"
```

## 使用规则

### 何时读取（每次新任务开始前）
1. 调用 search 查看是否有相关的历史决策
2. 如果有，遵循已有决策，除非有明确理由推翻

### 何时写入（以下情况必须记录）
- 做出技术选型决策（type: decision，必须包含 rejected）
- 发现踩坑经验（type: lesson）
- 建立新流程（type: process）
- 发现重要洞察（type: insight）
- 确定团队规则（type: rule）

### 写入质量要求
- title: 具体可搜索，不写"杂项笔记"
- content: 包含具体细节和原因
- tags: 至少 2 个
- rejected: decision 类型必填，写清楚为什么不选
