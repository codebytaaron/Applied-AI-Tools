from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

def _tokenize(text: str) -> list[str]:
    text = text.lower()
    out = []
    cur = []
    for ch in text:
        if ch.isalnum():
            cur.append(ch)
        else:
            if cur:
                out.append("".join(cur))
                cur = []
    if cur:
        out.append("".join(cur))
    return out

def _tf(text: str) -> dict[str, float]:
    toks = _tokenize(text)
    d: dict[str, float] = {}
    for t in toks:
        d[t] = d.get(t, 0.0) + 1.0
    if not toks:
        return d
    inv = 1.0 / len(toks)
    for k in list(d.keys()):
        d[k] *= inv
    return d

def _cos(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = 0.0
    for k, va in a.items():
        vb = b.get(k)
        if vb is not None:
            dot += va * vb
    na = math.sqrt(sum(v*v for v in a.values()))
    nb = math.sqrt(sum(v*v for v in b.values()))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)

@dataclass
class MemoryItem:
    id: str
    text: str
    meta: dict

class TinyVectorIndex:
    """A tiny TF-based index (no external deps). Good enough for demos and small apps."""
    def __init__(self) -> None:
        self.items: list[MemoryItem] = []
        self.vecs: list[dict[str, float]] = []

    def add(self, item: MemoryItem) -> None:
        self.items.append(item)
        self.vecs.append(_tf(item.text))

    def search(self, query: str, k: int = 5) -> list[tuple[MemoryItem, float]]:
        qv = _tf(query)
        scored = [(self.items[i], _cos(qv, self.vecs[i])) for i in range(len(self.items))]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s in scored[:k] if s[1] > 0.0]
