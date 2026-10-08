"""Regressions for the defects codex round 1 (gpt-6-astra, recorded; pva lane 2026-10-08) found in the NEW tabs, each
asserted on the committed review it was found in. Every one was span-verified against the rendered bytes before it was
accepted; the legacy-tab findings of the same round are handed over, not fixed here."""
from __future__ import annotations

import json
import re
from pathlib import Path

from harness import grade, manuscript, page, review_tabs as T

ROOT = Path(__file__).resolve().parents[1]


def _r(slug):
    return json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))


def test_included_never_calls_a_suppressed_or_refused_synthesis_pooled():
    for slug in ("balanced-crystalloids-vs-saline-mortality", "colchicine-secondary-cv-prevention", "corticosteroids-cap-mortality",
                 "iv-iron-hfref-hosp", "probiotics-aad-prevention", "sacubitril-valsartan-hfref", "sglt2-ckd-progression"):
        r = _r(slug)
        tab = T.included_tab(r)
        for o in r["outcomes"]:
            st = T.outcome_state(o)
            res = o.get("result") or {}
            if res.get("estimate") is None or T._gated(o):
                assert st != "pooled", (slug, o["name"])
                assert f"{o['name']} [pooled]" not in tab, (slug, o["name"])
        assert "Pooled in" not in tab


def test_conclusions_state_the_claim_checks_recorded_scope_and_no_universal_assurance():
    for slug in ("dpp4-mace-t2d", "sglt2-hfref-hosp-cvdeath"):
        r = _r(slug)
        c = T.conclusions(r)
        assert "every other sentence" not in c
        for x in r["reproduction"]["claim_check"]["scope"]["not_in_scope"]:
            assert x in c


def test_significant_is_labelled_by_claim_py_definition_not_as_excludes_the_null():
    c = T.conclusions(_r("tranexamic-acid-pph"))
    assert "95% CI excludes the null" not in c
    assert "does not strictly cross the null" in c


def test_continuous_rows_show_their_recorded_n():
    tab = T.extraction_tab(_r("esketamine-trd-madrs"))
    assert "n )" not in tab and re.search(r"n 109\)", tab)


def test_refused_ci_is_stated_not_blank():
    for slug in ("finerenone-ckd-t2d-renal", "sglt2-hfref-hosp-cvdeath", "statins-primary-prevention-elderly"):
        a = T.analysis_tab(_r(slug))
        assert "<td> to </td>" not in a
        assert "K2_SINGLE_DF" in a, slug


def test_refused_pool_is_stated():
    a = T.analysis_tab(_r("ticagrelor-vs-clopidogrel-acs"))
    assert "<td> to </td>" not in a and "POOL_REFUSED" in a


def test_stale_heterogeneity_is_qualified_and_never_called_absent():
    for slug in ("finerenone-ckd-t2d-renal", "glp1-ra-mace-t2d"):
        r = _r(slug)
        assert grade.membership_incomplete(r)
        a = T.analysis_tab(r)
        prim = a.split("(primary)</h4>", 1)[1].split("<h4>", 1)[0]
        assert grade.stale_heterogeneity(r) in prim
        assert "no between-study heterogeneity detected" not in prim


def test_single_trial_is_not_called_pooled():
    a = T.analysis_tab(_r("semaglutide-obesity-mace"))
    assert "<tr><th>Pooled estimate</th><td>0.8</td>" not in a and "single trial, k = 1" in a
    assert "Single trial (k = 1)" in a


def test_forest_shows_count_rows_in_the_pooled_scales_own_measure():
    r = _r("metformin-pcos-ovulation")
    prim = next(o for o in r["outcomes"] if o.get("primary"))
    assert (prim["result"].get("scale") or "").upper() == "OR"
    svg = manuscript.forest_for(prim)
    t = next(t for t in prim["trials"] if "19522426" in str(t.get("id")))
    a, n1, c, n2 = t["ai"], t["n1i"], t["ci"], t["n2i"]
    want = manuscript._fmt((a * (n2 - c)) / (c * (n1 - a)))
    assert f">{want}<" in svg or f">{want} [" in svg


def test_forest_axis_names_a_mixed_measure_pool():
    r = _r("spironolactone-hfref-mortality")
    prim = next(o for o in r["outcomes"] if o.get("primary"))
    svg = manuscript.forest_for(prim)
    assert prim["result"]["effect_label"] in svg


def test_amendment_headings_are_found_whatever_their_wording():
    for slug in ("probiotics-aad-prevention", "sglt2-ckd-progression", "colchicine-postop-af"):
        p = T.protocol_additions(_r(slug))
        assert "<table" in p.split("id='decisions'")[0], slug
        assert "no section headed as an amendment" not in p
    assert "17 Sep 2026" in T.protocol_additions(_r("colchicine-postop-af"))
