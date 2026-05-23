#!/usr/bin/env python3
"""Move AXIS LOCATIONS block on about page to just before </main>."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "aboutgymnearme" / "index.html"

WRAPPER_OPEN = '        <div class="">\n'
TITLE_LINE = '<h2 class="u-h1 u-text-center">AXIS LOCATIONS</h2>\n'
MAP_SECTION_TAG = "map-new-tab-section"


def find_section(lines: list[str]) -> tuple[int, int]:
    title_idx = next(
        (i for i, line in enumerate(lines) if line.strip() == TITLE_LINE.strip()),
        None,
    )
    if title_idx is None:
        raise SystemExit("AXIS LOCATIONS title not found.")

    start_idx = None
    for i in range(title_idx, -1, -1):
        if lines[i] == WRAPPER_OPEN:
            start_idx = i
            break
    if start_idx is None:
        raise SystemExit("Could not find LOCATIONS wrapper opener.")

    map_open_idx = next(
        (
            i
            for i in range(title_idx, len(lines))
            if "<section" in lines[i] and MAP_SECTION_TAG in lines[i]
        ),
        None,
    )
    if map_open_idx is None:
        raise SystemExit("Could not find map-new-tab-section opener.")

    depth = 0
    map_close_idx = None
    for i in range(map_open_idx, len(lines)):
        depth += lines[i].count("<section")
        depth -= lines[i].count("</section>")
        if depth == 0:
            map_close_idx = i
            break
    if map_close_idx is None:
        raise SystemExit("Could not find matching </section> for map section.")

    end_idx = next(
        (i for i in range(map_close_idx + 1, len(lines)) if lines[i] == WRAPPER_OPEN),
        None,
    )
    if end_idx is None:
        raise SystemExit("Could not find next-section wrapper opener.")

    return start_idx, end_idx


def main() -> None:
    lines = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)
    start, end = find_section(lines)
    block = lines[start:end]
    rest = lines[:start] + lines[end:]

    main_idx = next(i for i, line in enumerate(rest) if line.strip() == "</main>")
    new_lines = rest[:main_idx] + block + rest[main_idx:]
    TARGET.write_text("".join(new_lines), encoding="utf-8")
    print(f"Moved lines {start + 1}..{end} to before </main> (line {main_idx + 1})")


if __name__ == "__main__":
    main()
