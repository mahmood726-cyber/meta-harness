"""V1.0.1 ROOT OF TRUST (auditor, 2026-09-26): BUNDLE.json was pinned nowhere, yet the verifier loaded it first and trusted it.
A self-consistent rewrite -- LEADER's pooled input 0.87 [0.78, 0.97] -> 1.20 [1.08, 1.33] with pooled_reference.expected
recomputed -- left the certificate, release_sha256 and review_sha256 unchanged.

Now the certificate pins the bundle's core (bundle_core_sha256, a hash input to release_sha256), and the verifier checks that pin
FIRST: BUNDLE_DIGEST_MISMATCH before any scientific predicate, with nothing computed. Plants fired on the pre-fix verifier."""
import json
from pathlib import Path

import pytest

from harness import certificate
from scripts import verify_bundle as verifier

ROOT = Path(__file__).resolve().parents[1]
SLUG = "glp1-ra-mace-t2d"
BUNDLE = f"reviews/{SLUG}/BUNDLE.json"
LEADER = "PMID 27295427"


def _store():
    return verifier.Store(str(ROOT / "docs"), None)


def _rewrite_leader(raw):
    # the auditor's rewrite in V1.0.1's format: LEADER's pooled reference carries 1.20 [1.08, 1.33], and expected is recomputed
    # from the values that would then be pooled -- a CONSISTENT rewrite of the bundle alone
    b = json.loads(raw)
    review = json.loads((ROOT / "docs" / "reviews" / SLUG / "review.json").read_text(encoding="utf-8"))
    ins = b["pooled_reference"]["inputs"]
    next(i for i in ins if i["id"] == LEADER).update(effect=1.20, ci_low=1.08, ci_high=1.33)
    b["pooled_reference"]["expected"] = verifier._plant_expected_pool(verifier._plant_input_values(ins, review))
    return json.dumps(b, indent=1).encode("utf-8")


class Computed(AssertionError):
    pass


def test_authentic_then_self_consistent_rewrite_then_restore(monkeypatch):
    store = _store()
    original = store.get(BUNDLE)
    assert verifier.run(store, SLUG, None)["verdicts"]["artifact_integrity"] == "PASS"

    store.cache[BUNDLE] = _rewrite_leader(original)
    real_pool = verifier.pool

    def sentinel(*a, **k):
        raise Computed("a scientific predicate ran on an unpinned bundle")
    monkeypatch.setattr(verifier, "pool", sentinel)
    rep = verifier.run(store, SLUG, None)
    assert rep["verdict"] == "FAIL"
    assert rep["verdicts"]["artifact_integrity"] == "FAIL"
    assert [f for f in rep["failures"] if f.startswith("BUNDLE_DIGEST_MISMATCH")], rep["failures"]
    assert rep["failures"][0].startswith("BUNDLE_DIGEST_MISMATCH")          # FIRST, before anything scientific
    assert rep["rows"] == [] and rep["verdicts"]["publication_eligibility"] == "REFUSED"

    monkeypatch.setattr(verifier, "pool", real_pool)
    store.cache[BUNDLE] = original
    assert verifier.run(store, SLUG, None)["verdicts"]["artifact_integrity"] == "PASS"


def test_a_bundle_only_change_moves_the_release_identity():
    raw = (ROOT / "docs" / BUNDLE).read_bytes()
    a = certificate.bundle_core_sha256(json.loads(raw))
    b = certificate.bundle_core_sha256(json.loads(_rewrite_leader(raw)))
    assert a != b
    cert = json.loads((ROOT / "docs" / "reviews" / SLUG / "CERTIFICATE.json").read_text(encoding="utf-8"))
    assert cert["bundle_core_sha256"] == a and "bundle_core_sha256" in cert["hash_inputs"]


def test_the_verifier_and_the_producer_define_the_same_core():
    raw = json.loads((ROOT / "docs" / BUNDLE).read_text(encoding="utf-8"))
    assert verifier._bundle_core_sha256(raw) == certificate.bundle_core_sha256(raw)
    assert verifier.BUNDLE_RELEASE_BOUND_TOP == certificate.BUNDLE_RELEASE_BOUND_TOP
    assert verifier.BUNDLE_RELEASE_BOUND_EVIDENCE_VERSION == certificate.BUNDLE_RELEASE_BOUND_EVIDENCE_VERSION


@pytest.mark.parametrize("field", ["certificate", "review_files", "source"])
def test_the_excluded_fields_are_exactly_the_release_bound_ones(field):
    # the core must not depend on these (else pinning the bundle in the certificate is a cycle) ...
    raw = json.loads((ROOT / "docs" / BUNDLE).read_text(encoding="utf-8"))
    changed = dict(raw, **{field: "CHANGED"})
    assert certificate.bundle_core_sha256(changed) == certificate.bundle_core_sha256(raw)


def test_every_scientific_field_is_inside_the_core():
    # ... and must depend on everything the verifier trusts for science
    raw = json.loads((ROOT / "docs" / BUNDLE).read_text(encoding="utf-8"))
    base = certificate.bundle_core_sha256(raw)
    for key in ("pooled_reference", "verification_rows", "artefacts", "documents"):
        assert certificate.bundle_core_sha256(dict(raw, **{key: "CHANGED"})) != base, key
