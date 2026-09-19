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


def _independent_judge(docs):
    """Recompute the per-dimension judge margins straight from fair_judge.json, so the rendered figures
    are proven to REGENERATE from the committed judgment record, not just be typed into prose."""
    fj = json.load(open(os.path.join(docs, "fair_judge.json"), encoding="utf-8"))
    slugs = [k for k in fj if not k.startswith("_")]
    pd = lambda s, d: (fj[s].get("resolved") or {}).get("per_dimension", {}).get(d)
    out = {}
    for d in ("search_reproducibility", "per_number_source_traceability", "completeness_of_evidence",
              "risk_of_bias_reporting", "declared_absence_exclusion_transparency", "overall_auditability"):
        out[d] = (sum(pd(s, d) == "ours" for s in slugs), sum(pd(s, d) == "comparator" for s in slugs))
    return out


def test_per_dimension_fair_figures_regenerate_and_render():
    """The 27-1 / 13-14 figures must REGENERATE from fair_judge.json (a disclosure that cannot be
    reproduced is a claim): recompute each per-dimension margin independently, assert _fair_numbers agrees,
    and assert the exact margins + RoB direction render in the index."""
    dims = _independent_judge(DOCS)
    n = IDX._fair_numbers(DOCS)
    for d, (o, c) in dims.items():
        assert (n[f"judge_{d}_ours"], n[f"judge_{d}_comp"]) == (o, c), f"{d} margin diverged"
    html = IDX.build_index(DOCS)
    # every auditability-family dimension's exact ours-comparator margin is rendered
    for d in ("search_reproducibility", "per_number_source_traceability",
              "declared_absence_exclusion_transparency", "overall_auditability"):
        o, c = dims[d]
        assert f"{o}&ndash;{c}" in html, f"rendered margin for {d} ({o}-{c}) missing"
    # RoB margin + direction render, direction matching the data (to us / to the comparator / even)
    ro, rc = dims["risk_of_bias_reporting"]
    assert f"{ro}&ndash;{rc}" in html
    direction = "to us" if ro > rc else "to the comparator" if rc > ro else "even"
    assert direction in html, f"RoB direction '{direction}' not rendered"


def test_no_stale_hardcoded_fair_counts_slip_back_in():
    """The specific stale numbers that were hand-typed before the derivation existed must not reappear
    UNLESS they equal the derived value. Guards against a re-hardcode regression."""
    html = IDX.build_index(DOCS)
    n = IDX._fair_numbers(DOCS)
    # '95 of 95' was the original drift ("All 95 of 95 pooled trial-outcome numbers ... verified"); that CLAIM must never
    # reappear. The bare string may legitimately occur as a derived count elsewhere (the trial-family count chain renders
    # "Families screened 95 of 95" for sglt2-primary-prevention-hf), so the guard is on the drifted claim, not the digits.
    assert "All 95 of 95" not in html and "95 of 95 pooled" not in html
    # if the derived judge total is not 8, the old '8 of 8' phrasing must be gone
    if n["judge_total"] != 8:
        assert "8 of 8" not in html


def test_prose_number_guard_fires_on_unaccounted_numeral():
    """The build-time anti-drift guard must RAISE on a risky prose numeral that is neither object-derived
    nor whitelisted (an aggregate 'N of M', a decimal effect size, or an integer >= 10), and must PASS the
    real banners. This is the permanent version of the '95 of 95' drift, enforced fail-closed by the hook
    (which regenerates the index via build_index)."""
    import pytest
    for bad in ("<p>recovered 999 of 1234 cells</p>", "<p>now 47 topics live</p>", "<p>MD -7.77</p>"):
        with pytest.raises(ValueError):
            IDX._validate_prose_numbers(DOCS, bad)
    # the real static banners pass, and build_index (which calls the guard) succeeds
    IDX._validate_prose_numbers(DOCS, IDX._continuous_section(DOCS))
    assert IDX.build_index(DOCS)


def test_continuous_banner_numbers_are_object_derived():
    """Semaglutide's live k/MD/CI in the continuous banner must match its review.json (derived, not typed)."""
    html = IDX.build_index(DOCS)
    import json as _j, os as _o
    res = next(o["result"] for o in _j.load(open(_o.path.join(DOCS, "reviews", "semaglutide-obesity-weight",
              "review.json"), encoding="utf-8"))["outcomes"] if o.get("primary"))
    assert f"k={res['k']}, MD" in html
    assert f"{abs(round(res['estimate'],2))}%" in html
