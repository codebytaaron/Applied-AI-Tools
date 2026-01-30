from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from orchestra.bootstrap import bootstrap

app = FastAPI(title="Orchestra AI", version="0.1.0")
ctx = bootstrap()

class ChatIn(BaseModel):
    session_id: str = "api"
    message: str

class ChatOut(BaseModel):
    session_id: str
    reply: str
    meta: dict

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/tools")
def tools():
    return [t.__dict__ for t in ctx.tools.specs()]

@app.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn):
    ctx.sessions.append(payload.session_id, "user", payload.message)
    resp = ctx.router.run(payload.message)
    ctx.sessions.append(payload.session_id, "assistant", resp.text)
    return ChatOut(session_id=payload.session_id, reply=resp.text, meta=resp.meta or {})
