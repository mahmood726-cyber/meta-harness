"""The auditor reads a trial's OWN ClinicalTrials.gov results (pass 17; codex P17, verified corpus-wide: SALT-ED new RRT is the one
refusal that becomes REASON_FALSE_VALUE_HELD, as an independent held-out search had found), and a stage restricts (SALT-ED
'stage II or III' AKI is not 'Acute kidney injury')."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from copy import deepcopy
import json
from pathlib import Path

from harness import pipeline, reason_audit

ROOT = Path(__file__).resolve().parents[1]
SLUG = "balanced-crystalloids-vs-saline-mortality"


def plant():
    data = json.loads((ROOT / "cache" / SLUG / "records.json").read_text(encoding="utf-8"))
    record = next(r for r in data["records"] if r["id"] == "27749094")
    measure = next(m for m in data["ctgov_results"][record["nct"]]
                   if m["title"] == "New Use of Renal Replacement Therapy")
    review = json.loads(subprocess.run(["git", "-C", str(ROOT), "show", f"6260e70c:docs/reviews/{SLUG}/review.json"],
                                       capture_output=True, check=True).stdout)          # the SERVED page, not the regenerated one
    outcome = next(o for o in review["outcomes"] if o["name"] == "New renal-replacement therapy")
    row = next(r for r in outcome["declared_absent_trials"] if r["id"] == "PMID " + record["id"])
    specs = {s.get("name"): s for s, _ in pipeline._outcome_specs(
        json.loads((ROOT / "topics" / f"{SLUG}.json").read_text(encoding="utf-8")))}
    spec = {**specs[outcome["name"]], "target_population": review.get("question")}
    held = {"records": [record], "ctgov_results": {record["nct"]: [measure]}}
    return held, outcome, row, spec


def sources(held):
    return reason_audit.sources_by_trial(SLUG, held)["27749094"]


def test_registry_plant_answers_previously_unreachable_refusal():
    held, outcome, row, spec = plant()
    reached = sources(held)
    old_sources = [s for s in reached if s["source_kind"] != "registry_results"]
    assert reason_audit.audit_reason_row(outcome, row, old_sources, spec)["verdict"] == reason_audit.REASON_NOT_DISPROVED
    audit = reason_audit.audit_reason_row(outcome, row, reached, spec)
    assert audit["verdict"] == reason_audit.REASON_FALSE_VALUE_HELD
    assert audit["source_kind"] == "registry_results"
    ident = audit["evidence_identity"]
    assert ident["mismatch"] == []
    assert ident["timepoint"] == "30 days"
    assert ident["unit"] == "PATIENTS_WITH_EVENT"
    assert [(a["events"], a["n"]) for a in ident["arms"]] == [("14", "454"), ("24", "520")]
    registry = next(s for s in reached if s["source_kind"] == "registry_results")
    assert json.loads(registry["text"]) == held["ctgov_results"]["NCT02345486"][0]


def test_measure_from_unnamed_nct_is_never_attached():
    held, outcome, row, spec = plant()
    # Select an actually held foreign NCT, without inventing a trial identifier.
    cache = json.loads((ROOT / "cache" / SLUG / "records.json").read_text(encoding="utf-8"))
    foreign = next(nct for nct in sorted(cache["ctgov_results"])
                   if nct != held["records"][0]["nct"] and cache["ctgov_results"][nct])
    held["ctgov_results"] = {foreign: cache["ctgov_results"][foreign]}
    assert all(s["source_kind"] != "registry_results" for s in sources(held))
    assert reason_audit.audit_reason_row(outcome, row, sources(held), spec)["verdict"] == reason_audit.REASON_NOT_DISPROVED


def test_own_registry_measure_cannot_answer_different_outcome():
    held, _, row, _ = plant()
    unrelated = {"name": "Acute kidney injury", "estimand": "RR"}
    registry = [s for s in sources(held) if s["source_kind"] == "registry_results"]
    audit = reason_audit.audit_reason_row(unrelated, row, registry, {})
    assert audit["verdict"] == reason_audit.REASON_NOT_DISPROVED
    assert all("outcome" in c["mismatch"] for c in audit["candidates"])


def test_no_accession_means_no_registry_results_even_when_the_text_names_an_nct():
    # Pass 18c (adversarial review round 2, G1): an NCT merely named in the text may be another trial's, so without the record's own
    # DataBank accession NOTHING is attached -- neither the trial's own NCT from its text nor a foreign one.
    held, _, _, _ = plant()
    held["records"][0].pop("nct")
    held["fulltext_by_pmid"] = {"27749094": "This trial was registered as NCT02345486."}
    assert not [s for s in sources(held) if s["source_kind"] == "registry_results"]
    cache = json.loads((ROOT / "cache" / SLUG / "records.json").read_text(encoding="utf-8"))
    foreign = next(nct for nct in sorted(cache["ctgov_results"]) if nct != "NCT02345486")
    held["fulltext_by_pmid"] = {"27749094": "Related trial " + foreign}
    assert all(s["source_kind"] != "registry_results" for s in sources(held))


def test_registry_uses_unchanged_identity_gates():
    held, outcome, row, spec = plant()
    registry = [s for s in sources(held) if s["source_kind"] == "registry_results"]
    for changed_outcome, changed_row, field in [
        ({**outcome, "timepoint": "90 days"}, row, "timepoint:"),
        ({**outcome, "estimand": "HR"}, row, "effect_measure:"),
        (outcome, {**row, "reason_code": "POPULATION_MISMATCH"}, "population:"),
        (outcome, {**row, "design": {"design": "cluster", "adjustment_status": "UNRESOLVED"}}, "design_variance:"),
    ]:
        audit = reason_audit.audit_reason_row(changed_outcome, changed_row, registry, spec)
        assert audit["verdict"] == reason_audit.REASON_NOT_DISPROVED
        assert any(m.startswith(field) for c in audit["candidates"] for m in c["mismatch"])


def test_no_denominator_borrowing_or_value_derivation():
    held, outcome, row, spec = plant()
    measure = held["ctgov_results"]["NCT02345486"][0]
    measure.pop("denoms")
    registry = [s for s in sources(held) if s["source_kind"] == "registry_results"]
    audit = reason_audit.audit_reason_row(outcome, row, registry, spec)
    assert audit["verdict"] == reason_audit.REASON_NOT_DISPROVED
    assert all(c["unit"] != "PATIENTS_WITH_EVENT" for c in audit["candidates"])


def test_deterministic_render_preserves_all_measure_fields():
    held, _, _, _ = plant()
    reordered = deepcopy(held)
    measure = reordered["ctgov_results"]["NCT02345486"][0]
    reordered["ctgov_results"]["NCT02345486"][0] = dict(reversed(list(measure.items())))
    assert sources(held) == sources(reordered)


def test_PLANT_a_stage_restricts_the_category_it_qualifies():
    from harness import evidence_identity as ei
    assert ei.definition_of("Incidence of stage II or III acute kidney injury", "Acute kidney injury") == "RESTRICTED"
    assert ei.definition_of("stage 2 or higher AKI developing after enrollment", "Acute kidney injury") == "RESTRICTED"
    assert ei.definition_of("AKI developed in 102 of 1067 patients", "Acute kidney injury") == "AS_NAMED"
    assert ei.definition_of("stage 2 or 3 AKI in 40 vs 38", "Stage 2 or 3 acute kidney injury") == "AS_NAMED"
