import json
import subprocess

from harness import compat_check as C
from harness import unit_of_analysis as U


def _pre_fix_review(slug):
    data = subprocess.check_output(
        ["git", "show", f"aa8ed28a:docs/reviews/{slug}/review.json"],
        text=True,
        encoding="utf-8",
    )
    return json.loads(data)


def _records(slug):
    with open(f"cache/{slug}/records.json", encoding="utf-8") as f:
        return json.load(f)


def _by_dim(violations):
    return {v["dimension"]: v for v in violations if v["code"] == C.ASSERTED_NOT_UNDERLYING}


def test_pre_fix_probiotics_key_fires_on_underlying_trial_rows():
    review = _pre_fix_review("probiotics-aad-prevention")
    violations = C.check(review, _records("probiotics-aad-prevention"))
    by_dim = _by_dim(violations)
    assert {"analysis_set", "follow_up_window", "endpoint"} <= set(by_dim)

    analysis = by_dim["analysis_set"]["per_trial_values"]
    spaada = next(x for x in analysis if x["trial_id"] == "39529939")
    placide = next(x for x in analysis if x["trial_id"] == "23932219")
    assert spaada["value"] == "completers efficacy set"
    assert "no efficacy data" in spaada["span"]
    assert placide["value"] == "modified intention-to-treat"
    assert "modified intention-to-treat" in placide["span"]

    endpoint = by_dim["endpoint"]["per_trial_values"]
    kotowska = next(x for x in endpoint if x["trial_id"] == "15740542")
    assert "otherwise-unexplained" in kotowska["value"]


def test_post_fix_probiotics_key_is_mixed_and_no_asserted_violation():
    with open("docs/reviews/probiotics-aad-prevention/review.json", encoding="utf-8") as f:
        review = json.load(f)
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    ck = primary["compat_key"]
    assert ck["analysis_set"].startswith("mixed (")
    assert ck["follow_up_window"].startswith("trial-defined")
    assert ck["endpoint"].startswith("trial-defined antibiotic-associated diarrhoea")
    assert ck["dimension_matches"]["analysis_set"] is False
    assert ck["dimension_matches"]["follow_up_window"] is False
    assert ck["dimension_matches"]["endpoint"] is False
    assert not C.page_gate_violations(review, _records("probiotics-aad-prevention"))


def test_comparator_population_match_is_derived_false_for_adult_comparator_with_paediatric_pool():
    review = _pre_fix_review("probiotics-aad-prevention")
    C.enrich(review, _records("probiotics-aad-prevention"))
    scope = review["comparator"]["scope"]
    assert scope["topic_is_class"] is True
    assert scope["population_match"] is False
    paediatric = scope["population_match_basis"]["pool_has_paediatric_trials"]
    assert any(x["trial_id"] in {"40488914", "15740542", "18701826"} for x in paediatric)


def test_synthetic_uniform_trials_have_no_violation_and_missing_field_is_underivable():
    uniform = {
        "slug": "synthetic",
        "outcomes": [{
            "name": "Mortality",
            "compat_key": {
                "analysis_set": "intention-to-treat",
                "follow_up_window": "28 days",
                "endpoint": "Mortality",
            },
            "timepoint": "28 days",
            "trials": [
                {"id": "PMID 1", "source": "analysis was by intention-to-treat; mortality at 28 days"},
                {"id": "PMID 2", "source": "analysis was by intention-to-treat; mortality at 28 days"},
            ],
        }],
    }
    assert C.check(uniform, {"records": []}) == []

    missing = {
        "slug": "synthetic",
        "outcomes": [{
            "name": "Mortality",
            "compat_key": {"analysis_set": "intention-to-treat"},
            "trials": [{"id": "PMID 3"}],
        }],
    }
    violations = C.check(missing, {"records": []})
    assert violations[0]["code"] == C.UNDERIVABLE
    assert violations[0]["dimension"] == "analysis_set"


def test_omega_harms_incomplete_suppresses_isolated_single_trial_harm_number():
    review = _pre_fix_review("omega3-cardiovascular-events")
    C.enrich(review, _records("omega3-cardiovascular-events"))
    af = next(o for o in review["outcomes"] if o["name"] == "Atrial fibrillation")
    assert af["result"]["state"] == C.HARMS_INCOMPLETE
    unresolved = af["result"]["known_eligible_outcome_reports_unresolved"]
    assert any(x["trial_id"] == "30415628" for x in unresolved)
    assert any("atrial fibrillation" in x["span"] for x in unresolved)


def test_alpha_omega_publication_text_counts_as_factorial_despite_registry_silence():
    text = ("we randomly assigned 4837 patients to receive for 40 months one of four trial margarines: "
            "a margarine supplemented with a combination of EPA and DHA, a margarine supplemented with "
            "ALA, a margarine supplemented with EPA-DHA and ALA, or a placebo margarine")
    detail = U.detect_detail(text)
    assert detail["design"] == "factorial"


def test_risk_and_prevention_endpoint_refusal_persists():
    with open("docs/reviews/omega3-cardiovascular-events/review.json", encoding="utf-8") as f:
        review = json.load(f)
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    refused = [x for x in primary.get("declared_absent_trials", []) if x.get("id") == "PMID 23656645"]
    assert refused
    assert "REVISED primary endpoint" in refused[0]["reason"]
