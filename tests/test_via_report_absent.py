"""A trial matched to us only through ANOTHER of its reports is blocked by that report's declaration, not by the screen:
pcsk9 GLAGOV (NCT01813422) -- the comparator cites 27264224; we include the JAMA 2016 report 27846344, which is declared
absent for MACE from its abstract with no full text held. The blocker used to read 'SCREENED_VIA_OTHER_REPORT'."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402

F = {"stage": "SCREENED_VIA_OTHER_REPORT", "via": "27846344", "nct": "NCT01813422", "via_decision": "include",
     "pmid": "27264224"}


def _x(**kw):
    return dict({"label": "GLAGOV NCT01813422", "family": None, "in_our_pool": False, "seeded_funnel": F}, **kw)


def test_the_included_reports_declaration_is_the_blocker():
    x = _x(via_report_absent={"id": "PMID 27846344", "code": "outcome_not_reported", "full_text_held": False})
    assert gt.blocker_class(x, "pcsk9-mace") == "EXTRACTION:outcome_not_reported:VIA_OTHER_REPORT:DECLARED_WITHOUT_FULL_TEXT"


def test_held_or_unknown_full_text_adds_no_qualifier():
    for held in (True, None):
        x = _x(via_report_absent={"id": "PMID 27846344", "code": "outcome_not_reported", "full_text_held": held})
        assert gt.blocker_class(x, "pcsk9-mace") == "EXTRACTION:outcome_not_reported:VIA_OTHER_REPORT"


def test_without_a_declaration_the_stage_still_names_itself():
    assert gt.blocker_class(_x(), "pcsk9-mace") == "SCREENED_VIA_OTHER_REPORT"
