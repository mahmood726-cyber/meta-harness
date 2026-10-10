"""Two sentences glued without a space ('...respectively.At 12 months, ...') are two sentences (PHILO, ticagrelor).

Narrowing a multi-result sentence to its owning clause (V14-02's nested-bracket fix) exposed this: PHILO's composite
result clause names 'the composite primary efficacy endpoint', whose definition sits in the glued first half; the
definition finder skips any sentence carrying an effect, so the run-on hid the definition and PHILO abstained.
"""
import json
import os

from harness import hand_binding as hb
from harness import pipeline
from harness import target_endpoint as te

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLUED = ("Primary safety and efficacy endpoints were time to first occurrence of any major bleeding event and to any "
         "event from the composite of myocardial infarction, stroke or death from vascular causes, respectively.At 12 "
         "months, overall major bleeding occurred in 10.3% of ticagrelor-treated patients.")


def test_glued_sentences_split():
    assert hb._sentences(GLUED) == [GLUED[:GLUED.index("At 12")], GLUED[GLUED.index("At 12"):]]


def test_decimals_and_initialisms_do_not_split():
    s = "HR 0.84 in the U.S.Food cohort and e.g. 1.5 mg."
    assert hb._sentences(s) == [s]


def test_philo_binds_its_composite_exactly():
    slug = "ticagrelor-vs-clopidogrel-acs"
    cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    spec = next(s for s, _ in pipeline._outcome_specs(cfg))
    recs = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))["records"]
    ab = next(r for r in recs if str(r["id"]) == "26376600")["abstract"]
    v = json.load(open(os.path.join(ROOT, "cache", slug, "verified_effects.json"), encoding="utf-8"))["26376600"]
    row = dict(v if isinstance(v, dict) else v[0], id="PMID 26376600", handed_abstract=ab)
    assert hb.bind_hand_row(spec, row)["target_endpoint_class"] == te.EXACT_TARGET
