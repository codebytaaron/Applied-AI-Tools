# Orchestra AI (big codebase, <100 files)

A full agent-orchestration repo you can drop into GitHub. It's an "AI app framework" with:
- **CLI** (`orchestra run`, `orchestra chat`, `orchestra eval`, `orchestra tools`)
- **FastAPI server** (`orchestra serve`) with `/chat`, `/tools`, `/health`
- **Pluggable tools** (HTTP, file ops (sandboxed), calculator, text utils)
- **Router** that chooses which sub-agent should handle a request
- **Memory**: session history + a tiny local embedding index (no external DB)
- **Caching**: prompt+params cache for cheaper dev
- **Eval harness**: run test cases and score output with rules

This is intentionally "big" but still under 100 files.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
cp .env.example .env
orchestra chat
```

## Env
Create `./.env`:
- `OPENAI_API_KEY=...`
- `OPENAI_MODEL=gpt-4.1-mini`
- `MOCK_MODE=true` (runs without API keys)

## Commands
- `orchestra chat` interactive chat (router + tools)
- `orchestra run --task tasks/sample.yaml` run a task pipeline
- `orchestra serve --port 8000` start API
- `orchestra eval --suite eval/suite.yaml` run evaluation suite
- `orchestra tools` list available tools

## Project layout
```
orchestra-ai/
  orchestra/               main package
    agents/                router + specialist agents
    tools/                 tool plugins
    memory/                chat history + tiny vector index
    llm/                   OpenAI wrapper + cache + mock
    server/                FastAPI app
    eval/                  eval harness
  tasks/                   example task pipelines
  eval/                    example evaluation suite
```

## Notes
- Tools are **sandboxed**: file tool only reads/writes inside `./data/`.
- Mock mode makes the repo runnable anywhere.
- Everything is easy to extend: add a new tool in `orchestra/tools/` or new agent in `orchestra/agents/`.
