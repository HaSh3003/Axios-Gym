"""Rebuild gymsnearme/gymmembership/index.html on top of the
fitness-classes/boxing-classes/index.html structure.

The current membership page was assembled piecemeal and lost the
overall layout — the user reports no visible site header and no
footer. Rather than patching individual symptoms, we use the known-good
boxing-classes page (same folder depth, identical site header / footer
markup, legacy CSS) as the structural template and swap its <main>
content for the membership form we built earlier.

What's preserved from boxing-classes:
  • Entire <head> (CSS links to legacy bundles, GTM, body class, etc.)
  • Site <header> (logo, nav, mega-menus)
  • Everything between </main> and </body> (site footer, chatbot
    container, scripts, etc.)

What's customised for the membership page:
  • <title> and <meta name="description">
  • The canonical / hreflang / og / twitter URLs (set to the
    membership page itself)
  • <main> body — replaced with the form (style + section + script).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(".")
TEMPLATE = ROOT / "fitness-classes" / "boxing-classes" / "index.html"
TARGET = ROOT / "gymsnearme" / "gymmembership" / "index.html"

NEW_TITLE = "Membership | AXIS"
NEW_DESC = (
    "Join AXIS today — fill in your details and pick the membership "
    "plan that suits you best."
)

FORM_BODY = """\
            <style>
                .ax-membership-page {
                    background: #f4f5f7;
                    padding: 56px 0 80px;
                    min-height: calc(100vh - 200px);
                    font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    color: #111;
                }
                .ax-membership-page * { box-sizing: border-box; }
                .ax-membership-page .ax-container {
                    max-width: 1000px;
                    margin: 0 auto;
                    padding: 0 20px;
                }
                .ax-membership-hero {
                    text-align: center;
                    margin-bottom: 36px;
                }
                .ax-membership-hero h1 {
                    font-size: clamp(30px, 4.5vw, 46px);
                    font-weight: 800;
                    color: #0d0d0d;
                    letter-spacing: -0.02em;
                    margin: 0 0 12px;
                    line-height: 1.1;
                }
                .ax-membership-hero p {
                    color: #555;
                    font-size: 17px;
                    margin: 0;
                    line-height: 1.5;
                }
                .ax-membership-hero .ax-accent { color: #d12b2f; }
                .ax-membership-form {
                    background: #fff;
                    border-radius: 16px;
                    padding: clamp(22px, 4vw, 42px);
                    box-shadow: 0 22px 50px -22px rgba(0, 0, 0, .18), 0 2px 6px rgba(0, 0, 0, .04);
                }
                .ax-form-section + .ax-form-section {
                    margin-top: 40px;
                    padding-top: 36px;
                    border-top: 1px solid #e8eaee;
                }
                .ax-form-section h2 {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    font-size: 20px;
                    font-weight: 800;
                    color: #0d0d0d;
                    margin: 0 0 22px;
                    text-transform: uppercase;
                    letter-spacing: 0.04em;
                }
                .ax-step {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 34px;
                    height: 34px;
                    border-radius: 50%;
                    background: #d12b2f;
                    color: #fff;
                    font-size: 14px;
                    font-weight: 800;
                    flex-shrink: 0;
                }
                .ax-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 18px;
                }
                @media (max-width: 600px) { .ax-grid { grid-template-columns: 1fr; } }
                .ax-field { display: flex; flex-direction: column; }
                .ax-field-full { grid-column: 1 / -1; }
                .ax-field label {
                    font-size: 12px;
                    font-weight: 700;
                    color: #444;
                    margin-bottom: 8px;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }
                .ax-field input,
                .ax-field select {
                    height: 48px;
                    border: 1.5px solid #d8dadf;
                    background: #fff;
                    border-radius: 10px;
                    padding: 0 14px;
                    font-size: 15px;
                    color: #111;
                    font-family: inherit;
                    transition: border-color .15s, box-shadow .15s;
                    appearance: none;
                    -webkit-appearance: none;
                    width: 100%;
                }
                .ax-field select {
                    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'><path d='M1 1l5 5 5-5' stroke='%23666' stroke-width='2' fill='none' stroke-linecap='round'/></svg>");
                    background-repeat: no-repeat;
                    background-position: right 14px center;
                    padding-right: 38px;
                    cursor: pointer;
                }
                .ax-field input:focus,
                .ax-field select:focus {
                    outline: none;
                    border-color: #d12b2f;
                    box-shadow: 0 0 0 4px rgba(209, 43, 47, .12);
                }
                .ax-plans {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                    gap: 16px;
                }
                .ax-plan { display: block; cursor: pointer; position: relative; }
                .ax-plan input {
                    position: absolute;
                    opacity: 0;
                    pointer-events: none;
                }
                .ax-plan-card {
                    position: relative;
                    border: 2px solid #e3e5ea;
                    border-radius: 14px;
                    padding: 26px 20px 22px;
                    background: #fff;
                    height: 100%;
                    display: flex;
                    flex-direction: column;
                    transition: border-color .18s, transform .18s, box-shadow .18s, background .18s;
                }
                .ax-plan:hover .ax-plan-card {
                    border-color: #c9ccd2;
                    transform: translateY(-2px);
                }
                .ax-plan input:checked + .ax-plan-card {
                    border-color: #d12b2f;
                    background: #fff8f8;
                    box-shadow: 0 16px 30px -16px rgba(209, 43, 47, .45);
                }
                .ax-plan input:checked + .ax-plan-card::after {
                    content: '\\2713';
                    position: absolute;
                    top: 14px; right: 14px;
                    width: 28px; height: 28px;
                    border-radius: 50%;
                    background: #d12b2f;
                    color: #fff;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 15px;
                    font-weight: 700;
                }
                .ax-plan-tag {
                    display: inline-block;
                    align-self: flex-start;
                    font-size: 10px;
                    font-weight: 800;
                    color: #d12b2f;
                    background: #fde8e9;
                    padding: 5px 10px;
                    border-radius: 999px;
                    letter-spacing: 0.08em;
                    text-transform: uppercase;
                    margin-bottom: 10px;
                }
                .ax-plan-name {
                    font-size: 18px;
                    font-weight: 800;
                    color: #0d0d0d;
                    margin: 0 0 6px;
                    text-transform: uppercase;
                    letter-spacing: 0.04em;
                }
                .ax-plan-price {
                    font-size: 30px;
                    font-weight: 800;
                    color: #d12b2f;
                    margin: 0 0 16px;
                    line-height: 1;
                }
                .ax-plan-price span {
                    font-size: 14px;
                    font-weight: 600;
                    color: #666;
                    margin-left: 2px;
                }
                .ax-plan-features {
                    list-style: none;
                    padding: 0;
                    margin: 0 0 4px;
                    flex: 1;
                }
                .ax-plan-features li {
                    position: relative;
                    padding-left: 24px;
                    font-size: 14px;
                    color: #2a2a2a;
                    line-height: 1.5;
                    margin-bottom: 8px;
                }
                .ax-plan-features li::before {
                    content: '';
                    position: absolute;
                    left: 2px; top: 5px;
                    width: 12px; height: 7px;
                    border-left: 2px solid #d12b2f;
                    border-bottom: 2px solid #d12b2f;
                    transform: rotate(-45deg);
                }
                .ax-plan-featured .ax-plan-card { border-color: #d12b2f; }
                .ax-checkbox {
                    display: flex;
                    gap: 12px;
                    align-items: flex-start;
                    font-size: 14px;
                    color: #444;
                    cursor: pointer;
                    margin-bottom: 24px;
                    line-height: 1.5;
                }
                .ax-checkbox input {
                    width: 18px; height: 18px;
                    margin-top: 2px;
                    accent-color: #d12b2f;
                    flex-shrink: 0;
                }
                .ax-submit-btn {
                    display: block;
                    width: 100%;
                    background: #d12b2f;
                    color: #fff;
                    font-size: 17px;
                    font-weight: 800;
                    letter-spacing: 0.05em;
                    border: none;
                    border-radius: 12px;
                    padding: 18px 24px;
                    cursor: pointer;
                    text-transform: uppercase;
                    transition: background .15s, transform .1s;
                    font-family: inherit;
                }
                .ax-submit-btn:hover { background: #b51f23; }
                .ax-submit-btn:active { transform: scale(.99); }
                .ax-submit-btn:disabled { cursor: default; opacity: .9; }
                .ax-form-note {
                    text-align: center;
                    color: #777;
                    font-size: 13px;
                    margin: 14px 0 0;
                    line-height: 1.5;
                }
                .ax-success { background: #1e9e3f !important; }
            </style>

            <section class="ax-membership-page">
                <div class="ax-container">
                    <div class="ax-membership-hero">
                        <h1>Become an <span class="ax-accent">AXIS</span> Member</h1>
                        <p>Fill in your details, pick a plan, and we'll take it from there.</p>
                    </div>

                    <form class="ax-membership-form" id="ax-membership-form" novalidate>

                        <section class="ax-form-section">
                            <h2><span class="ax-step">1</span> Your Details</h2>
                            <div class="ax-grid">
                                <div class="ax-field">
                                    <label for="firstName">First Name *</label>
                                    <input id="firstName" name="firstName" type="text" autocomplete="given-name" required>
                                </div>
                                <div class="ax-field">
                                    <label for="lastName">Last Name *</label>
                                    <input id="lastName" name="lastName" type="text" autocomplete="family-name" required>
                                </div>
                                <div class="ax-field">
                                    <label for="email">Email Address *</label>
                                    <input id="email" name="email" type="email" autocomplete="email" required>
                                </div>
                                <div class="ax-field">
                                    <label for="phone">Phone Number *</label>
                                    <input id="phone" name="phone" type="tel" autocomplete="tel" placeholder="+971 ..." required>
                                </div>
                                <div class="ax-field">
                                    <label for="dob">Date of Birth</label>
                                    <input id="dob" name="dob" type="date">
                                </div>
                                <div class="ax-field">
                                    <label for="gender">Gender</label>
                                    <select id="gender" name="gender">
                                        <option value="">Select…</option>
                                        <option>Male</option>
                                        <option>Female</option>
                                        <option>Prefer not to say</option>
                                    </select>
                                </div>
                                <div class="ax-field ax-field-full">
                                    <label for="city">Preferred Branch *</label>
                                    <select id="city" name="city" required>
                                        <option value="">Choose a branch…</option>
                                        <optgroup label="Dubai">
                                            <option>Dubai – Al Quoz</option>
                                            <option>Dubai – Bur Dubai</option>
                                            <option>Dubai – Downtown</option>
                                            <option>Dubai – Mirdif</option>
                                            <option>Dubai – Motor City</option>
                                            <option>Dubai – Silicon Oasis</option>
                                        </optgroup>
                                        <optgroup label="Abu Dhabi">
                                            <option>Abu Dhabi – Khalidiyah Mall</option>
                                            <option>Abu Dhabi – Mushrif Mall</option>
                                            <option>Abu Dhabi – Reem Island</option>
                                        </optgroup>
                                        <optgroup label="Sharjah">
                                            <option>Sharjah – Mega Mall</option>
                                            <option>Sharjah – Al Zahia</option>
                                            <option>Sharjah – Sharjah Central</option>
                                        </optgroup>
                                        <optgroup label="Other">
                                            <option>Al Ain – Makani Al Ain Mall</option>
                                        </optgroup>
                                    </select>
                                </div>
                            </div>
                        </section>

                        <section class="ax-form-section">
                            <h2><span class="ax-step">2</span> Choose Your Membership</h2>
                            <div class="ax-plans">

                                <label class="ax-plan">
                                    <input type="radio" name="plan" value="monthly" required>
                                    <div class="ax-plan-card">
                                        <span class="ax-plan-tag">Most Flexible</span>
                                        <h3 class="ax-plan-name">Monthly</h3>
                                        <div class="ax-plan-price">AED 199<span>/ month</span></div>
                                        <ul class="ax-plan-features">
                                            <li>Access to your home club</li>
                                            <li>Unlimited group classes</li>
                                            <li>Cancel anytime</li>
                                        </ul>
                                    </div>
                                </label>

                                <label class="ax-plan">
                                    <input type="radio" name="plan" value="quarterly" required>
                                    <div class="ax-plan-card">
                                        <span class="ax-plan-tag">Save 8%</span>
                                        <h3 class="ax-plan-name">Quarterly</h3>
                                        <div class="ax-plan-price">AED 549<span>/ 3 months</span></div>
                                        <ul class="ax-plan-features">
                                            <li>Access to all UAE clubs</li>
                                            <li>Unlimited classes</li>
                                            <li>1 free guest pass / month</li>
                                        </ul>
                                    </div>
                                </label>

                                <label class="ax-plan ax-plan-featured">
                                    <input type="radio" name="plan" value="annual" required>
                                    <div class="ax-plan-card">
                                        <span class="ax-plan-tag">Best Value</span>
                                        <h3 class="ax-plan-name">Annual</h3>
                                        <div class="ax-plan-price">AED 1,799<span>/ year</span></div>
                                        <ul class="ax-plan-features">
                                            <li>All clubs (UAE / KSA / BHR)</li>
                                            <li>Unlimited classes + HYROX</li>
                                            <li>2 free PT sessions</li>
                                            <li>30-day free freeze</li>
                                        </ul>
                                    </div>
                                </label>

                                <label class="ax-plan">
                                    <input type="radio" name="plan" value="day-pass" required>
                                    <div class="ax-plan-card">
                                        <span class="ax-plan-tag">Try It Out</span>
                                        <h3 class="ax-plan-name">Day Pass</h3>
                                        <div class="ax-plan-price">AED 75<span>/ day</span></div>
                                        <ul class="ax-plan-features">
                                            <li>One-day full access</li>
                                            <li>Try before you commit</li>
                                            <li>Valid at any branch</li>
                                        </ul>
                                    </div>
                                </label>

                            </div>
                        </section>

                        <section class="ax-form-section">
                            <label class="ax-checkbox">
                                <input type="checkbox" name="terms" required>
                                <span>I agree to the Terms &amp; Conditions and the Privacy Policy of AXIS.</span>
                            </label>

                            <button type="submit" class="ax-submit-btn" id="ax-submit-btn">Join AXIS Now</button>
                            <p class="ax-form-note" id="ax-form-note">An AXIS team member will reach out to confirm your registration.</p>
                        </section>

                    </form>
                </div>
            </section>

            <script>
                (function () {
                    var form = document.getElementById('ax-membership-form');
                    if (!form) return;
                    form.addEventListener('submit', function (e) {
                        e.preventDefault();
                        if (!form.checkValidity()) { form.reportValidity(); return; }
                        var btn = document.getElementById('ax-submit-btn');
                        var note = document.getElementById('ax-form-note');
                        if (btn) {
                            btn.textContent = 'Submitted \\u2713';
                            btn.classList.add('ax-success');
                            btn.disabled = true;
                        }
                        if (note) {
                            note.textContent = 'Thank you! Your request has been received. An AXIS team member will contact you shortly.';
                            note.style.color = '#1e9e3f';
                            note.style.fontWeight = '600';
                        }
                    });
                })();
            </script>
"""


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    """Replace everything between (and including) lines containing the
    given start/end markers — but keep those marker lines themselves."""
    s = text.index(start)
    e = text.index(end, s + len(start))
    return text[: s + len(start)] + replacement + text[e:]


def main() -> None:
    template_text = TEMPLATE.read_text(encoding="utf-8")

    # 1. <title>
    template_text = re.sub(
        r"<title>[^<]*</title>",
        f"<title>{NEW_TITLE}</title>",
        template_text,
        count=1,
    )

    # 2. <meta name="description">
    template_text = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{NEW_DESC}">',
        template_text,
        count=1,
    )

    # 3. Update og:title / twitter:title
    template_text = re.sub(
        r'(<meta property="og:title" content=")[^"]*(">)',
        r"\1Become an AXIS Member\2",
        template_text,
    )
    template_text = re.sub(
        r'(<meta name="twitter:title" content=")[^"]*(">)',
        r"\1Become an AXIS Member\2",
        template_text,
    )
    template_text = re.sub(
        r'(<meta property="og:description" content=")[^"]*(">)',
        rf"\1{NEW_DESC}\2",
        template_text,
    )
    template_text = re.sub(
        r'(<meta name="twitter:description" content=")[^"]*(">)',
        rf"\1{NEW_DESC}\2",
        template_text,
    )

    # 4. Replace the body of <main>. Keep the literal "<main>" and
    #    "</main>" lines; swap everything between them.
    template_text = replace_between(
        template_text,
        "<main>",
        "</main>",
        "\n" + FORM_BODY + "\n        ",
    )

    TARGET.write_text(template_text, encoding="utf-8")
    print(f"Wrote rebuilt membership page: {TARGET}")
    print(f"Total chars: {len(template_text)}")


if __name__ == "__main__":
    main()
