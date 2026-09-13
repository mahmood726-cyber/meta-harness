"""Arm-contrast parser (TIER-1 structural fix, six audits). Eligibility must test the RANDOMISED CONTRAST
(what differs between arms), not the co-occurrence of the drug word. The check may only ever REMOVE a
provably-background inclusion; it must FAIL OPEN (never invent an exclusion) when arm data is missing or a
coded-name granularity gap hides a genuine contrast, and must NEVER flag a real drug-vs-placebo trial.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import armcontrast as ac  # noqa: E402

# minimal in-memory index: {NCT: (common_set, differing_set)}
IDX = {
    "NCT_DRUGPLACEBO": (set(), {"dapagliflozin"}),                 # genuine drug vs placebo
    "NCT_ACTIVECOMP": (set(), {"sacubitril/valsartan", "enalapril"}),  # active-comparator
    "NCT_BACKGROUND": ({"dapagliflozin"}, {"balcinrenone"}),        # MIRO-CKD: drug in every arm
    "NCT_BG_CODED": ({"metformin", "sglt2 inhibitor"}, {"insulin glargine/lixisenatide"}),  # SGLT2 background coded
    "NCT_DEVCODE": (set(), {"bi 10773"}),                          # empagliflozin coded as dev code
    "NCT_NOCONTRAST": ({"prednisone"}, set()),                     # only one active intervention coded
}
SGLT2 = ["empagliflozin", "canagliflozin", "dapagliflozin", "ertugliflozin", "SGLT2"]


def test_genuine_drug_vs_placebo_is_kept():
    assert ac.background_only_inclusion("NCT_DRUGPLACEBO", SGLT2, IDX) is False
    assert ac.contrast_status("NCT_DRUGPLACEBO", SGLT2, IDX)[0] == "verified"


def test_active_comparator_is_kept():
    kw = ["sacubitril", "sacubitril/valsartan"]
    assert ac.background_only_inclusion("NCT_ACTIVECOMP", kw, IDX) is False
    assert ac.contrast_status("NCT_ACTIVECOMP", kw, IDX)[0] == "verified"


def test_background_in_every_arm_is_flagged():
    # MIRO-CKD pattern: dapagliflozin in all arms, randomised contrast is balcinrenone.
    assert ac.background_only_inclusion("NCT_BACKGROUND", SGLT2, IDX) is True
    assert ac.contrast_status("NCT_BACKGROUND", SGLT2, IDX)[0] == "background_only"


def test_background_coded_class_label_is_flagged():
    # LIRA-pattern where the registry DID code 'sglt2 inhibitor' as a common (all-arm) intervention.
    assert ac.background_only_inclusion("NCT_BG_CODED", SGLT2, IDX) is True


def test_dev_code_granularity_fails_open_never_excludes():
    # empagliflozin coded as 'BI 10773': a genuine contrast the keyword cannot match -> must NOT be excluded.
    assert ac.background_only_inclusion("NCT_DEVCODE", SGLT2, IDX) is False
    assert ac.contrast_status("NCT_DEVCODE", SGLT2, IDX)[0] == "unverified_granularity"


def test_no_coded_contrast_fails_open():
    assert ac.background_only_inclusion("NCT_NOCONTRAST", ["prednisone", "corticosteroid"], IDX) is None
    assert ac.contrast_status("NCT_NOCONTRAST", ["prednisone"], IDX)[0] == "unverified_no_contrast"


def test_no_arm_data_fails_open_and_is_visible():
    assert ac.background_only_inclusion("NCT_ABSENT", SGLT2, IDX) is None
    st, basis = ac.contrast_status("NCT_ABSENT", SGLT2, IDX)
    assert st == "unverified_no_arm_data" and "no registry arm data" in basis


def test_placebo_normalised_away():
    # a 'Placebo for dapagliflozin' comparator arm must not leak 'dapagliflozin' into the control side.
    assert ac._norm_intv("Placebo for dapagliflozin") is None
    assert ac._norm_intv("Matching placebo") is None
    assert ac._norm_intv("Dapagliflozin 10 mg") == "dapagliflozin 10 mg"
