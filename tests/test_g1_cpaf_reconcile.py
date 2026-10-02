"""G1 colchicine-postop-af reconciliation plants (scripts/g1_reconcile.py): per comparator trial whose number is right and
why, and whether the comparator's conclusion survives on the shared trials. Pre-fix firing: at the branch base the
tracker named 0 of these differences and called 7 of 9 comparator trials open gaps."""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import g1_reconcile as rc  # noqa: E402

SLUG = "colchicine-postop-af"


def _res():
    return rc.reconcile(SLUG)


def test_every_comparator_trial_has_a_class_and_a_reason():
    r = _res()
    cls = {t["trial"]: t["cls"] for t in r["trials"]}
    assert cls == {
        "Bessissow [17]": "TRUE_SCOPE_DIFFERENCE:PROTOCOL_EXCLUDES_POPULATION",        # lung resection
        "Deftereos [15]": "TRUE_SCOPE_DIFFERENCE:PROTOCOL_EXCLUDES_POPULATION",        # pulmonary vein isolation
        "Deftereos [16]": "TRUE_SCOPE_DIFFERENCE:PROTOCOL_EXCLUDES_POPULATION",
        "Tabbalat [22]": "TRUE_SCOPE_DIFFERENCE:OPEN_LABEL_STATED",
        "Zarpelon [20]": "TRUE_SCOPE_DIFFERENCE:OPEN_DESIGN_STATED_FOR_THIS_STUDY",    # from its PMC full text
        "Imazio [19]": "SCREENER_ERROR:SECONDARY_REPORT_OF_RCT",                        # COPPS POAF substudy
        # COPPS-2: no held analysis set reproduces the comparator's 0.66 (0.45-0.96); on-treatment is only NEAREST (NR-C20)
        "Imazio [18]": "COMPARATOR_ROW_UNREPRODUCED:NEAREST_HELD_SET_NAMED",
        "Tabbalat [21]": "SAME_NUMBER",                                                  # END-AF low dose
        "Sarzaeem [23]": "IDENTITY_UNRESOLVED"}
    assert all(t.get("verdict") for t in r["trials"])


def test_copps2_both_numbers_are_in_the_report_and_ours_is_the_registered_estimand():
    t = next(t for t in _res()["trials"] if t["trial"] == "Imazio [18]")
    assert t["right_number_for_protocol"].startswith("all randomised")
    assert t["comparator_row_attribution"] == "NOT_REPRODUCED" and t["nearest_set_to_comparator_row"] == "on-treatment"
    assert "is nearest to, but is not reproduced by," in t["verdict"]
    assert "61 patients" in t["ours_span"] and "38/141" in t["theirs_span"]


def test_zarpelon_comparator_row_is_reproduced_from_our_held_counts():
    t = next(t for t in _res()["trials"] if t["trial"] == "Zarpelon [20]")
    assert t["comparator_row_reproduced_from_counts"] is True
    assert t["stating_span"].startswith("Methods Study Design and Participants This is a prospective, randomized, open")


def test_the_comparators_conclusion_does_not_survive_on_the_shared_trials():
    r = _res()
    s = r["scenarios"]
    assert s["A_shared_trials_comparator_rows"]["conclusion"] == "BENEFIT"
    assert s["B_shared_trials_our_rows_ITT"]["conclusion"] == "NULL_INCLUDED"
    assert s["C_shared_trials_held_set_nearest_the_comparator_row"]["conclusion"] == "BENEFIT"
    assert r["comparator_conclusion"]["on_shared_trials"] == "DOES_NOT_SURVIVE"
    # within protocol scope the benefit returns only with the COPPS substudy's comparator-only, unverified row
    assert s["F_protocol_scope_only_with_ITT_where_held"]["comparator_only_rows"] == ["Imazio [19]"]


def test_pre_fix_tracker_left_zarpelon_and_the_substudy_unresolved():
    # the base (acq/k-gap 8de6953) names the 4 record-spanned exclusions; Zarpelon (full text only) stays an open gap and
    # the COPPS substudy reads as a thin record, not the screener error it is
    base = json.loads(subprocess.check_output(["git", "show", f"origin/acq/k-gap:outputs/k_gap/g1/{SLUG}.json"], cwd=ROOT))
    assert base["N_eligible"] == 5 and "Zarpelon [20]" in base["open_gaps"]
    assert base["top_blocker"] == "INSUFFICIENT_RECORD:DESIGN_NOT_ESTABLISHED_BY_RECORD"


def test_reconcile_output_never_lands_among_the_tracker_rows():
    # every reader of outputs/k_gap/g1/*.json (the table, the audit's in-screen population, the scope-citation plant)
    # takes each file as a tracker row; a sidecar there crashed the table (KeyError 'routes') and failed the plant
    import g1_tracker as gt
    assert os.path.dirname(rc.RECON_DIR) == os.path.dirname(gt.G1_DIR) and rc.RECON_DIR != gt.G1_DIR
    assert not [f for f in os.listdir(gt.G1_DIR) if "reconcile" in f]
    assert os.path.exists(os.path.join(rc.RECON_DIR, SLUG + ".json"))
