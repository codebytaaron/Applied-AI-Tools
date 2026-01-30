from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass
class Message:
    role: str
    content: str

class SessionStore:
    def __init__(self, data_dir: str) -> None:
        self.root = Path(data_dir) / "sessions"
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, session_id: str) -> Path:
        return self.root / f"{session_id}.json"

    def load(self, session_id: str) -> list[Message]:
        p = self.path(session_id)
        if not p.exists():
            return []
        raw = json.loads(p.read_text(encoding="utf-8"))
        return [Message(**m) for m in raw]

    def save(self, session_id: str, messages: list[Message]) -> None:
        p = self.path(session_id)
        p.write_text(json.dumps([m.__dict__ for m in messages], ensure_ascii=False, indent=2), encoding="utf-8")

    def append(self, session_id: str, role: str, content: str) -> None:
        msgs = self.load(session_id)
        msgs.append(Message(role=role, content=content))
        self.save(session_id, msgs)
