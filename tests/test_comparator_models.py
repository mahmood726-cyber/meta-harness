"""V1.0.1 comparator model-specific tuples and internal mismatches (harness/comparator_models.py). Fixture: Ma 2022
(PMID 36176989) Figure 3A MACE -- fixed effect 0.65 [0.56, 0.75], random effects 0.54 [0.38, 0.77]; its prose says
0.65 (0.38-0.77), the fixed point with the random interval."""
import copy
import json
import os

import pytest

from harness import comparator_models as cm, comparator_panel, gate, overlap_relation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "colchicine-secondary-cv-prevention"


@pytest.fixture(scope="module")
def fig():
    return cm.load(ROOT, SLUG)["figures"][0]


def test_transcription_reproduces_both_printed_pools(fig):
    rc = fig["_recomputed"]
    assert round(rc["fixed_MH"], 2) == 0.65 and round(rc["random_DL"], 2) == 0.54
    assert [round(x, 2) for x in rc["random_DL_ci"]] == [0.38, 0.77] and round(rc["tau2_DL"], 3) == 0.122


@pytest.mark.parametrize("mutate,why", [
    (lambda f: f["rows"][2].__setitem__("events_int", 129), "Mantel-Haenszel|DerSimonian"),
    (lambda f: f["rows"][0].__setitem__("n_int", 121), "arm totals"),
    (lambda f: f["pooled"][1].__setitem__("ci_low", 0.56), "DerSimonian"),
    (lambda f: f["document"].__setitem__("sha256", "x"), "sha256"),
])
def test_PLANT_a_mistyped_transcription_is_refused(fig, mutate, why):
    f = copy.deepcopy(fig)
    f.pop("_recomputed", None)
    mutate(f)
    with pytest.raises(cm.FigureRefused, match=why):
        cm.validate(f)


def test_PLANT_prose_mixing_models_is_detected_and_kept(fig):
    text = open(os.path.join(ROOT, "cache", SLUG, "comparator_fulltext.txt"), encoding="utf-8").read()
    mm = cm.prose_mismatches(text, fig)
    assert len(mm) == 1
    x = mm[0]
    assert x["code"] == "COMPARATOR_INTERNAL_MISMATCH" and x["kind"] == "PROSE_MIXES_MODELS"
    assert (x["prose"]["point"], x["prose"]["ci_low"], x["prose"]["ci_high"]) == (0.65, 0.38, 0.77)
    assert x["point_from"].startswith("fixed") and x["interval_from"] == "random effects"
    assert "reduced the risk of MACE by 46%" in x["prose"]["quote"]
    # a prose tuple that IS one model's row is not a mismatch (the low-dose subgroup 0.65 [0.56-0.75] elsewhere)
    assert cm.prose_mismatches("RR: 0.65; 95% CI: 0.56-0.75", fig) == []


def test_figure_rows_bind_to_the_table_and_year_differences_are_kept():
    panel = json.load(open(os.path.join(ROOT, "cache", SLUG, "comparators.json"), encoding="utf-8"))
    bound = cm.bind_rows(cm.load(ROOT, SLUG)["figures"][0], panel[0]["trial_set"])
    assert all(m for _, m, _ in bound)
    got = {r["row_label"]: m["family_id"] for r, m, _ in bound}
    assert got["Stefan M Nidorf-2020"] == "Nidorf et al 2020 [B7]" and got["Nidorf SM, et al.-2013"] == "Nidorf et al 2013 [B13]"
    yd = {n["figure_row"]: (n["figure_year"], n["table_year"]) for _, _, n in bound if n}
    assert yd == {"Mehdi Akrami-2012": ("2012", "2021"), "Mewton N-2019": ("2019", "2021")}


def test_served_page_keeps_the_mismatch_flags_our_result_unmoved_and_computes_outcome_level_overlap():
    rev = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "review.json"), encoding="utf-8"))
    comp = rev["comparator"]
    row = next(r for r in comp["reported"] if r["outcome"].startswith("Trial-defined"))
    assert (row["estimate"], row["ci_low"], row["ci_high"]) == (0.65, 0.38, 0.77)            # kept as printed
    assert row["internal_mismatch"]["code"] == "COMPARATOR_INTERNAL_MISMATCH"
    assert {(t["model"].split()[0], t["point"], t["ci_low"], t["ci_high"]) for t in comp["model_tuples"]} == {
        ("fixed", 0.65, 0.56, 0.75), ("random", 0.54, 0.38, 0.77)}
    o = comp["overlap_relation"]
    fam = {f["family_id"]: f["aliases"].get("acronym") for f in rev["trial_families"]}
    assert o["relation"] == "OVERLAPPING" and o["theirs_k"] == 7                              # the MACE panel, not 15
    assert sorted(o["shared"]) == ["ACTRN12614000093684", "NCT02551094"]                     # LoDoCo2, COLCOT
    assert o["only_ours"] == ["NCT03048825"]                                                 # CLEAR SYNERGY
    html = open(os.path.join(ROOT, "docs", "reviews", SLUG, "index.html"), encoding="utf-8").read()
    assert gate.check_comparator_internal_mismatch_kept(os.path.join(ROOT, "docs", "reviews", SLUG), html) == []


def test_PLANT_gate_refuses_a_dropped_flag_or_an_unrendered_mismatch(tmp_path):
    rev = json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "review.json"), encoding="utf-8"))
    comp = copy.deepcopy(rev["comparator"])
    for r in comp["reported"]:
        r.pop("internal_mismatch", None)
    (tmp_path / "review.json").write_text(json.dumps({"comparator": comp}), encoding="utf-8")
    assert any("without the flag" in m for m in gate.check_comparator_internal_mismatch_kept(str(tmp_path)))
    (tmp_path / "review.json").write_text(json.dumps({"comparator": rev["comparator"]}), encoding="utf-8")
    assert any("rendered" in m for m in gate.check_comparator_internal_mismatch_kept(str(tmp_path), "<html></html>"))


def test_the_protocol_erratum_is_labelled_retrospective_and_the_registered_sentence_is_unchanged():
    text = open(os.path.join(ROOT, "protocols", f"{SLUG}.md"), encoding="utf-8").read()
    assert "It reports colchicine reduced MACE (RR 0.65, 95% CI 0.38-0.77) in coronary" in text   # as registered
    err = text[text.index("## Retrospective protocol erratum (2026-09-27)"):]
    assert "Labelled retrospective" in err and "FE 0.65 (0.56-0.75); RE 0.54 (0.38-0.77)" in err
