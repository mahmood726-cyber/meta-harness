"""Plant tests for the V1.1 GLP-1 discovery search (evidence/discovery/glp1-ra-mace-t2d): the deduplication guards
(amendment 3) and the registry-first CVOT criteria. Synthetic records only -- controls with known answers."""
import importlib.util, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "evidence", "discovery", "glp1-ra-mace-t2d")
sys.path.insert(0, D)


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(D, name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


screen = _load("screen")
rp = _load("registry_pass")


def _pub(pmid, ncts=()):
    return {"id": pmid, "databank_ncts": list(ncts), "abstract_ncts": [], "nct": ""}


def _reg(nct, refs):
    return {"id": nct, "reference_pmids": list(refs), "reference_types": {p: "RESULT" for p in refs}}


def _groups(tr):
    return {tuple(t["ncts"]): set(t["members"]) for t in tr}


def test_pooled_publication_cited_by_two_registrations_does_not_merge_them():
    # the amendment-3 defect: a review cited as RESULT by both trials chained them into one "trial"
    pm = [_pub("1"), _pub("2"), _pub("9")]
    ct = [_reg("NCT00000001", ["1", "9"]), _reg("NCT00000002", ["2", "9"])]
    tr, _, _ = screen.trials(pm, ct, [])
    g = _groups(tr)
    assert ("NCT00000001",) in g and ("NCT00000002",) in g, g
    assert "PMID:1" in g[("NCT00000001",)] and "PMID:2" in g[("NCT00000002",)]
    assert not any("PMID:9" in m and len(n) for n, m in g.items()), "the shared citation must link no registration"


def test_publication_naming_one_nct_links_and_naming_two_links_neither():
    pm = [_pub("5", ["NCT00000005"]), _pub("6", ["NCT00000005", "NCT00000006"])]
    ct = [_reg("NCT00000005", []), _reg("NCT00000006", [])]
    tr, _, _ = screen.trials(pm, ct, [])
    g = _groups(tr)
    assert g[("NCT00000005",)] == {"NCT:NCT00000005", "PMID:5"}
    assert g[("NCT00000006",)] == {"NCT:NCT00000006"}


def _f(**kw):
    base = {"conditions": ["Diabetes Mellitus, Type 2"], "title": "", "official_title": "", "eligibility_excerpt": "",
            "interventions": ["DRUG: Semaglutide", "DRUG: Placebo"], "arm_labels": [], "allocation": "RANDOMIZED",
            "primary_outcomes": ["Time to first MACE | CV death, non-fatal MI, non-fatal stroke"]}
    base.update(kw)
    return base


def test_cvot_candidate_needs_all_five_criteria():
    assert rp.criteria(_f())["cvot_candidate"]
    assert not rp.criteria(_f(interventions=["DRUG: Semaglutide", "DRUG: Insulin glargine"]))["cvot_candidate"]
    assert not rp.criteria(_f(allocation="NON_RANDOMIZED"))["cvot_candidate"]
    assert not rp.criteria(_f(primary_outcomes=["Change in HbA1c | week 26"]))["cvot_candidate"]
    assert not rp.criteria(_f(conditions=["Obesity"]))["cvot_candidate"]


def test_primary_outcome_mi_and_stroke_together_count_but_either_alone_does_not():
    assert rp.criteria(_f(primary_outcomes=["Composite of myocardial infarction and stroke |"]))["O_primary_cv"]
    assert not rp.criteria(_f(primary_outcomes=["Fatal or non-fatal stroke |"]))["O_primary_cv"]


def test_a_code_named_glp1_drug_is_missed_by_the_registered_I_test():
    # FREEDOM-CVO names its drug 'ITCA 650', never exenatide -- the disclosed filter miss, pinned so it stays visible
    assert not rp.criteria(_f(interventions=["DRUG: ITCA 650", "DRUG: ITCA placebo"]))["I_glp1"]


def test_registered_P_test_is_blind_to_exclusion_criteria_as_disclosed():
    # SELECT / SURMOUNT-MMO: T2D appears only as an exclusion yet P passes -- a known, disclosed defect of the
    # registered filter; if someone fixes it, this test must be rewritten with the report, not silently deleted
    f = _f(conditions=["Obesity"], eligibility_excerpt="Exclusion Criteria: * History of type 1 or type 2 diabetes")
    assert rp.criteria(f)["P_t2d"]
