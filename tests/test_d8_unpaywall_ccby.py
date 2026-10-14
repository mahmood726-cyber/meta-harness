"""D8: Unpaywall prompt text must use the shared CC BY / CC0 rule."""
import base64
import json

import pytest

from reproducible_ai import record_licence as rl
from scripts import g1_licence, g1_trial_acquire


@pytest.mark.parametrize("licence, permitted", [
    ("cc-by-nc", False),
    ("cc-by-nc-nd", False),
    ("cc-by-sa", False),
    ("cc-by-nd", False),
    ("cc-by", True),
    ("cc0", True),
    ("cc-by-4.0", True),
    ("CC BY 4.0", True),
    ("cc0-1.0", True),
    ("cc-by-nc-4.0", False),
    ("cc-by-sa-3.0-igo", False),
])
def test_record_unpaywall_prompt_licence(licence, permitted):
    prompt = "=== EVIDENCE ===\n" + json.dumps({"doi": "10.1/x", "text": "x" * (rl.MIN_TEXT + 1)})
    record = {"record_id": "d8-licence-plant",
              "prompt": {"b64": base64.b64encode(prompt.encode("utf-8")).decode("ascii")}}
    problems = rl.record_problems(record, dlic={"10.1/x": licence}, lic={}, reg={})
    if permitted:
        assert problems == []
    else:
        assert problems, f"Restricted Unpaywall licence {licence} was admitted"


@pytest.mark.parametrize("licence, permitted", [("cc-by-nc", False), ("cc-by", True)])
def test_repo_open_unpaywall(monkeypatch, licence, permitted):
    monkeypatch.setattr(rl, "pmid_doi", lambda pmid: "10.1/x")
    monkeypatch.setattr(rl, "doi_licences", lambda: {"10.1/x": licence})
    assert g1_licence.repo_open("12345", "UNPAYWALL") is permitted


@pytest.mark.parametrize("licence, permitted", [
    ("cc-by-nc", False), ("cc-by", True), ("cc0", True), (None, False),
])
def test_unpaywall_promptable(licence, permitted):
    assert g1_trial_acquire._unpaywall_promptable(licence) is permitted


@pytest.mark.parametrize("licence, permitted", [("cc-by-nc", False), ("cc-by", True)])
def test_evidence_unpaywall_prompt_licence(monkeypatch, licence, permitted):
    # Synthetic held text and identifiers; no source files, services, or model calls.
    whole = "Mortality is the outcome in this synthetic test fixture. " * 100
    trial = {"pmid": "d8-test-pmid", "ncts": [], "slug": "d8-test", "label": "D8 fixture"}
    monkeypatch.setattr(g1_trial_acquire, "outcome_terms", lambda cfg: ["mortality"])
    monkeypatch.setattr(g1_trial_acquire, "aact_evidence", lambda ncts: {})
    monkeypatch.setattr(g1_trial_acquire, "text_evidence", lambda pmid, terms: ("", "", None))
    monkeypatch.setattr(g1_trial_acquire, "unpaywall_evidence",
                        lambda pmid, terms: (whole, whole, "fixture-digest", "10.1/x", licence))
    monkeypatch.setattr(g1_trial_acquire, "meta_evidence", lambda slug, label: [])
    monkeypatch.setattr(g1_trial_acquire, "regulatory_evidence", lambda t, terms: ([], {}))

    def unexpected_pmc_lookup(pmid):
        pytest.fail("Unpaywall evidence must not look up a PMC licence")

    monkeypatch.setattr(g1_trial_acquire, "pmc_licence", unexpected_pmc_lookup)
    ev, held = g1_trial_acquire.evidence(trial, {}, comp="d8-test-comparator")

    assert held["text_origin"] == "UNPAYWALL"
    assert held["text"] == whole
    assert held["doi_licence"] == licence
    source = ev["full_text"]
    if permitted:
        assert source["text"] == whole
        assert source["doi"] == "10.1/x"
        assert source["licence"] == licence
    else:
        assert "text" not in source
        assert source["state"] == "HELD_NOT_OPEN_LICENSED"
