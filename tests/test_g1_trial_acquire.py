"""scripts/g1_trial_acquire.py gates (the 2 Oct one-primary-source decision) and g1_tracker.acquired_merge: a model's
answer is admitted only when a deterministic gate finds it in the trial's own source; never from the comparator; a scope
claim only under a protocol rule that is SET (iv-iron's design_double_blind is false: EFFECT-HF's 'open-label' names
nothing)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402
import g1_trial_acquire as ga  # noqa: E402

CFG = {"primary_outcome": {"name": "Heart-failure hospitalization", "estimand": "RR", "population": "intention-to-treat",
                           "keywords": ["hospitalization for worsening heart failure"]},
       "include": {"design_double_blind": False, "population_any": ["heart failure"]}}
REG = {"outcomes": {"1": {"title": "Number of Hospitalizations for Heart Failure", "type": "SECONDARY",
                          "time_frame": "12 months"}},
       "groups": {"1": [{"group": "g1", "count": 297, "n": 1532}, {"group": "g2", "count": 332, "n": 1533}]},
       "analyses": [], "group_titles": {}}
TEXT = ("Results. Hospitalization for worsening heart failure occurred in 12/80 patients assigned to ferric carboxymaltose "
        "and in 20/81 patients assigned to placebo during follow-up.")


def _held(text="", reg=None):
    return {"text": text, "sha": "x", "terms": ["hospitalization for worsening heart failure"], "comp": "39727669",
            "aact": {"NCT03037931": {"state": "POSTED", "_reg": reg, "snapshot": {"id": "AACT 2026-08-30"}}} if reg else {}}


def _resp(**kw):
    base = {"verdict": "FOUND", "source": "AACT", "source_ref": "NCT03037931", "aact_outcome_id": "1", "measure": "COUNTS",
            "events_t": 297, "n_t": 1532, "events_c": 332, "n_c": 1533, "effect": None, "lower": None, "upper": None,
            "quote": "297 1532 332 1533", "scope_rule_key": None, "scope_span": None}
    base.update(kw)
    return base


def test_posted_participant_counts_are_admitted():
    v, adm = ga.gate(_resp(), _held(reg=REG), CFG, "iv-iron-hfref-hosp")
    assert v == "ADMITTED" and adm["kind"] == "AACT"


def test_counts_that_are_not_the_posted_ones_are_refused():
    v, _ = ga.gate(_resp(events_t=290), _held(reg=REG), CFG, "iv-iron-hfref-hosp")
    assert v == "REFUSED:TUPLE_NOT_THE_POSTED_RESULT"


def test_text_counts_need_a_verbatim_quote_holding_every_number():
    ok = _resp(source="PMC_TEXT", source_ref="28701470", events_t=12, n_t=80, events_c=20, n_c=81,
               quote="occurred in 12/80 patients assigned to ferric carboxymaltose and in 20/81 patients")
    assert ga.gate(ok, _held(TEXT), CFG, "iv-iron-hfref-hosp")[0] == "ADMITTED"
    assert ga.gate(dict(ok, quote="occurred in 12 of 80 patients"), _held(TEXT), CFG, "x")[0] == \
        "REFUSED:QUOTE_NOT_VERBATIM_IN_WHOLE_TEXT"
    assert ga.gate(dict(ok, n_c=88), _held(TEXT), CFG, "x")[0] == "REFUSED:NUMBERS_NOT_IN_QUOTE"


def test_the_comparator_is_never_a_source_and_a_scope_rule_must_be_set():
    assert ga.gate(_resp(source="PMC_TEXT", source_ref="39727669"), _held(TEXT), CFG, "x")[0] == \
        "REFUSED:SOURCE_IS_COMPARATOR"
    sc = _resp(verdict="SCOPE_DIFFERENCE", scope_rule_key="design_double_blind", scope_span="assigned to placebo")
    assert ga.gate(sc, _held(TEXT), CFG, "x")[0] == "REFUSED:SCOPE_RULE_NOT_SET_IN_PROTOCOL"


def test_an_admitted_row_matches_the_trial_and_promotes_a_secondary_single(monkeypatch):
    row = {"label": "HEART-FID [11]", "verdict": "ADMITTED", "record_id": "mc-x",
           "admitted": {"kind": "AACT", "source": "AACT 2026-08-30 NCT03037931 outcome 1", "span": "s", "quote": "q",
                        "value": {"measure": "RR", "effect": None, "lower": None, "upper": None, "events_t": 297,
                                  "n_t": 1532, "events_c": 332, "n_c": 1533}}}
    monkeypatch.setattr(gt, "acquired_rows", lambda slug: {"HEART-FID [11]": row})
    cr = {"effect": None, "lower": None, "upper": None, "events_t": 297, "n_t": 1532, "events_c": 332, "n_c": 1533,
          "measure": "RR"}
    x = {"label": "HEART-FID [11]", "in_our_pool": False, "route": "UNVERIFIED", "g1_countable": False,
         "comparator_row": cr}
    from collections import Counter
    routes, pairs = Counter({"UNVERIFIED": 1}), []
    assert gt.acquired_merge("iv-iron-hfref-hosp", [x], routes, pairs, "39727669") == ["HEART-FID [11]"]
    assert x["route"] == "PRIMARY" and gt.is_matched(x) and x["agreement_with_comparator_row"] == "AGREE"
    assert len(pairs) == 1 and routes == Counter({"PRIMARY": 1})
    named = dict(x, route="UNVERIFIED", scope_difference={"kind": "X"})
    assert gt.acquired_merge("iv-iron-hfref-hosp", [named], None, None, "39727669") == []


def test_comparator_counts_that_are_posted_events_are_named(monkeypatch):
    det = {"NCT02937454": {"measurements": {
        "ev": [{"title": "HF Hospitalisations", "units": "Events", "param_value": "217"},
               {"title": "HF Hospitalisations", "units": "Events", "param_value": "294"}],
        "pp": [{"title": "HF Hospitalisations", "units": "Participants", "param_value": "142"},
               {"title": "HF Hospitalisations", "units": "Participants", "param_value": "178"}]}}}
    monkeypatch.setattr(ga, "aact_detail", lambda ncts: det)
    f = ga.comparator_counts_are_events({"events_t": 217, "n_t": 558, "events_c": 294, "n_c": 550}, ["NCT02937454"])
    assert f["finding"] == "COMPARATOR_COUNTS_ARE_POSTED_EVENTS" and f["units"] == ["Events"]
    # the participant outcome's own counts are never named
    assert ga.comparator_counts_are_events({"events_t": 142, "n_t": 558, "events_c": 178, "n_c": 550},
                                           ["NCT02937454"]) is None


def test_posted_counts_for_a_subpopulation_are_refused(monkeypatch):
    # SMART (NCT02444988) posts its medical-ICU subset, 2735 + 2646 = 5381; its report randomised 15,802 adults
    rec = {"abstract": "METHODS: In a pragmatic, cluster-randomized, multiple-crossover trial conducted in five intensive "
                       "care units, we assigned 15,802 adults to receive saline or balanced crystalloids. RESULTS: ..."}
    monkeypatch.setattr(gt, "held_record", lambda slug, pmid: rec)
    short = ga.posted_population_short("balanced", "29485925", 2735 + 2646)
    assert short["randomised_total"] == 15802 and short["posted_total"] == 5381
    assert ga.posted_population_short("balanced", "29485925", 15802) is None
    monkeypatch.setattr(gt, "held_record", lambda slug, pmid: {"abstract": "We studied adults in ICUs."})
    assert ga.posted_population_short("balanced", "29485925", 5381) is None        # no stated total: never a mismatch


def test_a_screened_count_is_never_the_randomised_total(monkeypatch):
    rec = {"abstract": "FINDINGS: Between March 21, 2017, and July 30, 2019, 1525 patients were screened, of whom 1132 "
                       "patients were randomly assigned to study groups."}
    monkeypatch.setattr(gt, "held_record", lambda slug, pmid: rec)
    assert ga.posted_population_short("iv-iron", "33197395", 558 + 550) is None      # 1108 vs 1132 randomised: >= 90%
    assert ga.posted_population_short("iv-iron", "33197395", 600)["randomised_total"] == 1132


def test_a_structured_table_row_under_column_ns_is_a_typed_tuple():
    q = ("Outcome | Balanced Crystalloids (N = 7942) | Saline (N = 7860) | Adjusted Odds Ratio (95% CI)\n"
         "Major adverse kidney event within 30 days — no. (%) | 1139 (14.3) | 1211 (15.4) | 0.90 (0.82 to 0.99)\n"
         "In-hospital death before 30 days — no. (%) | 818 (10.3) | 875 (11.1) | 0.90 (0.80 to 1.01)")
    r = {"events_t": 818, "n_t": 7942, "events_c": 875, "n_c": 7860}
    assert ga.typed_match_table(q, r, ["death", "mortality"])["route"] == "TABLE_ROW_WITH_COLUMN_N"
    assert ga.typed_match_table(q, dict(r, events_t=875, events_c=818), ["death"]) is None     # arm order matters
    assert ga.typed_match_table(q, dict(r, n_t=7860, n_c=7942), ["death"]) is None
    bad = q.replace("818 (10.3)", "818 (12.3)")                                                  # % must corroborate
    assert ga.typed_match_table(bad, r, ["death"]) is None
    assert ga.typed_match_table(q, r, ["stroke"]) is None                                         # row must name the outcome


def test_a_text_that_is_not_openly_licensed_never_enters_a_prompt(monkeypatch):
    # SMART (PMC5846085) is an NIH author manuscript: the prompt is stored in the committed record, so it may not carry it
    monkeypatch.setattr(ga, "text_evidence", lambda pmid, terms: ("full text " * 50, "full text " * 50, "sha"))
    monkeypatch.setattr(ga, "aact_evidence", lambda ncts: {})
    monkeypatch.setattr(ga, "meta_evidence", lambda slug, label: [])
    t = {"slug": "x", "label": "SMART", "pmid": "29485925", "ncts": []}
    monkeypatch.setattr(ga, "pmc_licence", lambda pmid: "NOT_OPEN")
    ev, held = ga.evidence(t, CFG, "0")
    assert ev["full_text"]["state"] == "HELD_NOT_OPEN_LICENSED" and "text" not in ev["full_text"] and held["text"]
    monkeypatch.setattr(ga, "pmc_licence", lambda pmid: "CC")
    assert "text" in ga.evidence(t, CFG, "0")[0]["full_text"]


def test_the_deterministic_table_reader_refuses_an_ambiguous_table():
    text = ("Outcome | A (N = 100) | B (N = 100)\nDeath at 30 days — no. (%) | 10 (10.0) | 20 (20.0)\n"
            "Death at 90 days — no. (%) | 15 (15.0) | 25 (25.0)\n")
    assert ga.table_tuple(text, ["death"], None) is None                       # two rows, no timepoint to choose
    assert ga.table_tuple(text, ["death"], "90 days")[1]["events_t"] == 15


def test_plant_a_table_row_from_a_copy_not_open_is_refused_not_kept(tmp_path, monkeypatch):
    text = ("Outcome | Balanced (N = 7942) | Saline (N = 7860)\n"
            "In-hospital death before 30 days — no. (%) | 818 (10.3) | 875 (11.1)\n")
    prop = tmp_path / "prop.json"
    prop.write_text(json.dumps({"runs": {"x|SMART": {"slug": "balanced-crystalloids-vs-saline-mortality", "label": "SMART",
                                                      "pmid": "29485925", "ncts": [], "record_id": None,
                                                      "state": "WITHHELD_NOT_OPEN_TEXT"}}}), encoding="utf-8")
    monkeypatch.setattr(ga, "PROP", str(prop))
    monkeypatch.setattr(ga, "ACQ_DIR", str(tmp_path / "acq"))
    monkeypatch.setattr(ga, "tracker_file", lambda slug, ref: {"comparator_pmid": "0", "trials": []})
    monkeypatch.setattr(ga, "evidence", lambda t, cfg, comp: ({}, {"text": text, "sha": "s", "terms": ["death"],
                                                                     "comp": "0", "pmid": "29485925", "aact": {}}))
    for lic, want in (("NOT_OPEN", "REFUSED:HELD_COPY_NOT_OPEN"), ("PMC_AUTHOR_MANUSCRIPT", "ADMITTED")):
        monkeypatch.setattr(ga, "pmc_copy", lambda pmid, lic=lic: {"pmcid": "PMC5846085", "url": "u", "licence": lic,
                                                                    "statement": "s"})
        row = ga.replay(["balanced-crystalloids-vs-saline-mortality"], "ref")["balanced-crystalloids-vs-saline-mortality"][0]
        assert row["verdict"] == want
        assert (row.get("source_copy") or (row.get("admitted") or {}).get("source_copy"))["licence"] == lic
