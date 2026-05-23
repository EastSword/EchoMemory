"""SQLite storage layer for EchoMemory"""
import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from .models import KnowledgeItem, Relation

DEFAULT_DB_PATH = os.environ.get("ECHOMEMORY_DB", str(Path.home() / ".echomemory" / "memory.db"))


class Storage:
    def __init__(self, db_path=None):
        self.db_path = db_path or DEFAULT_DB_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = self._conn()
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS knowledge (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL DEFAULT '',
            context TEXT DEFAULT '',
            rejected TEXT DEFAULT '[]',
            tags TEXT DEFAULT '[]',
            source TEXT DEFAULT '{}',
            confidence REAL DEFAULT 0.8,
            status TEXT DEFAULT 'active',
            superseded_by TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS relations (
            from_id TEXT NOT NULL,
            to_id TEXT NOT NULL,
            type TEXT NOT NULL,
            note TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            PRIMARY KEY (from_id, to_id, type)
        )""")
        # Full-text search index
        c.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
            id, title, content, context, tags,
            content=knowledge, content_rowid=rowid
        )""")
        # Triggers to keep FTS in sync
        c.execute("""CREATE TRIGGER IF NOT EXISTS knowledge_ai AFTER INSERT ON knowledge BEGIN
            INSERT INTO knowledge_fts(id, title, content, context, tags)
            VALUES (new.id, new.title, new.content, new.context, new.tags);
        END""")
        c.execute("""CREATE TRIGGER IF NOT EXISTS knowledge_ad AFTER DELETE ON knowledge BEGIN
            INSERT INTO knowledge_fts(knowledge_fts, id, title, content, context, tags)
            VALUES ('delete', old.id, old.title, old.content, old.context, old.tags);
        END""")
        c.execute("""CREATE TRIGGER IF NOT EXISTS knowledge_au AFTER UPDATE ON knowledge BEGIN
            INSERT INTO knowledge_fts(knowledge_fts, id, title, content, context, tags)
            VALUES ('delete', old.id, old.title, old.content, old.context, old.tags);
            INSERT INTO knowledge_fts(id, title, content, context, tags)
            VALUES (new.id, new.title, new.content, new.context, new.tags);
        END""")
        conn.commit()
        conn.close()

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def add(self, item: KnowledgeItem) -> str:
        conn = self._conn()
        d = item.to_dict()
        conn.execute("""INSERT OR REPLACE INTO knowledge 
            (id, type, title, content, context, rejected, tags, source, confidence, status, superseded_by, created_at, updated_at)
            VALUES (:id, :type, :title, :content, :context, :rejected, :tags, :source, :confidence, :status, :superseded_by, :created_at, :updated_at)""", d)
        conn.commit()
        conn.close()
        return item.id

    def get(self, item_id: str) -> KnowledgeItem:
        conn = self._conn()
        row = conn.execute("SELECT * FROM knowledge WHERE id = ?", (item_id,)).fetchone()
        conn.close()
        if row:
            return KnowledgeItem.from_dict(dict(row))
        return None

    def search(self, query: str, limit: int = 20) -> list:
        """Full-text search"""
        conn = self._conn()
        # FTS5 search
        rows = conn.execute("""
            SELECT k.* FROM knowledge k
            JOIN knowledge_fts f ON k.id = f.id
            WHERE knowledge_fts MATCH ?
            AND k.status = 'active'
            ORDER BY rank
            LIMIT ?
        """, (query, limit)).fetchall()
        conn.close()
        return [KnowledgeItem.from_dict(dict(r)) for r in rows]

    def list_items(self, type_filter=None, tag_filter=None, status="active", limit=50, days=None) -> list:
        """List knowledge items with filters"""
        conn = self._conn()
        query = "SELECT * FROM knowledge WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if type_filter:
            query += " AND type = ?"
            params.append(type_filter)
        if tag_filter:
            query += " AND tags LIKE ?"
            params.append(f"%{tag_filter}%")
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            query += " AND created_at >= ?"
            params.append(cutoff)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [KnowledgeItem.from_dict(dict(r)) for r in rows]

    def update_status(self, item_id: str, status: str, superseded_by: str = "") -> bool:
        conn = self._conn()
        conn.execute("UPDATE knowledge SET status = ?, superseded_by = ?, updated_at = ? WHERE id = ?",
                     (status, superseded_by, datetime.now().isoformat(), item_id))
        conn.commit()
        conn.close()
        return True

    def delete(self, item_id: str) -> bool:
        conn = self._conn()
        conn.execute("DELETE FROM knowledge WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        return True

    def add_relation(self, rel: Relation) -> bool:
        conn = self._conn()
        conn.execute("""INSERT OR REPLACE INTO relations (from_id, to_id, type, note, created_at)
            VALUES (?, ?, ?, ?, ?)""", (rel.from_id, rel.to_id, rel.type, rel.note, rel.created_at))
        conn.commit()
        conn.close()
        return True

    def get_relations(self, item_id: str) -> list:
        conn = self._conn()
        rows = conn.execute("SELECT * FROM relations WHERE from_id = ? OR to_id = ?", (item_id, item_id)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_tags(self) -> list:
        """Get all tags with counts"""
        conn = self._conn()
        rows = conn.execute("SELECT tags FROM knowledge WHERE status = 'active'").fetchall()
        conn.close()
        tag_counts = {}
        for row in rows:
            try:
                tags = json.loads(row["tags"])
                for t in tags:
                    tag_counts[t] = tag_counts.get(t, 0) + 1
            except:
                pass
        return sorted(tag_counts.items(), key=lambda x: -x[1])

    def stats(self) -> dict:
        conn = self._conn()
        total = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM knowledge WHERE status = 'active'").fetchone()[0]
        by_type = {}
        for row in conn.execute("SELECT type, COUNT(*) as cnt FROM knowledge WHERE status = 'active' GROUP BY type").fetchall():
            by_type[row["type"]] = row["cnt"]
        conn.close()
        return {"total": total, "active": active, "by_type": by_type, "db_path": self.db_path}
