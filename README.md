# AI Customer Message Auto-Responder

A simple web app that drafts ready-to-send replies to customer messages and flags urgency so businesses respond faster.

## ⚠️ Usage Notice

This repository is shared for visibility and reference only.

Please **do not use, copy, modify, deploy, or redistribute** this project without contacting me first.

If you are interested in using this model, adapting it, or collaborating, reach out via the link in my bio.

---

## Features

- Drafts a clean reply based on the customer message
- Classifies message type (billing, scheduling, complaint, product, other)
- Flags urgency (low, medium, high)
- Suggests follow-up questions
- Produces internal notes for next steps
- Runs locally with Ollama (no paid APIs)

---

## Tech Used

- Python
- FastAPI
- Jinja2
- Ollama (local LLM)
- HTML / CSS

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
# .venv\Scripts\activate     # Windows

pip install -r requirements.txt
cp .env.example .env
