"""Esketamine-TRD: Mahmood's RETROSPECTIVE clarification of 'newly-initiated oral antidepressant', recorded verbatim
with attribution, implemented as the explicit field `oad_initiation` (never a keyword), set per trial from its own
held source text. Takahashi (lead-in-initiated OAD) meets the field under the governing message but is ALSO excluded by
the phase-2 amendment, whose premise is not in the registered protocol: held UNRESOLVED, not silently decided."""
import copy
import json
import os
import shutil

import pytest

from harness import eligibility_field as ef, fetch, pipeline

ROOT = pipeline.ROOT
SLUG = "esketamine-trd-madrs"
CONFIG = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
_REV = {}


def _review():
    if "rv" not in _REV:
        _REV["rv"] = pipeline.build_review_core(SLUG, CONFIG, fetch.ensure(CONFIG, ""), "test")
    return _REV["rv"]


def test_the_clarification_is_recorded_verbatim_attributed_and_labelled_retrospective():
    r = ef.resolve(SLUG)
    c = r["clarification"]
    assert c["kind"] == "RETROSPECTIVE_PROTOCOL_CLARIFICATION" and c["decided_after_seeing_data"] is True
    m1, m2 = c["messages"]
    assert m1["verbatim"] == "newly started can be any time after randomisation as long as that is the intervention"
    assert m2["verbatim"] == "I think include as esketamine is the intervention."
    assert {m1["by"], m2["by"]} == {"Mahmood"}
    assert m1["how_it_reached_the_reviewer"] == m2["how_it_reached_the_reviewer"] == "Dispatch chat relay"
    assert (m1["status"], m2["status"]) == ("REFINED_BY_MESSAGE_2", "GOVERNING")


def test_each_trial_carries_its_field_value_from_its_own_source():
    t = {x["trial"]: x for x in ef.resolve(SLUG)["trials"]}
    for name in ("TRANSFORM-1", "TRANSFORM-2", "TRANSFORM-3", "Chen (China)"):
        assert t[name]["value"] == "AT_OR_AFTER_RANDOMISATION" and t[name]["meaning"] == "QUALIFIES"
    tk = t["Takahashi (Japan)"]
    assert tk["value"] == "PRE_RANDOMISATION_LEAD_IN_CONTINUED_UNCHANGED"
    assert tk["meaning"] == "QUALIFIES_DISCLOSED_DESIGN_DIFFERENCE"
    assert any("continued unchanged from the prospective lead-in phase" in w for w in tk["witnesses"])
    assert ef.resolve(SLUG)["sensitivity_analysis"]["members"] == ["Takahashi (Japan)"]


def test_takahashi_is_held_unresolved_not_silently_included_or_excluded():
    row = next(r for r in _review()["screening"]["records"] if "34696742" in str(r["id"]))
    assert row["decision"] == "awaiting_classification" and row["rule_id"] == "A-PROTOCOL-CONFLICT"
    assert sorted(p["kind"] for p in row["pending_decisions"]) == ["MULTI_ARM_SELECTION", "PENDING_PROTOCOL_CONFLICT"]
    assert row["screening_record"]["parent_eligibility"]["state"] == "UNRESOLVED"


def test_the_served_consequence_is_derived_no_k_change_until_the_phase_2_ruling():
    o = next(o for o in _review()["outcomes"] if "MADRS" in o["name"])
    assert o["result"]["k"] == 3 and not any("34696742" in str(t["id"]) for t in o["trials"])
    assert ef.problems(_review()) == []


def test_a_pooled_trial_whose_field_does_not_qualify_or_is_undeclared_is_blocking():
    rv = copy.deepcopy(_review())
    rv["protocol_clarifications"]["trials"][0]["value"] = "NOT_NEWLY_INITIATED"          # PLANT
    rv["protocol_clarifications"]["trials"][0]["meaning"] = "DOES_NOT_QUALIFY"
    o = next(o for o in rv["outcomes"] if "MADRS" in o["name"])
    o["trials"] = o["trials"] + [{"id": "NCT02417064"}, {"id": "PMID 99999999"}]            # PLANT: undeclared trial
    kinds = [p["kind"] for p in ef.problems(rv)]
    assert kinds.count("ELIGIBILITY_FIELD_CONFLICT") == 2


def test_a_corrupted_field_witness_fails_closed(tmp_path):
    (tmp_path / "docs").mkdir()
    d = json.load(open(os.path.join(ROOT, "docs", "protocol_clarifications.json"), encoding="utf-8"))
    d["fields"][SLUG][4]["witnesses"][0]["span"] = d["fields"][SLUG][4]["witnesses"][0]["span"].replace("6 weeks", "4 weeks")
    (tmp_path / "docs" / "protocol_clarifications.json").write_text(json.dumps(d), encoding="utf-8")
    for rel in ("protocols/esketamine-trd-madrs.md", "cache/esketamine-trd-madrs/ft_34696742.txt",
                "cache/esketamine-trd-madrs/ft_37025256.txt", "evidence/acquisition_cascade/held/NCT02417064/NCT02417064.json",
                "evidence/acquisition_cascade/held/NCT02422186/NCT02422186.json",
                "evidence/acquisition_cascade/held/TRANSFORM-2/NCT02418585.json"):
        (tmp_path / os.path.dirname(rel)).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, rel), tmp_path / rel)
    with pytest.raises(ValueError, match="not in the held bytes"):
        ef.resolve(SLUG, str(tmp_path))
