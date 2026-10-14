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
