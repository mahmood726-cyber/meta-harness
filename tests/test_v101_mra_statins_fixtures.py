"""V1.0.1 (MRA-HFrEF and statins-older-adults reviews). Served fixtures read the committed pages; plants are synthetic.

MRA: Zhang 2025's 9 trials are not our target; its Figure 4D (HFrEF all-cause mortality) is RALES, EPHESUS and
EMPHASIS-HF -- shared 2 of our 3, EPHESUS excluded by our protocol (post-MI), J-EMPHASIS-HF not in it. The plot prints
log[HR] and SE, and its fixed-effect result reproduces exactly. Statins: a registry condition the trial's own exclusion
criteria refuse (PREVENTABLE's dementia) is a prevention target, not a diagnosis; a subgroup report's registration is
its parent trial's (JUPITER = NCT00239681); Huang 2022 is observational; Ridker 2017 is an RCT checkpoint not held."""
import copy
import json
from pathlib import Path

import pytest

from harness import comparator_analysis as ca
from harness import comparator_panel as cp
from harness import condition_role as cr
from harness import design_key
from harness import identity
from harness import parent_registration as pr
from harness import positive_control as pc

ROOT = Path(__file__).resolve().parents[1]
MRA, ST = "spironolactone-hfref-mortality", "statins-primary-prevention-elderly"


def _review(slug):
    return json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))


def _page(slug):
    return (ROOT / "docs" / "reviews" / slug / "index.html").read_text(encoding="utf-8")


def _control(cid):
    return next(c for c in pc.load(ROOT) if c["id"] == cid)


# ---- MRA ------------------------------------------------------------------------------------------------------------
def test_figure_4d_is_the_governing_set_and_shares_two_of_our_three():
    ov = _review(MRA)["comparator"]["overlap"]
    assert (ov["relation"], ov["ours_k"], ov["theirs_k"], ov["shared_k"]) == ("OVERLAPPING", 3, 3, 2)
    page = _page(MRA)
    assert "EPHESUS (row 2)" in page and "SCREENED_OUT" in page
    assert "J-EMPHASIS-HF, is not in it" in page


def test_rales_binds_through_the_comparators_own_citation():
    panel = json.loads((ROOT / "cache" / MRA / "comparators.json").read_text(encoding="utf-8"))[0]
    rales = next(t for t in panel["trial_set"] if t["name_in_source"] == "RALES")
    assert {a["id"] for a in rales["aliases"]} == {"10471456", "10.1056/NEJM199909023411001"}
    cp.validate(panel, ROOT)
    bad = copy.deepcopy(panel)
    a = next(t for t in bad["trial_set"] if t["name_in_source"] == "RALES")["aliases"][0]
    a["linked_rid"] = "B14"  # EPHESUS's reference: the citation after 'RALES' does not link it
    with pytest.raises(ValueError):
        cp.validate(bad, ROOT)


def test_figure_4d_rows_check_against_the_plot_itself():
    doc = ca.load(ROOT, MRA)
    assert [r["label"] for r in doc["membership"]["rows"]] == ["RALES2000", "EPHESUS 2003", "EMPHASIS-HF2011"]
    for field, value in (("weight", 40.0), ("effect", [0.72, 0.61, 0.82])):
        bad = copy.deepcopy(doc["membership"]["rows"])
        bad[0]["printed"][field] = value
        with pytest.raises(ca.AnalysisRefused):
            ca._check_log_rows(MRA, bad, doc["governing"])


def test_figure_4d_fixed_effect_reproduces_exactly():
    c = _control("zhang-2025-mra-hfref-all-cause-mortality")
    got = pc.reproduce(c, ROOT)
    assert pc.compare(c, got) == []
    assert got["CE"] == pytest.approx((0.782269, 0.717895, 0.852414), abs=1e-6)
    assert got["Q"] == pytest.approx(3.530321, abs=1e-6) and got["I2"] == pytest.approx(43.35, abs=0.005)


# ---- statins: condition as outcome ------------------------------------------------------------------------------------
PREVENTABLE_CRIT = ("Inclusion Criteria:~* Community-dwelling adults~* Age >=75 years~Exclusion Criteria:~* Clinically "
                    "evident cardiovascular disease~* Dementia (clinically evident or previously diagnosed)~* Active Liver Disease")


def test_a_condition_the_criteria_exclude_is_a_prevention_target():
    t = cr.prevention_targets(PREVENTABLE_CRIT, ["Cognitive Impairment, Mild", "Dementia"], "Lipid-lowering in Older Adults",
                              ["dementia", "heart failure"])
    assert [(x["term"], x["condition"]) for x in t] == [("dementia", "Dementia")]


@pytest.mark.parametrize("crit, conds, title", [
    ("Inclusion Criteria:~* Diagnosed dementia~Exclusion Criteria:~* Dementia with Lewy bodies", ["Dementia"], "A trial"),
    ("Inclusion Criteria:~* Adults~Exclusion Criteria:~* history of diabetes insipidus", ["Diabetes"], "A trial"),
    ("Inclusion Criteria:~* Adults~Exclusion Criteria:~* metastatic breast cancer", ["Breast Cancer"], "A trial"),
    ("Inclusion Criteria:~* Adults~Exclusion Criteria:~* Dementia", ["Dementia"], "Statins in Dementia"),
    (None, ["Dementia"], "A trial"),
])
def test_a_condition_is_a_diagnosis_unless_the_criteria_refuse_it_unqualified(crit, conds, title):
    # inclusion names it; a qualified subset; a title that names it; no held criteria (silence is not evidence)
    assert cr.prevention_targets(crit, conds, title, ["dementia", "diabetes", "cancer", "breast cancer"]) == []


def test_preventable_is_eligible_ongoing_and_moves_no_number():
    row = next(x for x in _review(ST)["screening"]["records"] if x["id"].endswith("NCT04262206"))
    assert row["decision"] == "include" and row["completeness_state"] == "eligible+ongoing"
    assert row["condition_role"]["withdrawn"]["rule_id"] == "X2"
    prim = next(o for o in _review(ST)["outcomes"] if o.get("primary"))
    assert sorted(t["label"] for t in prim["trials"]) == ["20404379", "42670961"]


def test_registry_designs_leaves_the_screened_record_alone():
    rec = {"id": "NCT04262206", "id_type": "nct"}
    design_key.registry_designs({"ctgov": [rec], "designs": [{"nct_id": "NCT04262206", "id": "227809937"}]})
    assert rec["id"] == "NCT04262206"


def test_a_registry_record_is_its_own_registration_in_identity():
    ids = identity.build_identities([{"id": "NCT00418834", "id_type": "nct"}])
    assert identity._family_id(ids[0]) == "NCT00418834"


# ---- statins: parent registration --------------------------------------------------------------------------------------
def test_jupiter_report_is_registered_through_its_parent():
    recs = json.loads((ROOT / "cache" / ST / "records.json").read_text(encoding="utf-8"))
    out = pr.merge(ROOT, ST, recs)
    got = {str(r["id"]): r.get("nct") for r in out["records"] if str(r["id"]) in ("20404379", "30251369")}
    # ALLHAT-LLT's report is the same class but NOT linked this round: the same-registration de-duplication would
    # collapse it into 28531241 without a screening row (it must stay a visible include)
    assert got == {"20404379": "NCT00239681", "30251369": None} or got == {"20404379": "NCT00239681", "30251369": ""}
    inc = sorted(x["id"] for x in _review(ST)["screening"]["records"] if x["decision"] == "include")
    assert inc == ["20404379", "28531241", "30251369", "42670961", "PREVENTABLE · NCT04262206"]
    page = _page(ST)
    assert "pre-registration-era" not in page and "20404379 = JUPITER NCT00239681" in page
    assert "contributing to any outcome 2 of" in page and "pooled in primary 2 of" in page


def test_a_parent_link_not_located_in_the_report_is_refused():
    recs = json.loads((ROOT / "cache" / ST / "records.json").read_text(encoding="utf-8"))
    by_id = {str(r.get("id")): r for v in recs.values() if isinstance(v, list) for r in v if isinstance(r, dict)}
    x = dict(pr.links(ROOT, ST)[0], paper_quote="DESIGN: Secondary analysis of JUPITER, an observational cohort study.")
    with pytest.raises(pr.LinkRefused):
        pr.validate(ROOT, ST, x, by_id)
    y = dict(pr.links(ROOT, ST)[0], acronym="HOPE-3")
    with pytest.raises(pr.LinkRefused):
        pr.validate(ROOT, ST, y, by_id)


def test_ridker_rct_checkpoint_is_pending_never_run_from_memory():
    c = _control("ridker-2017-jupiter-hope3-elderly-3point")
    assert c["state"] == "PENDING_SOURCE" and c["expected"]["CE"] == [0.7441, 0.6053, 0.9147]
    with pytest.raises(pc.PendingSource):
        pc.reproduce(c, ROOT)


def test_huang_2022_is_observational_and_shares_no_rct_input():
    ov = _review(ST)["comparator"]["overlap"]
    assert (ov["relation"], ov["shared_k"]) == ("DISJOINT", 0)


def test_two_registrations_sharing_an_acronym_stay_two_families():
    units = identity.build_publication_units([{"id": "NCT04906720", "id_type": "nct", "acronym": "PAPERS"},
                                              {"id": "NCT06731595", "id_type": "nct", "acronym": "PAPERS"}])
    assert {units[k]["trial_family_id"] for k in units} == {"NCT04906720", "NCT06731595"}
