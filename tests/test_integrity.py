"""Trial-integrity gate: a pooled RETRACTED trial refuses the page; a clean set passes."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.gate import check_retraction  # noqa: E402


def _dir(integrity):
    d = tempfile.mkdtemp(prefix="mh-integ-")
    rev = {"outcomes": [{"primary": True, "trials": [{"id": "PMID 1"}]}], "integrity": integrity}
    json.dump(rev, open(os.path.join(d, "review.json"), "w", encoding="utf-8"))
    return d


def test_retracted_pooled_trial_refuses():
    reasons = check_retraction(_dir({"retracted": ["32450107"], "concern": []}))
    assert reasons and "RETRACTED" in reasons[0] and "32450107" in reasons[0]


def test_clean_passes():
    assert check_retraction(_dir({"retracted": [], "concern": []})) == []


def test_expression_of_concern_does_not_block():
    # concern is surfaced, not blocked
    assert check_retraction(_dir({"retracted": [], "concern": ["12345"]})) == []


def test_no_integrity_block_does_not_refuse():
    d = tempfile.mkdtemp(prefix="mh-integ2-")
    json.dump({"outcomes": []}, open(os.path.join(d, "review.json"), "w", encoding="utf-8"))
    assert check_retraction(d) == []


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _pooled_pmid_union(rev):
    """Every trial pooled ANYWHERE on the page (primary + secondary outcomes) that carries a
    PubMed id. This is the denominator the retraction line reports, so integrity.json must match
    it exactly or the rendered 'none of the N pooled trials is retracted' is stale."""
    union = set()
    for o in rev.get("outcomes", []) or []:
        for t in o.get("trials", []) or []:
            p = str(t.get("id", "")).replace("PMID ", "")
            if p.isdigit():
                union.add(p)
    return union


def test_committed_integrity_is_fresh_for_every_live_topic():
    """Corpus invariant (the durable fix for the stale-n_pooled defect the fair blind re-judge
    flagged): for every live topic that carries an integrity.json, its n_pooled and the PMIDs it
    actually checked (per_pmid keys) MUST equal the current all-outcome pooled PMID union. A pool
    change (a recovery added, a dedup drop) that is not followed by a fresh integrity run makes the
    retraction line report a wrong count — exactly the class this test forbids from returning."""
    reviews = os.path.join(ROOT, "docs", "reviews")
    if not os.path.isdir(reviews):
        return  # not a full repo checkout; nothing to assert
    checked = 0
    stale = []
    for slug in sorted(os.listdir(reviews)):
        rp = os.path.join(reviews, slug, "review.json")
        ip = os.path.join(ROOT, "cache", slug, "integrity.json")
        if not (os.path.exists(rp) and os.path.exists(ip)):
            continue
        rev = json.load(open(rp, encoding="utf-8"))
        integ = json.load(open(ip, encoding="utf-8"))
        union = _pooled_pmid_union(rev)
        checked += 1
        if integ.get("n_pooled") != len(union):
            stale.append(f"{slug}: n_pooled={integ.get('n_pooled')} != pooled union {len(union)}")
        elif set(integ.get("per_pmid", {})) != union:
            missing = union - set(integ.get("per_pmid", {}))
            extra = set(integ.get("per_pmid", {})) - union
            stale.append(f"{slug}: per_pmid coverage drifted (missing={sorted(missing)} extra={sorted(extra)})")
    assert not stale, "stale integrity.json (re-run scripts/integrity_check.py): " + "; ".join(stale)
    assert checked > 0, "no committed integrity.json found to verify"
