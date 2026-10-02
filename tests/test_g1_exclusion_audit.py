"""G1 exclusion audit over the TRACKER population (scripts/g1_exclusion_audit_tracker.py) and the two screener classes it
found and fixed in harness/screen.py. Each plant fires with its guard removed and not as built; controls stay put."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_exclusion_audit_tracker as t  # noqa: E402
import k_gap_exclusion_audit as xa  # noqa: E402
from harness import screen as s  # noqa: E402

A = json.load(open(t.OUT, encoding="utf-8"))
ROWS = {(r["slug"], str(r["pmid"])): r for r in A["rows"]}
t.load_axes()
POP = {(p["slug"], str(p["pmid"])): p for p in t.population()}
_OLD_BODY_RCT = re.compile(s._BODY_RCT.pattern.replace("|controlled study", ""), re.I)


def _refine(key):
    it = POP[key]
    cls, sc, base = xa.classify(it["rec"], xa._cfg(it["slug"]))
    return (cls, sc), t.refine(it, cls, sc, base)


def test_every_tracker_exclusion_is_classified_n_of_n():
    classes = {"TRUE_SCOPE_DIFFERENCE", "SCREENER_ERROR", "INSUFFICIENT_RECORD", "INCONSISTENT", "NOT_AN_EXCLUSION"}
    assert A["n"] == len(A["rows"]) == sum(A["by_class"].values()) and A["n"] >= 81
    assert all(r["class"] in classes for r in A["rows"])
    # an item THIS audit already classified (written into the lane tracker) stays in the denominator
    assert ("sglt2-hfref-hosp-cvdeath", "33200892") in ROWS and ("sglt2-hfref-hosp-cvdeath", "34449189") in ROWS


def test_plant_substudy_title_veto_on_a_typed_rct_is_fixed():
    rec = POP[("colchicine-postop-af", "22090167")]["rec"]                 # COPPS-POAF
    assert s._TITLE_RCT_NOT.search(rec["title"])                           # the old veto fired on it (guard removed)
    assert s._is_rct(rec)                                                  # as built: a randomised trial report
    assert s.screen_record(rec, xa._cfg("colchicine-postop-af")["include"], set()).decision == "include"


def test_control_a_substudy_that_does_not_describe_its_randomisation_stays_out():
    rec = {"id": "c1", "id_type": "pmid", "title": "Diarrhea in Mechanically Ventilated Patients: A Nested Multicenter "
           "Substudy.", "abstract": "We describe diarrhoea incidence in a cohort nested in a larger trial.",
           "pubtypes": ["Journal Article", "Randomized Controlled Trial"]}
    assert not s._is_rct(rec)


def test_plant_randomized_controlled_study_is_a_self_described_rct():
    rec = POP[("probiotics-aad-prevention", "32944084")]["rec"]             # Wu 2020: 'a prospective, randomized,
    assert not _OLD_BODY_RCT.search(rec["abstract"])                         # controlled study' -- old pattern missed it
    assert s._body_says_rct(rec)
    assert not s._BODY_RCT.search("A systematic review of randomized controlled studies of probiotics.")   # control


def test_plant_a_repair_flip_never_overrides_a_stated_protocol_exclusion():
    shared, refined = _refine(("tranexamic-acid-pph", "39461792"))          # WOMAN-2: 'prevent postpartum haemorrhage'
    assert shared[0] == "SCREENER_ERROR"                                    # fires with the lane guard removed
    assert refined[0] == "TRUE_SCOPE_DIFFERENCE" and "'prevent'" in refined[1]


def test_plant_a_repair_flip_with_an_unstated_axis_is_insufficient_not_an_error():
    shared, refined = _refine(("sglt2-hfref-hosp-cvdeath", "33200892"))     # SOLOIST-WHF: X3 misfired, EF unstated
    assert shared[0] == "SCREENER_ERROR" and refined[0] == "INSUFFICIENT_RECORD" and "POPULATION_NOT_STATED" in refined[1]


def test_the_design_axis_never_answers_a_context_rule():
    shared, refined = _refine(("metformin-pcos-ovulation", "16827766"))     # 'required design/context absent'
    assert shared[0] == "INSUFFICIENT_RECORD" and refined[0] == "INSUFFICIENT_RECORD"


def test_named_topics_are_fully_classified():
    named = {"doac-vte-recurrence", "sglt2-ckd-progression", "colchicine-postop-af", "tranexamic-acid-pph",
             "empagliflozin-hfpef-hosp", "sacubitril-valsartan-hfref", "sglt2-primary-prevention-hf",
             "sglt2-hfref-hosp-cvdeath"}
    rows = [r for r in A["rows"] if r["slug"] in named]
    # 34 = colchicine-postop-af 6 + doac-vte 1 + empagliflozin-hfpef 2 + sacubitril 8 + sglt2-ckd 9
    #      + sglt2-primary-prevention 2 + tranexamic-acid 4 + sglt2-hfref 2 (counted from the tracker files' blockers)
    assert len(rows) == 34 and not [r for r in rows if r["class"] == "INCONSISTENT"]
