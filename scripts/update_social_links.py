#!/usr/bin/env python3
"""Keep only Instagram + TikTok in FOLLOW US ON SOCIAL MEDIA blocks."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTAGRAM = "https://www.instagram.com/axis.spor/"
TIKTOK = "https://www.tiktok.com/@axis.sport"

SOCIAL_UL_RE = re.compile(
    r"(<ul class=\"social-media-group\">).*?(</ul>\s*(?=<h3\s*>DOWNLOAD THE))",
    re.DOTALL,
)


def media_prefix(html_path: Path) -> str:
    rel_dir = html_path.parent.relative_to(ROOT)
    if rel_dir == Path("."):
        return ""
    return "../" * len(rel_dir.parts)


def build_ul(prefix: str) -> str:
    return f"""<ul class="social-media-group">
                                <li class="social-media-box">
                                    <a href="{INSTAGRAM}" title="Instagram" target="_blank" rel="noopener noreferrer">
                                        <img  alt="Instagram White" class="img-primary"src="{prefix}media/3l5njzqw/instagram-white.svg" loading="lazy" decoding="async"  width="50" height="91">
                                        <img  alt="Instagram" class="img-hover"src="{prefix}media/lgak4dcl/instagram.webp" loading="lazy" decoding="async"  width="50" height="91">
                                    </a>
                                </li>
                                <li class="social-media-box">
                                    <a href="{TIKTOK}" title="TikTok" target="_blank" rel="noopener noreferrer">
                                        <img  alt="Tiktok White" class="img-primary"src="{prefix}media/gpwbxzof/tiktok-white.svg" loading="lazy" decoding="async"  width="50" height="91">
                                        <img  alt="TikTok" class="img-hover"src="{prefix}media/jp1pepof/ticktok.webp" loading="lazy" decoding="async"  width="50" height="91">
                                    </a>
                                </li>
                        </ul>
                    """


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "FOLLOW US ON SOCIAL MEDIA!" not in text:
        return False
    prefix = media_prefix(path)

    def repl(_match: re.Match[str]) -> str:
        return build_ul(prefix) + "\n                    "

    updated, n = SOCIAL_UL_RE.subn(repl, text, count=1)
    if n == 0 or updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    changed = []
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts:
            continue
        if patch_file(path):
            changed.append(path.relative_to(ROOT))
    print(f"Updated {len(changed)} file(s):")
    for p in changed:
        print(f"  - {p}")


if __name__ == "__main__":
    main()
