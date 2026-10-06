"""PLANTS: statins-primary-prevention-elderly comparator replacement (Mahmood 5 Oct, "go with a").

1 selection   the pre-registered rule (6713b9d17) alone picks nothing; Mahmood's RATIFIED exception waives C6 for
              32529863 ONLY, and only with decided_by + quote + date recorded
2 type        COMPARATOR_NO_PER_TRIAL_ROWS: per-trial comparison NOT_AVAILABLE_FROM_COMPARATOR, never comparator-side
              confirmation, RESULT agreement only from OUR verified rows for the SAME trial set
3 ledger      the old comparator 39076238 is retired COMPARATOR_POOLS_NO_RCT with spans verbatim in its held text
4 enumeration the comparator's result trial set (refs 29, 35-40) reaches the tracker as N = 7 through k_gap_table."""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))

SLUG = "statins-primary-prevention-elderly"
SEL = os.path.join(ROOT, "registry", "comparator_selection")


def _j(p):
    return json.load(open(p, encoding="utf-8"))


def test_rule_alone_picks_nothing_and_the_ratified_exception_picks_32529863_only():
    import g1_comparator_select as cs
    rule = _j(os.path.join(SEL, SLUG + ".rule.json"))
    cands = _j(os.path.join(SEL, SLUG + ".candidates.json"))["candidates"]
    exc = _j(os.path.join(SEL, SLUG + ".ratification.json"))["ratified_exception"]
    assert exc["quote"] == "go with a" and exc["date"] == "2026-10-05" and exc["decided_by"] == "Mahmood"
    assert cs.select(rule, cands) == (None, [])
    pick, ranked = cs.select(rule, cands, exc)
    assert pick["pmid"] == "32529863" and len(ranked) == 1
    # the waiver never reaches another candidate, and needs who/quote/date
    assert cs.select(rule, cands, dict(exc, candidate_pmid="31919804")) == (None, [])
    assert cs.select(rule, cands, dict(exc, quote=None)) == (None, [])
    sel = _j(os.path.join(SEL, SLUG + ".selection.json"))
    assert sel["rule_commit"].startswith("6713b9d17") and sel["result_under_preregistered_rule"] == "NO_ACHIEVABLE_COMPARATOR"
    assert sel["result"] == "PICKED_BY_RATIFIED_EXCEPTION" and sel["n_candidates"] == 26


def test_adoption_verifies_against_the_held_comparator():
    import g1_tracker as gt
    a = gt.no_rows_adoption(SLUG, "32529863")
    assert a and a["comparator_type"] == "COMPARATOR_NO_PER_TRIAL_ROWS" and a["pooled_result"]["k"] == 7
    assert gt.no_rows_adoption(SLUG, "39076238") is None                 # not for another comparator
    assert _j(os.path.join(ROOT, "topics", SLUG + ".json"))["comparator_pmid"] == "32529863"


def _o(rows):
    trials = []
    for i, v in enumerate(rows):
        x = {"label": f"T{i}", "in_our_pool": v is not None, "route": "PRIMARY" if v else "NO_ROW",
             "g1_countable": bool(v), "comparator_row": {"effect": "0.5"}, "agreement_with_comparator_row": "AGREE"}
        if v:
            x["our_value"] = dict(zip(("events_t", "n_t", "events_c", "n_c"), v))
        trials.append(x)
    return {"slug": SLUG, "comparator_pmid": "32529863", "trials": trials}


def test_per_trial_is_not_available_and_never_comparator_confirmation():
    import g1_tracker as gt
    o = _o([(10, 100, 12, 100)] + [None] * 6)
    st = gt.apply_no_rows_comparator(o)
    assert st["state"] == "OUR_ROWS_INCOMPLETE" and st["verdict"]["verdict"] == "NOT_COMPUTABLE"
    assert all(x["comparator_row"] is None and x["comparator_data_confirmation"] == "NONE" for x in o["trials"])
    assert o["trials"][0]["agreement_with_comparator_row"] == "NOT_AVAILABLE_FROM_COMPARATOR"
    assert o["per_trial_agreement"] == {"NOT_AVAILABLE_FROM_COMPARATOR": 1}


def test_result_agreement_is_computed_from_our_rows_for_the_whole_set():
    import g1_tracker as gt
    o = _o([(88, 1000, 100, 1000)] * 7)                     # each OR ~0.87: pooled near the comparator's 0.88
    st = gt.apply_no_rows_comparator(o)
    assert st["state"] == "OURS_POOLED_VS_COMPARATOR_POOLED_RESULT" and st["k_ours_verified"] == 7
    assert st["verdict"]["verdict"] in ("AGREE", "SAME_CONCLUSION_DIFFERENT_ESTIMATE", "DIFFERENT_CONCLUSION")
    assert st["theirs"]["estimate"] == 0.88 and st["per_trial"] == "NOT_AVAILABLE_FROM_COMPARATOR"
    o2 = _o([(30, 1000, 100, 1000)] * 7)                    # a clear benefit: different conclusion from 0.72-1.06
    assert gt.apply_no_rows_comparator(o2)["verdict"]["verdict"] == "DIFFERENT_CONCLUSION"


def test_a_changed_held_source_disables_the_adoption(tmp_path, monkeypatch):
    import g1_tracker as gt
    a = _j(os.path.join(SEL, SLUG + ".adoption.json"))
    bad = copy.deepcopy(a)
    bad["pooled_result"]["source"]["sha256"] = "0" * 64
    p = tmp_path / f"{SLUG}.adoption.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    monkeypatch.setattr(gt, "NO_ROWS_ADOPTION", str(tmp_path / "{slug}.adoption.json"))
    assert gt.no_rows_adoption(SLUG, "32529863") is None
    bad2 = copy.deepcopy(a)
    bad2["pooled_result"]["spans"]["result"] = a["pooled_result"]["spans"]["result"].replace("0.88", "0.70")
    p.write_text(json.dumps(bad2), encoding="utf-8")
    assert gt.no_rows_adoption(SLUG, "32529863") is None    # a span not in the held source


def test_old_comparator_retired_with_verbatim_spans_in_the_ledger():
    import g1_denominator_ledger as dl
    r = dl.retired_comparator(SLUG, "32529863")
    assert r and r["retired_pmid"] == "39076238" and r["reason_code"] == "COMPARATOR_POOLS_NO_RCT"
    assert len(r["span"]["parts"]) == 2 and "12 observational studies" in r["span"]["parts"][0]
    assert dl.retired_comparator(SLUG, "39076238") is None
    led = {"removed": [{"slug": SLUG, "label": "Lemaitre et al. [24], 2002 (USA)", "kind": "COMPARATOR_RETIRED",
                        "rule_id": "COMPARATOR_RETIRED:COMPARATOR_POOLS_NO_RCT", "span": r["span"]}],
           "baseline": {"N": 1}, "removed_n": 1, "added_n": 0, "current": {"N": 0}}
    assert dl.problems(led) == []
    tampered = copy.deepcopy(led)
    tampered["removed"][0]["span"]["parts"][0] = "A total of 12 randomised trials"
    assert dl.problems(tampered)


def test_enumeration_is_the_result_trial_set_and_reaches_k_gap_table():
    import k_gap_table as kt
    us = kt.enumeration_units(SLUG, ["statin", "statins", "rosuvastatin", "pravastatin", "atorvastatin"])
    assert [u["rids"][0] for u in us] == ["29", "35", "36", "37", "38", "39", "40"]
    assert all(u["cited"][0]["pmid"] for u in us)


@pytest.mark.skipif(not os.path.exists(os.path.join(ROOT, "outputs", "k_gap", "_aact_store.json")),
                    reason="needs the local AACT store (gitignored cache)")
def test_tracker_shows_comparator_n_7_and_no_rows_type():
    import k_gap_table as kt
    import g1_tracker as gt
    T = kt.main(["--offline", f"--only={SLUG}", "--no-write"])
    tp = next(t for t in T["topics"] if t["slug"] == SLUG)
    assert tp["comparator_set_state"] == "ENUMERATED" and tp["comparator_units"] == 7
    o = gt.topic(SLUG, T)
    assert o["comparator_pmid"] == "32529863" and o["N_comparator_trials"] == 7
    assert o["comparator_type"] == "COMPARATOR_NO_PER_TRIAL_ROWS"
    assert set(o["per_trial_agreement"]) <= {"NOT_AVAILABLE_FROM_COMPARATOR"}
    assert gt.scope_citation_violations(o) == []
