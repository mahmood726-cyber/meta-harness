"""armcontrast into screening: an audit-confirmed non-contrast is EVICTED at eligibility
(X-CONTRAST), not admitted then disclosed after pooling. Confirmed-only; a normal record is
untouched."""
import harness.screen as S


def _rec(rid, **kw):
    r = {"id": rid, "id_type": "pmid", "title": "A randomized controlled trial of X vs Y",
         "abstract": "randomized double-blind placebo-controlled", "pubtypes": ["Randomized Controlled Trial"]}
    r.update(kw)
    return r


def test_contrast_eviction_fires_by_id_nct_acronym():
    cfg = {"include": {}, "contrast_evictions": [
        {"key": "NCT03153150", "alt": ["SoSTART"], "basis": "START vs AVOID, not DOAC-vs-warfarin"}]}
    # match by NCT
    out = S.run([_rec("NCT03153150")], cfg)["decisions"][0]
    assert out["decision"] == "exclude" and out["rule_id"] == "X-CONTRAST" and "CONTRAST_ABSENT" in out["reason"]
    # match by acronym on a registry-only record whose raw id differs
    out2 = S.run([_rec("999", acronym="SoSTART", nct="NCT03153150")], cfg)["decisions"][0]
    assert out2["rule_id"] == "X-CONTRAST"


def test_non_listed_record_not_evicted():
    cfg = {"include": {"intervention_any": ["x"], "comparator_any": ["y"],
                       "population_any": ["z"]},
           "contrast_evictions": [{"key": "15472166", "basis": "..."}]}
    out = S.run([_rec("77777777", nct="NCT01111111")], cfg)["decisions"][0]
    assert out["rule_id"] != "X-CONTRAST"


def test_no_evictions_config_is_noop():
    cfg = {"include": {"intervention_any": ["x"], "comparator_any": ["y"], "population_any": ["z"]}}
    out = S.run([_rec("123", nct="NCT0")], cfg)["decisions"][0]
    assert out["rule_id"] != "X-CONTRAST"
