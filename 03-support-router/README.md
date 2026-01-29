# Support Ticket Router

Classifies support tickets and suggests replies, tags, and escalation paths.

## What it does
Given a ticket, outputs category, severity, sentiment, suggested macro reply, and escalation/ownership guidance.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# set MOCK_MODE=true to run without an API key
python main.py --in examples/input.txt --out out.md
```

## Inputs
- Put raw text in `examples/input.txt` (or pipe stdin).

## Output
- Writes a structured result to `out.md`.

## Customize
- Edit `prompt.py` to match your business rules, tone, and tools.
- Add examples to `examples/` and iterate.

## Notes
- This is a lightweight template, meant to be dropped into a repo and extended.
