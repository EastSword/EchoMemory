"""Data models for EchoMemory"""
import json
import hashlib
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

KNOWLEDGE_TYPES = ("decision", "lesson", "process", "insight", "contact", "reference", "rule")
RELATION_TYPES = ("supersedes", "conflicts_with", "extends", "related_to", "derived_from")
STATUS_VALUES = ("active", "superseded", "archived")


@dataclass
class KnowledgeItem:
    id: str = ""
    type: str = "insight"
    title: str = ""
    content: str = ""
    context: str = ""
    rejected: list = field(default_factory=list)  # [{"option": "...", "reason": "..."}]
    tags: list = field(default_factory=list)
    source: dict = field(default_factory=dict)  # {"agent": "...", "device": "...", "session": "..."}
    confidence: float = 0.8
    status: str = "active"
    superseded_by: str = ""
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at

    def _generate_id(self):
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        h = hashlib.md5((self.title + self.content + ts).encode()).hexdigest()[:6]
        return f"km_{ts}_{h}"

    def to_dict(self):
        d = asdict(self)
        d["rejected"] = json.dumps(d["rejected"], ensure_ascii=False) if isinstance(d["rejected"], list) else d["rejected"]
        d["tags"] = json.dumps(d["tags"], ensure_ascii=False) if isinstance(d["tags"], list) else d["tags"]
        d["source"] = json.dumps(d["source"], ensure_ascii=False) if isinstance(d["source"], dict) else d["source"]
        return d

    @classmethod
    def from_dict(cls, d):
        d = dict(d)
        if isinstance(d.get("rejected"), str):
            try:
                d["rejected"] = json.loads(d["rejected"])
            except:
                d["rejected"] = []
        if isinstance(d.get("tags"), str):
            try:
                d["tags"] = json.loads(d["tags"])
            except:
                d["tags"] = []
        if isinstance(d.get("source"), str):
            try:
                d["source"] = json.loads(d["source"])
            except:
                d["source"] = {}
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def to_json(self):
        d = asdict(self)
        return d

    def summary(self):
        """One-line summary for injection"""
        status_mark = "" if self.status == "active" else f" [{self.status}]"
        return f"[{self.type}]{status_mark} {self.title} ({self.created_at[:10]})"


@dataclass
class Relation:
    from_id: str = ""
    to_id: str = ""
    type: str = "related_to"
    note: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
