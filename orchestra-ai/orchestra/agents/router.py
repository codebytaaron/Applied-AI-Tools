from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from orchestra.agents.types import AgentResponse
from orchestra.llm.client import LLMClient
from orchestra.agents.specialists import PlannerAgent, WriterAgent, AnalystAgent, ToolUserAgent
from orchestra.tools.registry import ToolRegistry

@dataclass
class RouteDecision:
    agent: str
    reason: str

class Router:
    def __init__(self, llm: LLMClient, tools: ToolRegistry) -> None:
        self.llm = llm
        self.agents = {
            "planner": PlannerAgent(llm),
            "writer": WriterAgent(llm),
            "analyst": AnalystAgent(llm),
            "tool_user": ToolUserAgent(llm, tools),
        }

    def decide(self, query: str) -> RouteDecision:
        system = (
            "Route the user request to one agent: planner, writer, analyst, tool_user. "
            "Return STRICT JSON: {"agent":"...","reason":"..."}. "
            "Use tool_user if math, file operations, or fetching a url is needed."
        )
        r = self.llm.chat([
            {"role":"system","content":system},
            {"role":"user","content":query},
        ], temperature=0.0)
        txt = r.text.strip()
        try:
            obj = json.loads(txt)
            agent = obj.get("agent", "writer")
            if agent not in self.agents:
                agent = "writer"
            return RouteDecision(agent=agent, reason=str(obj.get("reason","")))
        except Exception:
            # fallback heuristic
            q = query.lower()
            if any(k in q for k in ["plan","timeline","steps","roadmap"]):
                return RouteDecision("planner","heuristic: planning keywords")
            if any(k in q for k in ["analyze","compare","pros","cons","estimate"]):
                return RouteDecision("analyst","heuristic: analysis keywords")
            if any(k in q for k in ["http","url","calculate","calc","read file","write file"]):
                return RouteDecision("tool_user","heuristic: tool keywords")
            return RouteDecision("writer","heuristic fallback")

    def run(self, query: str) -> AgentResponse:
        d = self.decide(query)
        resp = self.agents[d.agent].run(query)
        resp.meta = (resp.meta or {}) | {"route_reason": d.reason}
        return resp
