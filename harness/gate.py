"""Two-limb publication gate.

A page is publishable ONLY IF BOTH limbs pass. The gate is enforced at commit
time by .githooks/pre-commit against every staged docs/reviews/<slug>/ page, and
it is designed to REFUSE — see tests/test_gate.py, which proves refusal on each
failure mode. The old corpus reached 1,427 pages because nothing ever stopped a
page appearing; this is that stop.

Limb 1 - reproducibility & integrity:
  * manifest complete; served_method == declared_method
  * generator is the harness, not hand; no hand-made marker in the page
  * a reproduction census is committed with 0 failures, pinned to the exact
    served bytes (its html_sha256 == sha256(index.html) == manifest.html_sha256)
  * the census re-runs live here and reproduces (failures == 0)

Limb 2 - named published OPEN-ACCESS comparator:
  * manifest.comparator has name, PMID or DOI, url, open_access == True,
    and a trial-set overlap {ours_k, theirs_k, shared_k, method}
  * the SERVED page actually contains the comparator identifier and the three
    overlap counts (stated on the page, not merely in metadata)
"""
from __future__ import annotations
import json
import os
import sys

from .canonical import sha256_text
from .census import verify

REQUIRED_MANIFEST = ("slug", "declared_method", "served_method", "protocol_sha",
                     "generator", "review_sha256", "html_sha256")


def _load(review_dir):
    with open(os.path.join(review_dir, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    with open(os.path.join(review_dir, "index.html"), encoding="utf-8") as f:
        html = f.read()
    rep_path = os.path.join(review_dir, "REPRODUCTION.json")
    rep = None
    if os.path.exists(rep_path):
        with open(rep_path, encoding="utf-8") as f:
            rep = json.load(f)
    return manifest, html, rep


def check_limb1(review_dir, manifest, html, rep):
    reasons = []
    for k in REQUIRED_MANIFEST:
        if not manifest.get(k):
            reasons.append(f"L1: manifest missing '{k}'")
    if manifest.get("declared_method") != manifest.get("served_method"):
        reasons.append(
            f"L1: served method != declared method "
            f"({manifest.get('served_method')!r} vs {manifest.get('declared_method')!r})")
    if str(manifest.get("generator", "")).lower() == "hand":
        reasons.append("L1: generator is 'hand' (nothing hand-made may publish)")
    if "data-handmade" in html or "<!-- handmade -->" in html:
        reasons.append("L1: page carries a hand-made marker")

    if rep is None:
        reasons.append("L1: no committed reproduction census (REPRODUCTION.json)")
    else:
        if rep.get("failures") != 0:
            reasons.append(f"L1: committed census has {rep.get('failures')} failures")
        served_sha = sha256_text(html)
        if rep.get("html_sha256") != served_sha:
            reasons.append("L1: census html_sha256 != sha256(served index.html) "
                           "(page edited after census)")
        if manifest.get("html_sha256") != served_sha:
            reasons.append("L1: manifest html_sha256 != sha256(served index.html)")

    # Live fresh-clone-style reproduction.
    live = verify(review_dir)
    if live["failures"] != 0:
        reasons.append(f"L1: live census reproduced {live['failures']} failure(s): "
                       + "; ".join(c["check"] for c in live["checks"] if not c["ok"]))
    return reasons


def check_limb2(manifest, html):
    reasons = []
    c = manifest.get("comparator")
    if not c:
        reasons.append("L2: no named published comparator")
        return reasons
    if not c.get("name"):
        reasons.append("L2: comparator has no name")
    ident = c.get("pmid") or c.get("doi")
    if not ident:
        reasons.append("L2: comparator has no PMID or DOI")
    if not c.get("url"):
        reasons.append("L2: comparator has no URL")
    if c.get("open_access") is not True:
        reasons.append("L2: comparator is not marked open_access=true")
    ov = c.get("overlap") or {}
    for k in ("ours_k", "theirs_k", "shared_k", "method"):
        if ov.get(k) in (None, ""):
            reasons.append(f"L2: overlap missing '{k}'")
    # Served page must actually state the identifier and the three counts.
    if ident and str(ident) not in html:
        reasons.append("L2: comparator identifier not present on the served page")
    for k in ("ours_k", "theirs_k", "shared_k"):
        v = ov.get(k)
        if v is not None and str(v) not in html:
            reasons.append(f"L2: overlap {k}={v} not stated on the served page")
    return reasons


def gate_page(review_dir):
    """Return (ok: bool, reasons: list[str]). ok == True only if both limbs pass."""
    try:
        manifest, html, rep = _load(review_dir)
    except (OSError, ValueError) as exc:
        return False, [f"gate: cannot load review dir: {exc}"]
    reasons = check_limb1(review_dir, manifest, html, rep) + check_limb2(manifest, html)
    return (len(reasons) == 0), reasons


def main(argv):
    if not argv:
        print("usage: python -m harness.gate <review_dir> [<review_dir> ...]")
        return 2
    any_refused = False
    for d in argv:
        ok, reasons = gate_page(d)
        if ok:
            print(f"GATE PASS  {d}")
        else:
            any_refused = True
            print(f"GATE REFUSE {d}")
            for r in reasons:
                print(f"    - {r}")
    return 1 if any_refused else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
