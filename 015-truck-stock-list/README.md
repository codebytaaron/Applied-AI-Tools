# Truck Stock List

Industry template: **Blue‑Collar Services**

## What it does
Defines truck stock by trade.

## Run
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py --in examples/input.txt --out out.md
```

## Customize
Edit `prompt.py` to adjust rules, tone, and outputs.

## Notes
- Runs in MOCK_MODE by default.
- Set `MOCK_MODE=false` with an API key for real outputs.
