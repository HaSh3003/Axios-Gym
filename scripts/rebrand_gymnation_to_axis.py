#!/usr/bin/env python3
"""Remove all GymNation branding from HTML — replace with AXIS / axissportclub.com."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HTML_GLOBS = ["**/*.html"]

FOLDER_MAP = {
    "gymnationfaqs": "axis-faqs",
    "contact-gymnation": "contact-axis",
    "gymnationclasstimetable": "axis-class-timetable",
    "gymnationsignature": "axis-signature",
    "gymnationondemand": "axis-on-demand",
    "gymnation-member-rewards": "axis-member-rewards",
    "gymnationpartners": "axis-partners",
    "jobs-at-gymnation": "jobs-at-axis",
    "gymnationapp": "axis-app",
}

# Order matters — longest / most specific first.
LITERAL_REPLACEMENTS = [
    ("G Y M Nation Management W.L.L", "Axis Sport Club"),
    ("GymNation Sports Company", "Axis Sport Club"),
    ("GymNation LLC", "Axis Sport Club"),
    ("GYMNATION.AE", "axissportclub.com"),
    ("https://www.gymnation.com", "https://axissportclub.com"),
    ("http://www.gymnation.com", "https://axissportclub.com"),
    ("https://gymnation.com", "https://axissportclub.com"),
    ("http://gymnation.com", "https://axissportclub.com"),
    ("www.gymnation.com", "axissportclub.com"),
    ("Gymnation.com", "axissportclub.com"),
    ("gymnation.com", "axissportclub.com"),
    ("@gymnation.com", "@axissportclub.com"),
    ("com.netpulse.mobile.gymnation", "com.axissportclub.mobile"),
    ("GymNationClassTimetable", "AXIS Class Timetable"),
    ("GymNationFAQS", "AXIS FAQs"),
    ("Contact-GymNation", "Contact-AXIS"),
    ("ENG: /Contact-GymNation", "ENG: /Contact-AXIS"),
    ("GymNation Plus", "AXIS Plus"),
    ("GymNation Core", "AXIS Core"),
    ("GymNation Flexible", "AXIS Flexible"),
    ("GymNation Signature", "AXIS Signature"),
    ("GYMNATION-ABUDHABI", "AXIS-ABUDHABI"),
    ("GYMNATION LOCATIONS", "AXIS LOCATIONS"),
    ("GYMNATION FAQS", "AXIS FAQS"),
    ("GYMNATION APP", "AXIS APP"),
    ("GYMNATION BLOG & NEWS", "AXIS BLOG & NEWS"),
    ("GYMNATION BLOG &amp; NEWS", "AXIS BLOG &amp; NEWS"),
    ("CONTACT GYMNATION", "CONTACT AXIS"),
    ("TRY GYMNATION FOR FREE", "TRY AXIS FOR FREE"),
    ("SELECT GYMNATION", "SELECT AXIS"),
    ("Please select GymNation", "Please select AXIS"),
    ("FREE GYMNATION DAY PASS", "FREE AXIS DAY PASS"),
    ("About GymNation", "About AXIS"),
    ("GymNation in the News", "AXIS in the News"),
    ("GymNation Classes", "AXIS Classes"),
    ("The GymNation Chatbot", "The AXIS Chatbot"),
    ("Join GymNation", "Join AXIS"),
    ("Jobs at GymNation", "Jobs at AXIS"),
    ("Advertising in GymNation", "Advertising in AXIS"),
    ("Contact GymNation", "Contact AXIS"),
    ("GymNation UAE", "AXIS UAE"),
    ("GymNation homepage", "AXIS homepage"),
    ("GymNation homepage.", "AXIS homepage."),
    ("GymNation location finder", "AXIS location finder"),
    ("GymNation Class Timetable", "AXIS Class Timetable"),
    ("GymNation Class Timetable page", "AXIS Class Timetable page"),
    ("GymNation classes", "AXIS classes"),
    ("GymNation App", "AXIS App"),
    ("GymNation app", "AXIS app"),
    ("GymNation reception", "AXIS reception"),
    ("GymNation locations", "AXIS locations"),
    ("GymNation location", "AXIS location"),
    ("GymNation members", "AXIS members"),
    ("GymNation members", "AXIS members"),
    ("GymNation team", "AXIS team"),
    ("GymNation membership", "AXIS membership"),
    ("GymNation exercise library", "AXIS exercise library"),
    ("GymNation boxing classes FAQS", "AXIS boxing classes FAQS"),
    ("GymNation Box 'N Burn", "AXIS Box 'N Burn"),
    ("GymNation FAQs", "AXIS FAQs"),
    ("GymNation in the News", "AXIS in the News"),
    ("GymNation News", "AXIS News"),
    ("GymNation in the News", "AXIS in the News"),
    ("GymNation", "AXIS"),
    ("GYMNATION", "AXIS"),
    ("Gymnation", "Axis"),
    ("gymnation", "axis"),
]

# Fix double replacements / artifacts
CLEANUP_REPLACEMENTS = [
    ("AXIS.AE", "axissportclub.com"),
    ("Axis.com", "axissportclub.com"),
    ("axis.com", "axissportclub.com"),
    ("Axis Sport Club (UAE)/Axis Sport Club (KSA)/Axis Sport Club", "Axis Sport Club"),
    ("Axis Sport Club (UAE)/Axis Sport Club (KSA)/ Axis Sport Club", "Axis Sport Club"),
    ("trading as Axis.", "trading as AXIS."),
    ("references to the Axis Sport Club", "references to Axis Sport Club"),
    ("membership of axissportclub.com", "membership of AXIS"),
    ("AXIS On Demand", "AXIS On Demand"),  # noop anchor
]


def case_aware_gymnation(match: re.Match[str]) -> str:
    word = match.group(0)
    if word.isupper():
        return "AXIS"
    if word.islower():
        return "axis"
    if word[0].isupper():
        return "Axis"
    return "AXIS"


def transform(text: str) -> str:
    for old, new in FOLDER_MAP.items():
        text = text.replace(old, new)

    text = re.sub(r"gymnation-", "axis-", text, flags=re.IGNORECASE)

    for old, new in LITERAL_REPLACEMENTS:
        text = text.replace(old, new)

    for old, new in CLEANUP_REPLACEMENTS:
        text = text.replace(old, new)

    # HTTrack mirror comments
    text = re.sub(
        r"<!-- Mirrored from [^>]*gymnation[^>]*-->",
        "<!-- Mirrored from axissportclub.com -->",
        text,
        flags=re.IGNORECASE,
    )

    return text


def main() -> None:
    files: list[Path] = []
    for pattern in HTML_GLOBS:
        files.extend(ROOT.glob(pattern))

    files = sorted(set(files))
    changed = 0
    for path in files:
        original = path.read_text(encoding="utf-8")
        updated = transform(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"updated: {path.relative_to(ROOT)}")

    print(f"\nDone. {changed} file(s) updated.")


if __name__ == "__main__":
    main()
