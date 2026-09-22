"""A family ledger that is ELIGIBLE BY CONSTRUCTION, for tests of OTHER mechanisms.

Since 2026-09-21 the build reads the admission decision at the pooling convergence point (harness/admission.py,
on by default): a row whose family eligibility is not ELIGIBLE -- including a build handed no family ledger at all --
is set aside, never pooled. Tests that exercise source hierarchy, verified inputs, harms recovery or endpoint
binding on synthetic records therefore hand `_build_outcome` a ledger that declares every synthetic record eligible,
with a synthetic span that says so. A test of admission itself (tests/test_admission_enforced.py) never uses this.
"""
from __future__ import annotations

from harness import identity
from harness.trial_family import cell


def eligible_by_construction(rec_by_id):
    """One ELIGIBLE family per record id (keys of a rec_by_id dict, or ids of an `included` decision list)."""
    ids = list(rec_by_id.keys()) if isinstance(rec_by_id, dict) else [d.get("id") for d in rec_by_id]
    nodes = []
    for n, rid in enumerate(ids, 1):
        rid = identity._norm(rid)
        nodes.append({
            "family_id": f"synthetic-family-{n}",
            "identity_basis": {"registry_ids": [f"NCT-SYNTHETIC-{n}"], "primary_report_ids": [rid], "fallback_report_ids": []},
            "reports": [{"report_id": rid, "role": "PRIMARY", "retrieved_via": ["synthetic fixture"]}],
            "source_records": [{"id": rid, "id_type": "pmid"}],
            "eligibility": cell("ELIGIBLE", {"source": "synthetic fixture", "quote": "eligible by construction (test ledger)"}),
            "outcome_status": [], "randomised_contrasts": [], "arms": [], "population": {},
            "aliases": {"acronym": []}, "lifecycle": {}, "poolability": [], "is_trial_family": True,
        })
    return nodes
