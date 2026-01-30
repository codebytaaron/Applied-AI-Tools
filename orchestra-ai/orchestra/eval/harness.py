from __future__ import annotations

import re
import yaml
from dataclasses import dataclass
from typing import Any, Callable

from orchestra.agents.router import Router

@dataclass
class CaseResult:
    id: str
    passed: bool
    score: float
    notes: str
    output: str

def _score_rules(output: str, rules: list[dict[str, Any]]) -> tuple[float, str]:
    score = 1.0
    notes = []
    for r in rules:
        kind = r.get("type")
        if kind == "contains":
            s = r.get("text","")
            if s not in output:
                score *= float(r.get("penalty", 0.7))
                notes.append(f"missing contains: {s}")
        elif kind == "regex":
            pat = r.get("pattern","")
            if not re.search(pat, output, re.IGNORECASE | re.MULTILINE):
                score *= float(r.get("penalty", 0.7))
                notes.append(f"missing regex: {pat}")
        elif kind == "max_words":
            mw = int(r.get("n", 300))
            if len(output.split()) > mw:
                score *= float(r.get("penalty", 0.8))
                notes.append(f"too long: >{mw} words")
    return score, "; ".join(notes)

class Evaluator:
    def __init__(self, router: Router) -> None:
        self.router = router

    def run_suite(self, suite_path: str) -> list[CaseResult]:
        suite = yaml.safe_load(open(suite_path, "r", encoding="utf-8"))
        cases = suite.get("cases", [])
        out: list[CaseResult] = []
        for c in cases:
            cid = str(c.get("id"))
            prompt = str(c.get("prompt",""))
            rules = c.get("rules", [])
            resp = self.router.run(prompt).text
            score, notes = _score_rules(resp, rules)
            passed = score >= float(c.get("pass_score", 0.75))
            out.append(CaseResult(id=cid, passed=passed, score=score, notes=notes, output=resp))
        return out
