"""Web UI for EchoMemory — Admin management dashboard"""


def get_login_page():
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EchoMemory - Login</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='48' fill='%230f172a'/><circle cx='50' cy='50' r='18' fill='none' stroke='%23f59e0b' stroke-width='1.5' opacity='0.3'/><circle cx='50' cy='50' r='28' fill='none' stroke='%23f59e0b' stroke-width='1' opacity='0.2'/><circle cx='50' cy='50' r='38' fill='none' stroke='%23f59e0b' stroke-width='0.7' opacity='0.12'/><circle cx='50' cy='50' r='8' fill='%23f59e0b' opacity='0.9'/><circle cx='50' cy='50' r='5' fill='%23fbbf24'/><line x1='50' y1='50' x2='28' y2='32' stroke='%2322c55e' stroke-width='1.5' opacity='0.7'/><line x1='50' y1='50' x2='72' y2='35' stroke='%2360a5fa' stroke-width='1.5' opacity='0.7'/><line x1='50' y1='50' x2='35' y2='72' stroke='%23c084fc' stroke-width='1.5' opacity='0.7'/><line x1='50' y1='50' x2='70' y2='68' stroke='%23f472b6' stroke-width='1.5' opacity='0.7'/><circle cx='28' cy='32' r='4' fill='%2322c55e'/><circle cx='72' cy='35' r='4' fill='%2360a5fa'/><circle cx='35' cy='72' r='4' fill='%23c084fc'/><circle cx='70' cy='68' r='4' fill='%23f472b6'/><circle cx='50' cy='50' r='46' fill='none' stroke='%23f59e0b' stroke-width='1.5' opacity='0.5' stroke-dasharray='4,3'/></svg>">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#0f172a;display:flex;align-items:center;justify-content:center;min-height:100vh}
.login-card{background:#1e293b;border-radius:12px;padding:40px;width:360px;box-shadow:0 20px 60px rgba(0,0,0,.4)}
.logo{text-align:center;margin-bottom:24px;font-size:24px;font-weight:700;color:#f8fafc}
.logo span{color:#f59e0b}
.form-group{margin-bottom:16px}
.form-group label{display:block;font-size:12px;color:#94a3b8;margin-bottom:6px}
.form-group input{width:100%;padding:10px 14px;border:1px solid #334155;border-radius:8px;background:#0f172a;color:#f8fafc;font-size:14px}
.form-group input:focus{outline:none;border-color:#f59e0b}
.btn{width:100%;padding:12px;background:#f59e0b;color:#0f172a;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;margin-top:8px}
.btn:hover{background:#d97706}
.error{color:#ef4444;font-size:12px;margin-top:8px;display:none}
</style>
</head>
<body>
<div class="login-card">
<div class="logo"><svg width="22" height="22" viewBox="0 0 100 100" style="vertical-align:middle;margin-right:6px"><defs><linearGradient id="lg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#f59e0b"/><stop offset="100%" stop-color="#d97706"/></linearGradient></defs><circle cx="50" cy="50" r="45" fill="#0f172a" stroke="url(#lg)" stroke-width="4"/><path d="M30 50 C30 35 40 25 50 25 C60 25 70 35 70 50 C70 65 60 75 50 75 C40 75 30 65 30 50 Z" fill="none" stroke="#f59e0b" stroke-width="3"/><circle cx="50" cy="42" r="6" fill="#f59e0b"/><path d="M38 58 Q50 68 62 58" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round"/><circle cx="35" cy="50" r="3" fill="#22c55e" opacity="0.8"/><circle cx="65" cy="50" r="3" fill="#60a5fa" opacity="0.8"/><circle cx="50" cy="30" r="2.5" fill="#c084fc" opacity="0.8"/></svg>Echo<span>Memory</span></div>
<div class="form-group"><label>Agent ID</label><input id="agentId" placeholder="agent_xxxxxxxx"></div>
<div class="form-group"><label>Secret</label><input id="secret" type="password" placeholder="your secret"></div>
<button class="btn" onclick="login()">Login</button>
<div class="error" id="error"></div>
</div>
<script>
async function login(){
    var err=document.getElementById('error');err.style.display='none';
    var res=await fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({agent_id:document.getElementById('agentId').value,secret:document.getElementById('secret').value})});
    var data=await res.json();
    if(data.token){localStorage.setItem('em_token',data.token);localStorage.setItem('em_agent',data.agent_id);window.location='/admin';}
    else{err.textContent=data.error||'Login failed';err.style.display='block';}
}
document.addEventListener('keydown',function(e){if(e.key==='Enter')login();});
</script>
</body>
</html>'''


def get_admin_page():
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EchoMemory - Admin</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='48' fill='%230f172a'/><circle cx='50' cy='50' r='18' fill='none' stroke='%23f59e0b' stroke-width='1.5' opacity='0.3'/><circle cx='50' cy='50' r='28' fill='none' stroke='%23f59e0b' stroke-width='1' opacity='0.2'/><circle cx='50' cy='50' r='38' fill='none' stroke='%23f59e0b' stroke-width='0.7' opacity='0.12'/><circle cx='50' cy='50' r='8' fill='%23f59e0b' opacity='0.9'/><circle cx='50' cy='50' r='5' fill='%23fbbf24'/><line x1='50' y1='50' x2='28' y2='32' stroke='%2322c55e' stroke-width='1.5' opacity='0.7'/><line x1='50' y1='50' x2='72' y2='35' stroke='%2360a5fa' stroke-width='1.5' opacity='0.7'/><line x1='50' y1='50' x2='35' y2='72' stroke='%23c084fc' stroke-width='1.5' opacity='0.7'/><line x1='50' y1='50' x2='70' y2='68' stroke='%23f472b6' stroke-width='1.5' opacity='0.7'/><circle cx='28' cy='32' r='4' fill='%2322c55e'/><circle cx='72' cy='35' r='4' fill='%2360a5fa'/><circle cx='35' cy='72' r='4' fill='%23c084fc'/><circle cx='70' cy='68' r='4' fill='%23f472b6'/><circle cx='50' cy='50' r='46' fill='none' stroke='%23f59e0b' stroke-width='1.5' opacity='0.5' stroke-dasharray='4,3'/></svg>">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0f172a;--card:#1e293b;--border:#334155;--text:#f8fafc;--sec:#94a3b8;--accent:#f59e0b;--success:#22c55e;--danger:#ef4444}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--bg);color:var(--text);font-size:13px}
.header{background:var(--card);border-bottom:1px solid var(--border);padding:12px 24px;display:flex;align-items:center;gap:20px}
.logo{font-size:18px;font-weight:700}.logo span{color:var(--accent)}
.nav{display:flex;gap:4px;margin-left:24px}
.nav button{padding:6px 14px;border-radius:6px;border:1px solid var(--border);background:transparent;color:var(--sec);cursor:pointer;font-size:12px}
.nav button.active{background:var(--accent);color:var(--bg);border-color:var(--accent)}
.nav button:hover:not(.active){border-color:var(--accent);color:var(--accent)}
.user-info{margin-left:auto;font-size:11px;color:var(--sec)}
.logout{color:var(--danger);cursor:pointer;margin-left:12px;font-size:11px}
.container{max-width:1200px;margin:0 auto;padding:20px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:20px}
.stat-card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:16px;text-align:center}
.stat-card .num{font-size:28px;font-weight:700;color:var(--accent)}
.stat-card .label{font-size:11px;color:var(--sec);margin-top:4px}
.panel{display:none}.panel.active{display:block}
.toolbar{display:flex;gap:8px;margin-bottom:14px;align-items:center;flex-wrap:wrap}
.search-input{padding:8px 12px;border:1px solid var(--border);border-radius:6px;background:var(--bg);color:var(--text);font-size:12px;width:200px}
.search-input:focus{outline:none;border-color:var(--accent)}
.btn{padding:6px 14px;border:1px solid var(--border);border-radius:6px;background:var(--card);color:var(--text);cursor:pointer;font-size:12px}
.btn:hover{border-color:var(--accent)}
.btn-primary{background:var(--accent);color:var(--bg);border:none;font-weight:600}
.btn-danger{background:var(--danger);color:#fff;border:none}
.btn-sm{padding:4px 10px;font-size:11px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--border);border-radius:8px;overflow:hidden}
th{background:var(--bg);padding:10px 12px;text-align:left;font-size:11px;color:var(--sec);font-weight:600;border-bottom:1px solid var(--border)}
td{padding:10px 12px;border-bottom:1px solid var(--border);font-size:12px;vertical-align:top}
tr:last-child td{border-bottom:none}
.tag{display:inline-block;padding:2px 6px;border-radius:4px;font-size:10px;background:rgba(245,158,11,0.15);color:var(--accent);margin:1px 2px}
.type-badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:600}
.type-decision{background:rgba(59,130,246,0.2);color:#60a5fa}
.type-lesson{background:rgba(239,68,68,0.2);color:#f87171}
.type-rule{background:rgba(34,197,94,0.2);color:#4ade80}
.type-insight{background:rgba(168,85,247,0.2);color:#c084fc}
.type-process{background:rgba(6,182,212,0.2);color:#22d3ee}
.type-reference{background:rgba(148,163,184,0.2);color:#94a3b8}
.type-contact{background:rgba(251,146,60,0.2);color:#fb923c}
.status-active{color:var(--success)}.status-superseded{color:var(--sec);text-decoration:line-through}.status-archived{color:var(--sec)}
.rejected{font-size:11px;color:#f87171;margin-top:4px}
.content-preview{font-size:11px;color:var(--sec);margin-top:4px;max-width:400px}
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:100;align-items:center;justify-content:center}
.modal-overlay.active{display:flex}
.modal{background:var(--card);border-radius:10px;padding:24px;min-width:450px;max-width:600px;width:90%;max-height:80vh;overflow-y:auto}
.modal h3{margin-bottom:16px;font-size:16px}
.modal label{display:block;font-size:11px;color:var(--sec);margin:12px 0 4px}
.modal input,.modal select,.modal textarea{width:100%;padding:8px 12px;border:1px solid var(--border);border-radius:6px;background:var(--bg);color:var(--text);font-size:13px}
.modal textarea{min-height:80px;resize:vertical}
.modal .actions{display:flex;justify-content:flex-end;gap:8px;margin-top:20px}
.empty{text-align:center;padding:40px;color:var(--sec)}
</style>
</head>
<body>
<header class="header">
<div class="logo"><svg width="22" height="22" viewBox="0 0 100 100" style="vertical-align:middle;margin-right:6px"><defs><linearGradient id="lg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#f59e0b"/><stop offset="100%" stop-color="#d97706"/></linearGradient></defs><circle cx="50" cy="50" r="45" fill="#0f172a" stroke="url(#lg)" stroke-width="4"/><path d="M30 50 C30 35 40 25 50 25 C60 25 70 35 70 50 C70 65 60 75 50 75 C40 75 30 65 30 50 Z" fill="none" stroke="#f59e0b" stroke-width="3"/><circle cx="50" cy="42" r="6" fill="#f59e0b"/><path d="M38 58 Q50 68 62 58" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round"/><circle cx="35" cy="50" r="3" fill="#22c55e" opacity="0.8"/><circle cx="65" cy="50" r="3" fill="#60a5fa" opacity="0.8"/><circle cx="50" cy="30" r="2.5" fill="#c084fc" opacity="0.8"/></svg>Echo<span>Memory</span></div>
<nav class="nav">
<button class="active" onclick="showPanel('knowledge')">知识库</button>
<button onclick="showPanel('agents')">Agent 管理</button>
</nav>
<span class="user-info" id="userInfo"></span>
<span class="logout" onclick="logout()">退出</span>
</header>
<div class="container">
<div class="stats" id="statsRow"></div>
<div class="panel active" id="panel-knowledge">
<div class="toolbar">
<input class="search-input" id="searchInput" placeholder="搜索知识..." onkeydown="if(event.key==='Enter')searchKnowledge()">
<button class="btn" onclick="searchKnowledge()">搜索</button>
<select id="typeFilter" onchange="loadKnowledge()" style="padding:6px;border:1px solid var(--border);border-radius:6px;background:var(--bg);color:var(--text);font-size:12px">
<option value="">全部类型</option>
<option value="decision">decision</option>
<option value="lesson">lesson</option>
<option value="rule">rule</option>
<option value="insight">insight</option>
<option value="process">process</option>
<option value="reference">reference</option>
<option value="contact">contact</option>
</select>
<button class="btn btn-primary" onclick="openAddModal()" style="margin-left:auto">+ 添加知识</button>
</div>
<table id="knowledgeTable"><thead><tr><th>类型</th><th>标题</th><th>标签</th><th>来源</th><th>时间</th><th>操作</th></tr></thead><tbody id="knowledgeBody"></tbody></table>
</div>
<div class="panel" id="panel-agents">
<div class="toolbar">
<button class="btn btn-primary" onclick="openCreateAgentModal()">+ 创建 Agent</button>
</div>
<table><thead><tr><th>Agent ID</th><th>名称</th><th>角色</th><th>状态</th><th>创建时间</th><th>最后认证</th><th>操作</th></tr></thead><tbody id="agentsBody"></tbody></table>
</div>
</div>
<!-- Add Knowledge Modal -->
<div class="modal-overlay" id="addModal">
<div class="modal">
<h3>添加知识</h3>
<label>类型</label>
<select id="addType"><option value="decision">decision</option><option value="lesson">lesson</option><option value="rule">rule</option><option value="insight">insight</option><option value="process">process</option><option value="reference">reference</option><option value="contact">contact</option></select>
<label>标题</label><input id="addTitle" placeholder="简短描述">
<label>内容</label><textarea id="addContent" placeholder="详细内容（150-300字）"></textarea>
<label>标签（逗号分隔）</label><input id="addTags" placeholder="标签1,标签2">
<label>被否决的方案（每行一个，格式：方案名:原因）</label><textarea id="addRejected" placeholder="Redux:重渲染性能问题&#10;MobX:团队不熟悉" style="min-height:60px"></textarea>
<div class="actions">
<button class="btn" onclick="closeModal('addModal')">取消</button>
<button class="btn btn-primary" onclick="addKnowledge()">添加</button>
</div>
</div>
</div>
<!-- Create Agent Modal -->
<div class="modal-overlay" id="agentModal">
<div class="modal">
<h3>创建 Agent 账号</h3>
<label>名称</label><input id="agentName" placeholder="如: codex-macbook, cursor-office">
<label>角色</label>
<select id="agentRole"><option value="agent">agent（普通）</option><option value="admin">admin（管理员）</option></select>
<div class="actions">
<button class="btn" onclick="closeModal('agentModal')">取消</button>
<button class="btn btn-primary" onclick="createAgent()">创建</button>
</div>
</div>
</div>
<!-- Agent Credentials Modal -->
<div class="modal-overlay" id="credsModal">
<div class="modal">
<h3>Agent 创建成功</h3>
<p style="color:var(--danger);font-size:12px;margin-bottom:12px">⚠️ 以下凭证只显示一次，请立即保存</p>
<label>Agent ID</label><input id="credsId" readonly style="background:var(--card)">
<label>Secret</label><input id="credsSecret" readonly style="background:var(--card)">
<label>名称</label><input id="credsName" readonly style="background:var(--card)">
<div class="actions">
<button class="btn btn-primary" onclick="closeModal('credsModal')">已保存，关闭</button>
</div>
</div>
</div>
<script>
var token=localStorage.getItem('em_token');
var agentId=localStorage.getItem('em_agent');
if(!token)window.location='/login';
document.getElementById('userInfo').textContent=agentId||'';

function headers(){return{'Authorization':'Bearer '+token,'Content-Type':'application/json'};}
function showPanel(name){
    document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
    document.getElementById('panel-'+name).classList.add('active');
    document.querySelectorAll('.nav button').forEach(function(b){
        b.classList.toggle('active', b.textContent.includes(name==='knowledge'?'知识':'Agent'));
    });
    if(name==='agents')loadAgents();
    if(name==='knowledge')loadKnowledge();
}
function logout(){localStorage.removeItem('em_token');localStorage.removeItem('em_agent');window.location='/login';}
function openModal(id){document.getElementById(id).classList.add('active');}
function closeModal(id){document.getElementById(id).classList.remove('active');}
document.querySelectorAll('.modal-overlay').forEach(m=>m.addEventListener('click',function(e){if(e.target===e.currentTarget)e.target.classList.remove('active');}));

async function loadStats(){
    var res=await fetch('/api/stats',{headers:headers()});
    if(res.status===401){logout();return;}
    var s=await res.json();
    var tagsRes=await fetch('/api/tags',{headers:headers()});
    var tags=await tagsRes.json();
    document.getElementById('statsRow').innerHTML=
        '<div class="stat-card"><div class="num">'+s.active+'</div><div class="label">活跃知识</div></div>'+
        '<div class="stat-card"><div class="num">'+Object.keys(s.by_type||{}).length+'</div><div class="label">知识类型</div></div>'+
        '<div class="stat-card"><div class="num">'+(Array.isArray(tags)?tags.length:0)+'</div><div class="label">标签数</div></div>'+
        '<div class="stat-card"><div class="num">'+s.total+'</div><div class="label">总条目</div></div>';
}

async function loadKnowledge(){
    var type=document.getElementById('typeFilter').value;
    var url='/api/knowledge?limit=50'+(type?'&type='+type:'');
    var res=await fetch(url,{headers:headers()});
    if(res.status===401){logout();return;}
    var items=await res.json();
    if(!Array.isArray(items)){items=[];}
    renderKnowledge(items);
}

async function searchKnowledge(){
    var q=document.getElementById('searchInput').value.trim();
    if(!q){loadKnowledge();return;}
    var res=await fetch('/api/search?q='+encodeURIComponent(q)+'&limit=30',{headers:headers()});
    var items=await res.json();
    renderKnowledge(items);
}

function renderKnowledge(items){
    var body=document.getElementById('knowledgeBody');
    if(!items.length){body.innerHTML='<tr><td colspan="6" class="empty">暂无数据</td></tr>';return;}
    body.innerHTML=items.map(function(item){
        var tags=(item.tags||[]).map(function(t){return '<span class="tag">'+t+'</span>';}).join('');
        var rejected='';
        if(item.rejected&&item.rejected.length){
            rejected='<div class="rejected">✗ '+item.rejected.map(function(r){return r.option+'('+r.reason+')';}).join('; ')+'</div>';
        }
        var content=item.content?'<div class="content-preview">'+item.content.substring(0,100)+(item.content.length>100?'...':'')+'</div>':'';
        var source=item.source?((item.source.agent||'')+(item.source.name?' '+item.source.name:'')):'';
        return '<tr>'+
            '<td><span class="type-badge type-'+item.type+'">'+item.type+'</span></td>'+
            '<td><strong>'+item.title+'</strong>'+content+rejected+'</td>'+
            '<td>'+tags+'</td>'+
            '<td style="font-size:11px;color:var(--sec)">'+source+'</td>'+
            '<td style="font-size:11px;color:var(--sec);white-space:nowrap">'+(item.created_at||'').substring(0,10)+'</td>'+
            '<td><button class="btn btn-sm btn-danger" onclick="deleteKnowledge(\''+item.id+'\')">删除</button></td>'+
            '</tr>';
    }).join('');
}

function openAddModal(){openModal('addModal');}

async function addKnowledge(){
    var rejected=document.getElementById('addRejected').value.trim().split('\\n').filter(Boolean).map(function(line){
        var parts=line.split(':');return{option:parts[0].trim(),reason:(parts[1]||'').trim()};
    });
    var tags=document.getElementById('addTags').value.split(',').map(function(t){return t.trim();}).filter(Boolean);
    var res=await fetch('/api/knowledge',{method:'POST',headers:headers(),body:JSON.stringify({
        type:document.getElementById('addType').value,
        title:document.getElementById('addTitle').value,
        content:document.getElementById('addContent').value,
        tags:tags,
        rejected:rejected.length?rejected:undefined
    })});
    var data=await res.json();
    if(data.id){closeModal('addModal');loadKnowledge();loadStats();
        document.getElementById('addTitle').value='';document.getElementById('addContent').value='';
        document.getElementById('addTags').value='';document.getElementById('addRejected').value='';
    }else{alert(data.error||'Failed');}
}

async function deleteKnowledge(id){
    if(!confirm('确认删除？'))return;
    await fetch('/api/knowledge/'+id,{method:'DELETE',headers:headers()});
    loadKnowledge();loadStats();
}

async function loadAgents(){
    var res=await fetch('/api/agents',{headers:headers()});
    if(res.status===403){document.getElementById('agentsBody').innerHTML='<tr><td colspan="7" class="empty">需要 admin 权限</td></tr>';return;}
    var agents=await res.json();
    document.getElementById('agentsBody').innerHTML=agents.map(function(a){
        var statusClass=a.is_active?'status-active':'status-archived';
        var statusText=a.is_active?'活跃':'已撤销';
        return '<tr>'+
            '<td style="font-family:monospace;font-size:11px">'+a.agent_id+'</td>'+
            '<td>'+a.name+'</td>'+
            '<td><span class="type-badge type-'+(a.role==='admin'?'decision':'insight')+'">'+a.role+'</span></td>'+
            '<td><span class="'+statusClass+'">'+statusText+'</span></td>'+
            '<td style="font-size:11px;color:var(--sec)">'+(a.created_at||'').substring(0,10)+'</td>'+
            '<td style="font-size:11px;color:var(--sec)">'+(a.last_auth?(a.last_auth).substring(0,16).replace('T',' '):'从未')+'</td>'+
            '<td>'+(a.is_active?'<button class="btn btn-sm btn-danger" onclick="revokeAgent(\''+a.agent_id+'\')">撤销</button>':'')+'</td>'+
            '</tr>';
    }).join('');
}

function openCreateAgentModal(){openModal('agentModal');}

async function createAgent(){
    var name=document.getElementById('agentName').value.trim();
    if(!name){alert('请输入名称');return;}
    var res=await fetch('/api/agents/create',{method:'POST',headers:headers(),body:JSON.stringify({
        name:name,role:document.getElementById('agentRole').value
    })});
    var data=await res.json();
    if(data.agent_id){
        closeModal('agentModal');
        document.getElementById('credsId').value=data.agent_id;
        document.getElementById('credsSecret').value=data.secret;
        document.getElementById('credsName').value=data.name;
        openModal('credsModal');
        loadAgents();
        document.getElementById('agentName').value='';
    }else{alert(data.error||'Failed');}
}

async function revokeAgent(id){
    if(!confirm('确认撤销 '+id+' 的访问权限？'))return;
    await fetch('/api/agents/revoke',{method:'POST',headers:headers(),body:JSON.stringify({agent_id:id})});
    loadAgents();
}

loadStats();loadKnowledge();
</script>
</body>
</html>'''
