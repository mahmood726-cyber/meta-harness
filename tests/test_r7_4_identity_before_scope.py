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
