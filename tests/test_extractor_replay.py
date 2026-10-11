"""DISPATCH_V14_EXTRACTOR_ROUTE: a value read by a typed extractor over HELD text is EXTRACTOR only when its replay limb
re-derives it identically from the pinned bytes; a script-typed `*_verified` row stays HAND_ENTERED."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import extractor_replay as xr  # noqa: E402
from harness import provenance_class as pc  # noqa: E402

LABEL_SHA = "26c58886d7802376ecc2c3235a2e1acc0bae3dc775bf8744f4df116b23ee0c9d"
LABEL_SPEC = {"table": "Table 3", "trial": "FIDELIO-DKD", "arm_t": "Kerendia", "arm_c": "Placebo",
              "row_label": "Hyperkalemia"}
OMA_SHA = "6ade2476f3f931f8ef952c2afc46f2b11b3292361e933428cbb54784b6420c9b"
OMA_CLAUSE = ("The hHF outcome occurred in 20/2092 patients in the omarigliptin group (0.96%; 0.51/100 patient-years) and "
              "33/2100 patients in the placebo group (1.57%; 0.85/100 patient-years), with an HR of 0.60 (95% CI 0.35, 1.05)")
LINA_SHA = "94e500fb2025e3a5d004490722412507eb1aca81e62c61475b8cee6b17548705"
LINA_CLAUSE = ("Linagliptin versus placebo did not affect the incidence of hHF (209/3494 [6.0%] versus 226/3485 [6.5%], "
               "respectively; hazard ratio [HR], 0.90; 95% CI, 0.74-1.08)")


def _label_row(**kw):
    text = open(os.path.join(ROOT, "outputs", "held_labels", "fda_215341s000lbl.txt"), encoding="utf-8", newline="").read()
    v = xr.read_label_adr_table(text, LABEL_SPEC)
    row = {"id": "PMID 33264825", "provenance": "label_adr_table", "ai": v["ai"], "n1i": v["n1i"], "ci": v["ci"],
           "n2i": v["n2i"], "document_ref": "outputs/held_labels/fda_215341s000lbl.txt", "document_sha256": LABEL_SHA,
           "source_span": v["raw_row"], "source": "label Table 3", "replay": dict(LABEL_SPEC)}
    row.update(kw)
    return row


def _abs_row(pmid, sha, clause, effect, lo, hi, **kw):
    row = {"id": f"PMID {pmid}", "provenance": "held_abstract_clause", "effect": effect, "ci_low": lo, "ci_high": hi,
           "document_ref": f"outputs/held_abstracts/pubmed_{pmid}.txt", "document_sha256": sha, "source_span": clause,
           "source": f"PMID {pmid} abstract"}
    row.update(kw)
    return row


def _held(_):
    return True


def test_the_label_reader_reads_fidelio_hyperkalaemia_by_type():
    r = _label_row()
    assert (r["ai"], r["n1i"], r["ci"], r["n2i"]) == (516, 2827, 255, 2831)


def test_PLANT_a_replayed_label_row_is_extractor():
    assert pc.classify_served(_label_row(), _held)[0] == "EXTRACTOR"


@pytest.mark.parametrize("change", [{"ai": 517}, {"n2i": 2830}, {"document_sha256": "0" * 64},
                                    {"replay": dict(LABEL_SPEC, row_label="Hypokalemia")}, {"replay": {}},
                                    {"document_ref": "cache/finerenone-ckd-t2d-renal/records.json"},
                                    {"document_ref": "outputs/held_labels/../held_abstracts/pubmed_28893244.txt"},
                                    {"source_span": "Hyperkalemia 516 (18.3) 255 (9.0) X"}])
def test_PLANT_a_label_row_that_does_not_replay_identically_is_untraced(change):
    cls, why = pc.classify_served(_label_row(**change), _held)
    assert cls == "UNTRACED", why


@pytest.mark.parametrize("pmid,sha,clause,eff", [("28893244", OMA_SHA, OMA_CLAUSE, (0.60, 0.35, 1.05)),
                                                 ("30586723", LINA_SHA, LINA_CLAUSE, (0.90, 0.74, 1.08))])
def test_PLANT_a_replayed_held_abstract_clause_is_extractor(pmid, sha, clause, eff):
    assert pc.classify_served(_abs_row(pmid, sha, clause, *eff), _held)[0] == "EXTRACTOR"
    # one number moved, or the clause not in the held bytes, or another document: never extractor
    assert pc.classify_served(_abs_row(pmid, sha, clause, eff[0] + 0.01, *eff[1:]), _held)[0] == "UNTRACED"
    assert pc.classify_served(_abs_row(pmid, sha, clause + " x", *eff), _held)[0] == "UNTRACED"
    assert pc.classify_served(_abs_row(pmid, "f" * 64, clause, *eff), _held)[0] == "UNTRACED"


@pytest.mark.parametrize("clause", ["no hazard ratio here, 20/2092 events",                       # no HR
                                    "20/2092 v 33/2100; HR of 0.60 (95% CI 0.65, 1.05)",           # HR outside its CI
                                    "20/2092 v 33/2100; HR of 0.60 (95% CI 0.35, 1.05); HR of 0.70 (95% CI 0.5, 0.9)"])
def test_PLANT_the_clause_reader_refuses_rather_than_guesses(clause):
    with pytest.raises(xr.ReadRefused):
        xr.read_abstract_clause(clause)


def test_a_script_typed_verified_row_stays_hand_entered():
    """The class follows the replay, never the provenance string: '*_verified' is HAND_ENTERED as before."""
    assert pc.classify_served({"provenance": "abstract_verified", "source": "x", "effect": 0.6}, _held)[0] == \
        "HAND_ENTERED"


def _harm_outcome():
    return {"name": "Hyperkalemia (FDA label adverse reaction, FIDELIO-DKD safety population)", "kind": "harm",
            "trials": [{"id": "PMID 33264825", "label": "FIDELIO-DKD", "ai": 516, "n1i": 2827, "ci": 255, "n2i": 2831,
                        "source_span": "Hyperkalemia 516 (18.3) 255 (9.0)"}],
            "declared_absent_trials": [], "result": {"present": True}}


def test_PLANT_a_source_scoped_harm_is_not_incomplete_because_another_trial_uses_its_keyword():
    """V14-03: FIGARO's abstract reports LAB hyperkalaemia; the label endpoint is scoped to the label table, which covers
    FIDELIO only -- FIGARO is 'not in this source', never 'known reported, unresolved' (publication gate L1)."""
    from harness import harms
    spec = {"keywords": ["hyperkalemia", "hyperkalaemia"],
            "source_scope": {"document_ref": "outputs/held_labels/fda_215341s000lbl.txt", "trials": ["33264825"]}}
    included = [{"id": "33264825"}, {"id": "34449181"}]
    recs = {"34449181": {"abstract": "Hyperkalemia led to discontinuation in 1.2% of finerenone patients."}}
    out = harms.annotate_outcome(_harm_outcome(), spec, included, recs)
    assert not out["result"].get("harms_incomplete") and not out["result"].get("harms_synthesis_suppressed")
    # the same keyword WITHOUT a scope still makes it incomplete (the gate is unchanged for every other outcome)
    out = harms.annotate_outcome(_harm_outcome(), {"keywords": spec["keywords"]}, included, recs)
    assert out["result"].get("harms_incomplete")


def test_PLANT_a_malformed_source_scope_fails_loudly():
    from harness import harms
    with pytest.raises(ValueError):
        harms.annotate_outcome(_harm_outcome(), {"keywords": ["x"], "source_scope": {"trials": ["1"]}},
                               [{"id": "33264825"}, {"id": "2"}], {"2": {"abstract": "x"}})


# ---- codex extr-r1 (PR #84): plants that fail on b405fde84 ----------------------------------------------------------
def test_PLANT_extr_r1_1_replay_checks_every_served_count(tmp_path):
    clause = "Deaths: 5/100 versus 10/100; hazard ratio, 0.50; 95% CI, 0.30-0.80."
    import hashlib
    import json
    sha = hashlib.sha256(clause.encode("utf-8")).hexdigest()
    (tmp_path / "outputs" / "held_abstracts").mkdir(parents=True)
    (tmp_path / "outputs" / "held_abstracts" / "pubmed_1.txt").write_text(clause, encoding="utf-8", newline="")
    (tmp_path / "outputs" / "held_abstracts" / "manifest.json").write_text(json.dumps(
        {"documents": {"pubmed_1.txt": {"sha256": sha}}}), encoding="utf-8")
    row = _abs_row("1", sha, clause, 0.5, 0.3, 0.8)
    assert xr.replay(row, root=str(tmp_path))[0] is True
    # a clause row never serves counts -- right or wrong, a count on it is refused (extr-r2: counts not read)
    assert xr.replay(dict(row, ai=99, n1i=200), root=str(tmp_path))[0] is False
    assert xr.replay(dict(row, ai=5, n1i=100, ci=10, n2i=100), root=str(tmp_path))[0] is False


@pytest.mark.parametrize("clause", [
    "Mortality rates were 5/100 person-years versus 10/100 person-years; hazard ratio, 0.50; 95% CI, 0.30-0.80.",
    "Deaths: 5/100 randomized participants in the treatment arm versus 10/90 safety participants in the placebo arm; "
    "hazard ratio, 0.50; 95% CI, 0.30-0.80.",
])
def test_PLANT_extr_r1_2_3_rates_and_mixed_denominators_are_never_read_as_counts(clause):
    """extr-r2 design change: the clause reader reads the HR and its CI only -- a count is never read, so neither a
    rate nor a mixed denominator can become one."""
    assert set(xr.read_abstract_clause(clause)) == {"effect", "ci_low", "ci_high"}


def test_PLANT_extr_r1_4_the_header_never_crosses_into_the_next_table():
    text = ("Table 3: Adverse reactions in FIDELIO-DKD\nNo adverse reactions were tabulated.\nTable 4: Adverse reactions in "
            "FIGARO-DKD\nKerendia N = 100 n (%) Placebo N = 100 n (%)\nHyperkalemia 20 (20.0) 10 (10.0)\n")
    with pytest.raises(xr.ReadRefused):
        xr.read_label_adr_table(text, LABEL_SPEC)


def test_PLANT_extr_r1_5_the_row_label_starts_a_line():
    text = ("Table 3: Adverse reactions in FIDELIO-DKD\nKerendia N = 100 n (%) Placebo N = 100 n (%)\n"
            "Severe Hyperkalemia 2 (2) 1 (1)\nHyperkalemia 20 (20) 10 (10)\n")
    v = xr.read_label_adr_table(text, LABEL_SPEC)
    assert (v["ai"], v["ci"]) == (20, 10)


@pytest.mark.parametrize("clause", ["Deaths: 1/1,000 versus 2/2,000; HR of 0.50; 95% CI, 0.10-2.00.",
                                    "Among randomized participants, deaths were 5/100; among safety participants, deaths "
                                    "were 4/80; HR of 1.00; 95% CI, 0.50-2.00.",
                                    "Kaplan-Meier estimated mortality was 5/100 versus 10/100; HR of 0.50; 95% CI, 0.20-0.90."])
def test_PLANT_extr_r2_1_2_3_no_count_is_ever_read_from_a_clause(clause):
    assert set(xr.read_abstract_clause(clause)) == {"effect", "ci_low", "ci_high"}


def test_PLANT_extr_r2_4_the_trial_is_named_inside_its_own_caption():
    text = ("Table 3: Adverse reactions in OTHER-TRIAL\nTable 4: Adverse reactions in FIDELIO-DKD\nKerendia N = 100 n (%) "
            "Placebo N = 100 n (%)\nHyperkalemia 10 (10) 5 (5)")
    with pytest.raises(xr.ReadRefused):
        xr.read_label_adr_table(text, LABEL_SPEC)


# ---- codex extr-r3 (PR #84): plants that fail on 0e4a0ba93 ----------------------------------------------------------
def test_PLANT_extr_r3_1_a_number_ends_where_it_ends():
    with pytest.raises(xr.ReadRefused):
        xr.read_abstract_clause("hazard ratio, 0.90; 95% CI, 0.50-1.20e1")


def test_PLANT_extr_r3_2_several_arm_headers_in_one_table_are_refused():
    text = ("Table 3: Adverse reactions in FIDELIO-DKD\nRandomised population\nKerendia N = 100 n (%) Placebo N = 100 n (%)\n"
            "Safety population\nKerendia N = 80 n (%) Placebo N = 90 n (%)\nHyperkalemia 1 (1) 1 (1)\n")
    with pytest.raises(xr.ReadRefused):
        xr.read_label_adr_table(text, LABEL_SPEC)


def test_PLANT_extr_r3_3_a_label_row_serving_an_effect_is_untraced():
    cls, _ = pc.classify_served(_label_row(effect=2.03, ci_low=1.76, ci_high=2.33, scale="HR"), _held)
    assert cls == "UNTRACED"


def test_PLANT_extr_r3_4_a_zero_denominator_is_a_refusal():
    text = "Table 3: Adverse reactions in FIDELIO-DKD\nKerendia N = 0 n (%) Placebo N = 100 n (%)\nHyperkalemia 0 (0) 1 (1)\n"
    with pytest.raises(xr.ReadRefused):
        xr.read_label_adr_table(text, LABEL_SPEC)


def test_the_bracketed_hr_form_is_read():
    assert xr.read_abstract_clause("semaglutide reduced rates of the composite compared with placebo "
                                   "[HR 0.82 (95% CI 0.68\u20130.98)]") == {"effect": 0.82, "ci_low": 0.68, "ci_high": 0.98}
