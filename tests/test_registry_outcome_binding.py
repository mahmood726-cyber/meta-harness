"""Registry identity comes from the number's OWN held measure, never a nearby primary.

Real inputs are pinned git bytes, including full served tuples and registry arm
tables. Plants modify copies only. Run with the two requested binder controls.
"""
import copy
import importlib.util
from pathlib import Path

import pytest

from harness import target_endpoint as te
from harness.ctgov_results import extract_ctgov

ROOT = Path(__file__).resolve().parents[1]
REF = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
_spec = importlib.util.spec_from_file_location(
    "registry_audit", ROOT / "evidence/unbound_legacy/classify_legacy_rows.py")
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)


def held(slug, outcome, identifier):
    topic = audit.held_json(REF, f"topics/{slug}.json")
    spec = copy.deepcopy(audit.outcome_spec(topic, outcome))
    row, nct, measures = audit.registry_inputs(REF, slug, outcome, identifier)
    return spec, copy.deepcopy(row), copy.deepcopy(measures), topic["intervention_terms"], topic["comparator_terms"]


def bleeding():
    return held("ticagrelor-vs-clopidogrel-acs", "Major bleeding", "PMID 19717846")


def extract_measure(om, intervention, comparator):
    row = extract_ctgov([om], [om["title"]], intervention, comparator)
    assert row is not None
    return dict(row, provenance="ctgov_results")


@pytest.mark.parametrize("slug,outcome,identifier,title,counts", [
    ("omega3-cardiovascular-events", "Atrial fibrillation", "PMID 30146932",
     "Number of Participants With Event: Atrial Fibrillation (Omega-3 Comparison Only)", (166, 7740, 135, 7740)),
    ("ticagrelor-vs-clopidogrel-acs", "Major bleeding", "PMID 19717846",
     "Participants With Any Major Bleeding Event", (961, 9235, 929, 9186)),
])
def test_real_declared_targets_bind_their_own_held_measure(slug, outcome, identifier, title, counts):
    spec, row, oms, iv, cp = held(slug, outcome, identifier)
    c = te.bind_registry_row(spec, row, oms, iv, cp)
    assert c["target_endpoint_class"] == te.EXACT_TARGET
    assert c["registry_outcome_quote"]["title"] == title
    assert tuple(c["registry_matched_tuple"].values()) == counts
    assert c["registry_numeric_quote"]["classes"] == oms[c["registry_outcome_index"]]["classes"]
    assert te.admit_rows(spec, [dict(row, **c)])[0]


def test_secondary_same_number_cannot_borrow_primary_identity():
    spec, row, oms, iv, cp = bleeding()
    original = te.bind_registry_row(spec, row, oms, iv, cp)
    primary = oms[original["registry_outcome_index"]]
    secondary = copy.deepcopy(primary)
    secondary.update(type="SECONDARY", title="Participants With Minor Bleeding",
                     description="Minor bleeding events.")
    planted_row = extract_measure(secondary, iv, cp)
    assert [planted_row[k] for k in ("ai", "n1i", "ci", "n2i")] == [961, 9235, 929, 9186]
    c = te.bind_registry_row(spec, planted_row, [primary, secondary], iv, cp)
    assert c["registry_outcome_index"] == 1
    assert c["registry_outcome_quote"]["title"] == secondary["title"]
    assert c["target_endpoint_class"] == te.ENDPOINT_UNBOUND
    assert not te.admissibility(spec, dict(planted_row, **c))["admissible"]
    # Even deleting the primary does not change which identity is classified.
    assert te.bind_registry_row(spec, planted_row, [secondary], iv, cp)["target_endpoint_class"] == te.ENDPOINT_UNBOUND


def test_explicit_secondary_qualifier_cannot_become_primary():
    spec, row, oms, iv, cp = bleeding()
    om = oms[te.bind_registry_row(spec, row, oms, iv, cp)["registry_outcome_index"]]
    spec["kind"] = "primary"
    om["type"] = "SECONDARY"
    c = te.bind_registry_row(spec, row, [om], iv, cp)
    assert c["target_endpoint_class"] == te.ENDPOINT_UNBOUND


@pytest.mark.parametrize("timeframe", ["First dosing up to 24 months", "", "At 6 months and 12 months"])
def test_wrong_missing_or_ambiguous_timeframe_abstains(timeframe):
    spec, row, oms, iv, cp = bleeding()
    om = oms[te.bind_registry_row(spec, row, oms, iv, cp)["registry_outcome_index"]]
    spec["timepoint"] = "12 months"
    assert te.bind_registry_row(spec, row, [om], iv, cp)["target_endpoint_class"] == te.EXACT_TARGET
    om["timeFrame"] = timeframe
    c = te.bind_registry_row(spec, row, [om], iv, cp)
    assert c["target_endpoint_class"] == te.ENDPOINT_UNBOUND
    assert "timepoint" in c["endpoint_binding_reason"]


def test_safety_measure_under_efficacy_target_abstains():
    spec, row, oms, iv, cp = bleeding()
    spec.update(name="Cardiovascular death", keywords=["major bleeding", "death"])
    c = te.bind_registry_row(spec, row, oms, iv, cp)
    assert c["registry_outcome_quote"]["title"] == "Participants With Any Major Bleeding Event"
    assert c["target_endpoint_class"] == te.ENDPOINT_UNBOUND
    assert not te.admit_rows(spec, [dict(row, **c)])[0]


@pytest.mark.parametrize("title", ["Non-major bleeding", "Recurrent major bleeding", "Severe major bleeding"])
def test_undeclared_modifier_does_not_supply_exact_identity(title):
    assert te.classify_registry_measure({"name": "Major bleeding"}, {"title": title})["target_endpoint_class"] == te.ENDPOINT_UNBOUND


def test_missing_or_ambiguous_measure_never_guessed():
    spec, row, oms, iv, cp = bleeding()
    om = oms[te.bind_registry_row(spec, row, oms, iv, cp)["registry_outcome_index"]]
    for measures in ([], [om, copy.deepcopy(om)]):
        c = te.bind_registry_row(spec, row, measures, iv, cp)
        assert c["target_endpoint_class"] == te.ENDPOINT_IDENTITY_MISSING
        kept, refused = te.admit_rows(spec, [dict(row, **c)])
        assert not kept
        assert refused[0]["reason_code"] == te.ENDPOINT_IDENTITY_MISSING
        assert refused[0]["candidate_tuple"]["ai"] == 961
    row["ai"] += 1
    assert te.bind_registry_row(spec, row, [om], iv, cp)["target_endpoint_class"] == te.ENDPOINT_IDENTITY_MISSING


def test_derived_identity_requires_every_parent_rebound_not_parent_class_labels():
    spec, row, oms, iv, cp = bleeding()
    good = te.bind_derived_registry_row(spec, [row], oms, iv, cp)
    assert good["target_endpoint_class"] == te.EXACT_TARGET
    bad = dict(row, ai=row["ai"] + 1, target_endpoint_class=te.EXACT_TARGET)
    for parents in ([], [row, bad], [bad, row]):
        c = te.bind_derived_registry_row(spec, parents, oms, iv, cp)
        assert c["target_endpoint_class"] == te.ENDPOINT_IDENTITY_MISSING
        assert not te.admissibility(spec, dict(provenance="derived", **c))["admissible"]
    # Explicit lineage is checked even if the child carries a registry label.
    c = te.bind_registry_row(spec, dict(row, derived_from=[row, bad]), oms, iv, cp)
    assert c["target_endpoint_class"] == te.ENDPOINT_IDENTITY_MISSING


@pytest.mark.parametrize("slug,outcome,identifier", [
    ("esketamine-trd-madrs", "Observed-case Day-28 raw change-score MADRS MD", "PMID 37025256"),
    ("esketamine-trd-madrs", "Observed-case Day-28 raw change-score MADRS MD", "PMID 31109201"),
    ("esketamine-trd-madrs", "Observed-case Day-28 raw change-score MADRS MD", "NCT02422186"),
    ("melatonin-primary-insomnia-sol", "Sleep-onset latency", "PMID 20712869"),
    ("semaglutide-obesity-weight", "Percent change in body weight", "PMID 33625476"),
    ("semaglutide-obesity-weight", "Percent change in body weight", "PMID 33567185"),
])
def test_located_continuous_measures_do_not_gain_undeclared_synonyms(slug, outcome, identifier):
    spec, row, oms, iv, cp = held(slug, outcome, identifier)
    c = te.bind_registry_row(spec, row, oms, iv, cp)
    assert c["target_endpoint_class"] == te.ENDPOINT_UNBOUND
    assert c["registry_matched_tuple"]["mean1"] == row["mean1"]
    assert "no full declared outcome phrase" in c["endpoint_binding_reason"]
    # Positive control: with the actual held title as the declared outcome,
    # identical bytes/tuple can bind. No topic synonym list is built into code.
    om = oms[c["registry_outcome_index"]]
    declared = {"name": om["title"], "timepoint": om["timeFrame"]}
    positive = te.bind_registry_row(declared, row, oms, iv, cp)
    assert positive["target_endpoint_class"] == te.EXACT_TARGET


@pytest.mark.parametrize("slug,outcome,identifier", [
    ("metformin-pcos-ovulation", "Ovulation with metformin added to clomifene", "PMID 19522426"),
    ("metformin-pcos-ovulation", "Ovulation with metformin added to clomifene", "PMID 16769748"),
    ("noac-vs-warfarin-af-stroke", "Stroke or systemic embolism", "PMID 19717844"),
    ("noac-vs-warfarin-af-stroke", "Stroke or systemic embolism", "PMID 24251359"),
    ("probiotics-aad-prevention", "Antibiotic-associated diarrhoea", "PMID 15740542"),
    ("probiotics-aad-prevention", "Antibiotic-associated diarrhoea", "PMID 18026577"),
])
def test_abstract_override_or_arithmetic_label_is_not_a_registry_measure(slug, outcome, identifier):
    spec, row, oms, iv, cp = held(slug, outcome, identifier)
    assert te.bind_registry_row(spec, row, oms, iv, cp)["target_endpoint_class"] == te.ENDPOINT_IDENTITY_MISSING


def test_supported_composite_requires_its_own_enumerated_components():
    spec = {"name": "Major cardiovascular events", "components": ["cardiovascular death", "myocardial infarction", "stroke"]}
    om = {"title": "Major cardiovascular events", "description": "Cardiovascular death, myocardial infarction or stroke."}
    assert te.classify_registry_measure(spec, om)["target_endpoint_class"] == te.EXACT_TARGET
    om["description"] += " Or hospitalization for unstable angina."
    assert te.classify_registry_measure(spec, om)["target_endpoint_class"] == te.ENDPOINT_UNBOUND
    om["description"] = ""
    assert te.classify_registry_measure(spec, om)["target_endpoint_class"] == te.ENDPOINT_UNBOUND
