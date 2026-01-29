from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


OFFER_ANGLES: Dict[str, str] = {
    "restaurant": "Online ordering plus missed-call text back so you stop losing hungry customers",
    "home_services": "Quote capture plus auto follow up so estimates turn into booked jobs",
    "gym": "Trial signup plus automated nurture so leads convert into memberships",
    "dentist": "Appointment request plus reminder flow to reduce no shows",
    "retail": "Local promos plus review funnel to boost foot traffic and trust",
    "default": "Lead capture plus automated follow up to turn interest into bookings",
}

OPENERS: Dict[str, str] = {
    "restaurant": "Quick note, I noticed {biz} could win back more orders with a smoother online flow.",
    "home_services": "Hey, I was looking at {biz} and saw a few easy wins to turn more site visits into booked estimates.",
    "gym": "I took a look at {biz} and I think you could convert more visitors into trial signups fast.",
    "dentist": "I checked out {biz} and saw a couple quick improvements that can reduce no shows and increase requests.",
    "retail": "I saw {biz} online and there are a few fast upgrades that can boost trust and bring more people in.",
    "default": "I looked at {biz} and found a couple quick ways to capture and follow up with more leads.",
}

NEXT_STEPS: Dict[str, str] = {
    "high": "Call or walk-in is best. Offer a 10 minute demo and show the exact before/after.",
    "medium": "Email or DM. Share one specific improvement and ask if they want a quick demo.",
    "low": "Put them in a later list. Do not spend a lot of time unless they respond.",
}


def pick_offer(category: str) -> str:
    return OFFER_ANGLES.get(category, OFFER_ANGLES["default"])


def pick_opener(category: str, biz: str) -> str:
    t = OPENERS.get(category, OPENERS["default"])
    return t.format(biz=biz)


def next_step_from_score(score: int) -> str:
    if score >= 75:
        return NEXT_STEPS["high"]
    if score >= 50:
        return NEXT_STEPS["medium"]
    return NEXT_STEPS["low"]
