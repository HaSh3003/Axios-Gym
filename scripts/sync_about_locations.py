"""Sync the "AXIS LOCATIONS" section of aboutgymnearme/index.html to
match the version on the home page (index.html).

The user simplified the home page's locations block (it now uses
.axis-single-map-embed which collapses the multi-country tabs down to a
single Google Maps embed). They want the about page to render the same
way.

How we identify the section in each file:
  • Start = the line "        <div class=\"\">" that immediately
    precedes the <section> wrapping <h2>AXIS LOCATIONS</h2>.
  • End   = exclusive — the next "        <div class=\"\">" wrapper
    that appears after the map's </section>. (That wrapper is the
    opener for whatever section follows the locations area.)

Because index.html lives at the project root and aboutgymnearme/ is one
level deeper, every relative `src="…"` / `href="…"` we copy across needs
a leading "../" so the assets resolve.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(".")
SOURCE = ROOT / "index.html"
TARGET = ROOT / "aboutgymnearme" / "index.html"

WRAPPER_OPEN = '        <div class="">\n'
TITLE_LINE = '<h2 class="u-h1 u-text-center">AXIS LOCATIONS</h2>\n'

# Path prefixes that mean "site root" and therefore need "../" prefixed
# when copied to a one-level-deeper file. We deliberately don't rewrite
# absolute URLs, fragment / mailto / tel / javascript schemes, or any
# value already starting with "../".
ROOT_PATH_PREFIXES = (
    "public/",
    "media/",
    "dist/",
    "components/",
    "favicon",
    "gymsnearme/",
    "fitness-classes/",
    "aboutgymnearme/",
    "gymsignup/",
    "blog/",
    "contact-gymnation/",
    "gymnationfaqs/",
    "privacy-policy/",
    "terms-conditions/",
    "press/",
    "jobs-at-gymnation/",
    "gymnationapp/",
    "gymnationondemand/",
    "gymnationpartners/",
    "gymnationclasstimetable/",
    "gymnationsignature/",
    "gymnation-member-rewards/",
    "refer/",
    "websitesearch/",
    "newsletter/",
    "fitness-hub/",
    "exercise-library/",
    "fitness-calculators/",
    "best-personal-trainers/",
    "ladies-gym/",
    "gym-equipment/",
    "facilities/",
    "hyroxperformancecenter/",
    "hyrox-classes/",
    "reformer-pilates/",
    "hiitworkout/",
    "yalla-chef/",
    "coming-soon/",
    "ar/",
    "index.html",
    "index",
)


MAP_SECTION_TAG = "map-new-tab-section"


def find_section(lines: list[str]) -> tuple[int, int]:
    """Return (start_idx, end_idx) — half-open — for the LOCATIONS block.

    Start = the wrapper opener immediately *preceding* the AXIS LOCATIONS
            title.
    End   = the wrapper opener that starts the *next* page section
            after the map area. To find it reliably we first locate the
            <section ...map-new-tab-section...> opener, then its
            matching </section>, then the wrapper opener after that.
    """
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

    # Walk forward counting <section>/</section> to find the matching close.
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


_ATTR_RE = re.compile(r'(\s(?:src|href)\s*=\s*")([^"]+)(")')


def prefix_path(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith(("http://", "https://", "//", "#", "mailto:", "tel:", "javascript:", "data:")):
        return value
    if stripped.startswith("../") or stripped.startswith("./") or stripped.startswith("/"):
        return value
    for prefix in ROOT_PATH_PREFIXES:
        if stripped.startswith(prefix):
            return "../" + value
    return value


def adjust_paths(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        return f"{m.group(1)}{prefix_path(m.group(2))}{m.group(3)}"

    return _ATTR_RE.sub(repl, text)


def main() -> None:
    src_lines = SOURCE.read_text(encoding="utf-8").splitlines(keepends=True)
    dst_lines = TARGET.read_text(encoding="utf-8").splitlines(keepends=True)

    src_start, src_end = find_section(src_lines)
    dst_start, dst_end = find_section(dst_lines)

    new_section_raw = "".join(src_lines[src_start:src_end])
    new_section = adjust_paths(new_section_raw)

    rewritten = (
        "".join(dst_lines[:dst_start]) + new_section + "".join(dst_lines[dst_end:])
    )
    TARGET.write_text(rewritten, encoding="utf-8")

    print(f"Source lines  : {src_start + 1}..{src_end} ({src_end - src_start} lines)")
    print(f"Target lines  : {dst_start + 1}..{dst_end} ({dst_end - dst_start} lines) — replaced")
    print(f"New file size : {len(rewritten)} chars")


if __name__ == "__main__":
    main()
