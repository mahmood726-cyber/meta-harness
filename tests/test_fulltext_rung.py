"""Full-text rung of the source ladder (harness/fulltext.extraction_segments + pipeline._fulltext_extract +
source_hierarchy full-text candidates). Found by the acq/k-gap full-text counterfactual (2026-09-29): given PMC OA
text for 34 declared-absent trials, the rung admitted 7, of which 3 were WRONG -- two baseline-characteristics
tables read as outcomes, one PPI-subgroup effect taken as the trial result. Each plant below reproduces one of them
and must fail on the pre-fix code (the fixture tests check the pre-fix path still shows the defect)."""


_TM = "=== TABLES (structured; cell boundaries = ' | ') ==="
_KW = ["antibiotic-associated diarrhoea", "antibiotic-associated diarrhea", "AAD", "diarrhoea", "diarrhea"]


def _ft_extract(text, estimand="RR"):
    from harness import pipeline
    spec = {"keywords": _KW, "estimand": estimand, "name": "Antibiotic-associated diarrhoea"}
    return pipeline._fulltext_extract(text, spec, ["probiotic"], ["placebo"], False)


def _fixture(name):
    import os
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "k_gap", name)
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def _topic_fulltext(slug, text):
    import json
    import os
    from harness import extract, pipeline
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cfg = json.load(open(os.path.join(root, "topics", slug + ".json"), encoding="utf-8"))
    spec = cfg["primary_outcome"]
    dc = extract.declared_is_composite(spec.get("name", ""))
    old = extract.extract_trial(text, spec["keywords"], cfg.get("intervention_terms"), cfg.get("comparator_terms"),
                                declared_composite=dc, estimand=spec.get("estimand"))
    new = pipeline._fulltext_extract(text, spec, cfg.get("intervention_terms"), cfg.get("comparator_terms"), dc)
    return old, new


def test_real_baseline_table_is_not_read_as_outcome_counts():
    # PLANT, real excerpt (PMID 32295417, PMC OA): the rendered TABLES section read as ONE sentence gave
    # 202/206 vs 193/194 'events' from a baseline table. `old` is the pre-fix rung (whole text to the abstract
    # extractor) and must still show the defect -- if it stops doing so, this fixture no longer tests anything.
    old, new = _topic_fulltext("colchicine-secondary-cv-prevention", _fixture("ft_32295417_baseline_excerpt.txt"))
    assert (old.get("ai"), old.get("n1i"), old.get("ci"), old.get("n2i")) == (202, 206, 193, 194)
    assert new.get("absent") is True


def test_real_inline_baseline_table_is_not_read_as_a_mean_difference():
    # PLANT, real excerpt (PMID 39497860, PMC OA): the baseline table inline in <body> prose -> age 45.2+/-15.4 vs
    # 46.1+/-14.8 admitted as the AAD mean difference.
    old, new = _topic_fulltext("probiotics-aad-prevention", _fixture("ft_39497860_inline_baseline_excerpt.txt"))
    assert old.get("measure") == "MD" and old.get("mean1") == 45.2
    assert new.get("absent") is True


def test_inline_copy_of_baseline_table_is_removed_from_prose():
    # unit test of extraction_segments on a synthetic shape: the inline copy goes, the outcome sentence stays.
    from harness import fulltext as F
    prose = ("Results. Table 1 Baseline demographic and clinical characteristics Characteristic Probiotic group (n=170) "
             "Placebo group (n=170) Age, diarrhoea history (mean ± SD) 45.2 ± 15.4 46.1 ± 14.8 In the probiotic group, "
             "AAD occurred in 26 of 282 (9.2%) participants vs 69 of 273 (25.3%) in the placebo group (RR 0.36, 95% CI "
             "0.24 to 0.55).")
    text = (prose + "\n\n" + _TM + "\nTABLE Table 1: Baseline demographic and clinical characteristics\n"
            "Characteristic | Probiotic group (n=170) | Placebo group (n=170)\n"
            "Age, diarrhoea history (mean ± SD) | 45.2 ± 15.4 | 46.1 ± 14.8")
    seg = F.extraction_segments(text)
    assert "45.2" not in seg["prose"] and "RR 0.36" in seg["prose"]
    assert seg["dropped_tables"] and not seg["baseline_inline_not_located"]
    got = _ft_extract(text)
    assert not got.get("absent") and "mean1" not in got


def test_unbounded_inline_trace_refuses_the_full_text():
    # a baseline row IS in the prose but its caption is not, so its copy cannot be bounded: refuse, do not read
    from harness import fulltext as F
    text = ("Results. Age, diarrhoea history (mean ± SD) 45.2 ± 15.4 46.1 ± 14.8 was similar.\n\n" + _TM + "\n"
            "TABLE Table 1: Baseline characteristics\nCharacteristic | Probiotic | Placebo\n"
            "Age, diarrhoea history (mean ± SD) | 45.2 ± 15.4 | 46.1 ± 14.8")
    assert F.extraction_segments(text)["baseline_inline_not_located"]
    assert _ft_extract(text).get("absent") is True


def test_subgroup_effect_is_not_a_candidate():
    # PLANT (PMID 34541475): the PPI-subgroup RR 0.53 was a reported-effect CANDIDATE and the source-hierarchy
    # selector chose it over the refused ITT extraction. Candidates now obey the extractor's subgroup guard.
    from harness import source_hierarchy
    s = ("However, in the group of patients who were on regular PPI, probiotic use was associated with a lower risk "
         "of AAD at 7 days (19% v 35.7%, RR: 0.53, 95% CI: 0.29-0.99, p = 0.040).")
    spec = {"keywords": _KW, "name": "Antibiotic-associated diarrhoea"}
    assert source_hierarchy.source_effect_candidates(spec, fulltext=s) == []
    ok = "AAD occurred less often with probiotic (RR 0.36, 95% CI 0.24-0.55)."
    assert len(source_hierarchy.source_effect_candidates(spec, fulltext=ok)) == 1


# ---------------------------------------------------------------- CT.gov structured-results rung (pipeline)
def _ctgov_case(slug, fixture):
    import json
    import os
    from harness import pipeline
    from harness.ctgov_results import extract_ctgov
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cfg = json.load(open(os.path.join(root, "topics", slug + ".json"), encoding="utf-8"))
    oms = json.loads(_fixture(fixture))
    old = extract_ctgov(oms, cfg["primary_outcome"]["keywords"], cfg["intervention_terms"], cfg["comparator_terms"])
    new = pipeline._ctgov_rung_admissible(dict(old) if old else old, cfg["primary_outcome"])
    return old, new


def test_registry_percentage_is_not_read_as_event_counts():
    # PLANT, real registry results (EXAMINE NCT00968708, PMID 23992602): MACE is posted as a PERCENTAGE, 11.3 vs
    # 11.8. The rung read 11.3 as 11 events of 2701. The measure type was computed and never gated on.
    old, new = _ctgov_case("dpp4-mace-t2d", "ctgov_NCT00968708_EXAMINE.json")
    assert (old["ai"], old["n1i"], old["registry_measure_type"]) == (11, 2701, "PERCENTAGE")
    assert new is None


def test_single_component_registry_measure_is_not_the_declared_composite():
    # PLANT, real registry results (COLCHICINE-PCI NCT02594111, PMID 32295417): 'Peri-procedural Myocardial
    # Infarction' was admitted as the topic's major cardiovascular COMPOSITE because 'myocardial infarction' is one of
    # the composite's keywords.
    old, new = _ctgov_case("colchicine-secondary-cv-prevention", "ctgov_NCT02594111_COLCHICINE_PCI.json")
    assert old["registry_measure_type"] == "COUNT_OF_PARTICIPANTS" and "Myocardial Infarction" in old["registry_title"]
    assert new is None


def test_registry_title_composite_counts_components_not_words():
    from harness import pipeline as P
    for t, exp in (("Number of Participants With Peri-procedural Myocardial Infarction (MI)", False),
                   ("Hospitalization for heart failure (HHF)", False),
                   ("Time to First Occurrence of CV Death, MI, or Stroke", True),
                   ("Cardiovascular death or hospitalization for heart failure", True)):
        assert P._registry_title_is_composite(t) is exp, t


# ---------------------------------------------------------------- full text: other studies' results, unstructured OA copies
def _upw_case(slug, fixture, unstructured=True):
    import json
    import os
    from harness import extract, fulltext, pipeline
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cfg = json.load(open(os.path.join(root, "topics", slug + ".json"), encoding="utf-8"))
    spec = cfg["primary_outcome"]
    dc = extract.declared_is_composite(spec.get("name", ""))
    text = _fixture(fixture)
    old = extract.extract_trial(text, spec["keywords"], cfg.get("intervention_terms"), cfg.get("comparator_terms"),
                                declared_composite=dc, estimand=spec.get("estimand"))
    typed = (fulltext.UNSTRUCTURED_MARKER + "\n" + text) if unstructured else text
    new = pipeline._fulltext_extract(typed, spec, cfg.get("intervention_terms"), cfg.get("comparator_terms"), dc)
    return old, new


def test_a_cited_meta_analysis_is_not_the_trials_result():
    # PLANT, real excerpt (PMID 24044687, Unpaywall PDF): an INTRODUCTION sentence citing a meta-analysis
    # (RR 0.64, 0.47-0.86) was admitted as the trial's own AAD result.
    old, new = _upw_case("probiotics-aad-prevention", "upw_24044687_intro_metaanalysis_excerpt.txt", unstructured=False)
    assert old.get("effect") == 0.64
    assert new.get("absent") is True


def test_unstructured_copy_yields_no_counts_from_a_flattened_table():
    # PLANT, real excerpt (PMID 34138478, PMC HTML via Unpaywall): an outcome table flattened into prose gave
    # '1/16 vs 0/14'. From an HTML/PDF copy only a reported effect+CI in a prose sentence is typed evidence.
    old, new = _upw_case("corticosteroids-covid19-mortality", "upw_34138478_flattened_table_excerpt.txt")
    assert old.get("ai") is not None
    assert new.get("absent") is True


def test_unstructured_copy_still_yields_a_reported_effect():
    # CONTROL (PMID 32876695, CoDEX): the trial's own 28-day mortality HR 0.97 (0.72-1.31) must still be admitted.
    old, new = _upw_case("corticosteroids-covid19-mortality", "upw_32876695_codex_result_excerpt.txt")
    assert (new.get("effect"), new.get("ci_low"), new.get("ci_high")) == (0.97, 0.72, 1.31)


def test_a_covariate_odds_ratio_is_not_the_treatment_effect():
    # PLANT, real excerpt (PMID 24044687, Unpaywall PDF): 'binary multivariate logistic regression ... reduced appetite
    # (OR 5.04 ...) and being in the control group (OR 8.46 ...) as the unique risk factors' -> OR 5.04 was admitted as
    # the AAD effect of the probiotic.
    old, new = _upw_case("probiotics-aad-prevention", "upw_24044687_covariate_or_excerpt.txt")
    assert old.get("effect") == 5.04
    assert new.get("absent") is True
