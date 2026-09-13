"""Atomic comparator extraction (COMPARATOR_RESULT_CONTEXT_MISMATCH, audits 14/17 + comp_rowctx lane).
A comparator paragraph lists many outcomes' effects; label+estimate+CI must come from ONE row, never
assembled across rows. Five confirmed instances (right number, wrong row) drove a tighter binding
window (140) in comparator_effect plus disambiguating keywords. These pin the corrected bindings so a
future wording/keyword change that re-crosses the rows fails loudly.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import extract  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _comp(slug, outcome_sub):
    t = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
    r = json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8"))
    full = r.get("comparator_fulltext", "")
    cab = {str(x["id"]): x for x in r["records"]}.get(str(t.get("comparator_pmid")), {}).get("abstract", "")
    co = next(c for c in t["comparator_outcomes"] if outcome_sub.lower() in c["name"].lower())
    e = extract.comparator_effect(cab, full, co["keywords"])
    return None if not e else (e["scale"], e["effect"], e["ci_low"], e["ci_high"])


def test_crystalloids_rrt_binds_its_own_ci_not_mortality():
    # RRT row is (OR 0.92, 0.67-1.28); the mortality row's CI (0.85-1.01) must NOT be borrowed.
    assert _comp("balanced-crystalloids-vs-saline-mortality", "renal") == ("OR", 0.92, 0.67, 1.28)


def test_colchicine_noncv_death_not_all_cause():
    # non-cardiovascular mortality is RR 1.38 (1.00-1.90); the all-cause row (1.07) must not bind.
    assert _comp("colchicine-secondary-cv-prevention", "non-cardiovascular") == ("RR", 1.38, 1.0, 1.9)
    # and the GI harm row must stay on its own row (regression guard against an over-tight window)
    assert _comp("colchicine-secondary-cv-prevention", "astrointestinal") == ("RR", 2.07, 1.45, 2.95)


def test_empagliflozin_composite_not_hfhosp_alone():
    # composite is HR 0.80 (0.74-0.87); the HF-hospitalisation-alone row (0.74) must not bind.
    assert _comp("empagliflozin-hfpef-hosp", "composite") == ("HR", 0.8, 0.74, 0.87)


def test_sglt2_hfref_subgroup_not_entire_cohort():
    # our topic is LVEF<=40%: the subgroup row is HR 0.74 (0.68-0.81), not the entire-cohort 0.76.
    assert _comp("sglt2-hfref-hosp-cvdeath", "LVEF") == ("HR", 0.74, 0.68, 0.81)
