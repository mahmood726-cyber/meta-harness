"""Plants (5 Oct night, forest lane): the citing-meta target filter keeps a figure only when -- before any model call --
it is not a flow/funnel/network/bias/TSA figure, its caption or the meta's title names the topic's intervention, and the
admission pre-filter (g1_admission_check.prefilter: outcome, timepoint, measure from the meta's own words) passes."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_citing_targets as ct  # noqa: E402


def test_figure_filter_keeps_only_figures_that_can_pass_admission(monkeypatch):
    import g1_admission_check as ac
    monkeypatch.setattr(ac, "prefilter", lambda slug, pmid, cap, spec=None: (("28-day mortality" in cap), ["X"]))
    figs = [("F1", "PRISMA flow diagram"), ("F2", "Network plot for mortality"),
            ("F3", "Forest plot of comparison: 28-day mortality."), ("F4", "Forest plot of length of stay"),
            ("F5", "Trial sequential analysis of 28-day mortality")]
    kept = ct.figure_candidates("corticosteroids-covid19-mortality", "1", figs, "Corticosteroids in COVID-19")
    assert [k["fig_id"] for k in kept] == ["F3"]


def test_wrong_intervention_meta_is_dropped_before_the_prefilter(monkeypatch):
    import g1_admission_check as ac
    monkeypatch.setattr(ac, "prefilter", lambda slug, pmid, cap, spec=None: (True, []))
    figs = [("F2", "Forest plot of 28-day mortality")]
    assert ct.figure_candidates("corticosteroids-covid19-mortality", "1", figs,
                                "Interleukin-6 receptor antagonists in COVID-19") == []
