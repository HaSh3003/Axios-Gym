#!/usr/bin/env python3
"""Remove Arabic/English language switcher from headers (no translation site)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LANG_SWITCH_RE = re.compile(
    r'\s*<div class="language--switch">\s*'
    r'<a class="lang-btn ae-btn"[^>]*>.*?</a>\s*'
    r'<a class="lang-btn en-btn"[^>]*>.*?</a>\s*'
    r"</div>\s*",
    re.DOTALL,
)


def main() -> None:
    changed = []
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if "language--switch" not in text:
            continue
        updated = LANG_SWITCH_RE.sub("", text)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed.append(path.relative_to(ROOT))
    print(f"Removed language switcher from {len(changed)} file(s):")
    for p in changed:
        print(f"  - {p}")


if __name__ == "__main__":
    main()
