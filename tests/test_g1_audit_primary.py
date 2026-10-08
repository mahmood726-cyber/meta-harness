"""PLANTS for the independent-reader audit (scripts/g1_audit_primary.py): only a gated reading is compared; counts,
effect+CI (a re-expressed interval compared as PRINTED) and per-arm continuous rows (re-combined by Handbook 6.5.2.10)
each confirm or disagree deterministically; an arm number that is not in the quote is refused."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))

import g1_audit_primary as au  # noqa: E402

ARMS_Q = ("Intranasal Esketamine 56 mg Plus Oral Antidepressant: MEAN -19.0 (Standard Deviation 13.86) N=111 "
          "Intranasal Esketamine 84 mg Plus Oral AD: MEAN -18.8 (Standard Deviation 14.12) N=98 "
          "Oral AD Plus Intranasal Placebo: MEAN -14.8 (Standard Deviation 15.07) N=108")
ARMS = [{"label": "Intranasal Esketamine 56 mg Plus Oral Antidepressant", "mean": "-19.0", "sd": "13.86", "n": "111"},
        {"label": "Intranasal Esketamine 84 mg Plus Oral AD", "mean": "-18.8", "sd": "14.12", "n": "98"},
        {"label": "Oral AD Plus Intranasal Placebo", "mean": "-14.8", "sd": "15.07", "n": "108"}]
EMPTY = {k: None for k in ("measure", "point", "lower", "upper", "ci_level", "events_t", "n_t", "events_c", "n_c")}


def test_counts_confirm_and_disagree():
    claim = dict(EMPTY, events_t="305", n_t="2,701", events_c="316", n_c="2679")
    ours = {"events_t": 305, "n_t": 2701, "events_c": 316, "n_c": 2679}
    assert au.compare(claim, ours, []) == ("CONFIRMED", "COUNTS")
    assert au.compare(claim, dict(ours, events_c=317), []) == ("DISAGREE", "COUNTS")


def test_effect_compared_as_printed_when_reexpressed():
    ours = {"measure": "HR", "effect": "0.96", "lower": "0.8209", "upper": "1.1227",
            "ci_printed": {"level": "98", "lower": "0.80", "upper": "1.16"}}
    assert au.compare(dict(EMPTY, point="0.96", lower="0.80", upper="1.16"), ours, []) == ("CONFIRMED", "EFFECT_CI")
    assert au.compare(dict(EMPTY, point="0.96", lower="0.82", upper="1.12"), ours, []) == ("DISAGREE", "EFFECT_CI")


def test_arms_are_recombined_and_compared():
    ours = {"mean_t": "-18.9062", "sd_t": "13.9491", "n_t": 209, "mean_c": "-14.8", "sd_c": "15.07", "n_c": 108}
    claim = dict(EMPTY, arms=ARMS, quote=ARMS_Q, state="REPORTED")
    assert au.compare(claim, ours, ["esketamine"]) == ("CONFIRMED", "ARMS")
    one_dose = dict(claim, arms=[ARMS[0], ARMS[2]])                 # a reader that dropped a dose arm: not our row
    assert au.compare(one_dose, ours, ["esketamine"]) == ("DISAGREE", "ARMS")


def test_arms_gate():
    claim = dict(EMPTY, arms=ARMS, quote=ARMS_Q, state="REPORTED")
    assert au.gate(claim, "header " + ARMS_Q + " footer") == (True, "ACCEPTED_ARMS")
    bad = dict(claim, arms=[dict(ARMS[0], mean="-21.0")] + ARMS[1:])
    assert au.gate(bad, ARMS_Q) == (False, "ARM_NUMBER_NOT_IN_QUOTE")
    assert au.gate(dict(claim, quote="not in the material"), ARMS_Q)[1] == "QUOTE_NOT_IN_TEXT"


def test_events_only_and_printed_minus_variants():
    ours = {"events_t": 6, "n_t": 61, "events_c": 9, "n_c": 59}
    assert au.compare(dict(EMPTY, events_t="6", events_c="9"), ours, []) == ("CONFIRMED_EVENTS_ONLY", "EVENTS")
    assert au.compare(dict(EMPTY, events_t="7", events_c="9"), ours, []) == ("DISAGREE", "EVENTS")
    dash = [dict(a, mean=a["mean"].replace("-", "\u2013")) for a in ARMS]          # the trial's own table prints en dashes
    arms_ours = {"mean_t": "-18.9062", "sd_t": "13.9491", "n_t": 209, "mean_c": "-14.8", "sd_c": "15.07", "n_c": 108}
    assert au.compare(dict(EMPTY, arms=dash), arms_ours, ["esketamine"]) == ("CONFIRMED", "ARMS")
