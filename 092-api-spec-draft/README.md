# API Spec Draft

Drafts API endpoints for a feature.

## What it does
Given feature needs, output endpoints, request/response, errors.

## Run
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py --in examples/input.txt --out out.md
```

## Customize
Edit `prompt.py` to change rules, output format, and style.

## Notes
- Defaults to MOCK_MODE so it runs with no API key.
- Set `MOCK_MODE=false` and add `OPENAI_API_KEY` for real outputs.
