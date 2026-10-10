"""scripts/blinded_review.py: the deterministic parts that decide CONFIRMED vs UNCONFIRMED.

A blinded review is only as good as its adjudicator: these tests plant the cases it must refuse (a quote that is not on
the page, a number check whose two values are equal) and check the independent pool recompute against a served pool.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import blinded_review as B  # noqa: E402


def test_independent_recompute_reproduces_a_served_pool():
    # dpp4-mace-t2d's primary outcome: k=4, served HR 1.0007 (0.8998-1.1129), tau2 0 -- computed by the harness's own code
    review = json.loads((ROOT / "docs" / "reviews" / "dpp4-mace-t2d" / "review.json").read_text(encoding="utf-8"))
    r = B.recompute(review["outcomes"][0])
    assert r["status"] == "AGREES", r


def test_recompute_reports_differs_when_the_served_pool_is_wrong():
    review = json.loads((ROOT / "docs" / "reviews" / "dpp4-mace-t2d" / "review.json").read_text(encoding="utf-8"))
    o = json.loads(json.dumps(review["outcomes"][0]))
    o["result"]["estimate"] = round(o["result"]["estimate"] * 1.05, 4)        # plant: a served pool 5% off
    assert B.recompute(o)["status"] == "DIFFERS"


def test_recompute_refuses_rather_than_guesses_when_rows_do_not_match_k():
    review = json.loads((ROOT / "docs" / "reviews" / "dpp4-mace-t2d" / "review.json").read_text(encoding="utf-8"))
    o = json.loads(json.dumps(review["outcomes"][0]))
    o["trials"] = o["trials"][:2]
    assert B.recompute(o)["status"] == "CANNOT_RECOMPUTE"


def test_quote_gate_normalises_markup_and_typography_but_not_content():
    page = B.norm(B.page_text("<p>Hazard ratio <strong>0.80</strong> (95%&nbsp;CI 0.60–1.06)</p>"))
    assert B.contains(page, "Hazard ratio 0.80 (95% CI 0.60-1.06)")
    assert not B.contains(page, "Hazard ratio 0.81 (95% CI 0.60-1.06)")
    assert not B.contains(page, "0.80")                       # too short to identify a span


def _job(tmp_path, slug="t"):
    d = tmp_path / slug
    d.mkdir(parents=True)
    job = {"n": 99, "slug": slug, "commit": "c" * 40, "page_text": "=== TAB: Data extraction ===\nTrial A HR 0.80 (0.60 to 1.06) served",
           "sources": [{"url": "https://pubmed.ncbi.nlm.nih.gov/1/", "ref": "PubMed/CT.gov record 1 (ABSTRACT)",
                        "kind": "ABSTRACT", "sha256": "x", "text": "the rate ratio was 0.85 (95% CI, 0.60-1.06) overall"}],
           "dropped_by_licence": [], "recompute": []}
    (d / "input.json").write_text(json.dumps(job), encoding="utf-8")
    return d


def _finding(**kw):
    f = {"tab": "Data extraction", "page_quote": "Trial A HR 0.80 (0.60 to 1.06)", "severity": "changes_number",
         "source_evidence": {"url": "https://pubmed.ncbi.nlm.nih.gov/1/", "quote": "the rate ratio was 0.85 (95% CI"},
         "claim": "x", "served_value": "0.80", "source_value": "0.85"}
    f.update(kw)
    return f


def _run(tmp_path, monkeypatch, findings):
    monkeypatch.setattr(B, "OUT", str(tmp_path))
    d = _job(tmp_path)
    (d / "codex.json").write_text(json.dumps({"state": "RAN_OK", "response": {"findings": findings, "numeric_checks": [],
                                                                               "screening_sample": []}}), encoding="utf-8")
    return B.adjudicate("t")["findings"]


def test_one_model_plus_a_passing_typed_number_check_is_confirmed(tmp_path, monkeypatch):
    [f] = _run(tmp_path, monkeypatch, [_finding()])
    assert f["status"] == "CONFIRMED_TYPED" and f["typed_check"] == "spans+number"


def test_a_page_quote_not_on_the_page_is_never_confirmed(tmp_path, monkeypatch):
    [f] = _run(tmp_path, monkeypatch, [_finding(page_quote="Trial A HR 0.70 (0.60 to 1.06)")])
    assert f["status"] == "UNCONFIRMED" and f["why_unconfirmed"] == "page quote not on the page"


def test_a_source_quote_not_in_the_shown_source_is_never_confirmed(tmp_path, monkeypatch):
    [f] = _run(tmp_path, monkeypatch, [_finding(source_evidence={"url": "https://pubmed.ncbi.nlm.nih.gov/1/",
                                                                 "quote": "the rate ratio was 0.75 (95% CI"})])
    assert f["status"] == "UNCONFIRMED"


def test_a_number_finding_whose_values_are_equal_is_not_confirmed(tmp_path, monkeypatch):
    [f] = _run(tmp_path, monkeypatch, [_finding(source_value="0.80")])
    assert f["status"] == "UNCONFIRMED" and "number check failed" in f["why_unconfirmed"]


def test_wording_findings_are_confirmed_only_as_spans_and_say_so(tmp_path, monkeypatch):
    [f] = _run(tmp_path, monkeypatch, [_finding(severity="changes_wording", served_value="", source_value="")])
    assert f["status"] == "CONFIRMED_TYPED" and f["typed_check"] == "spans"


def test_a_topic_no_model_reviewed_is_not_reported_as_zero_findings(tmp_path, monkeypatch):
    """9 Oct: a selection bug ran no model on 21 topics and the adjudicator printed '0 findings' for each."""
    monkeypatch.setattr(B, "OUT", str(tmp_path))
    _job(tmp_path)
    r = B.adjudicate("t")
    assert r["reviewed"] is False and r["status"] == "NO_MODEL_RAN"


def test_run_refuses_a_selection_that_names_no_prepared_topic(tmp_path, monkeypatch):
    import argparse
    import pytest
    monkeypatch.setattr(B, "OUT", str(tmp_path))
    _job(tmp_path)
    with pytest.raises(SystemExit, match="REFUSED"):
        B.cmd_run(argparse.Namespace(only="t/,nope/", model="codex", workers=1))


def test_a_middle_dot_decimal_is_read_as_one_number():
    """9 Oct: 'p=0·045' was read as 0 and 45, so a check passed for the wrong reason."""
    assert B.numbers("p=0·045") == [0.045]
    assert B.numbers("1,138 of 2,124") == [1138.0, 2124.0]


def test_model_numeric_checks_are_compared_by_us_not_by_the_models_boolean():
    base = dict(served_estimate=0.91, served_ci_low=0.75, served_ci_high=1.10, agrees=False)
    assert B.model_numeric_state(dict(base, recomputed_estimate=0.9101, recomputed_ci_low=0.7499,
                                      recomputed_ci_high=1.1004)) == "AGREES"
    assert B.model_numeric_state(dict(base, recomputed_estimate=0.95, recomputed_ci_low=0.75,
                                      recomputed_ci_high=1.10, agrees=True)) == "DIFFERS"
    # a withheld served CI arrives as the schema placeholder 0/0: nothing to compare
    assert B.model_numeric_state(dict(served_estimate=0.97, served_ci_low=0, served_ci_high=0, recomputed_estimate=0.97,
                                      recomputed_ci_low=0.65, recomputed_ci_high=1.46)) == "NOT_ASSESSABLE"


def test_agreement_tolerance_follows_the_served_rounding():
    """9 Oct: served 0.61 (0.01-51.59) vs recomputed 0.6064 (0.0071-51.5861) was scored DIFFERS at a fixed 0.002."""
    c = dict(served_estimate=0.61, served_ci_low=0.01, served_ci_high=51.59, recomputed_estimate=0.606409,
             recomputed_ci_low=0.007128, recomputed_ci_high=51.5861)
    assert B.model_numeric_state(c) == "AGREES"
    assert B.model_numeric_state(dict(c, recomputed_estimate=0.62)) == "DIFFERS"


def _guard_job(pmid):
    return {"slug": "x", "n": 1, "url": "u", "commit": "c" * 40, "page_sha256": "p", "pack_section": "s", "tuples": [],
            "page_text": "page", "sources": [{"ref": f"held open text PMID {pmid} (HELD_CACHE_FT)", "sha256": "a" * 64,
                                                "url": f"https://europepmc.org/article/MED/{pmid}", "kind": "FULLTEXT",
                                                "text": "A trial sentence of full text. " * 400}]}


def test_the_call_time_licence_guard_sees_every_source_block():
    """9 Oct: sources outside <<<TEXT ... TEXT>>> were invisible to the guard; a non-open full text must now be caught."""
    job = _guard_job("99999999")                              # no open copy recorded for this PMID
    assert B.guard_problems(job, B.build_prompt(job)), "the guard did not see a non-open full-text block"


def test_two_models_agree_across_loose_tab_names_and_are_listed_once(tmp_path, monkeypatch):
    monkeypatch.setattr(B, "OUT", str(tmp_path))
    d = _job(tmp_path)
    resp = lambda tab: {"findings": [_finding(tab=tab, severity="changes_wording", served_value="", source_value="")],
                        "numeric_checks": [], "screening_sample": []}
    (d / "codex.json").write_text(json.dumps({"state": "RAN_OK", "response": resp("Data extraction")}), encoding="utf-8")
    (d / "gemini.json").write_text(json.dumps({"state": "RAN_OK", "response": resp("Data extraction tab")}), encoding="utf-8")
    fs = B.adjudicate("t")["findings"]
    assert {f["status"] for f in fs} == {"CONFIRMED_2MODEL"}
    import argparse
    out = tmp_path / "h.md"
    B.cmd_handover(argparse.Namespace(out=str(out), header="# h"))
    assert out.read_text(encoding="utf-8").count("- **99. t**") == 1        # the pair is ONE handover item


def test_a_quota_with_an_hours_long_reset_is_named_not_retried():
    e = 'client exited 3: error: Individual quota reached. Please upgrade your subscription. Resets in 4h31m28s.'
    assert B.quota_reset(e) == "4h31m28s"
    assert B.quota_reset("client exited 1: rate limited, try again") is None


def test_items_missing_schema_keys_are_dropped_and_counted_not_guessed(tmp_path, monkeypatch):
    monkeypatch.setattr(B, "OUT", str(tmp_path))
    d = _job(tmp_path)
    resp = {"findings": [_finding()], "numeric_checks": [{"outcome": "x", "k": 2}],
            "screening_sample": [{"nct_id": "NCT1", "agrees_with_abstract": True}]}
    (d / "gemini.json").write_text(json.dumps({"state": "RAN_OK", "response": resp}), encoding="utf-8")
    r = B.adjudicate("t")
    assert r["schema_violations"] == {"gemini": {"numeric_checks": 1, "screening_sample": 1}}
    assert r["screening"] == [] and len(r["findings"]) == 1


def test_a_finding_refuted_by_hand_is_listed_as_refuted_never_as_a_defect(tmp_path, monkeypatch):
    """10 Oct: a typed-confirmed number claim (STRENGTH 1.05 vs 0.99) was refuted by hand: different endpoints."""
    monkeypatch.setattr(B, "OUT", str(tmp_path))
    d = _job(tmp_path)
    (d / "gemini.json").write_text(json.dumps({"state": "RAN_OK", "response": {"findings": [_finding()],
                                   "numeric_checks": [], "screening_sample": []}}), encoding="utf-8")
    B.adjudicate("t")
    (tmp_path / "manual_checks.json").write_text(json.dumps({"t#gemini#1": {"class": "changes_number",
        "verdict": "NOT_A_DEFECT", "checked": "by hand", "note": "different endpoint"}}), encoding="utf-8")
    import argparse
    out = tmp_path / "h.md"
    B.cmd_handover(argparse.Namespace(out=str(out), header="# h"))
    txt = out.read_text(encoding="utf-8")
    assert "## changes_number: 0" in txt and "REFUTED (not handed over as defects): 1" in txt
