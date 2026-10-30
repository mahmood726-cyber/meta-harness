"""Synthetic source-only checks; NO benchmark review is enrolled."""
import copy
import pytest

from benchmarks.repro300_preflight import preflight, pilot_draw, SelectionRefusal


def case(review="CD999991", family="f1", stratum="COCHRANE"):
    return dict(
        review_id=review, analysis_id="1.1", family_key=family, stratum=stratum,
        source_sha256="a" * 64, source_version="2026-v2.6",
        rights_checked=True, source_download_verified=True,
        prior_exposure=False, source_checked_without_outcomes=True,
        access_path="synthetic-data-package", license_uri="https://example.org/terms",
        rights_scope="LOCAL_NUMERIC_ONLY", planned_use="NUMERIC_ONLY",
    )


def _eight():
    strata = ("COCHRANE", "OPEN_META", "KNOWN_ERROR", "UNSELECTED")
    return [case(f"CD{900000+i}", f"fam-{i}", strata[i % 4]) for i in range(8)]


def test_valid_synthetic_source_only_not_enrolled():
    frame = _eight()
    p = preflight(frame, set())
    d = pilot_draw(p, "c" * 64, frame=frame, previously_exposed_families=set())
    assert p["eligible_candidates"] == 8
    assert all(x["available_candidates"] == 2 for x in d["counts"].values())
    assert len(d["candidate_draw"]) == 8
    assert d["status"] == "CANDIDATES_NOT_FROZEN_NOT_EXECUTED"
    assert pilot_draw(
        p, "c" * 64, frame=frame, previously_exposed_families=set()
    ) == d


def test_familiarity_and_access_not_promoted():
    a = case()
    b = case("CD999992", "f2", "OPEN_META")
    c = case("CD999993", "f3", "UNSELECTED")
    d = case("CD999994", "f4", "KNOWN_ERROR")
    b["rights_checked"] = False
    c["source_download_verified"] = False
    d["source_checked_without_outcomes"] = False
    p = preflight([a, b, c, d], {"F1"})
    assert p["eligible_candidates"] == 0
    assert set(p["refusals_by_reason"]) == {
        "TESTED_LEAKAGE", "ACCESS_RIGHTS_UNVERIFIED",
        "SOURCE_UNAVAILABLE", "OUTCOME_EXPOSURE_UNVERIFIED",
    }


@pytest.mark.parametrize("alter", [
    lambda x: x.update(source_sha256="not-a-hash"),
    lambda x: x.update(analysis_id=""),
    lambda x: x.update(rights_checked="true"),
    lambda x: x.update(review_id="../file"),
    lambda x: x.update(license_uri="not-a-url"),
    lambda x: x.update(rights_scope=None),
])
def test_refuse_invalid_identity_or_evidence(alter):
    x = case()
    alter(x)
    with pytest.raises(SelectionRefusal):
        preflight([x], set())


def test_refuse_same_family_and_duplicate_identity():
    with pytest.raises(SelectionRefusal, match="same-family"):
        preflight([case(), case("CD999992", "F1")], set())
    with pytest.raises(SelectionRefusal, match="duplicate"):
        preflight([case(), case()], set())


def test_missing_sources_are_not_numeric_fail():
    x = case()
    x["source_download_verified"] = False
    p = preflight([x], set())
    assert p["eligible_candidates"] == 0
    assert p["refusals_by_reason"] == {"SOURCE_UNAVAILABLE": 1}
    assert not any("FAIL" in key for key in p["refusals_by_reason"])


def test_nonempty_candidate_does_not_imply_actual_enrolment():
    p = preflight([case()], set())
    d = pilot_draw(
        p, "a" * 64, frame=[case()], previously_exposed_families=set()
    )
    assert d["counts"]["COCHRANE"]["available_candidates"] == 1
    assert d["status"] == "BLOCKED_INSUFFICIENT_ELIGIBLE_CANDIDATES"
    assert not d["candidate_draw"]


def test_preflight_custody_binds_exposure_inventory():
    frame = [case()]
    a = preflight(frame, set())
    b = preflight(frame, {"f1"})
    assert a["source_only_frame_sha256"] == b["source_only_frame_sha256"]
    assert a["exposure_inventory_sha256"] != b["exposure_inventory_sha256"]
    assert a["eligible_candidates"] == 1 and b["eligible_candidates"] == 0
    with pytest.raises(SelectionRefusal, match="preflight mismatch"):
        pilot_draw(
            a, "c" * 64, frame=frame, previously_exposed_families={"f1"}
        )


def test_refuse_injected_candidate_from_stale_or_forged_preflight():
    frame = _eight()
    p = preflight(frame, set())
    p["candidates"].append(case("CD999999", "injected", "OPEN_META"))
    with pytest.raises(SelectionRefusal, match="preflight mismatch"):
        pilot_draw(
            p, "c" * 64, frame=frame, previously_exposed_families=set()
        )


def test_refuse_candidate_source_digest_tamper():
    frame = _eight()
    p = preflight(frame, set())
    p["candidates"][0]["source_sha256"] = "b" * 64
    with pytest.raises(SelectionRefusal, match="preflight mismatch"):
        pilot_draw(
            p, "c" * 64, frame=frame, previously_exposed_families=set()
        )


def test_refuse_source_frame_drift_after_preflight():
    frame = _eight()
    p = preflight(frame, set())
    mutated = copy.deepcopy(frame)
    mutated[0]["source_sha256"] = "b" * 64
    with pytest.raises(SelectionRefusal, match="preflight mismatch"):
        pilot_draw(
            p, "c" * 64, frame=mutated, previously_exposed_families=set()
        )


def test_missing_stratum_refuses_pilot_draw_instead_of_short_enrolment():
    strata = ("COCHRANE", "OPEN_META", "KNOWN_ERROR")
    frame = [
        case(f"CD{900000+i}", f"fam-{i}", strata[i % 3])
        for i in range(6)
    ]
    p = preflight(frame, set())
    d = pilot_draw(
        p, "c" * 64, frame=frame, previously_exposed_families=set()
    )
    assert d["status"] == "BLOCKED_INSUFFICIENT_ELIGIBLE_CANDIDATES"
    assert not d["candidate_draw"]
    assert d["counts"]["UNSELECTED"]["available_candidates"] == 0


def test_refuse_bool_as_pilot_required_count():
    frame = [case()]
    p = preflight(frame, set())
    with pytest.raises(SelectionRefusal):
        pilot_draw(
            p, "c" * 64, frame=frame,
            previously_exposed_families=set(), per_stratum=True
        )


def test_ai_extraction_source_cannot_use_numeric_only_permission():
    c = case()
    c["planned_use"] = "AI_ASSISTED_EXTRACTION"
    p = preflight([c], set())
    assert p["eligible_candidates"] == 0
    assert p["refusals_by_reason"] == {"PROCESSING_RIGHTS_MISMATCH": 1}
    c["rights_scope"] = "AI_PROCESSING_PERMITTED"
    assert preflight([c], set())["eligible_candidates"] == 1


def test_reject_unhashable_stratum_without_runtime_traceback():
    c = case()
    c["stratum"] = {"COCHRANE": "true"}
    with pytest.raises(SelectionRefusal, match="invalid stratum"):
        preflight([c], set())


def test_reject_same_review_multiple_analyses_cross_strata():
    # v0.2 FALSE PASS: CD999991's two analyses could count as two reviews.
    first = case("CD999991", "family-A", "COCHRANE")
    second = case("CD999991", "family-B", "KNOWN_ERROR")
    second["analysis_id"] = "2.4"
    with pytest.raises(SelectionRefusal, match="duplicate review identity"):
        preflight([first, second], set())


def test_reject_case_variant_same_doi_cross_analyses():
    first = case("10.1000/ABC.1", "family-A", "OPEN_META")
    second = case("10.1000/abc.1", "family-B", "UNSELECTED")
    second["analysis_id"] = "3.2"
    with pytest.raises(SelectionRefusal, match="duplicate review identity"):
        preflight([first, second], set())


def test_refuse_cochrane_cd_vs_versioned_doi_alias():
    first = case("CD013505", "family-A", "COCHRANE")
    second = case("10.1002/14651858.CD013505.pub2", "family-B", "KNOWN_ERROR")
    second["analysis_id"] = "2.4"
    with pytest.raises(SelectionRefusal, match="duplicate review identity"):
        preflight([first, second], set())


def test_refuse_two_versioned_doi_aliases():
    first = case("10.1002/14651858.CD013505.pub2", "family-A", "COCHRANE")
    second = case("10.1002/14651858.cd013505.PUB3", "family-B", "OPEN_META")
    second["analysis_id"] = "3.1"
    with pytest.raises(SelectionRefusal, match="duplicate review identity"):
        preflight([first, second], set())


def test_distinct_cochrane_review_dois_stay_distinct():
    first = case("10.1002/14651858.CD013505.pub2", "family-A", "COCHRANE")
    second = case("10.1002/14651858.CD013506.pub2", "family-B", "OPEN_META")
    assert preflight([first, second], set())["eligible_candidates"] == 2


def test_allow_different_reviews_with_distinct_families():
    first = case("10.1000/ABC.1", "family-A", "OPEN_META")
    second = case("10.1000/ABC.2", "family-B", "UNSELECTED")
    second["analysis_id"] = "3.2"
    assert preflight([first, second], set())["eligible_candidates"] == 2


def test_development_module_does_not_rewrite_historical_certificate_scope():
    # A new module under harness/ changed the historic 'not-covered' disclosure,
    # which is release-hashed, failing all 32 sealed certificates. Keep genuine
    # development-only selection tooling separate from the signed replay code.
    import json
    from pathlib import Path
    from harness import certificate
    root = Path(__file__).resolve().parents[1]
    assert not (root / "harness/repro300_preflight.py").exists()
    saved = json.loads(
        (root / "docs/reviews/glp1-ra-mace-t2d/CERTIFICATE.json").read_text(encoding="utf-8")
    )
    assert certificate._scope(saved["analysis_code_blobs"]) == saved["certificate_scope"]
