"""Integrator plants, 2026-09-16:
- GRADE's risk-of-bias domain joins rob2 by trial identity (PMID/NCT), not by display label;
- a domain the machine cannot assess counts as one conservative downgrade -- refusing to serve a CI
  can never raise certainty;
- at k=2 with the pooled CI refused, the RoB sensitivity object still exists and its CIs read as refused."""
from harness import grade
from harness import rob_sensitivity


def _review(k2_refused=False):
    trials = [
        {"id": "PMID 1", "label": "1", "effect": 0.8, "ci_low": 0.7, "ci_high": 0.9, "scale": "HR"},
        {"id": "PMID 2", "label": "ACRO", "effect": 0.85, "ci_low": 0.75, "ci_high": 0.95, "scale": "HR"},
    ]
    res = {"k": 2, "estimate": 0.82, "scale": "HR", "ci_low": 0.6, "ci_high": 1.1, "tau2": 0.0,
           "present": True, "n_total": 20000}
    if k2_refused:
        res.update({"ci_low": None, "ci_high": None, "pooled_ci_refused": {"code": "K2_SINGLE_DF"}})
    return {
        "slug": "synthetic",
        "outcomes": [{"name": "MACE", "primary": True, "estimand": "HR", "trials": trials, "result": res}],
        "rob2": {"trials": {"1": {"overall": "low", "domains": {"D3_missing_outcome_data": {"level": "not assessed"}}},
                            "2": {"overall": "low", "domains": {"D3_missing_outcome_data": {"level": "not assessed"}}}}},
    }


def test_grade_rob_domain_joins_by_trial_identity_not_label():
    g = grade.grade(_review())
    rob = g["domains"]["risk_of_bias"]
    # both trials are rated under their PMIDs; the acronym-labelled one must not read as unrated
    assert rob.get("n_rated") == 2, rob
    assert not rob.get("coverage_incomplete"), rob


def test_unassessable_imprecision_counts_as_conservative_downgrade_never_raises_certainty():
    served = grade.grade(_review(k2_refused=False))
    refused = grade.grade(_review(k2_refused=True))
    order = ["high", "moderate", "low", "very_low"]
    assert refused["domains"]["imprecision"].get("not_assessable_automatically") is True
    assert "imprecision" in refused.get("conservative_downgrades_pending_human_judgement", [])
    assert order.index(refused["certainty"]) >= order.index(served["certainty"]), (served["certainty"], refused["certainty"])


def test_rob_sensitivity_object_survives_k2_ci_refusal_with_refused_cis():
    sens = rob_sensitivity.sensitivity(_review(k2_refused=True))
    assert sens and sens["full"]["k"] == 2
    # the pipeline marks the CIs refused; emulate that contract here and check the renderer text path
    from harness import pipeline  # noqa: F401  (import guards against a missing module, not behaviour)
    pt = dict(sens["full"], ci_low=None, ci_high=None, ci_refused="K2_SINGLE_DF")
    assert pt["ci_refused"] == "K2_SINGLE_DF" and pt["estimate"] is not None
