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


def job(tmp_path, out, served, docs, registry=False):
    j = tmp_path / "HE-x"
    j.mkdir()
    rows = []
    for name, text in docs.items():
        (j / name).write_bytes(text.encode("utf-8"))
        rows.append({"file": name, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "origin": name})
    (j / "row.json").write_text(json.dumps({"held_key": "x/1", "served": served, "documents": rows,
                                            "registry_results": [{"nct": "NCT0"}] if registry else []}), encoding="utf-8")
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
