from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from .feature_extractor import WebsiteFeatures
from .templates import pick_offer, pick_opener, next_step_from_score


@dataclass
class LeadIQOutput:
    score: int
    reasons: List[str]
    recommended_offer: str
    outreach_opener: str
    next_step: str
    confidence: float
    debug: Optional[Dict] = None


def _clamp(n: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, n))


def score_lead(
    biz_name: str,
    category: str,
    town: str,
    features: WebsiteFeatures,
    notes: str = "",
    include_debug: bool = False,
) -> LeadIQOutput:
    reasons: List[str] = []
    score = 0
    confidence = 0.55

    if features.status_ok:
        score += 10
        confidence += 0.05
    else:
        score -= 20
        reasons.append("Site looks hard to access right now, which usually means leads are leaking.")
        confidence -= 0.10

    if features.has_https:
        score += 3
    else:
        reasons.append("Site is not on HTTPS, which can hurt trust and conversions.")

    # High intent signals
    if features.has_booking:
        score += 18
        reasons.append("They already mention booking or appointments, so automation can pay off fast.")
        confidence += 0.05
    else:
        score += 6
        reasons.append("No obvious booking path, which suggests a simple booking flow could increase conversions.")

    if features.has_contact_form:
        score += 12
        reasons.append("Contact form exists, so adding smart follow ups is an easy win.")
        confidence += 0.05
    else:
        score += 2
        reasons.append("No clear contact form, so lead capture can be improved.")

    if features.has_phone:
        score += 8
        reasons.append("Phone number is present, missed-call text back can recover leads.")
    else:
        score -= 3

    if features.has_email:
        score += 4

    # Trust signals
    if features.has_reviews:
        score += 8
        reasons.append("Reviews and testimonials are present, so a review funnel could scale trust.")
    else:
        score += 1
        reasons.append("Not many visible trust signals, so reviews and proof could be improved.")

    # Ops maturity signals
    if features.has_live_chat:
        score += 6
        reasons.append("Live chat hint suggests they care about leads and customer support.")
    if features.has_pricing:
        score += 4
    if features.has_locations:
        score += 4
    if features.has_careers:
        score += 4
        reasons.append("Careers or hiring signals suggest they are growing and may invest in systems.")

    # Category adjustment
    cat = (category or "").strip().lower()
    if cat in ["home services", "home_service", "home_services", "contractor", "plumber", "electrician", "hvac"]:
        score += 8
        cat_key = "home_services"
    elif cat in ["restaurant", "food", "cafe", "deli"]:
        score += 6
        cat_key = "restaurant"
    elif cat in ["gym", "fitness", "studio"]:
        score += 5
        cat_key = "gym"
    elif cat in ["dentist", "dental", "orthodontist"]:
        score += 6
        cat_key = "dentist"
    elif cat in ["retail", "store", "shop"]:
        score += 4
        cat_key = "retail"
    else:
        cat_key = "default"

    # Notes heuristics
    n = (notes or "").lower()
    if "busy" in n or "always" in n:
        score += 3
    if "no online booking" in n or "no booking" in n:
        score += 6
    if "hard to reach" in n or "never answers" in n:
        score += 5

    # Stabilize score and confidence
    score = _clamp(score)
    confidence = max(0.2, min(0.95, confidence))

    # Make reasons unique and top 5
    seen = set()
    cleaned: List[str] = []
    for r in reasons:
        if r not in seen:
            cleaned.append(r)
            seen.add(r)
    top_reasons = cleaned[:5] if cleaned else ["Looks like a solid fit for a simple lead capture and follow up system."]

    offer = pick_offer(cat_key)
    opener = pick_opener(cat_key, biz_name)
    next_step = next_step_from_score(score)

    debug = None
    if include_debug:
        debug = {
            "biz_name": biz_name,
            "category": category,
            "town": town,
            "notes": notes,
            "features": asdict(features),
        }

    return LeadIQOutput(
        score=score,
        reasons=top_reasons,
        recommended_offer=offer,
        outreach_opener=opener,
        next_step=next_step,
        confidence=round(confidence, 2),
        debug=debug,
    )
