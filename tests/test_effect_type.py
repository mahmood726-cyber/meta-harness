"""Lane TY plants. Numeric fixtures are read from held source records."""
import copy
import importlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def api():
    return importlib.import_module("harness.effect_type")


def target(axis, value):
    return {"binding_axes": [axis], "axes": {axis: {"value": value, "basis": {"rule_id": "fixture:protocol"}}}}


def test_freedom_censoring_plant():
    reg = read("outputs/handover/glp1_regulatory/regulatory_sources_glp1.json")
    source = next(s for s in reg["sources"] if any(d["trial"] == "FREEDOM-CVO" for d in s["decisions"]))
    eos = source["decisions"][0]
    eot = next(r for r in read("outputs/handover/glp1_reviewerB/reviewB_extraction.json")["records"] if r["trial_acronym"] == "FREEDOM-CVO")["three_point_mace"]
    assert eos["effect"]["estimate"] == 1.24 and eot["hr"] == 1.36
    ty = api()
    first = ty.build_effect({"id": eos["trial_key"], "source": eos["span"]})
    second = ty.build_effect({"id": eos["trial_key"], "source": eot["analysis_set"] + ": " + eot["span"]})
    t = target("censoring", "end-of-study")
    assert ty.unify(t, first)["status"] == "MATCH"
    result = ty.unify(t, second)
    assert result["status"] == "REFUSE" and result["axis"] == 8
    assert "end-of-treatment" in result["reason"]


def test_elixa_components_coercion_plant():
    row = next(r for r in read("outputs/handover/glp1_reviewerB/reviewB_extraction.json")["records"] if r["trial_acronym"] == "ELIXA")
    effect = row["four_point_mace_if_reported"]
    assert [effect[k] for k in ("hr", "ci_low", "ci_high")] == [1.02, .89, 1.17]
    ty = api()
    e = ty.build_effect({"id": row["pmid"], "source": row["primary_endpoint_of_trial"] + ". " + effect["span"]})
    t = target("endpoint_components", ["CV_DEATH", "NONFATAL_MI", "NONFATAL_STROKE"])
    assert ty.unify(t, e)["axis"] == 4
    c = {"coercion_id": "TEST-ONLY-ELIXA", "who": "fixture", "why": "test only, not clinical authorization", "evidence_spans": [{"source": "fixture:ELIXA", "span": effect["span"]}], "date": "2026-09-17", "consequence": "fixture removes UA_HOSP", "signed_by": "fixture signer", "axis": "endpoint_components", "from": e["axes"]["endpoint_components"]["value"], "to": t["axes"]["endpoint_components"]["value"]}
    v = ty.unify(t, e, [c])
    assert v["status"] == "MATCH_WITH_DECLARED_COERCION"
    from harness.page import typed_effects_html
    rendered = typed_effects_html({"effect_types": [dict(e, unification=v)], "coercions": [c]})
    assert "TEST-ONLY-ELIXA" in rendered and "fixture:ELIXA" in rendered
    bad = copy.deepcopy(c)
    del bad["signed_by"]
    assert ty.unify(t, e, [bad])["status"] == "REFUSE"


def test_unstated_binding_plant():
    ty = api()
    row = {"id": "fixture", "analysis_set": "unstated"}
    e = ty.build_effect(row)
    t = target("analysis_set", "ITT")
    assert ty.unify(t, e)["status"] == "UNKNOWN_FAILS_CLOSED"
    kept, refused, _ = ty.type_rows([row], t)
    assert not kept and len(refused) == 1
    t["binding_axes"] = []
    v = ty.unify(t, e)
    assert v["status"] == "MATCH"
    assert "axis 3 unstated" in v["disclosures"]


def test_current_glp1_baseline_plant():
    review = read("docs/reviews/glp1-ra-mace-t2d/review.json")
    outcome = next(o for o in review["outcomes"] if o.get("primary"))
    assert len(outcome["trials"]) == 8
    records = {str(r["id"]): r for r in read("cache/glp1-ra-mace-t2d/records.json")["records"]}
    ty = api()
    for row in outcome["trials"]:
        e = ty.build_effect(row, records.get(row["id"].replace("PMID ", "")))
        assert len(e["axes"]) == 12
        assert e["known_axes"] + len(e["unknown_axes"]) == 12
        # A protocol-inherited analysis population is NOT trial evidence.
        if "intention-to-treat" not in (records.get(row["id"].replace("PMID ", ""), {}).get("abstract", "").lower()):
            assert e["axes"]["analysis_set"]["value"] == "UNKNOWN"


def test_pipeline_gate_and_render_contract(tmp_path):
    from harness import pipeline, gate, page
    config = read("topics/glp1-ra-mace-t2d.json")
    records = {str(r["id"]): r for r in read("cache/glp1-ra-mace-t2d/records.json")["records"]}
    # Actual held trial lacking an explicitly stated analysis set.
    spec = dict(config["primary_outcome"], primary=True,
                effect_type_target=target("analysis_set", "ITT"))
    included = [{"id": "31185157", "id_type": "pmid", "decision": "include"}]
    out = pipeline._build_outcome(spec, "efficacy", included, records,
                                  config["intervention_terms"], config["comparator_terms"])
    assert out["result"]["k"] == 0 and not out["trials"]
    assert out["effect_type_counts"] == {"candidate_rows": 1, "accepted_rows": 0, "refused_rows": 1}
    html = page.render_outcome_block(out)
    assert "UNTYPED — axis 3 unknown" in html and "Typed effects" in html
    assert html.count('<td class=') == 12
    # Nonbinding protocol fixture permits the same extracted row; gate checks
    # the attached decision against the type, not an optimistic status string.
    spec["effect_type_target"]["binding_axes"] = []
    accepted = pipeline._build_outcome(spec, "efficacy", included, records,
                                       config["intervention_terms"], config["comparator_terms"])
    assert accepted["result"]["k"] == 1
    review = {"outcomes": [accepted]}
    assert api().check_review(review) == []
    accepted["trials"][0]["unification"] = {"status": "REFUSE"}
    (tmp_path / "review.json").write_text(json.dumps(review), encoding="utf-8")
    assert gate.check_effect_types(tmp_path)


def test_unknown_cannot_be_coerced_and_unbound_unknown_visible():
    ty = api()
    e = ty.build_effect({"analysis_set": "ITT", "study_effect": {"analysis_population": "ITT"}})
    assert not ty.known(e["axes"]["analysis_set"])
    assert ty.unify(target("analysis_set", "ITT"), e)["status"] == "UNKNOWN_FAILS_CLOSED"
    # Endpoint tokens are sets, not order-sensitive strings.
    a = ty.build_effect({"source": "cardiovascular death, nonfatal myocardial infarction and nonfatal stroke"})
    assert ty.unify(target("endpoint_components", ["NONFATAL_STROKE", "CV_DEATH", "NONFATAL_MI"]), a)["status"] == "MATCH"


def test_arm_background_and_documented_population():
    ty = api()
    f = lambda v: {"value": v, "span": "fixture arm record"}
    row = {"drug_of_interest": "drug A", "population_fields": ["entry_condition"],
           "arm_object": {"population": {"entry_condition": f("T2D")},
                          "randomised_arm": [{"drug": f("drug A"), "background_therapy": f("usual care")},
                                             {"drug": f("placebo"), "background_therapy": f("usual care")}]}}
    e = ty.build_effect(row)
    assert e["axes"]["randomised_contrast"]["value"] is True
    assert e["axes"]["population"]["value"] == {"entry_condition": "T2D"}
    row["arm_object"]["randomised_arm"][1]["background_therapy"] = f("different care")
    assert ty.unify(target("randomised_contrast", True), ty.build_effect(row))["status"] == "REFUSE"


def test_sweep_is_deterministic_and_does_not_rewrite_pages():
    from scripts.effect_type_sweep import sweep
    import hashlib
    paths = sorted((ROOT / "docs/reviews").glob("*/*"))
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
    a, b = sweep(), sweep()
    assert a == b and a["topic_count"] == 32
    assert before == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}


def test_regulatory_document_digest_and_two_distinct_table_rows():
    import hashlib
    import re
    reg = read("outputs/handover/glp1_regulatory/regulatory_sources_glp1.json")
    s = next(s for s in reg["sources"] if s["source_id"] == "FDA_NDA209053_EMDAC_briefing_2023")
    path = ROOT / s["held"]["held_in_tree"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == s["document_sha256"]
    text = (ROOT / s["held"]["extracted_text"]).read_text(encoding="utf-8")
    assert hashlib.sha256((ROOT / s["held"]["extracted_text"]).read_bytes()).hexdigest() == s["extracted_text_sha256"]
    folded = re.sub(r"\s+", " ", text)
    assert "1.24 (0.90, 1.70)" in folded and "1.36 (0.96, 1.92)" in folded
    assert "ITT Population End of Study" in folded and "ITT Population End of Treatment" in folded
    decision = s["decisions"][0]
    e = api().build_effect({"id": decision["trial_key"], "source": decision["span"],
                            "report_source": {"kind": "regulatory FDA/EMA", "source_level": 2,
                                              "span": decision["span"], "document_path": s["held"]["held_in_tree"],
                                              "document_sha256": s["document_sha256"]}})
    assert e["axes"]["report"]["value"]["document_sha256"] == s["document_sha256"]


def test_invalid_enum_and_duplicate_coercion_fail_closed(tmp_path):
    import pytest
    ty = api()
    e = ty.build_effect({"effect_type_evidence": {"analysis_set": {"value": "made-up", "basis": {"rule_id": "fixture"}}}})
    assert ty.unify(target("analysis_set", "ITT"), e)["status"] == "UNKNOWN_FAILS_CLOSED"
    p = tmp_path / "coercions.json"
    p.write_text('[{}]', encoding="utf-8")
    with pytest.raises(ValueError):
        ty.load_coercions(p)
