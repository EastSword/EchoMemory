"""MCP Server for EchoMemory — enables AI Agents to directly read/write shared memory"""
import sys
import json
from .storage import Storage
from .models import KnowledgeItem


def run_mcp(storage: Storage):
    """Run as MCP server over stdio"""
    # MCP protocol: read JSON-RPC from stdin, write to stdout
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line.strip())
            response = handle_request(request, storage)
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            continue
        except EOFError:
            break
        except Exception as e:
            error_response = {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": None}
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()


def handle_request(request: dict, storage: Storage) -> dict:
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "echomemory", "version": "0.1.0"}
            }
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": get_tool_definitions()}
        }

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        result = call_tool(tool_name, arguments, storage)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"content": [{"type": "text", "text": result}]}
        }

    elif method == "notifications/initialized":
        return None  # No response needed for notifications

    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }


def get_tool_definitions():
    return [
        {
            "name": "memory_add",
            "description": "Add a knowledge item to EchoMemory. Use this when a decision is made, a lesson is learned, or important information should be remembered across sessions.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["decision", "lesson", "process", "insight", "contact", "reference", "rule"], "description": "Type of knowledge"},
                    "title": {"type": "string", "description": "Short title summarizing the knowledge"},
                    "content": {"type": "string", "description": "Detailed content (150-300 chars recommended)"},
                    "context": {"type": "string", "description": "Context when this knowledge was created"},
                    "rejected": {"type": "array", "items": {"type": "object", "properties": {"option": {"type": "string"}, "reason": {"type": "string"}}}, "description": "Rejected alternatives (required for decisions)"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for categorization (at least 2)"},
                },
                "required": ["type", "title"]
            }
        },
        {
            "name": "memory_search",
            "description": "Search EchoMemory for relevant knowledge. Use this before making decisions to check if similar decisions were made before.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (keywords or natural language)"},
                    "limit": {"type": "integer", "description": "Max results (default 10)", "default": 10},
                },
                "required": ["query"]
            }
        },
        {
            "name": "memory_context",
            "description": "Get all relevant knowledge for the current task context. Call this at the start of a new task to load prior decisions and lessons.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Task description or topic to get context for"},
                    "limit": {"type": "integer", "description": "Max items (default 10)", "default": 10},
                },
                "required": ["query"]
            }
        },
        {
            "name": "memory_update",
            "description": "Update the status of a knowledge item (e.g., mark as superseded when a decision changes).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Knowledge item ID"},
                    "status": {"type": "string", "enum": ["active", "superseded", "archived"]},
                    "superseded_by": {"type": "string", "description": "ID of the new item that replaces this one"},
                },
                "required": ["id", "status"]
            }
        },
        {
            "name": "memory_history",
            "description": "View the history of decisions on a topic, including superseded ones.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Topic to get history for"},
                    "limit": {"type": "integer", "default": 20},
                },
                "required": ["query"]
            }
        },
    ]


def call_tool(name: str, arguments: dict, storage: Storage) -> str:
    if name == "memory_add":
        item = KnowledgeItem(
            type=arguments.get("type", "insight"),
            title=arguments.get("title", ""),
            content=arguments.get("content", ""),
            context=arguments.get("context", ""),
            rejected=arguments.get("rejected", []),
            tags=arguments.get("tags", []),
            source={"agent": "mcp"},
        )
        if not item.title:
            return "Error: title is required"
        item_id = storage.add(item)
        return f"Knowledge added: {item_id}\nType: {item.type}\nTitle: {item.title}"

    elif name == "memory_search":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        items = storage.search(query, limit)
        if not items:
            return "No relevant knowledge found."
        lines = [f"Found {len(items)} relevant items:\n"]
        for item in items:
            lines.append(f"- {item.summary()}")
            if item.content:
                lines.append(f"  {item.content[:150]}")
            if item.rejected:
                rejects = "; ".join(f"{r.get('option','')}({r.get('reason','')})" for r in item.rejected)
                lines.append(f"  rejected: {rejects}")
            lines.append("")
        return "\n".join(lines)

    elif name == "memory_context":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        items = storage.search(query, limit) if query else storage.list_items(limit=limit)
        if not items:
            return "No prior knowledge found for this context."
        lines = ["## Prior Knowledge (EchoMemory)\n"]
        for item in items:
            lines.append(f"- [{item.type}] {item.title} ({item.created_at[:10]})")
            if item.content:
                lines.append(f"  {item.content[:200]}")
            if item.rejected:
                rejects = "; ".join(f"{r.get('option','')}({r.get('reason','')})" for r in item.rejected)
                lines.append(f"  ⚠ rejected: {rejects}")
            lines.append("")
        return "\n".join(lines)

    elif name == "memory_update":
        item_id = arguments.get("id", "")
        status = arguments.get("status", "")
        superseded_by = arguments.get("superseded_by", "")
        storage.update_status(item_id, status, superseded_by)
        return f"Updated {item_id} -> status: {status}"

    elif name == "memory_history":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 20)
        # Search including superseded items
        items = storage.list_items(status=None, limit=limit)
        # Filter by query relevance (simple keyword match for now)
        if query:
            q_lower = query.lower()
            items = [i for i in items if q_lower in i.title.lower() or q_lower in i.content.lower() or any(q_lower in t.lower() for t in i.tags)]
        if not items:
            return "No history found for this topic."
        lines = [f"Decision history ({len(items)} items):\n"]
        for item in items:
            status_mark = f" [SUPERSEDED]" if item.status == "superseded" else ""
            lines.append(f"- {item.created_at[:10]}{status_mark} {item.title}")
            if item.content:
                lines.append(f"  {item.content[:100]}")
            lines.append("")
        return "\n".join(lines)

    return f"Unknown tool: {name}"
