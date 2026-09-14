"""Recovery-induced-incompatibility recheck.

A recovery is verified BEFORE integration (is this trial's number right?). That is not enough:
adding a trial can break the POOL it joins even when the trial itself is correct
(RECOVERY_INDUCED_INCOMPATIBILITY). This module RE-RUNS the compatibility contract on the whole
topic AFTER integration and records the verdict, so the recovery path checks the pool, not just
the trial.

Two things are surfaced:
  hard_incompatible  — the pooled trials span >1 effect-measure compatibility class (compat.check).
                       This is a build-refusal condition (a recovery that pools a RATE trial into a
                       FIRST_EVENT pool must be caught here, not silently averaged).
  label_mix_small_k  — the pool combines DIFFERENT effect-measure labels (e.g. HR + RR) at small k.
                       Not a hard incompatibility (a Cox HR and a cumulative RR are the same
                       first-event class), but at small k a single influential trial can dominate,
                       so it is DISCLOSED as a limitation (surfaced, not smoothed) rather than
                       reassured away. This is exactly the spironolactone case: RALES RR 0.70 +
                       EMPHASIS-HF HR 0.76 + reconstructed J-EMPHASIS RR 1.685, k=3.
"""
from . import compat

_SMALL_K = 4


def recheck_outcome(o, core):
    """Return the recovery-compat verdict for one pooled outcome, or None if it is not a pool."""
    res = o.get("result") or {}
    if not res.get("k") or res.get("suppressed_incompatible"):
        # a suppressed pool is already handled by the incompatibility path; nothing to add.
        return None
    key = compat.outcome_key(o, core)
    if not key:
        return None
    em = res.get("estmeasure") or {}
    labels = em.get("labels") or ([res.get("scale")] if res.get("scale") else [])
    labels = [l for l in labels if l]
    trials = o.get("trials") or []
    reconstructed = [t.get("label") for t in trials if t.get("derivation") == "reconstructed"]
    verdict = {
        "hard_incompatible": not key["matched"],
        "mismatches": key.get("mismatches") or [],
        "effect_measure_labels": sorted(set(labels)),
        "k": res.get("k"),
        "reconstructed_members": reconstructed,
        "label_mix_small_k": bool(len(set(labels)) > 1 and (res.get("k") or 0) <= _SMALL_K),
    }
    return verdict


def recheck(core):
    """Re-run the compatibility contract across every pooled outcome of a topic. Returns
    {outcome_name: verdict}. Empty when the topic has no rendered pool."""
    out = {}
    for o in (core.get("outcomes") or []):
        v = recheck_outcome(o, core)
        if v is not None:
            out[o.get("name")] = v
    return out


def disclosure(verdict):
    """One rendered limitation string for a pool whose recovery-recheck surfaced a concern, or None.
    Never reassures -- a label mix at small k is stated as an approximation to weigh, not waved away."""
    if not verdict:
        return None
    if verdict.get("hard_incompatible"):
        return None  # the incompatibility/suppression path renders its own, stronger banner
    if verdict.get("label_mix_small_k"):
        labs = " + ".join(verdict["effect_measure_labels"])
        recon = verdict.get("reconstructed_members") or []
        recon_note = (f" One contributing effect is reconstructed from raw arm counts "
                      f"({', '.join(str(r) for r in recon)}); at this k a single influential trial can "
                      f"move the summary and widen the interval." if recon else
                      f" At this k a single influential trial can move the summary.")
        return (f"Pooled trials report different effect-measure labels ({labs}), combined as "
                f"first-event relative ratios. This is an approximation, not an identity: a hazard "
                f"ratio and a cumulative risk ratio are not the same number when events are common "
                f"or follow-up differs.{recon_note} Read the pooled effect as approximate.")
    return None
