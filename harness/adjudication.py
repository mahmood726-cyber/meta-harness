"""The adjudication object and the reference a served row carries to it.

An adjudication is a decision between located readings (two reviewers' rows, three interval renderings,
a timepoint choice) made under a registered rule. Before 2026-09-19 the decisions lived in lane handover
files (outputs/handover/*/ADJUDICATIONS.json) and a served row cited one by NAME only:
`{"id": "ADJ-GLP1-001", "state": "PROPOSED", "countersigned": false}` -- the state and the countersignature
were literals in the renderer, and the id was joined by NCT ("the last proposal for this trial"), not by
the decision that cited it. A citation by name is a container: edit the decision (adopt the other row),
delete it, or add a later proposal for the same trial, and the served citation's bytes do not change.

This module makes the citation a content reference:

  ADJUDICATION record (registry/adjudications.json, object ADJUDICATION_REGISTRY):
    every field of the decision as written (id, trial, nct, question, the competing readings, rule_applied,
    decision, why, consequence, held document digests ...), plus
      status            PROPOSED | COUNTERSIGNED | WITHDRAWN
      countersignature  null, or {"by", "date_utc", "record_sha256"}   (a statement ABOUT the record)
      sha256            content hash of the record with `sha256`, `countersignature` and `status` removed
                        (the decision's content; lifecycle fields are statements about it)
  ADJUDICATION_REF (what a served row carries):
      {"adjudication_id", "adjudication_sha256", "status", "countersigned"}
    built only by reference(record); never typed.

The hash excludes the lifecycle fields so that signing or withdrawing does not move the hash the citing
rows carry: a countersignature signs `record_sha256`, a row citing that hash is citing what was signed, and
a withdrawn record is refused by status, not by a hash that silently stopped matching.

A decision names its adjudication with a bare `adjudication_id` (the input); the served row beside it carries
the reference under the key `adjudication`. check(root) is the verify limb: every citation in a served object resolves to a registry record by id,
its hash equals the record's content hash, its status equals the record's status, and no citation names a
WITHDRAWN record or an id the registry does not hold. A legacy name-only citation is refused.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any

REGISTRY_PATH = "registry/adjudications.json"
STATUSES = ("PROPOSED", "COUNTERSIGNED", "WITHDRAWN")
ID_RE = re.compile(r"\bADJ-[A-Z0-9]+-\d{3,}\b")
EXCLUDED_FROM_HASH = ("sha256", "countersignature", "status")
SERVED_OBJECTS = ("docs/reviews/*/review.json", "docs/parity.json", "docs/refusals.json")


class AdjudicationError(ValueError):
    pass


def canonical_bytes(record: dict[str, Any]) -> bytes:
    body = {k: v for k, v in record.items() if k not in EXCLUDED_FROM_HASH}
    return json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def record_sha256(record: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(record)).hexdigest()


def seal(record: dict[str, Any]) -> dict[str, Any]:
    """Return the record with its status defaulted, countersignature explicit and sha256 computed."""
    out = dict(record)
    out.setdefault("status", "PROPOSED")
    out.setdefault("countersignature", None)
    if out["status"] not in STATUSES:
        raise AdjudicationError(f"{out.get('id')}: status {out['status']!r} not in {STATUSES}")
    out["sha256"] = record_sha256(out)
    return out


def validate(record: dict[str, Any]) -> list[str]:
    problems = []
    rid = record.get("id")
    if not isinstance(rid, str) or not ID_RE.fullmatch(rid):
        problems.append(f"record id {rid!r} is not an ADJ-<TOPIC>-<NNN> id")
    if record.get("status") not in STATUSES:
        problems.append(f"{rid}: status {record.get('status')!r} not in {STATUSES}")
    if record.get("sha256") != record_sha256(record):
        problems.append(f"{rid}: sha256 {str(record.get('sha256'))[:12]} does not equal the content hash "
                        f"{record_sha256(record)[:12]} (the record was edited after sealing)")
    cs = record.get("countersignature")
    if record.get("status") == "COUNTERSIGNED":
        if not isinstance(cs, dict) or not cs.get("by") or not cs.get("date_utc"):
            problems.append(f"{rid}: COUNTERSIGNED without a countersignature {{by, date_utc, record_sha256}}")
        elif cs.get("record_sha256") != record.get("sha256"):
            problems.append(f"{rid}: countersignature signs {str(cs.get('record_sha256'))[:12]}, record is {str(record.get('sha256'))[:12]}")
    elif cs is not None:
        problems.append(f"{rid}: carries a countersignature but status is {record.get('status')}")
    if not record.get("question"):
        problems.append(f"{rid}: missing question")
    if not any(record.get(k) for k in ("decision", "reading_PROPOSED", "proposal")):
        problems.append(f"{rid}: carries neither a decision nor a proposal")
    return problems


def load(root: str) -> dict[str, dict[str, Any]]:
    """The registry as {id: record}; refuses (raises) on any invalid or duplicated record."""
    path = os.path.join(root, REGISTRY_PATH)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    if doc.get("object") != "ADJUDICATION_REGISTRY":
        raise AdjudicationError(f"{REGISTRY_PATH}: object is {doc.get('object')!r}, not ADJUDICATION_REGISTRY")
    out: dict[str, dict[str, Any]] = {}
    problems: list[str] = []
    for rec in doc.get("records", []):
        problems.extend(validate(rec))
        if rec.get("id") in out:
            problems.append(f"{rec.get('id')}: duplicated in the registry")
        out[rec.get("id")] = rec
    if problems:
        raise AdjudicationError(f"{REGISTRY_PATH}: " + "; ".join(problems))
    return out


def reference(record: dict[str, Any]) -> dict[str, Any]:
    """The reference a served row carries. Built from the record; the status is read, never asserted."""
    return {"adjudication_id": record["id"], "adjudication_sha256": record["sha256"],
            "status": record["status"], "countersigned": record.get("countersignature") is not None}


def resolve(adjudication_id: str | None, registry: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The record a decision names, or a refusal that names the id. Never 'the last one for this trial'."""
    if not adjudication_id:
        raise AdjudicationError("decision names no adjudication_id")
    rec = registry.get(adjudication_id)
    if rec is None:
        raise AdjudicationError(f"{adjudication_id}: not in {REGISTRY_PATH}")
    if rec["status"] == "WITHDRAWN":
        raise AdjudicationError(f"{adjudication_id}: WITHDRAWN; a served row may not cite it")
    return rec


def _walk(obj: Any, path: str = ""):
    if isinstance(obj, dict):
        yield path, obj
        for k, v in obj.items():
            yield from _walk(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]")


def check_object(doc: Any, registry: dict[str, dict[str, Any]], where: str) -> list[str]:
    """Every citation in one served object, refused by name."""
    problems: list[str] = []
    cited: set[str] = set()
    for path, node in _walk(doc):
        if "adjudication_id" in node:
            rid = node.get("adjudication_id")
            cited.add(str(rid))
            rec = registry.get(rid)
            if rec is None:
                problems.append(f"{where}{path}: cites {rid}, not in the registry")
                continue
            if rec["status"] == "WITHDRAWN":
                problems.append(f"{where}{path}: cites {rid}, which is WITHDRAWN")
            is_reference = path.endswith("/adjudication") or "adjudication_sha256" in node
            if not is_reference:
                continue  # a decision NAMING the adjudication it was decided by; the reference sits beside it
            if node.get("adjudication_sha256") != rec["sha256"]:
                problems.append(f"{where}{path}: {rid} cited at sha256 {str(node.get('adjudication_sha256'))[:12]}, "
                                f"registry record is {rec['sha256'][:12]} (the decision changed under the citation)")
            if node.get("status") != rec["status"]:
                problems.append(f"{where}{path}: {rid} cited as {node.get('status')}, registry says {rec['status']}")
            if bool(node.get("countersigned")) != (rec.get("countersignature") is not None):
                problems.append(f"{where}{path}: {rid} countersigned={node.get('countersigned')} disagrees with the record")
        elif isinstance(node.get("adjudication"), dict) and "id" in node["adjudication"] and "adjudication_sha256" not in node["adjudication"]:
            problems.append(f"{where}{path}/adjudication: name-only citation {node['adjudication'].get('id')} (no content hash)")
    # ids mentioned in prose must exist too: a page may not talk about an adjudication the registry does not hold
    for path, node in _walk(doc):
        for k, v in node.items():
            if isinstance(v, str):
                for rid in set(ID_RE.findall(v)):
                    if rid not in registry:
                        problems.append(f"{where}{path}/{k}: mentions {rid}, not in the registry")
    return problems


def check(root: str) -> tuple[bool, list[str]]:
    import glob
    try:
        registry = load(root)
    except AdjudicationError as e:
        return False, [str(e)]
    problems: list[str] = []
    n_docs = 0
    for pattern in SERVED_OBJECTS:
        for path in sorted(glob.glob(os.path.join(root, pattern))):
            n_docs += 1
            with open(path, encoding="utf-8") as f:
                doc = json.load(f)
            problems.extend(check_object(doc, registry, os.path.relpath(path, root).replace(os.sep, "/")))
    if n_docs == 0:
        problems.append("no served objects found to check (docs/reviews/*/review.json)")
    return (not problems), problems


def summary(root: str) -> dict[str, Any]:
    import glob
    registry = load(root)
    cited: dict[str, int] = {}
    for pattern in SERVED_OBJECTS:
        for path in glob.glob(os.path.join(root, pattern)):
            with open(path, encoding="utf-8") as f:
                doc = json.load(f)
            for _p, node in _walk(doc):
                if "adjudication_id" in node:
                    cited[str(node["adjudication_id"])] = cited.get(str(node["adjudication_id"]), 0) + 1
    return {"records": len(registry), "by_status": {s: sum(1 for r in registry.values() if r["status"] == s) for s in STATUSES},
            "citations": sum(cited.values()), "records_cited": len(cited)}
