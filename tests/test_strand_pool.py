"""External review 11 (iv-iron strands): every served strand goes through ONE analysis / provenance / gate path.

  11-01  strand member numbers are in the extraction inventory; strands are in the Analysis tab
  11-02  at k=2 a strand pool does not serve the single-df HKSJ interval (harness/k2.py), whichever doc it came from
  11-03  CONFIRM-HF participants with >=1 HF hospitalisation are 10/150 v 25/151 from the held FAS table -- the 7.6 and
         19.4 are incidence per 100 patient-years, so 'crude RR 0.39' was a rate ratio on invented denominators
Fixed strings are copied from the held sources (cache/iv-iron-hfref-hosp)."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import claimgraph, page, review_tabs, strand_pool as sp  # noqa: E402

TABLE = ("<table-wrap id='tbl2'><caption><p>Hospitalizations and deaths (full-analysis set)</p></caption><table><thead>"
         "<tr><td rowspan=\"2\">End-point or event</td><td colspan=\"2\">FCM (<italic>n</italic> = 150)</td>"
         "<td colspan=\"2\">Placebo (<italic>n</italic> = 151)</td></tr><tr><td>Total number of events</td>"
         "<td>Incidence/100 patient-years at risk</td><td>Total number of events</td><td>Incidence/100 patient-years "
         "at risk</td><td>Time to first event hazard ratio 95% CI</td><td>P-value</td></tr></thead><tbody><tr><td>Death</td><td>12</td><td>12 (8.9)</td><td>14</td><td>14 (9.9)</td>"
         "</tr><tr><td> Hospitalizations due to worsening HF</td><td>10</td><td>10 (7.6)</td><td>32</td>"
         "<td>25 (19.4)</td><td>0.39 (0.19–0.82)</td><td>0.009</td></tr></tbody></table></table-wrap>")


def test_PLANT_11_03_confirm_counts_are_read_from_the_fas_table_never_inferred():
    c = sp.table_arm_counts(TABLE_FOOT, **CONFIRM_LAYOUT)
    assert (c["ai"], c["n1i"], c["ci"], c["n2i"]) == (10, 150, 25, 151)
    rr = sp.counts_rr(10, 150, 25, 151)
    assert (rr["effect"], rr["ci_low"], rr["ci_high"]) == (0.4027, 0.2004, 0.809)
    # no arm size in the header -> refused, never ~132/~129
    assert sp.table_arm_counts(TABLE_FOOT.replace("(<italic>n</italic> = 150)", ""), **CONFIRM_LAYOUT) is None


def test_PLANT_11_02_a_k2_strand_never_serves_an_interval():
    m = [{"trial": "AFFIRM-AHF", "effect": 0.74, "ci_low": 0.58, "ci_high": 0.94},
         {"trial": "FAIR-HF2", "effect": 0.80, "ci_low": 0.60, "ci_high": 1.06}]
    p = sp.pool_strand(m, "RR")
    assert p["k"] == 2 and p["ci_low"] is None and p["ci_high"] is None
    assert p["pooled_ci_refused"]["code"] == "K2_SINGLE_DF"
    assert (p["ci_hksj_unserved"]["ci_low"], p["ci_hksj_unserved"]["ci_high"]) == (0.2318, 2.5218)   # reproduces r11
    assert sp.k2_violation(p) is None


def test_PLANT_11_02_a_hand_written_k2_doc_is_withheld_at_attach_and_flagged_by_the_gate():
    hand = {"k": 2, "estimate": 0.784, "ci_low": 0.474, "ci_high": 1.298, "scale": "HR"}     # pcsk9-shaped doc
    assert sp.k2_violation(hand) == "K2_SINGLE_DF_CI_SERVED"
    assert sp.served_view(hand)["ci_low"] is None and sp.served_view(hand)["withheld"]
    fixed = sp.policy_pool(dict(hand))
    assert fixed["ci_low"] is None and fixed["ci_hksj_unserved"]["ci_low"] == 0.474 and sp.k2_violation(fixed) is None
    review = {"slug": "x", "outcomes": [{"primary": True, "name": "P", "trials": []}],
              "strands": {"strands": [{"strand": "B", "name": "b", "k": 2, "pool": hand}]}}
    assert any(v["code"] == "STRAND_K2_CI_SERVED" for v in claimgraph._strand_violations(review))


def test_PLANT_11_02_the_shared_renderer_shows_no_k2_interval():
    d = {"strands": [{"strand": "B", "name": "b", "event_process": "RATE", "k": 2,
                      "pool": {"k": 2, "estimate": 0.784, "ci_low": 0.474, "ci_high": 1.298, "tau2": 0.0}}]}
    html = page.render_strands_section(d)
    assert "0.474" not in html and "95% CI not served" in html and "0.784" in html


def test_member_numbers_are_read_from_the_quote_in_held_text_and_refused_otherwise():
    held = "events (rate ratio [RR] 0·79, 95% CI 0·62-1·01, p=0·059). More text."
    got = sp.read_member(held, "(rate ratio [RR] 0·79, 95% CI 0·62-1·01")
    assert (got["effect"], got["ci_low"], got["ci_high"], got["ci_level"]) == (0.79, 0.62, 1.01, 95.0)
    assert sp.read_member(held, "(rate ratio [RR] 0.70, 95% CI 0.62-1.01") is None        # not in the held text
    assert sp.read_member("(RR 0.74; 95% CI 0.58-0.94e1)", "(RR 0.74; 95% CI 0.58-0.94e1)") is None   # whole bound


def test_PLANT_11_01_strand_members_are_in_the_extraction_inventory_and_analysis_tab():
    r = {"slug": "iv-iron-hfref-hosp", "outcomes": [],
         "strands": {"strands": [{"strand": "D", "name": "Participant-level risk", "k": 1, "effect_measure": "RR",
                                  "pool": None,
                                  "members": [{"trial": "CONFIRM-HF", "pmid": "25176939", "scale": "RR", "effect": 0.4027,
                                               "ci_low": 0.2004, "ci_high": 0.809, "ai": 10, "n1i": 150, "ci": 25,
                                               "n2i": 151, "source": "held full text x",
                                               "source_span": "Hospitalizations and deaths (full-analysis set) | FCM ( n = 150) Placebo ( n = 151) | Hospitalizations due to worsening HF | 10 | 10 (7.6) | 32 | 25 (19.4)"}]}]}}
    rows = review_tabs.strand_extraction_rows(r)
    assert len(rows) == 1 and rows[0]["class"] == "EXTRACTOR" and "10/150 v 25/151" in rows[0]["value"]
    assert rows[0]["passage_sha256"]
    assert "strand-analyses" in review_tabs.analysis_tab(r)


def test_the_builder_reads_every_number_from_held_text():
    out = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "build_iv_iron_strands.py"), "--out",
                          os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "iv_iron_strands.staged.json")],
                         capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    assert out.returncode == 0, out.stderr
    doc = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "iv_iron_strands.staged.json"),
                         encoding="utf-8"))
    by = {s["strand"]: s for s in doc["strands"]}
    assert by["B"]["pool"]["ci_low"] is None and by["C"]["pool"]["ci_low"] is None
    d = by["D"]["members"][0]
    assert (d["ai"], d["n1i"], d["ci"], d["n2i"], d["effect"]) == (10, 150, 25, 151, 0.4027)
    assert "crude_rr" not in d
    # the builder types no trial number: no numeric literal under an effect/count key anywhere in its source
    import ast
    tree = ast.parse(open(os.path.join(ROOT, "scripts", "build_iv_iron_strands.py"), encoding="utf-8").read())
    keys = {"effect", "ci_low", "ci_high", "ai", "n1i", "ci", "n2i", "crude_rr"}
    typed = [k.value for n in ast.walk(tree) if isinstance(n, ast.Dict) for k, v in zip(n.keys, n.values)
             if isinstance(k, ast.Constant) and k.value in keys and isinstance(v, ast.Constant)
             and isinstance(v.value, (int, float))]
    assert typed == []


def test_a_confidence_interval_ci_tag_is_read():
    q = "hazard ratio, 0.75; 95% confidence interval [CI], 0.65 to 0.86"
    got = sp.read_member("(" + q + "; P<0.001)", q)
    assert (got["effect"], got["ci_low"], got["ci_high"]) == (0.75, 0.65, 0.86)


def _rebind():
    import importlib.util
    spec = importlib.util.spec_from_file_location("rb", os.path.join(ROOT, "scripts", "rebind_strand_doc.py"))
    rb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rb)
    return rb


def test_hand_written_strand_docs_are_rebound_from_held_text():
    rb = _rebind()
    p = rb.rebind("docs/pcsk9_mace_strands.json")["strands"][0]
    assert [sp.member_class(m)[0] for m in p["members"]] == ["EXTRACTOR", "EXTRACTOR"]
    assert p["pool"]["ci_low"] is None and p["pool"]["pooled_ci_refused"]["code"] == "K2_SINGLE_DF"
    s = rb.rebind("docs/sglt2_ckd_strands.json")["strands"][0]
    assert [sp.member_class(m)[0] for m in s["members"]] == ["EXTRACTOR"] * 3
    # k=3: the served interval is unchanged by the rebind; only its provenance changes
    assert (s["pool"]["estimate"], s["pool"]["ci_low"], s["pool"]["ci_high"]) == (0.6511, 0.4818, 0.8798)


# ---------------------------------------------------------------- codex strands-r1 (each fails before its fix)
BASIS = "computed using the number of subjects with the end-point/event"
TABLE_FOOT = TABLE.replace("</table></table-wrap>", f"</table><table-wrap-foot><p>Incidence {BASIS}.</p>"
                                                    "</table-wrap-foot></table-wrap>")
CONFIRM_LAYOUT = {"caption": "full-analysis set", "row": "Hospitalizations due to worsening HF", "arm_cells": (2, 4),
                  "count_basis": BASIS}


def test_PLANT_strands_r1_1_a_quote_that_cuts_a_held_number_is_refused():
    held = "events (RR 0.74; 95% CI 0.58-0.945, p=0.01)"
    assert sp.read_member(held, "(RR 0.74; 95% CI 0.58-0.94") is None


def test_PLANT_strands_r1_2_a_leading_dot_decimal_is_not_read_as_an_integer():
    q = "was .56 (95% CI, 0.45 to 0.68"
    assert sp.read_member(q + ")", q) is None


def test_PLANT_strands_r1_3_cell_shape_alone_is_not_a_count():
    # the same table without the footnote stating what the bracketed number is
    assert sp.table_arm_counts(TABLE, **CONFIRM_LAYOUT) is None
    assert sp.table_arm_counts(TABLE_FOOT, **CONFIRM_LAYOUT)["ai"] == 10


def test_PLANT_strands_r1_4_arm_cells_are_read_by_position_never_by_shape():
    gap = TABLE_FOOT.replace("<td>10 (7.6)</td>", "<td>NR</td>")
    assert sp.table_arm_counts(gap, **CONFIRM_LAYOUT) is None


def test_PLANT_strands_r1_5_mixed_population_denominators_are_refused():
    mixed = TABLE_FOOT.replace("FCM (<italic>n</italic> = 150)", "FCM randomised (<italic>n</italic> = 150)")
    assert sp.table_arm_counts(mixed, **CONFIRM_LAYOUT) is None


def test_PLANT_strands_r1_6_one_paper_two_endpoints_needs_a_strand_specific_quote(tmp_path, monkeypatch):
    rb = _rebind()
    spec = {"docs/t.json": {"slug": "t", "members": {"1": {"text": "abstract", "quote": "HR 0.80; 95% CI 0.70-0.90"}}}}
    doc = {"strands": [{"strand": "m", "effect_measure": "HR", "members": [{"trial": "X", "pmid": "1"}]},
                       {"strand": "h", "effect_measure": "HR", "members": [{"trial": "X", "pmid": "1"}]}]}
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "t.json").write_text(json.dumps(doc), encoding="utf-8")
    (tmp_path / "cache" / "t").mkdir(parents=True)
    (tmp_path / "cache" / "t" / "records.json").write_text(json.dumps(
        {"records": [{"id": "1", "abstract": "mortality (HR 0.60; 95% CI 0.50-0.70) and hosp (HR 0.80; 95% CI 0.70-0.90)."}]}),
        encoding="utf-8")
    q = tmp_path / "q.json"
    q.write_text(json.dumps(spec), encoding="utf-8")
    monkeypatch.setattr(rb, "QUOTES", str(q))
    import pytest as _p
    with _p.raises(SystemExit):
        rb.rebind("docs/t.json", root=str(tmp_path))


def test_PLANT_strands_r1_7_a_member_whose_numbers_contradict_its_span_is_not_extractor():
    bad = {"effect": 99.0, "ci_low": 98.0, "ci_high": 100.0, "source": "held fabricated",
           "source_span": "(RR 0.74; 95% CI 0.58-0.94"}
    assert sp.member_class(bad)[0] != "EXTRACTOR"
    good = dict(bad, effect=0.74, ci_low=0.58, ci_high=0.94)
    assert sp.member_class(good)[0] == "EXTRACTOR"


def test_PLANT_strands_r1_8_a_k2_pool_without_an_interval_is_still_marked_withheld():
    v = sp.served_view({"k": 2, "estimate": 0.8})
    assert v["withheld"] and v["crosses_null"] is None
    assert "significant" not in page.render_strands_section(
        {"strands": [{"strand": "B", "name": "b", "k": 2, "pool": {"k": 2, "estimate": 0.8}}]})


# ---------------------------------------------------------------- codex strands-r2 (each fails before its fix)
def _t(head, row, foot=BASIS):
    return (f"<table-wrap><caption>Deaths (full-analysis set)</caption><table><thead><tr>{head}</tr></thead><tbody><tr>"
            f"{row}</tr></tbody></table><table-wrap-foot><p>{foot}</p></table-wrap-foot></table-wrap>")


DEATHS = {"caption": "full-analysis set", "row": "Deaths", "count_basis": BASIS}


def test_PLANT_strands_r2_1_scientific_notation_is_never_read_as_its_exponent():
    s = "HR 1e-2 (95% CI 0.005-0.02)"
    assert sp.read_member(s, s) is None


def test_PLANT_strands_r2_2_a_percentage_column_is_not_a_count_column():
    t = _t("<th>Outcome</th><th>FCM (n = 200), % (SE)</th><th>Placebo (n = 400), % (SE)</th>",
           "<td>Deaths</td><td>10 (2.0)</td><td>20 (3.0)</td>")
    assert sp.table_arm_counts(t, arm_cells=(1, 2), **DEATHS) is None


def test_PLANT_strands_r2_3_each_count_takes_its_own_columns_denominator():
    t = _t("<th>Outcome</th><th>A (n = 100)</th><th>B (n = 200)</th>", "<td>Deaths</td><td>10 (10.0)</td><td>20 (10.0)</td>")
    c = sp.table_arm_counts(t, arm_cells=(2, 1), **DEATHS)
    assert (c["ai"], c["n1i"], c["ci"], c["n2i"]) == (20, 200, 10, 100)


def test_PLANT_strands_r2_4_span_checks_use_whole_numbers():
    m = dict(ai=1, n1i=10, ci=2, n2i=20, source="held full text",
             source_span="A (n = 100) | B (n = 200) | Deaths | 11 (11.0) | 12 (6.0)", **sp.counts_rr(1, 10, 2, 20))
    m.pop("scale", None)
    assert sp.member_class(m)[0] == "HAND_ENTERED"


def test_PLANT_strands_r2_5_a_refused_member_renders_as_refused_not_as_a_single_trial():
    html = page.render_strands_section({"strands": [{"strand": "D", "name": "Participant-level risk", "k": 0,
                                                      "event_process": "PARTICIPANT_RISK", "pool": None,
                                                      "members": [{"trial": "CONFIRM-HF",
                                                                   "status": "REFUSED_DENOMINATORS_NOT_STATED",
                                                                   "reason": "no FAS table held"}]}]})
    assert "REFUSED_DENOMINATORS_NOT_STATED" in html and "no FAS table held" in html and "single trial" not in html
