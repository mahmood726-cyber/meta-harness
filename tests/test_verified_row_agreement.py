"""A comparator trial matched through a VERIFIED non-pool row is compared on that row: empagliflozin-hfpef
EMPEROR-Preserved (meta 35338608 PRIMARY_VERIFIED) and colchicine-postop Zarpelon read NOT_IN_OUR_POOL while their
pairs were already in the same-trials comparison."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402
from harness import secondary_meta as sm  # noqa: E402


def _row(**kw):
    base = dict(meta_pmid="35338608", meta_doi="", location={}, source_digest="", provenance="TYPED_TABLE",
                trial_label="EMPEROR-Preserved", measure="HR", outcome_definition="", effect="0.79", lower="0.69",
                upper="0.90", events_t=None, n_t=None, events_c=None, n_c=None)
    base.update(kw)
    return sm.SecondaryRow(**base)


def test_row_value_carries_the_compared_fields():
    v = gt.row_value(_row())
    assert v == {"measure": "HR", "effect": "0.79", "lower": "0.69", "upper": "0.90", "events_t": None, "n_t": None,
                 "events_c": None, "n_c": None}
    assert gt.row_value(None) is None


def test_a_verified_row_agrees_or_disagrees_with_the_comparator_row():
    theirs = _row(meta_pmid="37773799", provenance="COMPARATOR_ROW")
    assert gt.agreement(gt.row_value(_row()), theirs) == "AGREE"
    assert gt.agreement(gt.row_value(_row(effect="0.70")), theirs) == "DISAGREE"
