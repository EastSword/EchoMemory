# EchoMemory

团队共享记忆系统。你（AI Agent）通过 HTTP API 读写知识，和其他 Agent 共享决策、经验和规则。

## 你是谁

你是接入 EchoMemory 的一个 Agent。你的职责是：
1. 做事之前先查知识库，看看有没有相关的历史决策
2. 做完重要决策后，把决策写入知识库
3. 踩坑后，把教训写入知识库

## 快速开始

### 第一步：登录

用你的账号密码换取 token（72小时有效）：

```bash
curl -s -X POST http://SERVER_ADDRESS/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"YOUR_AGENT_ID","secret":"YOUR_SECRET"}'
```

返回：
```json
{"token": "eyJ...", "agent_id": "agent_xxx", "expires_in": "72h"}
```

### 第二步：用 token 操作知识库

所有后续请求都带上 token：
```
Authorization: Bearer <你的token>
```

---

## API 完整说明

### 搜索知识（最常用）

```bash
curl -s -H "Authorization: Bearer TOKEN" \
  "http://SERVER/api/search?q=搜索关键词&limit=10"
```

返回知识条目数组。每条包含 title、content、tags、rejected（被否决的方案）。

### 获取上下文（开始新任务时调用）

```bash
curl -s -H "Authorization: Bearer TOKEN" \
  "http://SERVER/api/context?q=任务主题"
```

返回格式化的上下文文本，可以直接作为你的背景知识。

### 添加知识

```bash
curl -s -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://SERVER/api/knowledge \
  -d '{
    "type": "decision",
    "title": "选择 X 而不是 Y",
    "content": "详细原因和背景（150-300字）",
    "rejected": [{"option":"Y","reason":"为什么不选Y"}],
    "tags": ["标签1","标签2"]
  }'
```

### 列出知识

```bash
# 全部
curl -s -H "Authorization: Bearer TOKEN" "http://SERVER/api/knowledge"

# 按类型
curl -s -H "Authorization: Bearer TOKEN" "http://SERVER/api/knowledge?type=decision"

# 按标签
curl -s -H "Authorization: Bearer TOKEN" "http://SERVER/api/knowledge?tag=安全"

# 最近7天
curl -s -H "Authorization: Bearer TOKEN" "http://SERVER/api/knowledge?days=7"
```

### 查看统计

```bash
curl -s -H "Authorization: Bearer TOKEN" "http://SERVER/api/stats"
```

### 查看所有标签

```bash
curl -s -H "Authorization: Bearer TOKEN" "http://SERVER/api/tags"
```

---

## 知识类型（type 字段）

| type | 什么时候用 | 必须包含 |
|------|-----------|---------|
| `decision` | 做了一个选择 | `rejected`（被否决的方案和原因） |
| `lesson` | 踩了一个坑 | 具体的坑和解决方法 |
| `process` | 确定了一个流程 | 步骤说明 |
| `insight` | 发现了一个规律 | 观察和推断 |
| `rule` | 定了一条规矩 | 规则内容和适用范围 |
| `reference` | 记录一个有用的链接 | URL 和说明 |
| `contact` | 记录一个人/资源 | 联系方式和专长 |

---

## 你的行为规范

### 开始任务前（必做）

```bash
# 搜索相关知识
curl -s -H "Authorization: Bearer TOKEN" "http://SERVER/api/context?q=你即将做的事"
```

如果搜索结果中有相关的 decision 或 rule，你必须遵循，除非用户明确要求推翻。

如果搜索结果中有 rejected 项，不要再建议那些被否决的方案，除非情况已经变化。

### 做完决策后（必做）

以下情况必须写入知识库：
- 技术选型（选了什么框架/工具/方案）
- 架构决策（怎么组织代码/服务/数据）
- 踩坑经验（什么东西不能这么用）
- 流程确定（部署步骤/操作规范）
- 团队规则（编码规范/安全要求）

写入示例：
```bash
curl -s -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://SERVER/api/knowledge \
  -d '{
    "type": "decision",
    "title": "EchoMemory 使用 SQLite 而非 PostgreSQL",
    "content": "选择 SQLite 作为存储引擎。原因：零依赖部署，单文件便于备份和迁移，FTS5 提供全文搜索能力，对于个人和小团队的知识量完全够用。",
    "rejected": [
      {"option": "PostgreSQL", "reason": "需要额外部署和运维，对小团队过重"},
      {"option": "MongoDB", "reason": "文档模型对结构化知识没有优势，且依赖重"}
    ],
    "tags": ["架构", "存储", "EchoMemory"]
  }'
```

### 不要写入的内容

- 临时的调试信息
- 一次性的操作记录
- 用户的私人信息
- 密码、token、密钥

---

## 错误处理

| HTTP 状态码 | 含义 | 你该怎么做 |
|------------|------|-----------|
| 200 | 成功 | 正常处理返回数据 |
| 400 | 参数错误 | 检查请求体格式 |
| 401 | 未认证 | 重新调用 /api/auth/login 获取新 token |
| 403 | 权限不足 | 你没有执行该操作的权限 |
| 404 | 未找到 | 检查 URL 路径 |

---

## 部署信息（给管理员看的）

### 安装

```bash
git clone <repo>
cd EchoMemory
pip install -e .
```

### 启动服务

```bash
# 首次启动会自动创建 admin 账号（控制台输出凭证）
echomemory serve --port 9090

# 或指定数据库路径
ECHOMEMORY_DB=/path/to/memory.db echomemory serve --port 9090
```

### 创建 Agent 账号

用 admin token 创建：

```bash
curl -s -X POST -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:9090/api/agents/create \
  -d '{"name":"codex-macbook","role":"agent"}'
```

返回 agent_id 和 secret，把这两个值给对应的 Agent 使用。

### 撤销 Agent

```bash
curl -s -X POST -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:9090/api/agents/revoke \
  -d '{"agent_id":"agent_xxx"}'
```

### 安全机制

- 密码存储：PBKDF2-SHA256（100000轮）
- 认证令牌：HMAC-SHA256 JWT（72小时过期）
- 每个 Agent 独立 Ed25519 密钥对
- 可选请求签名验证（X-Signature + X-Timestamp）
- 角色权限：admin 可管理 agent，普通 agent 只能读写知识

### CLI 工具（管理员本地使用）

```bash
echomemory add --type decision --title "..." --content "..." --tags "a,b"
echomemory search "关键词"
echomemory list --type decision --days 7
echomemory stats
echomemory inject --query "主题" --copy
echomemory export --format md
```

---

## License

MIT
