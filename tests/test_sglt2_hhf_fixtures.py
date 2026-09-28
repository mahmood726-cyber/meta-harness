"""SGLT2 HHF-in-CVOTs fixtures, 2026-09-28: PROGRAMME vs TRIALS, witnessed eligibility, EMPA-REG Table 2 relayed (plants)."""
import copy
import json
import os

from harness import family_invariant as fi, fetch, pipeline, trial_family as tf

ROOT = pipeline.ROOT
SLUG = "sglt2-primary-prevention-hf"
_R = {}


def _rv():
    if not _R:
        cfg = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
        _R["rv"] = pipeline.build_review_core(SLUG, cfg, fetch.ensure(cfg, ""), "test")
    return _R["rv"]


def _o(rv, name):
    return next(o for o in rv["outcomes"] if o["name"] == name)


def _fam(rv, fid):
    return next(f for f in rv["trial_families"] if f["family_id"] == fid)


def test_the_canvas_program_is_one_input_representing_two_trials():
    rv = _rv()
    ch = rv["family_count_chain"]
    assert (ch["analysis_inputs"], ch["trials_represented"]) == (4, 5)
    assert ch["programmes"] == [{"family_id": "PMID:28605608", "programme_id": "CANVAS-Program", "label": "CANVAS Program",
                                 "constituents": ["NCT01032629", "NCT01989754"], "contributing": True}]
    f = _fam(rv, "PMID:28605608")
    assert f["identity_anchor"] == "PROGRAMME" and f["eligibility"]["state"] == "ELIGIBLE"
    # eligibility is DERIVED from each constituent's own registry rows, never declared
    assert f["eligibility"]["span"]["basis"] == "PROGRAMME_CONSTITUENTS"
    assert [(c["acronym"], c["eligibility"]["state"]) for c in f["programme"]["constituents"]] == \
        [("CANVAS", "ELIGIBLE"), ("CANVAS-R", "ELIGIBLE")]
    hhf = _o(rv, "Hospitalization for heart failure")
    assert len(hhf["trials"]) == 4 and round(hhf["result"]["estimate"], 4) == 0.6956   # the served pool is unchanged
    row = next(t for t in hhf["trials"] if "28605608" in str(t["id"]))
    assert row["family_identity_state"] == "PROGRAMME" and row["programme"]["constituents"] == ["NCT01032629", "NCT01989754"]
    assert "4 analysis inputs represent 5 trials" in tf.count_sentence(ch)


def test_a_programme_pooled_alongside_its_own_constituent_is_blocked():
    rv = copy.deepcopy(_rv())
    assert fi.problems(rv) == []
    rv["trial_families"].append({"family_id": "NCT01032629", "identity_basis": {"registry_ids": ["NCT01032629"]}, "reports": []})
    _o(rv, "Hospitalization for heart failure")["trials"].append({"id": "NCT01032629", "family_id": "NCT01032629"})
    kinds = [p["kind"] for p in fi.problems(rv)]
    assert "PROGRAMME_WITH_CONSTITUENT" in kinds


def test_a_programme_with_an_unheld_constituent_stays_unresolved():
    f = {"family_id": "PMID:1", "identity_basis": {"registry_ids": []}, "eligibility": {}}
    decl = {"programme_id": "P", "label": "P", "constituents": ["NCT01032629", "NCT99999999"]}
    reg = tf.load_registry(ROOT, SLUG)
    cfg = dict(json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8")), slug=SLUG)
    tf.attach_programme(f, decl, {"NCT01032629": reg["NCT01032629"]}, cfg, cfg["include"]["intervention_any"],
                        cfg["include"]["comparator_any"])
    assert f["eligibility"]["state"] == "UNKNOWN"
    assert f["eligibility"]["absence_code"] == "PROGRAMME_CONSTITUENT_NOT_ESTABLISHED"


def test_empa_reg_and_declare_are_eligible_on_source_witnesses_nothing_contributes_unestablished():
    rv = _rv()
    assert rv["family_count_chain"]["contributing_without_structural_eligibility"] == []
    er, dc = _fam(rv, "NCT01131676"), _fam(rv, "NCT01730534")
    assert er["eligibility"]["span"]["contrast_basis"] == "SOURCE_WITNESS"
    assert dc["eligibility"]["span"]["population_basis"] == "SOURCE_WITNESS"
    # plant: the SAME double-dummy family without a declaration stays unproven (the witness, not the code, admits it)
    node = {k: er[k] for k in ("family_id", "registry_design", "population", "arms", "randomised_contrasts")}
    cfg = dict(json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8")), slug="no-such-topic")
    assert tf.screen_family(node, cfg)["absence_code"] == "INTERVENTION_CONTRAST_NOT_PROVEN"


def test_empa_reg_table2_is_relayed_typed_and_never_admitted():
    rv = _rv()
    want = {"Adverse events": "4,230/4,687", "Genital infection": "301/4,687", "Diabetic ketoacidosis": "4/4,687"}
    for outcome, value in want.items():
        o = _o(rv, outcome)
        assert not any("26378978" in str(t["id"]) for t in o.get("trials") or [])      # never admitted
        row = next(t for t in o["declared_absent_trials"] if "26378978" in str(t["id"]))
        assert row["result_status"]["state"] == "REPORTED_UNRESOLVED"                   # never 'not reported'
        assert value in row["relayed_not_held"]["value"]
        assert "DECLARE" not in row["reason"]                                           # the copied reason is gone
        assert "never summed" in row["reason"]


def test_declare_genital_refusal_stays_its_outcome_is_narrower():
    rv = _rv()
    row = next(t for t in _o(rv, "Genital infection")["declared_absent_trials"] if "30415602" in str(t["id"]))
    assert row["reason_code"] == "REFUSED_ON_EVIDENCE" and "narrower serious-or-discontinuation" in row["reason"]
    assert "led to discontinuation of the regimen or that were considered to be serious adverse events" in \
        (row.get("source_span") or row.get("verbatim_span") or "")
