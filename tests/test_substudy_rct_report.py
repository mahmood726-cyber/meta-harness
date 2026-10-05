"""Decision 5 Oct (Handbook, Mahmood's delegation): a 'substudy' reporting a prespecified outcome of a trial's randomised
comparison is a report of that RCT -- eligible; the title word alone never excludes (X1 narrowed to records that say the
analysis is non-randomised, post hoc or observational); collated with its parent as one study; with no open data it is
NO_OPEN_SOURCE. Plants: colchicine-postop Imazio [19] passes; a true observational substudy fails."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from harness import screen, trial_family  # noqa: E402

CFG = json.load(open(os.path.join(ROOT, "topics", "colchicine-postop-af.json"), encoding="utf-8"))
INC = screen.effective_include(CFG)


def _held(pmid):
    R = json.load(open(os.path.join(ROOT, "cache", "colchicine-postop-af", "records.json"), encoding="utf-8"))
    return next(r for r in R["records"] if str(r.get("id")) == pmid)


def test_plant_imazio_19_substudy_of_a_stated_rct_passes():
    d = screen.screen_record(_held("22090167"), INC, set())
    assert d.decision == "include", d


def test_plant_a_true_observational_substudy_fails_x1():
    rec = dict(_held("22090167"),
               title="Colchicine and postoperative atrial fibrillation: an observational substudy of a cardiac surgery registry.",
               abstract="In this observational cohort study of patients undergoing cardiac surgery, colchicine users were "
                        "compared with non-users for postoperative atrial fibrillation.")
    assert screen.screen_record(rec, INC, set()).rule_id == "X1"
    post_hoc = dict(_held("22090167"), title="Colchicine and atrial fibrillation: a post hoc substudy of COPPS.")
    assert screen.screen_record(post_hoc, INC, set()).rule_id == "X1"


def test_design_papers_still_never_count_as_results():
    rec = dict(_held("22090167"), title="Colchicine for atrial fibrillation after surgery: rationale and design of a randomized trial.")
    assert screen.screen_record(rec, INC, set()).rule_id == "X1"


def test_a_substudy_is_collated_with_its_parent_trial():
    base = {"pubtypes": ["Randomized Controlled Trial"], "abstract": "randomized"}
    parent = dict(base, id="111", title="Colchicine for the prevention of the post-pericardiotomy syndrome (COPPS) trial",
                  nct="NCT00128427")
    sub = dict(base, id="22090167", title="Colchicine reduces postoperative atrial fibrillation: results of the COPPS "
                                          "atrial fibrillation substudy", nct="NCT00128427")
    echo = dict(base, id="20952767", title="Effects of n-3 PUFA on left ventricular function: a substudy of GISSI-HF trial")
    gissi = dict(base, id="18757090", title="Effect of n-3 polyunsaturated fatty acids in patients with chronic heart "
                                            "failure (the GISSI-HF trial)", nct="NCT00336336")
    recs = [dict(r, id=trial_family._rid(r), registry_ids=trial_family.registry_ids(r)) for r in (parent, sub, echo, gissi)]
    trial_family._collate_substudies(recs)
    by = {r["id"]: r for r in recs}
    assert by["20952767"]["registry_ids"] == ["NCT00336336"]                       # joined via its own title
    assert trial_family.registry_ids(by["22090167"]) == trial_family.registry_ids(by["111"]) == ["NCT00128427"]
