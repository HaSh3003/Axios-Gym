#!/usr/bin/env python3
"""
Scan every HTML page for the broken combination:
  - links the NEW dist/css (vendor-styles7df1 / client-stylesef75), AND
  - uses LEGACY class names in markup (umb-block-list, o-band-low, hero-content__inner, fcblock@, o-layout, etc.)
The pages that match are visually broken because the new CSS doesn't ship those legacy selectors.

Usage:
  python3 scripts/detect_legacy_pages.py            # report
  python3 scripts/detect_legacy_pages.py --fix      # swap css links to legacy on every match
"""
from __future__ import annotations
import argparse
import os
import re
import sys
from pathlib import Path

NEW_VENDOR = re.compile(r"vendor-styles7df1\.css\?v=cNyhdo6AhTiWscNAB6ZnZ59mPVbeOWBEwm3ZvK0ZiYw")
NEW_CLIENT = re.compile(r"client-stylesef75\.css\?v=sgie15IPAOBT2CKW4MKUJ67yc04ju47HY7wOjFqlPlE")
LEGACY_VENDOR = "lagecy-vendor896c.css?v=-9SU7a4CHKW3ucnBpOB4iAdtCYDBAxk10jmam1-awww"
LEGACY_CLIENT = "lagecy-clientc5bb.css?v=J82jFTiBvCwYrUK7svGniqA0Rsm8l6xnGvdPtzWzAf0"

LEGACY_MARKERS = re.compile(
    r"\b(?:"
    r"umb-block-list"
    r"|o-band-low"
    r"|hero-content__inner"
    r"|fcblock@(?:desktop|tablet|mobile)"
    r"|o-layout__item"
    r"|u-width-\d/\d@(?:desktop|tablet|mobile)"
    r"|editor-content"
    r"|amp-form"
    r"|amp-cont-group"
    r"|curved-new-form"
    r"|hero-large-v"
    r"|classes-details-hero"
    r")\b"
)

SKIP_DIRS = {".git", "node_modules", "__pycache__", "dist", "media", "App_Plugins", "ar"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix", action="store_true", help="Apply the CSS swap")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    candidates: list[tuple[Path, int]] = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(".html"):
                continue
            p = Path(dirpath) / name
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if not (NEW_VENDOR.search(text) and NEW_CLIENT.search(text)):
                continue
            legacy_hits = len(LEGACY_MARKERS.findall(text))
            if legacy_hits == 0:
                continue
            candidates.append((p.relative_to(root), legacy_hits))

    candidates.sort(key=lambda x: -x[1])
    if not candidates:
        print("No pages need CSS swap.")
        return 0

    print(f"{'HITS':>5}  PAGE")
    for rel, hits in candidates:
        print(f"{hits:>5}  {rel}")
    print(f"\nTotal: {len(candidates)} pages")

    if args.fix:
        for rel, _ in candidates:
            p = root / rel
            text = p.read_text(encoding="utf-8")
            new = NEW_VENDOR.sub(LEGACY_VENDOR, text)
            new = NEW_CLIENT.sub(LEGACY_CLIENT, new)
            if new != text:
                p.write_text(new, encoding="utf-8")
                print(f"  fixed: {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
