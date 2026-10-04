"""G1 scoreboard (scripts/render_g1_tracker.py): the counting rule, the independent recomputation of the four G1
criteria, and the page's currency.

Rule (2026-10-02): verified = PRIMARY, or TWO_SOURCE with a recorded independent pair that holds no comparator id;
nothing sourced only from the comparator counts. A topic is MATCHED on the page only when the lane's status AND the
recomputation agree. Each plant would pass a renderer that copied the lane's status instead of recomputing it.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("render_g1_tracker", ROOT / "scripts" / "render_g1_tracker.py")
g1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g1)

COMP = "34526024"


def _rec(trials, lane="G1_MATCHED", n_el=None, k=None, verdict="AGREE", named=()):
    n = len(trials)
    return {"schema_version": 1, "slug": "glp1-ra-mace-t2d", "comparator_pmid": COMP, "N_comparator_trials": n,
            "N_eligible": n if n_el is None else n_el, "k_matched": n if k is None else k, "trials": trials,
            "same_trials": {"state": "POOLED", "k": n, "measure": "HR",
                            "ours": {"estimate": 0.85, "ci_low": 0.8, "ci_high": 0.9},
                            "theirs": {"estimate": 0.85, "ci_low": 0.8, "ci_high": 0.9},
                            "verdict": {"verdict": verdict}},
            "named_differences": [{"trial": t, "kind": "X"} for t in named], "comparator_findings": [],
            "g1_status": {"state": lane}}


def _t(label, route="PRIMARY", pooled=True, agree="AGREE", **kw):
    return dict({"label": label, "route": route, "in_our_pool": pooled, "agreement_with_comparator_row": agree}, **kw)


def test_a_fully_verified_agreeing_named_topic_is_matched():
    assert g1.recompute(_rec([_t("A"), _t("B")]))["matched"]


def test_PLANT_a_two_source_pair_containing_the_comparator_does_not_verify():
    r = g1.recompute(_rec([_t("A", "TWO_SOURCE", independent_pair_ids=["PMID 34526024", "1"])]))
    assert not r["criteria"]["MATCHED_ARE_VERIFIED"] and "anti-circularity" in r["rows"][0]["why"]


def test_PLANT_a_two_source_row_with_an_unknown_pair_does_not_verify():
    r = g1.recompute(_rec([_t("A", "TWO_SOURCE")]))
    assert not r["criteria"]["MATCHED_ARE_VERIFIED"] and "fail-closed" in r["rows"][0]["why"]


def test_PLANT_an_unnamed_divergence_fails_divergences_named():
    outside = _t("ELIXA", "UNVERIFIED", pooled=False, agree="NOT_IN_OUR_POOL")
    r = g1.recompute(_rec([_t("A"), outside]))
    assert not r["criteria"]["DIVERGENCES_NAMED"] and r["unnamed"] == ["ELIXA"]
    assert g1.recompute(_rec([_t("A"), outside], named=["ELIXA"]))["criteria"]["DIVERGENCES_NAMED"]


def test_unmatched_eligible_and_disagreeing_result_fail_their_criteria():
    assert not g1.recompute(_rec([_t("A")], n_el=2, k=1))["criteria"]["ALL_ELIGIBLE_MATCHED"]
    assert not g1.recompute(_rec([_t("A")], verdict="DIFFERENT_CONCLUSION"))["criteria"]["RESULT_AGREES"]


def test_PLANT_a_lane_matched_status_the_recomputation_refutes_is_not_counted(tmp_path):
    (tmp_path / g1.SRC).mkdir(parents=True)
    rec = _rec([_t("A", "TWO_SOURCE")])  # the lane says G1_MATCHED; the pair is unknown, so it is not verified
    (tmp_path / g1.SRC / "glp1-ra-mace-t2d.json").write_text(json.dumps(rec), encoding="utf-8")
    page = g1.render(tmp_path)
    assert "G1 MATCHED: 0 of 1 topics" in page and "lane status disagrees" in page


def test_the_committed_page_is_current():
    assert (ROOT / g1.OUT).read_bytes() == g1.render().encode("utf-8")


def test_committed_snapshot_matches_its_declared_tracker_blob():
    src = json.loads((ROOT / g1.SOURCE).read_text(encoding="utf-8"))
    data = (ROOT / "outputs" / "k_gap" / "G1_TRACKER.md").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest() == src["tracker_blob"]


# --- two-number scoreboard (decision 2026-10-03): COVERAGE beside INDEPENDENTLY CONFIRMED ---------------------------

def _cs(label, digest="d" * 64, meta=COMP, **kw):
    pv = {"meta_pmid": meta, "location": {"kind": "figure", "id": "f1", "row_label": label}, "digest": digest,
          "read": "MODEL_PROPOSAL_DUAL:mc-a+mc-b"}
    if digest is None:
        pv.pop("digest")
    return _t(label, route="NO_ROW", pooled=False, coverage="COMPARATOR_SOURCED",
              comparator_sourced={"value": {"measure": "OR"}, "provenance": pv}, **kw)


def test_PLANT_a_comparator_sourced_row_is_coverage_and_never_confirmation():
    r = g1.recompute(_rec([_t("A"), _cs("B")], k=1, named=("B",)))
    assert (r["covered"], r["g1_count"], r["comparator_sourced"]) == (2, 1, 1)
    # even pooled, a comparator-sourced row cannot make the topic MATCHED
    r2 = g1.recompute(_rec([_t("A"), dict(_cs("B"), in_our_pool=True)]))
    assert not r2["criteria"]["MATCHED_ARE_VERIFIED"] and not r2["matched"]


def test_PLANT_a_comparator_sourced_row_without_its_digest_is_not_covered():
    r = g1.recompute(_rec([_t("A"), _cs("B", digest=None)], k=1, named=("B",)))
    assert r["covered"] == 1 and r["rows"][1]["covered"] is False and r["comparator_sourced"] == 0


def _two(label, stated):
    return _t(label, route="TWO_SOURCE", readings=[{"counts_stated_by": stated}])


def test_PLANT_two_source_counts_on_two_distinct_recorded_non_comparator_sources():
    ok = g1.recompute(_rec([_two("A", ["TEXT PMID 33472855 + full text", "META 36102463 (prints events/total)"])]))
    assert ok["g1_count"] == 1 and ok["matched"]
    same = g1.recompute(_rec([_two("A", ["TEXT PMID 33472855", "TEXT PMID 33472855 + acquired full text"])]))
    assert same["g1_count"] == 0  # two readings of ONE text are one source
    circ = g1.recompute(_rec([_two("A", ["TEXT PMID 33472855", f"META {COMP} (prints events/total)"])]))
    assert circ["g1_count"] == 0 and "anti-circularity" in circ["rows"][0]["why"]


def _ss(label, meta, digest="e" * 64):
    return _t(label, route="SWEEP_SECONDARY_SINGLE", sweep={"basis": {
        "meta": meta, "where": {"kind": "figure", "id": "fig2"}, "digest": digest, "provenance": "MODEL_PROPOSAL:mc-x"}})


def test_PLANT_secondary_single_counts_only_from_a_recorded_non_comparator_meta():
    assert g1.recompute(_rec([_ss("A", "33745918")]))["g1_count"] == 1
    assert g1.recompute(_rec([_ss("A", COMP)]))["g1_count"] == 0
    assert g1.recompute(_rec([_ss("A", "33745918", digest="")]))["g1_count"] == 0


def test_the_committed_page_shows_both_numbers_recomputed_from_the_trial_rows():
    recs = g1.load()
    conf = sum(g1.recompute(r)["g1_count"] for r in recs.values())
    cov = sum(g1.recompute(r)["covered"] for r in recs.values())
    n = g1.trial_totals(recs)["comparator_n"]
    page = (ROOT / g1.OUT).read_text(encoding="utf-8")
    assert f"<strong>{cov} of {n}</strong>" in page and f"<strong>{conf} of {n}</strong>" in page
    assert "COVERAGE" in page and "INDEPENDENTLY CONFIRMED" in page and cov >= conf


def test_PLANT_codex_review_2026_10_03_four_miscount_inputs_are_refused():
    # 1. a comparator-sourced row is never confirmation, whatever route it carries
    r = g1.recompute(_rec([dict(_cs("A"), route="PRIMARY", in_our_pool=True)]))
    assert (r["g1_count"], r["covered"], r["comparator_sourced"]) == (0, 1, 1) and not r["matched"]
    # 2. unidentifiable 'sources' are not two sources
    assert g1.recompute(_rec([_two("A", ["", "unknown"])]))["g1_count"] == 0
    # 3. 'PMID: <comparator>' is still the comparator
    assert g1.recompute(_rec([_two("A", ["TEXT PMID 33472855", f"PMID: {COMP}"])]))["g1_count"] == 0
    # 4. a 'comparator-sourced' row read from ANOTHER meta is not comparator coverage
    r4 = g1.recompute(_rec([_t("A"), _cs("B", meta="33745918")], k=1, named=("B",)))
    assert (r4["covered"], r4["comparator_sourced"]) == (1, 0)


def test_PLANT_secondary_single_provenance_recorded_under_secondary_single_counts():
    # the tracker's non-sweep SECONDARY_SINGLE route records its meta / location / digest under
    # secondary_single.provenance (probiotics Cimperman: meta 24348885, figure2 panel A); the renderer read only
    # sweep.basis and refused 11 such rows as 'unrecorded' (consolidation 2026-10-04)
    t = _t("A", route="SECONDARY_SINGLE", secondary_single={"provenance": {
        "meta_pmid": "24348885", "where": "figure figure2 panel A", "digest": "8" * 64}})
    assert g1.recompute(_rec([t]))["g1_count"] == 1
    circ = _t("A", route="SECONDARY_SINGLE", secondary_single={"provenance": {
        "meta_pmid": COMP, "where": "figure 2", "digest": "8" * 64}})
    assert g1.recompute(_rec([circ]))["g1_count"] == 0
    bare = _t("A", route="SECONDARY_SINGLE", secondary_single={"provenance": {"meta_pmid": "24348885"}})
    assert g1.recompute(_rec([bare]))["g1_count"] == 0


def test_PLANT_a_trial_named_out_of_scope_is_neither_covered_nor_confirmed():
    # a comparator trial NAMED out of scope (rule + span) leaves the eligible set: it is not a coverage or a
    # confirmation of the comparator's N even when its own report verifies it (glp1 ELIXA: PRIMARY-verified, an
    # ESTIMAND_DIFFERENCE). The renderer counted 3 such trials the tracker does not (consolidation 2026-10-04).
    t = _t("A", route="PRIMARY", pooled=False, scope_difference={"kind": "ESTIMAND_DIFFERENCE", "rule_id": "GATE:x"})
    r = g1.recompute(_rec([_t("B"), t], named=("A",)))
    assert (r["g1_count"], r["covered"]) == (1, 1)
    assert "named out of scope" in r["rows"][1]["why"]
