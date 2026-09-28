"""NOAC-AF and PCSK9 fixtures, 2026-09-28 (plants included)."""
import copy
import json
import os

import pytest

from harness import (absence, fetch, hand_binding, outcome_restriction as orx, pipeline, reason_audit,
                     registry_publications as rp, result_status as rs, source_versions as sv, target_endpoint as te)
from harness.synth import Study, pool

ROOT = pipeline.ROOT
NOAC, PCSK9 = "noac-vs-warfarin-af-stroke", "pcsk9-mace"
SSE, MB = "Stroke or systemic embolism", "Major bleeding"
MACE, ISR, DISC = "Major adverse cardiovascular events", "Injection-site reactions", "Adverse events leading to discontinuation"
_R = {}


def _rv(slug):
    if slug not in _R:
        cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
        _R[slug] = pipeline.build_review_core(slug, cfg, fetch.ensure(cfg, ""), "test")
    return _R[slug]


def _o(rv, name):
    return next(o for o in rv["outcomes"] if o["name"] == name)


def _row(slug, outcome, pid, pooled=False):
    o = _o(_rv(slug), outcome)
    return next(t for t in (o["trials"] if pooled else o["declared_absent_trials"]) if pid in str(t["id"]))


# ------------------------------------------------------------------------------------------------ NOAC-AF
def test_rely_stroke_se_governing_version_is_decided_and_served():
    row = _row(NOAC, SSE, "19717844", pooled=True)
    ch = row["version_chain"]
    assert ch["governing"] == {**ch["governing"], "state": "DECIDED", "version_id": "v3-fda-label-2024-01"}
    assert (row["effect"], row["ci_low"], row["ci_high"], row["scale"]) == (0.65, 0.52, 0.81, "HR")
    ids = [v["version_id"] for v in ch["versions"]]
    assert ids == ["v0-article-2009", "v1-fda-label-2010-10", "v2-correspondence-2010-11", "v3-fda-label-2024-01", "v3b-ema-smpc"]
    assert not next(v for v in ch["versions"] if v["version_id"] == "v2-correspondence-2010-11")["held"]
    # PLANT: the original 2009 value served under the DECIDED chain -> refused
    rv = copy.deepcopy(_rv(NOAC))
    r = next(t for t in _o(rv, SSE)["trials"] if "19717844" in t["id"])
    r.update(effect=0.66, ci_low=0.53, ci_high=0.82)
    assert "VERSION_SUPERSEDED_SERVED" in [p["kind"] for p in sv.problems(rv)]


def test_rely_diagnostic_pools_reproduce_both_versions():
    o = _o(_rv(NOAC), SSE)
    S = lambda t, e=None: Study(label=t["id"], effect=(e or (t["effect"],))[0], ci_low=(e or (0, t["ci_low"]))[1],
                                ci_high=(e or (0, 0, t["ci_high"]))[2], measure="HR")
    served = pool([S(t) for t in o["trials"]], scale="HR")
    original = pool([S(t, (0.66, 0.53, 0.82)) if "19717844" in t["id"] else S(t) for t in o["trials"]], scale="HR")
    assert round(served.estimate, 4) == 0.8040 and round(original.estimate, 4) == 0.8069
    assert served.ci_high < 1 and original.ci_high < 1                       # the conclusion does not change


def test_major_bleeding_rely_pending_and_rocket_on_treatment_are_bound():
    rely = _row(NOAC, MB, "19717844", pooled=True)
    assert rely["hand_binding_state"] == hand_binding.BOUND and rely["version_chain"]["governing"]["state"] == "PENDING"
    vs = {v["version_id"]: v for v in rely["version_chain"]["versions"]}
    # an identical effect tuple never establishes an identical version: 0.93 (0.81-1.07) with 375/397 and with 399/421
    assert vs["v0-article-2009"]["relayed_value"]["ai"] == 375 and vs["v1-fda-label-2010-10"]["value"]["ai"] == 399
    assert "DIFFERENT ANALYSIS POPULATION" in vs["x-fda-label-2024-01-treated"]["relation"]
    rocket = _row(NOAC, MB, "21830957", pooled=True)
    assert (rocket["effect"], rocket["ci_low"], rocket["ci_high"]) == (1.04, 0.90, 1.20)
    assert rocket["hand_binding_state"] == hand_binding.BOUND and "On Treatment" in rocket["analysis_set"]


def test_rocket_major_plus_crnm_composite_never_binds_to_major_bleeding():
    cfg = json.load(open(os.path.join(ROOT, "topics", NOAC + ".json"), encoding="utf-8"))
    spec = cfg["harm_outcomes"][0]
    # PLANT: the principal safety composite's tuple offered as major bleeding, against the held abstract
    out = hand_binding.bind_hand_row(spec, {"id": "PMID 21830957", "effect": 1.03, "ci_low": 0.96, "ci_high": 1.11,
                                            "scale": "HR", "document_ref": f"cache/{NOAC}/records.json#PMID-21830957"})
    assert not (out["hand_binding_state"] == hand_binding.BOUND and out["target_endpoint_class"] == te.EXACT_TARGET)


def test_ing_keyword_matches_its_event_noun_as_a_whole_word_only():
    spec = {"name": "Major bleeding", "keywords": ["major bleeding"]}
    assert te._keyword_family_match(spec, "Major bleed | 399 (3.3) | 421 (3.6)")
    assert te._keyword_family_match(spec, "major bleeds were fewer")
    assert not te._keyword_family_match(spec, "major bleeder registry")          # PLANT: a longer word
    assert not te._keyword_family_match({"name": "x", "keywords": ["sing"]}, "s")  # stem shorter than 4: no match


def test_edoxaban_phase_ii_publications_are_reports_of_their_registrations():
    chung = _row(NOAC, SSE, "NCT00806624")
    assert chung["linked_publication"]["pmid"] == "21136011"
    assert chung["result_status"]["state"] == rs.REPORTED_ZERO_EVENTS
    assert chung["result_status"]["span"] == "No thromboembolic events occurred in any treatment group."
    yam = _row(NOAC, SSE, "NCT00829933")
    assert yam["result_status"]["state"] == rs.REPORTED_ZERO_EVENTS and "45 mg" in yam["result_status"]["note"]
    ymb = _row(NOAC, MB, "NCT00829933")
    assert ymb["result_status"]["state"] == rs.EXTRACTED_NOT_ADMITTED
    assert (ymb["held_out_row"]["ai"], ymb["held_out_row"]["n1i"], ymb["held_out_row"]["ci"], ymb["held_out_row"]["n2i"]) == (2, 130, 0, 125)
    weitz = _row(NOAC, SSE, "NCT00504556")
    assert weitz["result_status"]["state"] == rs.NOT_YET_RETRIEVED and weitz["linked_publication"]["coverage"] == "ABSTRACT_ONLY"
    pooled = {str(t["id"]) for o in _rv(NOAC)["outcomes"] for t in o["trials"]}
    assert not pooled & {"NCT00504556", "NCT00806624", "NCT00829933", "PMID 20694273", "PMID 21136011", "PMID 22664798"}


def test_a_registry_publication_state_fails_closed_on_its_witness(monkeypatch):
    links = rp.load(NOAC)
    y = copy.deepcopy(next(x for x in links if x["registration"] == "NCT00829933"))
    y["per_outcome"][MB]["held_out_row"]["ai"] = 7                       # PLANT: a count not in the witnessed span
    c = copy.deepcopy(next(x for x in links if x["registration"] == "NCT00806624"))
    c["per_outcome"][SSE]["zero_events_span"] = "No events occurred."     # PLANT: a zero span that is not the witness
    w = copy.deepcopy(next(x for x in links if x["registration"] == "NCT00806624"))
    w["per_outcome"][SSE]["witness"]["span"] = "No thromboembolic events occurred in the warfarin group."  # PLANT: unheld
    for bad in (y, c, w):
        monkeypatch.setattr(rp, "load", lambda slug, root=None, _b=bad: [_b])
        with pytest.raises(ValueError):
            rp.attach(copy.deepcopy(_rv(NOAC)), NOAC)


def test_j_rocket_is_a_known_eligible_trial_with_all_three_analyses_not_pooled():
    rv = _rv(NOAC)
    km = _o(rv, SSE)["known_missing_sensitivity"]
    j = next(r for r in km["rows"] if r["trial_key"] == "J-ROCKET AF")
    assert j["result_status"]["state"] == rs.EXTRACTED_NOT_ADMITTED
    assert [a["effect"] for a in j["result_status"]["analyses"]] == [0.49, 0.82, 0.48]
    assert "ITT including 30-day follow-up" in j["result_status"]["span"] or "30-day follow-up" in j["result_status"]["span"]
    assert "COMPATIBILITY DECISIONS PENDING" in j["design_note"]
    assert not any("22664783" in str(t["id"]) or "NCT00494871" in str(t["id"]) for o in rv["outcomes"] for t in o["trials"])
    assert "known_eligible_missing" in [x.get("code") for x in (rv.get("invalidation") or {}).get("reasons", [])]


# ------------------------------------------------------------------------------------------------ PCSK9
def test_glagov_mace_is_never_not_reported_and_its_relayed_counts_are_not_data():
    g = _row(PCSK9, MACE, "27846344")
    assert g["result_status"]["state"] == rs.NOT_YET_RETRIEVED
    assert "59/484" in g["relayed_not_held"]["value"]
    assert not any("27846344" in str(t["id"]) for t in _o(_rv(PCSK9), MACE)["trials"])


def test_component_rows_are_never_summed_into_a_patient_composite():
    rv = copy.deepcopy(_rv(PCSK9))
    _o(rv, MACE)["trials"].append({"id": "PMID 27846344", "ai": 59, "n1i": 484, "ci": 74, "n2i": 484,
                                   "components_summed": True})                         # PLANT
    assert "COMPONENT_SUM_AS_COMPOSITE" in [p["kind"] for p in orx.problems(rv)]
    rv2 = copy.deepcopy(_rv(PCSK9))
    _o(rv2, MACE)["trials"].append({"id": "PMID 27846344", "ai": 60, "n1i": 484, "ci": 80, "n2i": 484,
                                    "derivation": "sum of the component rows of Table 4"})   # PLANT
    assert "COMPONENT_SUM_AS_COMPOSITE" in [p["kind"] for p in orx.problems(rv2)]


def test_odyssey_long_term_post_hoc_refusal_stands_and_its_hr_does_not_lift_it():
    lt = _row(PCSK9, MACE, "25773378")
    assert lt["result_status"]["state"] == rs.EXTRACTED_NOT_ADMITTED
    assert lt["reason_code_audit"]["verdict"] == reason_audit.REASON_TRUE
    assert orx.problems(_rv(PCSK9)) == []
    # PLANT: the post-hoc row pooled -> refused
    rv = copy.deepcopy(_rv(PCSK9))
    _o(rv, MACE)["trials"].append({"id": "PMID 25773378", "effect": 0.52, "ci_low": 0.31, "ci_high": 0.90,
                                   "source_span": lt["source_span"]})
    assert "POST_HOC_POOLED" in [p["kind"] for p in orx.problems(rv)]
    # PLANT: the same code on a value whose span does NOT say post hoc stays falsifiable
    spec = {"name": MACE, "keywords": ["major adverse cardiovascular events"]}
    src = [{"source_id": "abstract:x", "source_kind": "abstract",
            "text": "The rate of major adverse cardiovascular events was lower (hazard ratio, 0.52; 95% CI, 0.31 to 0.90)."}]
    out = reason_audit.audit_reason_row({"name": MACE}, {"reason_code": absence.OUTCOME_POST_HOC_NOT_POOLED}, src, spec)
    assert out["verdict"] == reason_audit.REASON_FALSE_VALUE_HELD


def test_safety_rows_recovered_from_the_trials_table_3s():
    f = _row(PCSK9, ISR, "28304224", pooled=True)
    o = _row(PCSK9, ISR, "30403574", pooled=True)
    d = _row(PCSK9, DISC, "30403574", pooled=True)
    assert (f["ai"], f["n1i"], f["ci"], f["n2i"]) == (296, 13769, 219, 13756)
    assert (o["ai"], o["n1i"], o["ci"], o["n2i"]) == (360, 9451, 203, 9443)
    assert (d["ai"], d["n1i"], d["ci"], d["n2i"]) == (343, 9451, 324, 9443)
    assert all(r["hand_binding_state"] == hand_binding.BOUND and "safety population" in r["safety_population"] for r in (f, o, d))


def test_treatment_attributed_and_single_cause_discontinuation_are_other_outcomes():
    fd = _row(PCSK9, DISC, "28304224")
    assert fd["result_status"]["state"] == rs.EXTRACTED_NOT_ADMITTED and fd["attribution"] == "TREATMENT_ATTRIBUTED"
    assert (fd["held_out_row"]["ai"], fd["held_out_row"]["ci"]) == (226, 201)
    # PLANT: the attribution-restricted row pooled into the unrestricted outcome
    rv = copy.deepcopy(_rv(PCSK9))
    _o(rv, DISC)["trials"].append({"id": "PMID 28304224", "ai": 226, "n1i": 13769, "ci": 201, "n2i": 13756,
                                   "source_span": fd["source_span"]})
    assert "OUTCOME_RESTRICTION_MISMATCH" in [p["kind"] for p in orx.problems(rv)]
    # PLANT: ODYSSEY's 26 vs 3 injection-site discontinuations pooled as overall discontinuation
    rv2 = copy.deepcopy(_rv(PCSK9))
    span26 = rv2["outcome_restrictions"][DISC]["examples_refused"]["ODYSSEY OUTCOMES"]
    for t in _o(rv2, DISC)["trials"]:
        if "30403574" in t["id"]:
            t.update(ai=26, ci=3, source_span=span26, verbatim_span=span26)
    assert "OUTCOME_RESTRICTION_MISMATCH" in [p["kind"] for p in orx.problems(rv2)]


def test_a_post_hoc_typed_refusal_needs_a_span_that_says_post_hoc(tmp_path):
    d = tmp_path / "cache" / "t"
    d.mkdir(parents=True)
    (d / "records.json").write_text(json.dumps({"records": [{"id": "1", "abstract": "MACE was lower (HR 0.52; 95% CI 0.31 to 0.90)."}]}), encoding="utf-8")
    from harness import verified_inputs as vi
    entry = vi.normalise({"outcome": MACE, "absent": True, "override": True, "state": absence.OUTCOME_POST_HOC_NOT_POOLED,
                          "reason": "post hoc", "source_span": "MACE was lower (HR 0.52; 95% CI 0.31 to 0.90)."})
    with pytest.raises(ValueError, match="post hoc"):
        vi._validate(entry, d, "1", canonical=True)                                   # PLANT
