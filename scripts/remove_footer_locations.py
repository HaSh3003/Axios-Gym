#!/usr/bin/env python3
"""Remove the entire LOCATIONS flink-box from every page footer."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# A flink-box opener, optional whitespace, then the LOCATIONS heading, then
# its inner flink-box-content div, then the closing </div></div> of the outer
# flink-box. The inner block has no other <div>, so non-greedy matching works.
PATTERN = re.compile(
    r"[ \t]*<div class=\"flink-box\">\s*"
    r"<h3[^>]*>\s*LOCATIONS\s*</h3>\s*"
    r"<div class=\"flink-box-content\">.*?</div>\s*"
    r"</div>[ \t]*\n?",
    re.DOTALL,
)

SKIP_DIRS = {".git", "node_modules", "__pycache__", "dist", "media", "App_Plugins"}


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    updated = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(".html"):
                continue
            p = Path(dirpath) / name
            text = p.read_text(encoding="utf-8")
            new, n = PATTERN.subn("", text)
            if n:
                p.write_text(new, encoding="utf-8")
                print(f"  removed x{n}: {p.relative_to(root)}")
                updated += n
    print(f"\nLOCATIONS flink-box removed from {updated} file occurrences.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
