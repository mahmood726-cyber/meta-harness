"""Plant: a page is never built from another meta's records. After the V8 comparator switches (signed 7 Oct) the cached
records still held the OLD comparator's full text and Unpaywall status, and four of the five new comparators had no
PubMed record held: the rebuilt pages named the new comparator with pmid null and read its reported numbers from the
old comparator's text. harness.pipeline.comparator_records_problem refuses that build."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import pipeline as pl  # noqa: E402

CFG = {"comparator_pmid": "222"}


def test_matching_records_build():
    assert pl.comparator_records_problem(CFG, {"comparator_pmid": "222"}, {"222": {"id": "222"}}) is None


def test_PLANT_old_comparator_text_refuses():
    p = pl.comparator_records_problem(CFG, {"comparator_pmid": "111"}, {"222": {"id": "222"}})
    assert p and "STALE" in p and "PMID 111" in p


def test_PLANT_no_record_of_the_new_comparator_refuses():
    p = pl.comparator_records_problem(CFG, {"comparator_pmid": "222"}, {})
    assert p and "no PubMed record" in p


def test_a_dedicated_comparator_record_counts():
    recs = {"comparator_pmid": "222", "comparator_record": {"id": "222", "title": "t"}}
    assert pl.comparator_records_problem(CFG, recs, {}) is None


def test_every_served_topic_now_holds_its_own_comparators_records():
    import glob
    import json
    from harness import served_comparator as sc
    bad = []
    for p in sorted(glob.glob(os.path.join(ROOT, "topics", "*.json"))):
        s = os.path.basename(p)[:-5]
        rp = os.path.join(ROOT, "cache", s, "records.json")
        if not os.path.exists(os.path.join(ROOT, "docs", "reviews", s, "review.json")) or not os.path.exists(rp):
            continue
        cfg = sc.served_config(s, json.load(open(p, encoding="utf-8")))
        from harness import fetch
        recs = fetch.ensure(cfg, "")          # records.json + the signed comparator's comparator_records.json overlay
        prob = pl.comparator_records_problem(cfg, recs, {r["id"]: r for r in recs.get("records") or []})
        if prob:
            bad.append((s, prob))
    assert bad == []


def test_records_json_is_never_rewritten_for_a_switch():
    """The search cache is digested by other evidence (v2 observations pin cache/<slug>/records.json): a comparator
    switch writes cache/<slug>/comparator_records.json beside it and leaves records.json byte-identical to main."""
    import subprocess
    for s in ["dpp4-mace-t2d", "esketamine-trd-madrs", "melatonin-primary-insomnia-sol", "denosumab-vertebral-fracture",
              "statins-primary-prevention-elderly"]:
        assert os.path.exists(os.path.join(ROOT, "cache", s, "comparator_records.json")), s
        for k in ("comparator_record", "comparator_replaced", "comparator_acquired_utc"):
            assert k not in json.load(open(os.path.join(ROOT, "cache", s, "records.json"), encoding="utf-8")), (s, k)


def test_the_overlay_applies_only_to_the_configured_comparator(tmp_path):
    from harness import fetch
    (tmp_path / "comparator_records.json").write_text(json.dumps({"comparator_pmid": "222", "comparator_record": {"id": "222"}}),
                                                      encoding="utf-8")
    base = {"comparator_pmid": "111", "records": []}
    assert fetch._with_comparator_records(base, {"comparator_pmid": "222"}, str(tmp_path))["comparator_pmid"] == "222"
    assert fetch._with_comparator_records(base, {"comparator_pmid": "333"}, str(tmp_path)) == base
