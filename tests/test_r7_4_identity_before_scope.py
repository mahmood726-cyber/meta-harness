"""R7-4: G1 classifies a comparator unit by its VERIFIED intervention identity before any scope rule. SOLOIST-WHF
(sotagliflozin, NCT03521934) was AGENT_UNCONFIRMED in the empagliflozin topic (no agent in its unit text; its NCT not in
the k-gap AACT index) and was then named a POPULATION scope difference ('diabetes') -- it is another agent's trial.
g1_tracker.verified_agent_identity reads the registered interventions (AACT interventions.txt) for such units.
Synthetic fixtures."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402

AGENTS = {"t": ["empagliflozin", "jardiance"]}


def snap(tmp_path, rows):
    (tmp_path / "interventions.txt").write_text(
        "id|nct_id|intervention_type|name\n" + "".join(f"{i}|{n}|{ty}|{nm}\n" for i, (n, ty, nm) in enumerate(rows)),
        encoding="utf-8")
    return str(tmp_path)


def T(*units):
    return {"trials": [dict({"slug": "t", "drug": "AGENT_UNCONFIRMED"}, **u) for u in units]}


def test_PLANT_soloist_is_another_agents_trial_by_its_registered_interventions(tmp_path):
    s = snap(tmp_path, [("NCT03521934", "DRUG", "Sotagliflozin"), ("NCT03521934", "DRUG", "Placebo")])
    t = gt.verified_agent_identity(T({"label": "SOLOIST-WHF", "ncts": ["NCT03521934"]}), AGENTS, s)
    u = t["trials"][0]
    assert u["drug"] == "OTHER_AGENT" and "REGISTRY_INTERVENTIONS" in u["identity_basis"][-1]


def test_PLANT_a_registered_topic_agent_confirms_the_drug(tmp_path):
    s = snap(tmp_path, [("NCT01", "DRUG", "Empagliflozin 10 mg"), ("NCT01", "DRUG", "Placebo")])
    assert gt.verified_agent_identity(T({"label": "X", "ncts": ["NCT01"]}), AGENTS, s)["trials"][0]["drug"] == "DRUG_MATCH"


def test_PLANT_no_registered_drug_rows_or_no_snapshot_leaves_it_unconfirmed(tmp_path):
    s = snap(tmp_path, [("NCT02", "BEHAVIORAL", "Exercise")])
    assert gt.verified_agent_identity(T({"label": "Y", "ncts": ["NCT02"]}), AGENTS, s)["trials"][0]["drug"] == "AGENT_UNCONFIRMED"
    assert gt.verified_agent_identity(T({"label": "Y", "ncts": ["NCT02"]}), AGENTS, str(tmp_path / "none"))["trials"][0][
        "drug"] == "AGENT_UNCONFIRMED"


def test_a_drug_match_unit_is_never_touched(tmp_path):
    s = snap(tmp_path, [("NCT03", "DRUG", "Dapagliflozin")])
    t = gt.verified_agent_identity({"trials": [{"slug": "t", "drug": "DRUG_MATCH", "label": "Z", "ncts": ["NCT03"]}]},
                                   AGENTS, s)
    assert t["trials"][0]["drug"] == "DRUG_MATCH"


def test_PLANT_in_a_class_topic_an_unlisted_agent_is_for_the_protocol_to_decide(tmp_path):
    # sglt2-hfref-hosp-cvdeath is an 'SGLT2 inhibitors' CLASS topic: whether sotagliflozin (a dual SGLT1/2 inhibitor)
    # belongs is a protocol decision, never inferred from the agent list
    s = snap(tmp_path, [("NCT03521934", "DRUG", "Sotagliflozin")])
    t = gt.verified_agent_identity(T({"label": "SOLOIST-WHF", "ncts": ["NCT03521934"]}), AGENTS, s, class_topics={"t"})
    u = t["trials"][0]
    assert u["drug"] == "AGENT_UNCONFIRMED" and "CLASS_TOPIC_PROTOCOL_DECIDES" in u["identity_basis"][-1]


def test_PLANT_x2_sweep_flags_a_bare_config_term_the_protocol_qualifies():
    import r7_4_x2_wording_sweep as sw
    x2 = "X2** - wrong population, including HFrEF/LVEF <=40%, diabetes-only, CKD-only populations."
    assert sw.classify("diabetes", x2) == "CONFIG_BROADER_THAN_PROTOCOL"
    assert sw.classify("HFrEF", x2) == "MATCHES_PROTOCOL"
    assert sw.classify("pregnan", x2) == "NOT_IN_PROTOCOL_X2"
    assert sw.classify("diabetes", None) == "NO_PROTOCOL_X2"


def test_PLANT_r1_an_unnamed_registered_drug_cannot_establish_another_agent(tmp_path):
    s = snap(tmp_path, [("NCT04", "DRUG", ""), ("NCT04", "DRUG", "Sotagliflozin")])
    assert gt.verified_agent_identity(T({"label": "U", "ncts": ["NCT04"]}), AGENTS, s)["trials"][0]["drug"] == "AGENT_UNCONFIRMED"
    s = snap(tmp_path, [("NCT05", "DRUG", "  ")])
    assert gt.verified_agent_identity(T({"label": "V", "ncts": ["NCT05"]}), AGENTS, s)["trials"][0]["drug"] == "AGENT_UNCONFIRMED"


def test_PLANT_r1_x2_text_stops_at_another_rules_table_row_and_qualifiers_need_boundaries():
    import r7_4_x2_wording_sweep as sw
    x2 = sw.x2_text("| X2 | Wrong population: children. |\n| X3 | Wrong intervention: diabetes drugs. |")
    assert "X3" not in x2 and sw.classify("diabetes", x2) == "NOT_IN_PROTOCOL_X2"
    assert sw.classify("diabetes", "X2: Exclude diabetes; also exclude prediabetes-only cohorts.") == "MATCHES_PROTOCOL"
    assert sw.classify("diabetes", "X2: exclude diabetes; and diabetes-only cohorts") == "MATCHES_PROTOCOL"
    assert sw.classify("diabetes", "X2: only diabetes populations") == "CONFIG_BROADER_THAN_PROTOCOL"


def test_PLANT_r2_topic_agent_inside_a_placebo_named_row_still_matches(tmp_path):
    s = snap(tmp_path, [("NCT06", "DRUG", "empagliflozin plus matching placebo"), ("NCT06", "DRUG", "dapagliflozin")])
    assert gt.verified_agent_identity(T({"label": "W", "ncts": ["NCT06"]}), AGENTS, s)["trials"][0]["drug"] == "DRUG_MATCH"
    s = snap(tmp_path, [("NCT07", "DRUG", "Matching Placebo Tablets"), ("NCT07", "DRUG", "Sotagliflozin")])
    assert gt.verified_agent_identity(T({"label": "W", "ncts": ["NCT07"]}), AGENTS, s)["trials"][0]["drug"] == "OTHER_AGENT"


def test_PLANT_r2_no_topic_agent_definition_cannot_establish_another_agent(tmp_path):
    s = snap(tmp_path, [("NCT08", "DRUG", "empagliflozin")])
    assert gt.verified_agent_identity(T({"label": "W", "ncts": ["NCT08"]}), {}, s)["trials"][0]["drug"] == "AGENT_UNCONFIRMED"


def test_PLANT_r2_a_snapshot_missing_required_columns_is_a_schema_error(tmp_path):
    import pytest
    (tmp_path / "interventions.txt").write_text("nct_id|type|name\nNCT09|DRUG|empagliflozin\n", encoding="utf-8")
    with pytest.raises(ValueError, match="intervention_type"):
        gt.verified_agent_identity(T({"label": "W", "ncts": ["NCT09"]}), AGENTS, str(tmp_path))


def test_PLANT_r2_x2_definition_beats_a_cross_reference_and_unicode_hyphens_qualify():
    import r7_4_x2_wording_sweep as sw
    x2 = sw.x2_text("See X2 for population exclusions.\n\n- X2: diabetes-only\n- X3: wrong intervention")
    assert sw.classify("diabetes", x2) == "CONFIG_BROADER_THAN_PROTOCOL"
    assert sw.classify("diabetes", "X2: diabetes‑only") == "CONFIG_BROADER_THAN_PROTOCOL"


def test_PLANT_r3_a_placebo_named_for_the_topic_drug_is_not_the_topic_drug(tmp_path):
    for i, pl in enumerate(["Placebo for empagliflozin", "empagliflozin placebo", "Placebo to match empagliflozin",
                            "Empagliflozin matching placebo"]):
        s = snap(tmp_path, [(f"NCT1{i}", "DRUG", pl), (f"NCT1{i}", "DRUG", "Sotagliflozin")])
        u = gt.verified_agent_identity(T({"label": "P", "ncts": [f"NCT1{i}"]}), AGENTS, s)["trials"][0]
        assert u["drug"] == "OTHER_AGENT", pl
    s = snap(tmp_path, [("NCT20", "DRUG", "Empagliflozin with matching placebo")])
    assert gt.verified_agent_identity(T({"label": "Q", "ncts": ["NCT20"]}), AGENTS, s)["trials"][0]["drug"] == "DRUG_MATCH"


def test_PLANT_r3_numbered_definitions_and_long_rules_are_read_whole():
    import r7_4_x2_wording_sweep as sw
    assert sw.classify("diabetes", sw.x2_text("See X2 for diabetes exclusions.\n\n2. **X2**: Exclude diabetes-only "
                                              "populations.")) == "CONFIG_BROADER_THAN_PROTOCOL"
    md = ("- X2: Exclude the following populations:\n  - children;\n  - pregnant patients;\n  - healthy volunteers;\n"
          "  - diabetes-only populations.\n- X3: Wrong intervention: diabetes drugs.")
    x2 = sw.x2_text(md)
    assert "X3" not in x2 and sw.classify("diabetes", x2) == "CONFIG_BROADER_THAN_PROTOCOL"


def test_PLANT_r4_dose_bearing_placebo_names_are_placebos(tmp_path):
    for i, pl in enumerate(["Empagliflozin 10 mg placebo", "Placebo for empagliflozin 10 mg"]):
        s = snap(tmp_path, [(f"NCT3{i}", "DRUG", pl)])
        u = gt.verified_agent_identity(T({"label": "P", "ncts": [f"NCT3{i}"]}), AGENTS, s)["trials"][0]
        assert u["drug"] == "AGENT_UNCONFIRMED", pl
    s = snap(tmp_path, [("NCT32", "DRUG", "Empagliflozin 10 mg plus matching placebo")])
    assert gt.verified_agent_identity(T({"label": "Q", "ncts": ["NCT32"]}), AGENTS, s)["trials"][0]["drug"] == "DRUG_MATCH"


def test_PLANT_r4_a_listed_nct_without_registered_drugs_blocks_other_agent(tmp_path):
    s = snap(tmp_path, [("NCT40", "DRUG", "Sotagliflozin")])
    u = gt.verified_agent_identity(T({"label": "R", "ncts": ["NCT40", "NCT41"]}), AGENTS, s)["trials"][0]
    assert u["drug"] == "AGENT_UNCONFIRMED"


def test_PLANT_r4_cross_reference_is_no_rule_and_eligible_sentences_do_not_clear_a_term():
    import r7_4_x2_wording_sweep as sw
    assert sw.x2_text("See X2 for diabetes exclusions.") is None
    assert sw.classify("diabetes", sw.x2_text("See X2 for diabetes exclusions.")) == "NO_PROTOCOL_X2"
    assert sw.classify("diabetes", "- X2: Exclude diabetes-only trials. Trials with heart failure and diabetes are "
                                   "eligible.") == "CONFIG_BROADER_THAN_PROTOCOL"
    assert sw.classify("diabetes", "- X2: Exclude diabetes. Trials with diabetes are not eligible.") == "MATCHES_PROTOCOL"


def test_PLANT_r4_inline_bold_definition_is_read_to_the_next_rule():
    import r7_4_x2_wording_sweep as sw
    x2 = sw.x2_text("- Exclude: **X1** not RCT; **X2** wrong population (diabetes-only,\n  children); **X3** wrong drug "
                    "(diabetes drugs).")
    assert "X3" not in x2 and sw.classify("diabetes", x2) == "CONFIG_BROADER_THAN_PROTOCOL"
