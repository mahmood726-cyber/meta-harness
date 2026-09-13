"""RoB2-style risk-of-bias assessment, built from what is MACHINE-AVAILABLE (AACT structured design
fields + registry-vs-pooled outcome), with honest "not assessed — requires human judgement" where a
domain needs it. Partial-but-honest beats absent: no published-meta comparator in our set renders a
per-trial risk-of-bias signal computed from the registry, and Domain 5 (selective reporting) computed
from registry-vs-report is something most metas do worse than this.

Domains (RoB2):
  D1 randomisation      — AACT allocation (RANDOMIZED) [concealment as reported]
  D2 deviations         — blinding of participants/personnel (subject_masked, caregiver_masked)
  D3 missing outcome    — attrition; NOT assessed here (needs participant-flow + human judgement)
  D4 outcome measurement— blinded outcome assessment (outcomes_assessor_masked)
  D5 selective reporting— is the pooled outcome the trial's PRE-REGISTERED PRIMARY? (registry vs pooled)

Levels: "low" | "some concerns" | "high" | "not assessed". Never guessed — absence => "not assessed".
"""
from __future__ import annotations


def _b(v):
    """AACT boolean: 't'/'f' (or 'true'/'false'); anything else is unknown (None)."""
    s = str(v or "").strip().lower()
    if s in ("t", "true", "yes"):
        return True
    if s in ("f", "false", "no"):
        return False
    return None


def _d3(attr) -> dict:
    """RoB2 D3 (missing outcome data). DEFAULT: NOT ASSESSED (audits 20/21). The only machine-available
    signal is AACT participant-flow (study discontinuation / overall + between-arm attrition), and study
    discontinuation is NOT outcome missingness -- whether missingness DEPENDS on the outcome, and whether
    the OUTCOME itself was available despite discontinuation, need human reading of the trial. We do not
    have that evidence for any pooled trial, so a D3 LEVEL rating (low/some concerns/high) derived from the
    attrition PROXY is unearned: it contaminated the low-risk-only sensitivity and the GRADE risk-of-bias
    input across the corpus. D3 is therefore reported as NOT ASSESSED, with the attrition figures shown as
    context (a signal for a human), never as the rating. A genuine outcome-missingness rating requires
    committed outcome-level missingness evidence, which is a human judgement the registry cannot supply."""
    if not attr or attr.get("overall_pct") is None:
        return {"level": "not assessed",
                "basis": "no AACT participant-flow data; outcome missingness needs human judgement"}
    o, d = attr["overall_pct"], attr.get("differential_pct") or 0
    return {"level": "not assessed",
            "basis": (f"not assessed — AACT flow shows between-arm differential attrition {d}% (overall {o}%), "
                      "but study discontinuation is NOT outcome missingness and outcome-dependence needs human "
                      "reading; the attrition figures are context, not a risk-of-bias rating")}


def assess(design: dict, registered_primaries: list, pooled_outcome: str, matches,
           registered_secondaries: list = None, blinded_by_text: bool = False,
           randomized_by_text: bool = False) -> dict:
    """design: AACT designs row (allocation, subject_masked, caregiver_masked, outcomes_assessor_masked,
    masking). registered_primaries / registered_secondaries: the trial's AACT-registered PRIMARY and
    SECONDARY outcome titles (a registered secondary is prespecified -> not selective reporting).
    blinded_by_text: the trial's own abstract/full text states double-blind / placebo-controlled /
    double-masked (the TOP of the RoB source hierarchy -- overrides missing or contradictory registry
    masking; EMPHASIS-HF class: a trial's own text beats a registry field).
    randomized_by_text: the trial's own abstract states random assignment (randomly assigned/allocated,
    randomized to ...) -- same source hierarchy applied to D1: a registry allocation field of
    NON_RANDOMIZED that the trial's own text contradicts is a registry data error (EMPHASIS-HF /
    NCT00232180 read NON_RANDOMIZED though it was a randomised double-blind RCT), corrected with an
    abstract basis and the disagreement FLAGGED.
    matches(a, b) -> bool: outcome-identity match (embedding). Returns {domain: {level, basis}}."""
    design = design or {}
    alloc = (design.get("allocation") or "").upper()
    if alloc == "RANDOMIZED":
        d1, d1b = "low", f"AACT allocation = {alloc}"
    elif randomized_by_text:
        # SOURCE HIERARCHY on D1 (EMPHASIS-HF class): the trial's own abstract states random assignment;
        # the registry allocation field (NON_RANDOMIZED / unstated) is a data error, corrected + flagged.
        d1, d1b = "low", (f"AACT allocation = {alloc or 'unstated'} but the trial's own abstract states "
                          "random assignment (abstract-corrected registry data error; FLAGGED "
                          "registry-vs-trial disagreement)")
    elif alloc:
        d1, d1b = "some concerns", f"AACT allocation = {alloc}"
    else:
        d1, d1b = "not assessed", "AACT allocation = unstated"
    # SOURCE HIERARCHY (denosumab/FREEDOM cold audit): the trial-level masking (AACT 'masking' =
    # Double/Triple/Quadruple, a trial-specific field) OVERRIDES the generic per-role Booleans
    # (subject_masked/caregiver_masked/outcomes_assessor_masked), which are frequently wrong -- FREEDOM
    # was fully double-blind (subjects, investigators, site staff AND assessors) yet its
    # outcomes_assessor_masked/caregiver_masked Booleans read False, silently downgrading D2/D4 and
    # propagating to a GRADE -1. A masked trial's blinding-based domains are LOW, with the Boolean
    # disagreement FLAGGED rather than silently resolved in the registry's favour.
    masking = (design.get("masking") or "").upper()
    masking_blinded = any(w in masking for w in ("DOUBLE", "TRIPLE", "QUADRUPLE"))
    trial_blinded = masking_blinded or blinded_by_text
    _src = (f"trial masking = {masking.title()}" if masking_blinded else "the trial's own abstract/text (double-blind/placebo-controlled)")
    sm, cm = _b(design.get("subject_masked")), _b(design.get("caregiver_masked"))
    if trial_blinded:
        d2 = "low"
        d2b = (f"{_src} (blinded); overrides per-role Booleans "
               f"subject_masked={sm}/caregiver_masked={cm} (FLAGGED registry-vs-trial disagreement)"
               if (sm is False or cm is False) else
               f"{_src} (blinded): participants/personnel blinded")
    elif sm and cm:
        d2, d2b = "low", f"blinding: subject_masked={sm}, caregiver_masked={cm}"
    elif sm is False or cm is False:
        d2, d2b = "some concerns", f"blinding: subject_masked={sm}, caregiver_masked={cm}"
    else:
        d2, d2b = "not assessed", f"blinding: subject_masked={sm}, caregiver_masked={cm}"
    oa = _b(design.get("outcomes_assessor_masked"))
    if trial_blinded:
        d4 = "low"
        d4b = (f"{_src} (blinded); overrides outcomes_assessor_masked={oa} "
               f"(FLAGGED registry-vs-trial disagreement)" if oa is False else
               f"{_src} (blinded): outcome assessment blinded")
    else:
        d4 = "low" if oa else ("some concerns" if oa is False else "not assessed")
        d4b = f"outcome-assessor blinded = {oa}"
    # D5 SELECTIVE REPORTING: a PRE-REGISTERED outcome -- primary OR secondary -- is prespecified and is
    # NOT selective reporting (tranexamic/WOMAN, FIGARO, SELECT cold audits: death-due-to-bleeding is a
    # registered KEY SECONDARY in WOMAN's SAP; flagging it 'some concerns' as "a registered secondary" was
    # wrong). Only downgrade when the pooled outcome matches NO registered outcome (a genuinely post-hoc /
    # unregistered outcome).
    registered_secondaries = registered_secondaries or []
    if not registered_primaries and not registered_secondaries:
        d5, d5b = "not assessed", "no registered outcomes available for this trial"
    elif any(matches(pooled_outcome, rp) for rp in registered_primaries):
        d5, d5b = "low", "the pooled outcome IS the trial's pre-registered primary outcome"
    elif any(matches(pooled_outcome, rs) for rs in registered_secondaries):
        d5, d5b = "low", ("the pooled outcome is a PRE-REGISTERED SECONDARY outcome (prespecified in the "
                          "registry) -- prespecified reporting, not selective reporting")
    else:
        d5, d5b = "some concerns", ("the pooled outcome matches no registered primary or secondary outcome "
                                    f"(registered primary: {(registered_primaries or ['<none>'])[0][:50]!r}) "
                                    "-- possibly post-hoc/unregistered")
    return {
        "D1_randomisation": {"level": d1, "basis": d1b},
        "D2_deviations": {"level": d2, "basis": d2b},
        "D3_missing_outcome_data": _d3(design.get("attrition")),
        "D4_outcome_measurement": {"level": d4, "basis": d4b},
        "D5_selective_reporting": {"level": d5, "basis": d5b},
    }


def overall(domains: dict) -> str:
    """RoB2 algorithm (conservative): high if any domain high; some concerns if any 'some concerns';
    low only if every ASSESSED domain is low; else 'some concerns (partial — domains not assessed)'."""
    levels = [d["level"] for d in domains.values()]
    if "high" in levels:
        return "high"
    assessed = [x for x in levels if x != "not assessed"]
    if any(x == "some concerns" for x in assessed):
        return "some concerns"
    if assessed and all(x == "low" for x in assessed):
        return "low (on assessed domains; some domains require human judgement)"
    return "some concerns (partial — key domains not assessed)"
