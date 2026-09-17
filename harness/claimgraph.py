"""Claim/dependency graph for result-bearing review objects.

The graph is deliberately small and object-derived: every check reads review.json
fields, never rendered prose, except where the stored object itself is hand
prose (parity/refusal registries). A violation means the object is stale or
contradictory with the current input set; callers either refuse the page or
replace the affected registry row with an unrenderable block.
"""
from __future__ import annotations

import copy
import glob
import hashlib
import json
import os
import re
from pathlib import Path
import html
import subprocess
from typing import Any


_ID_SPLIT = ("·", "Â·", "Ã‚Â·")
_PMID_RE = re.compile(r"\b(?:PMID[:\s]*)?(\d{7,9})\b", re.I)
_NCT_RE = re.compile(r"\bNCT\d{8}\b", re.I)


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(obj: Any) -> str:
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()


def _norm_id(value: Any) -> str:
    s = str(value or "").strip()
    for sep in _ID_SPLIT:
        if sep in s:
            s = s.split(sep)[-1].strip()
    s = s.replace("PMID ", "").replace("PMID:", "").strip()
    if _NCT_RE.fullmatch(s):
        return s.upper()
    return s.split()[-1].strip() if s.split() else s


def trial_key(trial_dict: dict[str, Any]) -> str:
    """The one trial identity used by graph consumers: the identifier in ``trial["id"]``.

    ``PMID 39555823`` becomes ``39555823``; ``NCT02422186`` remains an NCT. Labels
    are intentionally ignored for pooled trials because labels are allowed to be
    acronyms and are not stable join keys.
    """
    return _norm_id(trial_dict.get("id"))


def _keys_from_text(value: Any) -> set[str]:
    text = str(value or "")
    out = {m.group(1) for m in _PMID_RE.finditer(text)}
    out |= {m.group(0).upper() for m in _NCT_RE.finditer(text)}
    return {x for x in out if x}


def _keys_from_registry_row(row: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for key in ("id", "pmid", "nct", "trial", "verified", "not_pooled_because"):
        if key in row:
            out |= _keys_from_text(row.get(key))
    return out


def _trial_inputs(trial: dict[str, Any]) -> dict[str, Any]:
    scale = trial.get("scale") or trial.get("estimand")
    if trial.get("ai") is not None:
        return {k: trial.get(k) for k in ("ai", "ci", "n1i", "n2i")} | {"scale": scale}
    if trial.get("effect") is not None:
        return {k: trial.get(k) for k in ("effect", "ci_low", "ci_high")} | {"scale": scale}
    if trial.get("mean1") is not None:
        return {k: trial.get(k) for k in ("mean1", "sd1", "nc1", "mean2", "sd2", "nc2")} | {"scale": scale}
    if trial.get("e1i") is not None:
        return {k: trial.get(k) for k in ("e1i", "t1i", "e2i", "t2i")} | {"scale": scale}
    return {"scale": scale}


def input_set_version(outcome: dict[str, Any]) -> str:
    rows = []
    for trial in outcome.get("trials") or []:
        key = trial_key(trial)
        if key:
            rows.append([key, _trial_inputs(trial)])
    rows.sort(key=lambda row: row[0])
    return _sha(rows)


def _claim_id(kind: str, outcome_name: str | None, version: str) -> str:
    return hashlib.sha256(f"{kind}|{outcome_name or ''}|{version}".encode("utf-8")).hexdigest()[:16]


def _stamp(obj: dict[str, Any], kind: str, outcome_name: str | None, version: str) -> None:
    obj["input_set_version"] = version
    obj["claim_id"] = _claim_id(kind, outcome_name, version)
    obj["depends_on"] = {"input_set_version": version}
    obj["claim_kind"] = kind


def primary_outcome(review: dict[str, Any]) -> dict[str, Any] | None:
    outs = review.get("outcomes") or []
    return next((o for o in outs if o.get("primary")), (outs[0] if outs else None))


def outcome_versions(review: dict[str, Any]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for outcome in review.get("outcomes") or []:
        name = str(outcome.get("name") or "")
        versions[name] = input_set_version(outcome)
    return versions


def strand_member_keys(strands_doc: dict[str, Any] | None) -> set[str]:
    out: set[str] = set()
    for strand in (strands_doc or {}).get("strands") or []:
        for member in strand.get("members") or []:
            if member.get("pmid"):
                out.add(str(member.get("pmid")).strip())
            elif member.get("nct"):
                out.add(str(member.get("nct")).strip().upper())
            else:
                out |= _keys_from_text(member.get("source"))
    return {x for x in out if x}


def _strand_version(strand: dict[str, Any]) -> str:
    rows = []
    for member in strand.get("members") or []:
        key = str(member.get("pmid") or member.get("nct") or "").strip()
        if key:
            rows.append([key, {k: member.get(k) for k in ("effect", "ci_low", "ci_high", "scale", "crude_rr", "counts")}])
    rows.sort(key=lambda row: row[0])
    return _sha(rows)


def attach_strands(review: dict[str, Any], root: str) -> None:
    """Attach the committed strands doc early enough that membership checks see it.

    A trial pooled in a declared strand is not a target-result-absent trial. Removing
    those absent rows fixes the stale "not pooled in any outcome" state without
    changing any strand number.
    """
    slug = review.get("slug")
    for path in glob.glob(os.path.join(root, "docs", "*_strands.json")):
        try:
            doc = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if doc.get("slug") != slug:
            continue
        review["strands"] = doc
        by_key = _strand_names_by_member(doc)
        if by_key:
            # The row is NOT dropped: on this outcome the trial is still unpooled (its effect is a
            # different estimand class), and a reader must see both facts -- absent here, pooled in
            # strand X. Dropping it made AFFIRM-AHF vanish from the primary's table (integration
            # 2026-09-16); annotating keeps the absence typed and the membership consistent.
            for outcome in review.get("outcomes") or []:
                for row in outcome.get("declared_absent_trials") or []:
                    strands = by_key.get(trial_key(row))
                    if strands:
                        row["absent_kind"] = "pooled_in_strand"
                        row["pooled_in_strands"] = strands
                        row["state_basis"] = ((row.get("state_basis") or "") +
                                              f" | not pooled on this outcome; pooled in declared strand(s) "
                                              f"{', '.join(strands)}").strip(" |")
        break


def _strand_names_by_member(strands_doc: dict[str, Any] | None) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for strand in (strands_doc or {}).get("strands") or []:
        if not isinstance(strand, dict):
            continue
        # k=1 strands carry pool=None but their member IS accounted for by the strand.
        name = str(strand.get("strand") or strand.get("name") or "?")
        for member in strand.get("members") or []:
            for key in _keys_from_registry_row(member) if isinstance(member, dict) else set():
                out.setdefault(key, []).append(name)
    return out


def stamp_review(review: dict[str, Any]) -> dict[str, Any]:
    versions = outcome_versions(review)
    for outcome in review.get("outcomes") or []:
        name = str(outcome.get("name") or "")
        version = versions.get(name) or input_set_version(outcome)
        result = outcome.get("result")
        if isinstance(result, dict):
            result["input_set_version"] = version
            _stamp(result, "outcome_result", name, version)
        design_consumption = outcome.get("design_consumption")
        if isinstance(design_consumption, dict):
            _stamp(design_consumption, "design_consumption", name, version)
            review.setdefault("claimgraph", {}).setdefault("objects", []).append({
                "kind": "design_consumption",
                "claim_id": design_consumption.get("claim_id"),
                "depends_on": design_consumption.get("depends_on"),
                "outcome": name,
            })
        for row in outcome.get("declared_absent_trials") or []:
            _stamp(row, "membership_state", name, version)

    primary = primary_outcome(review)
    primary_name = (primary or {}).get("name")
    primary_version = versions.get(str(primary_name or "")) or ""
    sens = review.get("rob_sensitivity") or {}
    for kind in ("full", "drop_high", "low_only"):
        point = sens.get(kind)
        if isinstance(point, dict) and primary_version:
            _stamp(point, f"rob_sensitivity.{kind}", primary_name, primary_version)
    if sens.get("full") and primary_version:
        review.setdefault("claimgraph", {}).setdefault("objects", []).append({
            "kind": "rob_sensitivity_prose",
            "claim_id": _claim_id("rob_sensitivity_prose", primary_name, primary_version),
            "depends_on": {"input_set_version": primary_version},
        })

    strands_doc = review.get("strands") or {}
    for strand in strands_doc.get("strands") or []:
        version = _strand_version(strand)
        strand["input_set_version"] = version
        _stamp(strand, "strand_pool", strand.get("name"), version)
        if isinstance(strand.get("pool"), dict):
            _stamp(strand["pool"], "strand_pool.result", strand.get("name"), version)

    grade = review.get("grade")
    if isinstance(grade, dict) and primary_version:
        _stamp(grade, "grade", primary_name, primary_version)
    if primary_version:
        review.setdefault("claimgraph", {}).setdefault("objects", []).append({
            "kind": "manuscript_result_sentence",
            "claim_id": _claim_id("manuscript_result_sentence", primary_name, primary_version),
            "depends_on": {"input_set_version": primary_version},
        })
    return review


def _violation(code: str, kind: str, claim_id: str, detail: str, **extra: Any) -> dict[str, Any]:
    return {"code": code, "kind": kind, "claim_id": claim_id, "detail": detail, **extra}


def _rob_join_miss(review: dict[str, Any]) -> list[dict[str, Any]]:
    primary = primary_outcome(review)
    if not primary:
        return []
    rob = (review.get("rob2") or {}).get("trials") or {}
    sens = review.get("rob_sensitivity") or {}
    if not sens.get("levels"):
        return []
    levels = sens.get("levels") or {}
    version = input_set_version(primary)
    out = []
    for trial in primary.get("trials") or []:
        key = trial_key(trial)
        if key in rob and not levels.get(key):
            out.append(_violation(
                "ROB_JOIN_MISS",
                "rob_sensitivity",
                _claim_id("rob_sensitivity", primary.get("name"), version),
                f"pooled trial {key} is rated in rob2 but absent from sensitivity levels",
                outcome=primary.get("name"),
                trial_key=key,
            ))
    return out


_DISPUTE_REQUIRED = ("pooled_trial_keys", "decision_owed_to", "signed_by", "date", "reason")


def _dispute_covers(row: dict[str, Any], hit: list[str]) -> bool:
    d = row.get("disputed")
    if not isinstance(d, dict) or any(not d.get(k) for k in _DISPUTE_REQUIRED):
        return False
    return set(hit) <= {_norm_id(k) for k in d.get("pooled_trial_keys") or []}


def disputes(review: dict[str, Any], registries: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Refusal rows that name a pooled trial under a signed dispute: rendered, counted, never silent."""
    registries = registries or {}
    refusals = registries.get("refusals")
    if refusals is None:
        refusals = (review.get("reproduction") or {}).get("refusals") or []
    elif isinstance(refusals, dict):
        refusals = refusals.get(review.get("slug"), [])
    primary = primary_outcome(review)
    pooled = {trial_key(t) for t in (primary or {}).get("trials") or [] if trial_key(t)}
    out = []
    for row in refusals or []:
        hit = sorted(_keys_from_registry_row(row) & pooled)
        if hit and _dispute_covers(row, hit):
            out.append({"code": "POOL_SCOPE_DISPUTE", "trial_keys": hit, "trial": row.get("trial"),
                        "not_pooled_because": row.get("not_pooled_because"), **row["disputed"]})
    return out


def _refused_and_pooled(review: dict[str, Any], registries: dict[str, Any] | None) -> list[dict[str, Any]]:
    registries = registries or {}
    refusals = registries.get("refusals")
    if refusals is None:
        refusals = (review.get("reproduction") or {}).get("refusals") or []
    elif isinstance(refusals, dict):
        refusals = refusals.get(review.get("slug"), [])
    primary = primary_outcome(review)
    pooled = {
        trial_key(trial)
        for trial in (primary or {}).get("trials") or []
        if trial_key(trial)
    }
    version = input_set_version(primary or {})
    out = []
    for row in refusals or []:
        if row.get("unrenderable"):
            continue
        keys = _keys_from_registry_row(row)
        hit = sorted(keys & pooled)
        if hit and _dispute_covers(row, hit):
            # Both policies are declared at once ON PURPOSE and signed: the refusal stays visible as
            # a dispute object (see disputes()), the pool is untouched, and the decision is owed to a
            # named person. An unsigned or partial dispute does not clear the violation.
            continue
        if hit:
            out.append(_violation(
                "REFUSED_AND_POOLED",
                "refusal",
                row.get("claim_id") or _claim_id("refusal", (primary or {}).get("name"), version),
                f"refusal row names pooled trial(s): {', '.join(hit)}",
                trial_keys=hit,
            ))
    return out


def _claim_scope_counts(review: dict[str, Any]) -> dict[str, int]:
    cc = (review.get("reproduction") or {}).get("claim_check") or {}
    return cc.get("scope_counts") or {}


def _strand_violations(review: dict[str, Any]) -> list[dict[str, Any]]:
    strands_doc = review.get("strands") or {}
    strands = [s for s in strands_doc.get("strands") or [] if s.get("pool") or (s.get("k") or 0) >= 1]
    if not strands:
        return []
    primary = primary_outcome(review)
    version = input_set_version(primary or {})
    out = []
    rep = review.get("reproduction") or {}
    if rep:
        counted = _claim_scope_counts(review).get("strand_pool", 0)
        if counted < len(strands):
            out.append(_violation(
                "STRAND_OUTSIDE_CLAIMS",
                "strand_pool",
                _claim_id("strand_pool", (primary or {}).get("name"), version),
                f"{len(strands)} strand result(s) exist but only {counted} are counted in claim scope",
            ))
    pooled = strand_member_keys(strands_doc)
    for reason in (review.get("invalidation") or {}).get("reasons") or []:
        detail = str(reason.get("detail") or "")
        if "not pooled in any outcome" in detail and any(key in detail for key in pooled):
            out.append(_violation(
                "STRAND_OUTSIDE_CLAIMS",
                "membership_state",
                _claim_id("strand_membership", (primary or {}).get("name"), version),
                "a strand member is still reported as not pooled in any outcome",
            ))
            break
    return out


def _membership_conflicts(review: dict[str, Any]) -> list[dict[str, Any]]:
    pooled = strand_member_keys(review.get("strands") or {})
    if not pooled:
        return []
    out = []
    # Strands decompose the PRIMARY outcome; a trial pooled in an HF-hospitalisation strand is
    # legitimately absent for a harms outcome, so only the primary is checked (integration 2026-09-16).
    for outcome in review.get("outcomes") or []:
        if not outcome.get("primary"):
            continue
        version = input_set_version(outcome)
        # An absent row that is typed pooled_in_strand is the consistent statement of both facts;
        # only an UN-annotated row that a strand pools is a conflict.
        absent = {trial_key(row) for row in outcome.get("declared_absent_trials") or []
                  if row.get("absent_kind") != "pooled_in_strand"}
        hit = sorted(pooled & absent)
        if hit:
            out.append(_violation(
                "MEMBERSHIP_CONFLICT",
                "membership_state",
                _claim_id("membership_state", outcome.get("name"), version),
                f"trial(s) both declared absent and pooled in a strand: {', '.join(hit)}",
                outcome=outcome.get("name"),
                trial_keys=hit,
            ))
    return out


def _rob_prose_false(review: dict[str, Any]) -> list[dict[str, Any]]:
    sens = review.get("rob_sensitivity") or {}
    full, low = sens.get("full") or {}, sens.get("low_only") or {}
    if not (full and low):
        return []
    stated = sens.get("low_only_relation")
    if stated is not None:
        # Post-FP objects carry the relation; a consumer may trust it only if it re-derives.
        from . import rob_sensitivity as _rs
        if stated == _rs.low_only_relation(full, low):
            return []
        primary = primary_outcome(review)
        version = input_set_version(primary or {})
        return [_violation(
            "PROSE_PREDICATE_FALSE",
            "rob_sensitivity_prose",
            _claim_id("rob_sensitivity_prose", (primary or {}).get("name"), version),
            f"stated low_only_relation {stated!r} does not re-derive from the stored pools",
        )]
    if full.get("k") == low.get("k") and sens.get("low_only_informative") is False:
        primary = primary_outcome(review)
        version = input_set_version(primary or {})
        return [_violation(
            "PROSE_PREDICATE_FALSE",
            "rob_sensitivity_prose",
            _claim_id("rob_sensitivity_prose", (primary or {}).get("name"), version),
            "renderer predicate says fewer trials when low-only k equals the full pool k",
        )]
    return []


def _parity_named_count(reason: str) -> int | None:
    text = str(reason or "")
    m = re.search(r"(\d+)\s+valid\s+RCT\b.*?=\s*ours?\b", text, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"([A-Z][A-Za-z0-9.\-]*(?:\s*\+\s*[A-Z][A-Za-z0-9.\-]*)+)\s*=\s*our pool\b", text)
    if m:
        return len([x for x in re.split(r"\s*\+\s*", m.group(1)) if x.strip()])
    return None


def parity_violation(review: dict[str, Any], parity: dict[str, Any] | None = None) -> dict[str, Any] | None:
    parity = parity or (review.get("reproduction") or {}).get("parity") or {}
    if not parity or parity.get("unrenderable"):
        return None
    named_count = _parity_named_count(str(parity.get("reason") or ""))
    primary = primary_outcome(review)
    if named_count is None or not primary:
        return None
    current_k = len(primary.get("trials") or [])
    if named_count != current_k:
        version = input_set_version(primary)
        return _violation(
            "PROSE_PREDICATE_FALSE",
            "parity",
            parity.get("claim_id") or _claim_id("parity", primary.get("name"), version),
            f"parity prose names {named_count} trial(s) as ours, but current primary trial set has {current_k}",
        )
    return None


def _prose_predicate_false(review: dict[str, Any]) -> list[dict[str, Any]]:
    out = _rob_prose_false(review)
    pv = parity_violation(review)
    if pv:
        out.append(pv)
    return out


def _scan_dependents(review: dict[str, Any]) -> list[dict[str, Any]]:
    versions = outcome_versions(review)
    primary = primary_outcome(review)
    primary_version = input_set_version(primary or {}) if primary else ""
    out = []

    def current_for(obj: dict[str, Any], inherited_outcome: str | None) -> str | None:
        if obj.get("input_set_version"):
            return str(obj.get("input_set_version"))
        outcome = obj.get("outcome") or inherited_outcome
        if outcome and outcome in versions:
            return versions[outcome]
        return primary_version or None

    def walk(obj: Any, path: str, inherited_outcome: str | None = None) -> None:
        if isinstance(obj, dict):
            dep = obj.get("depends_on") or {}
            recorded = dep.get("input_set_version")
            current = current_for(obj, inherited_outcome)
            if recorded and current and recorded != current and not obj.get("unrenderable"):
                out.append(_violation(
                    "STALE_DEPENDENT",
                    str(obj.get("claim_kind") or obj.get("kind") or "dependent"),
                    str(obj.get("claim_id") or _claim_id("dependent", inherited_outcome, current)),
                    f"{path} depends on {recorded}, current input_set_version is {current}",
                    object_path=path,
                ))
            next_outcome = inherited_outcome
            if path.startswith("/outcomes/") and obj.get("name"):
                next_outcome = str(obj.get("name"))
            for key, value in obj.items():
                if key in {"protocol", "search", "screening", "limitations"}:
                    continue
                walk(value, f"{path}/{key}", next_outcome)
        elif isinstance(obj, list):
            for idx, value in enumerate(obj):
                walk(value, f"{path}/{idx}", inherited_outcome)

    walk(review, "")
    return out


def scope_counts(review: dict[str, Any], outcome_claims_checked: int) -> dict[str, int]:
    strand_count = sum(
        1 for strand in (review.get("strands") or {}).get("strands") or []
        if strand.get("pool") or (strand.get("k") or 0) >= 1
    )
    return {
        "outcome_result": int(outcome_claims_checked),
        "strand_pool": strand_count,
        "rob_sensitivity": sum(1 for k in ("full", "drop_high", "low_only")
                               if isinstance((review.get("rob_sensitivity") or {}).get(k), dict)),
        "grade": 1 if review.get("grade") else 0,
    }


def scope_summary(scope: dict[str, Any]) -> str:
    counts = scope.get("counts") or {}
    checked = ", ".join(f"{kind}={counts[kind]}" for kind in sorted(counts)) or "none"
    surfaces = len(scope.get("surfaces_checked") or [])
    not_scope = ", ".join(scope.get("not_in_scope") or []) or "none"
    return f"{checked}; surfaces checked={surfaces}; not in scope: {not_scope}"


def unrenderable_object(code: str, kind: str, claim_id: str, detail: str = "") -> dict[str, Any]:
    return {
        "unrenderable": True,
        "violation_code": code,
        "kind": kind,
        "claim_id": claim_id,
        **({"detail": detail} if detail else {}),
    }


def prepare_reproduction(review_core: dict[str, Any], reproduction: dict[str, Any]) -> dict[str, Any]:
    """Stamp hand-registry reproduction rows and blank stale parity rows before rendering."""
    primary = primary_outcome(review_core)
    version = input_set_version(primary or {}) if primary else _sha([])
    reproduction = copy.deepcopy(reproduction)
    if isinstance(reproduction.get("parity"), dict):
        parity = reproduction["parity"]
        _stamp(parity, "parity", (primary or {}).get("name"), version)
        pv = parity_violation({**review_core, "reproduction": {"parity": parity}}, parity)
        if pv:
            reproduction["parity"] = unrenderable_object(
                pv["code"], "parity", pv["claim_id"], "stale parity prose is not rendered"
            )
    if isinstance(reproduction.get("refusals"), list):
        for row in reproduction["refusals"]:
            if isinstance(row, dict):
                _stamp(row, "refusal", (primary or {}).get("name"), version)
    return reproduction


def check(review: dict[str, Any], registries: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    violations.extend(_rob_join_miss(review))
    violations.extend(_refused_and_pooled(review, registries))
    violations.extend(_strand_violations(review))
    violations.extend(_membership_conflicts(review))
    violations.extend(_prose_predicate_false(review))
    violations.extend(_scan_dependents(review))
    return violations


# Typed provenance extends the existing graph; it does not replace its version,
# membership, predicate or signed-dispute checks.
OBJECT_CLASSES = ("FACT", "TRANSFORMATION", "JUDGEMENT", "INTERPRETATION")
ROOT = Path(__file__).resolve().parents[1]


def locate_span(text: str, quoted: str) -> str | None:
    """Locate a whitespace-normalized quote and return the EXACT original slice.

    PDF line wrapping is not silently removed from the provenance edge. The
    returned value, including line breaks, must pass literal substring checking.
    No punctuation, case, digits or words are normalized.
    """
    if not quoted or not quoted.strip():
        return None
    match = re.search(r"\s+".join(re.escape(w) for w in quoted.split()), text)
    return match.group(0) if match else None


def _held_path(root: Path, value: Any, *, document: bool = False) -> Path:
    rel = Path(str(value or ""))
    if not value or rel.is_absolute():
        raise ValueError("provenance paths must be repository-relative")
    path = (root / rel).resolve()
    path.relative_to(root.resolve())
    if document:
        parts = path.relative_to(root.resolve()).parts
        allowed = (len(parts) >= 4 and parts[0] == "cache" and parts[2] == "held")
        allowed |= parts[:4] == ("outputs", "handover", "glp1_regulatory", "held")
        # Already committed primary publications are held documents too.
        allowed |= (len(parts) == 3 and parts[0] == "cache" and
                    (parts[2] == "records.json" or
                     (parts[2].startswith("ft_") and parts[2].endswith(".txt"))))
        allowed |= (parts[:6] == ("outputs", "search_v2", "lanes", "R3", "lane_r3", "raw")
                    and parts[-1].endswith("-efetch.xml"))
        if not allowed:
            raise ValueError("document is not under an allowed held directory")
    return path


def _committed(root: Path, path: Path) -> bool:
    """A matching local digest alone cannot establish committed provenance."""
    rel = path.relative_to(root.resolve()).as_posix()
    result = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{rel}"],
                            capture_output=True)
    return result.returncode == 0 and result.stdout == path.read_bytes()


def verify_fact(row: dict[str, Any], root: Path | str = ROOT) -> dict[str, Any]:
    """Fail closed on absent, altered, uncommitted or unlocated evidence."""
    root = Path(root).resolve()
    evidence = _fact_evidence(row)
    try:
        digest = evidence.get("document_sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("missing full document_sha256")
        retrieved = evidence.get("retrieved_utc")
        from datetime import datetime
        if not isinstance(retrieved, str) or not retrieved.endswith("Z"):
            raise ValueError("missing retrieved_utc in UTC")
        datetime.fromisoformat(retrieved.replace("Z", "+00:00"))
        document = _held_path(root, evidence.get("document_path"), document=True)
        if hashlib.sha256(document.read_bytes()).hexdigest() != digest:
            raise ValueError("held document digest mismatch")
        extracted = _held_path(root, evidence.get("extracted_text"))
        raw = extracted.read_bytes()
        if hashlib.sha256(raw).hexdigest() != evidence.get("extracted_text_sha256"):
            raise ValueError("extracted text digest mismatch")
        span = evidence.get("span")
        if not isinstance(span, str) or not span.strip() or span not in raw.decode("utf-8"):
            raise ValueError("span is not located verbatim in extracted text")
        if not _committed(root, document) or not _committed(root, extracted):
            raise ValueError("held document or extraction differs from committed bytes")
        # Verify the displayed effect and bounds are in this span, not merely in
        # some unrelated sentence elsewhere in the held document.
        numeric_span = re.sub(r"(?<=\d)[·‧∙](?=\d)", ".", span)
        numbers = {float(n) for n in re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?(?!\w|\.\d)", numeric_span)}
        for field in ("effect", "ci_low", "ci_high", "ai", "ci", "n1i", "n2i", "e1i", "e2i", "t1i", "t2i", "mean1", "mean2", "sd1", "sd2", "nc1", "nc2"):
            value = row.get(field)
            if isinstance(value, (float, int)) and not isinstance(value, bool) and float(value) not in numbers:
                raise ValueError(f"{field}={value} is not in located span")
        return {"verified": True, "class": "FACT", "document_sha256": digest,
                "retrieved_utc": retrieved, "span": span}
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        return {"verified": False, "class": "UNVERIFIED_FACT", "reason": str(exc)}


def regulatory_fact(source: dict[str, Any], decision: dict[str, Any], root=ROOT) -> dict[str, Any]:
    """Adapt the held source record, retaining exact PDF-extraction whitespace."""
    held = source.get("held") or {}
    text = _held_path(Path(root), held.get("extracted_text")).read_bytes().decode("utf-8")
    effect = decision.get("effect") or {}
    return {"id": decision.get("trial_key"), "effect": effect.get("estimate"),
            "ci_low": effect.get("ci_low"), "ci_high": effect.get("ci_high"),
            "scale": effect.get("scale"), "source": decision.get("span"),
            "provenance": {"document_sha256": source.get("document_sha256"),
                "retrieved_utc": source.get("fetched_utc"),
                "document_path": held.get("held_in_tree"),
                "extracted_text": held.get("extracted_text"),
                "extracted_text_sha256": source.get("extracted_text_sha256"),
                "span": locate_span(text, decision.get("span") or "")}}


class ClaimGraph:
    """Four typed objects with explicit dependency edges and fail-closed rendering."""

    def __init__(self, root=ROOT):
        self.root = Path(root)
        self.objects: dict[str, dict[str, Any]] = {}
        self.invalidated: set[str] = set()

    def add(self, claim_id: str, object_class: str, **fields) -> str:
        if object_class not in OBJECT_CLASSES:
            raise ValueError(f"unknown object class {object_class}")
        if claim_id in self.objects:
            raise ValueError(f"duplicate claim id {claim_id}")
        self.objects[claim_id] = {"claim_id": claim_id, "class": object_class, **fields}
        return claim_id

    def invalidate(self, changed_document_sha: str) -> list[str]:
        affected = {cid for cid, obj in self.objects.items()
                    if _fact_evidence(obj.get("row", {})).get(
                        "document_sha256") == changed_document_sha}
        while True:
            next_set = affected | {cid for cid, obj in self.objects.items()
                                   if set(obj.get("depends_on") or []) & affected}
            if next_set == affected:
                break
            affected = next_set
        self.invalidated.update(affected)
        return sorted(affected)

    def check(self) -> list[dict[str, Any]]:
        violations = []
        def cyclic(start, node, seen):
            for dep in self.objects.get(node, {}).get("depends_on") or []:
                if dep == start or (dep not in seen and cyclic(start, dep, seen | {dep})):
                    return True
            return False
        for cid, obj in self.objects.items():
            code, detail = None, ""
            if cid in self.invalidated:
                code = "STALE_DEPENDENT"
            elif obj["class"] == "FACT":
                verified = verify_fact(obj.get("row") or {}, self.root)
                if not verified["verified"]:
                    code, detail = "UNVERIFIED_FACT", verified["reason"]
            elif obj["class"] == "TRANSFORMATION":
                try:
                    actual = self.recompute(cid)
                    if actual != obj.get("value"):
                        code = "TRANSFORMATION_MISMATCH"
                except (ValueError, KeyError, TypeError, ZeroDivisionError, RecursionError):
                    code = "UNRECOMPUTABLE_TRANSFORMATION"
            elif obj["class"] == "JUDGEMENT":
                basis = obj.get("basis")
                adjudication = obj.get("adjudication")
                if not basis:
                    code = "JUDGEMENT_WITHOUT_BASIS"
                elif adjudication not in ("RULE", "MODEL_SPAN_VERIFIED", "OWED", "HUMAN"):
                    code = "INVALID_ADJUDICATION"
                elif adjudication == "HUMAN" and not (obj.get("who") and obj.get("date")):
                    code = "INVALID_ADJUDICATION"
                elif adjudication == "RULE" and not (isinstance(basis, dict) and basis.get("rule_id")):
                    code = "INVALID_ADJUDICATION"
                elif adjudication == "MODEL_SPAN_VERIFIED" and not all(
                        obj.get(k) for k in ("prompt_hash", "model_pin", "cached_response_sha", "span")):
                    code = "INVALID_ADJUDICATION"
            elif obj["class"] == "INTERPRETATION":
                alternatives = obj.get("alternatives") or []
                if not any(str(a).strip() and a != obj.get("text") for a in alternatives):
                    code = "INTERPRETATION_WITHOUT_ALTERNATIVE"
            if any(dep not in self.objects for dep in obj.get("depends_on") or []):
                code = "MISSING_DEPENDENCY"
            if cyclic(cid, cid, {cid}):
                code = "CYCLIC_DEPENDENCY"
            if code:
                violations.append(_violation(code, obj["class"], cid, detail))
        return violations

    def recompute(self, claim_id):
        import math
        obj = self.objects[claim_id]
        operation = obj.get("operation")
        inputs = obj.get("inputs")
        if operation == "fact_coverage":
            refs = obj.get("input_refs") or []
            if set(refs) != set(obj.get("depends_on") or []):
                raise ValueError("coverage dependency mismatch")
            states = [verify_fact(self.objects[ref]["row"], self.root)["class"] for ref in refs]
            return {"FACT": states.count("FACT"), "UNVERIFIED_FACT": states.count("UNVERIFIED_FACT"), "total": len(states)}
        if operation == "count":
            return len(inputs)
        if operation == "sum":
            return sum(inputs)
        if operation == "log":
            return math.log(inputs)
        if operation == "state_counts":
            return {state: inputs.count(state) for state in sorted(set(inputs))}
        if operation == "certainty":
            domains = inputs["domains"]
            if any(d.get("assessed") is not True for d in domains):
                return "provisional"
            return ("very low", "low", "moderate", "high")[max(0, inputs["start"] - sum(
                d["downgrades"] for d in domains))]
        raise ValueError(f"unsupported transformation {operation}")

    def render(self, claim_id: str) -> str:
        if claim_id not in self.objects:
            raise ValueError(f"SENTENCE_WITHOUT_OBJECT: {claim_id}")
        obj = self.objects[claim_id]
        violations = {v["claim_id"]: v for v in self.check()}
        mark = obj["class"]
        if claim_id in violations:
            code = violations[claim_id]["code"]
            mark = "UNVERIFIED_FACT" if code == "UNVERIFIED_FACT" else "UNRENDERABLE"
        text = obj.get("text", "")
        if obj["class"] == "FACT":
            row = obj.get("row") or {}
            if row.get("effect") is not None:
                text = f"{row.get('id', claim_id)}: {row.get('scale', '')} {row.get('effect')} ({row.get('ci_low')}, {row.get('ci_high')})."
            else:
                values = {k: row[k] for k in ("ai", "n1i", "ci", "n2i", "e1i", "t1i", "e2i", "t2i", "mean1", "sd1", "nc1", "mean2", "sd2", "nc2") if k in row}
                text = f"{row.get('id', claim_id)}: {_canonical(values)}."
        if mark == "UNRENDERABLE":
            text = violations[claim_id]["code"]
        elif obj["class"] == "TRANSFORMATION":
            value = self.recompute(claim_id)
            if obj.get("operation") == "fact_coverage":
                text = f"Source provenance: {value['FACT']} FACT of {value['total']} trial-outcome rows; {value['UNVERIFIED_FACT']} UNVERIFIED_FACT of {value['total']}."
            else:
                text = f"{obj.get('label', claim_id)}: {value}."
        elif obj["class"] == "INTERPRETATION":
            text += " Alternative: " + " Alternative: ".join(obj.get("alternatives") or [])
        elif obj["class"] == "JUDGEMENT":
            text = f"{text} [adjudication: {obj.get('adjudication')}]"
        return (f'<span data-claim-id="{html.escape(claim_id, quote=True)}" '
                f'data-claim-class="{mark}"><strong>[{mark}]</strong> {html.escape(str(text))}</span>')


def fact_render(row: dict[str, Any], root=ROOT) -> str:
    graph = ClaimGraph(root)
    cid = graph.add("fact-" + _sha(row)[:16], "FACT", row=row)
    return graph.render(cid)


def _fact_evidence(row):
    return row.get("provenance") if isinstance(row.get("provenance"), dict) else row


def certainty_object(grade: dict[str, Any]) -> dict[str, Any]:
    names = ("risk_of_bias", "inconsistency", "imprecision", "indirectness", "publication_bias")
    domains = grade.get("domains") or {}
    inputs = {"start": ("very low", "low", "moderate", "high").index(grade.get("start", "high")),
              "domains": [{"assessed": domains.get(name, {}).get("assessed") is True,
                           "downgrades": domains.get(name, {}).get("downgrade", 0)} for name in names]}
    if any(not d["assessed"] for d in inputs["domains"]):
        value = "provisional"
    else:
        value = ("very low", "low", "moderate", "high")[max(0, inputs["start"] - sum(d["downgrades"] for d in inputs["domains"]))]
    return {"operation": "certainty", "inputs": inputs, "value": value, "label": "GRADE certainty"}


def certainty_render(review):
    graph = ClaimGraph()
    cid = graph.add("grade-certainty", "TRANSFORMATION", **certainty_object(review.get("grade") or {}))
    return graph.render(cid)


def certainty_violations(review):
    grade = review.get("grade") or {}
    if not grade or grade.get("certainty") == "not_rateable":
        return []
    try:
        obj = certainty_object(grade)
        expected = obj["value"]
        total = sum(d["downgrades"] for d in obj["inputs"]["domains"])
        if any(not isinstance(d["downgrades"], int) or isinstance(d["downgrades"], bool) or not 0 <= d["downgrades"] <= 3 for d in obj["inputs"]["domains"]):
            raise ValueError("invalid downgrade")
    except (ValueError, TypeError, IndexError):
        return [_violation("CERTAINTY_ARITHMETIC_MISMATCH", "TRANSFORMATION", "grade-certainty", "invalid GRADE inputs")]
    if grade.get("certainty", "").replace("_", " ") != expected or grade.get("downgrades") != total:
        return [_violation("CERTAINTY_ARITHMETIC_MISMATCH", "TRANSFORMATION", "grade-certainty",
                           f"stored {grade.get('certainty')} / {grade.get('downgrades')} downgrades; expected {expected} / {total}")]
    return []


def review_graph(review, root=ROOT):
    """Registry of migrated objects. Unmigrated prose remains scan debt."""
    graph = ClaimGraph(root)
    refs = []
    for outcome in review.get("outcomes") or []:
        state_id, state_obj = membership_object(outcome)
        if state_id not in graph.objects:
            graph.add(state_id, "TRANSFORMATION", **state_obj)
        for trial in outcome.get("trials") or []:
            row = dict(trial, scale=trial.get("scale") or outcome.get("estimand"))
            cid = "fact-" + _sha(row)[:16]
            if cid not in graph.objects:
                graph.add(cid, "FACT", row=row)
            refs.append(cid)
    graph.add("fact-coverage", "TRANSFORMATION", operation="fact_coverage", input_refs=refs,
              depends_on=sorted(set(refs)), value=None)
    graph.objects['fact-coverage']['value'] = graph.recompute('fact-coverage')
    if review.get("grade"):
        graph.add("grade-certainty", "TRANSFORMATION", **certainty_object(review["grade"]))
    for obj in (review.get("claimgraph") or {}).get("typed_objects") or []:
        fields = {k: v for k, v in obj.items() if k not in ("claim_id", "class")}
        graph.add(obj["claim_id"], obj["class"], **fields)
    return graph


def provenance_summary(review, root=ROOT):
    return review_graph(review, root).render('fact-coverage')


def membership_object(outcome):
    rows = outcome.get("declared_absent_trials") or []
    states = [row.get("state") or row.get("reason_code") or "UNCLASSIFIED" for row in rows]
    values = {state: states.count(state) for state in sorted(set(states))}
    cid = "membership-states-" + _sha({"outcome": outcome.get("name"), "rows": rows})[:16]
    return cid, {"operation": "state_counts", "inputs": states, "value": values,
                 "label": "Unpooled per-item states"}


def membership_summary(outcome):
    graph = ClaimGraph()
    cid, obj = membership_object(outcome)
    graph.add(cid, "TRANSFORMATION", **obj)
    return graph.render(cid)


def legacy_scope_violations(review, rendered):
    """Detect the old blanket absent count against per-item states, without
    treating extraction debt or unavailable sources as demonstrated absence."""
    plain = html.unescape(re.sub(r"<[^>]*>", " ", rendered))
    plain = " ".join(plain.split())
    primary = primary_outcome(review) or {}
    rows = primary.get("declared_absent_trials") or []
    # Family/report counting is intentionally not conflated: the old sentence
    # names families. A family's state is absent only when all its item states
    # demonstrate absence.
    families = {}
    for row in rows:
        key = row.get("trial_family_id") or row.get("id")
        families.setdefault(key, []).append(row.get("state") or row.get("reason_code"))
    actual = sum(all(s == "OUTCOME_NOT_IN_SOURCE" for s in states) for states in families.values())
    violations = []
    for match in re.finditer(r"\b(\d+) trial families were declared absent", plain):
        if int(match.group(1)) != actual:
            violations.append(_violation("PROSE_PREDICATE_FALSE", "TRANSFORMATION", membership_object(primary)[0],
                                         f"blanket absent sentence states {match.group(1)} families; per-item OUTCOME_NOT_IN_SOURCE families={actual}"))
    return violations


def scan_rendered(rendered: str, graph: ClaimGraph) -> dict[str, Any]:
    """Conservative visible-text scan, including table cells and short assertions.

    Text runs between block boundaries are audit units, not an NLP claim of an
    exact linguistic sentence count. All unregistered visible content is debt;
    script/style, navigation controls and headings alone are excluded.
    Marker ids AND text are checked against fresh graph rendering, so adding a
    real claim id around hand-authored text cannot launder the text.
    """
    from html.parser import HTMLParser

    class Scanner(HTMLParser):
        ignored = {"script", "style", "button", "nav", "title", "h1", "h2", "h3", "h4", "h5", "h6"}
        blocks = {"p", "div", "td", "th", "li", "section", "br", "tr", "figcaption", "header"}

        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.stack = []
            self.units = []
            self.buffer = []
            self.active = None
            self.claim_text = {}
            self.claim_marks = {}

        def flush(self):
            value = " ".join("".join(self.buffer).split())
            if value:
                self.units.append({"claim_id": self.active, "text": value})
            self.buffer = []

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            cid = attrs.get("data-claim-id")
            if tag in self.blocks or cid:
                self.flush()
            if tag not in {"br", "hr", "img", "input", "meta", "link", "wbr", "source"}:
                self.stack.append((tag, self.active))
            if cid:
                self.active = cid
                self.claim_marks[cid] = attrs.get("data-claim-class")

        def handle_endtag(self, tag):
            if self.stack:
                index = next((i for i in range(len(self.stack)-1, -1, -1) if self.stack[i][0] == tag), None)
                if index is not None:
                    previous = self.stack[index][1]
                    if previous != self.active or tag in self.blocks:
                        self.flush()
                    self.stack = self.stack[:index]
                    self.active = previous

        def handle_data(self, data):
            if not any(tag in self.ignored for tag, _ in self.stack):
                self.buffer.append(data)

    scanner = Scanner()
    scanner.feed(rendered)
    scanner.flush()
    violations = []
    matched = 0
    for unit in scanner.units:
        cid = unit["claim_id"]
        if cid not in graph.objects:
            violations.append(_violation("SENTENCE_WITHOUT_OBJECT", "unregistered", cid or "", unit["text"]))
            continue
        expected = Scanner()
        expected.feed(graph.render(cid))
        expected.flush()
        text = " ".join(u["text"] for u in expected.units)
        expected_mark = expected.claim_marks.get(cid)
        if unit["text"] != text or scanner.claim_marks.get(cid) != expected_mark:
            violations.append(_violation("RENDERING_MISMATCH", graph.objects[cid]["class"], cid, unit["text"]))
        else:
            matched += 1
    return {"rendered_units": len(scanner.units), "with_object": matched,
            "unit_contract": "conservative visible prose/table text runs; not an exact linguistic sentence count",
            "violations": violations}


def render(claim_id: str, graph: ClaimGraph) -> str:
    return graph.render(claim_id)
