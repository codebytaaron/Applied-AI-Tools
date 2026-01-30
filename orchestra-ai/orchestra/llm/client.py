from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Iterable

from orchestra.config import Settings
from orchestra.llm.cache import DiskCache

@dataclass
class LLMResult:
    text: str
    cached: bool

def _mock_text(messages: list[dict[str, str]]) -> str:
    # deterministic-ish mock
    joined = "\n".join([f"{m['role']}: {m['content']}" for m in messages])[:2000]
    h = abs(hash(joined)) % 99991
    return f"""MOCK_MODE RESPONSE
seed={h}

I can't call a real model right now because MOCK_MODE=true.
I received this input (truncated):
{joined}
"""

class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.cache = DiskCache(settings.cache_dir)

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.2) -> LLMResult:
        payload: dict[str, Any] = {
            "model": self.settings.model,
            "messages": messages,
            "temperature": temperature,
        }
        cached = self.cache.get(payload)
        if cached is not None:
            return LLMResult(text=cached, cached=True)

        if self.settings.mock_mode:
            out = _mock_text(messages)
            self.cache.set(payload, out)
            return LLMResult(text=out, cached=False)

        from openai import OpenAI

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("Missing OPENAI_API_KEY. Set it in .env or environment variables.")

        client = OpenAI(api_key=key)
        r = client.chat.completions.create(
            model=self.settings.model,
            messages=messages,
            temperature=temperature,
        )
        out = r.choices[0].message.content or ""
        self.cache.set(payload, out)
        return LLMResult(text=out, cached=False)
