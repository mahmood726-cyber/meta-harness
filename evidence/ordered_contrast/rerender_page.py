"""Re-render ONE served page from its replayed core, exactly as scripts/reproduce_review.py compares it, and write index.html.

Why this exists: the page names the sha256 of docs/scripts/verify_bundle.py (tests/test_page_verifier.py), so any verifier change
must be followed by a re-render. This is the reproduction limb's own render path (replay_core -> reproduction block -> certificate ->
render_page), not a hand edit. It REFUSES to write unless the replayed review_sha256 equals the committed one: the numbers must not
move, only the rendered verifier identity. usage: python evidence/ordered_contrast/rerender_page.py <slug>"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import reproduce_review as rr  # noqa: E402
from harness.page import render_page  # noqa: E402
from harness.canonical import review_sha256  # noqa: E402


def main(slug):
    ok, reasons = rr.reproduce(slug)
    others = [r for r in reasons if not r.startswith("served index.html does not byte-match")]
    if others:
        print("REFUSED: the replay disagrees on more than the rendered page:\n  " + "\n  ".join(others))
        return 1
    # rebuild `final` the way reproduce() does, then render it (reproduce() returns only verdicts)
    captured = {}
    orig = rr.render_page

    def spy(final):
        captured["final"] = final
        return orig(final)
    rr.render_page = spy
    try:
        rr.reproduce(slug)
    finally:
        rr.render_page = orig
    final = captured["final"]
    html = render_page(final)
    d = os.path.join(ROOT, "docs", "reviews", slug)
    committed_sha = __import__("json").load(open(os.path.join(d, "manifest.json"), encoding="utf-8")).get("review_sha256")
    if review_sha256({k: v for k, v in final.items() if k != "reproduction"}) != committed_sha and final.get("reproduction", {}).get("review_sha256") != committed_sha:
        print("REFUSED: replayed review_sha256 differs from the committed one")
        return 1
    open(os.path.join(d, "index.html"), "w", encoding="utf-8", newline="").write(html)
    ok2, reasons2 = rr.reproduce(slug)
    print("rewritten; reproduce ->", ok2, reasons2)
    return 0 if ok2 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
