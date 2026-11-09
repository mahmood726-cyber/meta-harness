"""Synthetic A7 adjudication plants; never read cache/ or use the network."""
import copy
import importlib
import json
from pathlib import Path

import pytest

from harness import extract, page, pipeline

SLUG = "colchicine-recurrent-pericarditis"
NAME = "Recurrent pericarditis"
ID = "PMID 24694983"
KEY = f"{SLUG}::{NAME}::{ID}"
ENTRY = {
    "decision": "POOL_COUNTS",
    "decided_by": "Mahmood Ahmad (decision relayed to the coverage lane in chat, 15 Oct 2026)",
    "date": "2026-10-15",
    "reported": {"scale": "RR", "effect": 0.49, "ci_low": 0.24, "ci_high": 0.65},
    "count_derived": {"ai": 26, "n1i": 120, "ci": 51, "n2i": 120},
    "basis": "option (B) of the A7-S1 signing item: the counts are the source's own data; the printed 0.49 differs from them by 0.020 (beyond its rounding); pooled with the discrepancy shown",
}
SPAN = "Recurrent pericarditis occurred in 26/120 patients given colchicine and 51/120 given placebo."
DOCUMENT = SPAN + " Recurrent pericarditis relative risk 0.49; 95% CI 0.24-0.65."


def typed(route="abstract"):
    result = extract.reported_vs_count_derived(
        (26, 120, 51, 120), ("RR", .49, .24, .65),
        "relative risk 0.49; 95% CI 0.24-0.65", SPAN)
    return {**result, "provenance": route}


def module(monkeypatch, entry=None):
    mod = importlib.import_module("harness.a7_adjudication")
    monkeypatch.setattr(mod, "load", lambda: {"adjudications": {KEY: copy.deepcopy(entry or ENTRY)}})
    return mod


@pytest.mark.parametrize("route", ["abstract", "pmc_fulltext"])
def test_matching_counts_are_admitted(monkeypatch, route):
    result = module(monkeypatch).resolve(SLUG, NAME, ID, typed(route))
    assert result["state"] == "ADJUDICATED_POOL_COUNTS"
    row = result["row"]
    assert {k: row[k] for k in ENTRY["count_derived"]} == ENTRY["count_derived"]
    assert row["source"] == SPAN and row["provenance"] == route
    record = row["reported_vs_count_derived"]
    assert record["reported"] == typed()["reported"]
    assert record["count_derived"] == typed()["count_derived"]
    for key in ("decision", "decided_by", "date"):
        assert record[key] == ENTRY[key]


@pytest.mark.parametrize("section,key,value", [
    ("count_derived", "ai", 27), ("count_derived", "n1i", 121),
    ("count_derived", "ci", 52), ("count_derived", "n2i", 121),
    ("reported", "scale", "OR"), ("reported", "effect", .50),
    ("reported", "ci_low", .25), ("reported", "ci_high", .66),
])
def test_changed_values_are_stale(monkeypatch, section, key, value):
    mod = module(monkeypatch)
    changed = typed()
    changed[section][key] = value
    assert mod.resolve(SLUG, NAME, ID, changed)["state"] == "A7_ADJUDICATION_STALE"


def test_no_adjudication(monkeypatch):
    assert module(monkeypatch).resolve("synthetic-other-topic", NAME, ID, typed()) is None


def test_unknown_decision_fails_closed(monkeypatch):
    mod = module(monkeypatch, {**ENTRY, "decision": "UNKNOWN"})
    with pytest.raises(ValueError):
        mod.resolve(SLUG, NAME, ID, typed())


def test_registry_exact_entry():
    path = Path(__file__).resolve().parents[1] / "registry/a7_adjudications.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["rule"]
    assert data["adjudications"] == {KEY: ENTRY}
    mod = importlib.import_module("harness.a7_adjudication")
    assert mod.load(path) == data


def test_page_discloses_and_escapes_adjudication():
    record = {**ENTRY, "reported": typed()["reported"], "count_derived": typed()["count_derived"]}
    record["decided_by"] = "<script>reviewer</script>"
    html = page._trial_inputs({"trials": [{"label": "synthetic", "id": "synthetic",
        **ENTRY["count_derived"], "source": SPAN, "reported_vs_count_derived": record}]})
    for text in ("0.49", "0.510", "26/120", "adjudication", "2026-10-15", "&lt;script&gt;"):
        assert text in html
    assert "<script>reviewer</script>" not in html


@pytest.mark.parametrize("route", ["abstract", "pmc_fulltext"])
@pytest.mark.parametrize("decision", ["match", "missing", "stale"])
@pytest.mark.parametrize("upper_ci", [.65, .90])
def test_pipeline_routes(monkeypatch, route, decision, upper_ci):
    entry = copy.deepcopy(ENTRY)
    entry["reported"]["ci_high"] = upper_ci
    module(monkeypatch, entry)
    current = typed(route)
    current["reported"]["ci_high"] = upper_ci
    if decision == "stale":
        current["count_derived"]["ai"] = 27
    monkeypatch.setattr(extract, "extract_trial", lambda *a, **kw:
                        current if route == "abstract" else {"absent": True})
    monkeypatch.setattr(pipeline, "_fulltext_extract", lambda *a, **kw: current)
    # A source-hierarchy candidate must not undo the explicit POOL_COUNTS decision.
    monkeypatch.setattr(pipeline, "_span_effect_candidates", lambda *a, **kw: [
        {**entry["reported"], "source": DOCUMENT, "provenance": route, "derivation": "reported"}])
    # Registry additions/contracts cannot supply synthetic inputs from disk.
    from harness import served_pool_additions, estimand_contract
    monkeypatch.setattr(served_pool_additions, "admitted_rows", lambda *a: [])
    monkeypatch.setattr(estimand_contract, "signed", lambda *a: None)
    out = pipeline._build_outcome(
        {"name": NAME, "keywords": ["recurrent pericarditis"], "estimand": "RR"}, "primary",
        [{"id": "24694983", "id_type": "pmid", "label": "Synthetic"}],
        {"24694983": {"abstract": DOCUMENT if route == "abstract" else "Synthetic trial."}},
        ["colchicine"], ["placebo"],
        fulltext_by_pmid={"24694983": DOCUMENT} if route == "pmc_fulltext" else {},
        slug=SLUG if decision != "missing" else "synthetic-other-topic")
    if decision == "match":
        assert len(out["trials"]) == 1
        assert out["trials"][0]["ai"] == 26
        assert out["trials"][0]["provenance"] == route
        assert out["trials"][0]["reported_vs_count_derived"]["decision"] == "POOL_COUNTS"
    else:
        assert out["trials"] == []
        refusal = out["declared_absent_trials"][0]
        assert refusal["state"] == extract.SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE
        assert refusal.get("a7_adjudication") == ("STALE" if decision == "stale" else None)
