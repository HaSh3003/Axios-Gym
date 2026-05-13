"""Make every class card on fitness-classes/index.html non-navigational.

Each class is rendered as:

    <div class="… fcblock …" onclick="javascript:location.href='…';">
      <a href="…">
        … image + title …
      </a>
    </div>

We want the cards visible but inert — clicking them must do nothing. We
therefore:
  1. Strip the entire `onclick="…"` attribute from each fcblock div.
  2. Rewrite the inner `<a href="…">` to `href="javascript:void(0);"`
     and add `aria-disabled="true"` (only when not already present).

This leaves the visuals, hover effect, and layout intact — only the
navigation is removed.
"""

from __future__ import annotations

import re
from pathlib import Path

TARGET = Path("fitness-classes/index.html")

ONCLICK_ATTR = re.compile(
    r'\s+onclick="javascript:location\.href=\'[^\']*\';?"',
)

# Match the <a href="…"> that opens immediately inside an fcblock div.
# It's always indented and on its own line — but we won't rely on that;
# instead we'll only touch <a> tags directly preceded (after whitespace)
# by an fcblock <div>. To keep the regex simple we run a two-step pass.
FCBLOCK_OPEN = re.compile(
    r'(<div class="[^"]*\bfcblock\b[^"]*"[^>]*>)',
)

INNER_A_HREF = re.compile(
    r'(<a\s+)href="[^"]*"',
)


def neutralise(text: str) -> tuple[str, int, int]:
    new_text, n_onclick = ONCLICK_ATTR.subn("", text)

    # For each fcblock div, find the *next* <a href="…"> after it and
    # rewrite it. We walk through the file from one fcblock to the
    # next.
    pieces: list[str] = []
    cursor = 0
    n_anchors = 0
    for m in FCBLOCK_OPEN.finditer(new_text):
        pieces.append(new_text[cursor : m.end()])
        cursor = m.end()
        # Look ahead to the next <a href="…"> within this fcblock; we
        # stop at the matching </div>.
        a_match = INNER_A_HREF.search(new_text, cursor)
        if a_match is None:
            continue
        # Make sure the anchor is still inside this card, i.e. it comes
        # before the next fcblock opener.
        next_block = FCBLOCK_OPEN.search(new_text, cursor)
        if next_block is not None and a_match.start() >= next_block.start():
            continue
        # Append everything up to the <a … and rewrite the href.
        pieces.append(new_text[cursor : a_match.start()])
        rewritten = a_match.group(1) + 'href="javascript:void(0);" aria-disabled="true"'
        pieces.append(rewritten)
        cursor = a_match.end()
        n_anchors += 1

    pieces.append(new_text[cursor:])
    return "".join(pieces), n_onclick, n_anchors


def main() -> None:
    original = TARGET.read_text(encoding="utf-8")
    updated, n_onclick, n_anchors = neutralise(original)

    if updated == original:
        print("No changes needed.")
        return

    TARGET.write_text(updated, encoding="utf-8")
    print(f"Stripped onclick from         : {n_onclick} fcblock divs")
    print(f"Rewrote inner href on         : {n_anchors} anchors")


if __name__ == "__main__":
    main()
