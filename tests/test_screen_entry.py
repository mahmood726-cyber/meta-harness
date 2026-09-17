import copy
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import extract, pipeline, screen  # noqa: E402


BASE = "ad5e7c66"


def _topic(slug):
    with open(os.path.join("topics", f"{slug}.json"), encoding="utf-8") as f:
        return json.load(f)


def _cache(slug):
    with open(os.path.join("cache", slug, "records.json"), encoding="utf-8") as f:
        data = json.load(f)
    return pipeline._dedup(data, _topic(slug).get("pivotal_trials"))


def _decisions(slug, records=None, config=None):
    return screen.run(records or _cache(slug), config or _topic(slug))["decisions"]


def _by_id(rows, key):
    for row in rows:
        if str(row.get("id")) == str(key):
            return row
    raise AssertionError(f"missing decision for {key}")


def _by_id_contains(rows, key):
    for row in rows:
        if str(key) in str(row.get("id")):
            return row
    raise AssertionError(f"missing decision containing {key}")


def _base_review(slug):
    raw = subprocess.check_output(
        ["git", "show", f"{BASE}:docs/reviews/{slug}/review.json"],
        text=True,
        encoding="utf-8",
    )
    return json.loads(raw)


def test_nct04385589_flips_from_diabetes_exclusion_to_include():
    pre = _by_id(_base_review("sglt2-hfref-hosp-cvdeath")["screening"]["records"], "NCT04385589")
    assert pre["decision"] == "exclude"
    assert pre["rule_id"] == "X2"
    assert "diabetic" in (pre.get("reason", "") + " " + pre.get("span", "")).lower()

    post = _by_id(_decisions("sglt2-hfref-hosp-cvdeath"), "NCT04385589")
    assert post["decision"] == "include"
    assert post["rule_id"] == "INCLUDE"
    assert post["completeness_state"] == "target outcome absent by design (short mechanistic/functional trial)"
    assert post["contrast_rule"] == "RANDOMISED_CONTRAST_PRESENT"


def test_nct06229678_remains_include_with_registry_lifecycle_fields():
    pre = _by_id(_base_review("sglt2-hfref-hosp-cvdeath")["screening"]["records"], "NCT06229678")
    assert pre["decision"] == "include"

    post = _by_id(_decisions("sglt2-hfref-hosp-cvdeath"), "NCT06229678")
    assert post["decision"] == "include"
    assert post["rule_id"] == "INCLUDE"
    for key in ("phase", "status", "primary_completion"):
        assert key in post
        assert post[key] is None
    assert post["completeness_state"] == "eligible ongoing mechanistic trial; target outcome absent by design"


def test_miro_ckd_is_evicted_as_absent_sglt2_contrast():
    pre = _by_id_contains(_base_review("sglt2-ckd-progression")["screening"]["records"], "NCT06350123")
    assert pre["decision"] == "include"

    post = _by_id(_decisions("sglt2-ckd-progression"), "NCT06350123")
    assert post["decision"] == "exclude"
    assert post["rule_id"] == "X-CONTRAST"
    assert post["contrast_rule"] == "CONTRAST_ABSENT"
    assert "balcinrenone" in post["reason"].lower()


def test_confidence_synthetic_positive_contrast_screens_then_refuses_kidney_outcome():
    cfg = _topic("finerenone-ckd-t2d-renal")
    rec = {
        "id": "CONFIDENCE-SYNTHETIC",
        "id_type": "pmid",
        "pubtypes": ["Randomized Controlled Trial"],
        "title": (
            "CONFIDENCE finerenone versus placebo in chronic kidney disease "
            "and type 2 diabetes"
        ),
        "abstract": (
            "Adults with chronic kidney disease and type 2 diabetes were randomly "
            "assigned in a double-blind trial to finerenone plus empagliflozin or "
            "placebo plus empagliflozin. The primary endpoint was change in UACR."
        ),
        "conditions": [],
        "interventions": ["finerenone plus empagliflozin", "placebo plus empagliflozin"],
        "masking": "DOUBLE",
    }

    decision = _decisions("finerenone-ckd-t2d-renal", records=[rec], config=cfg)[0]
    assert decision["decision"] == "include"
    assert decision["rule_id"] == "INCLUDE"
    assert decision["contrast_rule"] == "RANDOMISED_CONTRAST_PRESENT"

    out = extract.extract_trial(
        rec["abstract"],
        cfg["primary_outcome"]["keywords"],
        cfg["intervention_terms"],
        cfg["comparator_terms"],
        declared_composite=True,
        estimand=cfg["primary_outcome"]["estimand"],
    )
    assert out["absent"] is True


def test_diabetes_only_cvot_without_hfref_still_excluded():
    cfg = _topic("sglt2-hfref-hosp-cvdeath")
    rec = {
        "id": "DIABETES-CVOT",
        "id_type": "pmid",
        "pubtypes": ["Randomized Controlled Trial"],
        "title": "Empagliflozin cardiovascular outcomes in type 2 diabetes",
        "abstract": "Patients were randomly assigned to empagliflozin or placebo in a double-blind trial.",
        "conditions": ["Type 2 Diabetes"],
        "interventions": ["empagliflozin", "placebo"],
        "masking": "DOUBLE",
    }
    decision = _decisions("sglt2-hfref-hosp-cvdeath", records=[rec], config=cfg)[0]
    assert decision["decision"] == "exclude"
    assert decision["rule_id"] == "X2"


def test_dapa_hf_and_emperor_reduced_remain_included():
    rows = _decisions("sglt2-hfref-hosp-cvdeath")
    assert _by_id(rows, "31535829")["decision"] == "include"
    assert _by_id(rows, "32865377")["decision"] == "include"


def test_entry_condition_exception_is_removed_in_legacy_config():
    cfg = copy.deepcopy(_topic("sglt2-hfref-hosp-cvdeath"))
    cfg["include"].pop("population_none_entry_condition_only", None)
    cfg["include"].pop("comparator_overrides", None)
    legacy = _by_id(_decisions("sglt2-hfref-hosp-cvdeath", config=cfg), "NCT04385589")
    assert legacy["decision"] == "exclude"
    assert legacy["rule_id"] == "X2"
