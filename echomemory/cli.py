"""CLI interface for EchoMemory"""
import sys
import json
import argparse
from .storage import Storage
from .models import KnowledgeItem, KNOWLEDGE_TYPES
from .server import run_server


def cmd_add(args, storage):
    """Add a knowledge item"""
    rejected = []
    if args.rejected:
        for r in args.rejected:
            parts = r.split(":", 1)
            rejected.append({"option": parts[0].strip(), "reason": parts[1].strip() if len(parts) > 1 else ""})

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    source = {"agent": "cli", "device": args.device or ""}

    item = KnowledgeItem(
        type=args.type,
        title=args.title,
        content=args.content or "",
        context=args.context or "",
        rejected=rejected,
        tags=tags,
        source=source,
        confidence=args.confidence,
    )
    item_id = storage.add(item)
    print(f"Added: {item_id}")
    print(f"  [{item.type}] {item.title}")
    if tags:
        print(f"  tags: {', '.join(tags)}")


def cmd_search(args, storage):
    """Search knowledge"""
    items = storage.search(args.query, limit=args.limit)
    if not items:
        print("No results found.")
        return
    print(f"Found {len(items)} results:\n")
    for item in items:
        print(f"  {item.summary()}")
        if item.content:
            preview = item.content[:100] + ("..." if len(item.content) > 100 else "")
            print(f"    {preview}")
        print()


def cmd_list(args, storage):
    """List knowledge items"""
    items = storage.list_items(
        type_filter=args.type,
        tag_filter=args.tag,
        status=args.status,
        limit=args.limit,
        days=args.days,
    )
    if not items:
        print("No items found.")
        return
    print(f"Showing {len(items)} items:\n")
    for item in items:
        tags_str = ", ".join(item.tags) if item.tags else ""
        print(f"  {item.id} [{item.type}] {item.title}")
        if tags_str:
            print(f"    tags: {tags_str}")
        if item.rejected:
            rejects = "; ".join(f"{r.get('option','')}({r.get('reason','')})" for r in item.rejected)
            print(f"    rejected: {rejects}")
        print()


def cmd_inject(args, storage):
    """Get context for injection into agent conversation"""
    if args.query:
        items = storage.search(args.query, limit=args.limit)
    else:
        items = storage.list_items(limit=args.limit)

    if not items:
        print("No relevant knowledge found.")
        return

    lines = ["## EchoMemory Context", ""]
    for item in items:
        lines.append(f"- {item.summary()}")
        if item.content:
            lines.append(f"  {item.content[:200]}")
        if item.rejected:
            rejects = "; ".join(f"{r.get('option','')}({r.get('reason','')})" for r in item.rejected)
            lines.append(f"  rejected: {rejects}")
        lines.append("")

    output = "\n".join(lines)

    if args.copy:
        try:
            import subprocess
            process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            process.communicate(output.encode())
            print(f"Copied {len(items)} items to clipboard.")
        except:
            print(output)
    else:
        print(output)


def cmd_export(args, storage):
    """Export knowledge as Markdown"""
    items = storage.list_items(
        type_filter=args.type,
        tag_filter=args.tag,
        limit=args.limit,
        days=args.days,
    )
    if not items:
        print("No items to export.")
        return

    lines = [f"# EchoMemory Export ({len(items)} items)", ""]
    current_type = ""
    for item in items:
        if item.type != current_type:
            current_type = item.type
            lines.append(f"\n## {current_type.title()}\n")
        lines.append(f"### {item.title}")
        lines.append(f"*{item.created_at[:10]}* | tags: {', '.join(item.tags)}")
        lines.append("")
        if item.content:
            lines.append(item.content)
            lines.append("")
        if item.rejected:
            lines.append("**Rejected alternatives:**")
            for r in item.rejected:
                lines.append(f"- {r.get('option', '')}: {r.get('reason', '')}")
            lines.append("")

    output = "\n".join(lines)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Exported to {args.output}")
    else:
        print(output)


def cmd_stats(args, storage):
    """Show statistics"""
    stats = storage.stats()
    print(f"EchoMemory Stats")
    print(f"  Database: {stats['db_path']}")
    print(f"  Total items: {stats['total']}")
    print(f"  Active: {stats['active']}")
    print(f"  By type:")
    for t, c in stats.get("by_type", {}).items():
        print(f"    {t}: {c}")
    print()
    tags = storage.get_tags()
    if tags:
        print(f"  Top tags:")
        for tag, count in tags[:10]:
            print(f"    {tag}: {count}")


def cmd_serve(args, storage):
    """Start the REST API server"""
    run_server(port=args.port, token=args.token, db_path=storage.db_path)


def main():
    parser = argparse.ArgumentParser(prog="echomemory", description="Shared memory layer for AI Agents")
    parser.add_argument("--db", help="Database path", default=None)
    subparsers = parser.add_subparsers(dest="command")

    # add
    p_add = subparsers.add_parser("add", help="Add a knowledge item")
    p_add.add_argument("--type", "-t", choices=KNOWLEDGE_TYPES, default="insight", help="Knowledge type")
    p_add.add_argument("--title", required=True, help="Title")
    p_add.add_argument("--content", "-c", help="Content/description")
    p_add.add_argument("--context", help="Context when this knowledge was created")
    p_add.add_argument("--rejected", "-r", nargs="*", help="Rejected alternatives (format: 'option:reason')")
    p_add.add_argument("--tags", help="Comma-separated tags")
    p_add.add_argument("--confidence", type=float, default=0.8)
    p_add.add_argument("--device", help="Device identifier")

    # search
    p_search = subparsers.add_parser("search", help="Search knowledge")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", "-l", type=int, default=10)

    # list
    p_list = subparsers.add_parser("list", help="List knowledge items")
    p_list.add_argument("--type", "-t", choices=KNOWLEDGE_TYPES)
    p_list.add_argument("--tag", help="Filter by tag")
    p_list.add_argument("--status", default="active")
    p_list.add_argument("--limit", "-l", type=int, default=20)
    p_list.add_argument("--days", "-d", type=int, help="Only show items from last N days")

    # inject
    p_inject = subparsers.add_parser("inject", help="Get context for agent injection")
    p_inject.add_argument("--query", "-q", help="Search query for relevant context")
    p_inject.add_argument("--limit", "-l", type=int, default=10)
    p_inject.add_argument("--copy", action="store_true", help="Copy to clipboard")

    # export
    p_export = subparsers.add_parser("export", help="Export as Markdown")
    p_export.add_argument("--type", "-t", choices=KNOWLEDGE_TYPES)
    p_export.add_argument("--tag", help="Filter by tag")
    p_export.add_argument("--limit", "-l", type=int, default=100)
    p_export.add_argument("--days", "-d", type=int)
    p_export.add_argument("--output", "-o", help="Output file path")

    # stats
    subparsers.add_parser("stats", help="Show statistics")

    # serve
    p_serve = subparsers.add_parser("serve", help="Start REST API server")
    p_serve.add_argument("--port", "-p", type=int, default=9090)
    p_serve.add_argument("--token", help="Auth token (or set ECHOMEMORY_TOKEN env)")

    # mcp
    subparsers.add_parser("mcp", help="Run as MCP server (stdio)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    storage = Storage(args.db)

    commands = {
        "add": cmd_add,
        "search": cmd_search,
        "list": cmd_list,
        "inject": cmd_inject,
        "export": cmd_export,
        "stats": cmd_stats,
        "serve": cmd_serve,
        "mcp": lambda a, s: _run_mcp(a, s),
    }

    if args.command in commands:
        commands[args.command](args, storage)
    else:
        parser.print_help()


def _run_mcp(args, storage):
    from .mcp_server import run_mcp
    run_mcp(storage)


if __name__ == "__main__":
    main()
