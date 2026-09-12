"""Unit-of-analysis detector (ME-26/27): a cluster/crossover design is flagged; an ordinary
multicentre parallel trial is NOT (the conservative-on-purpose requirement — no false disclosures)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import unit_of_analysis as U  # noqa: E402


def test_cluster_crossover_detected():
    assert U.detect("a pragmatic, cluster-randomized, multiple-crossover trial in five ICUs") == "cluster-randomized crossover"
    assert U.detect("Double-blind, cluster randomized, double-crossover trial in 4 ICUs") == "cluster-randomized crossover"
    assert U.detect("we conducted a cluster-randomised trial across 20 hospitals") == "cluster-randomized"
    assert U.detect("a two-period crossover trial of the drug") == "crossover"


def test_ordinary_parallel_trial_not_flagged():
    # a plain multicentre parallel RCT must NOT trip the detector (else false disclosures everywhere)
    assert U.detect("a multicenter, double-blind, randomized, placebo-controlled trial at 40 centers") is None
    assert U.detect("patients were randomized 1:1 to drug or placebo and followed for 12 months") is None
    assert U.detect("") is None


def test_scan_pooled_reports_flagged_trials_once():
    review = {"outcomes": [{"trials": [{"id": "PMID 1"}, {"id": "PMID 2"}]},
                           {"trials": [{"id": "PMID 1"}]}]}  # PMID 1 appears twice
    rec = {"1": {"title": "SMART", "abstract": "a cluster-randomized, multiple-crossover trial in ICUs"},
           "2": {"title": "Plain", "abstract": "a multicenter parallel randomized placebo-controlled trial"}}
    out = U.scan_pooled(review, rec)
    ids = [o["id"] for o in out]
    assert ids == ["PMID 1"]  # only the cluster trial, and only once despite two outcomes
    assert out[0]["design"] == "cluster-randomized crossover" and out[0]["span"]
