"""Plants (external audit review 26-A / 12-03 / 04-2): the compatibility-panel fields of a served row bind to THE ROW'S
SELECTED OUTCOME, not to the first regex hit over the row's source + span + title + whole abstract.

- CAPE COD (cortico-CAP, 36942789), all-cause mortality: the follow-up was '14 days' -- the hydrocortisone TAPER
  ('tapering for a total of 8 or 14 days'). The row's own span says 'By day 28, death had occurred ...'.
- Torres (cortico-CAP, 25688779): 'The primary outcome was treatment failure (...)' was attached to the MORTALITY and the
  HYPERGLYCAEMIA rows. A primary-outcome clause binds only to the row whose outcome IS that primary.
- Melatonin (20712869), sleep-onset latency: the analysis set was 'completers', from the EXTENSION re-randomisation
  sentence; the row's own source says 'Pre-planned analysis on ITT'.
- Denosumab FREEDOM (19671655): 'The primary end point was new vertebral fracture' was attached to the nonvertebral and
  hip rows. The analysis set 'intention-to-treat' is the protocol's declaration, not trial-reported: it must say so.
Each test reads the served review and held records of this tree, and failed on main a8a7c4b6.
"""
from __future__ import annotations

import json
import os

from harness import compat_check as cc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _row(slug, outcome, pid):
    review = json.load(open(os.path.join(ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8"))
    records = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))
    o = next(x for x in review["outcomes"] if x["name"] == outcome)
    t = next(x for x in o["trials"] if str(x.get("id", "")).replace("PMID ", "") == pid)
    return cc.derive_trial_dimensions(review, o, t, records, cc._topic_definition_audit(slug, review))


def test_cape_cod_follow_up_is_the_outcome_window_not_the_treatment_taper():
    d = _row("corticosteroids-cap-mortality", "All-cause mortality", "36942789")
    assert d["follow_up_window"]["value"] == "28 days", d["follow_up_window"]
    assert "14 days" in (d["exposure_duration"]["value"] or ""), d["exposure_duration"]


def test_a_primary_outcome_clause_binds_only_to_the_row_whose_outcome_it_is():
    mort = _row("corticosteroids-cap-mortality", "All-cause mortality", "25688779")
    hyper = _row("corticosteroids-cap-mortality", "Hyperglycaemia", "25688779")
    for d in (mort, hyper):
        assert "treatment failure" not in (d["endpoint_definition"]["value"] or ""), d["endpoint_definition"]


def test_melatonin_analysis_set_is_the_rows_own_itt_not_the_extension_completers():
    d = _row("melatonin-primary-insomnia-sol", "Sleep-onset latency", "20712869")
    assert d["analysis_set"]["value"] == "intention-to-treat", d["analysis_set"]
    assert "completer" not in (d["analysis_set"]["span"] or "").lower()


def test_denosumab_vertebral_primary_clause_stays_on_its_own_row_only():
    vert = _row("denosumab-vertebral-fracture", "New vertebral fracture", "19671655")
    assert "new vertebral fracture" in (vert["endpoint_definition"]["value"] or "").lower()
    for name in ("Nonvertebral fracture", "Hip fracture"):
        d = _row("denosumab-vertebral-fracture", name, "19671655")
        assert "primary end point" not in (d["endpoint_definition"]["value"] or "").lower(), (name, d["endpoint_definition"])


def test_a_protocol_declared_analysis_set_is_labelled_as_declared_not_trial_reported():
    d = _row("denosumab-vertebral-fracture", "New vertebral fracture", "19671655")
    assert d["analysis_set"]["source"] == cc.SRC_DECLARED and d["analysis_set"]["trial_reported"] is False


def test_an_explicit_timeframe_wins_over_prose():
    d = _row("melatonin-primary-insomnia-sol", "Sleep-onset latency", "20712869")
    assert d["follow_up_window"]["value"] == "Baseline and 3 weeks" and d["follow_up_window"]["source"] == "trial.timeframe"


def test_time_phrases_are_typed_by_kind():
    k = cc.time_phrase_kind
    assert k("followed by tapering for a total of 8 or 14 days", "14 days") == "exposure"
    assert k("By day 28, death had occurred in 25 of 400 patients", "day 28") == "follow_up"
    assert k("the median length of hospital stay was 5 days", "5 days") == "length_of_stay"
    assert k("60 mg of denosumab subcutaneously every 6 months for 36 months", "every 6 months") == "schedule"


def test_age_dispersion_and_lancet_decimals_are_not_follow_up_windows():
    k = cc.time_phrase_kind
    assert k("Of the 1105 participants (mean age, 70 years [SD, 12 years]; 33% were women)", "70 years") == "age"
    assert k("The mean duration of exposure was 34.2±13.7 months", "13.7 months") == "dispersion"
    vals = [v for v, raw, s, kind in cc._phrases("During a median follow-up of 5·4 years (IQR 5·1-5·9), the outcome occurred.")]
    assert vals[0] == "5.4 years"


def test_the_outcome_acronym_binds_a_sentence():
    assert cc._about_outcome("AAD occurred in 12% of the placebo group.", cc._outcome_tokens({"name": "Antibiotic-associated diarrhoea"}))


def test_follow_up_comparison_trial_defined_accepts_durations_fixed_window_does_not():
    """A trial-defined window ('trial end') accepts each trial's own reported duration -- that is what it means; a fixed
    window ('28 days') flags a trial with another window, and wording ('within 28 days', 'Day 28') is not a difference."""
    from harness.compat_check import _follow_compatible, _is_mismatch
    assert _follow_compatible("trial end", "2.6 years")
    assert _follow_compatible("trial end / longest randomized follow-up", "40 months")
    assert not _is_mismatch("follow_up_window", "trial end", ["2.6 years", "3.4 years"])
    assert _follow_compatible("28 days", "within 28 days") and _follow_compatible("28 days", "Day 28")
    assert not _follow_compatible("28 days", "90 days")
    assert _is_mismatch("follow_up_window", "28 days", ["28 days", "90 days"])
    assert _follow_compatible("52-104 weeks", "68 weeks") and not _follow_compatible("52-104 weeks", "26 weeks")
    assert not _follow_compatible("in-hospital / index-admission", "14 days")
