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
        # COPPS POAF substudy: the screener error was FIXED (the screen includes it since the substudy exception);
        # what remains is extraction -- its POAF counts are not in the held abstract (consolidation 2026-10-04)
        "Imazio [19]": "EXTRACTION:OUTCOME_NOT_IN_SOURCE",
        # COPPS-2: no held analysis set reproduces the comparator's 0.66 (0.45-0.96); on-treatment is only NEAREST (NR-C20)
        "Imazio [18]": "COMPARATOR_ROW_UNREPRODUCED:NEAREST_HELD_SET_NAMED",
        "Tabbalat [21]": "SAME_NUMBER",                                                  # END-AF low dose
        "Sarzaeem [23]": "NOT_IN_REGISTERED_SOURCES"}                                  # Tehran Univ Med J 2014
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
    if not t.get("fulltext_span"):
        import pytest
        pytest.skip("Zarpelon's PMC full-text body (gitignored) is not held in this clone: its stating span is unverifiable here")
    assert t["stating_span"].startswith("Methods Study Design and Participants This is a prospective, randomized, open")


def test_the_comparators_conclusion_does_not_survive_on_the_shared_trials():
    r = _res()
    s = r["scenarios"]
    assert s["A_shared_trials_comparator_rows"]["conclusion"] == "BENEFIT"
    assert s["B_shared_trials_our_rows_ITT"]["conclusion"] == "NULL_INCLUDED"
    assert s["C_shared_trials_held_set_nearest_the_comparator_row"]["conclusion"] == "BENEFIT"
    assert r["comparator_conclusion"]["on_shared_trials"] == "DOES_NOT_SURVIVE"
    # within protocol scope the benefit returns only with comparator-only, unverified rows: the COPPS substudy's and --
    # since the consolidated label join attaches the comparator's row to it -- Sarzaeem [23]'s (eligible, not indexed in
    # the registered sources). Neither is a row of ours (consolidation 2026-10-04)
    F = s["F_protocol_scope_only_with_ITT_where_held"]
    assert "Imazio [19]" in F["comparator_only_rows"] and set(F["comparator_only_rows"]) <= {"Imazio [19]", "Sarzaeem [23]"}
    ours = {t["trial"] for t in r["trials"] if t.get("cls") == "SAME_NUMBER"}
    assert not (set(F["comparator_only_rows"]) & ours)


def test_pre_fix_tracker_left_zarpelon_and_the_substudy_unresolved():
    # the base (acq/k-gap 8de6953) names the 4 record-spanned exclusions; Zarpelon (full text only) stays an open gap and
    # the COPPS substudy reads as a thin record, not the screener error it is
    base = json.loads(subprocess.check_output(["git", "show", f"8de695346c3d63bb8da41446ce61c20b26e7166a:outputs/k_gap/g1/{SLUG}.json"], cwd=ROOT))
    assert base["N_eligible"] == 5 and "Zarpelon [20]" in base["open_gaps"]
    assert base["top_blocker"] == "INSUFFICIENT_RECORD:DESIGN_NOT_ESTABLISHED_BY_RECORD"


def test_reconcile_output_never_lands_among_the_tracker_rows():
    # every reader of outputs/k_gap/g1/*.json (the table, the audit's in-screen population, the scope-citation plant)
    # takes each file as a tracker row; a sidecar there crashed the table (KeyError 'routes') and failed the plant
    import g1_tracker as gt
    assert os.path.dirname(rc.RECON_DIR) == os.path.dirname(gt.G1_DIR) and rc.RECON_DIR != gt.G1_DIR
    assert not [f for f in os.listdir(gt.G1_DIR) if "reconcile" in f]
    assert os.path.exists(os.path.join(rc.RECON_DIR, SLUG + ".json"))


def test_sarzaeem_is_identified_by_the_comparators_own_reference_and_stays_eligible():
    r = _res()
    t = next(t for t in r["trials"] if t["trial"] == "Sarzaeem [23]")
    assert "Tehran Univ Med J 2014;72:147-154" in t["cited_reference"]["citation"]
    assert "stays ELIGIBLE" in t["verdict"]
    assert {q["source"] for q in t["searches"]} >= {"PubMed", "Europe PMC REST search"}
    # the identity is taken only when the pinned reference entry holds every required string (fails on one it lacks)
    c = rc.CITED_OUTSIDE_SOURCES[(SLUG, "Sarzaeem [23]")]
    assert rc.cited_reference_holds(c) and not rc.cited_reference_holds(dict(c, must_contain=c["must_contain"] + ["Lancet"]))
    import g1_tracker as gt
    g = json.load(open(os.path.join(gt.G1_DIR, SLUG + ".json"), encoding="utf-8"))
    assert "Sarzaeem [23]" in g["open_gaps"]                        # never named out of the denominator
