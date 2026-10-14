"""K-gap phase 3 (open sources): only a licensed copy's deterministic find is admissible; an unlicensed (bronze / green)
copy's find waits on the Captain's ruling; only CC BY / CC0 text is model-eligible (D8)."""
import os
import sys
import hashlib
import json
from types import SimpleNamespace

import pytest

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


@pytest.fixture
def companion_readers(monkeypatch):
    """Synthetic replay records isolate the companion contract from acquisition and models."""
    import g1_trial_acquire as ta
    import g1_registry_fill as rf
    row = {"slug": "t", "label": "Synthetic companion", "pmid": "2", "population_pmid": "1",
           "blocker_now": "NO_OPEN_SOURCE:X", "companion_sources": []}
    src = {"origin": "UNPAYWALL", "doi": "10.1/x", "licence": "cc-by", "model_ok": True}
    answer = {"verdict": "FOUND", "source": "PMC_TEXT", "source_ref": row["pmid"], "measure": "RR",
              "events_t": 30, "n_t": 50, "events_c": 15, "n_c": 50,
              "effect": None, "lower": None, "upper": None,
              "quote": "Ovulation 30/50 (60%) 15/50 (30%)"}
    calls, populations = [], []

    def call(prompt, reader, purpose, digest):
        assert digest == hashlib.sha256(prompt).hexdigest()
        calls.append((prompt, reader))
        return {"state": "RAN_OK", "record_id": reader[0], "replay": dict(answer)}

    def gate(resp, held, cfg, slug):
        assert resp["quote"] in held["text"]
        assert held == {"aact": {}, "text": PROSE, "sha": hashlib.sha256(PROSE.encode()).hexdigest(),
                        "terms": ["ovulation"], "comp": "comparator", "pmid": "2", "reg": {}, "slug": "t",
                        "text_origin": src["origin"], "doi": src.get("doi"), "doi_licence": src.get("licence")}
        return "ADMITTED", {"row": SimpleNamespace(**{k: resp[k] for k in (
            "measure", "effect", "lower", "upper", "events_t", "n_t", "events_c", "n_c")})}

    monkeypatch.setattr(of, "_call", call)
    monkeypatch.setattr(rf, "_answer", lambda rec: rec["replay"])
    monkeypatch.setattr(ta, "gate", gate)
    monkeypatch.setattr(ta, "posted_population_short", lambda *args: populations.append(args))
    monkeypatch.setattr(ta, "comparator_pmid", lambda *args: "comparator")
    monkeypatch.setattr(ta, "tracker_file", lambda *args: None)
    monkeypatch.setattr(ta, "outcome_terms", lambda cfg: ["ovulation"])
    return row, src, answer, calls, populations


def test_PLANT_companion_model_read_admits_only_both_readers_agreeing(companion_readers):
    import g1_registry_fill as rf
    row, src, _answer, calls, populations = companion_readers
    out = of.companion_model_read("t", CFG, row, PROSE, src)
    assert out["decision"] == "MODEL_ADMITTED_BOTH_READERS"
    assert out["admitted_candidate"]["source_pmid"] == row["pmid"]
    assert out["admitted_candidate"]["population_pmid"] == row["population_pmid"]
    assert populations == [("t", "1", 100)]
    assert [r for _p, r in calls] == [rf.READER_A, rf.READER_B]
    assert calls[0][0] == calls[1][0]
    prompt = calls[0][0].decode("utf-8")
    assert of.COMPANION_NOTE in prompt
    evidence = json.loads(prompt.split("\n\n=== EVIDENCE ===\n", 1)[1])
    assert evidence["companion_publication_pmid"] == "2"
    assert evidence["trial_report_pmid"] == "1"
    # an UNPAYWALL copy is named by its DOI (the D8 guard then checks the DOI's licence); naming it by PMID made the
    # guard check the PMC copy and refuse (14 Oct, 32876697). This assertion first encoded the PMID form: the defect
    assert evidence["full_text"] == {"doi": "10.1/x", "licence": "cc-by",
                                     "sha256": hashlib.sha256(PROSE.encode()).hexdigest(),
                                     "chars": len(PROSE), "shown_chars": len(PROSE), "text": PROSE}
    assert out["evidence_sha256"] == hashlib.sha256(calls[0][0]).hexdigest()


def test_PLANT_companion_subpopulation_is_refused(monkeypatch, companion_readers):
    import g1_trial_acquire as ta
    row, src, *_ = companion_readers
    monkeypatch.setattr(ta, "posted_population_short", lambda *args: "Below randomised total")
    out = of.companion_model_read("t", CFG, row, PROSE, src)
    assert out["decision"] == "MODEL_FOUND_REFUSED_SUBPOPULATION"
    assert "admitted_candidate" not in out


def test_companion_model_never_called_without_cc_by(monkeypatch):
    from kgap import k_gap
    monkeypatch.setattr(of, "COMP_MODEL", True)
    monkeypatch.setattr(of, "_COMP", True)
    monkeypatch.setattr(k_gap, "unpaywall_text", lambda *args, **kwargs: {"state": "OK", "text": PROSE})
    monkeypatch.setattr(of, "typed_read", lambda *args: (None, None, None))

    def forbidden(*args):
        raise AssertionError("Unlicensed companion reached a model")

    monkeypatch.setattr(of, "companion_model_read", forbidden)
    row = {"label": "Synthetic companion", "pmid": "2", "population_pmid": "1",
           "class": "OPEN_CC_OTHER_REGEX_ONLY", "europepmc": {"doi": "10.1/x"},
           "unpaywall": {"license": "cc-by-nc"}}
    assert of.run_trial("t", CFG, row)["decision"] == "TYPED_NONE_NOT_MODEL_LICENSED"


def test_companion_model_refuses_unadjusted_cluster_counts(companion_readers):
    row, src, *_ = companion_readers
    row["blocker_now"] = "UNIT_OF_ANALYSIS_ADJUSTMENT_UNAVAILABLE:cluster_crossover"
    out = of.companion_model_read("t", CFG, row, PROSE, src)
    assert out["decision"] == "MODEL_FOUND_REFUSED_UNIT_OF_ANALYSIS"
    assert "admitted_candidate" not in out


@pytest.mark.parametrize("enabled", [False, True])
def test_companion_model_run_trial_is_opt_in(monkeypatch, companion_readers, enabled):
    from kgap import k_gap
    row, src, _answer, calls, _populations = companion_readers
    row.update({"class": "OPEN_CC_BY_OR_CC0", "europepmc": {"doi": src["doi"]},
                "unpaywall": {"license": src["licence"]}})
    monkeypatch.setattr(of, "_COMP", True)
    monkeypatch.setattr(of, "MODEL", False)
    monkeypatch.setattr(of, "COMP_MODEL", enabled)
    monkeypatch.setattr(of, "typed_read", lambda *args: (None, None, None))
    monkeypatch.setattr(k_gap, "unpaywall_text", lambda *args, **kwargs: {"state": "OK", "text": PROSE})
    out = of.run_trial("t", CFG, row)
    if enabled:
        assert out["decision"] == "MODEL_ADMITTED_BOTH_READERS"
        assert out["stage"] == "MODEL"
        assert out["phase"] == "3_OPEN:UNPAYWALL:COMPANION"
    else:
        assert out["decision"] == "TYPED_NONE_MODEL_ELIGIBLE"
        assert not calls


def test_PLANT_a_licence_refusal_is_typed_per_trial_never_a_crash(monkeypatch):
    # 14 Oct: mcl.LicenceRefused raised out of _call and killed the whole companion run on its first refused prompt
    from reproducible_ai import model_call_live as mcl

    def refuse(*_a, **_k):
        raise mcl.LicenceRefused("pre-call: prompt carries text whose copy is not marked open")
    monkeypatch.setattr(mcl, "call", refuse)
    monkeypatch.setattr(of, "CALLS", os.path.join(ROOT, "nonexistent_calls_index.json"))
    rec = of._call(b"prompt", ("A", "gpt-6-astra", "high"), "test", "sha")
    assert rec["state"] == "REFUSED_LICENCE" and rec["record_id"] is None
