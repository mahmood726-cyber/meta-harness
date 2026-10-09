"""R8-6: a report with NO registry identifier of its own (no NCT in its record or abstract, no AACT study_references
row, no PubMed DataBank accession) joins the family whose REGISTERED acronym its TITLE prints -- TRANSFORM-3 (PMID
31734084, '...Treatment-Resistant Depression-TRANSFORM-3.') belongs to NCT02422186, registered acronym 'TRANSFORM-3'.
The rule never overrides a held identifier, refuses a title naming two registered acronyms, and never reads an acronym
from the abstract alone. Synthetic fixtures."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from harness import trial_family as tf  # noqa: E402


def idx(**acr):
    return {n: {"raw": {"studies": [{"nct_id": n, "acronym": a}]}} for n, a in acr.items()}


INDEX = idx(NCT02422186="TRANSFORM-3", NCT02417064="TRANSFORM-1", NCT02418585="TRANSFORM-2", NCT09999999="CAP")
T3 = {"id": "31734084", "pubtypes": ["Randomized Controlled Trial"], "title": "Efficacy and Safety of Esketamine Nasal Spray Plus an Oral Antidepressant in Elderly "
                                 "Patients With Treatment-Resistant Depression-TRANSFORM-3.", "abstract": "Background..."}


def test_PLANT_transform3_joins_its_family_by_the_registered_acronym_in_its_title():
    n, ev = tf.acronym_title_link(T3, INDEX)
    assert n == "NCT02422186" and ev["acronym"] == "TRANSFORM-3" and ev["source"].startswith("registered acronym")


def test_PLANT_a_title_naming_two_registered_acronyms_links_nothing():
    r = dict(T3, title="Pooled analysis of TRANSFORM-1 and TRANSFORM-2")
    n, why = tf.acronym_title_link(r, INDEX)
    assert n is None and why == "TITLE_NAMES_2_REGISTERED_ACRONYMS"


def test_PLANT_an_acronym_in_the_abstract_only_or_too_short_links_nothing():
    r = dict(T3, title="Esketamine in elderly patients", abstract="... the TRANSFORM-3 study ...")
    assert tf.acronym_title_link(r, INDEX)[0] is None
    r2 = dict(T3, title="Outcomes in CAP patients")
    assert tf.acronym_title_link(r2, INDEX)[0] is None


def test_PLANT_a_longer_acronym_is_not_a_shorter_one():
    r = dict(T3, title="Results of TRANSFORM-31")
    assert tf.acronym_title_link(r, INDEX)[0] is None


# ------------------------------------------------ the first sweep's false links (9 Oct): each must now link nothing
RCT = ["Randomized Controlled Trial", "Journal Article"]
IDX2 = idx(NCT04381936="RECOVERY", NCT00251134="OMEGA", NCT03574597="SELECT", NCT01035255="PARADIGM-HF",
           NCT02937454="Affirm-AHF", NCT02422186="TRANSFORM-3")


def link(title, pubtypes=RCT):
    return tf.acronym_title_link({"id": "1", "title": title, "pubtypes": pubtypes}, IDX2)[0]


def test_PLANT_a_common_word_in_title_case_is_not_the_acronym():
    assert link("Enhanced Recovery After Surgery (ERAS) Pathways in Elective Total Joint Arthroplasty.") is None
    assert link("Omega-3 fatty acids for the primary and secondary prevention of cardiovascular disease.") is None


def test_PLANT_a_look_alike_cohort_a_pooled_paper_and_a_non_trial_paper_link_nothing():
    assert link("Cardiovascular Outcomes in a SELECT-Like Obesity Cohort: Real-World Insights") is None
    assert link("Effect of semaglutide on kidney outcomes in the SELECT, FLOW, and SOUL trials: a pooled analysis.") is None
    assert link("PARADIGM-HF eligibility in historical German HFrEF populations", ["Journal Article"]) is None


def test_an_upper_case_registered_acronym_in_a_trial_reports_title_still_links():
    assert link("The effect of intravenous ferric carboxymaltose on quality of life: results from AFFIRM-AHF.") == "NCT02937454"
    assert link(T3["title"]) == "NCT02422186"


# ---------------------------------------------------------------------------------------- codex r8-6-links-r1
ONE = {"NCT00000001": {"raw": {"studies": [{"acronym": "SELECT"}]}}}


def test_PLANT_r1_1_an_acronym_continued_by_a_hyphenated_token_is_another_word():
    om = {"NCT00000001": {"raw": {"studies": [{"acronym": "OMEGA"}]}}}
    assert tf.acronym_title_link({"title": "Effects of OMEGA-3 supplementation: a randomized trial", "pubtypes": RCT}, om)[0] is None


def test_PLANT_r1_2_an_ordinary_abbreviation_is_not_another_trial():
    assert tf.acronym_title_link({"title": "SELECT: a randomized trial in patients with COPD", "pubtypes": RCT}, ONE)[0] \
        == "NCT00000001"


def test_PLANT_r1_3_the_same_acronym_twice_is_still_one_trial():
    assert tf.acronym_title_link({"title": "SELECT: primary results of the SELECT randomized trial", "pubtypes": RCT},
                                 ONE)[0] == "NCT00000001"


def test_pooled_wording_still_refuses_with_plain_capital_trial_names():
    assert tf.acronym_title_link({"title": "Kidney outcomes in the SELECT, FLOW, and SOUL trials", "pubtypes": RCT},
                                 ONE)[0] is None


def test_PLANT_r1_4_a_paper_either_route_ties_to_two_families_is_multi_parent():
    import r8_6_report_links as S
    held = {"123": {}}
    assert S.classify("123", "NCT00000001", held, {"123": {"NCT00000001", "NCT00000002"}}, {}) == "MULTI_PARENT"
    assert S.classify("123", "NCT00000001", held, {"123": {"NCT00000001"}}, {}) == "STALE_REGISTRY"
    assert S.classify("9", "NCT00000001", held, {}, {}) == "NOT_HELD"
