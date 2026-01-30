from __future__ import annotations

from orchestra.agents.base import Agent
from orchestra.agents.types import AgentResponse
from orchestra.llm.client import LLMClient
from orchestra.tools.registry import ToolRegistry

def _mk(llm: LLMClient, system: str, user: str) -> str:
    r = llm.chat([
        {"role":"system","content":system},
        {"role":"user","content":user},
    ])
    return r.text

class PlannerAgent(Agent):
    name = "planner"
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm
    def run(self, query: str) -> AgentResponse:
        system = "You are a planning assistant. Produce a numbered plan with checkpoints and risk notes."
        return AgentResponse(_mk(self.llm, system, query), {"agent": self.name})

class WriterAgent(Agent):
    name = "writer"
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm
    def run(self, query: str) -> AgentResponse:
        system = "You are a writing assistant. Produce a polished, structured deliverable."
        return AgentResponse(_mk(self.llm, system, query), {"agent": self.name})

class AnalystAgent(Agent):
    name = "analyst"
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm
    def run(self, query: str) -> AgentResponse:
        system = "You are an analyst. Be precise. Show assumptions. Use bullet points and small tables when useful."
        return AgentResponse(_mk(self.llm, system, query), {"agent": self.name})

class ToolUserAgent(Agent):
    name = "tool_user"
    def __init__(self, llm: LLMClient, tools: ToolRegistry) -> None:
        self.llm = llm
        self.tools = tools

    def run(self, query: str) -> AgentResponse:
        # lightweight tool calling: model outputs JSON commands we execute
        system = (
            "You can use tools by outputting JSON with keys: tool, args. "
            "If no tool needed, output plain text. "
            "Available tools: " + ", ".join([t.name for t in self.tools.specs()])
        )
        out = _mk(self.llm, system, query)

        # If JSON, try to execute tool
        import json
        out_str = out.strip()
        if out_str.startswith("{") and out_str.endswith("}"):
            try:
                obj = json.loads(out_str)
                tool = obj.get("tool")
                args = obj.get("args", {})
                if tool:
                    res = self.tools.call(tool, args)
                    return AgentResponse(
                        f"Tool result ({tool}):\n\n```json\n{json.dumps(res, indent=2)}\n```",
                        {"agent": self.name, "tool": tool},
                    )
            except Exception:
                pass
        return AgentResponse(out, {"agent": self.name})
