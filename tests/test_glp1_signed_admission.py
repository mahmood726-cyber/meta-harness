"""V1.0.1: FLOW and ELIXA enter the GLP-1 primary pool by SIGNED RESULT-LEVEL ADJUDICATION.

Written BEFORE the admission mechanism existed and run against that tree (it fired: see
evidence/glp1_adjudication/ADMISSION_TESTS_PREFIX.txt). Every case runs the real primary-outcome route
(pipeline.outcome_inputs + _build_outcome + synth.pool), never a hand pool.

  before (committed inputs, admission not declared)  k=8, HR 0.856 (0.8086-0.9061)   = the served V1 result
  after  (the topic config's adjudicated_results)    k=10, HR 0.861 (0.807-0.919), FLOW and ELIXA pooled with
                                                      every witness verified; FREEDOM-CVO still not pooled

Plants keep the battery's paired shape: the CONTROL admits (k=10) -> ONE input is edited -> the edited admission
is refused, fail closed, under a named reason -> nothing else moves. A plant can therefore not pass vacuously on a
tree that admits nothing.
"""
import copy
import hashlib
import json
import os
import shutil

import pytest

from harness import fetch, pipeline

SLUG = "glp1-ra-mace-t2d"
PRIMARY = "3-point major adverse cardiovascular events"
ROOT = pipeline.ROOT
ADJ = "evidence/glp1_adjudication"
FLOW, ELIXA, FREEDOM = "PMID 38785209", "PMID 26630143", "PMID 34873344"


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


@pytest.fixture(scope="module")
def inputs():
    config = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
    records = fetch.ensure(config, "")            # committed cache: no network
    inp = pipeline.outcome_inputs(SLUG, config, records)
    spec = next(s for s, k in pipeline._outcome_specs(config) if s.get("name") == PRIMARY)
    return inp, spec


def _build(inp, spec):
    return pipeline.build_outcome_from_inputs(inp, spec, "efficacy", SLUG)


def _ids(out):
    return {t.get("id") for t in out["trials"]}


def _entry(spec, trial_id):
    return next(e for e in spec.get("adjudicated_results") or [] if e.get("id") == trial_id)


# ------------------------------------------------------------------------------------------ before -> after
def test_before_is_the_served_k8(inputs):
    inp, spec = inputs
    before = dict(spec)
    before.pop("adjudicated_results", None)
    r = _build(inp, before)["result"]
    assert r["k"] == 8
    assert (round(r["estimate"], 3), round(r["ci_low"], 4), round(r["ci_high"], 4)) == (0.856, 0.8086, 0.9061)


def test_after_is_k10_with_flow_and_elixa_derived_by_the_pipeline(inputs):
    inp, spec = inputs
    out = _build(inp, spec)
    r = out["result"]
    assert r["k"] == 10, f"k={r['k']}: the declared admissions did not reach the pool"
    assert (round(r["estimate"], 3), round(r["ci_low"], 3), round(r["ci_high"], 3)) == (0.861, 0.807, 0.919)
    assert {FLOW, ELIXA} <= _ids(out)
    for tid in (FLOW, ELIXA):
        row = next(t for t in out["trials"] if t["id"] == tid)
        adj = row["result_adjudication"]
        assert row["provenance"] == "signed_result_adjudication"
        assert row["endpoint_admissibility"] == "EXACT_TARGET"
        assert adj["witnesses_verified"] >= 10 and adj["decision_sha256"] == _sha(os.path.join(ROOT, adj["decision"]))
        assert {"endpoint", "analysis", "population", "contrast", "eligibility"} <= set(adj["fields_witnessed"])
    elixa = next(t for t in out["trials"] if t["id"] == ELIXA)
    assert (elixa["effect"], elixa["ci_low"], elixa["ci_high"]) == (1.02, 0.887, 1.172)   # the unrounded text interval
    assert "source_conflict" in elixa["result_adjudication"]                               # the dispute travels with it
    assert ELIXA not in {a.get("id") for a in out["declared_absent_trials"]}, "ELIXA both pooled and declared absent"


def test_freedom_cvo_is_still_not_pooled(inputs):
    inp, spec = inputs
    out = _build(inp, spec)
    assert out["result"]["k"] == 10
    assert FREEDOM not in _ids(out) and not any("FREEDOM" in str(t.get("label")) for t in out["trials"])
    assert not any(e.get("trial") == "FREEDOM-CVO" for e in spec.get("adjudicated_results") or [])


# ------------------------------------------------------------------------------------------ plants
def test_PLANT_freedom_declared_on_the_primary_strand_is_refused(inputs):
    """FREEDOM-CVO's decision NAMES the primary strand only to exclude itself; a substring check admitted it."""
    inp, spec = inputs
    assert _build(inp, spec)["result"]["k"] == 10                           # control
    from harness import result_adjudication as RA
    bad = copy.deepcopy(spec)
    d = f"{ADJ}/FREEDOM-CVO.json"
    bad["adjudicated_results"].append({"trial": "FREEDOM-CVO", "id": FREEDOM, "nct": "NCT01455896", "decision": d,
                                       "decision_sha256": _sha(os.path.join(ROOT, d)), "strand": "CONVENTIONAL_GLP1RA"})
    with pytest.raises(RA.AdjudicationRefused, match="does not admit it on strand"):
        _build(inp, bad)


def test_PLANT_decision_bytes_changed_after_pinning_is_refused(inputs, tmp_path):
    inp, spec = inputs
    assert _build(inp, spec)["result"]["k"] == 10                           # control
    from harness import result_adjudication as RA
    src = os.path.join(ROOT, _entry(spec, ELIXA)["decision"])
    d = json.load(open(src, encoding="utf-8"))
    d["bound_result"]["ci"]["value"] = [0.80, 1.10]                         # a quieter interval
    p = tmp_path / "ELIXA.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    bad = copy.deepcopy(spec)
    _entry(bad, ELIXA)["decision"] = str(p)                                 # still pinned to the original bytes
    with pytest.raises(RA.AdjudicationRefused, match="sha256"):
        _build(inp, bad)


def test_PLANT_tuple_edited_and_repinned_has_no_witness_and_is_refused(inputs, tmp_path):
    """Re-pinning the edited decision beats the sha check; the tuple then has no witnessed span that carries it."""
    inp, spec = inputs
    assert _build(inp, spec)["result"]["k"] == 10                           # control
    from harness import result_adjudication as RA
    src = os.path.join(ROOT, _entry(spec, ELIXA)["decision"])
    d = json.load(open(src, encoding="utf-8"))
    d["bound_result"]["estimate"]["value"] = 0.95
    d["bound_result"]["ci"]["value"] = [0.80, 1.10]
    p = tmp_path / "ELIXA.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    bad = copy.deepcopy(spec)
    _entry(bad, ELIXA).update(decision=str(p), decision_sha256=_sha(p))
    with pytest.raises(RA.AdjudicationRefused, match="no witnessed span"):
        _build(inp, bad)


def test_PLANT_witness_span_not_in_the_held_bytes_is_refused(inputs, tmp_path):
    inp, spec = inputs
    assert _build(inp, spec)["result"]["k"] == 10                           # control
    from harness import result_adjudication as RA
    src = os.path.join(ROOT, _entry(spec, FLOW)["decision"])
    d = json.load(open(src, encoding="utf-8"))
    w = d["bound_result"]["population"]["witness"]
    w["span"] = w["span"].replace("3,533", "3,353")                         # one transposed digit
    p = tmp_path / "FLOW.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    bad = copy.deepcopy(spec)
    _entry(bad, FLOW).update(decision=str(p), decision_sha256=_sha(p))
    with pytest.raises(RA.AdjudicationRefused, match="not verbatim"):
        _build(inp, bad)


def test_PLANT_held_source_bytes_changed_is_refused(inputs, tmp_path, monkeypatch):
    """A witness names held bytes by sha256; a changed held file (same path) is refused, not re-read."""
    inp, spec = inputs
    assert _build(inp, spec)["result"]["k"] == 10                           # control
    from harness import result_adjudication as RA
    lane = tmp_path / "lane"
    for rel in ("evidence", "outputs/handover/glp1_regulatory", "protocols"):
        shutil.copytree(os.path.join(ROOT, rel), lane / rel,
                        ignore=shutil.ignore_patterns("held_local", "*.gz", "sweeps"))
    reg = lane / "evidence/held/registry/NCT01147250.json"
    reg.write_bytes(reg.read_bytes().replace(b"minimum age", b"minimum  age"))
    monkeypatch.setattr(RA, "ROOT", str(lane))
    RA._text_cache.clear()
    with pytest.raises(RA.AdjudicationRefused, match="NCT01147250.json sha256"):
        _build(inp, spec)
    RA._text_cache.clear()


def test_PLANT_row_claiming_the_provenance_without_a_declared_admission_is_refused(inputs):
    """Admissibility re-verifies: a row that merely CLAIMS signed adjudication never pools."""
    from harness import target_endpoint
    inp, spec = inputs
    out = _build(inp, spec)
    assert out["result"]["k"] == 10                                         # control
    forged = dict(next(t for t in out["trials"] if t["id"] == FLOW), id="PMID 99999999", label="FORGED")
    kept, refused = target_endpoint.admit_rows(spec, [forged])
    assert kept == [] and refused and "declares no such admission" in refused[0]["reason"]
    edited = dict(next(t for t in out["trials"] if t["id"] == FLOW), effect=0.70)
    kept, refused = target_endpoint.admit_rows(spec, [edited])
    assert kept == [] and "differs from its verified decision" in refused[0]["reason"]


def test_PLANT_renderer_swapped_is_refused(inputs):
    inp, spec = inputs
    assert _build(inp, spec)["result"]["k"] == 10                           # control
    from harness import result_adjudication as RA
    bad = copy.deepcopy(spec)
    bad["adjudication_renderer_sha256"] = "0" * 64
    RA._text_cache.clear()
    with pytest.raises(RA.AdjudicationRefused, match="renderer"):
        _build(inp, bad)
    RA._text_cache.clear()
