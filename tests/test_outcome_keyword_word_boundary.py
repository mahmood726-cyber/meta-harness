"""A keyword never matches inside a longer word (V14-01, denosumab).

'vertebral fracture' matched inside 'nonvertebral fracture', so FREEDOM's NONVERTEBRAL HR 0.80 (0.67-0.95) became a
published candidate for 'New vertebral fracture'; the estimand decision then labelled the served RR 0.32 'HR'
(and, with HR declared, served the nonvertebral HR -- the V13-03Q premise error).
"""
from harness import source_hierarchy as sh

NONVERT = ("Denosumab also reduced the risk of nonvertebral fracture, with a cumulative incidence of 6.5% in the "
           "denosumab group, versus 8.0% in the placebo group (hazard ratio, 0.80; 95% CI, 0.67 to 0.95; P=0.01)--a "
           "relative decrease of 20%.")
KWS = ["new vertebral fracture", "vertebral fracture", "vertebral fractures"]


def test_nonvertebral_is_not_vertebral():
    assert sh._effect_candidates_in_outcome(NONVERT, KWS) == []


def test_hyphenated_non_vertebral_is_not_vertebral():
    assert sh._effect_candidates_in_outcome(NONVERT.replace("nonvertebral", "non-vertebral"), KWS) == []


def test_vertebral_still_matches():
    s = NONVERT.replace("nonvertebral", "vertebral")
    got = sh._effect_candidates_in_outcome(s, KWS)
    assert [(c["scale"], c["effect"]) for c in got] == [("HR", 0.8)]
