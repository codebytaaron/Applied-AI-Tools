from __future__ import annotations

"""Reporting utilities.

This module helps turn runs into consistent markdown reports:
- sections
- tables
- code blocks
- summary footers

It's not required to use, but makes outputs presentable for GitHub.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

@dataclass
class ReportSection:
    title: str
    body: str

def md_table(headers: list[str], rows: list[list[str]]) -> str:
    h = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    out = [h, sep]
    for r in rows:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)

def code_block(lang: str, code: str) -> str:
    return f"```{lang}\n{code}\n```"

def report(title: str, sections: list[ReportSection], meta: dict[str, Any] | None = None) -> str:
    meta = meta or {}
    ts = datetime.utcnow().isoformat() + "Z"
    lines = [f"# {title}", "", f"_Generated: {ts}_", ""]
    if meta:
        lines.append("## Metadata")
        lines.append(md_table(["key","value"], [[k, str(v)] for k, v in meta.items()]))
        lines.append("")
    for s in sections:
        lines.append(f"## {s.title}")
        lines.append(s.body.strip())
        lines.append("")
    lines.append("---")
    lines.append("Orchestra AI report")
    return "\n".join(lines)
