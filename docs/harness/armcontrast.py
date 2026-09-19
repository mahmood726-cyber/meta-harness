"""Arm-contrast parser (TIER-1 structural fix, demanded by six audits).

Eligibility must test the RANDOMISED CONTRAST -- what actually DIFFERS between the randomised arms --
not the mere co-occurrence of the intervention word in the record. A trial where the drug of interest is
given as BACKGROUND in every arm (MIRO-CKD: all arms dapagliflozin; LIRA-ADD2SGLT2i: all arms on SGLT2,
randomised liraglutide; EXENDA: all arms dapagliflozin, randomised exenatide) has NO randomised contrast
for that drug and must not be screened in.

Built from the committed AACT snapshot (design_groups + interventions + design_group_interventions), so it
replays offline and reproduces. Placebo / sham / standard-care interventions are normalised away, so a
"placebo for X" comparator arm never inherits the active drug X. FAILS OPEN: when a trial has no AACT arm
data (old trials, unregistered), the contrast is unknown and the parser abstains (returns None) -- it can
only ever REMOVE a clearly-background inclusion, never invent an exclusion from missing data.
"""
from __future__ import annotations

import re

from harness import aact, aact_cache

# A control/placebo arm is not an active intervention; collapsing it to nothing prevents a
# "placebo for dapagliflozin" arm from leaking 'dapagliflozin' into the control side.
_PLACEBO = re.compile(r"placebo|\bsham\b|matching|standard care|usual care|no treatment|control arm", re.I)


def _norm_intv(name: str | None) -> str | None:
    if not name:
        return None
    if _PLACEBO.search(name):
        return None
    return name.strip().lower()


def build_arm_index(ncts) -> dict:
    """Replay measured contrasts only; no snapshot discovery, even outside a build."""
    cached = aact_cache.values("arm_index")
    return {n: (set(cached[n][0]), set(cached[n][1]))
            for n in sorted({str(n).upper() for n in ncts if n}) if n in cached}


def measure_arm_index(ncts) -> dict:
    """Three AACT scans total (not per-trial): {NCT: (common, differing)} where `common` are active
    interventions present in EVERY arm (background) and `differing` are those in some-but-not-all arms
    (the randomised contrast). A trial with <2 arms or no linked active interventions is omitted (unknown)."""
    want = {(n or "").upper() for n in ncts if n}
    if not want:
        return {}
    arms: dict[str, dict] = {}      # nct -> {design_group_id -> set(active intv names)}
    for r in aact._iter_rows(aact._table("design_groups")):
        n = (r.get("nct_id") or "").upper()
        if n in want:
            arms.setdefault(n, {})[r["id"]] = set()
    iv: dict[str, str | None] = {}  # intervention id -> normalised active name (or None if placebo)
    for r in aact._iter_rows(aact._table("interventions")):
        if (r.get("nct_id") or "").upper() in want:
            iv[r["id"]] = _norm_intv(r.get("name"))
    for r in aact._iter_rows(aact._table("design_group_interventions")):
        n = (r.get("nct_id") or "").upper()
        if n in want and n in arms:
            g = arms[n].get(r.get("design_group_id"))
            nm = iv.get(r.get("intervention_id"))
            if g is not None and nm:
                g.add(nm)
    out = {}
    for n, groups in arms.items():
        sets = [s for s in groups.values()]
        if len(sets) < 2 or not any(sets):
            continue  # need >=2 arms and at least one linked active intervention
        allint = set().union(*sets)
        common = set.intersection(*sets)
        out[n] = (common, allint - common)
    return out


def _kw_match(keywords, pool):
    for kw in keywords or []:
        k = (kw or "").strip().lower()
        if not k:
            continue
        for intv in pool:
            if k in intv or intv in k:
                return kw, intv
    return None


def _kw_matches(keywords, pool) -> bool:
    return _kw_match(keywords, pool) is not None


def contrast_status(nct: str, keywords, index: dict) -> tuple[str, str]:
    """(status, basis) disclosure for a pooled trial's randomised contrast, so a fail-open inclusion is
    VISIBLE rather than silent. status in:
      verified            -> the intervention of interest matches a DIFFERING intervention (a genuine
                             randomised contrast confirmed from the registry arm structure)
      background_only      -> the interest is present in EVERY arm; the contrast is a different drug
                             (MIRO-CKD pattern -- a false inclusion; should not occur for a pooled trial)
      unverified_granularity -> a contrast exists but the interest is not machine-matchable to a coded arm
                             (registry codes it under a class label or development code, e.g. 'BI 10773',
                             'AMR101'); not background, but not machine-verified
      unverified_no_contrast -> the registry coded no arm-level contrast (only one active intervention)
      unverified_no_arm_data -> no AACT arm data for this trial (old / unregistered)"""
    entry = index.get((nct or "").upper())
    if entry is None:
        return ("unverified_no_arm_data", "no registry arm data for this trial (contrast not machine-verified)")
    common, differing = entry
    if not differing:
        return ("unverified_no_contrast", "registry coded no arm-level contrast (single active intervention)")
    diff_match = _kw_match(keywords, differing)
    if diff_match:
        kw, arm = diff_match
        return ("verified", f"parser-confirmed contrast: keyword {kw!r} matched AACT arm intervention "
                f"{arm!r}; the intervention of interest DIFFERS across the randomised arms")
    common_match = _kw_match(keywords, common)
    if common_match:
        kw, arm = common_match
        return ("background_only", "the intervention of interest is present in EVERY arm (background); the "
                f"randomised contrast is a different intervention (keyword {kw!r} matched AACT arm "
                f"intervention {arm!r})")
    return ("unverified_granularity", "a randomised contrast exists but the intervention of interest is not "
            "machine-matchable to a coded arm (registry class label / development code); contrast not machine-verified")


def background_only_inclusion(nct: str, keywords, index: dict) -> bool | None:
    """Decide, CONSERVATIVELY, whether the intervention of interest is PURE BACKGROUND (present in every
    randomised arm) while a DIFFERENT intervention is the randomised contrast -- the MIRO-CKD pattern (all
    arms dapagliflozin, randomised balcinrenone), a false inclusion.

    True  -> exclude: the interest matches an intervention COMMON to every arm AND a different intervention
             is the randomised contrast (differing set non-empty and the interest is not in it).
    False -> keep: the interest is not provably background (it is the contrast, or drug-vs-placebo, etc.).
    None  -> abstain (fail open): no AACT arm data, or NO randomised contrast is detectable from the coded
             interventions (differing empty -- e.g. only the active drug is coded and the control arm is
             blank). Abstaining here is deliberate: a coded-name granularity gap (class label 'GLP-1
             receptor agonist' vs coded 'liraglutide'; dev code 'BI 10773'; 'AMR101') must NEVER manufacture
             an exclusion. The check can only ever REMOVE a provably-background inclusion.

    It therefore does NOT catch the 'class label named only in the arm TITLE' pattern (LIRA-ADD2SGLT2i,
    EXENDA), where the interest is absent from every coded arm and so is indistinguishable from a
    granularity-hidden genuine trial -- those need drug-class resolution or a manual intervention_none entry."""
    entry = index.get((nct or "").upper())
    if entry is None:
        return None
    common, differing = entry
    if not differing:
        return None  # no detectable randomised contrast -> abstain, never exclude
    if _kw_matches(keywords, common) and not _kw_matches(keywords, differing):
        return True  # interest is in EVERY arm (background); the contrast is a different intervention
    return False
