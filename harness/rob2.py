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


def assess(design: dict, registered_primaries: list, pooled_outcome: str, matches) -> dict:
    """design: AACT designs row (allocation, subject_masked, caregiver_masked, outcomes_assessor_masked).
    registered_primaries: the trial's AACT-registered PRIMARY outcome titles.
    matches(a, b) -> bool: outcome-identity match (embedding). Returns {domain: {level, basis}}."""
    design = design or {}
    alloc = (design.get("allocation") or "").upper()
    d1 = ("low" if alloc == "RANDOMIZED" else ("some concerns" if alloc else "not assessed"))
    sm, cm = _b(design.get("subject_masked")), _b(design.get("caregiver_masked"))
    if sm and cm:
        d2 = "low"
    elif sm is False or cm is False:
        d2 = "some concerns"
    else:
        d2 = "not assessed"
    oa = _b(design.get("outcomes_assessor_masked"))
    d4 = "low" if oa else ("some concerns" if oa is False else "not assessed")
    if not registered_primaries:
        d5, d5b = "not assessed", "no registered primary outcome available"
    elif any(matches(pooled_outcome, rp) for rp in registered_primaries):
        d5, d5b = "low", "the pooled outcome IS the trial's pre-registered primary outcome"
    else:
        d5, d5b = "some concerns", ("the pooled outcome is not the trial's registered primary "
                                    f"(registered: {registered_primaries[0][:60]!r}) — a registered secondary")
    return {
        "D1_randomisation": {"level": d1, "basis": f"AACT allocation = {alloc or 'unstated'}"},
        "D2_deviations": {"level": d2, "basis": f"blinding: subject_masked={sm}, caregiver_masked={cm}"},
        "D3_missing_outcome_data": {"level": "not assessed",
                                    "basis": "attrition/participant-flow needs human judgement — not automated"},
        "D4_outcome_measurement": {"level": d4, "basis": f"outcome-assessor blinded = {oa}"},
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
