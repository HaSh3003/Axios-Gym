"""One-off: scrub remaining visible GymNation mentions from
fitness-hub/index.html (head meta tags, JSON-LD, etc.) while protecting
URLs / paths / handles.
"""

from __future__ import annotations

import re
from pathlib import Path

TARGET = Path("fitness-hub/index.html")

PROTECT = [
    r"gymnation\.com",
    r"gymnation/id\d+",
    r"com\.netpulse\.mobile\.gymnation",
    r"gymnation-[a-z0-9-]+\.(?:webp|png|jpg|jpeg|svg|gif)",
    r"gymnation_me\b",
    r"gymnationme\b",
    r"\.\./gymnation[a-z0-9-]*/",
    r"\.\./[a-z0-9-]+-gymnation/",
    r"/media/[^\"'<>\s]*gymnation[^\"'<>\s]*",
]


def case_aware(m: re.Match[str]) -> str:
    w = m.group(0)
    if w.isupper():
        return "AXIS"
    if w.islower():
        return "axis"
    return "Axis"


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    original = text

    placeholders: dict[str, str] = {}
    counter = [0]

    def stash(m: re.Match[str]) -> str:
        counter[0] += 1
        key = f"\x00FH_PRES_{counter[0]}\x00"
        placeholders[key] = m.group(0)
        return key

    for pat in PROTECT:
        text = re.sub(pat, stash, text, flags=re.IGNORECASE)

    text, replaced = re.subn(r"gymnation", case_aware, text, flags=re.IGNORECASE)

    for k, v in placeholders.items():
        text = text.replace(k, v)

    TARGET.write_text(text, encoding="utf-8")
    print(f"Protected URL tokens     : {len(placeholders)}")
    print(f"Visible replacements     : {replaced}")
    print(f"Net length delta         : {len(text) - len(original)}")


if __name__ == "__main__":
    main()
