import json
import os
from dataclasses import dataclass
from typing import Any, Dict

import httpx

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


@dataclass
class ReplyRequest:
    business_name: str
    brand_voice: str  # professional | friendly | luxury | short
    policy_notes: str
    customer_message: str


def _system_prompt() -> str:
    return (
        "You are an assistant that drafts customer support replies for businesses. "
        "You must be clear, polite, and helpful. "
        "You must NOT promise refunds, discounts, or policy exceptions unless provided in policy notes. "
        "Return valid JSON only."
    )


def _voice_style(voice: str) -> str:
    v = (voice or "professional").lower().strip()
    if v == "friendly":
        return "Tone: friendly, warm, upbeat. Short sentences."
    if v == "luxury":
        return "Tone: premium, calm, confident, concise. Avoid emojis."
    if v == "short":
        return "Tone: very concise. Minimal words but still polite."
    return "Tone: professional, clear, direct, helpful."


def _user_prompt(req: ReplyRequest) -> str:
    return f"""
BUSINESS: {req.business_name}
BRAND VOICE: {req.brand_voice}
{_voice_style(req.brand_voice)}

POLICY NOTES (authoritative, may be blank):
{req.policy_notes}

CUSTOMER MESSAGE:
{req.customer_message}

Return VALID JSON matching:
{{
  "category": "billing | scheduling | complaint | product | other",
  "urgency": "low | medium | high",
  "suggested_reply": "string",
  "follow_up_questions": ["string", "string"],
  "internal_notes": ["string", "string"]
}}

Rules:
- Suggested reply must be ready to send.
- Ask only necessary questions.
- Internal notes are for the business (next steps, risk, what to check).
""".strip()


async def _call_ollama(system: str, user: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"temperature": 0.2},
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{OLLAMA_HOST}/api/chat", json=payload)
        r.raise_for_status()
        return r.json()["message"]["content"]


def _safe_json(text: str) -> Dict[str, Any]:
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        lines = cleaned.splitlines()
        if lines and lines[0].lower().strip() in {"json", "javascript"}:
            cleaned = "\n".join(lines[1:]).strip()
    return json.loads(cleaned)


async def generate_reply(req: ReplyRequest) -> Dict[str, Any]:
    raw = await _call_ollama(_system_prompt(), _user_prompt(req))
    try:
        return _safe_json(raw)
    except Exception:
        return {
            "category": "other",
            "urgency": "medium",
            "suggested_reply": "Could you share a bit more detail so I can help you correctly?",
            "follow_up_questions": ["What order or booking number is this about?", "What outcome are you hoping for?"],
            "internal_notes": ["Model returned non-JSON output.", "Review raw output in logs if needed."],
        }
