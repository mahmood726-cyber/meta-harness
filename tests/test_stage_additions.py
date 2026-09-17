"""Regression tests for the cycle-76 stage additions:
- absent-override tier (declare a trial absent for one outcome when the extractor grabbed a wrong endpoint)
- object-derived partial GRADE
- RoB-stratified sensitivity re-pool (its 'full' pool MUST reproduce the shipped primary result)
- the index error-rate banner numbers are derived from docs/error_rate.json (anti-drift)
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import grade as grade_mod  # noqa: E402
from harness import rob_sensitivity as rs  # noqa: E402
from harness import index as IDX  # noqa: E402
from harness import claimgraph  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")


def _reviews():
    for f in sorted(glob.glob(os.path.join(DOCS, "reviews", "*", "review.json"))):
        yield os.path.basename(os.path.dirname(f)), json.load(open(f, encoding="utf-8"))


# ---- absent-override ------------------------------------------------------------------------------
def test_absent_override_declared_and_flag_gated():
    """The semaglutide GI-AE wrong-endpoint fix must not pool STEP-12.

    STEP-12 is now refused upstream by the arm-object population contract, so the older
    outcome-level absent override remains a dormant cache guard rather than a rendered
    declared-absent trial.
    """
    r = json.load(open(os.path.join(DOCS, "reviews", "semaglutide-obesity-weight", "review.json"), encoding="utf-8"))
    gi = next(o for o in r["outcomes"] if "astrointestinal" in o["name"])
    assert "42575111" not in [str(t.get("label")) for t in gi.get("trials", [])], "wrong-endpoint trial still pooled"
    screening = [row for row in r["screening"]["records"] if str(row.get("id", "")).endswith("42575111")]
    assert screening and screening[0]["decision"] == "exclude"
    assert screening[0]["rule_id"] == "X-POPULATION"
    # the committed override entry carries both flags (flag-gated: absent requires override AND absent)
    ve = json.load(open(os.path.join(ROOT, "cache", "semaglutide-obesity-weight", "verified_effects.json"), encoding="utf-8"))
    e = ve["42575111"]
    assert e.get("override") is True and e.get("absent") is True and e.get("outcome") == gi["name"]


# ---- GRADE ---------------------------------------------------------------------------------------
def test_grade_present_and_valid_for_every_primary():
    for slug, r in _reviews():
        prim = next((o for o in r["outcomes"] if o.get("primary")), None)
        if not prim or not prim.get("result", {}).get("k"):
            continue
        g = r.get("grade")
        assert g, f"{slug}: no grade"
        # 'not_rateable' is a valid state (audit 21 #5): an estimand-incompatible / incoherent pool
        # yields domain signals but NO overall certainty category, with a reason.
        assert g["certainty"] in ("high", "moderate", "low", "very_low", "not_rateable", "provisional"), slug
        if g['certainty'] == 'provisional':
            assert any(d.get('assessed') is False for d in g['domains'].values())
        if g["certainty"] == "not_rateable":
            assert g.get("not_rateable_reason"), f"{slug}: not_rateable without a reason"
            continue
        # downgrades must equal the sum of domain downgrades (object-derived, not typed)
        s = sum(d.get("downgrade", 0) for d in g["domains"].values())
        assert g["downgrades"] == s, f"{slug}: downgrade total {g['downgrades']} != sum {s}"


def test_grade_imprecision_not_mechanical_on_tight_null():
    # External audit (C-GRADE-1): a tight CI around no-effect (0.91-1.08) is PRECISION about no
    # effect, not imprecision -- it must NOT be downgraded merely for crossing the null.
    tight = grade_mod._imprecision_domain({"k": 5, "ci_low": 0.91, "ci_high": 1.08}, "RR")
    assert tight["downgrade"] == 0, tight
    # a wide CI that reaches an appreciable effect while crossing null IS imprecise.
    wide = grade_mod._imprecision_domain({"k": 2, "ci_low": 0.57, "ci_high": 1.78}, "RR")
    assert wide["downgrade"] == 1, wide
    # a CI that includes an appreciable benefit and crosses null is still imprecise (one side is enough).
    onesidenull = grade_mod._imprecision_domain({"k": 2, "ci_low": 0.585, "ci_high": 1.235}, "RR")
    assert onesidenull["downgrade"] == 1, onesidenull


def test_common_effect_ci_shown_alongside_hksj_at_k2():
    # External audit (C-STATS-2): at k=2 the HKSJ t-multiplier (1 df) inflates the CI so it can read
    # "compatible with no effect" even when both trials agree; the conventional common-effect CI must
    # be exposed alongside. Two concordant studies -> a fixed CI that is NARROWER than the HKSJ CI.
    from harness.synth import Study, pool
    two = [Study(label="a", effect=0.80, ci_low=0.68, ci_high=0.94, measure="RR"),
           Study(label="b", effect=0.82, ci_low=0.70, ci_high=0.96, measure="RR")]
    r = pool(two, scale="RR")
    assert r.k == 2 and r.ci_low_fixed is not None and r.estimate_fixed is not None
    hksj_width = r.ci_high - r.ci_low
    fixed_width = r.ci_high_fixed - r.ci_low_fixed
    assert fixed_width < hksj_width, (fixed_width, hksj_width)  # t_1 inflates HKSJ vs z-based fixed


def test_grade_rob_downgrades_when_no_trial_assessed():
    # External audit (C-ROB-1): zero assessed cannot establish low risk; coverage gates the judgement.
    rob = grade_mod._rob_domain({"outcomes": [{"primary": True, "trials": [{"label": "a"}, {"label": "b"}]}],
                                 "rob2": {"trials": {}}})
    assert rob["downgrade"] == 1 and rob["n_rated"] == 0
    assert "not assessed" in rob["basis"].lower()


def test_grade_recomputes_from_object():
    """grade() run again on the committed review + ghost must equal the stored grade (regenerates)."""
    for slug, r in _reviews():
        if not r.get("grade"):
            continue
        gp = os.path.join(ROOT, "cache", slug, "ghost.json")
        ghost = json.load(open(gp, encoding="utf-8")) if os.path.exists(gp) else None
        assert grade_mod.grade(r, ghost)["certainty"] == r["grade"]["certainty"], slug


def test_grade_imprecision_uses_appreciable_threshold_not_bare_crossing():
    # Corrected requirement (external audit C-GRADE-1): imprecision downgrades when a ratio CI crosses
    # the null AND reaches an appreciable effect (<=0.75 or >=1.25) -- NOT for a tight null within
    # those bounds, which is precision about no effect. (This replaces the old iff-crosses-null rule,
    # which defended the mechanical behaviour the audit flagged.)
    for slug, r in _reviews():
        g = r.get("grade")
        if not g:
            continue
        res = next(o for o in r["outcomes"] if o.get("primary"))["result"]
        scale = (res.get("scale") or "").upper()
        imp = g["domains"]["imprecision"]
        if scale in ("RR", "OR", "HR", "IRR") and res.get("k", 0) > 1:
            cil, cih = res.get("ci_low"), res.get("ci_high")
            if cil is None or cih is None:
                continue
            crosses = cil <= 1.0 <= cih
            reaches_appreciable = (cil < 0.75) or (cih > 1.25)
            if crosses and reaches_appreciable:
                assert imp["downgrade"] >= 1, f"{slug}: wide CI crossing null must be imprecise"
            elif crosses and not reaches_appreciable:
                assert imp["downgrade"] == 0, f"{slug}: tight null CI must NOT be flagged imprecise"


# ---- RoB sensitivity -----------------------------------------------------------------------------
def test_rob_sensitivity_full_repool_matches_shipped():
    """The 'full' stratum re-pool MUST reproduce the shipped primary result — this is what guarantees the
    sensitivity re-pool uses the identical estimator and cannot drift from the page's number."""
    for slug, r in _reviews():
        sens = r.get("rob_sensitivity")
        if not sens:
            continue
        prim = next(o for o in r["outcomes"] if o.get("primary"))
        shipped = prim["result"]
        full = sens["full"]
        assert full["k"] == shipped["k"], f"{slug}: full k {full['k']} != shipped {shipped['k']}"
        assert abs(full["estimate"] - shipped["estimate"]) < 0.0011, f"{slug}: full estimate drifted"


def test_rob_sensitivity_recomputes():
    for slug, r in _reviews():
        if not r.get("rob_sensitivity"):
            continue
        again = rs.sensitivity(r)
        if r.get("claimgraph"):
            assert again["full"] == r["rob_sensitivity"]["full"], slug
            assert again["n_rob_rated"] == r["rob_sensitivity"]["n_rob_rated"], slug
            continue
        if again["full"] != r["rob_sensitivity"]["full"] or again["n_rob_rated"] != r["rob_sensitivity"]["n_rob_rated"]:
            codes = {v["code"] for v in claimgraph.check(r)}
            assert "ROB_JOIN_MISS" in codes, slug
        else:
            assert again["full"] == r["rob_sensitivity"]["full"], slug
            assert again["n_rob_rated"] == r["rob_sensitivity"]["n_rob_rated"], slug


# ---- error-rate index banner ---------------------------------------------------------------------
def test_error_rate_banner_numbers_are_object_derived():
    if not os.path.exists(os.path.join(DOCS, "error_rate.json")):
        return
    d = json.load(open(os.path.join(DOCS, "error_rate.json"), encoding="utf-8"))
    census = d.get("census_population") or d["population"]
    html = IDX.build_index(DOCS)
    assert "measured our own error rate" in html
    assert f"{d['independently_reverified']} of {census}" in html
    assert f"{d['exact_match']} of {d['independently_reverified']} matched exactly" in html
    assert "internal-consistency" in html  # the shared-architecture caveat must be stated


def test_error_rate_passes_prose_guard():
    """build_index runs _validate_prose_numbers over the error-rate banner; it must not raise."""
    assert IDX.build_index(DOCS)


# ---- manuscript (Stage PAPER) --------------------------------------------------------------------
def test_manuscript_limb_passes_on_every_live_review():
    from harness import gate
    for slug, _ in _reviews():
        d = os.path.join(DOCS, "reviews", slug)
        assert gate.check_manuscript_numbers(d) == [], f"{slug}: manuscript limb should pass"


def test_manuscript_limb_REFUSES_a_fabricated_number(monkeypatch, tmp_path):
    """A gate must be able to fail: plant a manuscript number that is not in the object and assert the
    limb refuses it (the anti-theater check)."""
    from harness import gate
    from harness import manuscript
    d = os.path.join(DOCS, "reviews", "glp1-ra-mace-t2d")
    # baseline passes
    assert gate.check_manuscript_numbers(d) == []
    # inject a fabricated MD and a fabricated large integer not present in the object
    orig = manuscript.render
    monkeypatch.setattr(manuscript, "render",
                        lambda rev, neutral=False: orig(rev) + "<p>MD 7.77 across 4321 patients</p>")
    reasons = gate.check_manuscript_numbers(d)
    assert reasons and "7.77" in reasons[0] and "4321" in reasons[0], reasons


def test_manuscript_renders_and_is_object_derived():
    from harness import manuscript
    for slug, r in _reviews():
        html = manuscript.render(r)
        assert "generated from the review object" in html
        assert "Data availability" in html


# ---- specification curve (Stage ANALYSIS A3) -----------------------------------------------------
def test_spec_curve_recomputes_and_direction_stable():
    from harness import spec_curve as scmod
    for slug, r in _reviews():
        sc = scmod.spec_curve(r)
        if not sc or sc.get("not_applicable"):
            continue
        # RE_HKSJ spec must equal the shipped primary estimate (identical estimator/data)
        prim = next(o for o in r["outcomes"] if o.get("primary"))
        shipped = prim["result"]
        assert abs(sc["specs"]["RE_HKSJ"]["estimate"] - round(shipped["estimate"], 4)) < 0.0011, slug


def test_spec_curve_index_numbers_derived():
    if not os.path.exists(os.path.join(DOCS, "spec_curve.json")):
        return
    n = IDX._spec_curve_numbers(DOCS)
    html = IDX.build_index(DOCS)
    assert f"{n['dir_stable']} of {n['n']}" in html
    assert f"{n['sig_stable']} of {n['n']}" in html


# ---- error-rate freshness invariant (the stale-number-in-a-new-costume guard) --------------------
def _pooled_population():
    """Every pooled number's row_id, recomputed from the live review.json set (same predicate as the
    census frame). If this set diverges from what error_rate.json was measured against, the rate is stale."""
    ids = set()
    for slug, r in _reviews():
        for o in r.get("outcomes", []):
            for t in o.get("trials", []):
                if t.get("effect") is not None or t.get("mean1") is not None or t.get("ai") is not None:
                    ids.add(f"{slug}::{o['name']}::{t.get('label')}")
    return ids


def test_error_rate_is_fresh_against_current_pooled_population():
    """A measured-once figure that looks live is the stale-number class in a new costume. The committed
    error_rate.json must have been measured against exactly the current pooled population; if a pooled
    number was added/removed/renamed since, this fails and the census must be re-run."""
    ep = os.path.join(DOCS, "error_rate.json")
    sp = os.path.join(DOCS, "error_rate_sample.json")
    if not os.path.exists(ep):
        return
    d = json.load(open(ep, encoding="utf-8"))
    assert os.path.exists(sp), "error_rate.json exists but the committed sample docs/error_rate_sample.json does not"
    sample = json.load(open(sp, encoding="utf-8"))
    sample_ids = {row["row_id"] for row in sample["rows"]}
    pop = _pooled_population()
    assert d.get("population") == len(sample_ids), "error_rate.json population != committed sample size"
    # EVERY currently-pooled number must be in the committed census sample: a new pooled number that was
    # never censused makes the live rate stale and fails here (re-run the census).
    uncensused = sorted(pop - sample_ids)
    assert not uncensused, (f"pooled numbers not in the error-rate census sample: {uncensused[:5]} — "
                            "re-run scripts/error_rate_compare.py + error_rate_pass2.py and rebuild the sample")
    # Any sample row no longer pooled must be an ACCOUNTED census-fix removal, not silent drift.
    removed = sorted(sample_ids - pop)
    unaccounted = sorted(set(removed) - set(d.get("removed_by_census_fixes", [])))
    assert not unaccounted, f"census-sample rows no longer pooled but not recorded as fixes: {unaccounted[:5]}"
    assert d.get("n_pooled_current_after_fixes") == len(pop), "n_pooled_current_after_fixes drifted from live"
    assert d.get("measured_utc"), "error_rate.json must declare measured_utc (freshness provenance)"


# ---- composite-component estimand guard (caught by cross-family Fable QA) -------------------------
def test_composite_component_mismatch_guard():
    """A 3-point MACE outcome must refuse a source whose composite adds a 4th component (TECOS's
    unstable-angina 4-point composite). Fires on the 4-point plant, not on a clean 3-point span."""
    from harness import extract
    tecos = ("The primary cardiovascular outcome was a composite of cardiovascular death, nonfatal "
             "myocardial infarction, nonfatal stroke, or hospitalization for unstable angina (hazard ratio 0.98)")
    assert extract.composite_component_mismatch("3-point major adverse cardiovascular events", tecos)
    clean3 = "composite of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke (HR 1.00)"
    assert not extract.composite_component_mismatch("3-point major adverse cardiovascular events", clean3)
    # a non-N-point outcome name is unaffected
    assert not extract.composite_component_mismatch("Kidney composite outcome", tecos)


def test_dpp4_tecos_declared_absent_for_estimand():
    """dpp4-mace-t2d must NOT pool TECOS under the 3-point label (its abstract is a 4-point composite)."""
    r = json.load(open(os.path.join(DOCS, "reviews", "dpp4-mace-t2d", "review.json"), encoding="utf-8"))
    prim = next(o for o in r["outcomes"] if o.get("primary"))
    assert "26052984" not in [str(t.get("label")) for t in prim.get("trials", [])], "TECOS still pooled 3-point"
    da = [t for t in prim.get("declared_absent_trials", []) if str(t.get("label")) == "26052984"]
    assert da and ("estimand" in da[0]["reason"].lower() or "4-point" in da[0]["reason"].lower() or "component" in da[0]["reason"].lower())


# ---- population guard + definition-audit fixes (cross-family definition sweep) -------------------
def test_population_mismatch_guard():
    from harness import extract
    pp = "Sixty-three patients completed the study according to the protocol; two (5.9%) vs eight (27.6%)"
    assert extract.population_mismatch(pp)
    itt = "by intention-to-treat analysis, the primary outcome occurred in 61 of 1591 vs 76 of 1592"
    assert not extract.population_mismatch(itt)


def test_definition_audit_refusals_are_absent():
    """The 4 cross-family definition-audit defects must not be pooled anywhere."""
    refused = {"23656645": "omega3-cardiovascular-events", "38184150": "omega3-cardiovascular-events",
               "17356555": "probiotics-aad-prevention", "22472744": "probiotics-aad-prevention"}
    for pmid, slug in refused.items():
        r = json.load(open(os.path.join(DOCS, "reviews", slug, "review.json"), encoding="utf-8"))
        pooled = [str(t.get("label")) for o in r["outcomes"] for t in o.get("trials", [])]
        assert pmid not in pooled, f"{pmid} still pooled in {slug} despite definition-mismatch refusal"


def test_definition_audit_index_numbers_derived():
    if not os.path.exists(os.path.join(DOCS, "definition_audit.json")):
        return
    d = json.load(open(os.path.join(DOCS, "definition_audit.json"), encoding="utf-8"))
    html = IDX.build_index(DOCS)
    assert f"{d['n_candidates']} of {d['n_rows_audited']}" in html


def test_timepoint_and_heterogeneity_guards():
    from harness import extract
    # timepoint: fires on pure in-hospital vs a follow-up window; not on a compound timepoint
    assert extract.timepoint_mismatch("index admission", "AF during 14 days of follow-up")
    assert not extract.timepoint_mismatch("28-90 day or in-hospital", "death within 90 days")
    assert not extract.timepoint_mismatch("Week 68", "at week 68")
    # composite heterogeneity: fires when composite-definition clauses differ, not on incidental mentions
    het = extract.composite_heterogeneity("Major adverse cardiovascular events", [
        "the primary composite outcome was cardiovascular death, myocardial infarction, or stroke",
        "primary composite endpoint comprised cardiovascular death, myocardial infarction, stroke, or coronary revascularization"])
    assert het
    clean = extract.composite_heterogeneity("3-point MACE", [
        "primary composite outcome was cardiovascular death, myocardial infarction, or stroke; heart failure was a secondary outcome",
        "the primary composite endpoint was death from cardiovascular causes, nonfatal MI, or nonfatal stroke"])
    assert not clean


def test_no_registry_abstract_disagreement_on_structural_facts():
    """EMPHASIS-HF class (the registry is not infallible): a partial machine domain must not be rated on a registry
    field that the trial's own abstract contradicts on a structural fact. Scans the whole corpus:
    (a) D1 basis 'NON_RANDOMIZED' while the abstract says randomized; (b) D2 'not assessed' while the
    abstract says double-blind. Any hit is a registry data error to correct (as EMPHASIS/CORP/ORIGIN were)."""
    import re
    bad = []
    for slug, r in _reviews():
        rob = (r.get("rob2") or {}).get("trials") or {}
        recs = {str(x.get("id")): (x.get("abstract") or "")
                for x in json.load(open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8")).get("records", [])}
        for pmid, a in rob.items():
            ab = recs.get(pmid, "").lower()
            doms = a.get("domains", {})
            d1b = (doms.get("D1_randomisation") or {}).get("basis", "").lower()
            if ("non_randomized" in d1b and "abstract-corrected" not in d1b
                    and re.search(r"random(ly|ized|ised)", ab)):
                bad.append(f"{slug}/{pmid} D1 NON_RANDOMIZED vs abstract 'randomized'")
            d2 = doms.get("D2_deviations") or {}
            if d2.get("level") == "not assessed" and "double-blind" in ab:
                bad.append(f"{slug}/{pmid} D2 not-assessed vs abstract 'double-blind'")
    assert not bad, "registry-vs-abstract disagreements (correct with an abstract basis): " + "; ".join(bad)
