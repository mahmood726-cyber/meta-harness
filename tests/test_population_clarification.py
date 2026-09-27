"""The D3 retrospective population-vocabulary clarification (Mahmood, 2026-09-25).

"Preserved systolic function" counts as the same entry population as "preserved ejection
fraction". The ruling was made AFTER the data were seen, so these tests pin two things at once:

  * the equivalence admits DELIVER, and
  * it is recorded as RETROSPECTIVE and never becomes indistinguishable from a pre-specified term.

The negative controls matter more than the positive one: a clarification that admits an unrelated
population, or that overrides an exclusion, is a loosening rather than a clarification.
"""
import json
from pathlib import Path

import pytest

from harness.family_compact import read_families
from harness.trial_family import population_clarification, screen_family

ROOT = Path(__file__).resolve().parents[1]
SLUG = "dapagliflozin-hfpef-hosp"
DELIVER = "NCT03030235"


def _config():
    return json.loads((ROOT / "topics" / f"{SLUG}.json").read_text(encoding="utf-8"))


def _deliver():
    reg = ROOT / "cache" / SLUG / "families.json"
    if not reg.exists():
        pytest.skip(f"no held families for {SLUG}; run the topic build first")
    # read_families, NOT expand alone: screening reads design fields that sit behind a $row.
    fams = read_families(reg)["families"]
    fam = next((f for f in fams if f.get("family_id") == DELIVER), None)
    if fam is None:
        pytest.skip(f"{DELIVER} not among the {len(fams)} held families")
    return fam


def test_the_clarification_is_declared_as_retrospective_not_pre_specified():
    clars = _config().get("population_vocabulary_clarifications") or []
    assert clars, "the D3 clarification must be declared in the topic config"
    c = next(x for x in clars if x["id"] == "D3-preserved-systolic-function")
    assert c["pre_specified"] is False
    assert c["decided_after_data_seen"] is True
    assert c["status"] == "RETROSPECTIVE_PROTOCOL_CLARIFICATION"
    assert c["decided_by"] == "Mahmood"
    assert c["how_it_reached_the_reviewer"] == (
        "Dispatch chat relay, answer to a plain-language question")
    # the pre-specified vocabulary must NOT have quietly absorbed the term
    assert not any("systolic function" in t.lower()
                   for t in _config()["include"]["population_any"]), \
        "a retrospective term must not be added to include.population_any, where it would read " \
        "as pre-specified"


def test_deliver_is_admitted_and_the_cell_says_the_basis_was_retrospective():
    got = screen_family(_deliver(), _config())
    assert got["state"] == "ELIGIBLE", got
    span = got["span"]
    assert span["population_basis"] == "RETROSPECTIVE_VOCABULARY_CLARIFICATION"
    assert span["population_clarification"]["id"] == "D3-preserved-systolic-function"
    assert span["population_clarification"]["pre_specified"] is False


def test_without_the_clarification_deliver_is_refused_again():
    """Proves the clarification is what admits DELIVER -- not some other change to screening."""
    cfg = dict(_config())
    cfg.pop("population_vocabulary_clarifications", None)
    got = screen_family(_deliver(), cfg)
    assert got["state"] != "ELIGIBLE"
    assert got["absence_code"] == "ENTRY_POPULATION_NOT_ESTABLISHED"


def test_an_unrelated_population_is_not_admitted_by_the_clarification():
    cfg = _config()
    assert population_clarification(cfg, ["Asthma"]) is None
    assert population_clarification(cfg, ["Type 2 Diabetes Mellitus"]) is None
    assert population_clarification(cfg, ["Chronic Heart Failure With Preserved Systolic Function"])


def test_the_clarification_does_not_override_an_excluded_population():
    """population_none runs after the clarification, so an excluded trial stays excluded."""
    fam = json.loads(json.dumps(_deliver()))
    fam["population"]["conditions"]["value"] = [
        "Chronic Heart Failure With Preserved Systolic Function",
        "Heart failure with reduced ejection fraction",
    ]
    got = screen_family(fam, _config())
    assert got["state"] == "INELIGIBLE", (
        "a population on population_none must stay excluded even when a retrospective "
        "clarification matches one of its other conditions")
