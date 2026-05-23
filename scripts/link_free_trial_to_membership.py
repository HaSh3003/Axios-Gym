#!/usr/bin/env python3
"""Point header FREE TRIAL buttons to the membership page."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BTN_RE = re.compile(
    r'<button(?=[^>]*\bid="btnFreetrail")[^>]*>FREE TRIAL</button>',
    re.IGNORECASE,
)

LINK_RE = re.compile(
    r'(<a(?=[^>]*\bid="btnFreetrail")[^>]*\bhref=")[^"]*(")',
    re.IGNORECASE,
)


def membership_href(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "gymsnearme/gymmembership/index.html":
        return "index.html"
    if rel.startswith("gymsnearme/"):
        return "gymmembership/index.html"
    parts = path.parent.relative_to(ROOT).parts
    if not parts:
        return "gymsnearme/gymmembership/index.html"
    return "../" * len(parts) + "gymsnearme/gymmembership/index.html"


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if 'id="btnFreetrail"' not in text:
        return False

    href = membership_href(path)
    updated = BTN_RE.sub(
        f'<a class="g-btn g-btn--fill-white g-btn--arrow" href="{href}" id="btnFreetrail" title="FREE TRIAL">FREE TRIAL</a>',
        text,
    )
    updated = LINK_RE.sub(rf"\1{href}\2", updated)

    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    changed = []
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts or "components" in path.parts:
            continue
        if patch_file(path):
            changed.append(path.relative_to(ROOT))
    print(f"Updated FREE TRIAL header link in {len(changed)} file(s):")
    for p in changed:
        print(f"  - {p}")


if __name__ == "__main__":
    main()
