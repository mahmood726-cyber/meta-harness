"""Plants (A7 part 2): the PICU pilot itself (probiotics-aad-prevention, PMID 39935568). Its held abstract prints
'Antibiotic associated diarrhea was experienced in 30% vs 55.5% of patients in the LGG groups vs placebo' for
'10 in the LGG group and 9 in the placebo group' (3/10 v 5/9 = RR 0.54) and 'The RR ratio for AAD when using LGG was
0.59 (95% CI, 0.21-1.6)'. Served: OUTCOME_NOT_IN_SOURCE, which is false -- the outcome is reported twice, inconsistently.
After A7 it is the typed state SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE with both values."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import extract  # noqa: E402

SLUG, PID = "probiotics-aad-prevention", "39935568"


def _picu():
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    rec = next(r for r in json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8"))["records"]
               if str(r["id"]) == PID)
    return cfg, rec["abstract"]


def test_an_effect_named_for_its_outcome_before_was_is_read():
    # '<label> for/of <the outcome> was <point> (95% CI ...)'
    assert tuple(extract.extract_effect("The RR ratio for AAD when using LGG was 0.59 (95% CI, 0.21-1.6).")) == \
        ("RR", 0.59, 0.21, 1.6)
    assert tuple(extract.extract_effect(
        "The relative risk of antibiotic-associated diarrhea was 0.59 (95% CI 0.21-1.60).")) == ("RR", 0.59, 0.21, 1.6)


def test_the_long_gap_form_still_needs_was_and_a_ci():
    # no 'was/were' -> the historical 25-char gap rule; a far number with no CI is never an effect
    assert extract.extract_effect("The relative risk of antibiotic-associated diarrhea in the LGG arm 0.59 (95% CI "
                                  "0.21-1.60).") is None
    assert extract.extract_effect("The relative risk of antibiotic-associated diarrhea was 0.59.") is None


def test_arm_sizes_stated_as_n_in_the_group_are_read():
    cfg, ab = _picu()
    assert extract._arm_ns(ab, cfg["intervention_terms"], cfg["comparator_terms"]) == {"i": 10, "c": 9}


def test_the_extractor_admits_neither_picu_value():
    # PICU prints percentages only (no event counts), so the extractor has no count row; it must not admit the reported
    # RR 0.59 on its own either (that would be the silent pick A7 forbids). It stays a refusal.
    cfg, ab = _picu()
    po = cfg["primary_outcome"]
    out = extract.extract_trial(ab, po["keywords"], cfg["intervention_terms"], cfg["comparator_terms"],
                                declared_composite=extract.declared_is_composite(po["name"]), estimand=po["estimand"])
    assert out.get("absent") is True and "effect" not in out and "ai" not in out, out


def test_percentages_and_arm_sizes_imply_counts_only_when_they_reproduce_the_printed_percentages():
    cfg, ab = _picu()
    sents = ["Antibiotic associated diarrhea was experienced in 30% vs 55.5% of patients in the LGG groups vs placebo "
             "(p = 0.375), respectively."]
    imp = extract.percentage_implied_counts(ab, sents, cfg["intervention_terms"], cfg["comparator_terms"])
    assert imp[:4] == (3, 10, 5, 9)        # 30% of 10 = 3; 55.5% of 9 = 5 (5/9 = 55.56%, printed truncated)
    assert extract.percentage_implied_counts(ab, ["Diarrhea occurred in 37% vs 55.5% of patients in the LGG groups vs "
                                                  "placebo."], cfg["intervention_terms"], cfg["comparator_terms"]) is None


def test_PLANT_picu_reason_is_the_typed_disagreement_not_outcome_not_in_source():
    from harness import absence
    cfg, ab = _picu()
    po = cfg["primary_outcome"]
    ann = absence.classify_reason(po["keywords"], ab, None, outcome_name=po["name"], declared_estimand=po["estimand"],
                                  arm_terms=(cfg["intervention_terms"], cfg["comparator_terms"]))
    assert ann["reason_code"] == absence.SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE, ann
    assert "0.59" in ann["state_basis"] and "3/10 v 5/9" in ann["state_basis"] and "percentages" in ann["state_basis"]


def test_PLACIDE_aad_and_cdd_counts_are_never_bound_to_aad():
    # the ELIXA risk, realised by a trial abbreviation (reverted): 'prevention of AAD and CDD' -- 12/1470 v 17/1471 are
    # the C. difficile counts. The extractor must not read them as the AAD outcome.
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    ab = next(r for r in json.load(open(os.path.join(ROOT, "cache", SLUG, "records.json"), encoding="utf-8"))["records"]
              if str(r["id"]) == "24309198")["abstract"]
    po = cfg["primary_outcome"]
    out = extract.extract_trial(ab, po["keywords"], cfg["intervention_terms"], cfg["comparator_terms"],
                                declared_composite=extract.declared_is_composite(po["name"]), estimand=po["estimand"])
    assert (out.get("ai"), out.get("ci")) != (12, 17), out
