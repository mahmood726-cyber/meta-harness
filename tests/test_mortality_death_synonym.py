"""Regression: mortality<->death synonymy in outcome-sentence selection.

Torres 2015 (corticosteroids-CAP) reports its in-hospital MORTALITY as a secondary
outcome ("In-hospital mortality did not differ ... 6 patients [10%] ... 9 patients
[15%]"). The topic keyword list enumerated 'in-hospital death' but not the word the
trial actually uses, 'mortality', so _outcome_sentences returned empty and the trial
was declared-absent -- an all-cause-mortality trial dropped on a pure synonym gap.

The fix expands PHRASE keywords naming death/mortality with the synonym swapped, so
'in-hospital death' also matches 'in-hospital mortality'. It must NOT:
  - broaden a bare token ('died' must not match arbitrary 'mortality' sentences), or
  - pull in Torres's PRIMARY (treatment-failure composite, 8/61 vs 18/59), which names
    no death/mortality word and is a composite the single-outcome guard skips.
"""
import json
import os

import harness.extract as E

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _torres_record():
    p = os.path.join(_ROOT, "cache", "corticosteroids-cap-mortality", "records.json")
    recs = json.load(open(p, encoding="utf-8"))
    recs = recs.get("records", recs) if isinstance(recs, dict) else recs
    return [r for r in recs if str(r.get("id")) == "25688779"][0]


def _cap_spec():
    p = os.path.join(_ROOT, "topics", "corticosteroids-cap-mortality.json")
    return json.load(open(p, encoding="utf-8"))


def test_phrase_keyword_matches_synonym():
    # 'in-hospital death' must select the trial's 'in-hospital mortality' sentence.
    tor = _torres_record()
    kws = _cap_spec()["primary_outcome"]["keywords"]
    sents = E._outcome_sentences(tor["abstract"], kws)
    assert any("in-hospital mortality did not differ" in s.lower() for s in sents), sents


def test_torres_binds_mortality_not_treatment_failure():
    # Real cached Torres abstract, real topic spec: must bind in-hospital mortality
    # (6/61 vs 9/59), NOT the primary treatment-failure composite (8/61 vs 18/59).
    tor = _torres_record()
    spec = _cap_spec()
    po = spec["primary_outcome"]
    res = E.extract_trial(tor["abstract"], po["keywords"], spec["intervention_terms"],
                          spec["comparator_terms"],
                          declared_composite=E.declared_is_composite(po["name"]),
                          estimand=po.get("estimand"))
    assert not res.get("absent"), res
    assert (res.get("ai"), res.get("n1i"), res.get("ci"), res.get("n2i")) == (6, 61, 9, 59), res


def test_bare_token_not_broadened():
    # A bare 'died' keyword must NOT be expanded to match a 'mortality' sentence.
    s = "Cardiovascular mortality was 4% versus 5%."
    assert not E._kw_in_sentence("died", s.lower())
    # but the true substring still matches
    assert E._kw_in_sentence("died", "3 patients died in the trial.".lower())


def test_variant_swap_both_directions():
    assert "in-hospital mortality" in E._mort_variants("in-hospital death")
    assert "28-day death" in E._mort_variants("28-day mortality")


def test_hyphen_insensitive_disease_keyword():
    # a multi-word DISEASE keyword matches its hyphenated surface form (Fish-Oil/PISCES class)
    assert E._kw_in_sentence("fish oil", "the fish-oil group had fewer events")
    assert E._kw_in_sentence("heart failure hospitalisation", "heart-failure hospitalisation was reduced")


def test_generic_anchor_is_NOT_hyphen_broadened():
    # the generic 'primary outcome' anchor must stay EXACT -- hyphen-broadening it pooled ELIXA's
    # 4-point primary composite into a 3-point MACE topic (its HR sentence names no components).
    assert not E._kw_in_sentence("primary outcome", "a primary-outcome event occurred")
    assert not E._kw_in_sentence("primary end point", "a primary end-point event occurred")
