"""Registry-linkage checker (evidence/typed_arms/reglink/check_reglink.py). Synthetic registry only; every pointer the
reader gives is resolved against the bytes, never trusted."""
import hashlib, importlib.util, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = importlib.util.spec_from_file_location("check_reglink", os.path.join(HERE, "..", "evidence", "typed_arms", "reglink", "check_reglink.py"))
cr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cr)

REG = {"resultsSection": {
    "baselineCharacteristicsModule": {"groups": [{"id": "BG000", "title": "Drugx"}, {"id": "BG001", "title": "Placebo"},
                                                 {"id": "BG002", "title": "Total"}]},
    "outcomeMeasuresModule": {"outcomeMeasures": [{"title": "Death", "groups": [{"id": "OG000", "title": "Drugx"}, {"id": "OG001", "title": "Placebo"}],
        "denoms": [{"counts": [{"groupId": "OG000", "value": "100"}, {"groupId": "OG001", "value": "98"}]}],
        "classes": [{"categories": [{"measurements": [{"groupId": "OG000", "value": "20"}, {"groupId": "OG001", "value": "10"}]}]}]}]}}}
M = "/resultsSection/outcomeMeasuresModule/outcomeMeasures/0"


def job(tmp_path, out):
    raw = json.dumps(REG, indent=1).encode()
    (tmp_path / "registry_NCT1.json").write_bytes(raw)
    (tmp_path / "rows.json").write_text(json.dumps({"nct": "NCT1", "registry_file": "registry_NCT1.json",
        "registry_sha256": hashlib.sha256(raw).hexdigest(), "rows": [{"population": "held", "row_key": "t/1", "outcome": "Death",
        "arms": [{"role": "intervention", "arm_name": "drugx", "events": 20, "total": 100},
                 {"role": "comparator", "arm_name": "placebo", "events": 10, "total": 98}]}]}))
    (tmp_path / "out.json").write_text(json.dumps(out))
    return cr.check_job(str(tmp_path))["rows"][0]


def reading(title0="Drugx", v1="10", same=True):
    return {"rows": [{"row_key": "t/1", "arm_correspondence": "ONE_TO_ONE",
        "arms": [{"role": "intervention", "links": [{"pointer": "/resultsSection/baselineCharacteristicsModule/groups/0", "id": "BG000", "title": title0},
                                                     {"pointer": f"{M}/groups/0", "id": "OG000", "title": "Drugx"}]},
                 {"role": "comparator", "links": [{"pointer": f"{M}/groups/1", "id": "OG001", "title": "Placebo"}]}],
        "outcome_candidates": [{"pointer": M, "title": "Death", "same_outcome": same, "why": "x", "per_group": [
            {"group_id": "OG000", "value": "20", "value_pointer": f"{M}/classes/0/categories/0/measurements/0",
             "denominator": "100", "denominator_pointer": f"{M}/denoms/0/counts/0"},
            {"group_id": "OG001", "value": v1, "value_pointer": f"{M}/classes/0/categories/0/measurements/1",
             "denominator": "98", "denominator_pointer": f"{M}/denoms/0/counts/1"}]}]}]}


def test_resolved_links_and_equal_numbers(tmp_path):
    r = job(tmp_path, reading())
    assert r["state"] == "LINKED" and r["outcome_candidates"][0]["state"] == "REGISTRY_CARRIES_OUTCOME_EQUAL"


def test_a_copied_title_the_pointer_does_not_hold_is_refused(tmp_path):
    r = job(tmp_path, reading(title0="Drugx 10 mg"))
    assert r["arms"][0]["links"][0]["state"] == "LINK_REFUSED"


def test_a_copied_number_the_pointer_does_not_hold_refuses_the_candidate(tmp_path):
    r = job(tmp_path, reading(v1="11"))
    assert r["outcome_candidates"][0]["state"] == "CANDIDATE_REFUSED"


def test_a_different_outcome_is_never_compared(tmp_path):
    assert job(tmp_path, reading(same=False))["outcome_candidates"][0]["state"] == "DIFFERENT_OUTCOME"


def test_committed_registry_links_reproduce_from_repo_bytes(tmp_path):
    ta = os.path.join(HERE, "..", "evidence", "typed_arms")
    out = tmp_path / "links.json"
    cr.main(os.path.join(ta, "reglink", "extractions"), str(out))
    assert json.load(open(out, encoding="utf-8")) == json.load(open(os.path.join(ta, "reglink", "REGISTRY_LINKS.json"), encoding="utf-8"))


# ---- review fixes, 2026-09-25 -------------------------------------------------------------------------------------
def _measure(title, first, second, e0, e1):
    return {"title": title, "groups": [{"id": "OG000", "title": first}, {"id": "OG001", "title": second}],
            "denoms": [{"counts": [{"groupId": "OG000", "value": "100"}, {"groupId": "OG001", "value": "98"}]}],
            "classes": [{"categories": [{"measurements": [{"groupId": "OG000", "value": e0}, {"groupId": "OG001", "value": e1}]}]}]}


def _eleven(tmp_path, reading, arms=None):
    """measure 1: OG000 = Drugx; measure 10: OG000 = Placebo (arms reversed). A link in /1 must not speak for /10."""
    ms = [_measure(f"M{i}", "Drugx", "Placebo", "1", "1") for i in range(11)]
    ms[10] = _measure("Death", "Placebo", "Drugx", "10", "20")
    reg = {"resultsSection": {"outcomeMeasuresModule": {"outcomeMeasures": ms}}}
    raw = json.dumps(reg, indent=1).encode()
    (tmp_path / "registry_NCT1.json").write_bytes(raw)
    (tmp_path / "rows.json").write_text(json.dumps({"nct": "NCT1", "registry_file": "registry_NCT1.json",
        "registry_sha256": hashlib.sha256(raw).hexdigest(), "rows": [{"population": "held", "row_key": "t/1", "outcome": "Death",
        "arms": arms or [{"role": "intervention", "arm_name": "drugx", "events": 20, "total": 100},
                         {"role": "comparator", "arm_name": "placebo", "events": 10, "total": 98}]}]}))
    (tmp_path / "out.json").write_text(json.dumps(reading))
    return cr.check_job(str(tmp_path))["rows"][0]


M1, M10 = "/resultsSection/outcomeMeasuresModule/outcomeMeasures/1", "/resultsSection/outcomeMeasuresModule/outcomeMeasures/10"


def _reading(cand_ptr, v_ptr_base, gid0="OG000", gid1="OG001"):
    return {"rows": [{"row_key": "t/1", "arm_correspondence": "ONE_TO_ONE",
        "arms": [{"role": "intervention", "links": [{"pointer": f"{M1}/groups/0", "id": "OG000", "title": "Drugx"}]},
                 {"role": "comparator", "links": [{"pointer": f"{M1}/groups/1", "id": "OG001", "title": "Placebo"}]}],
        "outcome_candidates": [{"pointer": cand_ptr, "title": "Death", "same_outcome": True, "why": "x", "per_group": [
            {"group_id": gid0, "value": "20", "value_pointer": f"{v_ptr_base}/classes/0/categories/0/measurements/1",
             "denominator": "100", "denominator_pointer": f"{v_ptr_base}/denoms/0/counts/0"},
            {"group_id": gid1, "value": "10", "value_pointer": f"{v_ptr_base}/classes/0/categories/0/measurements/0",
             "denominator": "98", "denominator_pointer": f"{v_ptr_base}/denoms/0/counts/1"}]}]}]}


def test_a_link_in_measure_1_never_speaks_for_measure_10(tmp_path):
    """Every pointer here is internally consistent; only the scope match is wrong. In measure 10 OG000 is Placebo
    (10/100). With '/1' treated as a prefix of '/10', measure 1's links would call OG000 the intervention, and a row
    whose intervention reads 10/100 (a REWIND-style swap) would be scored EQUAL."""
    reading = {"rows": [{"row_key": "t/1", "arm_correspondence": "ONE_TO_ONE",
        "arms": [{"role": "intervention", "links": [{"pointer": f"{M1}/groups/0", "id": "OG000", "title": "Drugx"}]},
                 {"role": "comparator", "links": [{"pointer": f"{M1}/groups/1", "id": "OG001", "title": "Placebo"}]}],
        "outcome_candidates": [{"pointer": M10, "title": "Death", "same_outcome": True, "why": "x", "per_group": [
            {"group_id": "OG000", "value": "10", "value_pointer": f"{M10}/classes/0/categories/0/measurements/0",
             "denominator": "100", "denominator_pointer": f"{M10}/denoms/0/counts/0"},
            {"group_id": "OG001", "value": "20", "value_pointer": f"{M10}/classes/0/categories/0/measurements/1",
             "denominator": "98", "denominator_pointer": f"{M10}/denoms/0/counts/1"}]}]}]}
    swapped_row = [{"role": "intervention", "arm_name": "drugx", "events": 10, "total": 100},
                   {"role": "comparator", "arm_name": "placebo", "events": 20, "total": 98}]
    r = _eleven(tmp_path, reading, arms=swapped_row)
    assert not r["outcome_candidates"][0]["problems"]
    assert r["outcome_candidates"][0]["state"] == "SAME_OUTCOME_ARMS_NOT_LINKED_IN_THIS_MEASURE"


def test_a_number_pointer_outside_the_candidates_measure_is_refused(tmp_path):
    r = _eleven(tmp_path, _reading(M1, M10))
    assert r["outcome_candidates"][0]["state"] == "CANDIDATE_REFUSED"


def test_a_number_pointer_on_another_groups_measurement_is_refused(tmp_path):
    """per-group item labelled OG000 whose value_pointer lands on OG001's measurement"""
    r = _eleven(tmp_path, _reading(M10, M10))
    assert any("belongs to group" in p for p in r["outcome_candidates"][0]["problems"])


def test_rfc6901_array_indexes_are_strict():
    import pytest
    for bad in ("/a/01", "/a/-1"):
        with pytest.raises(KeyError):
            cr.resolve({"a": [1, 2]}, bad)
    assert cr.resolve({"a": [1, 2]}, "/a/1") == 2


def test_a_link_whose_group_title_names_the_other_arm_is_refused(tmp_path, monkeypatch):
    """Review item 11: LINKED used to mean only 'the pointer holds what the reader copied'."""
    monkeypatch.setattr(cr, "row_terms", lambda row: ({"drugx"}, {"placebo"}))
    bad = reading()
    bad["rows"][0]["arms"][0]["links"] = [{"pointer": f"{M}/groups/1", "id": "OG001", "title": "Placebo"}]   # intervention -> placebo group
    r = job(tmp_path, bad)
    assert r["arms"][0]["links"][0]["state"] == "LINK_REFUSED" and "protocol's comparator" in r["arms"][0]["links"][0]["why"]
