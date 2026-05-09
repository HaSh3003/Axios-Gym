#!/usr/bin/env python3
"""Embed shared header/footer HTML into each page with correct relative URLs; remove site-layout.js."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
HEADER_PATH = ROOT / "components" / "site-header.html"
FOOTER_PATH = ROOT / "components" / "site-footer.html"


def rewrite_url_attr(val: str, page_dir: Path, site_root: Path) -> str:
    if not val or not str(val).strip():
        return val
    s = str(val).strip()
    if s.startswith(("#",)) and "/" not in s.split("#", 1)[0]:
        return val
    if s.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "data:", "//")):
        return val
    if s.startswith("/") and not s.startswith("//"):
        return val

    base = s
    hash_suffix = ""
    if "#" in base:
        base, h = base.split("#", 1)
        hash_suffix = "#" + h
    query_suffix = ""
    if "?" in base:
        base, q = base.split("?", 1)
        query_suffix = "?" + q
    if not base:
        return val

    try:
        target = (site_root / base).resolve()
        rel = os.path.relpath(target, page_dir.resolve())
    except (ValueError, OSError):
        return val
    rel = rel.replace("\\", "/")
    return rel + query_suffix + hash_suffix


def rewrite_srcset(val: str, page_dir: Path, site_root: Path) -> str:
    parts = []
    for chunk in val.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        sp = chunk.find(" ")
        if sp == -1:
            url, desc = chunk, ""
        else:
            url, desc = chunk[:sp].strip(), chunk[sp:]
        parts.append(rewrite_url_attr(url, page_dir, site_root) + desc)
    return ", ".join(parts)


def rewrite_fragment(html: str, page_dir: Path, site_root: Path) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(True):
        for attr in ("href", "src", "poster"):
            if tag.has_attr(attr):
                tag[attr] = rewrite_url_attr(tag[attr], page_dir, site_root)
        if tag.has_attr("srcset"):
            tag["srcset"] = rewrite_srcset(tag["srcset"], page_dir, site_root)
        if tag.has_attr("onclick"):
            oc = tag["onclick"]

            def desk(m: re.Match) -> str:
                q = m.group(1)
                inner = m.group(2)
                return f"desktopsearch({q}{rewrite_url_attr(inner, page_dir, site_root)}{q})"

            def mob(m: re.Match) -> str:
                q = m.group(1)
                inner = m.group(2)
                return f"mobilesearch({q}{rewrite_url_attr(inner, page_dir, site_root)}{q})"

            oc = re.sub(r"desktopsearch\(\s*(['\"])([^'\"]*)\1\s*\)", desk, oc)
            oc = re.sub(r"mobilesearch\(\s*(['\"])([^'\"]*)\1\s*\)", mob, oc)
            tag["onclick"] = oc

    return "".join(str(c) for c in soup.contents)


def strip_site_layout_scripts(html: str) -> str:
    html = re.sub(
        r'\s*<script\s+src="(?:\.\./)*components/site-layout\.js"(?:\s+defer)?></script>\s*',
        "\n",
        html,
        flags=re.IGNORECASE,
    )
    return html


HEADER_BLOCK_RE = re.compile(
    r"<!--\s*axis-layout:\s*header\s+mount\s*-->\s*"
    r'<div\s+id="axis-site-header"[^>]*></div>\s*'
    r'(?:<script\s+src="[^"]*components/site-layout\.js"[^>]*></script>\s*)?',
    re.IGNORECASE | re.DOTALL,
)

FOOTER_BLOCK_RE = re.compile(
    r"<!--\s*axis-layout:\s*footer\s+mount\s*-->\s*"
    r'<div\s+id="axis-site-footer"[^>]*></div>\s*',
    re.IGNORECASE | re.DOTALL,
)

HEADER_INLINE_RE = re.compile(
    r'<header class="btn-align-right">.*?</header>',
    re.DOTALL | re.IGNORECASE,
)
FOOTER_INLINE_RE = re.compile(
    r'<footer class="footer-scroll-js">.*?</footer>',
    re.DOTALL | re.IGNORECASE,
)


def merge_inline_header_footer(path: Path, header_raw: str, footer_raw: str, add_branding_css: bool = True) -> tuple[bool, list[str]]:
    """Swap existing <header>/<footer> blocks for rewritten components. Leaves all other HTML/CSS/JS unchanged."""
    msgs: list[str] = []
    page_dir = path.parent
    text = path.read_text(encoding="utf-8", errors="replace")
    orig = text

    frag_h = rewrite_fragment(header_raw, page_dir, ROOT).strip()
    text, nh = HEADER_INLINE_RE.subn(frag_h + "\n", text, count=1)
    if nh != 1:
        msgs.append(f"header replace count={nh}")

    frag_f = rewrite_fragment(footer_raw, page_dir, ROOT).strip()
    text, nf = FOOTER_INLINE_RE.subn(frag_f + "\n", text, count=1)
    if nf != 1:
        msgs.append(f"footer replace count={nf}")

    if add_branding_css and "axis-branding.css" not in text:
        link_line = (
            f'        <link id="axis-branding-css" rel="stylesheet" '
            f'href="{os.path.relpath(ROOT / "components" / "axis-branding.css", page_dir).replace(chr(92), "/")}" />\n'
        )
        inserted = False
        for needle in (
            'client-stylesef75.css?v=sgie15IPAOBT2CKW4MKUJ67yc04ju47HY7wOjFqlPlE" />',
            'lagecy-clientc5bb.css?v=J82jFTiBvCwYrUK7svGniqA0Rsm8l6xnGvdPtzWzAf0" />',
        ):
            if needle in text:
                text = text.replace(needle, needle + "\n" + link_line, 1)
                inserted = True
                break
        if not inserted and "</head>" in text:
            text = text.replace("</head>", link_line + "</head>", 1)
            inserted = True
        if not inserted:
            msgs.append("could not insert axis-branding.css")

    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True, msgs
    return False, msgs


def main() -> int:
    parser = argparse.ArgumentParser(description="Inline shared layout fragments.")
    parser.add_argument(
        "--merge-inline",
        nargs="+",
        metavar="REL_PATH",
        help="Replace inline <header>/<footer> with components only (keeps page CSS/JS). Paths relative to repo root.",
    )
    args = parser.parse_args()

    header_raw = HEADER_PATH.read_text(encoding="utf-8", errors="replace")
    footer_raw = FOOTER_PATH.read_text(encoding="utf-8", errors="replace")

    if args.merge_inline:
        ok_any = False
        for rel in args.merge_inline:
            path = (ROOT / rel).resolve()
            if not path.is_file():
                print("MISSING", rel, file=sys.stderr)
                continue
            changed, msgs = merge_inline_header_footer(path, header_raw, footer_raw)
            print(rel, "changed=" + str(changed), *msgs)
            ok_any = ok_any or changed
        return 0 if ok_any else 1

    updated = 0
    for path in sorted(ROOT.rglob("index.html")):
        if "components" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "axis-site-header" not in text and "axis-site-footer" not in text:
            continue

        page_dir = path.parent
        new_text = text

        if "axis-site-header" in new_text:
            frag = rewrite_fragment(header_raw, page_dir, ROOT)
            new_text, n_h = HEADER_BLOCK_RE.subn(frag.strip() + "\n", new_text, count=1)
            if n_h != 1:
                print("WARN header replace failed:", path.relative_to(ROOT), file=sys.stderr)

        if "axis-site-footer" in new_text:
            frag_f = rewrite_fragment(footer_raw, page_dir, ROOT)
            new_text, n_f = FOOTER_BLOCK_RE.subn(frag_f.strip() + "\n", new_text, count=1)
            if n_f != 1:
                print("WARN footer replace failed:", path.relative_to(ROOT), file=sys.stderr)

        new_text = strip_site_layout_scripts(new_text)

        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            updated += 1

    print("updated_files", updated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
