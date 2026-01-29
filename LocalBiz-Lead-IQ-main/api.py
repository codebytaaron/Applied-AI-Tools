from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.feature_extractor import extract_features
from src.scoring_model import score_lead

app = FastAPI(title="Lead IQ", version="1.0.0")


class LeadRequest(BaseModel):
    business_name: str = Field(..., min_length=1)
    website_url: str = Field(..., min_length=3)
    category: str = "default"
    town: str = ""
    notes: str = ""
    debug: bool = False


@app.post("/score")
def score(req: LeadRequest):
    feats, meta = extract_features(req.website_url)
    out = score_lead(
        biz_name=req.business_name,
        category=req.category,
        town=req.town,
        features=feats,
        notes=req.notes,
        include_debug=req.debug,
    )
    payload = {
        "score": out.score,
        "reasons": out.reasons,
        "recommended_offer": out.recommended_offer,
        "outreach_opener": out.outreach_opener,
        "next_step": out.next_step,
        "confidence": out.confidence,
    }
    if req.debug:
        payload["debug"] = out.debug
        payload["meta"] = meta
    return payload
