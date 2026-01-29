from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .utils import FetchResult, DEFAULT_UA, DEFAULT_TIMEOUT, normalize_url


@dataclass
class WebsiteFeatures:
    url: str
    status_ok: bool
    has_https: bool
    has_booking: bool
    has_contact_form: bool
    has_live_chat: bool
    has_email: bool
    has_phone: bool
    has_reviews: bool
    has_pricing: bool
    has_careers: bool
    has_locations: bool
    cms_hint: Optional[str]
    load_seconds_est: Optional[float]
    word_count: int


BOOKING_WORDS = [
    "book", "booking", "schedule", "appointment", "reserve", "reservation",
    "order online", "pickup", "delivery", "table", "get a quote", "estimate",
]
CONTACT_FORM_HINTS = ["<form", "contact", "get in touch", "message us", "inquiry"]
CHAT_HINTS = ["intercom", "zendesk", "tawk", "drift", "crisp", "livechat", "chat widget"]
REVIEWS_HINTS = ["testimonials", "reviews", "google reviews", "yelp", "trustpilot", "rating"]
PRICING_HINTS = ["pricing", "plans", "package", "packages", "membership", "rates"]
CAREERS_HINTS = ["careers", "jobs", "join our team", "hiring"]
LOCATIONS_HINTS = ["locations", "find us", "our locations", "store locator"]


def fetch_html(url: str) -> FetchResult:
    url = normalize_url(url)
    headers = {"User-Agent": DEFAULT_UA, "Accept": "text/html,*/*;q=0.8"}
    try:
        r = requests.get(url, headers=headers, timeout=DEFAULT_TIMEOUT, allow_redirects=True)
        html = r.text or ""
        return FetchResult(url=r.url, status_code=r.status_code, html=html)
    except Exception as e:
        return FetchResult(url=url, status_code=None, html="", error=str(e))


def _contains_any(text: str, needles: list[str]) -> bool:
    t = (text or "").lower()
    return any(n in t for n in needles)


def _detect_email(text: str) -> bool:
    return bool(re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text or "", flags=re.I))


def _detect_phone(text: str) -> bool:
    # US-focused, simple
    return bool(re.search(r"(\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text or ""))


def _cms_hint(html: str) -> Optional[str]:
    h = (html or "").lower()
    if "wp-content" in h or "wordpress" in h:
        return "WordPress"
    if "cdn.shopify.com" in h or "shopify" in h:
        return "Shopify"
    if "wix" in h and "wixsite" in h:
        return "Wix"
    if "squarespace" in h:
        return "Squarespace"
    if "webflow" in h:
        return "Webflow"
    return None


def extract_features(website_url: str) -> Tuple[WebsiteFeatures, Dict]:
    fr = fetch_html(website_url)
    meta: Dict = {"fetch": {"final_url": fr.url, "status_code": fr.status_code, "error": fr.error}}

    has_https = fr.url.lower().startswith("https://")
    status_ok = (fr.status_code is not None) and (200 <= fr.status_code < 400) and not fr.error

    html = fr.html or ""
    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text(" ", strip=True)
    lower_text = text.lower()
    lower_html = html.lower()

    # Rough "load" estimate: request elapsed is not reliable without timing hooks, so keep None.
    load_seconds_est = None

    has_booking = _contains_any(lower_text, BOOKING_WORDS) or _contains_any(lower_html, BOOKING_WORDS)
    has_contact_form = ("<form" in lower_html) and _contains_any(lower_text + " " + lower_html, ["contact", "message", "inquiry"])
    has_live_chat = _contains_any(lower_html, CHAT_HINTS)
    has_email = _detect_email(text) or ("mailto:" in lower_html)
    has_phone = _detect_phone(text) or ("tel:" in lower_html)
    has_reviews = _contains_any(lower_text + " " + lower_html, REVIEWS_HINTS)
    has_pricing = _contains_any(lower_text + " " + lower_html, PRICING_HINTS)
    has_careers = _contains_any(lower_text + " " + lower_html, CAREERS_HINTS)
    has_locations = _contains_any(lower_text + " " + lower_html, LOCATIONS_HINTS)

    cms = _cms_hint(html)

    wc = len(re.findall(r"\w+", text))

    feats = WebsiteFeatures(
        url=fr.url,
        status_ok=status_ok,
        has_https=has_https,
        has_booking=has_booking,
        has_contact_form=has_contact_form,
        has_live_chat=has_live_chat,
        has_email=has_email,
        has_phone=has_phone,
        has_reviews=has_reviews,
        has_pricing=has_pricing,
        has_careers=has_careers,
        has_locations=has_locations,
        cms_hint=cms,
        load_seconds_est=load_seconds_est,
        word_count=wc,
    )

    meta["features_raw"] = asdict(feats)
    return feats, meta
