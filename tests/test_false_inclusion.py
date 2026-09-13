"""Regression tests for the false-INCLUSION defect (melatonin cold audit, cycle 84):
lexical intervention matching INCLUDED records that share only a substring/class with the target --
receptor agonists (tasimelteon), analogues (beta-methyl-6-chloromelatonin), combinations
(melatonin + magnesium + zinc), and measured-not-randomised drugs (doxepin). intervention_none
excludes those forms (X3); population_none additions catch childhood / COMISA populations.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.screen import screen_record  # noqa: E402


def _rec(pmid, title, pubtypes=("Randomized Controlled Trial",)):
    return {"id": pmid, "id_type": "pmid", "title": title, "abstract": title,
            "conditions": [], "interventions": [], "pubtypes": list(pubtypes)}


INC = {
    "population_any": ["insomnia"],
    "population_none": ["children", "childhood", "comisa", "obstructive sleep apnea"],
    "intervention_any": ["melatonin"],
    "intervention_none": ["tasimelteon", "chloromelatonin", "beta-methyl", "magnesium", "zinc", "doxepin"],
    "intervention_in_title": True,
    "design_double_blind": False,
}


def _decision(title):
    return screen_record(_rec("1", title), INC, set())[0]


def test_receptor_agonist_excluded():
    assert _decision("Melatonin agonist tasimelteon improves sleep in patients with primary insomnia: an RCT") == "exclude"
    assert _decision("beta-Methyl-6-chloromelatonin, a melatonin receptor agonist, in insomnia: a randomized trial") == "exclude"


def test_combination_excluded():
    assert _decision("Effect of melatonin, magnesium, and zinc on primary insomnia: a randomized controlled trial") == "exclude"


def test_measured_not_randomised_excluded():
    assert _decision("Melatonin secretion after doxepin or placebo in insomnia: a randomized crossover trial") == "exclude"


def test_childhood_and_comisa_populations_excluded():
    assert _decision("Melatonin for childhood chronic sleep onset insomnia: a randomized controlled trial") == "exclude"
    assert _decision("Melatonin in obstructive sleep apnea and insomnia (COMISA): a randomized trial") == "exclude"


def test_genuine_melatonin_monotherapy_included():
    # A real prolonged-release melatonin monotherapy RCT in adult primary insomnia must still INCLUDE.
    assert _decision("Prolonged-release melatonin for primary insomnia in adults: a randomized controlled trial") == "include"


def test_melatonin_review_eligible_set_has_no_known_false_inclusions():
    """The live melatonin review must not carry the 6 audited PICO violators as screening includes."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rp = os.path.join(root, "docs", "reviews", "melatonin-primary-insomnia-sol", "review.json")
    if not os.path.exists(rp):
        return
    d = json.load(open(rp, encoding="utf-8"))
    inc = {str(r.get("id")) for r in d.get("screening", {}).get("records", []) if str(r.get("decision")) == "include"}
    for bad in ("28364493", "21226679", "15766306", "40971945", "8895944", "38816846"):
        assert bad not in inc, f"{bad} is a known PICO violation still screened INCLUDE"
