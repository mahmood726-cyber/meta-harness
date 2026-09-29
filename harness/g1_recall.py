"""Offline search recall audit; identity and screening never admit pooled data."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

from .identity_join import identity, join
from .screen import screen_record
from .search_v2 import _candidate_id


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def candidate_records(root, payload, slug):
    """Bind the lightweight candidate manifest to its full held snapshot records."""
    meta = payload.get("topics", {}).get(slug)
    if meta is None:
        raise ValueError("REFUSED_SEARCH_TOPIC_NOT_RUN:" + slug)
    if meta.get("state") not in {"RAN_OK", "RAN_OK_WITH_SOURCE_ERRORS", "RAN_ZERO"}:
        raise ValueError("REFUSED_SEARCH_STATE:" + slug + ":" + str(meta.get("state")))
    root = Path(root).resolve()
    path = (root / meta["snapshot_dir"] / "records.json").resolve()
    if not path.is_relative_to(root / "cache" / slug / "snapshots"):
        raise ValueError("REFUSED_SNAPSHOT_PATH:" + slug)
    held = read(path)
    records = held.get("records")
    candidates = payload.get("candidates", {}).get(slug)
    if held.get("slug") != slug or not isinstance(records, list) or not isinstance(candidates, list):
        raise ValueError("REFUSED_CANDIDATE_SCHEMA:" + slug)
    def signature(row, summary=False):
        cid, kind = (row["id"], row["id_type"]) if summary else _candidate_id(row)
        return (cid, kind, row.get("title") or "", row.get("doi") or "",
                row.get("nct") or (cid if kind == "nct" else ""),
                row.get("pmid") or (cid if kind == "pmid" else ""))
    if (meta.get("candidate_count") != len(candidates)
            or Counter(signature(r) for r in records) != Counter(signature(r, True) for r in candidates)):
        raise ValueError("REFUSED_CANDIDATE_SNAPSHOT_MISMATCH:" + slug)
    return records


def queue_identity(entry):
    return {"label": entry["label"], **{k: v for k, v in entry["resolved"].items()
                                       if k != "spans" and v is not None}}


def screen(rec, topic):
    # Full snapshots already use screen_record's schema; preserve it without enrichment.
    decision, rule, reason, span = screen_record(deepcopy(rec), deepcopy(topic.get("include", {})),
                                                set(topic.get("negative_control_pmids", [])))
    return dict(decision=decision, rule=rule, reason=reason, span=span)


def recall_trial(entry, records, topic, identities=None):
    linked = join(queue_identity(entry), identities if identities is not None else records)
    out = dict(label=entry["label"], resolution=entry["resolution"],
               identity_resolvable=any(identity(queue_identity(entry)).values()),
               evidence_kind=entry.get("evidence_kind", "PRINTED"), identity_join=linked)
    if linked["status"] == "AMBIGUOUS":
        out.update(status="ABSTAIN", reason=linked["reason"])
    elif linked["status"] == "NOT_JOINED":
        out.update(status="NOT_RETRIEVED", reason=linked["reason"])
    else:
        rec = records[linked["index"]]
        out.update(status="RETRIEVED", candidate_id=rec["id"], title=rec.get("title", ""),
                   screen=screen(rec, topic))
    return out


def metric(items, denominator):
    return dict(n=len(items), N=denominator, n_of_N=f"{len(items)} of {denominator}", items=items)


def metrics(rows):
    n = len(rows)
    retrieved = [r for r in rows if r["status"] == "RETRIEVED"]
    result = {s: metric([r["item"] for r in rows if r["status"] == s], n)
              for s in ("RETRIEVED", "NOT_RETRIEVED", "ABSTAIN", "UNAVAILABLE")}
    for d in ("include", "exclude"):
        result["SCREEN_" + d.upper()] = metric([r["item"] for r in retrieved if r["screen"]["decision"] == d], len(retrieved))
    for rule in sorted({r["screen"]["rule"] for r in retrieved}):
        result["SCREEN_RULE/" + rule] = metric([r["item"] for r in retrieved if r["screen"]["rule"] == rule], len(retrieved))
    for resolvable in (True, False):
        result["NOT_RETRIEVED/" + ("RESOLVABLE" if resolvable else "UNRESOLVABLE")] = metric(
            [r["item"] for r in rows if r["status"] == "NOT_RETRIEVED" and r["identity_resolvable"] == resolvable],
            result["NOT_RETRIEVED"]["n"])
    return result


def ceiling(our_k, rows):
    # Repeated labels joined to one record must not inflate even a hypothetical k.
    included = [r for r in rows if r["status"] == "RETRIEVED"
                and r["screen"]["decision"] == "include" and r["evidence_kind"] != "RELAYED"]
    additions = len({r["identity_join"]["index"] for r in included})
    return dict(label="CEILING: screening inclusion is not extraction or pool admission",
                additions=additions, our_k=our_k, k=None if our_k is None else our_k + additions)
