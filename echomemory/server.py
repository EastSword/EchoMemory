"""REST API Server for EchoMemory — enables cross-device shared memory"""
import json
import os
import time
import traceback
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from .storage import Storage
from .models import KnowledgeItem, Relation
from .auth import AgentRegistry, verify_signature, sign_message, derive_shared_key, encrypt_payload
from .web_ui import get_login_page, get_admin_page, get_credentials_page

DEFAULT_PORT = int(os.environ.get("ECHOMEMORY_PORT", "9090"))


class EchoMemoryHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    storage = None
    registry = None

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}", flush=True)

    def _get_agent_from_token(self):
        """Extract and verify JWT from Authorization header"""
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return None
        token = auth[7:]
        payload = self.registry.verify_token(token)
        return payload

    def _get_agent_from_cookie(self):
        """Extract and verify JWT from cookie"""
        cookies = self.headers.get("Cookie", "")
        for part in cookies.split(";"):
            part = part.strip()
            if part.startswith("em_token="):
                token = part[9:]
                return self.registry.verify_token(token)
        return None

    def _verify_request_signature(self, agent_id: str, body: str = ""):
        """Verify Ed25519 signature on request"""
        signature = self.headers.get("X-Signature", "")
        timestamp = self.headers.get("X-Timestamp", "")
        if not signature or not timestamp:
            return False
        # Check timestamp freshness (5 min window)
        try:
            ts = int(timestamp)
            if abs(time.time() - ts) > 300:
                return False
        except:
            return False
        # Verify signature over: method + path + timestamp + body
        message = f"{self.command}|{self.path}|{timestamp}|{body}"
        public_key = self.registry.get_agent_public_key(agent_id)
        if not public_key:
            return False
        return verify_signature(message, signature, public_key)

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html, status=200):
        body = html.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        raw = self.headers.get("Content-Length")
        if not raw:
            return ""
        try:
            length = int(raw)
        except (ValueError, TypeError):
            return ""
        if length > 0:
            return self.rfile.read(length).decode()
        return ""

    def _parse_form(self, body):
        from urllib.parse import unquote_plus
        form = {}
        for pair in body.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                form[unquote_plus(k)] = unquote_plus(v)
        return form

    def _redirect(self, url):
        from urllib.parse import quote, urlparse, urlencode, parse_qs, urlunparse
        # Encode non-ASCII characters in query string for HTTP header compatibility
        parts = urlparse(url)
        if parts.query:
            params = parse_qs(parts.query, keep_blank_values=True)
            encoded_query = urlencode({k: v[0] for k, v in params.items()}, quote_via=quote)
            url = urlunparse(parts._replace(query=encoded_query))
        self.send_response(302)
        self.send_header("Location", url)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Signature, X-Timestamp")
        self.end_headers()

    def do_GET(self):
        try:
            self._handle_get()
        except Exception:
            traceback.print_exc()
            self._send_json({"error": "internal server error"}, 500)

    def _handle_get(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # Public endpoints (no auth required)
        if path == "/api/health":
            return self._send_json({"status": "ok", "service": "echomemory", "version": "0.1.0", "auth": "enabled"})

        # Web UI pages (server-side rendered, cookie-based auth)
        if path in ["/", "/login"]:
            return self._send_html(get_login_page())
        if path == "/logout":
            self.send_response(302)
            self.send_header("Location", "/login")
            self.send_header("Set-Cookie", "em_token=; Max-Age=0; Path=/")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if path == "/admin":
            agent = self._get_agent_from_cookie()
            if not agent:
                self.send_response(302)
                self.send_header("Location", "/login")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            page = params.get("page", ["knowledge"])[0]
            msg = params.get("msg", [""])[0]
            from .web_ui import get_admin_page
            html = get_admin_page(self.storage, self.registry, agent, page, msg)
            return self._send_html(html)

        # Auth endpoint
        if path == "/api/auth/login":
            return self._send_json({"error": "use POST"}, 405)

        # All other endpoints require auth
        agent = self._get_agent_from_token()
        if not agent:
            return self._send_json({"error": "unauthorized", "hint": "POST /api/auth/login with agent_id and secret"}, 401)

        # Optional: verify request signature for high-security mode
        sig_header = self.headers.get("X-Signature")
        if sig_header and not self._verify_request_signature(agent["sub"]):
            return self._send_json({"error": "invalid signature"}, 403)

        if path == "/api/stats":
            self._send_json(self.storage.stats())

        elif path == "/api/tags":
            tags = self.storage.get_tags()
            self._send_json([{"tag": t, "count": c} for t, c in tags])

        elif path == "/api/search":
            q = params.get("q", [""])[0]
            limit = int(params.get("limit", ["20"])[0])
            if not q:
                return self._send_json({"error": "q parameter required"}, 400)
            items = self.storage.search(q, limit)
            self._send_json([i.to_json() for i in items])

        elif path == "/api/knowledge":
            type_filter = params.get("type", [None])[0]
            tag_filter = params.get("tag", [None])[0]
            status = params.get("status", ["active"])[0]
            limit = int(params.get("limit", ["50"])[0])
            days = int(params.get("days", ["0"])[0]) or None
            items = self.storage.list_items(type_filter, tag_filter, status, limit, days)
            self._send_json([i.to_json() for i in items])

        elif path.startswith("/api/knowledge/"):
            item_id = path.split("/")[-1]
            item = self.storage.get(item_id)
            if item:
                self._send_json(item.to_json())
            else:
                self._send_json({"error": "not found"}, 404)

        elif path == "/api/context":
            q = params.get("q", [""])[0]
            limit = int(params.get("limit", ["10"])[0])
            items = self.storage.search(q, limit) if q else self.storage.list_items(limit=limit)
            context_lines = []
            for item in items:
                context_lines.append(item.summary())
                if item.rejected:
                    rejects = ", ".join(f"{r.get('option','?')}({r.get('reason','')})" for r in item.rejected)
                    context_lines.append(f"  rejected: {rejects}")
            self._send_json({"context": "\n".join(context_lines), "count": len(items), "agent": agent["sub"]})

        elif path == "/api/agents":
            if agent.get("role") != "admin":
                return self._send_json({"error": "admin only"}, 403)
            self._send_json(self.registry.list_agents())

        elif path == "/api/knowledge-types":
            types = self.storage.get_knowledge_types()
            self._send_json(types)

        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        try:
            self._handle_post()
        except Exception:
            traceback.print_exc()
            self._send_json({"error": "internal server error"}, 500)

    def _handle_post(self):
        parsed = urlparse(self.path)
        path = parsed.path
        raw_body = self._read_body()

        # === Web form handlers (cookie-based) ===
        if path == "/login":
            # Parse form data
            form = {}
            for pair in raw_body.split("&"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    from urllib.parse import unquote_plus
                    form[unquote_plus(k)] = unquote_plus(v)
            agent_id = form.get("agent_id", "")
            secret = form.get("secret", "")
            token = self.registry.authenticate(agent_id, secret)
            if not token:
                from .web_ui import get_login_page
                return self._send_html(get_login_page("认证失败：账号或密码错误"))
            self.send_response(302)
            self.send_header("Location", "/admin")
            self.send_header("Set-Cookie", f"em_token={token}; Path=/; HttpOnly; Max-Age=259200")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        if path == "/admin/delete":
            agent = self._get_agent_from_cookie()
            if not agent:
                return self._redirect("/login")
            form = self._parse_form(raw_body)
            item_id = form.get("id", "")
            if item_id:
                self.storage.delete(item_id)
            return self._redirect("/admin?page=knowledge&msg=已删除")

        if path == "/admin/add-knowledge":
            agent = self._get_agent_from_cookie()
            if not agent:
                return self._redirect("/login")
            form = self._parse_form(raw_body)
            rejected = []
            for line in form.get("rejected", "").split("\n"):
                line = line.strip()
                if ":" in line:
                    parts = line.split(":", 1)
                    rejected.append({"option": parts[0].strip(), "reason": parts[1].strip()})
            tags = [t.strip() for t in form.get("tags", "").split(",") if t.strip()]
            item = KnowledgeItem(
                type=form.get("type", "insight"),
                title=form.get("title", ""),
                content=form.get("content", ""),
                rejected=rejected,
                tags=tags,
                source={"agent": agent.get("sub", ""), "name": agent.get("name", "")},
            )
            if item.title:
                self.storage.add(item)
            return self._redirect("/admin?page=knowledge&msg=已添加")

        if path == "/admin/create-agent":
            agent = self._get_agent_from_cookie()
            if not agent or agent.get("role") != "admin":
                return self._redirect("/admin?page=agents&msg=需要admin权限")
            form = self._parse_form(raw_body)
            name = form.get("name", "")
            role = form.get("role", "agent")
            if name:
                creds = self.registry.create_agent(name, role)
                from .web_ui import get_credentials_page
                return self._send_html(get_credentials_page(creds))
            return self._redirect("/admin?page=agents&msg=名称不能为空")

        if path == "/admin/revoke":
            agent = self._get_agent_from_cookie()
            if not agent or agent.get("role") != "admin":
                return self._redirect("/admin?page=agents&msg=需要admin权限")
            form = self._parse_form(raw_body)
            target_id = form.get("agent_id", "")
            if target_id:
                self.registry.revoke_agent(target_id)
            return self._redirect("/admin?page=agents&msg=已撤销")

        if path == "/admin/add-type":
            agent = self._get_agent_from_cookie()
            if not agent or agent.get("role") != "admin":
                return self._redirect("/admin?page=types&msg=需要admin权限")
            form = self._parse_form(raw_body)
            name = form.get("name", "").strip().lower()
            label = form.get("label", "").strip()
            description = form.get("description", "").strip()
            color = form.get("color", "#94a3b8").strip()
            if name and label:
                self.storage.add_knowledge_type(name, label, description, color)
                return self._redirect("/admin?page=types&msg=类型已添加")
            return self._redirect("/admin?page=types&msg=名称和显示名不能为空")

        if path == "/admin/update-type":
            agent = self._get_agent_from_cookie()
            if not agent or agent.get("role") != "admin":
                return self._redirect("/admin?page=types&msg=需要admin权限")
            form = self._parse_form(raw_body)
            name = form.get("name", "").strip()
            label = form.get("label", "").strip() or None
            description = form.get("description", "").strip()
            color = form.get("color", "").strip() or None
            if name:
                self.storage.update_knowledge_type(name, label, description, color)
            return self._redirect("/admin?page=types&msg=类型已更新")

        if path == "/admin/delete-type":
            agent = self._get_agent_from_cookie()
            if not agent or agent.get("role") != "admin":
                return self._redirect("/admin?page=types&msg=需要admin权限")
            form = self._parse_form(raw_body)
            name = form.get("name", "").strip()
            if name:
                success = self.storage.delete_knowledge_type(name)
                if not success:
                    return self._redirect("/admin?page=types&msg=无法删除：内置类型或仍有关联知识")
            return self._redirect("/admin?page=types&msg=类型已删除")

        if path == "/admin/create-agent-with-prompt":
            agent = self._get_agent_from_cookie()
            if not agent or agent.get("role") != "admin":
                return self._redirect("/admin?page=integration&msg=需要admin权限")
            form = self._parse_form(raw_body)
            name = form.get("name", "")
            role = form.get("role", "agent")
            server_url = form.get("server_url", "http://localhost:9090")
            if name:
                creds = self.registry.create_agent(name, role)
                from .web_ui import get_credentials_with_prompt_page
                return self._send_html(get_credentials_with_prompt_page(creds, server_url))
            return self._redirect("/admin?page=integration&msg=名称不能为空")

        # === API handlers (token-based) ===
        data = json.loads(raw_body) if raw_body and raw_body.startswith("{") else {}

        # Auth login — no token required
        if path == "/api/auth/login":
            agent_id = data.get("agent_id", "")
            secret = data.get("secret", "")
            if not agent_id or not secret:
                return self._send_json({"error": "agent_id and secret required"}, 400)
            token = self.registry.authenticate(agent_id, secret)
            if not token:
                return self._send_json({"error": "authentication failed"}, 401)
            return self._send_json({"token": token, "agent_id": agent_id, "expires_in": "72h"})

        # All other POST endpoints require auth
        agent = self._get_agent_from_token()
        if not agent:
            return self._send_json({"error": "unauthorized"}, 401)

        # Optional signature verification
        sig_header = self.headers.get("X-Signature")
        if sig_header and not self._verify_request_signature(agent["sub"], raw_body):
            return self._send_json({"error": "invalid signature"}, 403)

        if path == "/api/knowledge":
            item = KnowledgeItem(
                type=data.get("type", "insight"),
                title=data.get("title", ""),
                content=data.get("content", ""),
                context=data.get("context", ""),
                rejected=data.get("rejected", []),
                tags=data.get("tags", []),
                source={"agent": agent["sub"], "name": agent.get("name", "")},
                confidence=data.get("confidence", 0.8),
            )
            if not item.title:
                return self._send_json({"error": "title required"}, 400)
            item_id = self.storage.add(item)
            self._send_json({"id": item_id, "status": "created", "by": agent["sub"]})

        elif path == "/api/relations":
            rel = Relation(
                from_id=data.get("from_id", ""),
                to_id=data.get("to_id", ""),
                type=data.get("type", "related_to"),
                note=data.get("note", ""),
            )
            if not rel.from_id or not rel.to_id:
                return self._send_json({"error": "from_id and to_id required"}, 400)
            self.storage.add_relation(rel)
            self._send_json({"status": "created"})

        elif path == "/api/agents/create":
            if agent.get("role") != "admin":
                return self._send_json({"error": "admin only"}, 403)
            name = data.get("name", "")
            role = data.get("role", "agent")
            if not name:
                return self._send_json({"error": "name required"}, 400)
            creds = self.registry.create_agent(name, role)
            self._send_json(creds)

        elif path == "/api/agents/revoke":
            if agent.get("role") != "admin":
                return self._send_json({"error": "admin only"}, 403)
            target_id = data.get("agent_id", "")
            if not target_id:
                return self._send_json({"error": "agent_id required"}, 400)
            self.registry.revoke_agent(target_id)
            self._send_json({"status": "revoked", "agent_id": target_id})

        else:
            self._send_json({"error": "not found"}, 404)

    def do_PUT(self):
        try:
            self._handle_put()
        except Exception:
            traceback.print_exc()
            self._send_json({"error": "internal server error"}, 500)

    def _handle_put(self):
        agent = self._get_agent_from_token()
        if not agent:
            return self._send_json({"error": "unauthorized"}, 401)

        parsed = urlparse(self.path)
        path = parsed.path
        raw_body = self._read_body()
        data = json.loads(raw_body) if raw_body else {}

        if path.startswith("/api/knowledge/") and path.endswith("/status"):
            item_id = path.split("/")[-2]
            new_status = data.get("status", "")
            superseded_by = data.get("superseded_by", "")
            if new_status not in ("active", "superseded", "archived"):
                return self._send_json({"error": "invalid status"}, 400)
            self.storage.update_status(item_id, new_status, superseded_by)
            self._send_json({"status": "updated"})
        else:
            self._send_json({"error": "not found"}, 404)

    def do_DELETE(self):
        try:
            self._handle_delete()
        except Exception:
            traceback.print_exc()
            self._send_json({"error": "internal server error"}, 500)

    def _handle_delete(self):
        agent = self._get_agent_from_token()
        if not agent:
            return self._send_json({"error": "unauthorized"}, 401)
        if agent.get("role") != "admin":
            return self._send_json({"error": "admin only"}, 403)

        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/knowledge/"):
            item_id = path.split("/")[-1]
            self.storage.delete(item_id)
            self._send_json({"status": "deleted"})
        else:
            self._send_json({"error": "not found"}, 404)


def run_server(port=DEFAULT_PORT, token=None, db_path=None):
    storage = Storage(db_path)
    registry = AgentRegistry(storage.db_path.replace("memory.db", "auth.db"))

    EchoMemoryHandler.storage = storage
    EchoMemoryHandler.registry = registry

    # Check if admin exists, create one if not
    agents = registry.list_agents()
    if not agents:
        print("No agents found. Creating admin account...")
        creds = registry.create_agent("admin", "admin")
        print(f"  Admin created!")
        print(f"  agent_id: {creds['agent_id']}")
        print(f"  secret:   {creds['secret']}")
        print(f"  Save these credentials — the secret won't be shown again.")
        print()

    server = ThreadingHTTPServer(("0.0.0.0", port), EchoMemoryHandler)
    print(f"EchoMemory Server v0.1.0")
    print(f"  Port: {port}")
    print(f"  Database: {storage.db_path}")
    print(f"  Auth DB: {registry.db_path}")
    print(f"  Agents: {len(agents)} registered")
    print(f"  Security: JWT + Ed25519 signatures + scrypt password hashing")
    print(f"  Endpoints:")
    print(f"    POST /api/auth/login          — authenticate (get JWT)")
    print(f"    GET  /api/knowledge           — list knowledge")
    print(f"    GET  /api/search?q=...        — search")
    print(f"    POST /api/knowledge           — add knowledge")
    print(f"    POST /api/agents/create       — create agent (admin)")
    print(f"    POST /api/agents/revoke       — revoke agent (admin)")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()
