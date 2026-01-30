from __future__ import annotations

import yaml
from dataclasses import dataclass
from typing import Any

from orchestra.agents.router import Router
from orchestra.memory.session import SessionStore

@dataclass
class StepResult:
    name: str
    output: str

class PipelineRunner:
    def __init__(self, router: Router, sessions: SessionStore) -> None:
        self.router = router
        self.sessions = sessions

    def run_file(self, task_file: str, session_id: str = "pipeline") -> list[StepResult]:
        doc = yaml.safe_load(open(task_file, "r", encoding="utf-8"))
        steps = doc.get("steps", [])
        results: list[StepResult] = []
        for s in steps:
            name = s.get("name","step")
            prompt = s.get("prompt","")
            # allow templating from previous outputs
            for r in results:
                prompt = prompt.replace(f"{{{{{r.name}}}}}", r.output)
            self.sessions.append(session_id, "user", f"[{name}] {prompt}")
            out = self.router.run(prompt).text
            self.sessions.append(session_id, "assistant", out)
            results.append(StepResult(name=name, output=out))
        return results
