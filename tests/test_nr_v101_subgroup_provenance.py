"""Lane NR V1.0.1 plants: SUBGROUP PROVENANCE (statins-older-adults review).

JUPITER's >=70-years result was served as a 'pre-specified' subgroup because the topic asserted it; the paper's own
LIMITATION says the age cut-point was chosen after trial completion. subgroup_provenance is now DERIVED from a source
span (harness/subgroup_provenance.py) and feeds RoB D5 (selection of the reported result) -- never exclusion: the
number stays.
"""
from __future__ import annotations

import json
from pathlib import Path

from harness import rob2
from harness import subgroup_provenance as sp

ROOT = Path(__file__).resolve().parents[1]
JUPITER_LIMITATION = ("LIMITATION: Effect estimates from this exploratory analysis with age cut-point chosen after "
                      "trial completion should be viewed in the context of the overall trial results.")


def _row(pid="20404379"):
    return {"id": f"PMID {pid}", "estimate": 0.61, "source": ""}


# ---- the derivation ---------------------------------------------------------------------------------------------

def test_jupiter_post_hoc_from_limitation_span():
    rec = {"abstract": "BACKGROUND: ... RESULTS: HR 0.61 (0.46-0.82). " + JUPITER_LIMITATION}
    prov = sp.derive(_row(), rec, "subgroup")
    assert prov["value"] == sp.POST_HOC
    assert "chosen after trial completion" in prov["span"]
    assert prov["source"] == "held abstract"
    assert sp.evidence_unit(prov) == "post_hoc_subgroup"


def test_post_hoc_wins_over_a_general_prespecified_elsewhere():
    rec = {"abstract": "Prespecified subgroups included sex and region. " + JUPITER_LIMITATION}
    assert sp.derive(_row(), rec, "subgroup")["value"] == sp.POST_HOC


def test_bare_post_hoc_about_another_analysis_does_not_override_a_prespecification():
    rec = {"abstract": "A post hoc sensitivity analysis excluded non-adherent participants. "
                       "The subgroups were prespecified in the statistical analysis plan."}
    assert sp.derive(_row(), rec, "subgroup")["value"] == sp.PRESPECIFIED
    rec = {"abstract": "This post hoc analysis examined participants aged 70 years or older."}
    assert sp.derive(_row(), rec, "subgroup")["value"] == sp.POST_HOC


# codex call NR-C18 (adversarial), each case reproduced by execution before the fix
_ADVERSARIAL = [
    ("The subgroup analyses were not post hoc.", None),
    ("The subgroups were prespecified, not post hoc.", sp.PRESPECIFIED),
    ("The subgroups were prespecified, with cut-points not selected after trial completion.", sp.PRESPECIFIED),
    ("The subgroup analysis was prespecified; a post hoc sensitivity analysis excluded non-adherent participants.",
     sp.PRESPECIFIED),
    ("We evaluated a priori subgroups defined in the protocol.", sp.PRESPECIFIED),
    ("The subgroups had been predefined in the protocol before recruitment.", sp.PRESPECIFIED),
    ("This secondary analysis of a randomized trial examined subgroups defined a priori in the protocol.",
     sp.PRESPECIFIED),
    ("Exploratory subgroup analyses were devised after trial completion.", sp.POST_HOC),
    ("The hypothesis-generating subgroup analysis was planned after trial completion.", sp.POST_HOC),
    ("The subgroups were not prospectively prespecified.", sp.POST_HOC),
    ("The subgroup comparison of Drug A vs. Drug B was post hoc.", sp.POST_HOC),
    ("The subgroup analyses, e.g. Asian participants, were post hoc.", sp.POST_HOC),
    ("The subgroup analysis used the Smith et al. Risk Index and was post hoc.", sp.POST_HOC),
    # genuinely ambiguous boundary controls: stay UNRESOLVED
    ("The exploratory, hypothesis-generating subgroup analysis assessed treatment effects.", None),
    ("The subgroup cut-points were defined before unblinding.", None),
    ("This secondary analysis of a randomized trial examined treatment effects in subgroups.", None),
]


def test_adversarial_sentences():
    wrong = [(s, want, got) for s, want in _ADVERSARIAL
             if (got := sp.derive(_row(), {"abstract": s}, "subgroup")["value"]) != want]
    assert not wrong, wrong


def test_melatonin_subgroup_is_unresolved_not_asserted():
    # the topic used to assert 'pre-specified age 65-80 subgroup'; the held abstract does not state it
    topic = json.load(open(ROOT / "topics" / "melatonin-primary-insomnia-sol.json", encoding="utf-8"))
    assert "pre-specified" not in json.dumps(topic).lower()
    assert topic["primary_outcome"]["trial_annotations"]["20712869"]["evidence_unit"] == "subgroup"


def test_prespecified_control():
    rec = {"abstract": "The age subgroups were prespecified in the statistical analysis plan. HR 0.70 (0.55-0.90)."}
    prov = sp.derive(_row(), rec, "subgroup")
    assert prov["value"] == sp.PRESPECIFIED and "prespecified" in prov["span"]


def test_unresolved_control_is_not_assumed_prespecified():
    rec = {"abstract": "Among participants aged 70 years or older, HR 0.61 (0.46-0.82)."}
    prov = sp.derive(_row(), rec, "subgroup")
    assert prov["value"] is None and prov["span"] is None
    assert sp.evidence_unit(prov) == "subgroup_unresolved"


def test_whole_trial_control_ignores_post_hoc_text():
    rec = {"abstract": JUPITER_LIMITATION}
    assert sp.derive(_row(), rec, "trial")["value"] == sp.WHOLE_TRIAL
    assert sp.derive(_row(), rec, None)["value"] == sp.WHOLE_TRIAL


def test_the_topic_can_no_longer_assert_prespecified():
    # a stale 'prespecified_subgroup' declaration is only 'this is a subgroup'; the value still comes from the text
    rec = {"abstract": JUPITER_LIMITATION}
    assert sp.derive(_row(), rec, "prespecified_subgroup")["value"] == sp.POST_HOC


# ---- RoB D5, not exclusion --------------------------------------------------------------------------------------

POST = {"value": sp.POST_HOC, "span": JUPITER_LIMITATION, "source": "held abstract"}
PRE = {"value": sp.PRESPECIFIED, "span": "prespecified", "source": "held abstract"}


def test_post_hoc_raises_d5_from_not_assessable_and_low():
    na = rob2.derive_d5([], "Major vascular events", None, [], POST)
    assert na["level"] == "some concerns" and "POST-HOC subgroup" in na["basis"]
    assert na["rule_id"].endswith("+subgroup_provenance_v1")
    reg = [{"measure": "Major vascular events", "title": "", "description": ""}]
    low = rob2.derive_d5(reg, "Major vascular events", None, [], None)
    assert low["level"] == "low"
    assert rob2.derive_d5(reg, "Major vascular events", None, [], POST)["level"] == "some concerns"


def test_prespecified_and_absent_provenance_change_nothing():
    reg = [{"measure": "Major vascular events", "title": "", "description": ""}]
    assert rob2.derive_d5(reg, "Major vascular events", None, [], PRE)["level"] == "low"
    assert rob2.derive_d5([], "Major vascular events", None, [], None)["level"] == "not_assessable"


def test_d5_with_provenance_is_rederivable():
    d5 = rob2.derive_d5([], "Major vascular events", None, [], POST)
    again = rob2.rederive_domain(d5)
    assert (again["level"], again["rule_id"], again["basis"]) == (d5["level"], d5["rule_id"], d5["basis"])
    assert rob2.apply_subgroup_provenance(d5, POST)["level"] == "some concerns"  # idempotent on the stored domain


# ---- the served statins review ----------------------------------------------------------------------------------

def _live():
    p = ROOT / "docs" / "reviews" / "statins-primary-prevention-elderly" / "review.json"
    return json.load(open(p, encoding="utf-8"))


def test_served_jupiter_is_post_hoc_the_number_stays_and_d5_reflects_it():
    rev = _live()
    prim = next(o for o in rev["outcomes"] if o.get("primary"))
    jup = next(t for t in prim["trials"] if t["id"] == "PMID 20404379")
    assert jup["subgroup_provenance"]["value"] == "post_hoc_subgroup"
    assert "chosen after trial completion" in jup["subgroup_provenance"]["span"]
    assert jup["evidence_unit"] == "post_hoc_subgroup"
    assert prim["result"]["k"] == 2  # still pooled: RoB input, never an exclusion
    d5 = rev["rob2"]["trials"]["20404379"]["domains"]["D5_selective_reporting"]
    assert d5["level"] == "some concerns"
    assert rob2.rederive_domain(d5)["level"] == "some concerns"
    other = next(t for t in prim["trials"] if t["id"] != "PMID 20404379")
    assert other["subgroup_provenance"]["value"] == "whole_trial"


def test_served_page_no_longer_calls_jupiter_prespecified():
    page = open(ROOT / "docs" / "reviews" / "statins-primary-prevention-elderly" / "index.html",
                encoding="utf-8").read()
    assert "pre-specified subgroup" not in page
    assert "post-hoc subgroup of JUPITER" in page
    topic = json.load(open(ROOT / "topics" / "statins-primary-prevention-elderly.json", encoding="utf-8"))
    assert "pre-specified" not in json.dumps(topic).lower()
