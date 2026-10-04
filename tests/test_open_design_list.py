"""X-DESIGN audit: a design list states open-label without the word 'label' -- colchicine-postop-af Zarpelon [20]
(PMID 27223641, PMC4976950): 'a prospective, randomized, open, single-center clinical assay' read BLINDING_NOT_STATED."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import k_gap_exclusion_audit as ea  # noqa: E402


def test_open_in_a_design_list_is_open_label():
    for s in ("This is a prospective, randomized, open, single-center clinical assay",
              "DESIGN AND SETTING: Open randomized controlled trial in 17 units", "An open, prospective, comparative study",
              "an open-label trial"):
        assert ea.OPEN.search(s), s


def test_open_elsewhere_is_not():
    for s in ("randomized open heart surgery patients", "the trial was open to all patients", "open study visits",
              "patients undergoing open-heart surgery were randomized"):
        assert not ea.OPEN.search(s), s
