"""K-gap phase 3 (open sources): only a licensed copy's deterministic find is admissible; an unlicensed (bronze / green)
copy's find waits on the Captain's ruling; only CC BY / CC0 text is model-eligible (D8)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_open_fill as of  # noqa: E402

CFG = {"primary_outcome": {"name": "Ovulation", "keywords": ["ovulation rate", "ovulation"], "estimand": "RR"},
       "include": {"population_any": ["polycystic"]},
       "intervention_terms": ["metformin"], "comparator_terms": ["placebo"]}
PROSE = ("Table 2. Outcomes\n Metformin Placebo\n Ovulation 30/50 (60%) 15/50 (30%)\n"
         "Weight loss reported in both arms.")


def test_licence_classes():
    assert of.licence_class("cc-by") == of.licence_class("CC BY") == of.licence_class("cc0") == "CC_BY_OR_CC0"
    assert of.licence_class("cc-by-nc-nd") == of.licence_class("cc-by-nc") == "CC_OTHER"
    assert of.licence_class(None) == of.licence_class("other-oa") == "NONE"


def test_screening_blocked_trials_are_queued_not_acquired():
    assert of.screening_blocked({"blocker_now": "SCREENER_ERROR:COMPARATOR_WORDING"})
    assert of.screening_blocked({"blocker_now": "INSUFFICIENT_RECORD:BLINDING_NOT_STATED"})
    assert not of.screening_blocked({"blocker_now": "NO_OPEN_SOURCE:OUTCOME_NOT_IN_SOURCE"})


def test_prose_reader_is_deterministic_and_arm_ordered(monkeypatch):
    import g1_trial_acquire as ta
    monkeypatch.setattr(ta, "outcome_row_terms", lambda cfg: ["ovulation"])
    rr, span, reader = of.typed_read(PROSE, "UNPAYWALL", CFG)
    assert reader == "typed_counts" and rr == {"events_t": 30, "n_t": 50, "events_c": 15, "n_c": 50}
    flipped = PROSE.replace(" Metformin Placebo", " Placebo Metformin")
    assert of.typed_read(flipped, "UNPAYWALL", CFG)[0] == {"events_t": 15, "n_t": 50, "events_c": 30, "n_c": 50}
    assert of.typed_read("Ovulation 30/50 (60%) 15/50 (30%)", "UNPAYWALL", CFG)[0] is None   # no arm header: no pick


def test_PLANT_an_unlicensed_copys_find_is_pending_never_admissible(monkeypatch):
    import g1_trial_acquire as ta
    from kgap import k_gap
    monkeypatch.setattr(ta, "outcome_row_terms", lambda cfg: ["ovulation"])
    monkeypatch.setattr(ta, "posted_population_short", lambda *a: None)
    monkeypatch.setattr(k_gap, "unpaywall_text", lambda *a, **k: {"state": "OK", "text": PROSE})
    base = {"label": "X 2004", "pmid": "1", "class": "OPEN_NO_LICENCE_REGEX_ONLY", "blocker_now": "NO_OPEN_SOURCE:X",
            "europepmc": {"doi": "10.1/x"}, "unpaywall": {"license": None}}
    assert of.run_trial("t", CFG, base)["decision"] == "TYPED_FOUND_PENDING_RULING"
    cc = dict(base, unpaywall={"license": "cc-by-nc"})
    assert of.run_trial("t", CFG, cc)["decision"] == "TYPED_FOUND_ADMISSIBLE"
    monkeypatch.setattr(k_gap, "unpaywall_text", lambda *a, **k: {"state": "OK", "text": "No counts here. Ovulation."})
    assert of.run_trial("t", CFG, dict(base, unpaywall={"license": "cc-by"}))["decision"] == "TYPED_NONE_MODEL_ELIGIBLE"
    assert of.run_trial("t", CFG, dict(base, unpaywall={"license": "cc-by-nc"}))["decision"] == \
        "TYPED_NONE_NOT_MODEL_LICENSED"


def test_PLANT_cluster_design_counts_are_never_admissible(monkeypatch):
    # SMART / SALT (cluster crossover): the tracker refuses unadjusted counts (UNIT_OF_ANALYSIS_ADJUSTMENT_UNAVAILABLE);
    # phase 3 found SMART's whole-trial counts in its author manuscript and must not call them admissible (13 Oct)
    import g1_trial_acquire as ta
    from kgap import k_gap
    monkeypatch.setattr(ta, "outcome_row_terms", lambda cfg: ["ovulation"])
    monkeypatch.setattr(ta, "posted_population_short", lambda *a: None)
    monkeypatch.setattr(k_gap, "unpaywall_text", lambda *a, **k: {"state": "OK", "text": PROSE})
    r = {"label": "S", "pmid": "1", "class": "OPEN_CC_OTHER_REGEX_ONLY", "europepmc": {"doi": "10.1/x"},
         "unpaywall": {"license": "cc-by-nc"}, "blocker_now": "UNIT_OF_ANALYSIS_ADJUSTMENT_UNAVAILABLE:cluster_crossover"}
    assert of.run_trial("t", CFG, r)["decision"] == "TYPED_FOUND_REFUSED_UNIT_OF_ANALYSIS"


def test_PLANT_an_html_copys_table_is_read_by_the_table_reader(monkeypatch):
    # 13 Oct: after the HTML layout fix the CoDEX page kept its tables, but the runner only tried table_tuple on PMC text
    import g1_trial_acquire as ta
    from kgap import k_gap
    page = ("<p>Results.</p><table><tr><th>Outcome</th><th>Drug A (n = 200)</th><th>Control B (n = 200)</th></tr>"
            "<tr><td>Ovulation rate</td><td>40 (20.0)</td><td>50 (25.0)</td></tr></table>")
    monkeypatch.setattr(ta, "outcome_row_terms", lambda cfg: ["ovulation rate", "ovulation"])
    rr, _span, reader = of.typed_read(k_gap._html_text(page), "UNPAYWALL", CFG)
    assert reader == "table_tuple" and rr == {"events_t": 40, "n_t": 200, "events_c": 50, "n_c": 200}
