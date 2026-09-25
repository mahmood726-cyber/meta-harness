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


def run(tmp_path, out=None, row=None, doc=DOC, packet_doc=None):
    """`doc` is what is on disk at check time; `packet_doc` is what the packet recorded (default DOC)."""
    job = tmp_path / "CD-synthetic-0-0"
    job.mkdir(exist_ok=True)
    (job / "doc_x.txt").write_bytes(doc.encode("utf-8"))
    rec = (packet_doc if packet_doc is not None else DOC).encode("utf-8")
    docs = [{"file": "doc_x.txt", "sha256": hashlib.sha256(rec).hexdigest(), "origin": "synthetic"}]
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


def test_role_match_links_a_label_to_a_differently_named_registry_arm(tmp_path):
    """Source 'drugx' vs registry 'Dxsol 10 mg': no shared word, but both are on the review's intervention line and the
    family's other arm (Placebo) is not -- G5b links them and says so."""
    row = copy.deepcopy(ROW)
    row["registry_arms"] = [{"arm_id": "NCTX:1", "active_interventions": ["dxsol"], "label": {"value": "Dxsol 10 mg"}},
                            REG[1]]
    row["intervention_i_line"] = "drugx, including the dxsol formulation, added to usual care."
    rec = run(tmp_path, row=row)
    assert rec["state"] == "BOUND", rec["reasons"]
    assert "role match" in rec["arm_observations"][0]["arm_id_basis"]


def test_a_wrong_registry_proposal_never_reaches_the_record(tmp_path):
    """The extractor links the drug arm to the PLACEBO registry arm. The gate re-derives the link itself: the record
    carries the drug arm and says the extractor's proposal was overruled."""
    out = copy.deepcopy(GOOD)
    out["arms"][0]["registry_arm_id"] = "NCTX:2"
    rec = run(tmp_path, out=out)
    arm0 = rec["arm_observations"][0]
    assert arm0["arm_id"] == "NCTX:1" and "extractor proposed 'NCTX:2'" in arm0["arm_id_basis"]
    assert rec["comparator_direction"]["experimental_arm_id"] == "NCTX:1"


def test_registry_arm_ambiguous_for_the_label_is_refused(tmp_path):
    """Two registry drug arms (different doses), a source label that names only the drug: no unique link."""
    row = copy.deepcopy(ROW)
    row["registry_arms"] = [{"arm_id": "NCTX:1", "active_interventions": ["drugx"], "label": {"value": "Drugx 10 mg"}},
                            {"arm_id": "NCTX:3", "active_interventions": ["drugx"], "label": {"value": "Drugx 20 mg"}},
                            {"arm_id": "NCTX:2", "active_interventions": [], "label": {"value": "Placebo"}}]
    out = copy.deepcopy(GOOD)
    out["arms"][0]["registry_arm_id"] = None
    rec = run(tmp_path, out=out, row=row)
    assert rec["state"] == "SET_ASIDE" and "links to 2 registry arms" in codes(rec)


def test_factorial_margin_is_a_typed_union_of_registry_arms(tmp_path):
    row = copy.deepcopy(ROW)
    row["registry_arms"] = [
        {"arm_id": "F:1", "active_interventions": ["aspirin", "drugx"], "label": {"value": "Aspirin + Drugx"}},
        {"arm_id": "F:2", "active_interventions": ["aspirin"], "label": {"value": "Aspirin + Placebo Drugx"}},
        {"arm_id": "F:3", "active_interventions": ["drugx"], "label": {"value": "Placebo Aspirin + Drugx"}},
        {"arm_id": "F:4", "active_interventions": [], "label": {"value": "Placebo Aspirin + Placebo Drugx"}}]
    out = copy.deepcopy(GOOD)
    out["arms"][0]["registry_arm_id"] = out["arms"][1]["registry_arm_id"] = None
    rec = run(tmp_path, out=out, row=row)
    assert rec["state"] == "BOUND", rec["reasons"]
    assert rec["comparator_direction"]["experimental_arm_id"] == "F:1+F:3"
    assert rec["comparator_direction"]["comparator_arm_id"] == "F:2+F:4"


def test_non_discriminating_registry_falls_back_to_a_typed_source_label(tmp_path):
    row = copy.deepcopy(ROW)
    row["registry_arms"] = [{"arm_id": "D:1", "active_interventions": ["drugx"], "label": {"value": "1"}},
                            {"arm_id": "D:2", "active_interventions": ["drugx"], "label": {"value": "2"}}]
    out = copy.deepcopy(GOOD)
    out["arms"][0]["registry_arm_id"] = out["arms"][1]["registry_arm_id"] = None
    rec = run(tmp_path, out=out, row=row)
    assert rec["state"] == "BOUND", rec["reasons"]
    assert all("NON-DISCRIMINATING" in a["arm_id_basis"] for a in rec["arm_observations"])


DOC_AC = ("Participants were randomly assigned to the active group (n=100) or the control group (n=98). The event "
          "occurred in 20 (20.0%) participants in the active group and 10 (10.2%) participants in the control group. "
          "Adults aged 50 years or older with condition y were enrolled.\n")


def test_by_exclusion_direction_from_control_vocabulary(tmp_path):
    """'Active' vs 'Control' with no registry arms: the non-control arm is experimental."""
    def sp(t):
        assert t in DOC_AC, t
        return {"file": "doc_x.txt", "text": t}
    out = copy.deepcopy(GOOD)
    out["arms"][0].update(arm_label="Active", arm_label_span=sp("active group (n=100)"), events_span=sp("20 (20.0%) participants in the active group"), total_span=sp("active group (n=100)"))
    out["arms"][1].update(arm_label="Control", arm_label_span=sp("control group (n=98)"), events_span=sp("10 (10.2%) participants in the control group"), total_span=sp("control group (n=98)"))
    out.update(outcome={"text": "The event", "span": sp("The event occurred")}, window=None,
               population={"text": "Adults", "span": sp("Adults aged 50 years or older with condition y")})
    row = copy.deepcopy(ROW)
    row["registry_arms"] = None
    rec = run(tmp_path, out=out, row=row, doc=DOC_AC, packet_doc=DOC_AC)
    assert rec["state"] == "BOUND", rec["reasons"]
    assert rec["comparator_direction"]["experimental_label"] == "Active"


DOC_PAR = ("Participants were randomly assigned to drugx (n=100) or placebo (n=98). The event occurred in 20 (20.0%) and "
           "10 (10.2%) participants in the drugx and placebo groups, respectively. Adults aged 50 years or older with "
           "condition y were enrolled.\n")


def _par_out(ev0, ev1):
    def sp(t):
        assert t in DOC_PAR, t
        return {"file": "doc_x.txt", "text": t}
    shared = sp("20 (20.0%) and 10 (10.2%) participants in the drugx and placebo groups")
    out = copy.deepcopy(GOOD)
    out["arms"][0].update(events=ev0, events_span=shared, arm_label_span=sp("drugx (n=100)"), total_span=sp("drugx (n=100)"))
    out["arms"][1].update(events=ev1, events_span=shared, arm_label_span=sp("placebo (n=98)"), total_span=sp("placebo (n=98)"))
    out.update(outcome={"text": "The event", "span": sp("The event occurred")}, window=None,
               population={"text": "Adults", "span": sp("Adults aged 50 years or older with condition y")})
    return out


def test_shared_span_parallel_order_binds(tmp_path):
    rec = run(tmp_path, out=_par_out(20, 10), doc=DOC_PAR, packet_doc=DOC_PAR)
    assert rec["state"] == "BOUND", rec["reasons"]
    assert [a["events_ownership"] for a in rec["arm_observations"]] == ["PARALLEL_ORDER", "PARALLEL_ORDER"]


def test_numbers_swapped_inside_a_shared_span_are_refused_even_when_the_served_row_agrees(tmp_path):
    """The REWIND shape: the extractor gives drugx the placebo arm's count, and the served row carries the same swap,
    so G4 matches one-to-one. Only ownership in the TEXT can refuse it -- '10 ... in the drugx' is nearness inside a
    coordinated list, not ownership."""
    row = copy.deepcopy(ROW)
    row["served"] = {"ai": 10, "n1i": 100, "ci": 20, "n2i": 98}
    rec = run(tmp_path, out=_par_out(10, 20), row=row, doc=DOC_PAR, packet_doc=DOC_PAR)
    assert rec["state"] != "BOUND"
    assert "G7 arm 0: events 10" in codes(rec) and "G7 arm 1: events 20" in codes(rec)


def test_incomplete_numbers_are_set_aside_not_queued_as_a_served_difference(tmp_path):
    out = copy.deepcopy(GOOD)
    out["arms"][0].update(events=None, events_span=None)
    rec = run(tmp_path, out=out)
    assert rec["state"] == "SET_ASIDE" and "G4 not evaluated" in codes(rec)


def test_no_control_characters_in_the_lanes_sources():
    """A shell heredoc turned '\b' into a literal backspace in a regex three times in this lane; a regex holding
    \x08 still compiles and silently matches nothing. Refuse any C0 control byte except tab/newline/CR."""
    import glob
    base = os.path.join(HERE, "..")
    files = (glob.glob(os.path.join(base, "evidence", "typed_arms", "scripts", "*.py"))
             + glob.glob(os.path.join(base, "evidence", "p5_populations", "scripts", "*.py"))
             + glob.glob(os.path.join(base, "tests", "test_typed_arms*.py")))
    bad = [(f, b) for f in files for b in set(open(f, "rb").read()) if b < 32 and b not in (9, 10, 13)]
    assert files and not bad, bad


DOC_EQ = ("Participants were randomly assigned to drugx (n=100) or placebo (n=98). Treatment was stopped in one patient "
          "in each group. Adults aged 50 years or older with condition y were enrolled.\n")


def _eq_out():
    def sp(t):
        assert t in DOC_EQ, t
        return {"file": "doc_x.txt", "text": t}
    out = copy.deepcopy(GOOD)
    ev = sp("Treatment was stopped in one patient in each group.")
    out["arms"][0].update(events=1, events_span=ev, arm_label_span=sp("drugx (n=100)"), total_span=sp("drugx (n=100)"))
    out["arms"][1].update(events=1, events_span=ev, arm_label_span=sp("placebo (n=98)"), total_span=sp("placebo (n=98)"))
    out.update(outcome={"text": "stopped", "span": sp("Treatment was stopped")}, window=None,
               population={"text": "Adults", "span": sp("Adults aged 50 years or older with condition y")})
    return out


def test_a_count_stated_in_each_group_is_owned_by_every_arm(tmp_path):
    row = copy.deepcopy(ROW)
    row["served"] = {"ai": 1, "n1i": 100, "ci": 1, "n2i": 98}
    rec = run(tmp_path, out=_eq_out(), row=row, doc=DOC_EQ, packet_doc=DOC_EQ)
    assert rec["state"] == "BOUND", rec["reasons"]
    assert [a["events_ownership"] for a in rec["arm_observations"]] == ["EACH_GROUP", "EACH_GROUP"]


def test_each_group_never_owns_unequal_counts(tmp_path):
    out = _eq_out()
    out["arms"][1]["events"] = 2
    row = copy.deepcopy(ROW)
    row["served"] = {"ai": 1, "n1i": 100, "ci": 2, "n2i": 98}
    rec = run(tmp_path, out=out, row=row, doc=DOC_EQ, packet_doc=DOC_EQ)
    assert rec["state"] != "BOUND"


def test_identical_arms_are_mapped_by_direction_not_called_a_served_difference(tmp_path):
    """9/120 vs 9/120: the numbers cannot say whose slot is whose; the first gate called this SOURCE_DIFFERS."""
    doc = DOC.replace("(n=98)", "(n=100)").replace("10 (10.2%) participants assigned to placebo",
                                                   "20 (20.0%) participants assigned to placebo")
    out = copy.deepcopy(GOOD)
    def sp(t):
        assert t in doc, t
        return {"file": "doc_x.txt", "text": t}
    out["arms"][1].update(events=20, total=100, events_span=sp("20 (20.0%) participants assigned to placebo"),
                          arm_label_span=sp("placebo (n=100)"), total_span=sp("placebo (n=100)"))
    row = copy.deepcopy(ROW)
    row["served"] = {"ai": 20, "n1i": 100, "ci": 20, "n2i": 100}
    rec = run(tmp_path, out=out, row=row, doc=doc, packet_doc=doc)
    assert rec["state"] == "BOUND", rec["reasons"]
    assert rec["comparator_direction"]["experimental_label"] == "drugx"
    assert "identical" in rec["comparator_direction"]["basis"]


def test_a_named_absence_arm_is_the_comparator():
    typed = [{"arm_label": "colchicine", "arm_id": None}, {"arm_label": "no-colchicine", "arm_id": None}]
    j, _ = cta.direction(typed, "colchicine (peri-operative), added to usual care.", None)
    assert j == 0


DOC_AACT = ('{\n "reported_events": [\n  {\n   "id": "1",\n   "result_group_id": "G2",\n   "time_frame": "long text",\n'
            '   "subjects_affected": "20",\n   "subjects_at_risk": "100"\n  },\n  {\n   "id": "2",\n   "result_group_id": "G1",\n'
            '   "subjects_affected": "10",\n   "subjects_at_risk": "98"\n  }\n ],\n "result_groups": [\n'
            '  {\n   "id": "G1",\n   "title": "Placebo"\n  },\n  {\n   "id": "G2",\n   "title": "Drugx 10 mg"\n  }\n ]\n}\n')


def _aact_out(swap=False):
    def sp(t):
        assert t in DOC_AACT, t
        return {"file": "doc_x.txt", "text": t}
    out = copy.deepcopy(GOOD)
    a, b = ('"subjects_affected": "20",\n   "subjects_at_risk": "100"', '"subjects_affected": "10",\n   "subjects_at_risk": "98"')
    if swap:
        a, b = b, a
    out["arms"][0].update(arm_label="Drugx 10 mg", arm_label_span=sp('"title": "Drugx 10 mg"'), events_span=sp(a), total_span=sp(a))
    out["arms"][1].update(arm_label="Placebo", arm_label_span=sp('"title": "Placebo"'), events_span=sp(b), total_span=sp(b))
    if swap:
        out["arms"][0].update(events=10, total=98)
        out["arms"][1].update(events=20, total=100)
    out.update(outcome={"text": "events", "span": sp('"reported_events"')}, window=None,
               population={"text": "x", "span": sp('"time_frame": "long text"')})
    return out


def test_aact_row_is_owned_through_its_result_group(tmp_path):
    rec = run(tmp_path, out=_aact_out(), doc=DOC_AACT, packet_doc=DOC_AACT)
    assert rec["state"] == "BOUND", rec["reasons"]
    assert [a["events_ownership"] for a in rec["arm_observations"]] == ["AACT_GROUP", "AACT_GROUP"]


def test_aact_rows_attributed_to_the_wrong_group_are_refused(tmp_path):
    row = copy.deepcopy(ROW)
    row["served"] = {"ai": 10, "n1i": 98, "ci": 20, "n2i": 100}
    rec = run(tmp_path, out=_aact_out(swap=True), row=row, doc=DOC_AACT, packet_doc=DOC_AACT)
    assert rec["state"] != "BOUND" and "G7 arm 0" in codes(rec)


# ---- review of G1-G7, 2026-09-25: each route by which a swap or a wrong number bound ------------------------------
OWN = cta.ownership
A2 = [{"arm_label": "drugx"}, {"arm_label": "placebo"}]


def _own(text, arm_i, values):
    return OWN.owns(None, {"text": text, "start": 0, "end": len(text)}, values[arm_i], None, arm_i, A2, values)


def test_the_arm_after_compared_with_never_owns_the_first_number():
    text = "Compared with placebo, the event occurred in 20 (20.0%) vs 10 (10.2%) participants."
    swapped = {0: 10, 1: 20}          # truth: drugx 20, placebo 10
    assert _own(text, 1, swapped) is None and _own(text, 0, swapped) is None
    text_b = "Compared with placebo, drugx reduced the event: 10 (10.2%) vs 20 (20.0%)"
    assert _own(text_b, 1, {0: 20, 1: 10}) is None   # truth: drugx 10


def test_parallel_order_is_anchored_to_one_clause():
    wide = ("Patients receiving drugx or placebo were followed; the event occurred in 20 and 10 participants in the "
            "placebo and drugx groups, respectively")
    assert _own(wide, 0, {0: 20, 1: 10}) is None          # the swapped claim
    assert _own(wide, 0, {0: 10, 1: 20}) == "PARALLEL_ORDER"
    dose = "In the placebo and drugx groups, 20 and 10 events occurred; drugx was given at 20 mg daily."
    assert _own(dose, 0, {0: 20, 1: 10}) is None
    assert _own(dose, 0, {0: 10, 1: 20}) == "PARALLEL_ORDER"


def test_group_id_reads_the_numbers_own_object_and_refuses_a_span_across_objects():
    doc = json.dumps({"groups": [{"id": "OG000", "title": "Drugx"}, {"id": "OG001", "title": "Placebo"}],
                      "measurements": [{"groupId": "OG000", "value": "20"}, {"groupId": "OG001", "value": "10"}]}, indent=1)
    cross = doc[doc.index('"groupId": "OG000"'):doc.index('"value": "10"') + len('"value": "10"')]
    sp = {"text": cross, "start": doc.index(cross), "end": doc.index(cross) + len(cross)}
    assert not OWN.group_id(doc, sp, A2[0], A2, 10)       # drugx claims OG001's 10 through a span starting in OG000
    own = doc[doc.index('"groupId": "OG000"'):doc.index('"value": "20"') + len('"value": "20"')]
    sp = {"text": own, "start": doc.index(own), "end": doc.index(own) + len(own)}
    assert OWN.group_id(doc, sp, A2[0], A2, 20)


def test_counts_are_not_percent_words_doses_rates_or_name_numbers():
    for t, v in (("20 percent", 20), ("20,5%", 20), ("10 mg daily", 10), ("per 100 patient-years", 100), ("GLP-1 users", 1),
                 ("at least one event", 1)):
        assert not cta.has_count(t, v), t
    assert cta.has_count("4,949 patients", 4949) and cta.has_count("four of 119", 4)


def test_a_negated_or_background_arm_is_never_the_intervention():
    typed = [{"arm_label": "Non-drugx dairy drink"}, {"arm_label": "drugx"}]
    exp, _ = cta.direction(typed, "drugx added to heart-failure therapy", None)
    assert exp == 1
    typed = [{"arm_label": "Heart-failure therapy alone"}, {"arm_label": "Drugx"}]
    assert cta.direction(typed, "drugx added to heart-failure therapy", None)[0] == 1
    # 'omega-3' no longer matches 'omega-6' (whole-word terms); one weak vote then leaves it unresolved -- never the
    # comparator, which is the requirement
    assert cta.direction([{"arm_label": "Omega-6 corn oil"}, {"arm_label": "Omega-3"}], "omega-3 fatty acids", None)[0] != 0


def test_one_weak_vote_does_not_resolve_direction():
    """A label that merely contains an intervention word, against a label with nothing, is not enough."""
    assert cta.direction([{"arm_label": "drugx"}, {"arm_label": "group B"}], "drugx", None)[0] is None


def test_two_arms_resolving_to_one_registry_arm_are_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(cta, "resolve_arm", lambda *a, **k: ("NCTX:2", "forced"))
    assert "G5 two source arms resolve to the same registry arm" in codes(run(tmp_path))


def test_an_events_span_from_another_outcomes_sentence_is_refused(tmp_path):
    doc = DOC.replace("Adults aged", "Nausea occurred in 30 of 100 and 5 of 98 patients. Adults aged")
    out = copy.deepcopy(GOOD)
    out["outcome"] = {"text": "Death", "span": {"file": "doc_x.txt", "text": "the event occurred"}}
    for a, t in zip(out["arms"], ("30 of 100", "5 of 98")):
        a["events_span"] = {"file": "doc_x.txt", "text": t}
    out["arms"][0]["events"], out["arms"][1]["events"] = 30, 5
    row = copy.deepcopy(ROW)
    row["served"], row["outcome_name"] = {"ai": 30, "n1i": 100, "ci": 5, "n2i": 98}, "Death"
    rec = run(tmp_path, out=out, row=row, doc=doc, packet_doc=doc)
    assert "G9 arm 0" in codes(rec)


def test_a_label_span_that_names_another_arm_is_refused(tmp_path):
    out = copy.deepcopy(GOOD)
    out["arms"][0]["arm_label_span"] = span("placebo (n=98)")
    assert "G10 arm 0" in codes(run(tmp_path, out=out))
