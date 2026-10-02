"""G1 exclusion audit over the TRACKER population (scripts/g1_exclusion_audit_tracker.py) and the two screener classes it
found and fixed in harness/screen.py. Each plant fires with its guard removed and not as built; controls stay put.
Plant items are built from the HELD records directly, not from the current population: the shared audit
(k_gap_exclusion_audit) now covers most exclusions, and this lane audits only what it leaves."""
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
SHARED = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "exclusion_audit.json"), encoding="utf-8"))
t.load_axes()
_OLD_BODY_RCT = re.compile(s._BODY_RCT.pattern.replace("|controlled study", ""), re.I)
_MREC = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "member_records.json"), encoding="utf-8"))


def _item(slug, pmid, rule):
    rec = t._records(slug).get(pmid) or _MREC.get(pmid) or t.lane_record(slug, pmid)
    assert rec, (slug, pmid)
    return {"slug": slug, "label": pmid, "pmid": pmid, "found_as": pmid, "blocker": f"SCREENED_OUT_UNAUDITED:{rule}",
            "recorded_rule": rule, "rec": rec, "via_decision": None}


def _refine(slug, pmid, rule):
    it = _item(slug, pmid, rule)
    cls, sc, base = xa.classify(it["rec"], xa._cfg(slug))
    return (cls, sc), t.refine(it, cls, sc, base)


def test_every_tracker_exclusion_is_audited_by_one_of_the_two_audits():
    """Every comparator trial the tracker shows as screened out has a row in the shared audit or in this lane's; none is
    left SCREENED_OUT_UNAUDITED. This lane's rows are n of n classified."""
    classes = {"TRUE_SCOPE_DIFFERENCE", "SCREENER_ERROR", "INSUFFICIENT_RECORD", "INCONSISTENT", "NOT_AN_EXCLUSION"}
    assert A["n"] == len(A["rows"]) == sum(A["by_class"].values()) and all(r["class"] in classes for r in A["rows"])
    covered = {(r["slug"], str(r["pmid"])) for r in SHARED["rows"]} | {(r["slug"], str(r["pmid"])) for r in A["rows"]}
    missing = []
    for f in os.listdir(t.G1):
        d = json.load(open(os.path.join(t.G1, f), encoding="utf-8"))
        for x in d.get("trials") or []:
            sf = x.get("seeded_funnel") or {}
            m = t.PMID_IN.search(x.get("our_refusal") or "")
            pm = m.group(1) if m else sf.get("pmid")
            if sf.get("stage") == "SCREENED_OUT" or str(x.get("blocker") or "").startswith("SCREENED_OUT_UNAUDITED"):
                if (d["slug"], str(pm)) not in covered:
                    missing.append(f"{d['slug']}::{x['label']}::{pm}")
    assert not missing, missing


def test_plant_substudy_title_veto_on_a_typed_rct_is_fixed():
    rec = _item("colchicine-postop-af", "22090167", "X1")["rec"]           # COPPS-POAF
    assert s._TITLE_RCT_NOT.search(rec["title"])                           # the old veto fired on it (guard removed)
    assert s._is_rct(rec)                                                  # as built: a randomised trial report
    assert s.screen_record(rec, xa._cfg("colchicine-postop-af")["include"], set()).decision == "include"


def test_control_a_substudy_that_does_not_describe_its_randomisation_stays_out():
    rec = {"id": "c1", "id_type": "pmid", "title": "Diarrhea in Mechanically Ventilated Patients: A Nested Multicenter "
           "Substudy.", "abstract": "We describe diarrhoea incidence in a cohort nested in a larger trial.",
           "pubtypes": ["Journal Article", "Randomized Controlled Trial"]}
    assert not s._is_rct(rec)


def test_plant_randomized_controlled_study_is_a_self_described_rct():
    rec = _item("probiotics-aad-prevention", "32944084", "X1")["rec"]       # Wu 2020: 'a prospective, randomized,
    assert not _OLD_BODY_RCT.search(rec["abstract"])                         # controlled study' -- old pattern missed it
    assert s._body_says_rct(rec)
    assert not s._BODY_RCT.search("A systematic review of randomized controlled studies of probiotics.")   # control


def test_plant_a_repair_flip_never_overrides_a_stated_protocol_exclusion():
    shared, refined = _refine("tranexamic-acid-pph", "39461792", "X2")    # WOMAN-2: 'prevent postpartum haemorrhage'
    assert shared[0] == "SCREENER_ERROR"                                    # fires with the lane guard removed
    assert refined[0] == "TRUE_SCOPE_DIFFERENCE" and "'prevent'" in refined[1]


def test_plant_a_repair_flip_with_an_unstated_axis_is_insufficient_not_an_error():
    shared, refined = _refine("sglt2-hfref-hosp-cvdeath", "33200892", "X3")  # SOLOIST-WHF: X3 misfired, EF unstated
    assert shared[0] == "SCREENER_ERROR" and refined[0] == "INSUFFICIENT_RECORD" and "POPULATION_NOT_STATED" in refined[1]


def test_the_design_axis_never_answers_a_context_rule():
    shared, refined = _refine("metformin-pcos-ovulation", "16827766", "X-DESIGN")   # 'required design/context absent'
    assert shared[0] == "INSUFFICIENT_RECORD" and refined[0] == "INSUFFICIENT_RECORD"


def test_every_true_scope_row_of_this_audit_carries_a_span_or_is_not_named():
    """The shared contract: a TRUE_SCOPE_DIFFERENCE names a trial only with the record's own words (span). A row of this
    audit without a span is never used to name (scripts/g1_sglt2_tracker.py requires au['span'])."""
    for r in A["rows"]:
        if r["class"] == "TRUE_SCOPE_DIFFERENCE" and r.get("span"):
            assert (r["span"].get("text") or "").strip()
