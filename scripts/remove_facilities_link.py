"""Remove the "Facilities" link/menu from the site header.

Three things must go everywhere the header is duplicated:
  1. Desktop top-level <li> with the "Facilities" link
     (identified by data-id="facilities").
  2. Desktop mega-submenu panel: <div class="mega-submenu" id="facilities">…</div>
     (a single <ul> with HYROX PC, Recovery, Ladies Gym, Gym Equipment,
     Podcast Studio, Boditrax).
  3. Mobile menu <li> with title="Facilities" and its nested submenu-wrapper.

The script is idempotent.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(".")

# Pages with a duplicated header (collected via grep beforehand).
TARGETS = [
    "components/site-header.html",
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

# 1) Desktop top-level <li class="menu-item has-submenu"> with the
#    "Facilities" link (identified by data-id="facilities" anywhere in the
#    inner <a>'s attributes).
DESKTOP_TOP_RE = re.compile(
    r"""
    [ \t]*<li\s+class="menu-item\ has-submenu">[ \t]*\n
    [ \t]*<a\s[^>]*?data-id=["']facilities["'][^>]*>[^<]*</a>[ \t]*\n
    (?:[ \t]*\n)*
    [ \t]*</li>[ \t]*\n
    """,
    re.VERBOSE,
)

# 2) Desktop mega-submenu panel.
#    The <ul>…</ul> body lives on a single (very long) line, so we don't
#    need DOTALL — \S works.
DESKTOP_PANEL_RE = re.compile(
    r"""
    [ \t]*<div\s+class="mega-submenu"\s+id="facilities">[ \t]*\n
    [ \t]*<ul>.*?</ul>[ \t]*\n
    [ \t]*</div>[ \t]*\n
    """,
    re.VERBOSE | re.DOTALL,
)

# 3) Mobile <li class="menu-item has-submenu"> wrapping
#    <a … title="Facilities" …>Facilities</a> plus the nested submenu.
#    This must NOT match the desktop top-level item (already covered) — we
#    require the trailing <span class="child-trigger"></span> + nested
#    <ul class="submenu-wrapper"> structure, which is mobile-only.
MOBILE_RE = re.compile(
    r"""
    [ \t]*<li\s+class="menu-item\ has-submenu">[ \t]*\n
    (?:[ \t]*\n)*
    [ \t]*<a\s[^>]*?title="Facilities"[^>]*>Facilities</a>[ \t]*\n
    (?:[ \t]*\n)*
    [ \t]*<span\s+class="child-trigger"></span>[ \t]*\n
    (?:[ \t]*\n)*
    [ \t]*<ul\s+class="submenu-wrapper">[ \t]*\n
    (?:.*?\n)*?
    [ \t]*</ul>[ \t]*\n
    (?:[ \t]*\n)*
    [ \t]*</li>[ \t]*\n
    """,
    re.VERBOSE,
)


def scrub(path: Path) -> tuple[int, int, int]:
    original = path.read_text(encoding="utf-8")

    text, n_desktop_top = DESKTOP_TOP_RE.subn("", original)
    text, n_panel = DESKTOP_PANEL_RE.subn("", text)
    text, n_mobile = MOBILE_RE.subn("", text)

    if text != original:
        path.write_text(text, encoding="utf-8")

    return n_desktop_top, n_panel, n_mobile


def main() -> None:
    total = [0, 0, 0]
    for rel in TARGETS:
        path = ROOT / rel
        if not path.exists():
            print(f"SKIP  {rel} (not found)")
            continue
        counts = scrub(path)
        total = [a + b for a, b in zip(total, counts)]
        flag = "OK   " if any(counts) else "(noop)"
        print(f"{flag} {rel}  top={counts[0]} panel={counts[1]} mobile={counts[2]}")

    print()
    print(f"Totals: desktop-top={total[0]}  panel={total[1]}  mobile={total[2]}")


if __name__ == "__main__":
    main()
