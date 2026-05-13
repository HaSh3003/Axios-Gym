"""Disable the footer page-link columns site-wide.

The footer has three columns of page links inside
`<div class="flink-box-content"> … </div>`. The user wants every
`<a>` link inside those columns rendered visually muted and
non-clickable, because most of those destination pages don't exist yet.

We do NOT touch:
  • The "JOIN NOW" CTA (its destination exists and works)
  • The brand-logo link
  • PROUD SUPPORTER imagery
  • Social-icon links

For each `<a href="…">` inside a flink-box-content block, we:
  1. Replace its href with javascript:void(0); so clicks do nothing.
  2. Inject aria-disabled="true" and tabindex="-1" for accessibility.
  3. Append an inline style providing the visual disabled state
     (pointer-events:none, dim opacity, not-allowed cursor).

Idempotent: links already carrying aria-disabled="true" are skipped.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(".")

TARGETS = [
    "components/site-footer.html",
    "index.html",
    "aboutgymnearme/index.html",
    "blog/index.html",
    "coming-soon/index.html",
    "contact-gymnation/index.html",
    "exercise-library/index.html",
    "fitness-classes/boxing-classes/index.html",
    "fitness-hub/index.html",
    "gymnationfaqs/index.html",
    "gymsnearme/index.html",
    "gymsnearme/gymmembership/index.html",
    "privacy-policy/index.html",
]

DISABLE_STYLE = "pointer-events:none;opacity:.55;cursor:not-allowed;"

# Each footer column body. Non-greedy DOTALL — these blocks contain
# multi-line <ul> markup.
FLINK_BLOCK_RE = re.compile(
    r'<div class="flink-box-content">(.*?)</div>',
    re.DOTALL,
)

# Match an <a> opening tag with an href attribute. Captures attrs
# before/after href so we can preserve arbitrary attribute order
# (class, title, etc.).
A_TAG_RE = re.compile(
    r'<a\s+([^>]*?)href="([^"]*)"([^>]*)>',
)


def disable_anchor(m: re.Match[str]) -> str:
    attrs_before, _href, attrs_after = m.group(1), m.group(2), m.group(3)
    combined = attrs_before + attrs_after
    if 'aria-disabled="true"' in combined:
        return m.group(0)

    return (
        f'<a {attrs_before}href="javascript:void(0);"{attrs_after} '
        f'aria-disabled="true" tabindex="-1" '
        f'style="{DISABLE_STYLE}">'
    )


def disable_block(m: re.Match[str]) -> str:
    inner = m.group(1)
    new_inner = A_TAG_RE.sub(disable_anchor, inner)
    return f'<div class="flink-box-content">{new_inner}</div>'


def process(path: Path) -> int:
    original = path.read_text(encoding="utf-8")
    updated = FLINK_BLOCK_RE.sub(disable_block, original)
    if updated == original:
        return 0

    path.write_text(updated, encoding="utf-8")
    # Count how many <a> tags ended up disabled in this file.
    return updated.count('aria-disabled="true"') - original.count('aria-disabled="true"')


def main() -> None:
    total = 0
    for rel in TARGETS:
        path = ROOT / rel
        if not path.exists():
            print(f"SKIP  {rel}  (not found)")
            continue
        delta = process(path)
        total += delta
        flag = "OK   " if delta else "(noop)"
        print(f"{flag} {rel}  disabled={delta}")

    print(f"\nTotal anchors disabled: {total}")


if __name__ == "__main__":
    main()
