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


def check_primary_result(review_dir):
    """A page whose PRIMARY outcome has no pooled result cannot make its central claim and
    must not publish (this is what a k=0 decline looks like — the gate refuses it here rather
    than relying on a human to notice and not commit it)."""
    p = os.path.join(review_dir, "review.json")
    if not os.path.exists(p):
        return ["L1: no review.json to verify the primary outcome has a result"]
    try:
        with open(p, encoding="utf-8") as f:
            rev = json.load(f)
    except (OSError, ValueError) as exc:
        return [f"L1: cannot read review.json: {exc}"]
    outs = rev.get("outcomes") or []
    prim = next((o for o in outs if o.get("primary")), outs[0] if outs else None)
    if not prim:
        return ["L1: review has no primary outcome"]
    res = prim.get("result") or {}
    if res.get("present") is False or not res.get("k"):
        return [f"L1: primary outcome {prim.get('name')!r} has no pooled result "
                f"(k={res.get('k')}) — a page whose primary claim is absent must not publish"]
    return []


def check_cache_tracked(manifest):
    """A page replays from its committed cache, so that cache MUST be git-tracked — an untracked
    cache means a fresh clone cannot reproduce the page (this silently broke empagliflozin: the
    page looked fine, but its cache/<slug>/records.json was never committed). Refuse if untracked."""
    import subprocess
    slug = manifest.get("slug")
    if not slug:
        return ["L1: manifest has no slug to check cache tracking"]
    rel = f"cache/{slug}/records.json"
    try:
        out = subprocess.check_output(["git", "-C", ROOT, "ls-files", "--", rel], text=True).strip()
    except Exception as exc:  # noqa: BLE001
        return [f"L1: cannot check cache tracking ({exc})"]
    if not out:
        return [f"L1: committed cache {rel} is NOT git-tracked — a fresh clone could not reproduce "
                "this page; commit the cache"]
    return []


def check_reproduction(review_dir, manifest):
    """Level B: re-run the pipeline from the COMMITTED cache + protocol SHA and confirm it
    regenerates the committed review core (the numbers), not just that the HTML matches the
    JSON. This is what makes 'reproducible from the protocol SHA on a fresh clone' an enforced
    property rather than a claim — every extraction/screening/dedup change must survive it."""
    import json as _json
    slug = manifest.get("slug")
    if not slug:
        return ["L1: manifest has no slug to replay"]
    try:
        from . import fetch
        from .canonical import review_sha256
        from .pipeline import build_review_core
        import subprocess
        cfg = _json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
        sha = subprocess.check_output(["git", "-C", ROOT, "log", "-1", "--format=%H", "--",
                                       f"protocols/{slug}.md"], text=True).strip()
        records = fetch.ensure(cfg, "")  # committed cache present -> offline
        regen = review_sha256(build_review_core(slug, cfg, records, sha))
    except Exception as exc:  # noqa: BLE001 - a replay that cannot run is a refusal, not a pass
        return [f"L1: offline replay could not execute ({exc}) — cannot confirm reproduction"]
    if regen != manifest.get("review_sha256"):
        return [f"L1: offline replay does NOT regenerate the committed numbers "
                f"(replay {regen} vs committed {manifest.get('review_sha256')})"]
    return []


def check_controls(review_dir, manifest):
    """Screening controls must be ENFORCED, not just reported. Every topic must declare >=1 positive
    and >=1 negative control (a control that never runs is decoration); every POSITIVE control (a
    canonical trial a comparator includes) must be screened IN, and every NEGATIVE control (a
    same-drug/design trial of the wrong topic) must be screened OUT. A positive control screened out,
    or a negative control screened in, is a screening regression and REFUSES here rather than sitting
    as a 'MISSED' string on the page."""
    slug = manifest.get("slug")
    if not slug:
        return ["L1: manifest has no slug to check controls"]
    try:
        cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
        rev = json.load(open(os.path.join(review_dir, "review.json"), encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"L1: cannot load config/review to check controls ({exc})"]
    pos = [str(p) for p in cfg.get("positive_control_pmids", [])]
    neg = [str(p) for p in cfg.get("negative_control_pmids", [])]
    reasons = []
    if not pos:
        reasons.append("L1: no positive control declared (every topic needs >=1 canonical-trial control)")
    if not neg:
        reasons.append("L1: no negative control declared (every topic needs >=1 wrong-topic control)")
    dec = {}
    for x in (rev.get("screening") or {}).get("records", []):
        rid = str(x.get("id", "")).split("·")[-1].strip()
        dec[rid] = x.get("decision")
    pos_miss = [p for p in pos if dec.get(p) != "include"]
    neg_in = [p for p in neg if dec.get(p) == "include"]
    if pos_miss:
        reasons.append(f"L1: positive control(s) {pos_miss} were NOT screened in "
                       "(a canonical trial the comparator includes must pass our screen)")
    if neg_in:
        reasons.append(f"L1: negative control(s) {neg_in} were wrongly screened in "
                       "(a wrong-topic trial must be excluded by rule)")
    return reasons


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def gate_page(review_dir):
    """Return (ok: bool, reasons: list[str]). ok == True only if both limbs pass."""
    try:
        manifest, html, rep = _load(review_dir)
    except (OSError, ValueError) as exc:
        return False, [f"gate: cannot load review dir: {exc}"]
    reasons = (check_limb1(review_dir, manifest, html, rep)
               + check_cache_tracked(manifest)
               + check_reproduction(review_dir, manifest)
               + check_primary_result(review_dir)
               + check_controls(review_dir, manifest)
               + check_limb2(manifest, html))
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
