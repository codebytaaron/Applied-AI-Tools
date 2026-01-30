from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

def _key(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()

class DiskCache:
    def __init__(self, cache_dir: str) -> None:
        self.root = Path(cache_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def get(self, payload: dict[str, Any]) -> str | None:
        k = _key(payload)
        p = self.root / f"{k}.json"
        if not p.exists():
            return None
        return p.read_text(encoding="utf-8")

    def set(self, payload: dict[str, Any], value: str) -> None:
        k = _key(payload)
        p = self.root / f"{k}.json"
        p.write_text(value, encoding="utf-8")
