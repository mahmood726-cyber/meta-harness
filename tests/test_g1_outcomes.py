"""D10 inventory R1 (regex over held comparator text): the phrasings seen in the 12 comparators, 7 Oct."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_outcomes as go  # noqa: E402


def _one(text):
    hits, _ = go.regex_inventory(text)
    return [(h["family"], h["estimate"], h["lower"], h["upper"]) for h in hits]


def test_lancet_middle_dot_and_bracketed_abbreviation():
    t = "Thromboembolic events occurred (pooled odds ratio [OR] 0·96 [95% CI 0·65–1·41]; low-quality evidence)."
    assert _one(t) == [("HARM", "0.96", "0.65", "1.41")]
    hits, _ = go.regex_inventory(t)
    assert "0·96" in hits[0]["span"]                      # the span is the ORIGINAL text


def test_pdf_equals_glyph_and_ci_without_95():
    assert _one("more cases of drug withdrawals (RR ¼1.85, 95% CI 1.04 to 3.29, p for effect 0.04).") == \
        [("HARM", "1.85", "1.04", "3.29")]
    assert _one("this primary outcome showed a tendency to favor DOACs (OR 0.88, CI 0.75–1.03).") == \
        [("OTHER", "0.88", "0.75", "1.03")]


def test_spelled_measure_with_parenthesised_abbreviations():
    t = "DOAC recipients had a lower risk of stroke [Pooled Odds Ratio (OR) 0.76, 95% Confidence Interval (CI) (0.68–0.84)]."
    assert _one(t) == [("OTHER", "0.76", "0.68", "0.84")]


def test_all_cause_mortality_family():
    assert _one("the two groups did not differ in death from any cause (OR 0.94, 95% CI 0.79-1.12).") == \
        [("ALL_CAUSE_MORTALITY", "0.94", "0.79", "1.12")]


def test_a_result_of_another_contrast_or_population_is_not_ours():
    # 7 Oct, inventory v1: denosumab's 'acceptability' was risedronate vs placebo (a network meta-analysis) and
    # sglt2-ppHF's 'cardiovascular death' was canagliflozin-only in one population
    den = go.topic("denosumab-vertebral-fracture")
    assert not go.contrast_is_ours("risedronate vs placebo", den)
    assert go.contrast_is_ours("denosumab vs placebo", den)
    assert not go.contrast_is_ours("denosumab vs alendronate", den)
    doac = go.topic("doac-vte-recurrence")
    assert go.population_is_ours(None, doac)
    assert go.population_is_ours("patients with acute VTE", doac)
    assert not go.population_is_ours("patients with NVAF", doac)


def test_an_already_declared_outcome_is_linked_whatever_its_read_family():
    # a SYNTHETIC topic: the live topic file changes when amendments register (a control pinned to a mutable artefact
    # retires itself -- this assertion broke the moment 'Net clinical benefit' was registered, 7 Oct)
    t = {"secondary_outcomes": [], "harm_outcomes": [{"name": "Major bleeding", "keywords": ["major bleeding"]}]}
    assert go.linked_to("major bleeding", t) == "Major bleeding"
    assert go.linked_to("net clinical benefit", t) is None


def test_one_agent_of_a_class_topic_is_a_split_not_our_result():
    sg = go.topic("sglt2-primary-prevention-hf")
    assert not go.contrast_is_ours("canagliflozin vs placebo", sg)
    assert go.contrast_is_ours("SGLT2 inhibitors vs placebo", sg)
    assert go.contrast_is_ours("denosumab vs placebo", go.topic("denosumab-vertebral-fracture"))   # one-agent topic


def test_a_single_agent_meta_of_a_class_topic_is_the_whole_analysis():
    # iv-iron's comparator 39727669 pools FCM only: 'FCM vs placebo/SoC' IS its result; a split only when the same
    # comparator also prints a class-level result
    iv = go.topic("iv-iron-hfref-hosp")
    assert go.contrast_is_ours("FCM vs placebo/SoC", iv, class_level_printed=False)
    assert not go.contrast_is_ours("FCM vs placebo/SoC", iv, class_level_printed=True)


def test_sharing_one_word_with_our_primary_does_not_make_it_our_primary():
    tx = go.topic("tranexamic-acid-pph")
    assert not go.is_our_primary("Death within 24 h", tx)
    assert go.is_our_primary("Death due to bleeding", tx)
    assert go.is_our_primary("recurrent VTE and related death", go.topic("doac-vte-recurrence"))


def test_the_registered_spec_is_the_comparators_wording_and_measure():
    e = {"name": "incidence of serious adverse events", "family": "P2_KEY_HARMS",
         "comparator_result": {"measure": "OR", "estimate": "0.73", "lower": "0.49", "upper": "1.10", "timepoint": None}}
    sp = go.spec_of(e)
    assert sp["name"] == "Incidence of serious adverse events" and sp["estimand"] == "OR"
    assert sp["keywords"] == ["incidence of serious adverse events", "serious adverse events"]
    assert sp["population"].startswith("trial-reported")
    p1 = go.spec_of({"name": "total deaths", "family": "P1_ALL_CAUSE_MORTALITY",
                     "comparator_result": {"measure": "pooled OR", "timepoint": "24 weeks"}})
    assert "death from any cause" in p1["keywords"] and p1["timepoint"] == "24 weeks" and "population" not in p1
    assert [go.estimand_of(m) for m in ("WMD", "RR", "Pooled OR", "hazard ratio", "SMD")] == ["MD", "RR", "OR", "HR", "SMD"]


def test_posted_arms_map_by_our_terms_and_refuse_ambiguity():
    doac = go.topic("doac-vte-recurrence")
    assert go._arm("Dabigatran Etexilate", doac) == "intervention"
    assert go._arm("Warfarin", doac) == "control"
    assert go._arm("Placebo for dabigatran + warfarin", doac) == "control"     # the placebo-for clause is not the drug
    assert go._arm("Run-in period", doac) is None
    v, why = go._two_arms([("Dabigatran 150 mg", 10, 100), ("Dabigatran 110 mg", 12, 100), ("Warfarin", 15, 100),
                           ("Total", 37, 300)], doac)
    assert v == (22, 200, 15, 100) and why is None                           # dose arms summed; shared control once
    v, why = go._two_arms([("Dabigatran", 10, 100), ("Warfarin", 15, 100), ("Aspirin", 9, 100)], doac)
    assert v is None and why.startswith("UNMAPPED_GROUP")


def test_counts_pool_on_the_comparators_measure_and_other_scales_are_never_converted():
    r = {"id": "A", "events_t": 10, "n_t": 100, "events_c": 20, "n_c": 100, "measure": None}
    st, why = go.to_study(r, "OR")
    assert st is not None and why is None
    st, why = go.to_study({"id": "B", "measure": "HR", "effect": 0.8, "lower": 0.6, "upper": 1.1}, "OR")
    assert st is None and why.startswith("MEASURE_DIFFERENCE")
    st, why = go.to_study({"id": "C", "events_t": 120, "n_t": 100, "events_c": 20, "n_c": 100}, "OR")
    assert st is None                                   # events > N is never pooled
    assert go._f("0·77") == 0.77 and go._f("−10.94") == -10.94


def test_a_space_separated_thousand_is_the_number():
    import g1_trial_acquire as ta
    q = "Complications * | 10 033 | 9985 | .. | Sepsis | 180 (1·8%) | 185 (1·9%)"
    assert ta._num_in(10033, q) and ta._num_in(9985, q) and ta._num_in(180, q)
    assert not ta._num_in(1003, q)


def test_a_ladder_row_bound_to_another_outcome_is_named_and_set_aside():
    # 7 Oct (D10): the served abstract extractor gave 'Death from any cause' DECLARE's RENAL HR 0.76 (the effect sits in
    # the clause before the keyword), and a structured CT.gov row 'HF Hospitalisations' was bound to 'Non-HF
    # hospitalizations' -- both would serve another outcome's number under the new outcome's name
    sp = {"name": "Death from any cause", "keywords": ["death from any cause", "all-cause mortality"]}
    src = ("abstract effect+CI (HR): A renal event occurred in 4.3% in the dapagliflozin group and in 5.6% in the placebo "
           "group (hazard ratio, 0.76; 95% CI, 0.67 to 0.87), and death from any cause occurred in 6.2% and 6.6%")
    assert go.ladder_misbound({"effect": 0.76, "source": src}, sp)
    ok = "abstract effect+CI (HR): death from any cause occurred in 6.2% and 6.6% (hazard ratio, 0.93; 95% CI 0.82 to 1.04)"
    assert not go.ladder_misbound({"effect": 0.93, "source": ok}, sp)
    nh = {"name": "Non-HF hospitalizations", "keywords": ["non-hf hospitalizations"]}
    st = "ClinicalTrials.gov results (structured target endpoint): outcome 'HF Hospitalisations' HR 0.73 (95% CI 0.59 to 0.92)"
    assert go.ladder_misbound({"effect": 0.73, "source": st}, nh)


def test_a_qualified_subset_or_a_composite_is_not_our_outcome():
    # 7 Oct (D10): IRONMAN's 'cardiac serious adverse events' was served as serious adverse events, and STAREE's
    # 'Death from any cause, dementia, or persistent physical disability' HR 0.94 as all-cause mortality
    sae = {"name": "Incidence of serious adverse events", "keywords": ["incidence of serious adverse events",
                                                                        "serious adverse events"]}
    r = {"counts": {"events_t": 200}, "source": "abstract arm-level counts (percentage-corroborated): Fewer patients in "
         "the ferric derisomaltose group had cardiac serious adverse events (200 [36%]) than in the usual care group"}
    assert go.ladder_misbound(r, sae)
    ok = {"counts": {"events_t": 250}, "source": "abstract arm-level counts (percentage-corroborated): Serious adverse "
          "events occurred in 250 (45%) of 559 patients in the ferric carboxymaltose group"}
    assert not go.ladder_misbound(ok, sae)
    acm = {"name": "All-cause mortality", "keywords": ["all-cause mortality", "death from any cause"]}
    comp = {"effect": 0.94, "source": "abstract effect+CI (HR): Death from any cause, dementia, or persistent physical "
            "disability occurred in 637 participants (hazard ratio, 0.94; 95% CI, 0.80 to 1.10)"}
    assert go.ladder_misbound(comp, acm)
    jup = {"effect": 0.8, "source": "abstract effect+CI (HR): Corresponding rates of all-cause mortality in this age group "
           "were 1.63 and 2.04 (hazard ratio, 0.80 [CI, 0.62 to 1.04]; P = 0.09)"}
    assert not go.ladder_misbound(jup, acm)


def test_a_number_the_source_does_not_show_is_refused_not_passed():
    acm = {"name": "All-cause mortality", "keywords": ["all-cause mortality", "death from any cause"]}
    cut = {"effect": 0.94, "source": "abstract effect+CI (HR): Death from any cause, dementia, or persistent physical "
           "disability occurred in 637 participants (21.6 events per 1000 person-years) in the atorvastatin group and in 676 "
           "participants (23.0 events per 10"}
    assert go.ladder_misbound(cut, acm)
