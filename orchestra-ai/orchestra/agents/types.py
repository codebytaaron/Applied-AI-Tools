from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass
class AgentResponse:
    text: str
    meta: dict[str, Any] | None = None
