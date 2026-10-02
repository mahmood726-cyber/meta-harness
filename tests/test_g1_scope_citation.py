"""PLANTS for the eligible DENOMINATOR (Mahmood 3 Oct): between two tracker runs ELIGIBLE fell 335 -> 298 while matched
rose 71 -> 75. A trial may leave 'eligible' only as a NAMED difference that cites a rule ID AND the source span (the
record's own words) establishing it; otherwise it stays eligible as an open gap. These tests fail if any comparator
trial is non-eligible without both, on synthetic objects and on every committed tracker file."""
import glob
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
import g1_tracker as gt  # noqa: E402
import k_gap_exclusion_audit as au  # noqa: E402

SPAN = {"field": "title", "text": "Effect of enalapril on survival."}


def _o(named=(), gaps=(), pool=("A",), others=("B",), n_elig=None):
    trials = [{"label": t, "in_our_pool": True} for t in pool] + [{"label": t, "in_our_pool": False} for t in others]
    nd = list(named)
    return {"slug": "t", "trials": trials, "named_differences": nd, "open_gaps": list(gaps),
            "N_comparator_trials": len(trials), "k_matched": len(pool),
            "N_eligible": len(trials) - len(nd) if n_elig is None else n_elig}


def test_a_trial_dropped_from_the_denominator_without_a_name_fails():
    assert gt.scope_citation_violations(_o()) == ["B: not matched, not an open gap, not named -- dropped from the denominator"]
    assert gt.scope_citation_violations(_o(gaps=["B"])) == []


def test_a_named_difference_needs_a_rule_id_and_a_span():
    no_span = {"trial": "B", "kind": "PROTOCOL_SCOPE_DIFFERENCE", "rule_id": "X3", "protocol_rule": "include..."}
    assert gt.scope_citation_violations(_o(named=[no_span])) == ["B: non-eligible without a source span"]
    no_rule = dict(no_span, rule_id=None, span=SPAN, span_source="PMID 1 record title")
    assert gt.scope_citation_violations(_o(named=[no_rule])) == ["B: non-eligible without a cited rule ID"]
    ok = dict(no_span, span=SPAN, span_source="PMID 1 record title")
    assert gt.scope_citation_violations(_o(named=[ok])) == []


def test_the_eligible_count_must_equal_N_minus_named():
    ok = {"trial": "B", "kind": "PROTOCOL_SCOPE_DIFFERENCE", "rule_id": "X3", "span": SPAN, "span_source": "PMID 1"}
    assert gt.scope_citation_violations(_o(named=[ok], n_elig=0)) == ["N_eligible 0 != comparator N 2 - named 1"]


def test_the_table_refuses_a_topic_with_an_uncited_exclusion(tmp_path, monkeypatch):
    g = tmp_path / "g1"
    g.mkdir()
    (g / "t.json").write_text(json.dumps(_o()), encoding="utf-8")
    monkeypatch.setattr(gt, "G1_DIR", str(g))
    monkeypatch.setattr(gt, "served_topics", lambda: ["t"])
    with pytest.raises(SystemExit, match="non-eligible without a cited rule"):
        gt.table()


def test_an_unspanned_lane_exclusion_is_demoted_to_an_open_gap(monkeypatch):
    # SOLOIST-WHF: the lane named it X3 'not an SGLT2 inhibitor'; its abstract names SGLT2 -> no span -> eligible again
    monkeypatch.setattr(gt, "exclusion_audit_span", lambda s, p: None)
    monkeypatch.setattr(gt, "exclusion_audit_class", lambda s, p: ("SCREENER_ERROR", "INTERVENTION_ONLY_IN_ABSTRACT"))
    o = _o(named=[{"trial": "B", "kind": "PROTOCOL_SCOPE_DIFFERENCE", "rule_id": "X3", "pmid": "1"}])
    gt.cite_or_demote(o, "t")
    assert o["named_differences"] == [] and o["open_gaps"] == ["B"] and o["N_eligible"] == 2
    assert o["trials"][1]["blocker"] == "SCOPE_UNCITED:X3 (audit SCREENER_ERROR:INTERVENTION_ONLY_IN_ABSTRACT)"
    assert gt.scope_citation_violations(o) == []


def test_g1_status_reports_how_many_left_the_denominator():
    ok = {"trial": "B", "kind": "PROTOCOL_SCOPE_DIFFERENCE", "rule_id": "X3", "protocol_rule": "r", "span": SPAN,
          "span_source": "PMID 1"}
    o = _o(named=[ok])
    o.update(same_trials={"verdict": {"verdict": "AGREE"}}, open_gaps=[])
    o["trials"][0].update(route="PRIMARY")
    s = gt.g1_status(o)
    assert s["excluded_by_scope"]["n"] == 1 and s["excluded_by_scope"]["of_comparator_N"] == 2
    o["named_differences"][0].pop("span")
    assert "DIVERGENCES_NAMED" in gt.g1_status(o)["unmet"]


# ---- the audit's span: the record must STATE the excluding fact
INC = {"intervention_any": ["sacubitril", "LCZ696"], "intervention_in_title": True,
       "comparator_any": ["enalapril"], "population_any": ["heart failure"]}


def test_a_background_sentence_is_not_a_span_for_another_intervention():
    rec = {"title": "Heart failure outcomes in the elderly.",
           "abstract": "Few randomized controlled trials have been conducted in this population. Results were mixed."}
    assert au.span_of(rec, au.THIS_STUDY_RANDOMISED, ("abstract",)) is None
    rec["abstract"] += " This was a randomized double-blind trial, comparing placebo with perindopril."
    sp = au.span_of(rec, au.THIS_STUDY_RANDOMISED, ("abstract",))
    assert sp["text"] == "This was a randomized double-blind trial, comparing placebo with perindopril."


def test_a_sentence_never_ends_at_vs():
    rec = {"title": "Medical vs. surgical ovulation induction: a randomized trial."}
    assert au.span_of(rec, au.TITLE_STUDY_STATED, ("title",))["text"] == rec["title"]


def test_a_record_naming_our_intervention_never_gets_an_other_intervention_span(monkeypatch):
    # Liu 2004 (metformin 15498183): generic title, metformin randomised in the abstract -> not 'another agent'
    monkeypatch.setattr(au, "decide", lambda rec, inc: {"decision": "exclude", "rule_id": "X3",
                                                        "reason": "the randomised intervention is not [...]"})
    rec = {"id": "1", "title": "[Clinical study on heart failure].",
           "abstract": "Patients were randomly divided into LCZ696 or enalapril groups."}
    cls, sub, base = au.classify(rec, {"include": INC})
    assert (cls, sub) == ("INSUFFICIENT_RECORD", "OTHER_INTERVENTION_OR_FORM_RANDOMISED_NO_SPAN")
    rec = {"id": "2", "title": "Effect of enalapril on survival in heart failure.",
           "abstract": "Patients were randomly assigned to receive placebo or enalapril."}
    cls, sub, base = au.classify(rec, {"include": INC})
    assert cls == "TRUE_SCOPE_DIFFERENCE" and base["span"]["text"] == rec["title"]


# ---- corpus-wide: every committed tracker file, every named difference (n of N reported on failure)
def _files():
    return sorted(glob.glob(os.path.join(ROOT, "outputs", "k_gap", "g1", "*.json")))


def test_every_committed_topic_cites_rule_and_span_for_every_non_eligible_trial():
    bad = {}
    n_named = 0
    for p in _files():
        o = json.load(open(p, encoding="utf-8"))
        n_named += len(o.get("named_differences") or [])
        v = gt.scope_citation_violations(o)
        if v:
            bad[o["slug"]] = v
    assert not bad, f"{len(bad)} of {len(_files())} topics; {bad}"
    assert n_named > 0


def test_every_protocol_scope_span_is_verbatim_in_the_held_record():
    miss, n = [], 0
    for p in _files():
        o = json.load(open(p, encoding="utf-8"))
        for d in o.get("named_differences") or []:
            if d.get("kind") != "PROTOCOL_SCOPE_DIFFERENCE":
                continue
            n += 1
            if not gt.span_is_verbatim(o["slug"], d.get("pmid"), d.get("span")):
                miss.append(f"{o['slug']}::{d.get('trial')}")
    assert not miss, f"{len(miss)} of {n} spans not verbatim: {miss}"
