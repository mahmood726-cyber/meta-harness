"""The tab layout contract, on every served review page (the "why are all the tabs empty" defect, 2026-09-25).

Measured on the live GLP-1 page before the fix: the verifier box, its digests and the evidence certificate rendered in <main>
ABOVE the tab panels (~6,300 px at 1280x800, ~12,200 px at a phone width), each tab's own heading was display:none, and a tab
click never scrolled -- so clicking any tab showed the certificate, not the tab. The contract below is what makes that
structurally impossible; the browser measurement (outputs/pva-2026-09-25/tab_acceptance.js) is the acceptance on top of it.

  1. nothing but tab panels follows the tab bar: <main>'s first element child is a tab panel (or a one-line notice);
  2. the verifier box and the evidence certificate are INSIDE the "Verify this page" tab (non-neutral pages);
  3. above the tabs, one line names the certificate auditor, the sha256 of its SERVED bytes and the command;
  4. each tab's own heading is not hidden, and a tab click scrolls (show(id, byClick) scrolls to the tab bar);
  5. the trial-family ledger and the missing-evidence panel are inside the Screening tab."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
AUDITOR = DOCS / "scripts" / "audit_certificate_stdlib.py"
ALLOWED_BEFORE_TABS = re.compile(r"^<div class='absent'><strong>AACT_NOT_MEASURED</strong>[^<]*</div>")


def _pages():
    return sorted(p for p in (DOCS / "reviews").glob("*/index.html"))


def _tab_of(html: str, pos: int) -> str | None:
    tab = None
    for m in re.finditer(r'<section class="tab" id="tab-([a-z]+)"', html):
        if m.start() < pos:
            tab = m.group(1)
    return tab


def layout_problems(html: str, auditor_sha: str) -> list[str]:
    """The contract as a pure function of one page's HTML (so each clause can be planted against)."""
    out = []
    main = html.split("<main>", 1)[1] if "<main>" in html else ""
    first_tab = main.find('<section class="tab"')
    lead = main[:first_tab] if first_tab >= 0 else main
    if first_tab < 0:
        out.append("no tab panels in <main>")
    elif lead and not ALLOWED_BEFORE_TABS.fullmatch(lead):
        out.append(f"{len(lead)} characters of content between the tab bar and the first tab panel")
    for anchor in ("page-verifier", "evidence-certificate"):
        m = re.search(r"""id=["']""" + anchor + r"""["']""", html)          # either quote: the certificate renders id='...'
        pos = m.start() if m else -1
        if pos >= 0 and _tab_of(html, pos) != "verify":
            out.append(f"{anchor} is outside the 'Verify this page' tab (in: {_tab_of(html, pos)})")
    if "id='page-verifier'" in html:
        nav = html.find("<nav>")
        line = re.search(r"<div id='verify-line'.*?</div>", html, re.S)
        if not line or line.start() > nav:
            out.append("no one-line verifier summary above the tab bar")
        elif auditor_sha[:16] not in line.group(0) or "audit_certificate_stdlib.py" not in line.group(0):
            out.append("the verifier line does not name the served auditor and its sha256")
    if re.search(r"h3\.tabname\{display:none\}", html):
        out.append("each tab's own heading is hidden (h3.tabname display:none)")
    if not re.search(r"function show\(id,byClick\).*?scrollTo", html, re.S) or "show('overview',1)" not in html:
        out.append("a tab click does not scroll to the tab")
    for anchor in ("trial-families", "family-missing-evidence"):
        m = re.search(r"""id=["']""" + anchor + r"""["']""", html)
        pos = m.start() if m else -1
        if pos >= 0 and _tab_of(html, pos) != "screening":
            out.append(f"{anchor} is outside the Screening tab (in: {_tab_of(html, pos)})")
    return out


def test_there_are_served_pages():
    assert len(_pages()) >= 32


@pytest.mark.parametrize("page", _pages(), ids=lambda p: p.parent.name)
def test_every_served_page_keeps_the_tab_layout_contract(page):
    sha = hashlib.sha256(AUDITOR.read_bytes()).hexdigest()
    assert layout_problems(page.read_text(encoding="utf-8"), sha) == []


def _glp1():
    return (DOCS / "reviews" / "glp1-ra-mace-t2d" / "index.html").read_text(encoding="utf-8"), \
        hashlib.sha256(AUDITOR.read_bytes()).hexdigest()


def test_plant_the_old_layout_certificate_above_the_tabs_is_named():
    html, sha = _glp1()
    i = html.index("<section id='evidence-certificate'")                   # the real rendered block, moved above the tabs
    j = html.index("</section>", i) + len("</section>")
    cert = html[i:j]
    rest = html[:i] + html[j:]
    main_open = rest.index("<main>") + len("<main>")
    planted = rest[:main_open] + cert + rest[main_open:]
    probs = layout_problems(planted, sha)
    assert any("between the tab bar and the first tab panel" in p for p in probs), probs
    assert any("evidence-certificate" in p and "outside" in p for p in probs), probs


def test_plant_a_hidden_tab_heading_is_named():
    html, sha = _glp1()
    assert any("heading is hidden" in p for p in layout_problems(html.replace("</style>", "html.js .tab h3.tabname{display:none}</style>", 1), sha))


def test_plant_a_click_that_does_not_scroll_is_named():
    html, sha = _glp1()
    planted = html.replace("show('overview',1)", "show('overview')")
    assert any("does not scroll" in p for p in layout_problems(planted, sha))


def test_plant_a_verifier_line_naming_other_bytes_is_named():
    html, sha = _glp1()
    assert any("does not name the served auditor" in p for p in layout_problems(html, "f" * 64))


def test_plant_the_family_ledger_outside_screening_is_named():
    html, sha = _glp1()
    i = html.index('<section id="trial-families">')
    j = html.index("</section>", i) + len("</section>")
    block = html[i:j]
    moved = html[:i] + html[j:]
    k = moved.index('<section class="tab" id="tab-verify">')
    planted = moved[:k] + block + moved[k:]
    assert any("trial-families" in p and "outside the Screening tab" in p for p in layout_problems(planted, sha))
