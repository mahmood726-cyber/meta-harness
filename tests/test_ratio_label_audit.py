"""A printed ratio may outrank the same source's arm counts only if it AGREES with them (V1.0.1 acquisition cascade).

CORP-2 (PMID 24694983, colchicine-recurrent-pericarditis): the abstract says "26 (21.6%) of 120 in the colchicine group
and 51 (42.5%) of 120 in the placebo group (relative risk 0.49; 95% CI 0.24-0.65)". The counts give RR 0.51 (95% CI
0.34-0.76); 1 - (0.51, 0.76, 0.34) = (0.49, 0.24, 0.66): the printed '0.49 (0.24-0.65)' is the RELATIVE RISK REDUCTION
under the label 'relative risk'. The source hierarchy selected it over the counts (PUBLISHED_EFFECT_TARGET_CLASS) and
the page pooled RR 0.49. Written BEFORE the fix.
"""
import json
import os

from harness import design_key, fetch, pipeline

SLUG = "colchicine-recurrent-pericarditis"
CORP2 = "PMID 24694983"


def test_the_audit_names_corp2s_printed_ratio_a_mislabelled_rrr():
    a = design_key.ratio_label_audit(26, 120, 51, 120, 0.49, 0.24, 0.65)
    assert a["verdict"] == "MISLABELLED_RRR", a
    assert round(a["counts_rr"], 2) == 0.51


def test_the_audit_accepts_a_ratio_that_matches_its_counts():
    a = design_key.ratio_label_audit(26, 120, 51, 120, 0.51, 0.34, 0.76)
    assert a["verdict"] == "CONSISTENT", a


def test_the_audit_does_not_guess_when_neither_reading_fits():
    a = design_key.ratio_label_audit(26, 120, 51, 120, 0.20, 0.10, 0.40)
    assert a["verdict"] == "INCONSISTENT", a


def test_corp2_is_pooled_from_its_counts_not_the_mislabelled_ratio():
    config = json.load(open(os.path.join(pipeline.ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
    records = fetch.ensure(config, "")
    inp = pipeline.outcome_inputs(SLUG, config, records)
    spec = next(s for s, k in pipeline._outcome_specs(config) if s.get("primary"))
    out = pipeline.build_outcome_from_inputs(inp, spec, "efficacy", SLUG)
    row = next(t for t in out["trials"] if t["id"] == CORP2)
    assert (row.get("ai"), row.get("n1i"), row.get("ci"), row.get("n2i")) == (26, 120, 51, 120), row
    assert row.get("effect") != 0.49
    assert row["selection_rule"] == "KEEP_COUNTS_PUBLISHED_RATIO_MISLABELLED_RRR"
    assert any(alt.get("ratio_label_audit", {}).get("verdict") == "MISLABELLED_RRR" for alt in row.get("alternatives") or [])
