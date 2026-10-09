"""R6 P2 dpp4 hHF bindings (scripts/g1_r6_dpp4_hf.py): a binding is staged only when its span is verbatim in the
trial's own abstract (which carries the trial's NCT), every value is printed in the span, and BOTH recorded readers quote
that same clause with the same numbers. EXAMINE's 'first event' count is never staged."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_r6_dpp4_hf as H  # noqa: E402

T = H.TARGETS[1]                                                # CARMELINA
AB = {"abstract": "Background. " + T["span"] + ", the composite of cardiovascular death/hHF (HR, 0.94; 95% CI, 0.82-1.08).",
      "ncts": ["NCT01897532"]}


def test_the_carmelina_first_event_clause_verifies():
    assert H.verify(T, AB) is None


def test_PLANT_a_binding_whose_span_or_value_is_not_in_the_trials_own_abstract_is_refused():
    assert H.verify(T, dict(AB, ncts=["NCT00000000"])) == "ABSTRACT_DOES_NOT_CARRY_THE_TRIAL_NCT"
    assert H.verify(T, dict(AB, abstract=AB["abstract"].replace("0.74-1.08", "0.75-1.08"))) == "SPAN_NOT_VERBATIM"
    bad = dict(T, value=dict(T["value"], upper=1.09))
    assert H.verify(bad, AB).startswith("VALUE_NOT_IN_SPAN")
    assert H.verify(T, None) == "ABSTRACT_NOT_FETCHED"


def test_PLANT_a_reader_quoting_another_clause_never_confirms():
    other = {"state": "FOUND", "quote": "the composite of cardiovascular death/hHF (HR, 0.94; 95% CI, 0.82-1.08)",
             "hr": 0.94, "lower": 0.82, "upper": 1.08}
    assert H.gate(other, AB["abstract"], T) == "GATED_OTHER_CLAUSE"
    ok = {"state": "FOUND", "quote": T["span"], "hr": 0.90, "lower": 0.74, "upper": 1.08}
    assert H.gate(ok, AB["abstract"], T) == "GATED_AGREES"


def test_PLANT_examine_is_never_staged():
    ex = [t for t in H.TARGETS if t["label"] == "EXAMINE"][0]
    assert ex["state"] == "REFUSED_DEFINITION"


# ------------------------------------------------------------------------------------------- codex r6-dpp4-hf-r1
def test_PLANT_r1_1_swapped_arm_counts_never_agree():
    t = H.TARGETS[0]
    a = dict(state="FOUND", quote=t["span"], hr=0.60, lower=0.35, upper=1.05, events_t=33, n_t=2100, events_c=20, n_c=2092)
    assert H.gate(a, t["span"], t) == "GATED_DIFFERS"
    ok = dict(a, events_t=20, n_t=2092, events_c=33, n_c=2100)
    assert H.gate(ok, t["span"], t) == "GATED_AGREES"


def test_PLANT_r1_2_every_quoted_passage_must_be_our_clause():
    t = H.TARGETS[0]
    other = "All-cause mortality had an HR of 0.60 (95% CI 0.35, 1.05)."
    ab = t["span"] + " " + other
    a = dict(state="FOUND", quote="The hHF outcome occurred in 20/2092 patients\n" + other, hr=0.60, lower=0.35,
             upper=1.05, events_t=None, n_t=None, events_c=None, n_c=None)
    assert H.gate(a, ab, t) == "GATED_OTHER_CLAUSE"


def test_PLANT_r1_3_a_cited_papers_nct_never_identifies_the_trial(monkeypatch):
    from harness import http
    t = H.TARGETS[0]
    xml = ("<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>28893244</PMID><Article><Abstract><AbstractText>"
           + t["span"] + "</AbstractText></Abstract></Article></MedlineCitation><PubmedData><ReferenceList><Reference>"
           "<Citation>Another trial NCT01703208.</Citation></Reference></ReferenceList></PubmedData></PubmedArticle>"
           "</PubmedArticleSet>")
    monkeypatch.setattr(http, "get_text", lambda *a, **k: xml)
    ab = H._abstracts(["28893244"])["28893244"]
    assert "NCT01703208" not in ab["ncts"] and H.verify(t, ab) == "ABSTRACT_DOES_NOT_CARRY_THE_TRIAL_NCT"
