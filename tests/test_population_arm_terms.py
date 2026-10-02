"""PLANTS: a POPULATION rule (X2, include.population_none) never matches an ARM name (Mahmood 3 Oct). O'Neil 2018
(semaglutide vs liraglutide vs placebo in adults with obesity) was excluded as 'wrong population: title mentions
liraglutide' -- its active-comparator arm read as who was enrolled, the condition-as-outcome family."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from harness import screen, screen_entry  # noqa: E402

ART = os.path.join(ROOT, "harness", "data", "population_term_classes.json")


def _rec(slug, pmid):
    rj = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))
    r = next((x for x in rj.get("records", []) if str(x.get("id")) == pmid), None)
    return r or json.load(open(os.path.join(ROOT, "outputs", "k_gap", "member_records.json"), encoding="utf-8"))[pmid]


def test_oneil_2018_passes_the_population_rule():
    cfg = json.load(open(os.path.join(ROOT, "topics", "semaglutide-obesity-weight.json"), encoding="utf-8"))
    d = screen.screen_record(_rec("semaglutide-obesity-weight", "30122305"), cfg["include"], set())
    assert d[1] != "X2", d                      # was: X2 wrong population: title/conditions mention 'liraglutide'


def test_a_population_rule_keeps_population_and_design_words_and_drops_arm_names():
    inc = {"population_none": ["diabetes", "maintenance", "liraglutide", "tirzepatide", "children"],
           "intervention_any": ["semaglutide"], "comparator_any": ["placebo"]}
    assert screen_entry.population_descriptors(inc) == ["diabetes", "maintenance", "children"]
    # the topic's own arm terms are never population descriptors either
    assert screen_entry.population_descriptors({"population_none": ["placebo", "adults"],
                                                "comparator_any": ["placebo"]}) == ["adults"]


def test_a_real_population_exclusion_still_fires():
    # Rubino 2021 (STEP 4, randomised withdrawal: 'Weight Loss Maintenance') stays excluded -- 'maintenance' is not an arm
    cfg = json.load(open(os.path.join(ROOT, "topics", "semaglutide-obesity-weight.json"), encoding="utf-8"))
    d = screen.screen_record(_rec("semaglutide-obesity-weight", "33755728"), cfg["include"], set())
    assert d[1] == "X2" and "maintenance" in d[2].lower(), d


def test_the_term_classes_cover_every_population_term_and_no_population_term_is_an_inn():
    import glob
    import build_population_term_classes as b
    art = json.load(open(ART, encoding="utf-8"))
    assert art["snapshot"]["digest"]
    for p in glob.glob(os.path.join(ROOT, "topics", "*.json")):
        slug = os.path.basename(p)[:-5]
        pn = (json.load(open(p, encoding="utf-8")).get("include") or {}).get("population_none") or []
        if not pn:
            continue
        rows = art["topics"][slug]
        assert set(pn) == set(rows), slug                    # the artefact is stale for this topic: rebuild it
        for t, r in rows.items():
            if b.inn_stem(b.fold(t)):
                assert r["class"] == "ARM_NAME", (slug, t)


def test_a_pooled_row_naming_another_active_agent_is_refused():
    # arm names left the population rule, so a multi-arm trial now passes the screen; its pooled contrast must still be
    # OURS. 40544433 (cagrilintide-semaglutide vs placebo) entered the semaglutide-weight pool as -17.3 without this.
    import sys as _s
    _s.path.append(os.path.join(ROOT, "scripts"))
    import k_gap_counterfactual as cfm
    core, _ = cfm.build_with_held_sources("semaglutide-obesity-weight")
    prim = next(o for o in core["outcomes"] if o.get("primary"))
    ids = {t["id"] for t in prim["trials"]}
    assert "PMID 40544433" not in ids and "NCT04074161" not in ids, ids
    refused = {a["id"]: a for a in prim["declared_absent_trials"]}
    assert "another active agent 'cagrilintide'" in refused["PMID 40544433"]["reason"]


def test_other_agent_terms_exclude_our_drug_and_its_form_terms():
    from harness import pipeline
    o = pipeline._other_agent_terms("semaglutide-obesity-weight")
    assert "liraglutide" in o and "cagrilintide" in o and "oral semaglutide" not in o and "semaglutide" not in o
