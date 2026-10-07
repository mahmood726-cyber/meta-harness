"""Plant: a served-pool row never cites the COMPARATOR's own row as its span. V6-01's TECOS row took its span from the
comparator table (which calls TECOS's 3-point 0.99 its 4-point composite); the endpoint gate refused it once signed rows
met the gate. The trial's own sources come first and comparator keys are never read."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import build_served_pool_additions as b  # noqa: E402


def test_comparator_row_spans_are_never_collected():
    x = {"label": "T", "comparator_row_provenance": {"span": "COMPARATOR TABLE 0.99 (0.89-1.10)"},
         "comparator_sourced": {"provenance": {"quote": "COMPARATOR QUOTE"}},
         "our_value": {"span": "OUR SOURCE 0.99 (0.89, 1.1)"}}
    got = b._spans(x)
    assert got == ["OUR SOURCE 0.99 (0.89, 1.1)"]


def test_the_v6_01_tecos_row_now_cites_the_registry_outcome():
    import json
    o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", "dpp4-mace-t2d.json"), encoding="utf-8"))
    x = next(t for t in o["trials"] if t["label"] == "TECOS")
    row, why = b.pipeline_row("dpp4-mace-t2d", x, "HR")
    assert why is None and "unstable angina" not in row["source"].lower()
    assert "Hazard Ratio (HR) 0.99 (0.89, 1.1)" in row["source"]
