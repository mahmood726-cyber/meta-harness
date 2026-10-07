"""Plants (search+screen audit, 2026-10-05): class SCREEN_POPULATION_TITLE_ONLY.

harness.screen judged the population from the title/conditions only, so a trial whose title names the outcome
('...secondary prevention of cardiovascular disease') was X2 'population not on-topic' although its abstract states
whom it randomised ('532 patients with stable coronary disease ... were randomly assigned'): LoDoCo, Nidorf 2013,
PMID 23265346. A sentence that states THIS study's enrolment is not an incidental mention; a background sentence is.
Radius over all 3,201 held decisions of the 32 topics: 20 records leave X2 -- 6 to include, 14 to a later rule
(LoDoCo itself to X3: our protocol requires a placebo comparator; LoDoCo randomised 'colchicine ... or no colchicine').
All tests below fail on the old code (enrolled_population absent / X2 fires)."""
from __future__ import annotations

from harness import screen

TERMS = ["coronary", "myocardial infarction", "acute coronary", "stable angina"]
LODOCO = {"id": "23265346", "id_type": "pmid", "title": "Low-dose colchicine for secondary prevention of cardiovascular disease.",
          "pubtypes": ["Journal Article", "Randomized Controlled Trial"],
          "abstract": ("OBJECTIVES: The objective of this study was to determine whether colchicine 0.5 mg/day can reduce the risk "
                       "of cardiovascular events. BACKGROUND: The presence of activated neutrophils in culprit plaques of patients "
                       "with unstable coronary disease raises the possibility of benefit. METHODS: In a clinical trial with a "
                       "prospective, randomized, observer-blinded endpoint design, 532 patients with stable coronary disease "
                       "receiving aspirin were randomly assigned colchicine 0.5 mg/day or no colchicine and followed for 3 years.")}
INC = {"population_any": TERMS, "intervention_any": ["colchicine"], "intervention_in_title": True,
       "comparator_any": ["placebo", "no colchicine"], "design_double_blind": False}


def test_the_enrolment_sentence_states_the_population():
    hit = screen.enrolled_population(LODOCO, TERMS)
    assert hit and hit[0] == "coronary" and "532 patients with stable coronary disease" in hit[1]


def test_lodoco_is_no_longer_excluded_for_its_population():
    d = screen.screen_record(LODOCO, INC, [])
    assert d.rule_id != "X2" and d.decision == "include"


def test_a_background_sentence_never_qualifies_even_with_randomised_in_it():
    rec = dict(LODOCO, abstract=("BACKGROUND: Randomized trials in patients with coronary disease have shown benefit. "
                                 "METHODS: We randomly assigned 200 adults with gout to colchicine or placebo."))
    assert screen.enrolled_population(rec, TERMS) is None
    assert screen.screen_record(rec, INC, []).rule_id == "X2"


def test_a_negated_population_never_qualifies():
    rec = dict(LODOCO, abstract="METHODS: 300 adults without coronary disease were randomly assigned colchicine or placebo.")
    assert screen.enrolled_population(rec, TERMS) is None


def test_the_section_label_in_force_is_the_one_at_the_verb_not_the_one_before_the_sentence():
    # 'METHODS:' opens the sentence that holds the verb; the previous label (BACKGROUND) must not govern it
    rec = dict(LODOCO, abstract="BACKGROUND: Inflammation matters. METHODS: In a trial, 50 patients with stable angina were "
                                "randomized to colchicine or placebo.")
    assert screen.enrolled_population(rec, TERMS)[0] == "stable angina"
