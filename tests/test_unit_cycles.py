"""Unit of analysis: women vs cycles (metformin-PCOS review, served review_sha256 f1643a7150..., pinned at 6260e70c).
Legro (PMID 17287476) Table 2: women who ovulated 174/209 vs 157/209 AND ovulatory cycles 582/964 vs 462/942. Legro's full text is NOT
held (abstract only) and the served review screened it out, so Table 2 is a TEST FIXTURE carrying the cited values. A per-woman target
binds to 174/157 (OR 1.6466, 1.0191-2.6604); cycle counts are never independent participants; and the reverse direction holds."""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import evidence_identity as ei, held_rows, reason_audit  # noqa: E402

# TEST FIXTURE -- not a held source
TABLE2 = ("<table-wrap><label>Table 2</label><caption>Ovulation outcomes</caption><table><thead><tr><th>Outcome</th>"
          "<th>Clomiphene + metformin (N = 209)</th><th>Clomiphene + placebo (N = 209)</th></tr></thead><tbody>"
          "<tr><td>Women who ovulated — no./total no. (%)</td><td>174/209 (83.3)</td><td>157/209 (75.1)</td></tr>"
          "<tr><td>Ovulatory cycles — no./total no. of cycles (%)</td><td>582/964 (60.4)</td><td>462/942 (49.0)</td></tr>"
          "</tbody></table></table-wrap>")
SRC = [{"source_id": "fixture:legro-table2", "text": "", "raw": TABLE2}]
WOMEN, CYCLES = "Women who ovulated — no./total no. (%)", "Ovulatory cycles — no./total no. of cycles (%)"
PER_WOMAN = {"name": "Ovulation with metformin added to clomifene", "estimand": "OR", "timepoint": None, "population": None}
PER_CYCLE = {"name": "Ovulatory cycles", "estimand": "OR", "timepoint": None, "population": None}


def _cands(outcome):
    return {c["label"]: c for c in reason_audit.typed_candidates(outcome, {"id": "17287476"}, SRC, {})}


def _unit_ok(c):
    return not [m for m in c["mismatch"] if m.startswith("unit")]


def test_units_are_read_from_the_rows():
    rows = {r["label"]: r for r in ei.count_rows(TABLE2, "17287476", "fixture")}
    assert rows[WOMEN]["unit"] == "PATIENTS_WITH_EVENT" and rows[CYCLES]["unit"] == "CYCLES"
    assert ei.unit_of("582 of 964 ovulatory cycles") == "CYCLES" and ei.unit_of("174 of 209 women ovulated") == "PATIENTS_WITH_EVENT"


def test_PLANT_a_per_woman_target_binds_to_women_and_never_to_cycles():
    c = _cands(PER_WOMAN)
    assert _unit_ok(c[WOMEN]) and [(a["events"], a["n"]) for a in c[WOMEN]["arms"]] == [(174, 209), (157, 209)]
    assert "unit:CYCLES!=PARTICIPANTS" in c[CYCLES]["mismatch"]


def test_PLANT_a_per_cycle_target_binds_to_cycles_and_never_to_women():
    c = _cands(PER_CYCLE)
    assert _unit_ok(c[CYCLES]) and [(a["events"], a["n"]) for a in c[CYCLES]["arms"]] == [(582, 964), (462, 942)]
    assert "unit:PATIENTS_WITH_EVENT!=CYCLES" in c[WOMEN]["mismatch"]


def test_PLANT_cycle_counts_are_never_independent_participants():
    row = next(r for r in ei.count_rows(TABLE2, "17287476", "fixture") if r["label"] == CYCLES)
    got = held_rows.ascertained_counts(row)
    assert got["unit"] == "CYCLES"
    assert all(a["n_ascertained"] is None and a["non_events"] is None and a["n_cycles"] in (964, 942) for a in got["arms"])


def test_the_per_woman_or_reproduces():
    (a, n1), (c, n2) = (174, 209), (157, 209)
    b, d = n1 - a, n2 - c
    or_ = (a * d) / (b * c)
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    z = 1.959963984540054
    assert [round(x, 4) for x in (or_, or_ * math.exp(-z * se), or_ * math.exp(z * se))] == [1.6466, 1.0191, 2.6604]
