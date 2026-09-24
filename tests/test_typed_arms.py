"""Typed per-arm observation gate (evidence/typed_arms/scripts/check_typed_arms.py).

Every fixture is SYNTHETIC (a control must have a known answer that no corpus edit can move). One positive control
must stay BOUND; each plant must be refused FOR ITS OWN REASON (the reason code is asserted, not just the state)."""
import copy, hashlib, importlib.util, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = importlib.util.spec_from_file_location(
    "check_typed_arms", os.path.join(HERE, "..", "evidence", "typed_arms", "scripts", "check_typed_arms.py"))
cta = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cta)

DOC = ("TITLE: Synthetic trial of drugx\n\nParticipants were randomly assigned to drugx (n=100) or placebo (n=98). "
       "During a median follow-up of 2 years, the event occurred in 20 (20.0%) participants assigned to drugx and "
       "10 (10.2%) participants assigned to placebo. Adults aged 50 years or older with condition y were enrolled.\n")
REG = [{"arm_id": "NCTX:1", "active_interventions": ["drugx"], "label": {"value": "Drugx 10 mg"}},
       {"arm_id": "NCTX:2", "active_interventions": [], "label": {"value": "Placebo"}}]


def span(t):
    assert t in DOC, t
    return {"file": "doc_x.txt", "text": t}


GOOD = {
    "row_id": "CD-synthetic-0-0",
    "arms": [
        {"arm_label": "drugx", "arm_label_span": span("drugx (n=100)"), "registry_arm_id": "NCTX:1",
         "events": 20, "events_span": span("20 (20.0%) participants assigned to drugx"),
         "total": 100, "total_span": span("drugx (n=100)"), "total_basis": "RANDOMISED", "percentage_text": "20.0%"},
        {"arm_label": "placebo", "arm_label_span": span("placebo (n=98)"), "registry_arm_id": "NCTX:2",
         "events": 10, "events_span": span("10 (10.2%) participants assigned to placebo"),
         "total": 98, "total_span": span("placebo (n=98)"), "total_basis": "RANDOMISED", "percentage_text": "10.2%"}],
    "outcome": {"text": "the event", "span": span("the event occurred")},
    "population": {"text": "Adults aged 50", "span": span("Adults aged 50 years or older with condition y")},
    "window": {"text": "median follow-up of 2 years", "span": span("median follow-up of 2 years")},
    "notes": "", "not_found": []}
ROW = {"row_id": "CD-synthetic-0-0", "slug": "synthetic", "outcome_index": 0, "trial_index": 0,
       "outcome_name": "event", "trial_id": "PMID 1", "family_id": "NCTX", "row_sha256": "0" * 64,
       "served": {"ai": 20, "n1i": 100, "ci": 10, "n2i": 98}, "registry_arms": REG,
       "intervention_i_line": "drugx added to usual care."}


def run(tmp_path, out=None, row=None, doc=DOC):
    job = tmp_path / "CD-synthetic-0-0"
    job.mkdir(exist_ok=True)
    (job / "doc_x.txt").write_bytes(doc.encode("utf-8"))
    docs = [{"file": "doc_x.txt", "sha256": hashlib.sha256(DOC.encode("utf-8")).hexdigest(), "origin": "synthetic"}]
    (job / "row.json").write_text(json.dumps({"documents": docs}), encoding="utf-8")
    (job / "out.json").write_text(json.dumps(out or GOOD), encoding="utf-8")
    return cta.check_row(row or ROW, str(tmp_path))


def codes(rec):
    return " | ".join(rec["reasons"])


def test_positive_control_binds_with_direction(tmp_path):
    rec = run(tmp_path)
    assert rec["state"] == "BOUND", rec["reasons"]
    assert rec["comparator_direction"]["experimental_arm_id"] == "NCTX:1"
    assert rec["comparator_direction"]["comparator_arm_id"] == "NCTX:2"
    assert {a["f4b_slot"] for a in rec["arm_observations"]} == {"ai/n1i", "ci/n2i"}
    assert all(a["total_span"]["text"] in DOC for a in rec["arm_observations"])


def test_rewind_style_arm_swap_is_never_bound(tmp_path):
    """The served experimental slot holds the comparator's pair: a one-to-one numeric match, reversed."""
    row = copy.deepcopy(ROW)
    row["served"] = {"ai": 10, "n1i": 98, "ci": 20, "n2i": 100}
    rec = run(tmp_path, row=row)
    assert rec["state"] == "SOURCE_DIFFERS"
    assert "G6 ARM_SWAP" in codes(rec)
    assert rec["source_differs"][0]["kind"] == "ARM_SWAP"


def test_percentage_never_stands_in_for_a_denominator(tmp_path):
    out = copy.deepcopy(GOOD)
    out["arms"][0]["total_span"] = span("20 (20.0%) participants assigned to drugx")
    rec = run(tmp_path, out=out)
    assert rec["state"] != "BOUND" and "G3 arm 0" in codes(rec)


def test_not_stated_denominator_is_refused(tmp_path):
    out = copy.deepcopy(GOOD)
    out["arms"][1].update(total=None, total_span=None, total_basis="NOT_STATED")
    rec = run(tmp_path, out=out)
    assert rec["state"] != "BOUND" and "G3 arm 1" in codes(rec)


def test_span_not_verbatim_is_refused(tmp_path):
    out = copy.deepcopy(GOOD)
    out["arms"][0]["events_span"] = {"file": "doc_x.txt", "text": "20 participants assigned to drugx"}
    rec = run(tmp_path, out=out)
    assert rec["state"] != "BOUND" and "G1 arm 0 events" in codes(rec)


def test_changed_document_bytes_are_refused(tmp_path):
    rec = run(tmp_path, doc=DOC.replace("condition y", "condition z"))
    assert rec["state"] != "BOUND" and "bytes changed" in codes(rec)


def test_served_number_differing_from_source_goes_to_signature_not_binding(tmp_path):
    row = copy.deepcopy(ROW)
    row["served"] = {"ai": 21, "n1i": 100, "ci": 10, "n2i": 98}
    rec = run(tmp_path, row=row)
    assert rec["state"] == "SOURCE_DIFFERS" and rec["source_differs"][0]["kind"] == "NUMBERS_DIFFER"


def test_foreign_registry_arm_is_refused(tmp_path):
    out = copy.deepcopy(GOOD)
    out["arms"][0]["registry_arm_id"] = "NCTY:9"
    rec = run(tmp_path, out=out)
    assert rec["state"] != "BOUND" and "G5 arm 0" in codes(rec)


def test_direction_without_independent_evidence_is_unresolved(tmp_path):
    out = copy.deepcopy(GOOD)
    out["arms"][0]["arm_label"], out["arms"][1]["arm_label"] = "group A", "group B"
    row = copy.deepcopy(ROW)
    row["registry_arms"] = None
    rec = run(tmp_path, out=out, row=row)
    assert rec["state"] == "SET_ASIDE" and "G6 DIRECTION_UNRESOLVED" in codes(rec)


def test_missing_extractor_artefact_is_not_extracted(tmp_path):
    job = tmp_path / "CD-synthetic-0-0"
    job.mkdir()
    (job / "row.json").write_text(json.dumps({"documents": []}), encoding="utf-8")
    assert cta.check_row(ROW, str(tmp_path))["state"] == "NOT_EXTRACTED"


def test_role_match_links_an_abbreviated_label_to_its_registry_arm(tmp_path):
    """'dxsol group' shares no word with registry 'Drugx 10 mg', but both are on the review's intervention line and the
    family's other arm (Placebo) is not -- G5b links them and says so."""
    out = copy.deepcopy(GOOD)
    out["arms"][0]["arm_label"] = "dxsol group"
    row = copy.deepcopy(ROW)
    row["intervention_i_line"] = "drugx, including the dxsol formulation, added to usual care."
    rec = run(tmp_path, out=out, row=row)
    assert rec["state"] == "BOUND", rec["reasons"]
    assert "role match" in rec["arm_observations"][0]["arm_id_basis"]


def test_role_match_refuses_intervention_label_on_placebo_registry_arm(tmp_path):
    out = copy.deepcopy(GOOD)
    out["arms"][0]["arm_label"], out["arms"][0]["registry_arm_id"] = "dxsol group", "NCTX:2"
    row = copy.deepcopy(ROW)
    row["intervention_i_line"] = "drugx, including the dxsol formulation, added to usual care."
    rec = run(tmp_path, out=out, row=row)
    assert rec["state"] != "BOUND" and "G5 arm 0" in codes(rec)
