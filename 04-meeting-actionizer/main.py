#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel

console = Console()

# ---------- LLM Adapter ----------
def _mock_response(system: str, user: str) -> str:
    # Deterministic "good enough" placeholder so the project runs with no key.
    # Swap MOCK_MODE=false and add OPENAI_API_KEY to use a real model.
    seed = abs(hash(system + "\n" + user)) % 99991
    return (
        "MOCK_MODE response\n"
        f"seed={seed}\n\n"
        "Summary:\n"
        "- Parsed your input and generated a structured draft.\n\n"
        "Suggested next actions:\n"
        "1) Validate assumptions with a human.\n"
        "2) Plug into your workflow tooling (email/CRM/docs).\n"
        "3) Add domain rules + examples to improve accuracy.\n"
    )

def call_llm(system: str, user: str) -> str:
    load_dotenv()
    mock = os.getenv("MOCK_MODE", "false").lower() == "true"
    if mock:
        return _mock_response(system, user)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Set it in .env or environment.")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}") from e

# ---------- I/O ----------
def read_input(path: Optional[str]) -> str:
    if path:
        return open(path, "r", encoding="utf-8").read()
    # stdin or interactive
    if not sys.stdin.isatty():
        return sys.stdin.read()
    console.print("[bold]Paste input, then press Ctrl+D (macOS/Linux) or Ctrl+Z then Enter (Windows):[/bold]")
    return sys.stdin.read()

def write_output(text: str, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

# ---------- CLI ----------
def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Run this AI workflow model.")
    parser.add_argument("--in", dest="inp", default=None, help="Input file path (optional). If omitted, uses stdin.")
    parser.add_argument("--out", dest="out", default="out.md", help="Output path (default: out.md)")
    args = parser.parse_args()

    from prompt import SYSTEM_PROMPT, USER_INSTRUCTIONS

    raw = read_input(args.inp).strip()
    if not raw:
        console.print("[red]No input provided.[/red]")
        sys.exit(1)

    user = USER_INSTRUCTIONS.format(input=raw)
    console.print(Panel.fit("Running...", title="AI Model", border_style="cyan"))
    result = call_llm(SYSTEM_PROMPT, user)
    write_output(result, args.out)
    console.print(Panel.fit(f"Wrote: {args.out}", title="Done", border_style="green"))

if __name__ == "__main__":
    main()
