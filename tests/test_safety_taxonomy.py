"""GI safety-outcome taxonomy (colchicine-secondary-CV review): four outcomes, every result bound by its SOURCE LABEL into exactly
one, and one admission rule for every trial. Plants: Akrami 15 vs 3 -> DIARRHOEA (not any-GI); LoDoCo2 GI hospitalisation
53/2,762 vs 50/2,760 (HR 1.06, 0.72-1.56) -> GI_HOSPITALISATION; CLEAR diarrhoea 10.2% vs 6.6% -> DIARRHOEA, RECONSTRUCTED."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from harness import reason_audit, safety_taxonomy as st  # noqa: E402
import rebind_safety_outcomes as rb  # noqa: E402

SLUG = "colchicine-secondary-cv-prevention"
AKRAMI_ABSTRACT = ("Evaluating adverse effects, gastrointestinal symptom was the most with the rate of 15 (12.5%) in the colchicine "
                   "group and 3 (2.5%) in the controls.")
CLEAR_ABSTRACT = "Diarrhea occurred in a higher percentage of patients with colchicine than with placebo (10.2% vs. 6.6%; P<0.001), but the incidence of serious infections did not differ between groups."
COLCOT_ABSTRACT = "Diarrhea was reported in 9.7% of the patients in the colchicine group and in 8.9% of those in the placebo group (P = 0.35)."
# TEST FIXTURE -- not a held source: LoDoCo2's GI-hospitalisation result is not in any source this corpus holds (its abstract omits
# it and the NEJM article is not in PMC). The sentence exercises the label/arm/effect parser on the values the review cites.
LODOCO2_FIXTURE = ("Hospitalization for gastrointestinal events occurred in 53 of 2762 patients (1.9%) in the colchicine group and "
                   "in 50 of 2760 patients (1.8%) in the placebo group (hazard ratio, 1.06; 95% CI, 0.72 to 1.56).")


def _src(text, sid="abstract:x"):
    return [{"source_id": sid, "text": text}]


def _review():
    return json.load(open(os.path.join(ROOT, "docs", "reviews", SLUG, "review.json"), encoding="utf-8"))


def test_PLANT_served_page_admits_akrami_as_any_gi_and_refuses_colcot_clear_diarrhoea():
    """Pre-fix state (fires on the served page): the inconsistency the taxonomy removes."""
    gi = next(o for o in _review()["outcomes"] if o["name"] == "Gastrointestinal adverse effects")
    assert [(t["label"], t["ai"], t["ci"]) for t in gi["trials"]] == [("34876021", 15, 3)]
    refused = {reason_audit.canonical_trial_id(a.get("id")): a for a in gi["declared_absent_trials"]}
    assert "diarrhea" in refused["31733140"]["reason"].lower() and "diarrhea" in refused["39555823"]["reason"].lower()


def test_PLANT_akrami_binds_to_diarrhoea_through_its_full_text_label():
    srcs = _src(AKRAMI_ABSTRACT) + rb.excerpt_sources("34876021")
    bound = st.bind_results(srcs, "34876021")
    hit = [b for b in bound if b["arms"] and [a["events"] for a in b["arms"]] == [15, 3]]
    assert len(hit) == 1 and hit[0]["outcome"] == st.DIARRHOEA and hit[0]["status"] == st.EXACT and hit[0]["admissible"]
    assert hit[0]["relabelled_from"]["outcome"] == st.GI_ANY          # the abstract's looser label lost to the full text's


def test_abstract_alone_does_not_invent_diarrhoea():
    bound = st.bind_results(_src(AKRAMI_ABSTRACT), "34876021")
    assert [b["outcome"] for b in bound] == [st.GI_ANY]


def test_PLANT_lodoco2_gi_hospitalisation_fixture_binds_there_with_counts_and_effect():
    (b,) = st.bind_results(_src(LODOCO2_FIXTURE), "32865380")
    assert b["outcome"] == st.GI_HOSPITALISATION and b["status"] == st.EXACT and b["admissible"]
    assert b["arms"] == [{"events": 53, "n": 2762}, {"events": 50, "n": 2760}]
    assert b["effect"]["estimate"] == 1.06 and b["effect"]["ci"] == [0.72, 1.56]


def test_PLANT_clear_diarrhoea_percentages_are_a_reconstructed_candidate():
    (b,) = st.bind_results(_src(CLEAR_ABSTRACT), "39555823")
    assert b["outcome"] == st.DIARRHOEA and b["status"] == st.RECONSTRUCTED and not b["admissible"]
    assert b["arms"] == [{"pct": 10.2}, {"pct": 6.6}] and "until exact counts are held" in b["admission"]


def test_same_rule_for_every_trial_colcot_is_treated_like_clear():
    (b,) = st.bind_results(_src(COLCOT_ABSTRACT), "31733140")
    assert (b["outcome"], b["status"], b["admissible"]) == (st.DIARRHOEA, st.RECONSTRUCTED, False)


def test_a_composition_note_does_not_relabel_an_any_gi_total():
    s = "Gastrointestinal adverse events, mostly diarrhoea, occurred in 40 of 200 patients and 20 of 198 patients."
    (b,) = st.bind_results(_src(s), "t")
    assert b["outcome"] == st.GI_ANY and b["admissible"] and b["unique_patient_total"]


def test_any_gi_event_counts_are_not_a_unique_patient_total():
    s = "There were 61 of 300 gastrointestinal adverse event episodes versus 30 of 298 episodes."
    (b,) = st.bind_results(_src(s), "t")
    assert b["outcome"] == st.GI_ANY and not b["admissible"] and "unique-patient" in b["admission"]


def test_discontinuation_for_gi_intolerance_is_its_own_outcome():
    s = "Discontinuation due to gastrointestinal intolerance occurred in 26 of 400 patients and 12 of 401 patients."
    (b,) = st.bind_results(_src(s), "t")
    assert b["outcome"] == st.GI_DISCONTINUATION and b["arms"][0]["events"] == 26


def test_gi_bleeding_is_outside_the_taxonomy():
    assert st.outcome_of_name("Gastrointestinal bleeding") is None
    assert st.outcome_of_name("Gastrointestinal adverse effects") == st.GI_ANY


def test_rebind_moves_akrami_out_of_any_gi_and_gives_clear_a_home():
    gi = next(o for o in _review()["outcomes"] if o["name"] == "Gastrointestinal adverse effects")
    akr = gi["trials"][0]
    r = st.rebind_row(gi["name"], akr, True, st.bind_results(_src(AKRAMI_ABSTRACT) + rb.excerpt_sources("34876021"), "34876021"))
    assert r["rebound"] and r["after"]["outcome"] == st.DIARRHOEA
    clear = next(a for a in gi["declared_absent_trials"] if "39555823" in str(a.get("id")))
    r2 = st.rebind_row(gi["name"], clear, False, st.bind_results(_src(CLEAR_ABSTRACT), "39555823"))
    assert r2["rebound"] and r2["after"]["outcome"] == st.DIARRHOEA and "narrower" in r2["why"]


def test_harms_only_trial_without_outcome_specific_rob_is_flagged_and_an_entry_clears_it():
    review = _review()
    flags = st.harms_only_rob_flags(review, reason_audit.canonical_trial_id)
    assert {"trial": "34876021", "outcome": "Gastrointestinal adverse effects", "flag": "HARMS_ONLY_NO_ROB_ENTRY"} in flags
    review["rob2"]["trials"]["34876021"] = {"outcomes": {"Gastrointestinal adverse effects": {"overall": "some concerns"}}}
    assert not [f for f in st.harms_only_rob_flags(review, reason_audit.canonical_trial_id) if f["trial"] == "34876021"]
    review["rob2"]["trials"]["34876021"] = {"overall": "low"}                          # trial-level only: still flagged
    assert [f["flag"] for f in st.harms_only_rob_flags(review, reason_audit.canonical_trial_id)
            if f["trial"] == "34876021"] == ["HARMS_ONLY_ROB_NOT_OUTCOME_SPECIFIC"]


# Regressions from the first corpus run, where a whole sentence's label was given to every result in it and adjacent
# percentages were paired across outcomes. Verbatim held abstract sentences.
def test_two_outcomes_in_one_sentence_are_not_paired_and_each_keeps_its_own_label():
    s = ("The most common adverse events were chest pain (8.1%), which did not differ between groups, and gastrointestinal "
         "symptoms (6.3%), which occurred more frequently in the colchicine (9.3%) versus placebo (3.2%) group.")
    (b,) = st.bind_results(_src(s), "32295417")
    assert b["outcome"] == st.GI_ANY and b["arms"] == [{"pct": 9.3}, {"pct": 3.2}] and b["status"] == st.RECONSTRUCTED


def test_diarrhoea_and_abdominal_pain_in_one_sentence_bind_separately():
    s = ("Also, statistically significant differences between the groups in the frequency of adverse events were revealed: the "
         "incidence of diarrhea in the colchicine group was 25.7% vs. 11.8% in the placebo group (OR 2.578; 95% Cl 1.300-5.111; "
         "p = 0.005); for abdominal pain, incidence values were 7% vs. 1.6%, correspondingly (OR 4.762; 95% Cl 1.010-22.91; p = 0.028).")
    bound = st.bind_results(_src(s), "36286314")
    assert [(b["outcome"], [a["pct"] for a in b["arms"]]) for b in bound] == [(st.DIARRHOEA, [25.7, 11.8])]   # abdominal pain: none
    assert bound[0]["status"] == st.EFFECT_CI and bound[0]["effect"]["ci"] == [1.3, 5.111]


def test_any_adverse_effect_rates_are_not_gi_even_when_gi_follows_in_the_sentence():
    s = ("The rates of reported adverse effects were not different (colchicine 23.0% versus placebo 24.3%), and they were "
         "predominantly gastrointestinal symptoms (colchicine, 23.0% versus placebo, 20.8%).")
    bound = st.bind_results(_src(s), "32862667")
    assert [[a["pct"] for a in b["arms"]] for b in bound] == [[23.0, 20.8]]
