"""R9-2: a trial's lifecycle comes from its VERIFIED registry overall_status, and its completion dates are kept as the
registry gives them -- WHICH completion (primary v study) and of WHICH type (actual v anticipated/estimated) -- never
folded together and never inferred from the record's path. Auditor dispute (finerenone FineCaRe, NCT07026539): R9 said
'completion 2028', R9b said 'primary completion 31 Dec 2026 (estimated)'; the registry says RECRUITING, primary
completion 2026-12-31 ESTIMATED, study completion 2028-04-30 ESTIMATED -- both auditors quoted a real date of a
different completion."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from harness import aact, pipeline  # noqa: E402

FINECARE = {"overall_status": "RECRUITING", "completion_date": "2028-04-30", "completion_date_type": "ESTIMATED",
            "primary_completion_date": "2026-12-31", "primary_completion_date_type": "ESTIMATED"}


def rec(nct, **kw):
    return dict({"id": nct, "nct": nct, "id_type": "nct"}, **kw)


def test_PLANT_finecare_is_ongoing_with_both_completions_kept_by_type():
    a = pipeline._completeness_for_record(rec("NCT07026539"), {"NCT07026539": FINECARE})
    assert a["completeness_state"] == "eligible+ongoing"
    assert a["primary_completion_date"] == "2026-12-31" and a["primary_completion_date_type"] == "ESTIMATED"
    assert a["completion_date"] == "2028-04-30" and a["completion_date_type"] == "ESTIMATED"


def test_PLANT_suspended_and_unknown_are_never_completed():
    for st, want in (("SUSPENDED", "eligible+suspended"), ("UNKNOWN", "eligible+status_unknown")):
        a = pipeline._completeness_for_record(rec("NCT1"), {"NCT1": {"overall_status": st}})
        assert a["completeness_state"] == want, st


def test_PLANT_a_publication_without_a_verified_registry_status_is_not_called_completed():
    a = pipeline._completeness_for_record({"id": "12345678", "id_type": "pmid"}, {})
    assert a["completeness_state"] == "eligible+published+registry_status_unverified"


def test_a_completed_trial_with_results_is_still_completed():
    d = {"NCT2": {"overall_status": "COMPLETED", "results_first_posted_date": "2020-01-01",
                  "completion_date": "2019-06-30", "completion_date_type": "ACTUAL"}}
    assert pipeline._completeness_for_record(rec("NCT2"), d)["completeness_state"] == "eligible+completed+results_available"


def test_PLANT_aact_study_dates_never_folds_primary_completion_into_completion(tmp_path, monkeypatch):
    hdr = ("nct_id|overall_status|start_date|completion_date|completion_date_type|primary_completion_date|"
           "primary_completion_date_type|study_first_submitted_date|results_first_posted_date")
    (tmp_path / "studies.txt").write_text(hdr + "\nNCT07026539|RECRUITING|2025-06-01||ESTIMATED|2026-12-31|ESTIMATED||\n",
                                          encoding="utf-8")
    monkeypatch.setattr(aact, "_table", lambda name, root=None: str(tmp_path / f"{name}.txt"))
    d = aact.study_dates(["NCT07026539"])["NCT07026539"]
    assert d["completion_date"] in (None, "") and d["primary_completion_date"] == "2026-12-31"
    assert d["primary_completion_date_type"] == "ESTIMATED"


# ---------------------------------------------------------------------------------------- codex r9-2-lifecycle-r1
def _topic(tmp_path, monkeypatch, ids):
    import json as _j
    import r9_2_lifecycle_sweep as SW
    monkeypatch.setattr(SW, "ROOT", str(tmp_path))
    monkeypatch.setattr(SW, "OUT", str(tmp_path / "out.json"))
    (tmp_path / "docs" / "reviews" / "t").mkdir(parents=True)
    (tmp_path / "cache" / "t").mkdir(parents=True)
    (tmp_path / "docs" / "reviews" / "t" / "review.json").write_text(_j.dumps({"screening": {"records": [
        {"id": i, "completeness_state": "eligible+ongoing"} for i in ids]}}), encoding="utf-8")
    (tmp_path / "cache" / "t" / "records.json").write_text(_j.dumps({"records": [
        {"id": "NCT1", "nct": "NCT1", "id_type": "nct"}]}), encoding="utf-8")
    return SW


def test_PLANT_r1_1_a_cache_that_fails_to_load_marks_the_topic_unverified(tmp_path, monkeypatch):
    from harness import aact_cache
    SW = _topic(tmp_path, monkeypatch, ["NCT1"])

    def boom(slug):
        raise OSError("disk")
    monkeypatch.setattr(aact_cache, "load", boom)
    out = SW.main()
    assert out["topics"]["t"]["state"].startswith("UNVERIFIED:CACHE_LOAD_FAILED") and out["topics"]["t"]["changed"] == 0


def test_PLANT_r1_2_annotations_without_a_cached_record_are_counted_as_unchecked(tmp_path, monkeypatch):
    from harness import aact_cache
    SW = _topic(tmp_path, monkeypatch, ["NCT1", "NCT404"])
    monkeypatch.setattr(aact_cache, "load", lambda slug: {"values": {"study_dates": {"NCT1": {"overall_status": "RECRUITING"}}}})
    out = SW.main()
    assert out["topics"]["t"]["annotated"] == 2 and out["topics"]["t"]["unchecked"] == ["NCT404"]
