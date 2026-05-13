"""Disable all social-media / external-platform links site-wide.

The user wants social-media links present visually but non-functional:
the markup stays so the icons / labels still render, but clicking
does nothing.

What we target (case-insensitive on the URL scheme/domain):
  • facebook.com         (follow links)
  • instagram.com        (follow links)
  • tiktok.com           (follow links)
  • x.com / twitter.com  (follow links)
  • youtube.com / youtu.be (follow / video links)
  • apps.apple.com       (App Store)
  • play.google.com      (Google Play)
  • linkedin.com         (just in case)

For every <a ...> tag whose href points at one of those domains we:
  • replace href with "javascript:void(0);"
  • drop the target="_blank" attribute
  • drop the rel="..." attribute (now redundant)
  • add aria-disabled="true"
  • add a sentinel data attribute (data-link-disabled="1") so the script
    is idempotent — already-disabled anchors are skipped.

Other attributes (class, title, alt, etc.) are preserved verbatim and
the inner HTML (icons / text) is untouched.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(".")

SOCIAL_HOST_RE = re.compile(
    r"^https?://(?:www\.)?(?:"
    r"facebook\.com|instagram\.com|tiktok\.com|"
    r"x\.com|twitter\.com|"
    r"youtube\.com|youtu\.be|"
    r"apps\.apple\.com|play\.google\.com|"
    r"linkedin\.com"
    r")/",
    re.IGNORECASE,
)

ANCHOR_RE = re.compile(r"<a\b([^>]*)>", re.IGNORECASE)
ATTR_RE = re.compile(r"""([A-Za-z_:][-A-Za-z0-9_:.]*)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""")
ATTRS_TO_DROP = {"target", "rel"}


def parse_attrs(tag_inner: str) -> list[tuple[str, str, str | None]]:
    """Return [(attr_name, value, quote_char)] preserving order.

    Boolean attributes (no `=`) appear as (name, "", None).
    """
    pos = 0
    out: list[tuple[str, str, str | None]] = []
    while pos < len(tag_inner):
        m = re.match(r"\s+", tag_inner[pos:])
        if m:
            pos += m.end()
            if pos >= len(tag_inner):
                break
        m = ATTR_RE.match(tag_inner, pos)
        if m:
            name = m.group(1)
            if m.group(2) is not None:
                out.append((name, m.group(2), '"'))
            elif m.group(3) is not None:
                out.append((name, m.group(3), "'"))
            else:
                out.append((name, m.group(4), None))
            pos = m.end()
            continue
        m = re.match(r"([A-Za-z_:][-A-Za-z0-9_:.]*)", tag_inner[pos:])
        if m:
            out.append((m.group(1), "", None))
            pos += m.end()
            continue
        # Unknown character; skip 1 to avoid infinite loop.
        pos += 1
    return out


def rebuild_tag(attrs: list[tuple[str, str, str | None]]) -> str:
    parts = ["<a"]
    for name, value, quote in attrs:
        if quote is None and value == "":
            parts.append(f" {name}")
        else:
            q = quote or '"'
            parts.append(f' {name}={q}{value}{q}')
    parts.append(">")
    return "".join(parts)


def disable_anchor(match: re.Match[str], state: dict[str, int]) -> str:
    tag_inner = match.group(1)
    attrs = parse_attrs(tag_inner)

    href = next((v for n, v, _ in attrs if n.lower() == "href"), None)
    if href is None or not SOCIAL_HOST_RE.match(href.strip()):
        return match.group(0)

    # Idempotency
    if any(n.lower() == "data-link-disabled" for n, _, _ in attrs):
        return match.group(0)

    new_attrs: list[tuple[str, str, str | None]] = []
    seen_aria = False
    for name, value, quote in attrs:
        lname = name.lower()
        if lname in ATTRS_TO_DROP:
            continue
        if lname == "href":
            new_attrs.append((name, "javascript:void(0);", '"'))
            continue
        if lname == "aria-disabled":
            new_attrs.append((name, "true", '"'))
            seen_aria = True
            continue
        new_attrs.append((name, value, quote))

    if not seen_aria:
        new_attrs.append(("aria-disabled", "true", '"'))
    new_attrs.append(("data-link-disabled", "1", '"'))

    state["count"] += 1
    return rebuild_tag(new_attrs)


def process(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    state = {"count": 0}
    new_text = ANCHOR_RE.sub(lambda m: disable_anchor(m, state), text)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return state["count"]


def main() -> None:
    html_files = [p for p in ROOT.rglob("*.html") if "node_modules" not in p.parts]
    total = 0
    changed = 0
    for path in sorted(html_files):
        count = process(path)
        if count:
            changed += 1
            total += count
            print(f"  {count:4d}  {path}")
    print(f"\nDisabled {total} anchors across {changed} files "
          f"(scanned {len(html_files)} files).")


if __name__ == "__main__":
    main()
