"""NR-C06 (Codex patch, verified by the lane): arm counts were assigned by the sentence-wide FIRST mention of an arm term,
so an introductory 'Compared with placebo, ...' reversed two counts each labelled by its own arm -- an inverted effect.
Rule: the nearest unambiguous arm label of each count (not crossing another count or a clause separator) decides; two
counts claiming the same arm are refused (R4); missing or tied labels keep reading order. 'X vs Y ... receiving A and B,
respectively' is positional."""
from __future__ import annotations

import pytest

from harness import extract

I, C = ["colchicine"], ["placebo"]


def _t(a):
    return None if a is None else (a.ai, a.n1i, a.ci, a.n2i)


@pytest.mark.parametrize("sentence,expected", [
    ("Compared with placebo, colchicine reduced diarrhoea: 15/120 (12.5%) in the colchicine group versus 30/120 (25.0%) "
     "in the placebo group.", (15, 120, 30, 120)),
    ("Compared with placebo, colchicine: 15/120 (12.5%) versus placebo: 30/120 (25.0%).", (15, 120, 30, 120)),
    ("Compared with colchicine, placebo: 30/120 (25.0%) versus colchicine: 15/120 (12.5%).", (15, 120, 30, 120)),
    ("Compared with colchicine, 30/120 (25.0%) in the placebo group versus 15/120 (12.5%) in the colchicine group.",
     (15, 120, 30, 120)),
    # 'respectively' is ORDER: first count -> first listed arm
    ("Compared with colchicine, diarrhoea occurred in 30/120 (25.0%) vs 15/120 (12.5%) patients receiving placebo and "
     "colchicine, respectively.", (15, 120, 30, 120)),
    # controls: unlabelled counts keep reading order
    ("Colchicine versus placebo: 15/120 (12.5%) versus 30/120 (25.0%).", (15, 120, 30, 120)),
])
def test_each_count_goes_to_the_arm_that_labels_it(sentence, expected):
    assert _t(extract.extract_arm_counts(sentence, I, C, conflicts=[])) == expected


def test_two_counts_labelled_with_the_same_arm_are_refused():
    s = ("Colchicine was compared with placebo: 15/120 (12.5%) in the placebo group versus 30/120 (25.0%) in the placebo "
         "group.")
    assert extract.extract_arm_counts(s, I, C, conflicts=[]) is None


# ---- NR-C10 (Codex patch for NR-C08 round-2 counterexamples, verified by the lane) ------------------------------------
@pytest.mark.parametrize("sentence,interv,comp,expected", [
    # 'respectively' with arm nouns in the list is positional (#1, #2: were REVERSED)
    ("Compared with colchicine, diarrhoea occurred in 30/120 (25.0%) versus 15/120 (12.5%) in the placebo group and "
     "colchicine group, respectively.", ["colchicine"], ["placebo"], (15, 120, 30, 120)),
    ("Compared with aspirin, diarrhoea occurred in 15/120 (12.5%) versus 30/120 (25.0%) in the colchicine plus aspirin "
     "group and aspirin group, respectively.", ["colchicine plus aspirin"], ["aspirin"], (15, 120, 30, 120)),
    # three arm groups: never 'the first two' (#3: the 1 mg arm was served as placebo)
    ("Diarrhoea occurred in 15/120 (12.5%) with colchicine 0.5 mg, 24/120 (20.0%) with colchicine 1 mg, and 30/120 "
     "(25.0%) with placebo.", ["colchicine 0.5 mg"], ["placebo"], None),
    # a comparator label containing 'no' is not a negation (#6)
    ("Diarrhoea occurred with colchicine: 15/120 (12.5%); with no colchicine: 30/120 (25.0%).", ["colchicine"],
     ["no colchicine"], (15, 120, 30, 120)),
    # thousands separators (#7)
    ("Diarrhoea occurred in 150/1,200 (12.5%) with colchicine and 300/1,200 (25.0%) with placebo.", ["colchicine"],
     ["placebo"], (150, 1200, 300, 1200)),
])
def test_c10_arm_assignment(sentence, interv, comp, expected):
    assert _t(extract.extract_arm_counts(sentence, interv, comp, conflicts=[])) == expected


def test_c10_4_a_failed_identity_pairing_is_never_rescued_by_swapping_sizes():
    out = extract.extract_trial("Patients were assigned to colchicine (n=200) or placebo (n=100). Diarrhoea occurred in 10 "
                                "(10.0%) with colchicine and 40 (20.0%) with placebo.", ["diarrhoea"], ["colchicine"],
                                ["placebo"], declared_composite=False, estimand="RR")
    assert out.get("absent"), out


def test_c10_5_a_denominator_stated_in_the_result_sentence_wins():
    out = extract.extract_trial("Patients were assigned to colchicine (n=100) or placebo (n=100). In the safety population "
                                "of 96 treated patients per arm, diarrhoea occurred in 15 (15.6%) with colchicine and 24 "
                                "(25.0%) with placebo.", ["diarrhoea"], ["colchicine"], ["placebo"],
                                declared_composite=False, estimand="RR")
    assert (out.get("ai"), out.get("n1i"), out.get("ci"), out.get("n2i")) == (15, 96, 24, 96), out
    assert not out.get("count_pct_conflicts")


def test_c10_the_stored_source_keeps_the_text_as_written():
    out = extract.extract_trial("Diarrhoea occurred in 150/1,200 (12.5%) with colchicine and 300/1,200 (25.0%) with "
                                "placebo.", ["diarrhoea"], ["colchicine"], ["placebo"], declared_composite=False,
                                estimand="RR")
    assert "1,200" in str(out.get("source")), out     # the verifier locates the span verbatim


# ---- corpus radius of NR-C10 (lane NR): only a third ARM refuses; further RESULTS in the sentence do not --------------
@pytest.mark.parametrize("sentence,interv,comp,kw,expected", [
    # metformin 11172832 (served): two outcomes for the same two arms
    ("RESULT(S): In the metformin and placebo groups, 9 of 12 participants (75%) and 4 of 15 participants (27%) "
     "ovulated, and 6 of 11 participants (55%) and 1 of 14 participants (7%) conceived, respectively.",
     ["metformin"], ["placebo"], {}, (9, 12, 4, 15)),
    # COPPS-2 25172965 (served): AF, then effusion, each colchicine vs placebo
    ("There were no significant differences between the colchicine and placebo groups for the secondary end points of "
     "postoperative AF (colchicine, 61 patients [33.9%]; placebo, 75 patients [41.7%]; absolute difference, 7.8%; 95% CI, "
     "-2.2% to 17.6%) or postoperative pericardial/pleural effusion (colchicine, 103 patients [57.2%]; placebo, 106 "
     "patients [58.9%]; absolute difference, 1.7%)", ["colchicine"], ["placebo"], {"denom_each": 180},
     (61, 180, 75, 180)),
    # semaglutide 40961952 (not served): one result, THREE arms -> refused (it compared the two doses before)
    ("Gastrointestinal adverse events were more common with semaglutide 7·2 mg (711 [70·8%] of 1004) versus 2·4 mg "
     "(123 [61·2%] of 201) or placebo (86 [42·8%] of 201), as was dysaesthesia.", ["semaglutide"], ["placebo"], {}, None),
])
def test_radius_only_a_third_arm_refuses(sentence, interv, comp, kw, expected):
    assert _t(extract.extract_arm_counts(sentence, interv, comp, conflicts=[], **kw)) == expected


# ---- NR-C15 (Codex): a THIRD ARM is refused whatever it is called; a new RESULT is marked by a statistic or an
#      outcome verb, not by an unknown word; the paired "A versus B and C versus D, respectively" keeps its first pair
C15 = [
 [
  "Remission occurred with methotrexate in 15/100 (15%), with adalimumab in 24/100 (24%), and with placebo in 10/100 (10%).",
  [
   "methotrexate"
  ],
  [
   "placebo"
  ],
  None
 ],
 [
  "Response rates were 15/100 (15%) with the standard regimen, 24/100 (24%) with the intensive regimen, and 10/100 (10%) with usual care.",
  [
   "standard regimen"
  ],
  [
   "usual care"
  ],
  None
 ],
 [
  "Diarrhoea occurred in 15/120 (12.5%) with colchicine, while 24/120 (20.0%) receiving aspirin and 30/120 (25.0%) receiving placebo experienced diarrhoea.",
  [
   "colchicine"
  ],
  [
   "placebo"
  ],
  None
 ],
 [
  "Diarrhoea by randomized group: A (colchicine): 15/120 (12.5%); B (aspirin): 24/120 (20.0%); C (placebo): 30/120 (25.0%).",
  [
   "colchicine"
  ],
  [
   "placebo"
  ],
  None
 ],
 [
  "Response occurred in 15/100 (15%) with metformin, 24/100 (24%) with usual care, and 10/100 (10%) with placebo.",
  [
   "metformin"
  ],
  [
   "placebo"
  ],
  None
 ],
 [
  "Diarrhoea occurred with colchicine 0.5 mg in 15/120 (12.5%), compared with 24/120 (20.0%) with colchicine 1 mg and 30/120 (25.0%) with placebo.",
  [
   "colchicine 0.5 mg"
  ],
  [
   "placebo"
  ],
  None
 ],
 [
  "Diarrhoea occurred in 15/120 (12.5%) with low-dose colchicine, 24/120 (20.0%) with high-dose colchicine, and 30/120 (25.0%) with placebo.",
  [
   "low-dose colchicine"
  ],
  [
   "placebo"
  ],
  None
 ],
 [
  "Diarrhoea and nausea occurred in the colchicine versus placebo groups in 15/120 (12.5%) versus 30/120 (25.0%) and 12/120 (10.0%) versus 18/120 (15.0%), respectively.",
  [
   "colchicine"
  ],
  [
   "placebo"
  ],
  [
   15,
   120,
   30,
   120
  ]
 ],
 [
  "Response at weeks 4 and 8 in the metformin versus placebo groups was 15/100 (15%) versus 10/100 (10%) and 24/100 (24%) versus 18/100 (18%), respectively.",
  [
   "metformin"
  ],
  [
   "placebo"
  ],
  [
   15,
   100,
   10,
   100
  ]
 ]
]


@pytest.mark.parametrize("sentence,interv,comp,expected", C15)
def test_c15_a_third_arm_is_never_read_as_the_comparator(sentence, interv, comp, expected):
    assert _t(extract.extract_arm_counts(sentence, interv, comp, conflicts=[])) == (tuple(expected) if expected else None)
