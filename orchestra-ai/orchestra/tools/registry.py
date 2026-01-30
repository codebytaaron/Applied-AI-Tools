from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any

@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    schema: dict

class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, tuple[ToolSpec, Callable[[dict], Any]]] = {}

    def register(self, spec: ToolSpec, fn: Callable[[dict], Any]) -> None:
        if spec.name in self._tools:
            raise ValueError(f"Tool already registered: {spec.name}")
        self._tools[spec.name] = (spec, fn)

    def specs(self) -> list[ToolSpec]:
        return [v[0] for v in self._tools.values()]

    def call(self, name: str, args: dict) -> Any:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name][1](args)
