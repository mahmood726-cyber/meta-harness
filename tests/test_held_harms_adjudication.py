"""Held-full-text harm adjudications (scripts/held_harms_adjudication.py).

Enabling held full texts let harms.reporting_signal see 17 term hits that the abstracts never showed, and
gate.check_harms_complete refused 7 pages. Plant: for every decision, the pre-fix row (the machine's
OUTCOME_NOT_IN_SOURCE, read against the real held text through the build's own held_fulltexts) leaves the harm
outcome HARMS_INCOMPLETE -- the gate fires; the decided row (typed refusal, or the trial pooled) resolves it.
Corpus: every decision is present in cache/, its span is verbatim in the held bytes, and the loader re-validates it.
"""
import importlib.util
import json
from pathlib import Path

import pytest

from harness import harms, verified_inputs
from harness.pipeline import held_fulltexts

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("held_harms_adjudication", ROOT / "scripts" / "held_harms_adjudication.py")
adj = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(adj)


def _inputs(slug, outcome_name):
    config = json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))
    records = json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8"))
    spec = next(s for s in config.get("harm_outcomes", []) if s.get("name") == outcome_name)
    rec_by_id = {str(r.get("id")): r for r in records.get("records", [])}
    ftbp, _ = held_fulltexts(slug, records, config=config)
    return spec, rec_by_id, ftbp


def _annotate(spec, rec_by_id, ftbp, pid, row_code, pooled):
    outcome = {"kind": "harm", "name": spec["name"], "trials": [], "declared_absent_trials": [], "result": {}}
    if pooled:
        outcome["trials"].append({"id": f"PMID {pid}", "label": pid, "ai": 1, "n1i": 10, "ci": 1, "n2i": 10})
    else:
        outcome["declared_absent_trials"].append({"id": f"PMID {pid}", "label": pid, "reason_code": row_code,
                                                  "state": row_code})
    included = [{"id": pid}]
    return harms.annotate_outcome(outcome, spec, included, rec_by_id, ftbp)["result"]


@pytest.mark.parametrize("decision", adj.DECISIONS, ids=[f"{d[0]}:{d[1]}:{d[2]}" for d in adj.DECISIONS])
def test_plant_fires_before_the_decision_and_clears_after(decision):
    slug, pid, outcome, prov, span, reason, counts = decision
    spec, rec_by_id, ftbp = _inputs(slug, outcome)
    assert pid in ftbp, "the held full text the decision reads is not enabled for this topic"
    before = _annotate(spec, rec_by_id, ftbp, pid, "OUTCOME_NOT_IN_SOURCE", pooled=False)
    assert before.get("harms_incomplete"), "plant did not fire: the held text no longer carries the signal"
    after = _annotate(spec, rec_by_id, ftbp, pid, prov, pooled=bool(counts))
    assert not after.get("harms_incomplete"), after.get("reason")


def test_every_decision_is_present_and_validated_n_of_n():
    assert adj.apply(check=True) == []
    for slug in sorted({d[0] for d in adj.DECISIONS}):
        verified_inputs.load(slug)  # raises if any span is not verbatim in its held document


def test_a_tampered_span_is_refused_by_the_loader(tmp_path):
    slug, pid, outcome, prov, span, reason, counts = adj.DECISIONS[1]
    d = tmp_path / slug
    d.mkdir()
    (d / f"ft_{pid}.txt").write_text((ROOT / "cache" / slug / f"ft_{pid}.txt").read_text(encoding="utf-8"),
                                     encoding="utf-8")
    _, entry = adj.entry_for(slug, pid, outcome, prov, span.replace("insulin", "insuline"), reason, counts)
    entry["document_ref"] = f"ft_{pid}.txt"
    (d / "verified_effects.json").write_text(json.dumps({pid: entry}), encoding="utf-8")
    with pytest.raises(ValueError, match="source_span absent"):
        verified_inputs.load(slug, cache_root=tmp_path)
