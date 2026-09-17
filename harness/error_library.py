"""Meta-analysis error library → harness checks.

Every documented meta-analysis mistake is one of four things in this harness:
  - GATE_LIMB      : detectable on a finished review; the publication gate REFUSES if present.
  - REGRESSION_TEST: detectable in code; a test with a plant that fires PRE-fix guards it.
  - RENDERED       : a judgement the harness cannot fully make; the page STATES whether it applies.
  - NOT_CHECKED    : no mechanism yet — the work queue, in severity order.
  - VERIFICATION   : caught only by human source-verification (recorded, not machine-enforced).

Each entry names the mechanism and the evidence (a module/test/gate limb) so the coverage claim
"this review is screened against N documented meta-analysis errors" is itself auditable. `applies(review)`
returns, for one review dict, the ids whose check is ACTIVE on it (universal checks always; conditional
checks when their trigger is present), so coverage can be reported per review.
"""
from __future__ import annotations

GATE_LIMB, REGRESSION_TEST, RENDERED, NOT_CHECKED, VERIFICATION = (
    "GATE_LIMB", "REGRESSION_TEST", "RENDERED", "NOT_CHECKED", "VERIFICATION")

# id, label, kind, universal?, mechanism (module/gate-limb/test), evidence
LIBRARY = [
    ("ME-01", "Retracted / expression-of-concern trial pooled", GATE_LIMB, True,
     "gate.check_retraction + integrity.py (PubMed) — REFUSE on a retracted pooled trial",
     "test_integrity.py; cache/<slug>/integrity.json"),
    ("ME-02", "Duplicate-publication double-counting (same trial pooled twice)", GATE_LIMB, True,
     "gate.check_duplicate_publication + pipeline._dedup RCT-primacy (earliest full report wins its NCT)",
     "test_dup_pub.py"),
    ("ME-03", "Stale page / analysis-code divergence (served ≠ declared method)", GATE_LIMB, True,
     "gate.check_limb1 (served method == declared) + check_reproduction (offline replay byte-match)",
     "test_gate.py; scripts/reproduce_review.py"),
    ("ME-04", "Empty / hollow pool shipped (k=0 presented as a review)", GATE_LIMB, True,
     "gate.check_primary_result — REFUSE a page whose primary outcome has no pooled result",
     "test_gate.py"),
    ("ME-05", "No controls (a topic that cannot detect a wrong include/exclude)", GATE_LIMB, True,
     "gate.check_controls — REFUSE unless ≥1 positive (must screen IN) + ≥1 negative (must screen OUT)",
     "test_gate_controls.py"),
    ("ME-06", "Pivotal landmark trial silently missing from the pool", GATE_LIMB, False,
     "gate.check_pivotal_present — each declared pivotal must be in the committed cache or REFUSE",
     "test_gate.py"),
    ("ME-07", "Scale / estimand mixture (e.g. Peto OR pooled with a Cox HR)", RENDERED, True,
     "pipeline estimand-homogeneity: result.scale='mixed (X/Y)' when pooled trials differ; garbage pools REFUSED",
     "weakness_survey mixed-scale count; page Estimand row"),
    ("ME-08", "Wrong-endpoint binding (a number for the wrong outcome)", REGRESSION_TEST, True,
     "outcome-identity gate (extract_ctgov judgments) + composite-containment guard + generic-harm guard "
     "(caught at extraction, not the publication gate — the gate does not judge endpoint identity)",
     "test_outcome_identity.py; test_composite_guard.py"),
    ("ME-09", "Wrong-arm / control-first inverted extraction", REGRESSION_TEST, True,
     "arm-identity: inferred denominators pair each count with its own arm (reading-order + %-corroboration)",
     "test_arm_identity.py"),
    ("ME-10", "Subgroup-as-total (a post-hoc/pre-specified subgroup pooled as the trial)", REGRESSION_TEST, True,
     "subgroup guard (refuse per-protocol/post-hoc/'lowest in') + ctgov min_total + subgroup DISCLOSED (melatonin 65-80)",
     "test_extract_class.py; melatonin population note"),
    ("ME-11", "Composite substitution (pooling a composite where a single outcome is declared)", REGRESSION_TEST, True,
     "composite-containment guard — declared-single skips composite-endpoint sentences",
     "test_composite_guard.py"),
    ("ME-12", "Factorial trial: wrong factor's effect bound", REGRESSION_TEST, True,
     "factorial guard — effect-only factorial refused / correct factor required (SU.FOL.OM3 caught)",
     "test_extract_class.py; JUDGELOG omega3"),
    ("ME-13", "Multi-arm dose: arbitrary dose-arm selection without a pre-specified rule", REGRESSION_TEST, True,
     "multi-arm guard — >2 randomised arms must specify the comparison or REFUSE (CANTOS declined)",
     "test_extract_class.py"),
    ("ME-14", "Imputed variance (SD reconstructed from a figure / KM curve)", RENDERED, True,
     "continuous extractor refuses when no per-arm SD/IQR in accessible source; 'we decline where they imputed'",
     "zinc decline (JUDGELOG); test_ctgov_continuous.py refuses SE/IQR"),
    ("ME-15", "Recurrent-event count pooled as a binomial (participants)", REGRESSION_TEST, False,
     "AACT recurrent-event guard (is_recurrent_event_title; 'hospitalizations'/'number of' ⇒ events not patients)",
     "test_aact_recurrent_guard.py"),
    ("ME-16", "Outcome-based eligibility (including a trial because it reported the outcome)", RENDERED, True,
     "screening is P/I/C/design only; eligibility not based on outcome reporting; non-reporters declared-absent",
     "every protocol's eligibility clause; PRISMA flow"),
    ("ME-17", "Unverified / fabricated pooled number", GATE_LIMB, True,
     "gate.check_pooled_verified — REFUSE a page pooling any number whose digits are not located in its "
     "committed source span (verify.verify_pooled marks verified/handchecked/not-yet)",
     "test_gate.py (planted not-yet refuses); weakness_survey: 0 UNVERIFIED"),
    ("ME-18", "DL τ² small-k collapse (DerSimonian-Laird biased at k<10)", REGRESSION_TEST, True,
     "synth uses Paule-Mandel (not DL); validated vs metafor <1e-6",
     "test_synth.py; advanced-stats DL rule"),
    ("ME-19", "HKSJ-vs-Wald drift (z used where t_{k-1} required at small k)", REGRESSION_TEST, True,
     "synth HKSJ CI on t_{k-1} with floor max(1,Q/(k-1)); k=1 shows single-trial effect, no RE machinery",
     "test_synth.py; advanced-stats HKSJ rules"),
    ("ME-20", "Prediction interval wrong (z-based or t_{k-2})", REGRESSION_TEST, True,
     "synth PI = mu ± t_{k-1}·sqrt(tau2+se^2); undefined and suppressed at k<2",
     "test_synth.py; advanced-stats PI rule"),
    ("ME-21", "Natural-scale pooling (should pool log-effects)", REGRESSION_TEST, True,
     "synth pools log(RR/OR/HR/IRR), back-transforms — avoids the Simpson trap",
     "test_synth.py"),
    ("ME-22", "Retrospective registration not flagged (reporting-bias signal)", RENDERED, False,
     "integrity._prospective (AACT dates): registered-after-enrolment flagged, non-blocking, rendered",
     "cache/<slug>/integrity.json retrospectively_registered"),
    ("ME-23", "partial machine assessment / selective-outcome-reporting not assessed", RENDERED, True,
     "rob2.py D5 = registered-primary vs pooled outcome; coverage stated per page; unassessed trials shown",
     "test_page.py partial machine coverage; rob2.json"),
    ("ME-24", "Search miss presented as absence (recall not measured)", RENDERED, True,
     "registry-first recall metric per topic (recovered X/Y of known); reach vs inclusion distinguished",
     "recall.json; Search tab"),
    # --- NOT YET CHECKED — the work queue, in severity order ---
    ("ME-25", "Unit-of-analysis: multi-arm SHARED-CONTROL double-counting in one pool", GATE_LIMB, True,
     "gate.check_no_double_counted_trial — REFUSE if a trial id is pooled more than once within an outcome "
     "(one-effect-per-trial + the multi-arm guard prevent it; this asserts the guarantee structurally)",
     "test_gate/test_error_library planted-duplicate refuses"),
    ("ME-26", "Unit-of-analysis: cluster-randomised trial without design-effect inflation", RENDERED, True,
     "unit_of_analysis.detect flags a pooled cluster-randomized trial from its committed abstract; the page "
     "DISCLOSES that patient-level counts are pooled without an ICC design-effect (optimistic precision) — "
     "cannot correct without the unreported ICC (e.g. balanced-crystalloids: SMART/SALT-ED/SPLIT)",
     "harness/unit_of_analysis.py; test_unit_of_analysis.py; RoB tab disclosure"),
    ("ME-27", "Unit-of-analysis: crossover trial paired-data / carryover", RENDERED, True,
     "unit_of_analysis.detect flags a pooled crossover-design trial; the page DISCLOSES that it is pooled "
     "without a within-subject/paired adjustment (the crystalloid trials are cluster-randomized multiple-crossover)",
     "harness/unit_of_analysis.py; test_unit_of_analysis.py"),
    ("ME-28", "Zero-cell continuity correction applied unconditionally (biases OR toward 1)", REGRESSION_TEST, True,
     "synth adds the 0.5 correction ONLY to a study that has a zero cell (2x2) or zero event (IRR), never "
     "unconditionally — per the advanced-stats rule; asserted directly on the pooler",
     "test_synth.py::test_zero_cell_continuity_applied_only_to_that_study + test_irr_zero_event_correction"),
    ("ME-29", "Small-study / publication-bias not assessed (funnel/Egger)", RENDERED, True,
     "small k stated as the dominant limitation on every page; Egger low-power at our k, not computed",
     "weakness_survey small-k; stated limitation"),
    ("ME-30", "GRADE certainty not formally rated", RENDERED, True,
     "certainty signals shown (RoB/inconsistency/imprecision) but a formal GRADE rating is NOT automated",
     "PRISMA item 15 declared partial"),
    # --- folded in from the external e156/rapidmeta 13_ERROR_LIBRARY.md cross-check (UG-007, UG-013) ---
    ("ME-31", "Network / indirect-comparison connectivity not tested (NMA)", RENDERED, True,
     "we pool PAIRWISE only; scope.py flags single-drug-vs-drug-CLASS comparator mismatch (a PICO/NMA "
     "error class) and states it; a full NMA connectivity/consistency test is N/A because no network is pooled",
     "harness/scope.py; comparator scope note; JUDGELOG scope-audit"),
    ("ME-33", "Throttled/partial fetch → silently incomplete cache builds a wrong pool", GATE_LIMB, True,
     "gate.check_fetch_complete — REFUSE if a CORE source (PubMed/Europe PMC/ClinicalTrials.gov) reported "
     "RAN_ERROR; a rate-limit (429) drops trials (incl. a pivotal) and the degraded cache looks complete",
     "test_error_library planted core RAN_ERROR refuses; semaglutide 429 build refused"),
    ("ME-32", "Trial conflict-of-interest / funding integrity not assessed", RENDERED, False,
     "funding.scan_pooled classifies each pooled trial's funding source (industry / public-non-profit / mixed / "
     "not-stated) from a VERBATIM statement in the committed full text (preferred) or abstract, and the page "
     "DISCLOSES it per trial with the span and the industry-funded count; industry funding is the documented bias "
     "direction. Never inferred (refuse-on-absence: 'not stated in source'); disclosed not adjusted, because the "
     "per-trial bias magnitude is not quantifiable from a funding line (prior work: a uniform industry x0.80 channel was inert)",
     "RENDERED per pooled trial (from source); severity medium — a documented reporting/bias dimension, cross-checked from UG-013"),
]

_UNIVERSAL = {e[0] for e in LIBRARY if e[3]}
_KINDS = {e[0]: e[2] for e in LIBRARY}


def summary():
    """Count the library by kind."""
    from collections import Counter
    c = Counter(e[2] for e in LIBRARY)
    return {"total": len(LIBRARY), **c}


def _has_multiarm(review):
    for o in review.get("outcomes", []):
        for t in o.get("trials", []) or []:
            if "multi" in (t.get("source", "").lower()) or "mg group" in (t.get("source", "").lower()):
                return True
    return False


def applies(review, config=None):
    """Ids whose check is ACTIVE on this review: every universal check, plus conditional checks whose
    trigger is present. A NOT_CHECKED entry is never 'active' (it is the gap, reported separately)."""
    active = set(i for i in _UNIVERSAL if _KINDS[i] != NOT_CHECKED)
    cfg = config or {}
    # conditional checks
    if cfg.get("pivotal_trials"):
        active.add("ME-06")          # pivotal-present limb only when pivotals declared
    active.add("ME-15")              # recurrent-event guard runs on any AACT-sourced outcome
    active.add("ME-22")              # retrospective-registration flag computed for any NCT-linked trial
    if any((o.get("trials") for o in review.get("outcomes", []) or [])):
        active.add("ME-32")          # per-trial funding/COI disclosure runs on any review with pooled trials
    return active


def coverage(review, config=None):
    """(n_active, n_checkable, active_ids). n_checkable excludes NOT_CHECKED (the gaps)."""
    checkable = [e[0] for e in LIBRARY if e[2] != NOT_CHECKED]
    active = applies(review, config)
    active &= set(checkable)
    return len(active), len(checkable), sorted(active)


def not_checked():
    return [(e[0], e[1], e[5]) for e in LIBRARY if e[2] == NOT_CHECKED]
