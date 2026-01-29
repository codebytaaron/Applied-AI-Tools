from __future__ import annotations

import argparse
import json
import sys

from src.feature_extractor import extract_features
from src.scoring_model import score_lead


def main() -> int:
    p = argparse.ArgumentParser(prog="lead-iq", description="Score a local business lead from a website URL.")
    p.add_argument("--biz", required=True, help="Business name")
    p.add_argument("--url", required=True, help="Website URL")
    p.add_argument("--category", default="default", help="Category, ex: restaurant, home_services, gym")
    p.add_argument("--town", default="", help="Town or area")
    p.add_argument("--notes", default="", help="Optional notes")
    p.add_argument("--debug", action="store_true", help="Include debug info")
    args = p.parse_args()

    feats, meta = extract_features(args.url)
    out = score_lead(
        biz_name=args.biz,
        category=args.category,
        town=args.town,
        features=feats,
        notes=args.notes,
        include_debug=args.debug,
    )

    payload = {
        "score": out.score,
        "reasons": out.reasons,
        "recommended_offer": out.recommended_offer,
        "outreach_opener": out.outreach_opener,
        "next_step": out.next_step,
        "confidence": out.confidence,
    }
    if args.debug:
        payload["debug"] = out.debug
        payload["meta"] = meta

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
