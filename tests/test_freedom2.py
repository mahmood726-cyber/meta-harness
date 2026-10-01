"""Row ownership contracts independent of any named trial or identifier."""
import copy
import json
import re

import pytest

from scripts import build_bundle as producer, verify_bundle as verifier
from scripts.freedom2_acceptance import ROOT, SLUG, PREFIX, mutate


@pytest.mark.parametrize("effect,expected", [
    ((1.24, .90, 1.70), True), ((1.2, .90, 1.70), False),
    ((1.24, .90, 1.63), False), ((1.21, .90, 1.63), True),
])
def test_complete_table_tuples(effect, expected):
    text = "3-Point MACE | 1.240 (0.900, 1.700) | 4-Point MACE | 1.21 (0.90, 1.63)"
    eff = dict(zip(("estimate", "ci_low", "ci_high"), effect))
    assert verifier.regulatory_tuple_matches(text, eff) is expected
    if expected:
        candidate = {"text": text}
        assert verifier.regulatory_holder_endpoint(candidate, eff) == {
            "3-point MACE" if effect[0] == 1.24 else "4-point MACE+"}


def test_sentence_terminal_decimal_is_a_complete_number():
    eff = {"estimate": 1.02, "ci_low": .887, "ci_high": 1.172}
    assert verifier.regulatory_tuple_matches("(0.887, 1.172) with a point estimate of 1.02.", eff)


@pytest.mark.parametrize("case", ["sustain6_mi_as_mace", "amplitudeo_renal_as_mace"])
def test_held_alternate_clause_and_fail_loud_setup(case):
    store = verifier.Store(str(ROOT / "docs"), None)
    review = store.json(PREFIX + "review.json")
    records = store.json(f"cache/{SLUG}/records.json")
    bundle = store.json(PREFIX + "BUNDLE.json")
    evidence = mutate(case, review, records, bundle)
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    trial = next(t for t in primary["trials"] if t["id"] == evidence["source_id"])
    values = [trial[k] for k in ("effect", "ci_low", "ci_high")]
    for route in (producer, verifier):
        result = route.span_target_mention(trial["endpoint_result_span"], values,
                                          trial["endpoint_definition_span"], primary["endpoint_canonical"]["components"])
        assert result["state"] == "ENDPOINT_INCOMPATIBLE", result
    changed = copy.deepcopy(records)
    for record in changed["records"]:
        if "PMID " + str(record["id"]).removeprefix("PMID ") == evidence["source_id"]:
            record["abstract"] = record["abstract"].replace(evidence["clause"], "")
    with pytest.raises(AssertionError, match="Alternate result clause"):
        mutate(case, review, changed, bundle)


def test_measured_lane_semantics():
    ledger = json.loads((ROOT / "freedom2.json").read_text(encoding="utf-8"))
    for case in ledger["cases"]:
        assert case["intended_semantics_credited"], case
        assert case["restore_byte_identical"]
    assert ledger["served_corpus_byte_identical"]


def test_legacy_multirow_witness_and_disagreement_are_both_checked():
    store = verifier.Store(str(ROOT / "docs"), None)
    bundle = store.json(PREFIX + "BUNDLE.json")
    candidates = [f for f in bundle["regulatory_facts"]
                  if any(len(re.findall(r"\d+\.\d+ \(\d+\.\d+, \d+\.\d+\)", a["text"])) > 1
                         for a in f["candidate_analyses"])]
    assert len(candidates) == 1
    fact = candidates[0]
    text = fact["candidate_analyses"][0]["text"]
    triples = re.findall(r"(\d+\.\d+) \((\d+\.\d+), (\d+\.\d+)\)", text)
    fact["decision"]["effect"].update(zip(("estimate", "ci_low", "ci_high"), map(float, triples[1])))
    assert fact["tuple_to_identity_binding"] == "BOUND"
    store.cache[PREFIX + "BUNDLE.json"] = json.dumps(bundle).encode("utf-8")
    report = verifier.run(store, SLUG, None)
    errors = report["failure_categories"]["semantics"]
    assert errors[0].startswith("ANALYSIS_IDENTITY_MISMATCH "), errors
    assert any(e.startswith("ROW_VERDICT_DISAGREES regulatory ") for e in errors), errors
