"""Outcome membership contract.

Each outcome carries one membership object keyed by the trial identifier used in
the pooled row, not by display label. Consumers that need a denominator (trial
integrity, RoB sensitivity, comparator parity) read the same object.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any


REGISTRY_ONLY_INTEGRITY_SOURCE = "ctgov_results_only - retraction not checkable via PubMed"

_NCT_RE = re.compile(r"\bNCT\d{8}\b", re.I)
_PMID_RE = re.compile(r"\bPMID[:\s]*(\d+)\b", re.I)
_NUMERIC_PMID_RE = re.compile(r"^\d+$")
_NEGATIVE_PARITY_RE = re.compile(
    r"\b(gap trials?|refus(?:e|es|ed|al)|declared[- ]absent|not pooled|excluded|"
    r"design[- ]excluded|scope[- ]excluded|out[- ]of[- ]scope|declined)\b",
    re.I,
)


def trial_key(trial: dict[str, Any]) -> str:
    return str((trial or {}).get("id") or "").strip()


def canonical_trial_key(value: Any) -> str:
    s = str(value or "").strip()
    if not s:
        return ""
    nct = _NCT_RE.search(s)
    if nct:
        return nct.group(0).upper()
    pmid = _PMID_RE.search(s)
    if pmid:
        return pmid.group(1)
    if _NUMERIC_PMID_RE.match(s):
        return s
    return s


def key_variants(value: Any) -> set[str]:
    s = str(value or "").strip()
    c = canonical_trial_key(s)
    out = {x for x in (s, c) if x}
    if c and _NUMERIC_PMID_RE.match(c):
        out.add(f"PMID {c}")
    return out


def lookup_by_trial_key(mapping: dict[str, Any], key: Any) -> Any:
    if not mapping:
        return None
    for candidate in key_variants(key):
        if candidate in mapping:
            return mapping[candidate]
    canon = canonical_trial_key(key)
    if not canon:
        return None
    for existing, value in mapping.items():
        if canonical_trial_key(existing) == canon:
            return value
    return None


def _screen_record_key(record: dict[str, Any]) -> str:
    rid = str((record or {}).get("id") or "").strip()
    if not rid:
        return ""
    nct = _NCT_RE.search(rid)
    if nct:
        return nct.group(0).upper()
    nums = re.findall(r"\b\d{7,9}\b", rid)
    if nums and (record or {}).get("id_type") == "pmid":
        return f"PMID {nums[-1]}"
    if nums:
        return nums[-1]
    return rid


def _unique(seq: list[str]) -> list[str]:
    out, seen = [], set()
    for value in seq:
        value = str(value or "").strip()
        if value and value not in seen:
            out.append(value)
            seen.add(value)
    return out


def _input_set_version(seed: dict[str, Any]) -> str:
    payload = json.dumps(seed, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_outcome_membership(
    outcome: dict[str, Any],
    included: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    pooled = _unique([trial_key(t) for t in outcome.get("trials", []) or []])
    declared_absent = _unique([
        str(a.get("id") or "").strip()
        for a in outcome.get("declared_absent_trials", []) or []
    ])
    refused = _unique([
        str(r.get("id") or "").strip()
        for r in outcome.get("design_refusals", []) or []
    ] + [
        str(a.get("id") or "").strip()
        for a in outcome.get("declared_absent_trials", []) or []
        if str(a.get("absent_kind") or "").startswith("refused")
    ])
    screened = _unique([
        _screen_record_key(d)
        for d in (included or [])
        if (d or {}).get("decision") == "include"
    ])
    accounted = {canonical_trial_key(k) for k in (pooled + declared_absent + refused) if k}
    screened_in_not_pooled = [k for k in screened if canonical_trial_key(k) not in accounted]
    seed = {
        "outcome": outcome.get("name"),
        "pooled": pooled,
        "declared_absent": declared_absent,
        "refused": refused,
        "screened_in": screened,
    }
    return {
        "pooled": pooled,
        "declared_absent": declared_absent,
        "refused": refused,
        "screened_in_not_pooled": screened_in_not_pooled,
        "input_set_version": _input_set_version(seed),
    }


def outcome_membership(outcome: dict[str, Any], review: dict[str, Any] | None = None) -> dict[str, Any]:
    membership = outcome.get("membership")
    if isinstance(membership, dict) and "pooled" in membership:
        return membership
    included = ((review or {}).get("screening") or {}).get("records") or []
    return build_outcome_membership(outcome, included)


def pooled_membership_keys(review: dict[str, Any]) -> list[str]:
    keys = []
    for outcome in review.get("outcomes", []) or []:
        keys.extend(outcome_membership(outcome, review).get("pooled") or [])
    return _unique(keys)


def integrity_with_membership(
    integrity: dict[str, Any] | None,
    outcomes: list[dict[str, Any]],
) -> dict[str, Any] | None:
    pooled = _unique([
        key
        for outcome in outcomes or []
        for key in outcome_membership(outcome).get("pooled", [])
    ])
    if not integrity and not pooled:
        return None
    out = copy.deepcopy(integrity or {})
    per_pmid = out.get("per_pmid") or {}
    per_trial = {}
    pubmed_checked = 0
    not_checkable = 0
    not_assessed = 0
    for key in pooled:
        canon = canonical_trial_key(key)
        if _NUMERIC_PMID_RE.match(canon):
            entry = copy.deepcopy(per_pmid.get(canon) or {})
            if not entry:
                not_assessed += 1
                per_trial[key] = {
                    "trial_key": key, "pubmed_key": canon,
                    "pubmed_checked": False,
                    "state": "NOT_ASSESSED",
                    "evidence": "NOT_ASSESSED (offline lane): no held integrity result for this PMID",
                }
                continue
            pubmed_checked += 1
            per_trial[key] = {
                "trial_key": key,
                "pubmed_key": canon,
                "pubmed_checked": True,
                "integrity_source": out.get("source") or "PubMed efetch",
                "retracted": bool(entry.get("retracted")),
                "concern": bool(entry.get("concern")),
                "evidence": entry.get("evidence"),
            }
        else:
            not_checkable += 1
            per_trial[key] = {
                "trial_key": key,
                "pubmed_checked": False,
                "integrity_source": REGISTRY_ONLY_INTEGRITY_SOURCE,
                "retraction_checkable": False,
                "evidence": "ClinicalTrials.gov registry-only row has no PubMed retraction notice channel",
            }
    out["n_pooled"] = len(pooled)
    out["n_pubmed_checked"] = pubmed_checked
    out["n_not_checkable"] = not_checkable
    out["n_not_assessed"] = not_assessed
    out["per_trial"] = per_trial
    out["membership_pooled"] = pooled
    return out


def _trial_identities(trial: dict[str, Any]) -> set[str]:
    identities = set()
    for value in (trial_key(trial), canonical_trial_key(trial_key(trial)), trial.get("label")):
        if value:
            identities.add(str(value))
    source = str(trial.get("source") or "")
    for acronym in re.findall(r"\b([A-Z][A-Za-z0-9.\-]{2,})\s*\((?:PMID|NCT)", source):
        identities.add(acronym)
    return identities


def parity_conflicts(
    parity_row: dict[str, Any] | None,
    outcome: dict[str, Any],
    membership: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not parity_row:
        return []
    text = str(parity_row.get("reason") or "")
    if not text:
        return []
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    m = membership or outcome_membership(outcome)
    pooled_canon = {canonical_trial_key(k) for k in m.get("pooled", []) or []}
    conflicts = []
    for trial in outcome.get("trials", []) or []:
        key = trial_key(trial)
        if canonical_trial_key(key) not in pooled_canon:
            continue
        identities = {i for i in _trial_identities(trial) if len(str(i)) >= 3}
        for sentence in sentences:
            if not _NEGATIVE_PARITY_RE.search(sentence):
                continue
            if any(re.search(rf"\b{re.escape(str(identity))}\b", sentence, re.I) for identity in identities):
                conflicts.append({
                    "trial_key": key,
                    "label": trial.get("label"),
                    "sentence": sentence,
                })
                break
    return conflicts


def annotate_parity(parity_row: dict[str, Any] | None, review: dict[str, Any]) -> dict[str, Any] | None:
    if not parity_row:
        return None
    row = copy.deepcopy(parity_row)
    primary = next((o for o in review.get("outcomes", []) or [] if o.get("primary")), None)
    conflicts = parity_conflicts(row, primary or {}, outcome_membership(primary or {}, review) if primary else {})
    if conflicts:
        row["membership_status"] = "STALE_VS_MEMBERSHIP"
        row["membership_unrenderable"] = True
        row["membership_conflicts"] = conflicts
    return row


def consistency_violations(
    review: dict[str, Any],
    parity_row: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    primary = next((o for o in review.get("outcomes", []) or [] if o.get("primary")), None)
    if not primary:
        return []
    membership = outcome_membership(primary, review)
    pooled = membership.get("pooled") or []
    violations = []

    integrity = review.get("integrity") or {}
    integrity_pooled = pooled_membership_keys(review)
    if integrity and integrity.get("n_pooled") != len(integrity_pooled):
        violations.append({
            "code": "INTEGRITY_COUNT_MISMATCH",
            "detail": f"{integrity.get('n_pooled')} vs {len(integrity_pooled)}",
            "integrity_n_pooled": integrity.get("n_pooled"),
            "membership_pooled": len(integrity_pooled),
        })

    rob = (review.get("rob2") or {}).get("trials") or {}
    sensitivity = review.get("rob_sensitivity") or {}
    levels = sensitivity.get("levels") or {}
    if rob and levels:
        rated = [key for key in pooled if lookup_by_trial_key(rob, key) is not None]
        invisible = [key for key in rated if lookup_by_trial_key(levels, key) is None]
        if invisible:
            violations.append({
                "code": "ROB_JOIN_MISS",
                "detail": f"{len(invisible)} rated-and-pooled trials invisible to levels",
                "trial_keys": invisible,
            })

    row = parity_row if parity_row is not None else (review.get("reproduction") or {}).get("parity")
    if row and row.get("membership_status") != "STALE_VS_MEMBERSHIP":
        conflicts = parity_conflicts(row, primary, membership)
        if conflicts:
            violations.append({
                "code": "PARITY_TEXT_STALE",
                "detail": "names a pooled trial as refused/not pooled",
                "conflicts": conflicts,
            })
    return violations
