from __future__ import annotations

import json
import uuid
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from orchestra.bootstrap import bootstrap
from orchestra.pipeline import PipelineRunner
from orchestra.eval.harness import Evaluator

app = typer.Typer(add_completion=False, help="Orchestra AI - modular agent framework")
console = Console()

@app.command()
def tools():
    """List available tools."""
    ctx = bootstrap()
    t = Table(title="Tools")
    t.add_column("name"); t.add_column("description")
    for s in ctx.tools.specs():
        t.add_row(s.name, s.description)
    console.print(t)

@app.command()
def chat(session: str = typer.Option("chat", help="Session id")):
    """Interactive chat (router + tools)."""
    ctx = bootstrap()
    console.print(Panel.fit("Type /exit to quit. Type /new to start a new session.", title="Orchestra"))
    sid = session
    while True:
        msg = console.input("[bold cyan]you[/bold cyan]> ").strip()
        if not msg:
            continue
        if msg == "/exit":
            break
        if msg == "/new":
            sid = f"chat-{uuid.uuid4().hex[:8]}"
            console.print(f"[green]new session:[/green] {sid}")
            continue

        ctx.sessions.append(sid, "user", msg)
        resp = ctx.router.run(msg)
        ctx.sessions.append(sid, "assistant", resp.text)
        meta = resp.meta or {}
        console.print(Panel(resp.text, title=f"assistant ({meta.get('agent','?')})", subtitle=meta.get("route_reason","")))

@app.command()
def run(task: str = typer.Option(..., help="YAML pipeline file"), session: str = "pipeline"):
    """Run a multi-step YAML pipeline."""
    ctx = bootstrap()
    runner = PipelineRunner(ctx.router, ctx.sessions)
    results = runner.run_file(task, session_id=session)
    for r in results:
        console.print(Panel(r.output, title=f"step: {r.name}"))

@app.command()
def eval(suite: str = typer.Option(..., help="Eval suite YAML"), show_failures: bool = True):
    """Run evaluation suite."""
    ctx = bootstrap()
    ev = Evaluator(ctx.router)
    results = ev.run_suite(suite)

    passed = sum(1 for r in results if r.passed)
    t = Table(title=f"Eval results: {passed}/{len(results)} passed")
    t.add_column("id"); t.add_column("passed"); t.add_column("score"); t.add_column("notes")
    for r in results:
        t.add_row(r.id, "yes" if r.passed else "no", f"{r.score:.2f}", r.notes)
    console.print(t)

    if show_failures:
        for r in results:
            if not r.passed:
                console.print(Panel(r.output, title=f"FAIL {r.id}", subtitle=r.notes))

@app.command()
def serve(port: int = 8000):
    """Start FastAPI server."""
    import uvicorn
    uvicorn.run("orchestra.server.app:app", host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    app()
