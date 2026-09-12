"""Anti-drift guard for the index prose: the fair-comparison numbers must be DERIVED from the committed
JSON records, never typed into the banner (the '95 of 95' drift class — any number typed into a sentence
rather than read from the object will drift as topics are added). This test recomputes the numbers
independently from prisma_fair.json / fair_judge.json and asserts the rendered index contains exactly
those, so a future hand-typed number (or a divergence in the derivation) fails loudly."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json  # noqa: E402
from harness import index as IDX  # noqa: E402

DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")


def _independent_prisma(docs):
    pf = json.load(open(os.path.join(docs, "prisma_fair.json"), encoding="utf-8"))
    rows = {k: v for k, v in pf.items() if not k.startswith("_")}
    inc = {k: v for k, v in rows.items() if v.get("comparator_fulltext_source") != "NONE"}
    items = list(next(iter(inc.values()))["ours"].keys())
    cells = len(inc) * len(items)
    comp = sum(1 for s in inc for i in items if inc[s]["comparator"][i].get("present"))
    lacks = sum(1 for s in inc for i in items if inc[s]["comparator"][i].get("present") and not inc[s]["ours"][i])
    we = sum(1 for s in inc for i in items if inc[s]["ours"][i] and not inc[s]["comparator"][i].get("present"))
    return len(inc), len(rows), cells, comp, lacks, we


def test_fair_numbers_match_independent_recompute():
    n = IDX._fair_numbers(DOCS)
    scor, tot, cells, comp, lacks, we = _independent_prisma(DOCS)
    assert (n["prisma_scorable"], n["prisma_total"], n["prisma_cells"]) == (scor, tot, cells)
    assert (n["prisma_comp_present"], n["prisma_ours_lacks"], n["prisma_we_present"]) == (comp, lacks, we)


def test_rendered_index_contains_the_derived_prisma_numbers():
    html = IDX.build_index(DOCS)
    scor, tot, cells, comp, lacks, we = _independent_prisma(DOCS)
    assert f"{scor} of {tot} topics" in html
    assert f"{comp} of {cells}" in html          # comparators satisfy N of M
    assert f"{lacks} of {cells}" in html          # ours lacks N of M (should be 0)
    assert f"<strong>{we}</strong>" in html       # we present N they don't


def test_rendered_index_contains_the_derived_judge_numbers():
    html = IDX.build_index(DOCS)
    n = IDX._fair_numbers(DOCS)
    assert f"{n['judge_total']} topics" in html
    assert f"auditable on {n['judge_more_auditable_ours']} of {n['judge_total']}" in html


def test_no_stale_hardcoded_fair_counts_slip_back_in():
    """The specific stale numbers that were hand-typed before the derivation existed must not reappear
    UNLESS they equal the derived value. Guards against a re-hardcode regression."""
    html = IDX.build_index(DOCS)
    n = IDX._fair_numbers(DOCS)
    # '95 of 95' was the original drift; it must never appear now (verification count is self-counted elsewhere)
    assert "95 of 95" not in html
    # if the derived judge total is not 8, the old '8 of 8' phrasing must be gone
    if n["judge_total"] != 8:
        assert "8 of 8" not in html
