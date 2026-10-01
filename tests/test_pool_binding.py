"""Real certified GLP-1 fixture: substitution controls keep sources and digests intact.

These deliberately altered copies are tests, never revised scientific results.
"""
import copy
import json
from pathlib import Path
import re

import pytest

from scripts import verify_bundle as verifier

ROOT = Path(__file__).resolve().parents[1]
SLUG = "glp1-ra-mace-t2d"
BUNDLE_PATH = f"reviews/{SLUG}/BUNDLE.json"
CASES = ("reciprocal_updated", "unknown_ids", "rotated_ids", "repeated_pioneer6", "reciprocal_stale")


def plant(bundle, case, review):
    ref = bundle["pooled_reference"]
    rows = ref["inputs"]
    if case.startswith("reciprocal"):
        values = verifier._plant_input_values(rows, review)
        for row, value in zip(rows, values):
            row.update(effect=1 / value["effect"], ci_low=1 / value["ci_high"], ci_high=1 / value["ci_low"])
        if case == "reciprocal_updated":
            got = verifier._plant_expected_pool(verifier._plant_input_values(rows, review))
            ref["expected"] = {k: got[k] for k in ref["expected"]}
    elif case == "unknown_ids":
        for i, row in enumerate(rows):
            row["id"] = f"UNKNOWN-PLANT-{i}"
    elif case == "rotated_ids":
        ids = [r["id"] for r in rows]
        for row, ident in zip(rows, ids[1:] + ids[:1]):
            row["id"] = ident
    elif case == "repeated_pioneer6":
        # Historical case name: duplicating any selected reference must be refused.
        selected = rows[0]
        ref["inputs"] = [copy.deepcopy(selected) for _ in rows]
        got = verifier._plant_expected_pool(verifier._plant_input_values(ref["inputs"], review))
        ref["expected"] = {k: got[k] for k in ref["expected"]}
    else:
        raise ValueError(f"unknown plant: {case}")


@pytest.fixture
def objects():
    store = admissible_control(verifier.Store(str(ROOT / "docs"), None))
    return (store.json(f"reviews/{SLUG}/review.json"), store.json(BUNDLE_PATH), store.json(f"cache/{SLUG}/records.json"))


def put_json(store, path, value):
    store.cache[path] = (json.dumps(value, ensure_ascii=False, indent=1) + "\n").encode("utf-8")


def recertify_fixture(store, review, bundle):
    """Re-pin an isolated producer fixture, including its review and execution-record links."""
    prefix = f"reviews/{SLUG}/"
    cert = store.json(prefix + "CERTIFICATE.json")
    cert["review_sha256"] = verifier.sha256_text(verifier.canonical({k: v for k, v in review.items() if k != "reproduction"}))
    cert["bundle_core_sha256"] = verifier._bundle_core_sha256(bundle)
    cert["release_sha256"] = verifier.sha256_text(verifier.canonical({k: v for k, v in cert.items() if k != "release_sha256"}))
    put_json(store, prefix + "review.json", review)
    put_json(store, prefix + "CERTIFICATE.json", cert)
    cert_bytes = store.get(prefix + "CERTIFICATE.json")
    bundle["certificate"].update(sha256_of_file=verifier.sha256(cert_bytes), bytes=len(cert_bytes), release_sha256=cert["release_sha256"])
    for record in bundle["review_files"]:
        if record["file"] == "EXECUTION_RECORD.json":
            execution = store.json(prefix + record["file"])
            execution["release"].update(release_sha256=cert["release_sha256"], review_sha256=cert["review_sha256"])
            put_json(store, prefix + record["file"], execution)
        if record["file"] in ("review.json", "CERTIFICATE.json", "EXECUTION_RECORD.json"):
            raw = store.get(prefix + record["file"])
            record.update(sha256=verifier.sha256(raw), bytes=len(raw))
    put_json(store, BUNDLE_PATH, bundle)


def refused_on_admission(store=None):
    """The ids the verifier currently refuses on admission -- DERIVED, never hardcoded.

    Naming a PMID here would pin the fixture to one trial's evidence state; the day that state changes
    the control silently stops controlling anything, which is worse than having no control.
    """
    report = verifier.run(store or verifier.Store(str(ROOT / "docs"), None), SLUG, None)
    return {f"PMID {row['pmid']}" for row in report["rows"] if row["final"] != "ADMISSIBLE"}


HARMONY_FAMILY, HARMONY_ID = "NCT02465515", "PMID 30291013"


def refused_row_store():
    """A baseline that HAS an admission-refused row, built rather than borrowed.

    Until V1.0.1 the live corpus supplied one (HARMONY, INADMISSIBLE on P5), so the refusal controls were anchored to a live
    defect and retired themselves when HARMONY's population was established on source evidence (evid2, 91f057a4). This copy
    sets HARMONY's CERTIFIED family eligibility to UNKNOWN and re-pins families.json exactly as a producer would (file digests,
    the certificate's trial_family_map_sha256, the bundle pin), so the only thing wrong with it is the admission state."""
    import hashlib
    store = verifier.Store(str(ROOT / "docs"), None)
    fam_path = f"cache/{SLUG}/families.json"
    fam = copy.deepcopy(store.json(fam_path))
    next(f for f in fam["families"] if f["family_id"] == HARMONY_FAMILY)["eligibility"] = {"state": "UNKNOWN"}
    raw = (json.dumps(fam, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    store.cache[fam_path] = raw
    declared = verifier.sha256_text(verifier.canonical(fam))
    bundle = copy.deepcopy(store.json(BUNDLE_PATH))
    for art in bundle["artefacts"]:
        if art.get("ref") == fam_path:
            art.update(bytes=len(raw), sha256=verifier.sha256(raw), declared_digest=declared,
                       git_blob_sha1=hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest())
    row = next(r for r in bundle["verification_rows"] if r["trial"]["id"] == HARMONY_ID)      # the producer's recorded verdict
    row["admission"]["final"] = "INADMISSIBLE"
    row["admission"]["predicates"]["P5_family_eligible"]["state"] = "FAIL"
    review = copy.deepcopy(store.json(f"reviews/{SLUG}/review.json"))
    next(f for f in review["trial_families"] if f.get("family_id") == HARMONY_FAMILY)["eligibility"] = {"state": "UNKNOWN"}  # rendered copy
    cert_path = f"reviews/{SLUG}/CERTIFICATE.json"
    cert = store.json(cert_path)
    cert["trial_family_map_sha256"] = declared
    put_json(store, cert_path, cert)
    recertify_fixture(store, review, bundle)
    return store


def admissible_control(store):
    """The all-admissible control, in an isolated copy, never from docs: remove whichever rows are refused on admission (none
    in the served corpus since V1.0.1, when it is the authentic tree itself). Its property -- all five verdicts PASS -- is
    asserted by test_valid_admissible_source_backed_control_can_pass_all_five_verdicts."""
    review = copy.deepcopy(store.json(f"reviews/{SLUG}/review.json"))
    bundle = copy.deepcopy(store.json(BUNDLE_PATH))
    dropped = refused_on_admission()
    if not dropped:
        return store
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    primary["trials"] = [r for r in primary["trials"] if r["id"] not in dropped]
    bundle["verification_rows"] = [r for r in bundle["verification_rows"]
                                   if r["trial"]["id"] not in dropped]
    ref = bundle["pooled_reference"]
    # Preserve each surviving reference and its outcome_effect_id; only remove refused members.
    ref["inputs"] = [r for r in ref["inputs"] if r["id"] not in dropped]
    got = verifier._plant_expected_pool(verifier._plant_input_values(ref["inputs"], review))
    ref["k"] = got["k"]
    ref["expected"] = {k: got[k] for k in ref["expected"]}
    for key, places in {"estimate": 4, "ci_low": 4, "ci_high": 4, "tau2": 5, "Q": 5}.items():
        primary["result"][key] = round(got[key], places)
    primary["result"]["k"] = got["k"]
    recertify_fixture(store, review, bundle)
    return store


def test_authentic_pool_passes_with_every_row_admissible():
    """V1.0.1 (evid2 population evidence): the served GLP-1 pool is 8 of 8 admissible and passes all five verdicts."""
    report = verifier.run(verifier.Store(str(ROOT / "docs"), None), SLUG, None)
    assert report["verdict"] == "PASS", report["failures"]
    assert [row["final"] for row in report["rows"]] == ["ADMISSIBLE"] * 8
    assert report["pool"]["recomputed"]["k"] == 8


def test_built_baseline_is_refused_on_admission_and_nothing_else():
    store = refused_row_store()
    report = verifier.run(store, SLUG, None)
    assert report["verdicts"]["artifact_integrity"] == "PASS", report["failures"]
    assert refused_on_admission(store) == {HARMONY_ID}
    harmony = next(r for r in report["rows"] if f"PMID {r['pmid']}" == HARMONY_ID)
    assert harmony["predicates"]["P5_family_eligible"] is False


def test_pool_refuses_exactly_the_admission_refused_rows():
    """A pool refuses its inadmissible members without computing or hiding rows (on the built baseline).

    Admission alone and publication eligibility remain separate, as tested below with separate_verdicts.
    Including an admission-refused member in this pool is an explicit linkage failure.
    """
    store = refused_row_store()
    review = store.json(f"reviews/{SLUG}/review.json")
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    certified_ids = {row["id"] for row in primary["trials"]}
    expected_refused = refused_on_admission(store)
    assert expected_refused == {HARMONY_ID}, "the refusal control needs its built admission-refused row"

    report = verifier.run(store, SLUG, None)
    assert report["verdict"] == "FAIL", report["failures"]
    verdicts = report["verdicts"]
    assert verdicts["artifact_integrity"] == "PASS", verdicts
    assert verdicts["input_linkage"] == "FAIL", verdicts
    assert verdicts["scientific_admission"] == "FAIL", verdicts
    assert verdicts["publication_eligibility"] == "REFUSED", verdicts
    assert {failure.split(maxsplit=1)[0] for failure in report["failures"]} == {"POOL_CONTAINS_INADMISSIBLE_ROW"}
    linkage = report["failure_categories"]["input_linkage"]
    assert linkage == report["failures"], report["failure_categories"]
    named_refused = {f"PMID {pmid}" for failure in linkage
                     for pmid in re.findall(r"\bPMID\s+([0-9]+)\b", failure)}
    assert named_refused == expected_refused, linkage
    assert report["pool"]["recomputed"] is None, report["pool"]
    assert report["pool"]["refused_before_logs"], report["pool"]

    refused = [row for row in report["rows"] if row["final"] != "ADMISSIBLE"]
    assert refused, "scientific_admission failed but no row is named as inadmissible"
    assert {f"PMID {row['pmid']}" for row in refused} == expected_refused
    # Anchor disclosure to the certified source, since a refused pool has no recomputed k.
    assert len(report["rows"]) == len(primary["trials"]), "a certified row has been dropped from the report"
    assert {f"PMID {row['pmid']}" for row in report["rows"]} == certified_ids
    for row in refused:
        failing = [name for name, value in row["predicates"].items() if value is False]
        assert failing, f"row {row['pmid']} is inadmissible but no predicate explains why"
    assert report["pool"]["admissible_rows"] == len(primary["trials"]) - len(refused)


@pytest.mark.parametrize("case", CASES)
def test_full_verifier_refuses_substitution_semantically_and_restores(case):
    store = admissible_control(verifier.Store(str(ROOT / "docs"), None))
    review, bundle = store.json(f"reviews/{SLUG}/review.json"), store.json(BUNDLE_PATH)
    original = dict(store.cache)
    plant(bundle, case, review)
    recertify_fixture(store, review, bundle)
    report = verifier.run(store, SLUG, None)
    assert report["verdict"] == "FAIL"
    assert report["verdicts"]["artifact_integrity"] == "PASS"
    assert report["failure_categories"]["integrity"] == []
    assert report["pool"]["binding_ok"] is False
    if case.startswith("reciprocal"):
        # V1.0.1 references carry no values: an input that carries (reciprocal) values is refused BEFORE any arithmetic, so there
        # is no pool to agree or disagree with the certificate -- the refusal is the result (was: arithmetic agreed, linkage failed)
        assert report["pool"]["recomputed"] is None and report["pool"]["pool_measure_guard"]["refused"] is True
    else:
        assert report["pool"]["certified_result_agrees"] is True
    code = {"unknown_ids": "POOL_INPUT_MEMBERSHIP_MISMATCH", "repeated_pioneer6": "POOL_INPUT_DUPLICATE", "rotated_ids": "POOL_ROW_IDENTITY_MISMATCH"}.get(case, "POOL_INPUT_NOT_A_REFERENCE")
    # Linkage has its own verdict: arithmetic agreement cannot excuse a malformed reference.
    assert any(x.startswith(code) for x in report["failure_categories"]["input_linkage"])
    assert report["verdicts"]["input_linkage"] == "FAIL"
    # Restore the complete release, including the certificate and execution record.
    store.cache.clear()
    store.cache.update(original)
    assert verifier.run(store, SLUG, None)["verdict"] == "PASS"


def test_rotated_ids_fail_linkage_while_state_reproduction_passes():
    """Rotating ids preserves the multiset of dereferenced values but breaks outcome_effect_id binding.

    State reproduction must PASS while input linkage FAILS. If these verdicts move together,
    the split no longer distinguishes numerical agreement from certified-row identity.
    """
    store = admissible_control(verifier.Store(str(ROOT / "docs"), None))
    review, bundle = store.json(f"reviews/{SLUG}/review.json"), store.json(BUNDLE_PATH)
    original = dict(store.cache)
    plant(bundle, "rotated_ids", review)
    recertify_fixture(store, review, bundle)
    report = verifier.run(store, SLUG, None)
    v = report["verdicts"]
    assert v["state_reproduction"] == "PASS", report["pool"]
    assert v["input_linkage"] == "FAIL", report["failure_categories"]
    assert v["publication_eligibility"] == "REFUSED"
    assert report["failure_categories"]["input_linkage"][0].startswith("POOL_ROW_IDENTITY_MISMATCH ")
    store.cache.clear()
    store.cache.update(original)
    assert verifier.run(store, SLUG, None)["verdicts"]["input_linkage"] == "PASS"


@pytest.mark.parametrize("case", ("reciprocal_updated", "repeated_pioneer6"))
def test_self_consistent_mutations_fail_linkage_as_well_as_reproduction(case):
    """Producer expectations match the planted values, but disagree with the certified result.

    Both aggregate disagreement and invalid references must be detected independently.
    """
    store = admissible_control(verifier.Store(str(ROOT / "docs"), None))
    review, bundle = store.json(f"reviews/{SLUG}/review.json"), store.json(BUNDLE_PATH)
    original = dict(store.cache)
    plant(bundle, case, review)
    recertify_fixture(store, review, bundle)
    report = verifier.run(store, SLUG, None)
    v = report["verdicts"]
    assert v["input_linkage"] == "FAIL", report["failure_categories"]
    assert v["state_reproduction"] == "FAIL", report["pool"]
    assert v["publication_eligibility"] == "REFUSED"
    store.cache.clear()
    store.cache.update(original)
    assert verifier.run(store, SLUG, None)["verdicts"]["input_linkage"] == "PASS"


def test_valid_admissible_source_backed_control_can_pass_all_five_verdicts():
    report = verifier.run(admissible_control(verifier.Store(str(ROOT / "docs"), None)), SLUG, None)
    assert report["verdict"] == "PASS", report["failures"]
    assert report["verdicts"] == {"artifact_integrity": "PASS", "state_reproduction": "PASS",
                                  "input_linkage": "PASS", "scientific_admission": "PASS",
                                  "publication_eligibility": "ELIGIBLE"}


@pytest.mark.parametrize("field", ("analysis_set", "treatment_strategy", "follow_up_window", "estimator", "comparator_direction"))
def test_identity_value_mutation_is_not_saved_by_a_valid_span(objects, field):
    review, bundle, records = objects
    bundle["verification_rows"][0]["analysis_identity"][field]["value"] = "CONTRADICTORY TEST VALUE"
    _, errors = verifier.check_pool_contract(review, bundle, records)
    code = "POOL_CONTRAST_MISMATCH" if field == "comparator_direction" else "POOL_ANALYSIS_IDENTITY_MISMATCH"
    assert any(e.startswith(code) for e in errors)


@pytest.mark.parametrize("mutation,code", [
    ("missing", "POOL_INPUT_MEMBERSHIP_MISMATCH"), ("scale", "POOL_SCALE_MISMATCH"),
    ("analysis_key", "POOL_ANALYSIS_IDENTITY_MISMATCH"), ("family", "POOL_ROW_IDENTITY_MISMATCH"),
    ("direction", "POOL_CONTRAST_MISMATCH"), ("witness_tuple", "POOL_INPUT_TUPLE_MISMATCH"),
    ("certified_result", "POOL_CERTIFIED_RESULT_DISAGREES"), ("bundle_result", "POOL_BUNDLE_RESULT_DISAGREES"),
    ("nonfinite", "POOL_INPUT_NOT_A_REFERENCE"), ("duplicate_witness", "POOL_INPUT_DUPLICATE"),
    ("tiny_numeric_change", "POOL_INPUT_NOT_A_REFERENCE"), ("identity_erased", "POOL_ANALYSIS_IDENTITY_MISMATCH"),
    ("identity_malformed", "POOL_ANALYSIS_IDENTITY_MISMATCH"),
    ("certified_analysis", "POOL_ANALYSIS_IDENTITY_MISMATCH"),
])
def test_additional_contract_controls(objects, mutation, code):
    review, bundle, records = objects
    ref, witness = bundle["pooled_reference"], bundle["verification_rows"][0]
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    if mutation == "missing":
        ref["inputs"].pop()
    elif mutation == "scale":
        ref["scale"] = "RR"
    elif mutation == "analysis_key":
        witness["analysis_identity"]["analysis_identity_key"] = "wrong"
    elif mutation == "family":
        witness["trial"]["family_id"] = "NCT00000000"
    elif mutation == "direction":
        witness["analysis_identity"]["comparator_direction"]["effect_less_than_1_favours"] = "control"
    elif mutation == "witness_tuple":
        witness["effect"]["estimate"] += 0.01
    elif mutation == "certified_result":
        primary["result"]["estimate"] += 0.01
    elif mutation == "bundle_result":
        ref["expected"]["estimate"] += 0.01
    elif mutation == "nonfinite":
        ref["inputs"][0]["effect"] = float("nan")
    elif mutation == "duplicate_witness":
        bundle["verification_rows"].append(copy.deepcopy(witness))
    elif mutation == "tiny_numeric_change":
        value = verifier._plant_input_values(ref["inputs"], review)[0]["effect"]
        ref["inputs"][0]["effect"] = value + 1e-12
    elif mutation == "identity_erased":
        witness["analysis_identity"] = {}
    elif mutation == "identity_malformed":
        witness["analysis_identity"] = "wrong type"
    elif mutation == "certified_analysis":
        primary["trials"][0]["analysis_set"] = "per-protocol"
    _, errors = verifier.check_pool_contract(review, bundle, records)
    assert any(e.startswith(code) for e in errors), errors


def test_certified_result_disagreement_is_semantic_with_consistent_digests():
    store = admissible_control(verifier.Store(str(ROOT / "docs"), None))
    review, bundle = store.json(f"reviews/{SLUG}/review.json"), store.json(BUNDLE_PATH)
    next(o for o in review["outcomes"] if o.get("primary"))["result"]["estimate"] += 0.01
    recertify_fixture(store, review, bundle)
    report = verifier.run(store, SLUG, None)
    assert report["verdicts"]["artifact_integrity"] == "PASS"
    assert any(f.startswith("POOL_CERTIFIED_RESULT_DISAGREES") for f in report["failures"])


def test_integrity_positive_control_is_separate_from_semantic_refusal():
    store = admissible_control(verifier.Store(str(ROOT / "docs"), None))
    review, bundle = store.json(f"reviews/{SLUG}/review.json"), store.json(BUNDLE_PATH)
    artifact = next(a for a in bundle["artefacts"] if a["state"] == "SERVED")
    artifact["sha256"] = "0" * 64
    recertify_fixture(store, review, bundle)
    report = verifier.run(store, SLUG, None)
    assert report["verdicts"]["artifact_integrity"] == "FAIL"
    assert report["verdicts"]["publication_eligibility"] == "REFUSED"
    assert any(f.startswith("ARTEFACT_DIGEST_MISMATCH") for f in report["failure_categories"]["integrity"])
    assert report["pool"]["binding_ok"]


def test_producer_emission_boundary_refuses_substitution(monkeypatch):
    from scripts import build_bundle
    original = build_bundle.pooled_reference

    def altered(review):
        reference = original(review)
        plant({"pooled_reference": reference}, "rotated_ids", review)
        return reference

    monkeypatch.setattr(build_bundle, "pooled_reference", altered)
    _, problems = build_bundle.build(SLUG, check_only=True)
    # The contract is that the FIRST SEMANTIC refusal names the defect -- not that it is the first
    # problem overall. Integrity and semantic checks are separate categories (acceptance item (d)), and
    # an integrity problem legitimately precedes: editing any pinned module changes the tree bytes, so
    # `analysis_code_sha256` stops matching the certificate until the corpus is rebuilt. Asserting
    # problems[0] coupled this test to that unrelated state and made it fail on any patched tree.
    # Pinned-module digest complaints name a PATH first, and the mirrored copies under docs/ produce a
    # second family ("docs/harness/gate.py: mirrored bytes differ from the certificate input"), so the
    # prefix set must cover docs/ too -- a first version of this filter missed exactly that one.
    integrity = ("harness/", "scripts/", "docs/", "ARTEFACT_DIGEST_MISMATCH",
                 "SUPPORTING_FILE_DIGEST_MISMATCH", "CERTIFICATE_MISMATCH", "EXECUTION_RECORD_MISMATCH")
    semantic = [p for p in problems if not p.startswith(integrity)]
    assert semantic, f"no semantic problem at all; only integrity noise: {problems}"
    assert semantic[0].startswith("POOL_ROW_IDENTITY_MISMATCH "), problems


def test_publication_cannot_skip_a_deleted_required_bundle(tmp_path):
    from harness.gate import check_bundle_pool
    manifest = (ROOT / "docs/reviews" / SLUG / "manifest.json").read_bytes()
    (tmp_path / "manifest.json").write_bytes(manifest)
    assert any("POOL_BUNDLE_REQUIRED" in p for p in check_bundle_pool(tmp_path))


def test_selected_set_is_named_with_a_declared_multiplicity_rule():
    """Eligible candidates and the SELECTED set are different objects.

    A row that is admissible evidence is not thereby a permitted input to this analysis, and not every
    admissible candidate must be forced into every pool. Naming the set is what makes the invariant checkable
    rather than assumed: every derived statistical input is exactly the permitted derivation of ONE selected
    record. The multiplicity rule is declared rather than implicit because the failure it forbids -- one trial
    contributing several rows to an independent-trial pool -- is arithmetically silent.
    """
    report = verifier.run(admissible_control(verifier.Store(str(ROOT / "docs"), None)), SLUG, None)
    sel = report["pool"]["selected_set"]
    assert sel["identity"] == f"{SLUG}::{report['pool']['selected_set']['identity'].split('::', 1)[1]}"
    assert sel["k_selected"] == len(sel["members"]) == report["pool"]["recomputed"]["k"]
    assert sel["multiplicity_policy"] == "ONE_ROW_PER_TRIAL_FAMILY"
    assert sel["derivation_is_one_per_selected_record"] is True
    # The candidate count cannot be smaller, and unselected members are explicitly disjoint.
    assert sel["candidates_considered"] >= sel["k_selected"]
    assert set(sel["not_selected"]).isdisjoint(sel["members"])


def test_a_repeated_selected_record_breaks_the_declared_multiplicity_rule():
    """A repeated reference must fail membership and multiplicity even with an updated expectation."""
    store = admissible_control(verifier.Store(str(ROOT / "docs"), None))
    review, bundle = store.json(f"reviews/{SLUG}/review.json"), store.json(BUNDLE_PATH)
    original = dict(store.cache)
    plant(bundle, "repeated_pioneer6", review)
    recertify_fixture(store, review, bundle)
    report = verifier.run(store, SLUG, None)
    assert report["verdicts"]["input_linkage"] == "FAIL"
    assert any("POOL_INPUT_" in f for f in report["failure_categories"]["input_linkage"])
    store.cache.clear()
    store.cache.update(original)
    assert verifier.run(store, SLUG, None)["verdicts"]["input_linkage"] == "PASS"


@pytest.mark.skipif(not (ROOT / "f6_repaired.json").is_file(), reason="NOT RUN: f6_repaired.json is absent; do not generate it for this suite")
@pytest.mark.parametrize("case", ("baseline", "reorder_records", "reorder_pool_records", "freedom_decimal_normalisation"))
def test_required_control_publishes_in_full_acceptance_ledger(case):
    # Evidence contract: run scripts/f6_acceptance.py before this acceptance check.
    evidence = json.loads((ROOT / "f6_repaired.json").read_text(encoding="utf-8"))
    row = next(r for r in evidence["cases"] if r["case"] == case)
    assert row["first_refusal"] is None
    stages = {s["stage"]: s for s in row["stages"]}
    for name in ("producer_renderer", "bundle", "publication_gate", "independent_verifier"):
        assert stages[name]["returncode"] == 0, stages[name]
    assert row["five_verdicts"]["publication_eligibility"] == "ELIGIBLE"
    assert row["five_verdicts"]["scientific_admission"] == "FAIL"
    for stage in stages.values():
        assert "POOL_PUBLICATION_INELIGIBLE" not in stage["stdout"] + stage["stderr"]
        assert "certified primary contains inadmissible rows" not in stage["stdout"] + stage["stderr"]


def test_novel_tuple_change_is_not_mislabelled_as_identity_rotation(objects):
    review, bundle, records = objects
    inputs = bundle["pooled_reference"]["inputs"]
    value = verifier._plant_input_values(inputs, review)[0]["effect"]
    inputs[0]["effect"] = value * 1.01
    got = verifier._plant_expected_pool(verifier._plant_input_values(inputs, review))
    bundle["pooled_reference"]["expected"] = {k: got[k] for k in bundle["pooled_reference"]["expected"]}
    _, errors = verifier.check_pool_contract(review, bundle, records)
    assert errors[0].startswith("POOL_INPUT_NOT_A_REFERENCE "), errors
    assert not any(e.startswith("POOL_ROW_IDENTITY_MISMATCH ") for e in errors)


@pytest.mark.parametrize("state", ("INADMISSIBLE", "UNKNOWN", "ADMISSIBLE"))
def test_admission_state_alone_does_not_control_publication(state):
    report = {"failures": [], "rows": [{"final": state}],
              "pool": {"reproduced_to_1e-9": True, "bundle_internal_arithmetic_agrees": True,
                       "certified_result_agrees": True, "binding_ok": True}}
    verifier.separate_verdicts(report)
    assert report["verdicts"]["scientific_admission"] == ("PASS" if state == "ADMISSIBLE" else "FAIL")
    assert report["verdicts"]["publication_eligibility"] == "ELIGIBLE"
