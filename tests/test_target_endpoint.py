import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import protocol_compiler as PC  # noqa: E402
from harness import target_endpoint as TE  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _json(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


def _git_json(ref_path):
    raw = subprocess.check_output(["git", "show", ref_path], cwd=ROOT)
    return json.loads(raw)


def _trial(review, outcome_name, pmid):
    for outcome in review["outcomes"]:
        if outcome["name"] == outcome_name:
            for row in outcome.get("trials") or []:
                if str(row.get("id")) == f"PMID {pmid}":
                    return row
    raise AssertionError((outcome_name, pmid))


def test_sglt2_dapa_plant_prefixed_row_and_rebuilt_exact_target():
    old = _git_json("ad5e7c66:docs/reviews/sglt2-hfref-hosp-cvdeath/review.json")
    outcome = "Composite cardiovascular death or hospitalisation for heart failure"
    old_row = _trial(old, outcome, "31535829")
    assert (old_row["ai"], old_row["n1i"], old_row["ci"], old_row["n2i"]) == (386, 2373, 502, 2371)
    assert "primary outcome occurred in 386 of 2373" in old_row["source"]
    assert "urgent visit requiring intravenous therapy for heart failure" in old_row["components"]

    current = _json("docs/reviews/sglt2-hfref-hosp-cvdeath/review.json")
    row = _trial(current, outcome, "31535829")
    assert row["target_endpoint_class"] == TE.EXACT_TARGET
    assert row["effect"] == 0.75
    assert row["ci_low"] == 0.65
    assert row["ci_high"] == 0.85
    assert row["endpoint_counts"] == {"ai": 382, "n1i": 2373, "ci": 495, "n2i": 2371}
    assert "urgent heart failure visit" not in row.get("target_endpoint_components", [])


def test_sglt2_selector_prefers_exact_ctgov_target_over_near_abstract_primary():
    topic = _json("topics/sglt2-hfref-hosp-cvdeath.json")
    records = _json("cache/sglt2-hfref-hosp-cvdeath/records.json")
    rec = next(r for r in records["records"] if str(r["id"]) == "31535829")
    selected = TE.select_target_endpoint(
        topic["primary_outcome"],
        rec["abstract"],
        records["ctgov_results"]["NCT03036124"],
        topic["intervention_terms"],
        topic["comparator_terms"],
    )["selected"]
    assert selected["target_endpoint_class"] == TE.EXACT_TARGET
    assert selected["effect"] == 0.75
    assert selected["endpoint_counts"] == {"ai": 382, "n1i": 2373, "ci": 495, "n2i": 2371}
    assert any(a.get("target_endpoint_class") == TE.NEAR_MATCH for a in selected["target_endpoint_alternatives"])


def test_sglt2_emperor_reduced_is_exact_target():
    topic = _json("topics/sglt2-hfref-hosp-cvdeath.json")
    records = _json("cache/sglt2-hfref-hosp-cvdeath/records.json")
    rec = next(r for r in records["records"] if str(r["id"]) == "32865377")
    selected = TE.select_target_endpoint(
        topic["primary_outcome"],
        rec["abstract"],
        records["ctgov_results"]["NCT03057977"],
        topic["intervention_terms"],
        topic["comparator_terms"],
    )["selected"]
    assert selected["target_endpoint_class"] == TE.EXACT_TARGET
    assert selected["effect"] == 0.75
    assert selected["ci_low"] == 0.65
    assert selected["ci_high"] == 0.86


def test_fidelio_published_hr_beats_count_reconstruction():
    topic = _json("topics/finerenone-ckd-t2d-renal.json")
    records = _json("cache/finerenone-ckd-t2d-renal/records.json")
    rec = next(r for r in records["records"] if str(r["id"]) == "33264825")
    selected = TE.select_target_endpoint(
        topic["primary_outcome"],
        rec["abstract"],
        records.get("ctgov_results", {}).get("NCT02540993"),
        topic["intervention_terms"],
        topic["comparator_terms"],
    )["selected"]
    assert selected["effect"] == 0.82
    assert selected["ci_low"] == 0.73
    assert selected["ci_high"] == 0.93
    assert selected["scale"] == "HR"
    assert selected["target_endpoint_source_rank"] == TE.PUBLISHED_TARGET_EFFECT


def test_pcsk9_odyssey_generic_recurrent_phrase_is_not_endpoint_component():
    topic = _json("topics/pcsk9-mace.json")
    records = _json("cache/pcsk9-mace/records.json")
    rec = next(r for r in records["records"] if str(r["id"]) == "30403574")
    selected = TE.select_target_endpoint(
        topic["primary_outcome"],
        rec["abstract"],
        records["ctgov_results"]["NCT01663402"],
        topic["intervention_terms"],
        topic["comparator_terms"],
    )["selected"]
    assert "recurrent events" not in selected["target_endpoint_components"]


def test_synthetic_ctgov_exact_beats_abstract_near_match():
    spec = {
        "name": "Composite cardiovascular death or hospitalisation for heart failure",
        "keywords": ["cardiovascular death or hospitalization for heart failure", "primary outcome"],
        "estimand": "RR",
    }
    abstract = (
        "The primary outcome was worsening heart failure, including hospitalization or urgent visit "
        "for heart failure, or cardiovascular death. The primary outcome occurred in 10 of 100 drug "
        "patients and 20 of 100 placebo patients (hazard ratio, 0.50; 95% CI, 0.25 to 0.90)."
    )
    ctgov = [{
        "type": "SECONDARY",
        "title": "Cardiovascular Death or Hospitalization Due to Heart Failure",
        "paramType": "COUNT_OF_PARTICIPANTS",
        "groups": [{"id": "g1", "title": "Drug"}, {"id": "g2", "title": "Placebo"}],
        "classes": [{"categories": [{"measurements": [
            {"groupId": "g1", "value": "9"}, {"groupId": "g2", "value": "18"}]}]}],
        "denoms": [{"units": "Participants", "counts": [
            {"groupId": "g1", "value": "100"}, {"groupId": "g2", "value": "100"}]}],
    }]
    selected = TE.select_target_endpoint(spec, abstract, ctgov, ["drug"], ["placebo"])["selected"]
    assert selected["target_endpoint_class"] == TE.EXACT_TARGET
    assert (selected["ai"], selected["n1i"], selected["ci"], selected["n2i"]) == (9, 100, 18, 100)
    assert selected["provenance"] == "ctgov_results"


def test_sglt2_protocol_estimand_preference_undeclared():
    topic = _json("topics/sglt2-hfref-hosp-cvdeath.json")
    with open(os.path.join(ROOT, "protocols", "sglt2-hfref-hosp-cvdeath.md"), encoding="utf-8") as f:
        md = f.read()
    div = PC.compare("sglt2-hfref-hosp-cvdeath", md, topic)
    assert any(d["code"] == "ESTIMAND_PREFERENCE_UNDECLARED" for d in div)
