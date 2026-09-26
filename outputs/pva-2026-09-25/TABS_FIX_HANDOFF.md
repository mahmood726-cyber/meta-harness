# To the release captain: the "all the tabs are empty" fix for V1 (page-verifier lane, page.py)

Reported by Mahmood ("why are all the tabs empty"), 2026-09-25. **Served HTML changes; no served number moves.**

## What was wrong (measured in a real browser on the live GLP-1 page, origin/main 640695a5 era)
- `render_page` put the verifier box (1,426 px desktop / 2,791 px phone), its digests and the evidence certificate
  (4,724 / 8,898 px) in `<main>` **before** the tab panels, so every panel started at **y = 6,482 px at 1280x800** and
  **~12,400 px at a phone width**. The first ~1,500 px of "banners" was this lane's own verifier box.
- Each tab's own heading (`h3.tabname`) was `display:none`, and `show()` never scrolled.
- Result: clicking any tab left the viewport on the certificate. **0 of 11 tabs** showed their content in the first viewport,
  at desktop or phone width.
- "Trial families" (1.15 MB) and "Missing evidence" are **already inside the Screening tab on all 32 pages** (static check
  of every served page). That part of the report did not reproduce. The placement is now pinned by a test.

## The fix (harness/page.py; docs/harness/page.py mirrored byte-identical)
1. The verifier box and the evidence certificate move into their own last tab, **"Verify this page"** (dropped on neutral/blind
   pages, which carry neither).
2. Above the tabs there is **one line**: "Verify this page: `python audit_certificate_stdlib.py CERTIFICATE.json` -- Certificate
   auditor, `docs/scripts/audit_certificate_stdlib.py` sha256 `<first 16>` (+N more). Commands, limits and the full certificate:
   the Verify this page tab."
3. Every tab shows its own heading, and a tab click scrolls so the tab bar and that heading are at the top of the viewport.

## Acceptance (real browser, `outputs/pva-2026-09-25/tab_acceptance.js`, three scenarios each)
| width | tabs whose own heading is in the first viewport after the click | area above the tabs |
|---|---|---|
| before, 1280x800 | **0 of 11** (content at y~6,500) | 6,482 px |
| after, 1280x800 | **12 of 12** (headings at 78 px; Reporting 133 px) | 184 px |
| before, phone | **0 of 11** (content at y~12,400) | ~12,300 px |
| after, phone | **12 of 12** (lowest heading 204 px) | 366 px (the tab bar wraps to 166 px) |

## Tests
`tests/test_page_tabs_layout.py`: the layout contract on every served page (nothing but tab panels after the tab bar; the
verifier box and certificate inside the Verify tab; the one line names the SERVED auditor sha256; headings not hidden; a click
scrolls; the family ledger inside Screening), plus 5 plants, each failing on the planted defect. Run on the OLD live GLP-1 page,
the contract names 5 problems (25,594 characters above the tabs, verifier box outside the tab, no line, hidden headings, no scroll).

## For V1 integration
- page.py is pinned by every certificate, so this is a re-certification: all 32 pages rebuilt (`build_topic.py <slug> --now
  2026-09-11`), then build_bundle glp1, render_fix_ledger, rewrite_fixstate_lines, build_evidence_index. 0 served numbers change
  (served_numbers_diff).
- It conflicts with the other re-certifications (rai's R1+R4, oc's GLP-1 page) **only in generated files**. Merge the code (page.py
  does not overlap with their files), then **regenerate every page once**; never hand-merge generated HTML/JSON.
- After deploy, re-run `tab_acceptance.js` on the served GLP-1 page at desktop and phone widths (this lane will).
