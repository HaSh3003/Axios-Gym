#!/usr/bin/env python3
"""
Inject the standard site header (with logo + nav + free-trial button) into
gymsnearme/gymmembership/index.html. The header is copied verbatim from the
already-working fitness-classes/boxing-classes/index.html since both pages
live two levels deep (../../ relative paths line up).

What this does to gymmembership/index.html:
  1. Inserts the wrapper opening (panel-wrapper / align-items-start) and the
     full <header> right before <main>.
  2. Adds the matching wrapper closing (</div></div>) right after </main>.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "fitness-classes" / "boxing-classes" / "index.html"
TARGET = ROOT / "gymsnearme" / "gymmembership" / "index.html"

# Source header range:
#   line 143 -> <div class="panel-wrapper">
#   line 144 -> (blank with whitespace)
#   line 145 -> <div class="align-items-start">
#   line 146 -> skip-link
#   line 147 -> <header class="btn-align-right">
#   ...
#   line 684 -> </header>
SRC_FIRST_LINE = 143  # inclusive (1-based) — starts at panel-wrapper opener
SRC_LAST_LINE = 684  # inclusive (1-based) — ends at </header>


def main() -> int:
    src_lines = SOURCE.read_text(encoding="utf-8").splitlines(keepends=True)
    header_block = "".join(src_lines[SRC_FIRST_LINE - 1 : SRC_LAST_LINE])

    target = TARGET.read_text(encoding="utf-8")

    if 'class="panel-wrapper"' in target and "btn-align-right" in target:
        print("gymmembership already has a header; aborting to avoid double-inject.")
        return 0

    # Insert the header block right before the <main> tag.
    marker_open = "        <main>"
    if target.count(marker_open) != 1:
        print(f"Could not find unique '{marker_open}' marker; aborting.")
        return 1

    target = target.replace(marker_open, header_block + marker_open, 1)

    # Insert wrapper closers right after </main>.
    marker_close = "        </main>"
    if target.count(marker_close) != 1:
        print(f"Could not find unique '{marker_close}' marker; aborting.")
        return 1
    target = target.replace(
        marker_close,
        marker_close + "\n        </div>\n    </div>\n",
        1,
    )

    TARGET.write_text(target, encoding="utf-8")
    print(f"Header injected into {TARGET.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
