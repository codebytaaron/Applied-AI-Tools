from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

DEFAULT_UA = os.getenv("USER_AGENT", "LeadIQBot/1.0")
DEFAULT_TIMEOUT = int(os.getenv("TIMEOUT_SECONDS", "12"))


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        raise ValueError("website_url is required")
    if not re.match(r"^https?://", url, flags=re.I):
        url = "https://" + url
    return url


def root_domain(url: str) -> str:
    p = urlparse(url)
    return p.netloc.lower()


@dataclass
class FetchResult:
    url: str
    status_code: Optional[int]
    html: str
    error: Optional[str] = None
