"""Token-level witness checker (evidence/typed_arms/witness/check_witness.py). Synthetic fixtures only; each plant is
refused for its own reason code."""
import copy, hashlib, importlib.util, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = importlib.util.spec_from_file_location(
    "check_witness", os.path.join(HERE, "..", "evidence", "typed_arms", "witness", "check_witness.py"))
cw = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cw)

PROSE = ("Patients were randomly assigned to drugx (n=100) or placebo (n=98). The event occurred in 9 patients in the "
         "drugx group and 9 patients in the placebo group.\n")
REG = json.dumps({"adverseEventsModule": {"eventGroups": [
    {"id": "EG000", "title": "Placebo"}, {"id": "EG001", "title": "Drugx"}],
    "seriousEvents": [{"term": "Event", "stats": [
        {"groupId": "EG000", "numAffected": 10, "numAtRisk": 98},
        {"groupId": "EG001", "numAffected": 20, "numAtRisk": 100}]}]}}, indent=1, sort_keys=True)


def W(doc, text, nth=0, file="doc_p.txt"):
    """The nth WHOLE-token occurrence of text (a '9' inside '98' is not an occurrence of the token '9')."""
    import re
    hits = [m.start() for m in re.finditer(r"(?<![0-9A-Za-z])" + re.escape(text) + r"(?![0-9A-Za-z])", doc)]
    at = hits[nth]
    return {"file": file, "start": at, "end": at + len(text), "text": text}


def job(tmp_path, out, served, docs, registry=False, **row_extra):
    j = tmp_path / "HE-x"
    j.mkdir()
    rows = []
    for name, text in docs.items():
        (j / name).write_bytes(text.encode("utf-8"))
        rows.append({"file": name, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "origin": name})
    (j / "row.json").write_text(json.dumps({"held_key": "x/1", "served": served, "documents": rows,
                                            "registry_results": [{"nct": "NCT0"}] if registry else [], **row_extra}), encoding="utf-8")
    (j / "out.json").write_text(json.dumps(out), encoding="utf-8")
    return cw.check_job(str(j))


def prose_out():
    return {"ownership_source": "PROSE_OR_TABLE", "arms": [
        {"role": "intervention", "group_id": None, "arm_name": "drugx", "arm_name_witness": W(PROSE, "drugx"),
         "events": 9, "event_witness": W(PROSE, "9", 0), "total": 100, "total_witness": W(PROSE, "100")},
        {"role": "comparator", "group_id": None, "arm_name": "placebo", "arm_name_witness": W(PROSE, "placebo"),
         "events": 9, "event_witness": W(PROSE, "9", 1), "total": 98, "total_witness": W(PROSE, "98")}]}


SERVED_P = {"ai": 9, "n1i": 100, "ci": 9, "n2i": 98}


def test_equal_values_with_distinct_occurrences_are_witnessed(tmp_path):
    rec = job(tmp_path, prose_out(), SERVED_P, {"doc_p.txt": PROSE})
    assert rec["state"] == "WITNESSED", rec["reasons"]


def test_one_occurrence_cannot_witness_two_arm_fields(tmp_path):
    out = prose_out()
    out["arms"][1]["event_witness"] = copy.deepcopy(out["arms"][0]["event_witness"])
    rec = job(tmp_path, out, SERVED_P, {"doc_p.txt": PROSE})
    assert rec["state"] == "INCOMPLETE" and any(r.startswith("T4") for r in rec["reasons"])


def test_a_digit_inside_a_longer_number_is_not_a_token(tmp_path):
    out = prose_out()
    w = W(PROSE, "100")
    out["arms"][0]["total_witness"] = {"file": "doc_p.txt", "start": w["start"], "end": w["start"] + 1, "text": "1"}
    out["arms"][0]["total"] = 1
    rec = job(tmp_path, out, SERVED_P, {"doc_p.txt": PROSE})
    assert any(r.startswith("T3") for r in rec["reasons"])


def test_wrong_offsets_are_refused(tmp_path):
    out = prose_out()
    out["arms"][0]["total_witness"]["start"] += 1
    rec = job(tmp_path, out, SERVED_P, {"doc_p.txt": PROSE})
    assert any(r.startswith("T1") for r in rec["reasons"])


def reg_out():
    def R(t, nth=0):
        return W(REG, t, nth, file="doc_registry_NCT0.json")
    return {"ownership_source": "REGISTRY_GROUPS", "arms": [
        {"role": "intervention", "group_id": "EG001", "arm_name": "Drugx", "arm_name_witness": R('"Drugx"'.strip('"')),
         "events": 20, "event_witness": R("20"), "total": 100, "total_witness": R("100")},
        {"role": "comparator", "group_id": "EG000", "arm_name": "Placebo", "arm_name_witness": R("Placebo"),
         "events": 10, "event_witness": R("10"), "total": 98, "total_witness": R("98")}]}


def test_registry_counts_owned_through_their_group_id(tmp_path):
    rec = job(tmp_path, reg_out(), {"ai": 20, "n1i": 100, "ci": 10, "n2i": 98}, {"doc_registry_NCT0.json": REG}, registry=True)
    assert rec["state"] == "WITNESSED", rec["reasons"]


def test_registry_group_swap_is_refused(tmp_path):
    out = reg_out()
    out["arms"][0]["group_id"], out["arms"][1]["group_id"] = "EG000", "EG001"
    rec = job(tmp_path, out, {"ai": 20, "n1i": 100, "ci": 10, "n2i": 98}, {"doc_registry_NCT0.json": REG}, registry=True)
    assert rec["state"] == "INCOMPLETE" and any(r.startswith("T5") for r in rec["reasons"])


def test_prose_used_where_registry_results_exist_is_flagged(tmp_path):
    rec = job(tmp_path, prose_out(), SERVED_P, {"doc_p.txt": PROSE}, registry=True)
    assert any(f.startswith("REGISTRY_NOT_USED") for f in rec["flags"])


def test_a_count_inside_the_group_object_itself_is_owned_by_that_group(tmp_path):
    """adverseEventsModule.eventGroups carry seriousNumAffected/seriousNumAtRisk on the group object ("id", "title")."""
    reg = json.dumps({"adverseEventsModule": {"eventGroups": [
        {"id": "EG000", "title": "Placebo", "seriousNumAffected": 10, "seriousNumAtRisk": 98},
        {"id": "EG001", "title": "Drugx", "seriousNumAffected": 20, "seriousNumAtRisk": 100}]}}, indent=1, sort_keys=True)
    def R(t):
        return W(reg, t, file="doc_registry_NCT0.json")
    out = {"ownership_source": "REGISTRY_GROUPS", "arms": [
        {"role": "intervention", "group_id": "EG001", "arm_name": "Drugx", "arm_name_witness": R("Drugx"),
         "events": 20, "event_witness": R("20"), "total": 100, "total_witness": R("100")},
        {"role": "comparator", "group_id": "EG000", "arm_name": "Placebo", "arm_name_witness": R("Placebo"),
         "events": 10, "event_witness": R("10"), "total": 98, "total_witness": R("98")}]}
    rec = job(tmp_path, out, {"ai": 20, "n1i": 100, "ci": 10, "n2i": 98}, {"doc_registry_NCT0.json": reg}, registry=True)
    assert rec["state"] == "WITNESSED", rec["reasons"]
    out["arms"][0]["group_id"], out["arms"][1]["group_id"] = "EG000", "EG001"
    (tmp_path / "HE-x").rename(tmp_path / "old")
    rec = job(tmp_path, out, {"ai": 20, "n1i": 100, "ci": 10, "n2i": 98}, {"doc_registry_NCT0.json": reg}, registry=True)
    assert rec["state"] == "INCOMPLETE" and any(r.startswith("T5") for r in rec["reasons"])


def test_group_ids_are_resolved_inside_their_own_outcome_measure(tmp_path):
    """OG000 is 'Aspirin' in measure 1 and 'Omega-3' in measure 2; with sorted keys a measure's groups come AFTER
    its counts. The title must come from the measure that contains the witness."""
    reg = json.dumps({"outcomeMeasuresModule": {"outcomeMeasures": [
        {"title": "Aspirin comparison", "denoms": [{"counts": [{"groupId": "OG000", "value": "500"}, {"groupId": "OG001", "value": "501"}]}],
         "classes": [{"categories": [{"measurements": [{"groupId": "OG000", "value": "50"}, {"groupId": "OG001", "value": "51"}]}]}],
         "groups": [{"id": "OG000", "title": "Aspirin"}, {"id": "OG001", "title": "Placebo Aspirin"}]},
        {"title": "AF", "denoms": [{"counts": [{"groupId": "OG000", "value": "7740"}, {"groupId": "OG001", "value": "7741"}]}],
         "classes": [{"categories": [{"measurements": [{"groupId": "OG000", "value": "166"}, {"groupId": "OG001", "value": "135"}]}]}],
         "groups": [{"id": "OG000", "title": "Omega-3"}, {"id": "OG001", "title": "Placebo Omega-3"}]}]}}, indent=1, sort_keys=True)
    def R(t):
        return W(reg, t, file="doc_registry_NCT0.json")
    out = {"ownership_source": "REGISTRY_GROUPS", "arms": [
        {"role": "intervention", "group_id": "OG000", "arm_name": "Omega-3", "arm_name_witness": R("Omega-3"),
         "events": 166, "event_witness": R("166"), "total": 7740, "total_witness": R("7740")},
        {"role": "comparator", "group_id": "OG001", "arm_name": "Placebo Omega-3", "arm_name_witness": R("Placebo Omega-3"),
         "events": 135, "event_witness": R("135"), "total": 7741, "total_witness": R("7741")}]}
    served = {"ai": 166, "n1i": 7740, "ci": 135, "n2i": 7741}
    rec = job(tmp_path, out, served, {"doc_registry_NCT0.json": reg}, registry=True)
    assert rec["state"] == "WITNESSED", rec["reasons"]
    out["arms"][0]["arm_name"] = "Aspirin"   # the other measure's meaning of OG000
    (tmp_path / "HE-x").rename(tmp_path / "old")
    rec = job(tmp_path, out, served, {"doc_registry_NCT0.json": reg}, registry=True)
    assert rec["state"] == "INCOMPLETE" and any(r.startswith("T5") for r in rec["reasons"])


def test_a_typographic_thousands_separator_is_one_token_and_a_plain_space_is_not():
    assert cw.token_value("10\u2008033") == 10033 and cw.token_value("10\u202f033") == 10033
    assert cw.token_value("10 033") is None          # ten and thirty-three, never joined
    assert cw.token_value("1\u20080330") is None     # a separator must start a group of exactly three
    assert cw.token_value("10,033") == 10033 and cw.token_value("twenty") == 20


TERMS = {"intervention_terms": ["drugx"], "comparator_terms": ["placebo"]}


def test_role_is_anchored_to_the_protocol_when_terms_exist(tmp_path):
    rec = job(tmp_path, prose_out(), SERVED_P, {"doc_p.txt": PROSE}, **TERMS)
    assert rec["state"] == "WITNESSED" and not [f for f in rec["flags"] if f.startswith("ROLE_")]


def test_a_consistently_reversed_object_is_refused(tmp_path):
    """The F4 lane's reproduction: placebo declared 'intervention' AND the tuple reversed to match. T5 alone passed it."""
    out = prose_out()
    for a in out["arms"]:
        a["role"] = {"intervention": "comparator", "comparator": "intervention"}[a["role"]]
    reversed_served = {"ai": 9, "n1i": 98, "ci": 9, "n2i": 100}
    rec = job(tmp_path, out, reversed_served, {"doc_p.txt": PROSE}, **TERMS)
    assert rec["state"] == "INCOMPLETE" and sum("ARM_ROLE_MISMATCH" in r for r in rec["reasons"]) == 2


def test_without_protocol_terms_the_role_is_flagged_unanchored_never_silently_passed(tmp_path):
    rec = job(tmp_path, prose_out(), SERVED_P, {"doc_p.txt": PROSE})
    assert any(f.startswith("ROLE_UNANCHORED") for f in rec["flags"])


def test_a_named_absence_arm_is_the_comparator_and_an_unknown_name_is_fixed_by_its_partner(tmp_path):
    out = prose_out()
    out["arms"][1]["arm_name"] = "no-drugx"
    out["arms"][1]["arm_name_witness"] = None
    rec = job(tmp_path, out, SERVED_P, {"doc_p.txt": PROSE}, **TERMS)
    assert not any("ARM_ROLE" in r for r in rec["reasons"])
    out = prose_out()
    out["arms"][0]["arm_name"], out["arms"][0]["arm_name_witness"] = "study drug", None   # neither vocabulary
    for a in out["arms"]:
        a["role"] = {"intervention": "comparator", "comparator": "intervention"}[a["role"]]
    (tmp_path / "b").mkdir()
    rec = job(tmp_path / "b", out, {"ai": 9, "n1i": 98, "ci": 9, "n2i": 100}, {"doc_p.txt": PROSE}, **TERMS)
    assert any("ARM_ROLE_MISMATCH arm 0" in r for r in rec["reasons"])


# ---- review fixes, 2026-09-25 -------------------------------------------------------------------------------------
GROUPED = "Randomly assigned: drugx (n=10\u2008033) or placebo (n=9985). Events: 30 and 34, respectively.\n"


def grouped_out(total_text, total_value):
    at = GROUPED.index(total_text)
    return {"ownership_source": "PROSE_OR_TABLE", "arms": [
        {"role": "intervention", "group_id": None, "arm_name": "drugx", "arm_name_witness": W(GROUPED, "drugx"),
         "events": 30, "event_witness": W(GROUPED, "30"), "total": total_value,
         "total_witness": {"file": "doc_p.txt", "start": at, "end": at + len(total_text), "text": total_text}},
        {"role": "comparator", "group_id": None, "arm_name": "placebo", "arm_name_witness": W(GROUPED, "placebo"),
         "events": 34, "event_witness": W(GROUPED, "34"), "total": 9985, "total_witness": W(GROUPED, "9985")}]}


def test_one_group_of_a_grouped_number_is_not_a_token(tmp_path):
    whole = job(tmp_path, grouped_out("10\u2008033", 10033), {"ai": 30, "n1i": 10033, "ci": 34, "n2i": 9985}, {"doc_p.txt": GROUPED}, **TERMS)
    assert whole["state"] == "WITNESSED", whole["reasons"]
    for i, (text, value) in enumerate((("10", 10), ("033", 33))):
        d = tmp_path / f"g{i}"
        d.mkdir()
        out = grouped_out(text, value) if text == "10" else grouped_out("\u2008033", 33)
        if text == "033":   # the tail group itself
            at = GROUPED.index("\u2008033") + 1
            out["arms"][0]["total_witness"] = {"file": "doc_p.txt", "start": at, "end": at + 3, "text": "033"}
        rec = job(d, out, {"ai": 30, "n1i": value, "ci": 34, "n2i": 9985}, {"doc_p.txt": GROUPED}, **TERMS)
        assert any("grouped number" in r for r in rec["reasons"]), (text, rec["reasons"])


def test_a_role_outside_the_two_values_or_a_duplicate_role_is_refused(tmp_path):
    out = prose_out()
    out["arms"][0]["role"] = "Intervention"
    rec = job(tmp_path, out, None, {"doc_p.txt": PROSE}, **TERMS)
    assert any(r.startswith("ARM_ROLE_INVALID") for r in rec["reasons"])
    out = prose_out()
    out["arms"][1]["role"] = "intervention"
    (tmp_path / "b").mkdir()
    rec = job(tmp_path / "b", out, None, {"doc_p.txt": PROSE}, **TERMS)
    assert any(r.startswith("ARM_ROLE_DUPLICATE") for r in rec["reasons"])


def test_an_add_on_arm_named_with_usual_care_is_still_the_intervention():
    rec = {"reasons": [], "flags": []}
    arms = [{"role": "intervention", "arm_name": "Drugx plus usual care"}, {"role": "comparator", "arm_name": "Usual care"}]
    cw.role_anchor(rec, TERMS, arms)
    assert not rec["reasons"], rec["reasons"]
    rec = {"reasons": [], "flags": []}
    cw.role_anchor(rec, TERMS, [{"role": "intervention", "arm_name": "Placebo drugx"}, {"role": "comparator", "arm_name": "Drugx"}])
    assert any("ARM_ROLE_MISMATCH" in r for r in rec["reasons"])   # 'placebo' is never the intervention


# ---- second review, 2026-09-25: T5 key/list/scope, T3 decimals/thin spaces/hyphens, unchecked group ids ------------
OM = json.dumps({"outcomeMeasuresModule": {"outcomeMeasures": [
    {"title": "Mortality", "denoms": [{"counts": [{"groupId": "OG000", "value": "100"}, {"groupId": "OG001", "value": "98"}]}],
     "classes": [{"categories": [{"measurements": [{"groupId": "OG000", "value": "20", "lowerLimit": "11"}, {"groupId": "OG001", "value": "10"}]}]}],
     "groups": [{"id": "OG000", "title": "Drugx", "description": "drugx; 97 randomised"}, {"id": "OG001", "title": "Placebo"}]},
    {"title": "Some other outcome", "denoms": [{"counts": [{"groupId": "OG000", "value": "101"}, {"groupId": "OG001", "value": "98"}]}],
     "classes": [{"categories": [{"measurements": [{"groupId": "OG000", "value": "21"}, {"groupId": "OG001", "value": "10"}]}]}],
     "groups": [{"id": "OG000", "title": "Drugx"}, {"id": "OG001", "title": "Placebo"}]}]}}, indent=1, sort_keys=True)


def om_out():
    def R(t, nth=0):
        return W(OM, t, nth, file="doc_registry_NCT0.json")
    return {"ownership_source": "REGISTRY_GROUPS", "registry": {"item_title": "Mortality"}, "arms": [
        {"role": "intervention", "group_id": "OG000", "arm_name": "Drugx", "arm_name_witness": R("Drugx"),
         "events": 20, "event_witness": R("20"), "total": 100, "total_witness": R("100")},
        {"role": "comparator", "group_id": "OG001", "arm_name": "Placebo", "arm_name_witness": R("Placebo"),
         "events": 10, "event_witness": R("10"), "total": 98, "total_witness": R("98")}]}


OM_SERVED = {"ai": 20, "n1i": 100, "ci": 10, "n2i": 98}


def _om(tmp_path, out, served=OM_SERVED, name="HE-x"):
    d = tmp_path / name
    d.mkdir()
    return job(d, out, served, {"doc_registry_NCT0.json": OM}, registry=True, **TERMS)


def test_registry_counts_in_one_measure_are_witnessed(tmp_path):
    rec = _om(tmp_path, om_out())
    assert rec["state"] == "WITNESSED", rec["reasons"]


def test_a_registry_token_from_a_non_count_field_or_another_measure_is_refused(tmp_path):
    out = om_out()   # the intervention's events from the OTHER measure (21 there, so pick its 101 total instead)
    out["arms"][0]["total"] = 101
    out["arms"][0]["total_witness"] = W(OM, "101", file="doc_registry_NCT0.json")
    rec = _om(tmp_path, out, {"ai": 20, "n1i": 101, "ci": 10, "n2i": 98}, "a")
    assert any("different scopes" in r for r in rec["reasons"]), rec["reasons"]
    out = om_out()   # comparator events from a lowerLimit field
    out["arms"][0]["events"], out["arms"][0]["event_witness"] = 11, W(OM, "11", file="doc_registry_NCT0.json")
    rec = _om(tmp_path, out, {"ai": 11, "n1i": 100, "ci": 10, "n2i": 98}, "b")
    assert any("not a count field" in r for r in rec["reasons"]), rec["reasons"]
    out = om_out()   # a total from a group description
    out["arms"][0]["total"], out["arms"][0]["total_witness"] = 97, W(OM, "97", file="doc_registry_NCT0.json")
    rec = _om(tmp_path, out, {"ai": 20, "n1i": 97, "ci": 10, "n2i": 98}, "c")
    assert rec["state"] == "INCOMPLETE" and any(r.startswith("T5") for r in rec["reasons"]), rec["reasons"]


def test_a_registry_row_without_group_ids_and_an_unchecked_group_id_on_prose(tmp_path):
    out = om_out()
    for a in out["arms"]:
        a["group_id"] = None
    rec = _om(tmp_path, out, name="a")
    assert any("must carry its group_id" in r for r in rec["reasons"])
    out = prose_out()
    out["arms"][0]["group_id"], out["arms"][1]["group_id"] = "OG001", "OG000"   # asserted, never checked
    (tmp_path / "b").mkdir()
    rec = job(tmp_path / "b", out, SERVED_P, {"doc_p.txt": PROSE}, **TERMS)
    assert rec["state"] == "WITNESSED" and all(a["group_id"] is None for a in rec["arms"])
    assert sum(f.startswith("GROUP_ID_UNCHECKED_DROPPED") for f in rec["flags"]) == 2


def test_part_of_a_decimal_a_thin_space_group_or_a_hyphenated_word_is_not_a_token(tmp_path):
    cases = [("Deaths: drugx 20.5 (n=100) vs placebo 10 (n=98).", "20", 20),
             ("Deaths: drugx 20 (n=10\u2009033) vs placebo 10 (n=98).", "10", 10),
             ("Deaths: drugx twenty-one (n=100) vs placebo 10 (n=98).", "twenty", 20)]
    for k, (doc, tok, val) in enumerate(cases):
        at = doc.index(tok)
        out = {"ownership_source": "PROSE_OR_TABLE", "arms": [
            {"role": "intervention", "group_id": None, "arm_name": "drugx", "arm_name_witness": W(doc, "drugx"),
             "events": val, "event_witness": {"file": "doc_p.txt", "start": at, "end": at + len(tok), "text": tok},
             "total": 100, "total_witness": W(doc, "100") if "n=100" in doc else W(doc, "033")},
            {"role": "comparator", "group_id": None, "arm_name": "placebo", "arm_name_witness": W(doc, "placebo"),
             "events": 10, "event_witness": W(doc, "10", 1 if k == 1 else 0), "total": 98, "total_witness": W(doc, "98")}]}
        (tmp_path / f"d{k}").mkdir()
        rec = job(tmp_path / f"d{k}", out, None, {"doc_p.txt": doc}, **TERMS)
        assert any(r.startswith("T3") for r in rec["reasons"]), (doc, rec["reasons"])


# ---- producer arm_roles + T5b (the main lane's ARM_ROLE_ANCHOR, integrated 2026-09-25) ------------------------------
OMAB = OM.replace('"Drugx"', '"Arm A"').replace('"Placebo"', '"Arm B"')


def test_a_registry_arm_whose_role_contradicts_the_classifier_is_refused_even_when_names_say_nothing(tmp_path):
    """Titles 'Arm A'/'Arm B' carry no protocol vocabulary, so T6 can only flag; the classifier's arm_roles decide."""
    def R(t, nth=0):
        return W(OMAB, t, nth, file="doc_registry_NCT0.json")
    roles = {"intervention": ["drugx"], "comparator": ["placebo"], "source": "test",
             "registry": [{"nct": "NCT0", "scope": "Mortality", "state": "CLASSIFIED",
                           "intervention_group": "OG000", "comparator_group": "OG001"}]}
    def out(swap):
        a = [{"role": "intervention", "group_id": "OG000", "arm_name": "Arm A", "arm_name_witness": R("Arm A"),
              "events": 20, "event_witness": R("20"), "total": 100, "total_witness": R("100")},
             {"role": "comparator", "group_id": "OG001", "arm_name": "Arm B", "arm_name_witness": R("Arm B"),
              "events": 10, "event_witness": R("10"), "total": 98, "total_witness": R("98")}]
        if swap:
            a[0]["role"], a[1]["role"] = "comparator", "intervention"
        return {"ownership_source": "REGISTRY_GROUPS", "registry": {"item_title": "Mortality"}, "arms": a}
    (tmp_path / "a").mkdir()
    ok = job(tmp_path / "a", out(False), OM_SERVED, {"doc_registry_NCT0.json": OMAB}, registry=True, arm_roles=roles)
    assert ok["state"] == "WITNESSED", ok["reasons"]
    (tmp_path / "b").mkdir()
    bad = job(tmp_path / "b", out(True), {"ai": 10, "n1i": 98, "ci": 20, "n2i": 100}, {"doc_registry_NCT0.json": OMAB},
              registry=True, arm_roles=roles)
    assert any(r.startswith("T5b") for r in bad["reasons"]), bad["reasons"]


def test_arm_roles_come_from_the_topic_config_and_the_pipelines_classifier():
    import sys
    sys.path.insert(0, os.path.join(HERE, "..", "evidence", "typed_arms", "witness"))
    import arm_roles
    ta = os.path.join(HERE, "..", "evidence", "typed_arms")
    r = arm_roles.arm_roles_for("pcsk9-mace", [os.path.join(ta, "registry", "NCT03872401.json")])
    assert r["source"] == "topics/pcsk9-mace.json" and "evolocumab" in r["intervention"]
    chd = [e for e in r["registry"] if e["scope"].startswith("Number of Participants Who Experienced Coronary Heart Disease")]
    assert chd and chd[0]["state"] == "CLASSIFIED" and (chd[0]["intervention_group"], chd[0]["comparator_group"]) == ("OG001", "OG000")
    for d in ("extractions_witness", "extractions_witness_served"):
        for j in os.listdir(os.path.join(ta, d)):
            row = json.load(open(os.path.join(ta, d, j, "row.json"), encoding="utf-8"))
            assert row.get("arm_roles", {}).get("source"), (d, j, "every packet carries the protocol's arm_roles")


def test_local_only_witnesses_reverify_when_their_held_copy_is_present():
    """A witness in a non-redistributable full text is held beside v2 (witness/local_only/). Where the held copy exists
    (evid2's machine), its sha256 and every token offset must still hold; elsewhere the test says so and skips."""
    import glob, hashlib, pytest
    recs = glob.glob(os.path.join(HERE, "..", "evidence", "typed_arms", "witness", "local_only", "*.json"))
    assert recs
    held = os.environ.get("EVID2_HELD", r"C:\mh-lanes\evid2-held")
    checked = 0
    for p in recs:
        rec = json.load(open(p, encoding="utf-8"))
        for a in rec["arms"]:
            for w in (a["event_witness"], a["total_witness"]):
                f = os.path.join(held, w["document"].split(":", 1)[1])
                if not os.path.exists(f):
                    continue
                raw = open(f, "rb").read()
                assert hashlib.sha256(raw).hexdigest() == w["document_sha256"]
                t = raw.decode("utf-8")
                assert t[w["start"]:w["end"]] == w["text"] == str(a["events"] if w["role"].endswith("events") else a["total"])
                checked += 1
    if not checked:
        pytest.skip("no local-only held copy in this checkout (sha256 recorded)")
