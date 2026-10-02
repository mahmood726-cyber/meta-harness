"""Plants for scripts/abstract_harms_adjudication.py (acq/k-gap integration, 2026-10-03): for every decision the
pre-fix row (machine OUTCOME_NOT_IN_SOURCE against the held abstract) leaves the harm outcome HARMS_INCOMPLETE, and
the decided typed refusal clears it; every span is verbatim in the held record and re-validated by the loader."""
import importlib.util
import json
from pathlib import Path

import pytest

from harness import harms, verified_inputs

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("abstract_harms_adjudication",
                                               ROOT / "scripts" / "abstract_harms_adjudication.py")
adj = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(adj)


def _spec_and_records(slug, outcome):
    config = json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))
    records = json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8"))
    spec = next(s for s in config.get("harm_outcomes", []) if s.get("name") == outcome)
    return spec, {str(r.get("id")): r for r in records.get("records", [])}


def _annotate(spec, rec_by_id, pid, code):
    outcome = {"kind": "harm", "name": spec["name"], "trials": [], "result": {},
               "declared_absent_trials": [{"id": f"PMID {pid}", "label": pid, "reason_code": code, "state": code}]}
    return harms.annotate_outcome(outcome, spec, [{"id": pid}], rec_by_id, {})["result"]


@pytest.mark.parametrize("d", adj.DECISIONS, ids=[f"{d[0]}:{d[1]}:{d[2]}" for d in adj.DECISIONS])
def test_PLANT_fires_before_the_decision_and_clears_after(d):
    slug, pid, outcome, prov, span, reason = d
    spec, rec_by_id = _spec_and_records(slug, outcome)
    assert _annotate(spec, rec_by_id, pid, "OUTCOME_NOT_IN_SOURCE").get("harms_incomplete"), "plant did not fire"
    assert not _annotate(spec, rec_by_id, pid, prov).get("harms_incomplete")


def test_every_decision_is_present_validated_and_audited():
    assert adj.apply(check=True) == []
    for slug in sorted({d[0] for d in adj.DECISIONS}):
        verified_inputs.load(slug)
