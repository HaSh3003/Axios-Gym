"""Replace visible GymNation/AXIS-branding occurrences on the About page.

Strategy:
1) Protect URL-like/path/filename/handle tokens that contain "gymnation"
   by swapping them for unique placeholders.
2) Run a case-aware regex replacement of any remaining "gymnation" with
   the matching case form of "axis".
3) Restore the protected tokens.

This keeps SEO URLs (gymnation.com), social handles (gymnation_me),
folder routes (../gymnationapp/), and image filenames
(gymnation-al-quoz.webp) intact while changing every visible mention of
"GymNation" to "Axis".
"""

from __future__ import annotations

import re
from pathlib import Path

TARGET = Path("aboutgymnearme/index.html")

# Patterns that must NOT be replaced. Order matters: longer / more
# specific patterns first so they are protected before shorter ones.
PROTECT_PATTERNS = [
    # App Store iOS app URL component: "gymnation/id1669518396"
    r"gymnation/id\d+",
    # Android package name
    r"com\.netpulse\.mobile\.gymnation",
    # Domain
    r"gymnation\.com",
    # Image / media filenames: gymnation-anything.{webp,jpg,png,...}
    r"gymnation-[a-z0-9-]+\.(?:webp|png|jpg|jpeg|svg|gif)",
    # Iconic / boditrax filenames (without extension catch-all already
    # covered above, but kept as a safety net).
    r"gymnation-iconic-workout-arena",
    r"gymnation-boditrax-scan-results-screen[a-z0-9-]*",
    # Social media handles (Facebook / Instagram / Twitter / TikTok)
    r"gymnation_me\b",
    r"gymnationme\b",
    # Folder routes: ../gymnationXXX/ ...
    r"\.\./gymnation[a-z0-9-]*/",
    # Folder routes that have gymnation as a suffix: ../contact-gymnation/,
    # ../jobs-at-gymnation/
    r"\.\./[a-z0-9-]+-gymnation/",
    # Any /media/.../gymnation*.* asset path inside src / srcset
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
