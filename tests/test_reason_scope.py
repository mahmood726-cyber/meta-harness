"""REASON_NOT_DISPROVED fixtures: the evidence must answer the refusal's OWN reason, and a component or a severity grade is never the
category (pass 15; independent adjudication by codex A3 of every verdict the PASS-14 auditor still called REASON_FALSE_VALUE_HELD).
Two were FALSE on the SERVED page (pinned at 6260e70c) -- plants that fire on the served page:
  23992601  SAVOR HHF, ENDPOINT_UNBOUND 'disproved' by the very span the refusal weighed (R2);
  26973849  S. boulardii any-AE, ENDPOINT_UNBOUND 'disproved' by its own span with the markup removed (R2).
Three were false positives of the typed-identity auditor BEFORE pass 15 (never served; the served page says WRONG_KIND / TRUE / TRUE),
fixed in the same change; their pre-fix behaviour is recorded by the lane's corpus measurement, and synthetic plants for the same rules
are below and in test_adversarial_findings.py:
  32720823  'Diarrhea occurred in two patients in each group' for 'Gastrointestinal adverse effects' -- a component, named only by the
            search keyword 'diarrh' (S2);
  22449293  'Major bleeding ... 26 vs 52' for 'Any bleeding' -- a severity-restricted subset (S1);
  33080017  a POPULATION_MISMATCH refusal 'disproved' by an SAE count that says nothing about population (R3)."""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import evidence_identity as ei, pipeline, reason_audit  # noqa: E402

SERVED = "6260e70c"
CASES = {  # key: (slug, outcome, trial, a field the fixed verdict must name, served page called it FALSE)
    "gi_component": ("colchicine-postop-af", "Gastrointestinal adverse effects", "32720823", "outcome", False),
    "major_is_not_any": ("doac-vte-recurrence", "Any bleeding", "22449293", "definition", False),
    "savor_same_span": ("dpp4-mace-t2d", "Hospitalization for heart failure", "23992601", "reason_scope", True),
    "boulardii_same_span": ("probiotics-aad-prevention", "Any adverse events", "26973849", "reason_scope", True),
    "population_code": ("tocilizumab-covid19-mortality", "Serious adverse events", "33080017", "population", False),
}
SERVED_FALSE = sorted(k for k, c in CASES.items() if c[4])


def _served(slug):
    out = subprocess.run(["git", "-C", ROOT, "show", f"{SERVED}:docs/reviews/{slug}/review.json"], capture_output=True, check=True).stdout
    return json.loads(out)


def _case(key):
    slug, name, trial = CASES[key][:3]
    rv = _served(slug)
    o = next(x for x in rv["outcomes"] if x["name"] == name)
    row = next(a for a in o["declared_absent_trials"] if reason_audit.canonical_trial_id(a.get("id") or a.get("label")) == trial)
    topic = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
    spec = {**({s.get("name"): s for s, _ in pipeline._outcome_specs(topic)}.get(name) or {}), "target_population": rv.get("question")}
    recs = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))
    return o, row, spec, reason_audit.sources_by_trial(slug, recs, ROOT).get(trial, [])


@pytest.mark.parametrize("key", SERVED_FALSE)
def test_PLANT_the_served_page_called_the_refusal_false(key):
    _, row, _, _ = _case(key)
    assert row["reason_code_audit"]["verdict"] == "REASON_FALSE_VALUE_HELD"


@pytest.mark.parametrize("key", sorted(CASES))
def test_the_evidence_does_not_answer_the_refusal(key):
    o, row, spec, srcs = _case(key)
    v = reason_audit.audit_reason_row(o, row, srcs, spec)
    assert v["verdict"] == "REASON_NOT_DISPROVED", v.get("detail")
    named = " ".join(m for c in v.get("candidates") or [] for m in c["mismatch"])
    if CASES[key][4]:                        # the served audit cited a span: that chain, judged alone, is not disproof either
        chain = reason_audit.audit_cited_chain(o, row, row["reason_code_audit"]["source_span"], spec)
        assert chain["chain_verdict"] == "REASON_NOT_DISPROVED"
        named += " " + " ".join(chain["fails_on"])
    if CASES[key][3] != "reason_scope":      # R2 cases may now also fail earlier fields; R2 itself is tested directly below
        assert CASES[key][3] in named, (CASES[key][3], named[:600])


def test_corroborated_counts_answer_a_not_corroborated_refusal_and_bare_counts_do_not():
    code = "COUNTS_PRESENT_NOT_CORROBORATED"
    with_n = {"span": "7/78 vs 1/73", "role": "OUTCOME_COUNT", "effect_measure": "COUNTS",
              "arms": [{"events": 7, "n": 78}, {"events": 1, "n": 73}]}
    bare = {"span": "31 patients (18.23%) developed AAD compared to 53 patients (31.17%)", "role": "OUTCOME_COUNT",
            "effect_measure": "COUNTS", "arms": [{"events": 31, "n": None}, {"events": 53, "n": None}]}
    assert reason_audit._answers_reason(code, with_n, {}) is None                  # per-arm denominators corroborate
    assert reason_audit._answers_reason(code, bare, {}) is not None                # the counts the refusal already conceded
    assert reason_audit._answers_reason("EXTRACTION_NOT_PERFORMED", bare, {}) is None     # scope applies only to its own reason


@pytest.mark.parametrize("key", SERVED_FALSE)
def test_R2_the_span_the_refusal_already_weighed_never_answers_it(key):
    _, row, _, _ = _case(key)
    cited = {"span": row["reason_code_audit"]["source_span"], "role": "EFFECT_ESTIMATE"}
    assert reason_audit._answers_reason(row.get("reason_code") or row.get("state"), cited, row) is not None


def test_severity_grades_restrict_and_non_major_is_the_complement():
    assert ei.definition_of("Major bleeding was observed in 26 patients", "Any bleeding") == "RESTRICTED"
    assert ei.definition_of("Major bleeding was observed in 26 patients", "Major bleeding") == "AS_NAMED"
    assert ei.definition_of("major adverse cardiovascular events occurred in 336", "Major adverse cardiovascular events") == "AS_NAMED"
    assert ei.definition_of("clinically relevant non-major bleeding in 40 vs 38", "Major bleeding") == "RESTRICTED"
