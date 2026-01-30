#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

console = Console()

def _mock(system: str, user: str) -> str:
    seed = abs(hash(system + "\n" + user)) % 99991
    return (
        "MOCK_MODE output\n"
        f"seed={seed}\n\n"
        "This is a placeholder response so the repo runs without an API key.\n"
        "Set MOCK_MODE=false and add OPENAI_API_KEY to generate real outputs.\n"
    )

def call_llm(system: str, user: str) -> str:
    load_dotenv()
    if os.getenv("MOCK_MODE", "true").lower() == "true":
        return _mock(system, user)

    from openai import OpenAI
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("Missing OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    client = OpenAI(api_key=key)
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.2,
    )
    return r.choices[0].message.content or ""

def read_input(path: Optional[str]) -> str:
    if path:
        return open(path, "r", encoding="utf-8").read()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    console.print("[bold]Paste input then Ctrl+D (macOS/Linux) or Ctrl+Z then Enter (Windows):[/bold]")
    return sys.stdin.read()

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Run this AI model template.")
    parser.add_argument("--in", dest="inp", default="examples/input.txt", help="Input file path")
    parser.add_argument("--out", dest="out", default="out.md", help="Output file path")
    args = parser.parse_args()

    from prompt import SYSTEM_PROMPT, USER_TEMPLATE
    raw = read_input(args.inp).strip()
    if not raw:
        console.print("[red]No input provided[/red]")
        raise SystemExit(1)

    user = USER_TEMPLATE.format(input=raw)
    console.print(Panel.fit("Running...", title="AI Model"))
    out = call_llm(SYSTEM_PROMPT, user)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out)
    console.print(Panel.fit(f"Wrote {args.out}", title="Done", border_style="green"))

if __name__ == "__main__":
    main()
