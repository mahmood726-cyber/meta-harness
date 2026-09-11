"""Locate-parse-round-trip IDENTITY GATE (model-derived, cached, replay-safe).

The model (Fable) LOCATES a verbatim span for the review's target outcome and judges its IDENTITY
(is this the target outcome, same concept + timepoint, both arms, matching population). It emits NO
number. Deterministic code still parses the number; this layer only DECIDES whether the located
evidence is the review's outcome at all — the safeguard against the right-number/wrong-endpoint class
(EMPEROR secondary, appendicitis 30-day-resolution, vitamin-D influenza-A-as-ARI). Judgments are
cached per (slug, pmid, outcome) with the model id, prompt hash and date, committed and rendered
model-derived, so replay reproduces without re-calling the model.

Opt-in per topic via config.locate_gate; absent a committed judgment the gate is inert (existing
behaviour unchanged). A judgment with is_target_outcome == False forces the trial to declared-absent
with the model's reason — it can only REMOVE a mis-identified number, never add one.
"""
from __future__ import annotations
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(slug: str) -> dict:
    """{pmid: {outcome: judgment}} committed at cache/<slug>/locate_judgments.json, else {}."""
    p = os.path.join(ROOT, "cache", slug, "locate_judgments.json")
    if not os.path.exists(p):
        return {}
    try:
        return json.load(open(p, encoding="utf-8"))
    except (ValueError, OSError):
        return {}


def rejects(judgments: dict, pmid: str, outcome_name: str) -> dict | None:
    """Return the judgment (with a 'reject_reason') if the model identified this (pmid, outcome) as an
    IDENTITY FAILURE — the located evidence is NOT the target outcome (is_target_outcome False) OR the
    trial's population does not match the review (population_matches False, e.g. DAPA-HF's HFrEF in an
    HFpEF topic). The gate then declares the trial absent. Else None (inert). It can only REMOVE a
    mis-identified number, never add one."""
    j = (judgments.get(str(pmid)) or {}).get(outcome_name)
    if not j:
        return None
    if j.get("is_target_outcome") is False:
        return {**j, "reject_reason": "located evidence is not the target outcome"}
    if j.get("population_matches") is False:
        return {**j, "reject_reason": "trial population does not match the review population"}
    return None
