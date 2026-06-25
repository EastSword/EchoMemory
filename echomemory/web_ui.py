"""Web UI for EchoMemory — Server-side rendered admin dashboard"""
import json
import html as html_lib

STYLE = '''
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#0f172a;color:#f8fafc;font-size:13px;min-height:100vh}
a{color:#f59e0b;text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1100px;margin:0 auto;padding:20px}
.header{background:#1e293b;border-bottom:1px solid #334155;padding:12px 24px;display:flex;align-items:center;gap:20px;margin-bottom:20px}
.logo{font-size:18px;font-weight:700;color:#f8fafc}.logo span{color:#f59e0b}
.nav a{padding:6px 14px;border-radius:6px;color:#94a3b8;font-size:13px;margin-right:4px}
.nav a.active{background:#f59e0b;color:#0f172a}
.nav a:hover:not(.active){color:#f59e0b;text-decoration:none}
.right{margin-left:auto;font-size:11px;color:#94a3b8}
.right a{color:#ef4444;margin-left:12px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
.stat{background:#1e293b;border:1px solid #334155;border-radius:8px;padding:14px;text-align:center}
.stat .n{font-size:26px;font-weight:700;color:#f59e0b}.stat .l{font-size:11px;color:#94a3b8;margin-top:4px}
table{width:100%;border-collapse:collapse;background:#1e293b;border:1px solid #334155;border-radius:8px;overflow:hidden;margin-bottom:20px}
th{background:#0f172a;padding:10px 12px;text-align:left;font-size:11px;color:#94a3b8;font-weight:600}
td{padding:10px 12px;border-top:1px solid #334155;font-size:12px;vertical-align:top}
.tag{display:inline-block;padding:1px 6px;border-radius:3px;font-size:10px;background:rgba(245,158,11,0.15);color:#f59e0b;margin:1px}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:600}
.badge-decision{background:rgba(59,130,246,0.2);color:#60a5fa}
.badge-lesson{background:rgba(239,68,68,0.2);color:#f87171}
.badge-rule{background:rgba(34,197,94,0.2);color:#4ade80}
.badge-insight{background:rgba(168,85,247,0.2);color:#c084fc}
.badge-process{background:rgba(6,182,212,0.2);color:#22d3ee}
.badge-reference{background:rgba(148,163,184,0.2);color:#94a3b8}
.badge-contact{background:rgba(251,146,60,0.2);color:#fb923c}
.rejected{font-size:11px;color:#f87171;margin-top:3px}
.content{font-size:11px;color:#94a3b8;margin-top:3px;max-width:400px}
.btn{padding:6px 14px;border:1px solid #334155;border-radius:6px;background:#1e293b;color:#f8fafc;cursor:pointer;font-size:12px;text-decoration:none;display:inline-block}
.btn:hover{border-color:#f59e0b;text-decoration:none}
.btn-primary{background:#f59e0b;color:#0f172a;border:none;font-weight:600}
.btn-danger{background:#ef4444;color:#fff;border:none}
.btn-sm{padding:3px 10px;font-size:11px}
.login-box{background:#1e293b;border-radius:12px;padding:40px;width:360px;margin:100px auto;box-shadow:0 20px 60px rgba(0,0,0,.4)}
.login-box h2{text-align:center;margin-bottom:20px;color:#f8fafc}
.login-box h2 span{color:#f59e0b}
.form-group{margin-bottom:14px}
.form-group label{display:block;font-size:12px;color:#94a3b8;margin-bottom:4px}
.form-group input,.form-group select,.form-group textarea{width:100%;padding:9px 12px;border:1px solid #334155;border-radius:6px;background:#0f172a;color:#f8fafc;font-size:13px}
.form-group textarea{min-height:80px;resize:vertical;font-family:inherit}
.error{color:#ef4444;font-size:12px;margin:8px 0}
.success{color:#22c55e;font-size:12px;margin:8px 0;background:rgba(34,197,94,0.1);padding:8px 12px;border-radius:6px}
.mono{font-family:monospace;font-size:11px;background:#0f172a;padding:2px 6px;border-radius:3px}
.empty{text-align:center;padding:40px;color:#64748b}
.toolbar{display:flex;gap:8px;margin-bottom:14px;align-items:center}
.toolbar form{display:flex;gap:8px;align-items:center}
'''


def esc(s):
    return html_lib.escape(str(s)) if s else ''


def get_login_page(error=''):
    error_html = f'<div class="error">{esc(error)}</div>' if error else ''
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>EchoMemory</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='48' fill='%230f172a'/><circle cx='50' cy='50' r='8' fill='%23f59e0b'/><circle cx='50' cy='50' r='18' fill='none' stroke='%23f59e0b' stroke-width='1.5' opacity='0.3'/><circle cx='50' cy='50' r='28' fill='none' stroke='%23f59e0b' stroke-width='1' opacity='0.2'/></svg>">
<style>{STYLE}</style></head><body>
<div class="login-box">
<h2>Echo<span>Memory</span></h2>
<form method="POST" action="/login">
<div class="form-group"><label>Agent ID</label><input name="agent_id" placeholder="agent_xxxxxxxx" required></div>
<div class="form-group"><label>Secret</label><input name="secret" type="password" required></div>
{error_html}
<button class="btn btn-primary" style="width:100%;padding:12px;margin-top:8px">登录</button>
</form>
</div></body></html>'''


def get_admin_page(storage, registry, agent_info, page='knowledge', message=''):
    stats = storage.stats()
    msg_html = f'<div class="success">{esc(message)}</div>' if message else ''

    # Navigation
    nav = f'''<div class="header">
<div class="logo">Echo<span>Memory</span></div>
<div class="nav">
<a href="/admin?page=knowledge" class="{'active' if page=='knowledge' else ''}">知识库</a>
<a href="/admin?page=agents" class="{'active' if page=='agents' else ''}">Agent 管理</a>
<a href="/admin?page=types" class="{'active' if page=='types' else ''}">类型管理</a>
<a href="/admin?page=integration" class="{'active' if page=='integration' else ''}">对接设置</a>
<a href="/admin?page=add" class="{'active' if page=='add' else ''}">添加知识</a>
</div>
<div class="right">{esc(agent_info.get('name',''))} ({esc(agent_info.get('sub',''))}) <a href="/logout">退出</a></div>
</div>'''

    # Stats bar
    stats_html = f'''<div class="stats">
<div class="stat"><div class="n">{stats['active']}</div><div class="l">活跃知识</div></div>
<div class="stat"><div class="n">{len(stats.get('by_type',{}))}</div><div class="l">知识类型</div></div>
<div class="stat"><div class="n">{stats['total']}</div><div class="l">总条目</div></div>
<div class="stat"><div class="n">{len(storage.get_tags())}</div><div class="l">标签数</div></div>
</div>'''

    # Page content
    if page == 'knowledge':
        content = _render_knowledge_page(storage)
    elif page == 'agents':
        content = _render_agents_page(registry, agent_info)
    elif page == 'types':
        content = _render_types_page(storage)
    elif page == 'integration':
        content = _render_integration_page(registry, agent_info)
    elif page == 'add':
        content = _render_add_page(storage)
    else:
        content = '<div class="empty">未知页面</div>'

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>EchoMemory Admin</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='48' fill='%230f172a'/><circle cx='50' cy='50' r='8' fill='%23f59e0b'/><circle cx='50' cy='50' r='18' fill='none' stroke='%23f59e0b' stroke-width='1.5' opacity='0.3'/><circle cx='50' cy='50' r='28' fill='none' stroke='%23f59e0b' stroke-width='1' opacity='0.2'/></svg>">
<style>{STYLE}</style></head><body>
{nav}
<div class="wrap">
{msg_html}
{stats_html}
{content}
</div></body></html>'''


def _render_knowledge_page(storage):
    items = storage.list_items(limit=50)
    if not items:
        return '<div class="empty">暂无知识条目</div>'

    rows = ''
    for item in items:
        tags_html = ''.join(f'<span class="tag">{esc(t)}</span>' for t in (item.tags or []))
        rejected_html = ''
        if item.rejected:
            parts = '; '.join(f"{esc(r.get('option',''))}({esc(r.get('reason',''))})" for r in item.rejected)
            rejected_html = f'<div class="rejected">✗ {parts}</div>'
        content_html = ''
        if item.content:
            preview = item.content[:120] + ('...' if len(item.content) > 120 else '')
            content_html = f'<div class="content">{esc(preview)}</div>'
        source = item.source.get('agent', '') if item.source else ''

        rows += f'''<tr>
<td><span class="badge badge-{item.type}">{item.type}</span></td>
<td><strong>{esc(item.title)}</strong>{content_html}{rejected_html}</td>
<td>{tags_html}</td>
<td style="color:#64748b">{esc(source)}</td>
<td style="color:#64748b;white-space:nowrap">{item.created_at[:10] if item.created_at else ''}</td>
<td><form method="POST" action="/admin/delete" style="display:inline"><input type="hidden" name="id" value="{item.id}"><button class="btn btn-sm btn-danger" onclick="return confirm('确认删除？')">删除</button></form></td>
</tr>'''

    return f'''<table>
<thead><tr><th>类型</th><th>标题</th><th>标签</th><th>来源</th><th>时间</th><th>操作</th></tr></thead>
<tbody>{rows}</tbody>
</table>'''


def _render_agents_page(registry, current_agent):
    agents = registry.list_agents()
    if not agents:
        return '<div class="empty">暂无 Agent</div>'

    rows = ''
    for a in agents:
        status = '🟢 活跃' if a.get('is_active') else '🔴 已撤销'
        last_auth = (a.get('last_auth') or '从未')[:16].replace('T', ' ')
        revoke_btn = ''
        if a.get('is_active') and a.get('agent_id') != current_agent.get('sub'):
            revoke_btn = f'<form method="POST" action="/admin/revoke" style="display:inline"><input type="hidden" name="agent_id" value="{a["agent_id"]}"><button class="btn btn-sm btn-danger" onclick="return confirm(\'确认撤销？\')">撤销</button></form>'

        rows += f'''<tr>
<td class="mono">{esc(a.get('agent_id',''))}</td>
<td>{esc(a.get('name',''))}</td>
<td><span class="badge badge-{'decision' if a.get('role')=='admin' else 'insight'}">{esc(a.get('role',''))}</span></td>
<td>{status}</td>
<td style="color:#64748b">{esc((a.get('created_at') or '')[:10])}</td>
<td style="color:#64748b">{last_auth}</td>
<td>{revoke_btn}</td>
</tr>'''

    create_form = '''<div style="margin-top:20px;background:#1e293b;border:1px solid #334155;border-radius:8px;padding:16px">
<h3 style="margin-bottom:12px;font-size:14px">创建新 Agent</h3>
<form method="POST" action="/admin/create-agent" style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">
<div class="form-group" style="margin:0;flex:1;min-width:150px"><label>名称</label><input name="name" placeholder="如: codex-macbook" required></div>
<div class="form-group" style="margin:0;width:120px"><label>角色</label><select name="role"><option value="agent">agent</option><option value="admin">admin</option></select></div>
<button class="btn btn-primary">创建</button>
</form></div>'''

    return f'''<table>
<thead><tr><th>Agent ID</th><th>名称</th><th>角色</th><th>状态</th><th>创建时间</th><th>最后认证</th><th>操作</th></tr></thead>
<tbody>{rows}</tbody>
</table>
{create_form}'''


def _render_types_page(storage):
    """Knowledge types management page"""
    types = storage.get_knowledge_types()

    rows = ''
    for t in types:
        builtin_badge = '<span class="tag" style="background:rgba(34,197,94,0.15);color:#4ade80">内置</span>' if t.get('is_builtin') else '<span class="tag">自定义</span>'
        color_dot = f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{esc(t.get("color","#94a3b8"))};vertical-align:middle;margin-right:6px"></span>'
        delete_btn = ''
        if not t.get('is_builtin'):
            delete_btn = f'<form method="POST" action="/admin/delete-type" style="display:inline"><input type="hidden" name="name" value="{esc(t["name"])}"><button class="btn btn-sm btn-danger" onclick="return confirm(\'确认删除？仅在无关联知识时可删\')">删除</button></form>'
        edit_btn = f'<button class="btn btn-sm" onclick="editType(\'{esc(t["name"])}\',\'{esc(t["label"])}\',\'{esc(t.get("description",""))}\',\'{esc(t.get("color","#94a3b8"))}\')">编辑</button>'

        rows += f'''<tr>
<td>{color_dot}<span class="badge badge-{esc(t['name'])}">{esc(t['name'])}</span></td>
<td><strong>{esc(t.get('label',''))}</strong></td>
<td style="color:#94a3b8;font-size:11px">{esc(t.get('description',''))}</td>
<td>{builtin_badge}</td>
<td style="color:#64748b">{esc((t.get('created_at') or '')[:10])}</td>
<td style="white-space:nowrap">{edit_btn} {delete_btn}</td>
</tr>'''

    return f'''<table>
<thead><tr><th>类型名</th><th>显示名</th><th>说明</th><th>属性</th><th>创建时间</th><th>操作</th></tr></thead>
<tbody>{rows}</tbody>
</table>

<!-- Add Type Form -->
<div style="margin-top:20px;background:#1e293b;border:1px solid #334155;border-radius:8px;padding:16px">
<h3 style="margin-bottom:12px;font-size:14px">添加知识类型</h3>
<form method="POST" action="/admin/add-type" style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">
<div class="form-group" style="margin:0;width:120px"><label>类型名（英文）</label><input name="name" placeholder="如: strategy" required pattern="[a-z_]+" title="小写英文+下划线"></div>
<div class="form-group" style="margin:0;width:100px"><label>显示名</label><input name="label" placeholder="如: 策略" required></div>
<div class="form-group" style="margin:0;flex:1;min-width:180px"><label>说明</label><input name="description" placeholder="这类知识的用途"></div>
<div class="form-group" style="margin:0;width:60px"><label>颜色</label><input name="color" type="color" value="#94a3b8"></div>
<button class="btn btn-primary">添加</button>
</form></div>

<!-- Edit Modal -->
<div id="editModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:1000;justify-content:center;align-items:center">
<div style="background:#1e293b;border:1px solid #334155;border-radius:12px;padding:24px;width:400px">
<h3 style="margin-bottom:16px;font-size:15px">编辑知识类型</h3>
<form method="POST" action="/admin/update-type">
<input type="hidden" name="name" id="editName">
<div class="form-group"><label>显示名</label><input name="label" id="editLabel" required></div>
<div class="form-group"><label>说明</label><input name="description" id="editDesc"></div>
<div class="form-group"><label>颜色</label><input name="color" type="color" id="editColor"></div>
<div style="display:flex;gap:8px;margin-top:12px">
<button class="btn btn-primary">保存</button>
<button type="button" class="btn" onclick="document.getElementById(\'editModal\').style.display=\'none\'">取消</button>
</div>
</form></div></div>

<script>
function editType(name, label, desc, color) {{
    document.getElementById('editName').value = name;
    document.getElementById('editLabel').value = label;
    document.getElementById('editDesc').value = desc;
    document.getElementById('editColor').value = color || '#94a3b8';
    document.getElementById('editModal').style.display = 'flex';
}}
document.getElementById('editModal').addEventListener('click', function(e) {{ if(e.target===e.currentTarget) e.target.style.display='none'; }});
</script>'''


def _render_integration_page(registry, agent_info):
    """Agent integration/onboarding settings page with prompt generation"""
    agents = registry.list_agents()
    active_agents = [a for a in agents if a.get('is_active')]

    # Get server URL info
    import socket
    hostname = socket.gethostname()

    agent_options = ''.join(
        f'<option value="{esc(a["agent_id"])}">{esc(a.get("name",""))} ({esc(a["agent_id"])})</option>'
        for a in active_agents
    )

    return f'''
<div style="display:grid;gap:20px">

<!-- Integration Guide -->
<div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:20px">
<h3 style="margin-bottom:12px;font-size:15px">🔗 EchoMemory 对接方式</h3>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
<div style="background:#0f172a;border-radius:6px;padding:12px">
<div style="font-size:11px;color:#f59e0b;margin-bottom:4px;font-weight:600">REST API</div>
<div style="font-size:12px;color:#94a3b8">适用于任何语言/框架的 Agent</div>
<div class="mono" style="margin-top:6px;color:#f8fafc">POST /api/auth/login</div>
<div class="mono" style="color:#f8fafc">GET /api/knowledge</div>
<div class="mono" style="color:#f8fafc">POST /api/knowledge</div>
<div class="mono" style="color:#f8fafc">GET /api/search?q=...</div>
<div class="mono" style="color:#f8fafc">GET /api/context?q=...</div>
</div>
<div style="background:#0f172a;border-radius:6px;padding:12px">
<div style="font-size:11px;color:#f59e0b;margin-bottom:4px;font-weight:600">MCP Server</div>
<div style="font-size:12px;color:#94a3b8">适用于支持 MCP 协议的 Agent</div>
<div class="mono" style="margin-top:6px;color:#f8fafc">python3 -m echomemory mcp</div>
<div style="font-size:11px;color:#64748b;margin-top:4px">工具: memory_search, memory_add,<br>memory_list, memory_context</div>
</div>
</div>
</div>

<!-- Prompt Generator -->
<div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:20px">
<h3 style="margin-bottom:12px;font-size:15px">📋 对接提示词生成器</h3>
<p style="font-size:12px;color:#94a3b8;margin-bottom:12px">选择 Agent 或手动输入凭证，生成可直接复制给 Agent 使用的系统提示词。</p>

<div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap;margin-bottom:16px">
<div class="form-group" style="margin:0;width:250px">
<label>选择已有 Agent</label>
<select id="agentSelect" onchange="selectAgent(this.value)">
<option value="">-- 手动输入 --</option>
{agent_options}
</select>
</div>
<div class="form-group" style="margin:0;width:180px">
<label>服务地址</label>
<input id="serverUrl" value="http://localhost:9090" placeholder="http://host:port">
</div>
<button class="btn btn-primary" onclick="generatePrompt()">生成提示词</button>
</div>

<div id="manualCreds" style="display:flex;gap:8px;margin-bottom:16px">
<div class="form-group" style="margin:0;flex:1"><label>Agent ID</label><input id="promptAgentId" placeholder="agent_xxxxxxxx"></div>
<div class="form-group" style="margin:0;flex:1"><label>Secret</label><input id="promptSecret" placeholder="凭证（仅新创建时可见）" type="password"></div>
</div>

<div id="promptOutput" style="display:none;background:#0f172a;border:1px solid #334155;border-radius:8px;padding:16px;position:relative">
<button onclick="copyPrompt()" style="position:absolute;top:8px;right:8px;background:#f59e0b;color:#0f172a;border:none;padding:4px 10px;border-radius:4px;font-size:11px;cursor:pointer;font-weight:600">复制</button>
<pre id="promptText" style="white-space:pre-wrap;font-size:11px;color:#e2e8f0;line-height:1.6;max-height:500px;overflow-y:auto;font-family:monospace"></pre>
</div>
</div>

<!-- Quick Create + Generate -->
<div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:20px">
<h3 style="margin-bottom:12px;font-size:15px">⚡ 快速创建并生成对接提示词</h3>
<p style="font-size:12px;color:#94a3b8;margin-bottom:12px">一步完成：创建新 Agent 账号 + 生成对接提示词。凭证仅显示一次。</p>
<form method="POST" action="/admin/create-agent-with-prompt" style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">
<div class="form-group" style="margin:0;flex:1;min-width:150px"><label>Agent 名称</label><input name="name" placeholder="如: research-agent" required></div>
<div class="form-group" style="margin:0;width:120px"><label>角色</label><select name="role"><option value="agent">agent</option><option value="admin">admin</option></select></div>
<div class="form-group" style="margin:0;width:200px"><label>服务地址</label><input name="server_url" value="http://localhost:9090"></div>
<button class="btn btn-primary">创建并生成提示词</button>
</form>
</div>

</div>

<script>
function selectAgent(agentId) {{
    if (agentId) {{
        document.getElementById('promptAgentId').value = agentId;
        document.getElementById('manualCreds').style.display = 'none';
    }} else {{
        document.getElementById('promptAgentId').value = '';
        document.getElementById('manualCreds').style.display = 'flex';
    }}
}}

function generatePrompt() {{
    var agentId = document.getElementById('promptAgentId').value || '<YOUR_AGENT_ID>';
    var secret = document.getElementById('promptSecret').value || '<YOUR_SECRET>';
    var serverUrl = document.getElementById('serverUrl').value || 'http://localhost:9090';

    var prompt = `## EchoMemory 共享记忆对接指南

你已被授权接入 EchoMemory 共享记忆系统。以下是你的认证凭据和使用方式。

### 认证信息
- 服务地址: ${{serverUrl}}
- Agent ID: ${{agentId}}
- Secret: ${{secret}}

### 认证流程
每次会话开始时，先获取 Token：

\`\`\`bash
curl -X POST ${{serverUrl}}/api/auth/login \\\\
  -H "Content-Type: application/json" \\\\
  -d '{{"agent_id": "${{agentId}}", "secret": "${{secret}}"}}'
\`\`\`

返回: {{"token": "eyJ...", "agent_id": "...", "expires_in": "72h"}}

后续请求在 Header 中携带: Authorization: Bearer <token>

### 核心操作

**查询知识（带上下文注入）：**
\`\`\`bash
GET ${{serverUrl}}/api/context?q=关键词&limit=10
\`\`\`

**搜索知识：**
\`\`\`bash
GET ${{serverUrl}}/api/search?q=关键词&limit=20
\`\`\`

**添加知识：**
\`\`\`bash
POST ${{serverUrl}}/api/knowledge
Content-Type: application/json
{{"type": "lesson|decision|rule|insight|process|reference|contact", "title": "...", "content": "...", "tags": ["tag1"], "rejected": [{{"option":"被否决方案","reason":"原因"}}]}}
\`\`\`

**列出知识：**
\`\`\`bash
GET ${{serverUrl}}/api/knowledge?type=decision&tag=security&limit=50
\`\`\`

### 使用原则
1. 每次会话开始时，用 /api/context 获取相关记忆作为上下文
2. 做出重要决策、发现教训、建立规则时，写入共享记忆
3. 记录被否决的方案和原因，避免团队重复踩坑
4. 标签要简洁有意义，便于跨 Agent 检索
5. 写入内容要精炼（150-300字），突出核心信息`;

    document.getElementById('promptText').textContent = prompt;
    document.getElementById('promptOutput').style.display = 'block';
}}

function copyPrompt() {{
    var text = document.getElementById('promptText').textContent;
    navigator.clipboard.writeText(text).then(function() {{
        var btn = event.target;
        btn.textContent = '已复制 ✓';
        setTimeout(function() {{ btn.textContent = '复制'; }}, 2000);
    }});
}}
</script>'''


def _render_add_page(storage):
    types = storage.get_knowledge_types()
    type_options = ''.join(
        f'<option value="{esc(t["name"])}">{esc(t["name"])}（{esc(t["label"])}）</option>' for t in types
    )
    return f'''<div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:20px;max-width:600px">
<h3 style="margin-bottom:16px;font-size:15px">添加知识</h3>
<form method="POST" action="/admin/add-knowledge">
<div class="form-group"><label>类型</label><select name="type">
{type_options}
</select></div>
<div class="form-group"><label>标题</label><input name="title" placeholder="简短描述" required></div>
<div class="form-group"><label>内容</label><textarea name="content" placeholder="详细内容（150-300字）"></textarea></div>
<div class="form-group"><label>标签（逗号分隔）</label><input name="tags" placeholder="标签1,标签2"></div>
<div class="form-group"><label>被否决的方案（每行一个，格式：方案名:原因）</label><textarea name="rejected" placeholder="Redux:重渲染性能问题&#10;MobX:团队不熟悉" style="min-height:60px"></textarea></div>
<button class="btn btn-primary" style="margin-top:8px">添加</button>
</form></div>'''


def get_credentials_page(creds):
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Agent 创建成功</title><style>{STYLE}</style></head><body>
<div class="wrap" style="max-width:500px;margin-top:60px">
<div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:24px">
<h3 style="margin-bottom:12px">✅ Agent 创建成功</h3>
<div class="error" style="color:#f59e0b">⚠️ 以下凭证只显示一次，请立即保存</div>
<div class="form-group"><label>Agent ID</label><input value="{esc(creds['agent_id'])}" readonly style="background:#0f172a"></div>
<div class="form-group"><label>Secret</label><input value="{esc(creds['secret'])}" readonly style="background:#0f172a"></div>
<div class="form-group"><label>名称</label><input value="{esc(creds['name'])}" readonly style="background:#0f172a"></div>
<div class="form-group"><label>角色</label><input value="{esc(creds['role'])}" readonly style="background:#0f172a"></div>
<a href="/admin?page=agents" class="btn btn-primary" style="margin-top:12px">已保存，返回管理</a>
</div></div></body></html>'''


def get_credentials_with_prompt_page(creds, server_url='http://localhost:9090'):
    agent_id = esc(creds['agent_id'])
    secret = esc(creds['secret'])
    name = esc(creds['name'])
    role = esc(creds['role'])

    prompt_text = f"""## EchoMemory 共享记忆对接指南

你已被授权接入 EchoMemory 共享记忆系统。以下是你的认证凭据和使用方式。

### 认证信息
- 服务地址: {server_url}
- Agent ID: {agent_id}
- Secret: {secret}

### 认证流程
每次会话开始时，先获取 Token：

```bash
curl -X POST {server_url}/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{{"agent_id": "{agent_id}", "secret": "{secret}"}}'
```

返回: {{"token": "eyJ...", "agent_id": "...", "expires_in": "72h"}}

后续请求在 Header 中携带: Authorization: Bearer <token>

### 核心操作

**查询知识（带上下文注入）：**
```bash
GET {server_url}/api/context?q=关键词&limit=10
```

**搜索知识：**
```bash
GET {server_url}/api/search?q=关键词&limit=20
```

**添加知识：**
```bash
POST {server_url}/api/knowledge
Content-Type: application/json
{{"type": "lesson|decision|rule|insight|process|reference|contact", "title": "...", "content": "...", "tags": ["tag1"], "rejected": [{{"option":"被否决方案","reason":"原因"}}]}}
```

**列出知识：**
```bash
GET {server_url}/api/knowledge?type=decision&tag=security&limit=50
```

### 使用原则
1. 每次会话开始时，用 /api/context 获取相关记忆作为上下文
2. 做出重要决策、发现教训、建立规则时，写入共享记忆
3. 记录被否决的方案和原因，避免团队重复踩坑
4. 标签要简洁有意义，便于跨 Agent 检索
5. 写入内容要精炼（150-300字），突出核心信息"""

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Agent 创建成功 + 对接提示词</title><style>{STYLE}</style></head><body>
<div class="wrap" style="max-width:700px;margin-top:40px">
<div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:24px;margin-bottom:20px">
<h3 style="margin-bottom:12px">✅ Agent 创建成功</h3>
<div class="error" style="color:#f59e0b">⚠️ 以下凭证只显示一次，请立即保存</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
<div class="form-group"><label>Agent ID</label><input value="{agent_id}" readonly style="background:#0f172a"></div>
<div class="form-group"><label>Secret</label><input value="{secret}" readonly style="background:#0f172a"></div>
<div class="form-group"><label>名称</label><input value="{name}" readonly style="background:#0f172a"></div>
<div class="form-group"><label>角色</label><input value="{role}" readonly style="background:#0f172a"></div>
</div>
</div>

<div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:24px;position:relative">
<h3 style="margin-bottom:12px">📋 对接提示词（复制给 Agent）</h3>
<button onclick="copyAll()" style="position:absolute;top:16px;right:16px;background:#f59e0b;color:#0f172a;border:none;padding:6px 14px;border-radius:4px;font-size:12px;cursor:pointer;font-weight:600">复制全部</button>
<pre id="fullPrompt" style="background:#0f172a;border:1px solid #334155;border-radius:6px;padding:14px;white-space:pre-wrap;font-size:11px;color:#e2e8f0;line-height:1.6;max-height:500px;overflow-y:auto;font-family:monospace">{esc(prompt_text)}</pre>
</div>

<div style="margin-top:16px;text-align:center">
<a href="/admin?page=integration" class="btn btn-primary">返回对接设置</a>
<a href="/admin?page=agents" class="btn" style="margin-left:8px">Agent 管理</a>
</div>
</div>
<script>
function copyAll() {{
    var text = document.getElementById('fullPrompt').textContent;
    navigator.clipboard.writeText(text).then(function() {{
        event.target.textContent = '已复制 ✓';
        setTimeout(function() {{ event.target.textContent = '复制全部'; }}, 2000);
    }});
}}
</script>
</body></html>'''
