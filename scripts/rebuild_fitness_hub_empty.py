"""Rebuild fitness-hub/index.html into a stylish empty-state page.

The page currently shows the FITNESS HUB hero followed by a long intro
paragraph + 9 card links (Personal Trainers, Exercise Library, Yalla
Chef, etc.). The user wants:

  • All those links removed (commented out, not deleted) — including
    the inline intro links.
  • A clean, modern English message saying nothing is available right
    now in their place.
  • No visible "GymNation" mentions anywhere — also scrubbed from the
    commented-out markup so that a future "uncomment" doesn't bring
    them back.

We keep the FITNESS HUB hero exactly as it is, inject a new empty-state
<div class=""> section right after it, and wrap everything else inside
the original umb-block-list in an HTML comment.
"""

from __future__ import annotations

import re
from pathlib import Path

TARGET = Path("fitness-hub/index.html")

# Sentinel lines that delimit the area we're rewriting. We keep the
# hero ABOVE these and the closing </div>'s + </main> BELOW.
HERO_CLOSE_LINE = "        </div>\n"  # the </div> that closes the hero wrapper
INTRO_OPEN_LINE = '        <div class="">\n'  # the wrapper that starts the intro section
UMB_CLOSE_FRAGMENT = "    </div>\n</div>\n\n</div>\n            </main>\n"


REPLACEMENT_BLOCK = """\
        <div class="ax-fh-empty-wrapper">
            <style>
                .ax-fh-empty {
                    font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: radial-gradient(120% 100% at 50% 0%, #ffffff 0%, #f5f5f7 60%, #ececef 100%);
                    padding: clamp(70px, 10vw, 130px) 24px;
                    text-align: center;
                    color: #111;
                    position: relative;
                    overflow: hidden;
                }
                .ax-fh-empty::before,
                .ax-fh-empty::after {
                    content: '';
                    position: absolute;
                    border-radius: 50%;
                    pointer-events: none;
                    z-index: 0;
                }
                .ax-fh-empty::before {
                    top: -120px; right: -120px;
                    width: 320px; height: 320px;
                    background: radial-gradient(closest-side, rgba(209,43,47,.10), rgba(209,43,47,0));
                }
                .ax-fh-empty::after {
                    bottom: -160px; left: -100px;
                    width: 380px; height: 380px;
                    background: radial-gradient(closest-side, rgba(0,0,0,.06), rgba(0,0,0,0));
                }
                .ax-fh-empty__inner {
                    position: relative;
                    z-index: 1;
                    max-width: 640px;
                    margin: 0 auto;
                }
                .ax-fh-empty__chip {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 11px;
                    font-weight: 800;
                    letter-spacing: 0.16em;
                    text-transform: uppercase;
                    background: #fde8e9;
                    color: #d12b2f;
                    padding: 8px 16px;
                    border-radius: 999px;
                    margin-bottom: 28px;
                }
                .ax-fh-empty__chip-dot {
                    width: 7px; height: 7px;
                    border-radius: 50%;
                    background: #d12b2f;
                    box-shadow: 0 0 0 4px rgba(209,43,47,.18);
                    animation: ax-pulse 1.6s ease-in-out infinite;
                }
                @keyframes ax-pulse {
                    0%, 100% { transform: scale(1); opacity: 1; }
                    50%      { transform: scale(1.3); opacity: .55; }
                }
                .ax-fh-empty__icon {
                    width: 110px;
                    height: 110px;
                    margin: 0 auto 28px;
                    display: block;
                }
                .ax-fh-empty__title {
                    font-size: clamp(32px, 4.5vw, 52px);
                    font-weight: 800;
                    line-height: 1.05;
                    letter-spacing: -0.025em;
                    color: #0d0d0d;
                    margin: 0 0 16px;
                }
                .ax-fh-empty__accent { color: #d12b2f; }
                .ax-fh-empty__lead {
                    font-size: clamp(15px, 1.5vw, 18px);
                    line-height: 1.7;
                    color: #555;
                    margin: 0 0 32px;
                }
                .ax-fh-empty__divider {
                    width: 80px;
                    height: 4px;
                    background: #d12b2f;
                    border-radius: 4px;
                    margin: 0 auto 26px;
                }
                .ax-fh-empty__meta {
                    font-size: 12px;
                    font-weight: 700;
                    letter-spacing: 0.18em;
                    text-transform: uppercase;
                    color: #888;
                }
                .ax-fh-empty__meta span {
                    color: #d12b2f;
                }
            </style>

            <section class="ax-fh-empty" aria-labelledby="ax-fh-empty-title">
                <div class="ax-fh-empty__inner">
                    <span class="ax-fh-empty__chip">
                        <span class="ax-fh-empty__chip-dot"></span>
                        In Progress
                    </span>

                    <svg class="ax-fh-empty__icon" viewBox="0 0 110 110" fill="none" aria-hidden="true">
                        <circle cx="55" cy="55" r="52" stroke="#d12b2f" stroke-width="3" stroke-dasharray="5 7" opacity=".35"/>
                        <path d="M40 36h30M40 74h30" stroke="#d12b2f" stroke-width="4" stroke-linecap="round"/>
                        <path d="M42 38l2 12c.7 4.2 3.4 7.8 7 10l4 2.5 4-2.5c3.6-2.2 6.3-5.8 7-10l2-12" stroke="#0d0d0d" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M42 72l2-12c.7-4.2 3.4-7.8 7-10l4-2.5 4 2.5c3.6 2.2 6.3 5.8 7 10l2 12" stroke="#0d0d0d" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle cx="55" cy="55" r="3" fill="#d12b2f"/>
                    </svg>

                    <h1 id="ax-fh-empty-title" class="ax-fh-empty__title">
                        Nothing Here <span class="ax-fh-empty__accent">Just Yet</span>
                    </h1>
                    <p class="ax-fh-empty__lead">
                        We're putting the finishing touches on the new AXIS Fitness Hub.
                        Personal trainers, workout guides, fitness calculators and more are
                        on their way &mdash; check back with us soon.
                    </p>

                    <div class="ax-fh-empty__divider"></div>
                    <p class="ax-fh-empty__meta">AXIS &middot; <span>Coming Soon</span></p>
                </div>
            </section>
        </div>
"""


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    # 1. Find the index of </main> and the line of the hero's closing wrapper.
    main_close_idx = next(
        (i for i, line in enumerate(lines) if line.strip() == "</main>"),
        None,
    )
    if main_close_idx is None:
        raise SystemExit("Could not find </main>.")

    # The hero is the first <div class=""> block inside <main>. Its
    # closing </div> is the one right before the second <div class="">.
    main_open_idx = next(
        (i for i, line in enumerate(lines) if line.strip() == "<main>"),
        None,
    )
    if main_open_idx is None:
        raise SystemExit("Could not find <main>.")

    # Find the FIRST <div class=""> inside main (hero opener) and then
    # the SECOND <div class=""> inside main (intro opener) — and the
    # line right before the second is the hero's </div>.
    wrapper_indices = [
        i
        for i in range(main_open_idx, main_close_idx)
        if lines[i] == INTRO_OPEN_LINE
    ]
    if len(wrapper_indices) < 2:
        raise SystemExit("Expected at least two <div class=\"\"> wrappers under <main>.")

    hero_close_idx = wrapper_indices[1] - 1
    intro_open_idx = wrapper_indices[1]

    # 2. Capture the everything-after-hero block (the intro + cards),
    # which lives between intro_open_idx and the closing </div></div>
    # combination just above </main>. We anchor on the
    # UMB_CLOSE_FRAGMENT — find the index where it begins.
    suffix = "".join(lines[intro_open_idx:])
    idx_in_suffix = suffix.find(UMB_CLOSE_FRAGMENT)
    if idx_in_suffix == -1:
        raise SystemExit("Could not find umb-block-list closing fragment.")

    body_to_comment = suffix[:idx_in_suffix]
    tail = suffix[idx_in_suffix:]

    # 3. Sanitize the body we're commenting out so any future
    # un-commenting doesn't surface GymNation again. We do this with a
    # small case-aware replacement (skipping URL/path tokens).
    body_to_comment = _strip_gymnation(body_to_comment)

    # 4. Make sure the commented block doesn't contain "--" sequences,
    # which would break the HTML comment. (None expected, but cheap to
    # neutralise: replace "--" with "- -".)
    safe_body = body_to_comment.replace("--", "- -")

    commented = (
        "        <!-- BEGIN ORIGINAL FITNESS HUB CONTENT (links disabled) -->\n"
        "        <!--\n"
        f"{safe_body}"
        "        -->\n"
        "        <!-- END ORIGINAL FITNESS HUB CONTENT -->\n"
    )

    rewritten = (
        "".join(lines[: hero_close_idx + 1])
        + REPLACEMENT_BLOCK
        + commented
        + tail
    )

    # Also scrub GymNation mentions across the rest of the file (head
    # meta tags, JSON-LD, etc.) so the browser tab title and SEO data
    # reflect the new brand. URL/path tokens are preserved.
    rewritten = _strip_gymnation(rewritten)

    TARGET.write_text(rewritten, encoding="utf-8")

    print(f"Hero kept through line     : {hero_close_idx + 1}")
    print(f"Original content lines     : {intro_open_idx + 1}..{intro_open_idx + body_to_comment.count(chr(10))} (commented)")
    print(f"New empty-state inserted   : after line {hero_close_idx + 1}")
    print(f"New file size              : {len(rewritten)} chars")


# Tiny GymNation -> Axis stripper that leaves URL/path tokens alone.
# Same idea (much simpler scope) as scripts/rebrand_about_page.py.
_PROTECT_PATTERNS = [
    r"gymnation\.com",
    r"gymnation/id\d+",
    r"com\.netpulse\.mobile\.gymnation",
    r"gymnation-[a-z0-9-]+\.(?:webp|png|jpg|jpeg|svg|gif)",
    r"gymnation_me\b",
    r"gymnationme\b",
    r"\.\./gymnation[a-z0-9-]*/",
    r"\.\./[a-z0-9-]+-gymnation/",
    r"/media/[^\"'<>\s]*gymnation[^\"'<>\s]*",
]


def _strip_gymnation(text: str) -> str:
    placeholders: dict[str, str] = {}
    counter = [0]

    def stash(m: re.Match[str]) -> str:
        counter[0] += 1
        key = f"\x00GN_FH_{counter[0]}\x00"
        placeholders[key] = m.group(0)
        return key

    for pattern in _PROTECT_PATTERNS:
        text = re.sub(pattern, stash, text, flags=re.IGNORECASE)

    def case_aware(m: re.Match[str]) -> str:
        word = m.group(0)
        if word.isupper():
            return "AXIS"
        if word.islower():
            return "axis"
        return "Axis"

    text = re.sub(r"gymnation", case_aware, text, flags=re.IGNORECASE)

    for key, value in placeholders.items():
        text = text.replace(key, value)

    return text


if __name__ == "__main__":
    main()
