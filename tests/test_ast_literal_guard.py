"""r24: a trial's count or effect is never written in harness code. Values are read from a held source with its span,
or refused. The guard fails on any numeric trial-value literal not in registry/ast_literal_allowlist.json, and the
plants prove it can fail (each is a shape that stood in the harness before r24)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import ast_literal_sweep as sweep  # noqa: E402
from harness import comparator_second_pass as csp  # noqa: E402
from harness import scope_identity as si  # noqa: E402

RELY = ("Results: ... 110 mg of dabigatran (relative risk with dabigatran, 0.91; 95% confidence interval [CI], 0.74 to "
        "1.11; P<0.001 for noninferiority)")
ENGAGE = ("... low-dose edoxaban (hazard ratio, 1.07; 97.5% CI, 0.87 to 1.31; P=0.005 for noninferiority). In the "
          "intention-to-treat analysis, there was a trend favoring high-dose edoxaban versus warfarin (hazard ratio, "
          "0.87; 97.5% CI, 0.73 to 1.04; P=0.08) and an unfavorable trend with low-dose edoxaban versus warfarin "
          "(hazard ratio, 1.13; 97.5% CI, 0.96 to 1.34; P=0.10).")


def _allow():
    return json.load(open(os.path.join(ROOT, "registry", "ast_literal_allowlist.json"), encoding="utf-8"))["allowed"]


def test_no_unlisted_trial_value_literal_in_the_harness():
    allow = _allow()
    new = [h for h in sweep.sweep(ROOT) if sweep.key(h) not in allow]
    assert new == [], new


def test_PLANT_the_sweep_flags_each_pre_r24_shape():
    src = ('X = {"ai": 20, "n1i": 169}\n'
           'Y = {"effect": 0.91, "ci_low": 0.74}\n'
           'Z = "RR 0.91 (0.74-1.11)"\n'
           'W = "20/169 v 37/167"\n')
    kinds = {(h["kind"], h.get("key", "")) for h in sweep.sweep_source(src, "plant.py")}
    assert {("COUNT_OR_EFFECT_KEY", "ai"), ("COUNT_OR_EFFECT_KEY", "n1i"), ("COUNT_OR_EFFECT_KEY", "effect"),
            ("EFFECT_TUPLE_TEXT", ""), ("COUNT_PAIR_TEXT", "")} <= kinds


def test_noac_lower_dose_values_are_read_with_their_ci_level():
    rows = {"records": [{"id": "19717844", "title": "", "abstract": RELY},
                        {"id": "24251359", "title": "", "abstract": ENGAGE}]}
    got = {a["trial"]: a for a in si._noac_lower_dose_status(rows)["available_lower_dose_rows"]}
    assert (got["RE-LY"]["effect"], got["RE-LY"]["ci_level"], got["RE-LY"]["ci_low"], got["RE-LY"]["ci_high"]) == \
        (0.91, 95.0, 0.74, 1.11)
    e = got["ENGAGE AF-TIMI 48"]
    # PLANT: the on-treatment 1.07 (0.87-1.31) comes first in the abstract; a loose regex reads it
    assert (e["effect"], e["ci_level"], e["ci_low"], e["ci_high"]) == (1.13, 97.5, 0.96, 1.34)


def test_PLANT_a_changed_source_number_changes_the_value_not_a_literal():
    rows = {"records": [{"id": "19717844", "title": "", "abstract": RELY.replace("0.91", "0.93")}]}
    got = si._noac_lower_dose_status(rows)["available_lower_dose_rows"]
    assert got[0]["effect"] == 0.93


def test_metformin_overrides_are_read_from_the_comparator_text():
    text = ("The combined group may have higher rates of ovulation (OR 1.65, 95% CI 1.35 to 2.03; 8 studies). ... "
            "gastrointestinal side effects are probably more common with combined therapy (OR 4.26, 95% CI 2.83 to "
            "6.40; 4 studies)")
    items = csp.PROFILES["metformin-pcos-ovulation"]["reported_overrides"]
    vals = [csp.reported_value_at(text, i["source_term"]) for i in items]
    assert vals == [{"estimate": 1.65, "ci_level": 95.0, "ci_low": 1.35, "ci_high": 2.03},
                    {"estimate": 4.26, "ci_level": 95.0, "ci_low": 2.83, "ci_high": 6.4}]
    assert all("estimate" not in i for i in items)


def test_PLANT_an_anchor_without_numbers_gives_no_override():
    assert csp.reported_value_at("The combined group may have higher rates of ovulation (OR not estimable)",
                                 "The combined group may have higher rates of ovulation (OR") is None


def test_PLANT_codex_r1_1_a_bound_split_by_padding_is_never_truncated():
    text = "OR" + " 1.65, 95% CI 1.35 to " + " " * 55 + "2.03)"
    assert csp.reported_value_at(text, "OR") is None
    assert csp.reported_value_at("OR 1.65, 95% CI 1.35 to 2.03123", "OR")["ci_high"] == 2.03123   # read whole


def test_PLANT_codex_r1_2_negative_literals_are_flagged():
    hits = sweep.sweep_source('row = {"estimate": -0.35, "ci_low": -0.60, "ci_high": -0.10}', "harness/x.py")
    assert sorted(h["key"] for h in hits) == ["ci_high", "ci_low", "estimate"]
    assert {h["value"] for h in hits} == {-0.35, -0.6, -0.1}


def test_PLANT_codex_r1_3_four_digit_denominators_are_flagged():
    hits = sweep.sweep_source('counts = "20/1000 versus 30/1000"', "harness/x.py")
    assert [(h["kind"], h["value"]) for h in hits] == [("COUNT_PAIR_TEXT", "20/1000"), ("COUNT_PAIR_TEXT", "30/1000")]


def test_PLANT_codex_r2_1_an_exponent_bound_is_never_truncated():
    a = "The combined group may have higher rates of ovulation (OR"
    assert csp.reported_value_at(a + " 1.65, 95% CI 1.35 to 2.03e1)", a) is None


def test_PLANT_codex_r2_2_zero_and_one_event_arms_are_flagged():
    hits = sweep.sweep_source("trial = {'ai': 1, 'ci': 0}", "harness/x.py")
    assert sorted((h["key"], h["value"]) for h in hits) == [("ai", 1), ("ci", 0)]


def test_PLANT_codex_r2_3_counts_beside_a_url_or_four_digit_counts_are_flagged():
    assert [h["value"] for h in sweep.sweep_source('result = "1000/2000"', "harness/x.py")] == ["1000/2000"]
    hits = sweep.sweep_source('r = "Deaths: 20/169 versus 35/167; source https://example.org/trial/12/345"', "harness/x.py")
    assert "20/169" in [h["value"] for h in hits]
    # a URL path and a year/month are still not counts
    assert sweep.sweep_source('u = "https://example.org/trial/12/345"', "harness/x.py") == []
    assert sweep.sweep_source('d = "accessed 2024/09"', "harness/x.py") == []


def test_PLANT_codex_r3_1_engage_bound_with_exponent_is_refused():
    rows = {"records": [{"id": "24251359", "title": "", "abstract": ENGAGE.replace("0.96 to 1.34", "0.96 to 1.34e1")}]}
    assert si._noac_lower_dose_status(rows)["available_lower_dose_rows"] == []


def test_PLANT_codex_r3_2_small_denominator_counts_are_not_dates():
    hits = sweep.sweep_source("summary = 'Deaths: 5/10 versus 6/12'", "harness/x.py")
    assert [h["value"] for h in hits] == ["5/10", "6/12"]
    assert sweep.sweep_source("d = 'on 5/10/2019'", "harness/x.py") == []          # a d/m/y date still is not


def test_PLANT_codex_r3_3_every_count_in_a_string_is_reported():
    hits = sweep.sweep_source("summary = 'Deaths: 20/169 versus 99/100'", "harness/x.py")
    assert [h["value"] for h in hits] == ["20/169", "99/100"]
