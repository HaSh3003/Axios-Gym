#!/usr/bin/env python3
"""Fill Api/jbr-reviews-cache.json using Google Places API (New).

1. Enable "Places API (New)" on a Google Cloud project.
2. Create an API key (server-side use is fine for this script).
3. Put the key in Api/.env as GOOGLE_PLACES_API_KEY=your_key

Optional: set PLACE_ID=ChIJ... in Api/.env to skip text search.

Then run from repo root:
  python3 scripts/fetch_google_reviews.py
"""

from __future__ import annotations

import json
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / "Api" / ".env"
OUT_PATH = ROOT / "Api" / "jbr-reviews-cache.json"

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
DETAILS_PREFIX = "https://places.googleapis.com/v1/places/"


def load_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.is_file():
        return data
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        data[key.strip()] = val.strip().strip('"').strip("'")
    return data


def http_post_json(url: str, headers: dict[str, str], body: object) -> dict:
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_get_json(url: str, headers: dict[str, str]) -> dict:
    req = urllib.request.Request(url, headers=headers, method="GET")
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def normalize_reviews(details: dict) -> list[dict]:
    out: list[dict] = []
    for r in details.get("reviews") or []:
        auth = r.get("authorAttribution") or {}
        text_obj = r.get("text") or r.get("originalText") or {}
        text = text_obj.get("text") if isinstance(text_obj, dict) else ""
        out.append(
            {
                "author": auth.get("displayName") or "Google user",
                "rating": int(r.get("rating") or 0),
                "text": (text or "").strip(),
                "time": r.get("relativePublishTimeDescription") or "",
                "photoUri": auth.get("photoUri") or "",
                "authorUri": auth.get("uri") or "",
            }
        )
    return [x for x in out if x["text"]]


def main() -> int:
    env = load_env(ENV_PATH)
    api_key = env.get("GOOGLE_PLACES_API_KEY", "").strip()
    if not api_key:
        print("Missing GOOGLE_PLACES_API_KEY in Api/.env", file=sys.stderr)
        return 1

    place_id = env.get("PLACE_ID", "").strip()
    headers_json = {"Content-Type": "application/json", "X-Goog-Api-Key": api_key}

    if not place_id:
        body = {
            "textQuery": "AXIS SPORT Personal Training Gym JBR Dubai",
            "locationBias": {
                "circle": {
                    "center": {"latitude": 25.0744576, "longitude": 55.1314458},
                    "radius": 120.0,
                }
            },
        }
        headers_search = {
            **headers_json,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress",
        }
        try:
            search = http_post_json(SEARCH_URL, headers_search, body)
        except urllib.error.HTTPError as e:
            print(e.read().decode("utf-8", "replace"), file=sys.stderr)
            return 1
        places = search.get("places") or []
        if not places:
            print("No places returned from searchText; set PLACE_ID in Api/.env", file=sys.stderr)
            return 1
        top = places[0]
        place_id = top.get("id") or ""
        name_guess = (top.get("displayName") or {}).get("text") or top.get("displayName")
        print("Using place:", name_guess, "| id:", place_id)

    field_mask = "reviews,displayName,id,rating,userRatingCount"
    headers_get = {**headers_json, "X-Goog-FieldMask": field_mask}
    url = f"{DETAILS_PREFIX}{place_id}"
    try:
        details = http_get_json(url, headers_get)
    except urllib.error.HTTPError as e:
        print(e.read().decode("utf-8", "replace"), file=sys.stderr)
        return 1

    dn = details.get("displayName")
    if isinstance(dn, dict):
        display = dn.get("text") or dn.get("name") or ""
    else:
        display = dn or ""
    doc = {
        "_source": "Google Places API (New) — Place Details; Google may return up to ~5 reviews per request.",
        "placeName": display or "AXIS SPORT - Personal Training & Gym JBR",
        "mapsUrl": "https://maps.app.goo.gl/L25K8wumDAcFRxXN8",
        "placeId": place_id,
        "overallRating": details.get("rating"),
        "userRatingCount": details.get("userRatingCount"),
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "reviews": normalize_reviews(details),
    }
    OUT_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(doc['reviews'])} reviews to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
