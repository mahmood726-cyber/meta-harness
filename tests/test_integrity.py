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
    """Every current PMID has either held integrity evidence or an explicit
    NOT_ASSESSED state. Historical snapshot coverage is never called current
    merely because membership changed during an offline rebuild."""
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
        # The immutable snapshot can cover an earlier population. The served
        # object must account for the current union without inventing checks.
        current = rev.get("integrity") or {}
        rows = {v.get("pubmed_key"): v for v in current.get("per_trial", {}).values()
                if v.get("pubmed_key")}
        if set(rows) != union:
            stale.append(f"{slug}: served integrity membership differs from current union")
        missing = union - set(integ.get("per_pmid", {}))
        for pid in union:
            row = rows.get(pid, {})
            if pid in missing:
                assert row.get("state") == "NOT_ASSESSED", (slug, pid)
                assert row.get("pubmed_checked") is False, (slug, pid)
            else:
                assert row.get("pubmed_checked") is True, (slug, pid)
                assert row.get("retracted") == bool(integ["per_pmid"][pid].get("retracted"))
        assert current.get("n_pubmed_checked") == len(union - missing), slug
        assert current.get("n_not_assessed") == len(missing), slug
        if missing:
            html = open(os.path.join(reviews, slug, "index.html"), encoding="utf-8").read()
            assert "NOT_ASSESSED (offline lane)" in html, slug
    assert not stale, "stale integrity.json (re-run scripts/integrity_check.py): " + "; ".join(stale)
    assert checked > 0, "no committed integrity.json found to verify"
