#!/usr/bin/env python3
"""Sync membership plans from WordPress REST API into Api/membership-plans.json."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

API_URL = "https://axissportclub.com/wp-json/wp/v2/Membership?per_page=100"
ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "Api" / "membership-plans.json"
FIELDS = ("id", "category", "time", "price", "duration", "features")


def has_details(item: dict) -> bool:
    return bool(item.get("time") or item.get("price") or item.get("features"))


def main() -> int:
    with urllib.request.urlopen(API_URL, timeout=30) as response:
        items = json.load(response)

    if not isinstance(items, list):
        print("Unexpected API response.")
        return 1

    plans = []
    for item in items:
        if not isinstance(item, dict) or item.get("status") not in (None, "publish"):
            continue
        plan = {field: item.get(field) for field in FIELDS if field in item}
        plan["id"] = item.get("id")
        if has_details(plan):
            plans.append(plan)

    if not plans:
        print("API returned no plan fields yet. Install scripts/wp-membership-rest-fields.php on WordPress.")
        return 1

    TARGET.write_text(json.dumps(plans, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(plans)} plan(s) to {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
