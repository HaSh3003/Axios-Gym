#!/usr/bin/env python3
"""
Strip every reference to the removed fitness-classes/* sub-pages so the site
stops linking to pages that no longer exist.

What it does, per file:
  1. Removes mobile-menu `<li class="menu-item">...href=".../fitness-classes/CLASS/index.html"...</li>`.
  2. Removes desktop mega-menu `<li class="gn-subnav-item">...href=".../fitness-classes/CLASS/index.html"...</li>`.
  3. Removes the listing-page `<div class="fcblock...">...CLASS/index.html...</div>` cards
     in fitness-classes/index.html.
  4. Replaces any remaining inline `<a href="...fitness-classes/CLASS/index.html"...>TEXT</a>`
     with just `TEXT` so prose stops linking to dead pages.

The folders themselves are deleted separately (after this script).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REMOVED_CLASSES = [
    "bollynation-classes",
    "les-mills-bodyattack-classes",
    "les-mills-bodycombat-classes",
    "les-mills-bodypump-classes",
    "les-mills-rpm-classes",
    "les-mills-shapes-classes",
    "mat-pilates-classes",
    "muay-thai-muppets",
    "pop-pilates-classes",
    "sound-healing-classes",
    "wodnation-classes",
    "yoga-classes",
    "zumba-classes",
]

CLASSES_ALT = "|".join(re.escape(c) for c in REMOVED_CLASSES)

# Match an href whose value (single- or double-quoted) ends with
# CLASS/index.html. Covers both the absolute form ".../fitness-classes/CLASS/index.html"
# and the sibling form "../CLASS/index.html" used inside the fitness-classes folder.
# The (?<![a-zA-Z0-9-]) lookbehind prevents matching inside compound names like
# breathing-yoga-classes/... (where the char before "yoga" would be a hyphen).
HREF_FRAG = (
    r"href=[\"'][^\"']*?(?<![a-zA-Z0-9-])(?:"
    + CLASSES_ALT
    + r")/index\.html[\"']"
)

# Mobile menu item (multi-line). The <a> tag can have any attribute order
# (e.g. class, title, href in site-header.html vs class, href in the prebuilt pages),
# may have multiple spaces between attributes, and is followed by an optional blank line.
#   <li class="menu-item">
#       <a ... href="...fitness-classes/CLASS/index.html" ...>X</a>
#                                                         <-- optional blank line -->
#   </li>
MOBILE_ITEM = re.compile(
    r"[ \t]*<li class=\"menu-item\">[ \t]*\n"
    r"[ \t]*<a\s[^>]*?" + HREF_FRAG + r"[^>]*>[^<]*</a>[ \t]*\n"
    r"(?:[ \t]*\n)*"
    r"[ \t]*</li>[ \t]*\n",
)

# Desktop mega-menu item (inline, on the giant single-line <ul>). Attribute
# order/quotes vary between the static pages (double quotes, class first) and
# components/site-header.html (single quotes, href first).
#   <li class="gn-subnav-item"><a ... href="...fitness-classes/CLASS/index.html" ...>...</a></li>
DESKTOP_ITEM = re.compile(
    r"<li class=[\"']gn-subnav-item[\"']><a\s[^>]*?" + HREF_FRAG + r"[^>]*?>.*?</a></li>",
    re.DOTALL,
)

# fcblock card in fitness-classes/index.html:
#   <div class="fcblock@desktop fcblock@tablet fcblock@mobile fcblock u-margin-bottom" onclick="javascript:location.href='CLASS/index.html'">
#       <a href="CLASS/index.html">
#           ...
#       </a>
#   </div>
FCBLOCK_CARD = re.compile(
    r"[ \t]*<div class=\"fcblock@desktop fcblock@tablet fcblock@mobile fcblock u-margin-bottom\" onclick=\"javascript:location\.href='(?:" + CLASSES_ALT + r")/index\.html'\">.*?</a>[ \t]*\n[ \t]*</div>[ \t]*\n",
    re.DOTALL,
)

# Inline anchor in prose:  <a href="...fitness-classes/CLASS/index.html" ...>TEXT</a>
INLINE_ANCHOR = re.compile(
    r"<a\s+[^>]*?" + HREF_FRAG + r"[^>]*>(.*?)</a>",
    re.DOTALL,
)

SKIP_DIRS = {".git", "node_modules", "__pycache__", "dist", "media", "App_Plugins"}


def should_skip(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    parts = rel.parts
    if any(p in SKIP_DIRS for p in parts):
        return True
    # Skip the class folders we're about to delete anyway.
    if len(parts) >= 2 and parts[0] == "fitness-classes" and parts[1] in REMOVED_CLASSES:
        return True
    return False


def process_file(path: Path, is_listing_page: bool) -> tuple[int, int, int, int]:
    original = path.read_text(encoding="utf-8", errors="surrogatepass")
    text = original

    mob = MOBILE_ITEM.subn("", text)
    text, mob_n = mob

    desk = DESKTOP_ITEM.subn("", text)
    text, desk_n = desk

    fc_n = 0
    if is_listing_page:
        fc = FCBLOCK_CARD.subn("", text)
        text, fc_n = fc

    inl = INLINE_ANCHOR.subn(lambda m: m.group(1), text)
    text, inl_n = inl

    if text != original:
        path.write_text(text, encoding="utf-8")
    return mob_n, desk_n, fc_n, inl_n


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    totals = {"mobile": 0, "desktop": 0, "fcblock": 0, "inline": 0, "files": 0}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(".html"):
                continue
            p = Path(dirpath) / name
            if should_skip(p, root):
                continue
            is_listing = p.resolve() == (root / "fitness-classes" / "index.html").resolve()
            mob_n, desk_n, fc_n, inl_n = process_file(p, is_listing)
            if mob_n or desk_n or fc_n or inl_n:
                totals["mobile"] += mob_n
                totals["desktop"] += desk_n
                totals["fcblock"] += fc_n
                totals["inline"] += inl_n
                totals["files"] += 1
                print(f"  {p.relative_to(root)}: mobile={mob_n} desktop={desk_n} fcblock={fc_n} inline={inl_n}")

    print()
    print(f"Files updated: {totals['files']}")
    print(f"Mobile menu items removed: {totals['mobile']}")
    print(f"Desktop mega-menu items removed: {totals['desktop']}")
    print(f"fcblock cards removed: {totals['fcblock']}")
    print(f"Inline anchors flattened: {totals['inline']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
