"""Plants from the adversarial review of the enforcement gate (Codex lane R, 2026-09-21, model gpt-6-astra at xhigh):
every route by which a row the build refused on admission could still reach a rendered number, and every way the
gate's own reporting could read as safe. Each plant is a PROPERTY; none asserts a corpus number.

  R1  a trial screened IN on the served page that leaves the candidate set on a rebuild (screened out, or gone from
      the screening ledger) is refused by the honest ratchet unless acknowledged by name -- lane R's executed bypass:
      deleting one term from the topic's executable include list rebuilt glp1 with HARMONY screened out (X3) and the
      whole gate passed with no refusal naming it;
  R2  the known-missing sensitivity panel never re-pools an admission set-aside;
  R3  the invalidation 'known eligible missing' what-if never re-pools an admission set-aside, and records the
      conflict between the audit's eligibility claim and the structural screen instead;
  R4  a declared strand with a member the build does not admit is refused and its saved result withheld;
  R6  a pooled row stamped INADMISSIBLE is a refusal of the summary text and of the census, never exit 0;
  R7  a passing gate prints the scope of its pass;
  R8  a set-aside record names the predicate that failed;
  R9  an outcome whose every candidate was set aside on admission says so, never 'not extractable';
  A9  (lane V2, drop-the-rows round 2) a served outcome that VANISHES from the rebuilt review is a result change the
      honest ratchet refuses by name -- deleting a harm outcome from the topic config took PMID 31189511 out of a
      pool and only a marker count noticed.
"""
from __future__ import annotations

import copy
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from harness import admission, honest_ratchet, known_missing, invalidation, page, gate, pipeline  # noqa: E402
from harness.trial_family import cell  # noqa: E402
from test_admission_enforced import _family, _row, _outcome  # noqa: E402


def _review(screening_ids, decisions=None):
    decisions = decisions or {}
    return {"slug": "t", "outcomes": [], "screening": {"records": [
        {"id": i, "id_type": "pmid", "decision": decisions.get(i, "include"), "rule_id": "I1"} for i in screening_ids]}}


# ----------------------------------------------------------------------------- R1
def test_screening_ratchet_refuses_a_screened_in_record_that_left_silently():
    base = _review(["1", "2"])
    gone = _review(["1"])                                   # 2 vanished from the ledger
    out = _review(["1", "2"], {"2": "exclude"})             # 2 screened out on the rebuild
    for new, word in ((gone, "ABSENT_FROM_SCREENING"), (out, "exclude")):
        v = honest_ratchet.compare_screening(base, new, {}, "t")
        assert len(v) == 1 and "2" in v[0] and word in v[0] and "include" in v[0]
    assert honest_ratchet.compare_screening(base, base, {}, "t") == []
    assert honest_ratchet.compare_screening(base, _review(["1", "2", "3"]), {}, "t") == [], "a new record needs nothing"
    ack = {"screening_acknowledgements": [{"slug": "t", "record_id": "2", "old_decision": "include", "new_decision": "exclude",
                                           "reason": "protocol amendment 2026-09-21: comparator narrowed", "by": "Mahmood", "when_utc": "2026-09-21T00:00:00Z"}]}
    assert honest_ratchet.compare_screening(base, out, ack, "t") == []
    assert honest_ratchet.compare_screening(base, gone, ack, "t"), "an ack for 'exclude' does not cover 'absent from the ledger'"
    bad_ack = copy.deepcopy(ack); bad_ack["screening_acknowledgements"][0]["reason"] = ""
    assert honest_ratchet.compare_screening(base, out, bad_ack, "t"), "an ack without a reason is no ack"


def test_screening_ratchet_is_wired_into_check():
    import inspect
    src = inspect.getsource(honest_ratchet.check)
    assert "compare_screening(" in src


# ----------------------------------------------------------------------------- shared fixture: an admission set-aside
def _aside_row(pid="2"):
    kept, aside = admission.admit([_row(pid)], [_family("fam-" + pid, pid, state="UNKNOWN", code="INTERVENTION_CONTRAST_NOT_PROVEN")],
                                  {"name": "Primary event"})
    assert kept == [] and admission.is_set_aside(aside[0])
    return aside[0]


def _core_with_aside():
    pooled = [_row("1")]
    kept, _ = admission.admit(pooled, [_family("fam-1", "1")], {"name": "Primary event"})
    out = _outcome(kept)
    out["declared_absent_trials"] = [_aside_row("2")]
    out["admission_summary"] = admission.summary(out)
    return {"slug": "t", "outcomes": [out], "screening": {"records": [
        {"id": "1", "id_type": "pmid", "decision": "include", "rule_id": "I1", "reason": "RCT"},
        {"id": "2", "id_type": "pmid", "decision": "include", "rule_id": "I1", "reason": "RCT"}]}}


# ----------------------------------------------------------------------------- R2
def test_known_missing_never_repools_an_admission_set_aside():
    core = _core_with_aside()
    cands = known_missing._missing_candidates(core, {"known_eligible_missing": []})
    assert "2" not in {str(c.get("id") or c.get("trial") or "").replace("PMID ", "") for c in cands}


# ----------------------------------------------------------------------------- R3
def test_invalidation_does_not_repool_an_admission_set_aside_and_names_the_conflict():
    core = _core_with_aside()
    signals = {"known_eligible_missing": [{"trial": "PMID 2", "id": "2", "effect": 0.5, "ci_low": 0.3, "ci_high": 0.8, "scale": "RR",
                                           "source": "audit", "mechanism": "audit"}]}
    res = invalidation.assess(core, signals)
    text = json.dumps(res)
    codes = [r.get("code") for r in (res.get("reasons") or []) if isinstance(r, dict)]
    assert "audit_eligibility_vs_screen_conflict" in codes
    assert "missing_evidence_effect" not in text or "PMID 2" not in json.dumps([r for r in res.get("reasons") or [] if "missing_evidence_effect" in json.dumps(r)]), \
        "the set-aside tuple must not be re-pooled as a what-if"


# ----------------------------------------------------------------------------- R4
def test_strand_with_an_inadmissible_member_is_refused_and_its_saved_result_withheld():
    doc = {"slug": "t", "strands": [
        {"strand": "A", "name": "declared A", "event_process": "first", "members": [{"trial": "GOOD", "pmid": "1", "effect": 0.7, "scale": "RR"}],
         "pool": {"effect": 0.7, "ci_low": 0.5, "ci_high": 0.9, "k": 1, "tau2": 0}},
        {"strand": "B", "name": "declared B", "event_process": "recurrent", "members": [{"trial": "BAD", "pmid": "2", "effect": 0.42, "scale": "RR"}],
         "pool": {"effect": 0.42, "ci_low": 0.3, "ci_high": 0.6, "k": 1, "tau2": 0}}]}
    fams = [_family("fam-1", "1"), _family("fam-2", "2", state="UNKNOWN", code="REGISTRY_PARENT_UNRESOLVED", registry=False)]
    counts = admission.admit_strands(doc, fams)
    assert counts == {"strands": 2, "refused": 1}
    a, b = doc["strands"]
    assert "admission_refused" not in a and b["admission_refused"]["members"] and "BAD" in b["admission_refused"]["members"][0]
    html = page.render_strands_section(doc)
    assert "REFUSED on admission" in html and "0.42" not in html and "0.7" in html
    assert admission.admit_strands(doc, None)["refused"] == 2, "no ledger admits no strand member"


# ----------------------------------------------------------------------------- R6
def test_a_pooled_row_stamped_inadmissible_is_a_refusal_of_summary_and_census(tmp_path, monkeypatch):
    import admission_census as census_mod  # scripts/ on sys.path below
    row = _row("7"); row["admission_verdict"] = admission.verdict(row, None)      # INADMISSIBLE, yet left in trials
    out = _outcome([row]); out["admission_summary"] = admission.summary(out)
    assert out["admission_summary"]["pooled_with_a_verdict_other_than_admissible_or_migration"] == ["PMID 7"]
    assert admission.describe(out["admission_summary"]).startswith("REFUSAL")
    d = tmp_path / "docs" / "reviews" / "t"; d.mkdir(parents=True)
    (d / "review.json").write_text(json.dumps({"slug": "t", "outcomes": [out]}), encoding="utf-8")
    monkeypatch.setattr(census_mod, "ROOT", str(tmp_path))
    assert census_mod.main([]) == 1


# ----------------------------------------------------------------------------- R7
def test_a_passing_gate_prints_its_scope(tmp_path, monkeypatch, capsys):
    scope = gate.admission_scope(str(tmp_path))
    assert "P1_source_bytes" in scope and "NOT evaluated" in scope and "migration-state" in scope
    monkeypatch.setattr(gate, "gate_page", lambda d: (True, []))
    assert gate.main([str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "GATE PASS" in out and "NOT evaluated in-build" in out and "P14_missing_components_consistent" in out


# ----------------------------------------------------------------------------- R8
def test_set_aside_record_names_the_predicate_that_failed():
    row = _row("3", binding=None)
    kept, aside = admission.admit([row], [_family("fam-3", "3")], {"name": "Primary event"})
    assert kept == [] and aside[0]["reason_code"] == "P8_endpoint_bound" and aside[0]["state"] == admission.STATE_ENDPOINT_UNBOUND
    assert "P8" in aside[0]["reason"] and aside[0]["eligibility_state"] == "ELIGIBLE"
    assert admission.is_set_aside(aside[0])


# ----------------------------------------------------------------------------- R9
def test_an_outcome_whose_every_candidate_was_set_aside_says_so():
    from _families import eligible_by_construction
    rec = {"9": {"abstract": "Randomised trial. Death occurred in 10 of 100 (10%) vs 20 of 100 (20%) (RR 0.50, 95% CI 0.30 to 0.85)."}}
    spec = {"name": "Death", "keywords": ["death"], "estimand": "RR", "primary": True}
    inc = [{"id": "9", "id_type": "pmid"}]
    fams = eligible_by_construction(rec)
    ok = pipeline._build_outcome(spec, "efficacy", inc, rec, ["drug"], ["placebo"], family_nodes=fams)
    assert ok["trials"], "control: an eligible family pools"
    fams[0]["eligibility"] = cell(code="ENTRY_POPULATION_NOT_ESTABLISHED")
    o = pipeline._build_outcome(spec, "efficacy", inc, rec, ["drug"], ["placebo"], family_nodes=fams)
    assert not o["trials"] and o["result"].get("present") is False
    assert o["result"].get("set_aside_on_admission") == ["PMID 9"]
    assert "set aside on admission" in o["result"]["reason"] and "not extractable" not in o["result"]["reason"]



# ----------------------------------------------------------------------------- A9 (lane V2): an outcome that vanishes
def test_ratchet_refuses_a_served_outcome_that_vanished_from_the_rebuild_by_name():
    from harness import result_changes as rc
    base = {"slug": "t", "outcomes": [
        {"name": "Primary event", "primary": True, "result": {"k": 2, "estimate": 0.8, "ci_low": 0.7, "ci_high": 0.9, "scale": "RR"},
         "trials": [_row("1"), _row("2")]},
        {"name": "GI adverse events", "kind": "harm", "result": {"k": 1, "estimate": 1.3, "ci_low": 1.1, "ci_high": 1.5, "scale": "RR"},
         "trials": [_row("3")]}]}
    new = {"slug": "t", "outcomes": [copy.deepcopy(base["outcomes"][0])]}          # the harm outcome is gone
    v = honest_ratchet.compare_results(base, new, [], "t")
    assert len(v) == 1 and "outcome removed" in v[0] and "PMID 3" in v[0] and "GI adverse events" in v[0]
    notice = {"slug": "t", "outcome": "GI adverse events", "before": rc.result_tuple(base["outcomes"][1]["result"]), "after": rc.result_tuple(None),
              "left_pool": ["PMID 3"], "entered_pool": [], "reason": "outcome withdrawn from the protocol by amendment", "by": "Mahmood",
              "when_utc": "2026-09-21T00:00:00Z"}
    assert honest_ratchet.compare_results(base, new, [notice], "t") == []
    wrong = dict(notice, left_pool=[])
    assert honest_ratchet.compare_results(base, new, [wrong], "t"), "a notice that does not name the row that left is no notice"
    empty_base = {"slug": "t", "outcomes": [{"name": "Nothing pooled", "kind": "harm", "result": {"present": False}, "trials": []}]}
    assert honest_ratchet.compare_results(empty_base, {"slug": "t", "outcomes": []}, [], "t") == [], "an outcome that pooled nothing may go"


# ----------------------------------------------------------------------------- P1 (lane ACK): parity against a stale k
def test_parity_relation_reads_the_live_pool_never_the_hand_count_when_the_pool_is_empty():
    """A relation computed against a stale k is the container/contents confusion in another place: on the served
    module (38c04411) an emptied pool -- result without k, trials [] -- fell back to the hand our_k and kept
    noac at IDENTICAL_SET '4 of 4' with 0 rows (observed before the fix: served module IDENTICAL_SET/our_k 4,
    landing module SUBSET/our_k 0). The live pool's size is the k, 0 included; a pool cannot share more trials
    than it holds, so a hand shared_k above the live k is clamped and the clamp is recorded."""
    from harness import parity_relation as pr
    row = {"slug": "t", "status": "IDENTICAL_SET", "our_k": 4, "comparable_comparator_k": 4, "reason": "the 4 pivotal trials",
           "overlap": {"ours_k": 4, "theirs_k": 4, "shared_k": 4, "only_ours": [], "only_theirs": []}}
    comp = {"overlap": row["overlap"]}
    empty = {"slug": "t", "comparator": comp, "outcomes": [{"name": "Primary", "primary": True, "trials": [], "result": {"present": False}}]}
    rel = pr.compute(dict(row), empty)
    assert rel["our_k"] == 0 and rel["shared_k"] == 0 and rel["shared_k_clamped_to_pool"] is True
    assert rel["relation"] != "IDENTICAL_SET" and rel["hand_status_disagrees"] is True
    full = {"slug": "t", "comparator": comp, "outcomes": [{"name": "Primary", "primary": True, "trials": [_row(str(i)) for i in range(4)], "result": {"k": 4}}]}
    rel2 = pr.compute(dict(row), full)
    assert rel2["relation"] == "IDENTICAL_SET" and rel2["our_k"] == 4 and rel2["shared_k_clamped_to_pool"] is False, "control: a full pool is unchanged"
    two = {"slug": "t", "comparator": comp, "outcomes": [{"name": "Primary", "primary": True, "trials": [_row("1"), _row("2")], "result": {"k": 2}}]}
    rel3 = pr.compute(dict(row), two)
    assert rel3["our_k"] == 2 and rel3["shared_k"] == 2 and rel3["relation"] == "SUBSET"
