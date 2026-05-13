"""Rebrand visible GymNation occurrences on the Locations page.

Mirrors `rebrand_about_page.py` but targets `gymsnearme/index.html`.
All visible "GymNation" text is replaced with the case-matching form
of "Axis", while URLs, social handles, file paths and asset filenames
are left untouched.
"""

from __future__ import annotations

import re
from pathlib import Path

TARGET = Path("gymsnearme/index.html")

PROTECT_PATTERNS = [
    r"gymnation/id\d+",
    r"com\.netpulse\.mobile\.gymnation",
    r"gymnation\.com",
    r"gymnation-[a-z0-9-]+\.(?:webp|png|jpg|jpeg|svg|gif)",
    r"gymnation-iconic-workout-arena",
    r"gymnation-boditrax-scan-results-screen[a-z0-9-]*",
    r"gymnation_me\b",
    r"gymnationme\b",
    r"\.\./gymnation[a-z0-9-]*/",
    r"\.\./[a-z0-9-]+-gymnation/",
    # Paths inside this folder don't need ../
    r"\bgymnation[a-z0-9-]*/index[0-9a-z]*\.html",
    r"/media/[^\"'<>\s]*gymnation[^\"'<>\s]*",
]


def case_aware_replace(match: re.Match[str]) -> str:
    word = match.group(0)
    if word.isupper():
        return "AXIS"
    if word.islower():
        return "axis"
    return "Axis"


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    original = text

    placeholders: dict[str, str] = {}
    counter = 0

    def stash(m: re.Match[str]) -> str:
        nonlocal counter
        counter += 1
        key = f"\x00GN_PRES_{counter}\x00"
        placeholders[key] = m.group(0)
        return key

    for pattern in PROTECT_PATTERNS:
        text = re.sub(pattern, stash, text, flags=re.IGNORECASE)

    text, replaced = re.subn(
        r"gymnation",
        case_aware_replace,
        text,
        flags=re.IGNORECASE,
    )

    for key, value in placeholders.items():
        text = text.replace(key, value)

    TARGET.write_text(text, encoding="utf-8")

    print(f"Protected tokens     : {len(placeholders)}")
    print(f"Visible replacements : {replaced}")
    print(f"Net length delta     : {len(text) - len(original)}")


if __name__ == "__main__":
    main()
