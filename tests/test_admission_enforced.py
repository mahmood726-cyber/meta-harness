"""Plants for the enforcement gate (2026-09-21).

Until this landing the build computed the family-eligibility evidence BEFORE pooling and never read it: the
admission verdict (bundle predicates P5 family eligible / P8 endpoint bound) was computed AFTER the build, from
the built review.json, and no harness module read it -- 53 of 87 pooled primary rows were INADMISSIBLE on P5 while
the page said "existing pooling membership is preserved". These tests assert PROPERTIES of one implementation
(harness/admission.py) read at the pooling convergence point and checked by the page gate:

  * a row whose family eligibility is not ELIGIBLE is not pooled, and the TRIAL is not erased: it stays on the
    outcome as a set-aside candidate extraction with the tuple it carried, the absence code, and the recovery;
  * a row whose family is ELIGIBLE and whose endpoint is bound is pooled and stamped ADMISSIBLE;
  * an unbound_legacy row is the named MIGRATION state: pooled, counted separately, never silently ADMISSIBLE;
  * a build handed no family ledger admits nothing (the gate is on by default; absence of evidence is not a pass);
  * the page gate refuses a page that pools an unstamped row, a row whose stamp disagrees with the families the
    page itself carries, or a page from which a screened-in row VANISHED (neither pooled nor set aside);
  * a summary over nothing evaluated reads NOT_EVALUATED, never "0 inadmissible";
  * the vocabulary is the bundle's (no second vocabulary for one decision).

Every plant was run against 38c04411 before the fix and observed to FAIL there (see the landing commit message);
no test asserts a corpus number.
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from harness import pipeline, trial_family  # noqa: E402
from harness.gate import gate_page  # noqa: E402
from harness.synth import CI_PROVENANCE as _CI_PROV  # noqa: E402
from test_gate import _build as _build_page, _review_core  # noqa: E402

SLUG = "glp1-ra-mace-t2d"
PRIMARY = "3-point major adverse cardiovascular events"


# ----------------------------------------------------------------------------- synthetic families and rows
def _family(fid, report_id, state="ELIGIBLE", code=None, registry=True):
    """The smallest family node the eligibility function reads: identity basis, reports, held records, cell."""
    span = {"design": {"allocation": "RANDOMIZED"}, "population": {"quote": "adults with the condition"}}
    if state == "ELIGIBLE":
        el = trial_family.cell("ELIGIBLE", span)
    elif state == "INELIGIBLE":
        el = trial_family.cell("INELIGIBLE", {"source": "AACT.designs", "quote": "Allocation: NON_RANDOMIZED"})
    else:
        el = trial_family.cell(code=code or "ENTRY_POPULATION_NOT_ESTABLISHED")
    return {"family_id": fid, "identity_basis": {"registry_ids": ["NCT0000" + fid[-1]] if registry else [],
                                                 "primary_report_ids": [], "fallback_report_ids": []},
            "reports": [{"report_id": report_id, "role": "PRIMARY", "retrieved_via": ["pubmed#1"]}],
            "source_records": [{"id": report_id, "id_type": "pmid"}],
            "eligibility": el, "outcome_status": [], "randomised_contrasts": [], "arms": [], "population": {},
            "aliases": {"acronym": []}, "lifecycle": {}, "poolability": [], "is_trial_family": registry}


def _row(pid, binding="named_endpoint_resolved_to_definition_span"):
    return {"label": "T" + pid[-1], "id": "PMID " + pid, "effect": 0.8, "ci_low": 0.7, "ci_high": 0.9, "scale": "RR",
            "source": "pub", "endpoint_binding": binding, "endpoint_admissibility": "EXACT_TARGET",
            "verified": "verified"}


def _outcome(rows):
    return {"name": "Primary event", "kind": "efficacy", "primary": True, "estimand": "RR",
            "result": {"k": len(rows), "estimate": 0.8, "ci_low": 0.7, "ci_high": 0.9, "scale": "RR", "tau2": 0.0,
                       "pi_low": 0.6, "pi_high": 1.0, "ci_provenance": _CI_PROV},
            "trials": rows, "declared_absent_trials": []}


# ----------------------------------------------------------------------------- the build reads the decision
def test_build_sets_aside_a_row_whose_family_eligibility_is_not_established():
    """P5 FAIL by UNKNOWN: the candidate extraction is rejected, the trial is not."""
    from harness import admission
    rows = [_row("1"), _row("2")]
    fams = [_family("fam-1", "1"), _family("fam-2", "2", state="UNKNOWN", code="REGISTRY_PARENT_UNRESOLVED", registry=False)]
    kept, aside = admission.admit(rows, fams, {"name": "Primary event"})
    assert [t["id"] for t in kept] == ["PMID 1"]
    assert [a["id"] for a in aside] == ["PMID 2"], "the set-aside row must keep its trial id on the outcome"
    a = aside[0]
    assert a["absent_kind"] == "machine_absent" and a["state"] == admission.STATE_NOT_ESTABLISHED
    assert a["absence_code"] == "REGISTRY_PARENT_UNRESOLVED"
    assert a["candidate_tuple"] == {"effect": 0.8, "ci_low": 0.7, "ci_high": 0.9, "scale": "RR"}, "the tuple it carried stays visible"
    assert a["admission_verdict"]["final"] == "INADMISSIBLE" and a["admission_verdict"]["failing"] == ["P5_family_eligible"]
    assert "recovery" in a and a["recovery"]
    assert kept[0]["admission_verdict"]["final"] == "ADMISSIBLE"


def test_build_refuses_on_evidence_a_row_whose_family_is_ineligible():
    """P5 FAIL by INELIGIBLE (a positive finding with a span): refused on evidence, span carried, trial kept."""
    from harness import admission
    kept, aside = admission.admit([_row("3")], [_family("fam-3", "3", state="INELIGIBLE")], {"name": "Primary event"})
    assert kept == [] and aside[0]["id"] == "PMID 3"
    assert aside[0]["absent_kind"] == "refused_on_evidence" and aside[0]["state"] == admission.STATE_INELIGIBLE
    assert aside[0]["eligibility_span"]


def test_build_keeps_the_migration_state_pooled_and_named():
    """An unbound_legacy row whose family is ELIGIBLE is the bundle's MIGRATION state: pooled, counted separately."""
    from harness import admission
    kept, aside = admission.admit([_row("4", binding="unbound_legacy")], [_family("fam-4", "4")], {"name": "Primary event"})
    assert aside == [] and kept[0]["admission_verdict"]["final"] == "MIGRATION_STATE_UNBOUND_LEGACY"
    assert kept[0]["admission_verdict"]["failing"] == ["P8_endpoint_bound"]
    s = admission.summary(_outcome(kept))
    assert s["state"] == "EVALUATED" and s["migration_state_rows"] == ["PMID 4"]


def test_build_handed_no_family_ledger_admits_nothing():
    """ON by default: a build that has no family ledger cannot establish P5 and pools nothing."""
    from harness import admission
    kept, aside = admission.admit([_row("5")], None, {"name": "Primary event"})
    assert kept == [] and aside[0]["id"] == "PMID 5"
    assert aside[0]["admission_verdict"]["predicates"]["P5_family_eligible"]["eligibility_state"] is None


def test_the_producer_route_reads_the_decision_on_the_real_inputs():
    """The real route (pipeline.outcome_inputs + the real _build_outcome) on committed glp1 inputs: flipping ONE
    family's eligibility to INELIGIBLE removes exactly that trial from the pool, keeps it on the outcome as a
    refusal, and the restored ledger gives the control pool back. Paired shape; no number asserted."""
    from harness import fetch
    config = json.load(open(os.path.join(pipeline.ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
    records = fetch.ensure(config, "")
    inp = pipeline.outcome_inputs(SLUG, config, records)
    spec = next(s for s, k in pipeline._outcome_specs(config) if s.get("name") == PRIMARY)
    control = pipeline.build_outcome_from_inputs(inp, spec, "efficacy", SLUG)
    pooled = [t for t in control["trials"] if t["admission_verdict"]["final"] == "ADMISSIBLE"]
    assert pooled, "control has at least one ADMISSIBLE row to plant on"
    victim = pooled[0]
    by_report = {r["report_id"]: f for f in inp["family_nodes"] for r in f["reports"]}
    mutated = copy.deepcopy(inp["family_nodes"])
    fam = next(f for f in mutated if f["family_id"] == victim["family_id"])
    fam["eligibility"] = trial_family.cell("INELIGIBLE", {"source": "plant", "quote": "synthetic ineligibility"})
    changed = pipeline.build_outcome_from_inputs(inp, spec, "efficacy", SLUG, family_nodes=mutated)
    assert victim["id"] not in [t["id"] for t in changed["trials"]]
    assert victim["id"] in [a["id"] for a in changed["declared_absent_trials"]], "the trial stays on the outcome"
    assert changed["result"]["k"] == control["result"]["k"] - 1
    assert sorted(t["id"] for t in changed["trials"]) == sorted(t["id"] for t in control["trials"] if t["id"] != victim["id"])
    restored = pipeline.build_outcome_from_inputs(inp, spec, "efficacy", SLUG, family_nodes=inp["family_nodes"])
    assert sorted(t["id"] for t in restored["trials"]) == sorted(t["id"] for t in control["trials"])
    assert restored["result"] == control["result"]
    assert by_report  # the plant used the real ledger's own report map


# ----------------------------------------------------------------------------- the page gate refuses
def _page(tmp, rows, fams, stamp=True, screening_ids=None):
    """A synthetic served page: the review carries its own trial_families copy and (optionally) stamped rows."""
    from harness import admission
    rev = _review_core()
    kept, aside = (admission.admit(copy.deepcopy(rows), fams, {"name": "Primary event"}) if stamp else (rows, []))
    out = _outcome(kept)
    out["declared_absent_trials"] = aside
    if stamp:
        out["admission_summary"] = admission.summary(out)
    rev["outcomes"][0] = out
    rev["trial_families"] = fams
    ids = screening_ids if screening_ids is not None else [r["id"].replace("PMID ", "") for r in rows]
    # the served corpus accounts for every screened-in record on EVERY outcome (0 of 97 outcomes have a
    # screened-in record that is neither pooled nor declared absent); the fixture's harm outcome does the same
    rev["outcomes"][1]["declared_absent_trials"] = [{"label": "T" + i[-1], "id": "PMID " + i, "absent_kind": "machine_absent",
                                                     "state": "NO_OUTCOME_DATA_IN_SOURCE", "reason": "no counts"} for i in ids]
    if stamp:
        rev["outcomes"][1]["admission_summary"] = admission.summary(rev["outcomes"][1])
    rev["screening"] = {"records": [{"id": i, "id_type": "pmid", "decision": "include", "rule_id": "I1", "reason": "RCT"} for i in ids]}
    return _build_page(tmp, rev)


def _admission_reasons(d):
    ok, reasons = gate_page(d)
    return [r for r in reasons if "admission" in r.lower()]


def test_gate_refuses_a_page_that_pools_an_unstamped_row_whose_family_is_not_eligible():
    """RED on today's pages: no stamp AND the page's own families say UNKNOWN. The refusal names the trial,
    the family, the state and the absence code, and prints the scope of what it checked."""
    with tempfile.TemporaryDirectory() as tmp:
        d = _page(tmp, [_row("1")], [_family("fam-1", "1", state="UNKNOWN", code="INTERVENTION_CONTRAST_NOT_PROVEN")], stamp=False)
        reasons = _admission_reasons(d)
        assert reasons, "a page pooling a row with unestablished family eligibility must be refused"
        text = " ".join(reasons)
        for needle in ("PMID 1", "fam-1", "UNKNOWN", "INTERVENTION_CONTRAST_NOT_PROVEN", "P5", "not evaluated"):
            assert needle in text, needle


def test_gate_refuses_a_stamped_row_whose_stamp_disagrees_with_the_page_families():
    """A stamp is not trusted: ADMISSIBLE on the row while the page's own families read UNKNOWN is refused."""
    with tempfile.TemporaryDirectory() as tmp:
        fams = [_family("fam-1", "1")]
        d = _page(tmp, [_row("1")], fams)
        rev = json.load(open(os.path.join(d, "review.json"), encoding="utf-8"))
        rev["trial_families"][0]["eligibility"] = trial_family.cell(code="INSUFFICIENT_PICD_EVIDENCE")
        d = _build_page(tmp, rev)
        assert any("stamp" in r and "PMID 1" in r for r in _admission_reasons(d))


def test_gate_refuses_a_page_from_which_a_screened_in_row_vanished():
    """Not satisfiable by dropping rows: a record screened IN that is neither pooled nor set aside is a refusal."""
    with tempfile.TemporaryDirectory() as tmp:
        fams = [_family("fam-1", "1"), _family("fam-2", "2")]
        d = _page(tmp, [_row("1"), _row("2")], fams)
        rev = json.load(open(os.path.join(d, "review.json"), encoding="utf-8"))
        rev["outcomes"][0]["trials"] = [t for t in rev["outcomes"][0]["trials"] if t["id"] != "PMID 2"]
        rev["outcomes"][0]["result"]["k"] = 1
        d = _build_page(tmp, rev)
        reasons = _admission_reasons(d)
        assert any("vanished" in r and "2" in r for r in reasons), reasons


def test_gate_accepts_a_consistent_stamped_page_and_names_its_scope():
    """Control: stamped, consistent, nothing vanished -> the admission check adds no refusal."""
    with tempfile.TemporaryDirectory() as tmp:
        d = _page(tmp, [_row("1"), _row("2", binding="unbound_legacy")], [_family("fam-1", "1"), _family("fam-2", "2")])
        assert _admission_reasons(d) == []
        from harness import gate
        assert gate.check_admission_enforced(d) == []


# ----------------------------------------------------------------------------- limits and vocabulary
def test_summary_over_nothing_evaluated_reads_not_evaluated_not_zero():
    from harness import admission
    s = admission.summary(_outcome([]))                # nothing reached the pool: a named state, not a zero
    assert s["state"] == "NO_CANDIDATE_ROWS"
    assert "no candidate row" in admission.describe(s).lower()
    assert "0 inadmissible" not in admission.describe(s).lower()
    s2 = admission.summary(_outcome([_row("9")]))     # a pooled row with no stamp: NOT evaluated, never "0 inadmissible"
    assert s2["state"] == "NOT_EVALUATED" and s2["unstamped_rows"] == ["PMID 9"]
    assert "not evaluated" in admission.describe(s2).lower()
    assert "0 inadmissible" not in admission.describe(s2).lower()


def test_scope_names_what_is_and_is_not_evaluated_in_build():
    from harness import admission
    sc = admission.SCOPE
    assert set(sc["evaluated_in_build"]) == {"P5_family_eligible", "P8_endpoint_bound"}
    assert set(sc["evaluated_in_build"]).isdisjoint(sc["not_evaluated_in_build"])
    assert len(sc["evaluated_in_build"]) + len(sc["not_evaluated_in_build"]) == 14
    for o in (_outcome([]), _outcome([_row("9")])):
        text = admission.describe(admission.summary(o))
        assert "P1_source_bytes" in text and "bundle" in text.lower(), "every state prints what is not evaluated in-build"


def test_vocabulary_is_the_bundles():
    """One decision, one vocabulary: the verdict words and predicate ids the build stamps are the words the served
    bundle defines (docs/reviews/<slug>/BUNDLE.json, predicate_definitions / final)."""
    from harness import admission
    p = os.path.join(pipeline.ROOT, "docs", "reviews", SLUG, "BUNDLE.json")
    if not os.path.isfile(p):
        pytest.skip("no served bundle to compare against (skip is visible, not a pass)")
    b = json.load(open(p, encoding="utf-8"))
    finals = {r["admission"]["final"] for r in b["verification_rows"]}
    assert finals <= admission.VERDICTS
    bundle_predicates = {k for r in b["verification_rows"] for k in r["admission"]["predicates"]}
    assert set(admission.SCOPE["evaluated_in_build"]) <= bundle_predicates
    assert set(admission.SCOPE["not_evaluated_in_build"]) <= bundle_predicates | {"P10_estimand_evidence"}


# ----------------------------------------------------------------------------- the certified map's EMPTY state
# Found 2026-09-22 by lanes E and E2b, ONE DAY AFTER this gate landed: `scripts/build_families.py <slug> --offline`
# emits a schema-valid {"families": []} for a real topic (empty records, held registry), `build_topic` regenerates the
# page's families from ingredients but never refreshes the certified file, and the guard below read the empty map as
# "no certified data" and SKIPPED the comparison -- so the full gate PASSED a page whose non-empty-but-incomplete
# control it REFUSES. An empty container is not an absence of evidence about the container; a check that an empty
# input switches off is a check that can be switched off.
def _certified_root(tmp, slug, families, write=True):
    """A ROOT whose cache/<slug>/families.json holds exactly `families` (compact form). write=False: no file."""
    root = os.path.join(tmp, "certroot")
    os.makedirs(os.path.join(root, "cache", slug), exist_ok=True)
    if write:
        with open(os.path.join(root, "cache", slug, "families.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"schema_version": 1, "format": "compact", "families": families}, f)
    return root


def _compact(fid, state="ELIGIBLE"):
    return {"family_id": fid, "eligibility": {"state": state}}


def _admission_with_root(monkeypatch, d, root):
    from harness import gate
    monkeypatch.setattr(gate, "ROOT", root)
    return gate.check_admission_enforced(d)


def test_gate_refuses_when_the_certified_family_map_is_EMPTY_while_the_page_pools_families(monkeypatch):
    """PLANT (observed PASSING on b25027e3 before this fix): a certified families.json holding zero families is a
    CERTIFICATION THAT NOTHING IS CERTIFIED. It must never silently disable the page-vs-certified comparison."""
    with tempfile.TemporaryDirectory() as tmp:
        d = _page(tmp, [_row("1")], [_family("fam-1", "1")])
        rev = json.load(open(os.path.join(d, "review.json"), encoding="utf-8"))
        root = _certified_root(tmp, rev["slug"], [])
        reasons = _admission_with_root(monkeypatch, d, root)
        assert reasons, "an empty certified family map must not pass a page that pools families"
        text = " ".join(reasons).lower()
        assert "certified" in text and ("0 famil" in text or "zero famil" in text or "empty" in text), text


def test_gate_refuses_an_incomplete_certified_map_the_same_way_it_always_did(monkeypatch):
    """CONTROL (refuses before and after the fix): a NON-empty certified map that omits the pooled row's family.
    If this ever passes, the plant above proves nothing -- the two differ only by the map being empty."""
    with tempfile.TemporaryDirectory() as tmp:
        d = _page(tmp, [_row("1")], [_family("fam-1", "1")])
        rev = json.load(open(os.path.join(d, "review.json"), encoding="utf-8"))
        root = _certified_root(tmp, rev["slug"], [_compact("some-other-family")])
        reasons = _admission_with_root(monkeypatch, d, root)
        assert any("absent from the certified" in r for r in reasons), reasons


def test_gate_states_that_the_certified_comparison_was_not_evaluated_when_no_file_exists(monkeypatch):
    """A missing certified file is NOT the same state as an empty one and must not read as agreement: the check
    says so in its scope rather than passing silently."""
    with tempfile.TemporaryDirectory() as tmp:
        d = _page(tmp, [_row("1")], [_family("fam-1", "1")])
        rev = json.load(open(os.path.join(d, "review.json"), encoding="utf-8"))
        root = _certified_root(tmp, rev["slug"], [], write=False)
        reasons = _admission_with_root(monkeypatch, d, root)
        from harness import gate
        monkeypatch.setattr(gate, "ROOT", root)
        scope = gate.admission_scope(d)
        assert reasons == [], reasons
        assert "not evaluated" in scope.lower() and "certified" in scope.lower(), scope


def test_gate_refuses_a_malformed_certified_map_instead_of_crashing(monkeypatch):
    """PLANT (observed CRASHING on b25027e3 with AttributeError): the file parses as JSON but is a top-level list.
    A check that raises is a check that cannot report; the states of this file are absent / malformed / empty /
    incomplete / complete, and only 'absent' may pass -- as NOT_EVALUATED, said out loud in the scope."""
    with tempfile.TemporaryDirectory() as tmp:
        d = _page(tmp, [_row("1")], [_family("fam-1", "1")])
        rev = json.load(open(os.path.join(d, "review.json"), encoding="utf-8"))
        root = os.path.join(tmp, "certroot-list")
        os.makedirs(os.path.join(root, "cache", rev["slug"]), exist_ok=True)
        with open(os.path.join(root, "cache", rev["slug"], "families.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump([{"family_id": "fam-1"}], f)          # a LIST, not an object
        reasons = _admission_with_root(monkeypatch, d, root)
        assert any("not an object" in r and "refusal" in r for r in reasons), reasons
