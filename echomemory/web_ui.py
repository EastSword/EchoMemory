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
    elif page == 'add':
        content = _render_add_page()
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
<form method="POST" action="/admin/create-agent" style="display:flex;gap:8px;align-items:end">
<div class="form-group" style="margin:0;flex:1"><label>名称</label><input name="name" placeholder="如: codex-macbook" required></div>
<div class="form-group" style="margin:0;width:120px"><label>角色</label><select name="role"><option value="agent">agent</option><option value="admin">admin</option></select></div>
<button class="btn btn-primary">创建</button>
</form></div>'''

    return f'''<table>
<thead><tr><th>Agent ID</th><th>名称</th><th>角色</th><th>状态</th><th>创建时间</th><th>最后认证</th><th>操作</th></tr></thead>
<tbody>{rows}</tbody>
</table>
{create_form}'''


def _render_add_page():
    return '''<div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:20px;max-width:600px">
<h3 style="margin-bottom:16px;font-size:15px">添加知识</h3>
<form method="POST" action="/admin/add-knowledge">
<div class="form-group"><label>类型</label><select name="type">
<option value="decision">decision（决策）</option>
<option value="lesson">lesson（教训）</option>
<option value="rule">rule（规则）</option>
<option value="insight">insight（洞察）</option>
<option value="process">process（流程）</option>
<option value="reference">reference（参考）</option>
<option value="contact">contact（联系人）</option>
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
