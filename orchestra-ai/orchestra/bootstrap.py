from __future__ import annotations

from dataclasses import dataclass

from orchestra.config import load_settings
from orchestra.llm.client import LLMClient
from orchestra.tools.registry import ToolRegistry
from orchestra.tools.builtins import install_builtin_tools
from orchestra.agents.router import Router
from orchestra.memory.session import SessionStore

@dataclass
class AppContext:
    settings: object
    llm: LLMClient
    tools: ToolRegistry
    router: Router
    sessions: SessionStore

def bootstrap() -> AppContext:
    settings = load_settings()
    llm = LLMClient(settings)
    sessions = SessionStore(settings.data_dir)
    tools = ToolRegistry()
    install_builtin_tools(tools, settings.data_dir)
    router = Router(llm, tools)
    return AppContext(settings=settings, llm=llm, tools=tools, router=router, sessions=sessions)
