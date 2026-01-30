from __future__ import annotations

from abc import ABC, abstractmethod
from orchestra.agents.types import AgentResponse

class Agent(ABC):
    name: str = "agent"

    @abstractmethod
    def run(self, query: str) -> AgentResponse:
        raise NotImplementedError
