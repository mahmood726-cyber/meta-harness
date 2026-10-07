"""D10 inventory R1 (regex over held comparator text): the phrasings seen in the 12 comparators, 7 Oct."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_outcomes as go  # noqa: E402


def _one(text):
    hits, _ = go.regex_inventory(text)
    return [(h["family"], h["estimate"], h["lower"], h["upper"]) for h in hits]


def test_lancet_middle_dot_and_bracketed_abbreviation():
    t = "Thromboembolic events occurred (pooled odds ratio [OR] 0·96 [95% CI 0·65–1·41]; low-quality evidence)."
    assert _one(t) == [("HARM", "0.96", "0.65", "1.41")]
    hits, _ = go.regex_inventory(t)
    assert "0·96" in hits[0]["span"]                      # the span is the ORIGINAL text


def test_pdf_equals_glyph_and_ci_without_95():
    assert _one("more cases of drug withdrawals (RR ¼1.85, 95% CI 1.04 to 3.29, p for effect 0.04).") == \
        [("HARM", "1.85", "1.04", "3.29")]
    assert _one("this primary outcome showed a tendency to favor DOACs (OR 0.88, CI 0.75–1.03).") == \
        [("OTHER", "0.88", "0.75", "1.03")]


def test_spelled_measure_with_parenthesised_abbreviations():
    t = "DOAC recipients had a lower risk of stroke [Pooled Odds Ratio (OR) 0.76, 95% Confidence Interval (CI) (0.68–0.84)]."
    assert _one(t) == [("OTHER", "0.76", "0.68", "0.84")]


def test_all_cause_mortality_family():
    assert _one("the two groups did not differ in death from any cause (OR 0.94, 95% CI 0.79-1.12).") == \
        [("ALL_CAUSE_MORTALITY", "0.94", "0.79", "1.12")]


def test_a_result_of_another_contrast_or_population_is_not_ours():
    # 7 Oct, inventory v1: denosumab's 'acceptability' was risedronate vs placebo (a network meta-analysis) and
    # sglt2-ppHF's 'cardiovascular death' was canagliflozin-only in one population
    den = go.topic("denosumab-vertebral-fracture")
    assert not go.contrast_is_ours("risedronate vs placebo", den)
    assert go.contrast_is_ours("denosumab vs placebo", den)
    assert not go.contrast_is_ours("denosumab vs alendronate", den)
    doac = go.topic("doac-vte-recurrence")
    assert go.population_is_ours(None, doac)
    assert go.population_is_ours("patients with acute VTE", doac)
    assert not go.population_is_ours("patients with NVAF", doac)


def test_an_already_declared_outcome_is_linked_whatever_its_read_family():
    doac = go.topic("doac-vte-recurrence")
    assert go.linked_to("major bleeding", doac) == "Major bleeding"
    assert go.linked_to("net clinical benefit", doac) is None


def test_one_agent_of_a_class_topic_is_a_split_not_our_result():
    sg = go.topic("sglt2-primary-prevention-hf")
    assert not go.contrast_is_ours("canagliflozin vs placebo", sg)
    assert go.contrast_is_ours("SGLT2 inhibitors vs placebo", sg)
    assert go.contrast_is_ours("denosumab vs placebo", go.topic("denosumab-vertebral-fracture"))   # one-agent topic
