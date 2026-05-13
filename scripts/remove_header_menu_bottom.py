"""Remove the header's "menu-bottom" block from every page.

The header on every page contains a `<div class="menu-bottom">` that
wraps two promotional sections:

    • "FOLLOW US ON SOCIAL MEDIA!"  + 6 social-icon links
    • "DOWNLOAD THE AXIS APP!"     + App Store / Play Store buttons

The user asked for these links to be removed. Since stripping only the
<a> tags would leave orphan headings and icons hanging in the layout,
we remove the entire menu-bottom block in one clean cut.

We locate the opening `<div class="menu-bottom">` and then scan forward
counting <div / </div> occurrences to find its matching close. Then we
delete the whole inclusive range, including any blank lines that follow.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(".")

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

OPEN_RE = re.compile(r'<div\s+class="menu-bottom">')
OPEN_TAG_RE = re.compile(r"<div\b")
CLOSE_TAG_RE = re.compile(r"</div\s*>")


def find_close_line(lines: list[str], open_idx: int) -> int | None:
    """Return the line index of the </div> that closes the block opened
    on `open_idx`. We track every <div / </div> occurrence (substring-
    level) until depth returns to zero.
    """
    depth = 0
    for i in range(open_idx, len(lines)):
        line = lines[i]
        depth += len(OPEN_TAG_RE.findall(line))
        depth -= len(CLOSE_TAG_RE.findall(line))
        if depth == 0:
            return i
    return None


def scrub(path: Path) -> int:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)

    removals = 0
    i = 0
    out: list[str] = []
    while i < len(lines):
        if OPEN_RE.search(lines[i]):
            close_idx = find_close_line(lines, i)
            if close_idx is None:
                out.append(lines[i])
                i += 1
                continue
            # Skip the matched block. Also swallow any immediately
            # following blank lines so we don't leave a gap.
            i = close_idx + 1
            while i < len(lines) and lines[i].strip() == "":
                i += 1
            removals += 1
        else:
            out.append(lines[i])
            i += 1

    if removals == 0:
        return 0

    path.write_text("".join(out), encoding="utf-8")
    return removals


def main() -> None:
    total = 0
    for rel in TARGETS:
        path = ROOT / rel
        if not path.exists():
            print(f"SKIP  {rel}  (not found)")
            continue
        n = scrub(path)
        total += n
        flag = "OK   " if n else "(noop)"
        print(f"{flag} {rel}  blocks_removed={n}")

    print(f"\nTotal menu-bottom blocks removed: {total}")


if __name__ == "__main__":
    main()
