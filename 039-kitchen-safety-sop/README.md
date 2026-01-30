# Kitchen Safety SOP

Industry template: **Restaurant**

## What it does
Creates safety SOPs and incident reporting steps.

## Run
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py --in examples/input.txt --out out.md
```

## Customize
Edit `prompt.py` to change output format, constraints, and tone.

## Notes
- Defaults to MOCK_MODE so it runs with no API key.
- Set `MOCK_MODE=false` and add `OPENAI_API_KEY` for real outputs.
