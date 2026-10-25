"""Dual independent extraction of OUTCOME fields, and adjudication by the source text.

reading = {"reader": {"family": "anthropic"|"openai"|..., "model_reported": str, "record_id": str},
           "items": [item, ...]}          # items as in fields.py, each with its own passage
adjudication = {"field": str, "arm": str|None, "decided_value": <typed>, "passage": {...},
                "adjudicator": {"kind": "human"|"model", "name": str, "record_id": str|None, "family": str|None},
                "rationale": str}

Independence (refused otherwise): exactly two readings; their families are {"anthropic", "openai"} (Claude + Codex);
their record_ids are distinct and non-empty; and, when the call records are supplied, neither reader's prompt inputs
include the other reader's response (a reader shown the first answer is a confirmer, not a second reader).

Per OUTCOME (field, arm):
  AGREED       both readers give the same typed value, each with its own verified passage containing it;
  UNRESOLVED   readers disagree, one is unsupported, or a proposed adjudication exists without
               an independently authenticated blinded external-review receipt. Source-supported
               arithmetic may identify a proposed value, but does NOT verify human independence.
               Preserve both reader observations and claimed adjudicator identities for review.
               An UNRESOLVED outcome field blocks a match claim.
No authenticated external-adjudication receipt verifier is implemented in this module.
A caller-supplied "human", "blinded" or "independent" flag is not such verification.
"""
from __future__ import annotations

from decimal import Decimal

from . import fields as F
from .passage import passage_problems, value_in_quote

REQUIRED_FAMILIES = frozenset({"anthropic", "openai"})


def same_value(a, b) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return False
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return Decimal(str(a)) == Decimal(str(b))
    if isinstance(a, str) and isinstance(b, str):
        return " ".join(a.casefold().split()) == " ".join(b.casefold().split())
    return False


def item_problems(item, docs_root, cache) -> list[str]:
    """Everything that stops ONE item from being evidence: type, passage, value-in-passage."""
    probs = F.type_problems(item)
    if probs:
        return probs
    pp = passage_problems(item.get("passage"), docs_root, cache)
    if pp:
        return pp
    spec = F.FIELDS[item["field"]]
    if not value_in_quote(item["field"], spec.kind, item["value"], item["passage"]["quote"]):
        return [f"value {item['value']!r} is not in its quoted passage (a real quote that does not contain the value "
                f"is a citation, not a source)"]
    return []


def independence_problems(readings, call_records: dict | None = None) -> list[str]:
    if not isinstance(readings, list) or len(readings) != 2:
        return [f"dual extraction needs exactly 2 readings, got {len(readings) if isinstance(readings, list) else 0}"]
    rs = [r.get("reader") or {} for r in readings]
    fams = {str(r.get("family") or "") for r in rs}
    out = []
    if fams != REQUIRED_FAMILIES:
        out.append(f"reader families {sorted(fams)} != {sorted(REQUIRED_FAMILIES)} (Claude + Codex)")
    ids = [str(r.get("record_id") or "") for r in rs]
    if not all(ids) or ids[0] == ids[1]:
        out.append("each reading must cite its own distinct call record_id")
    if call_records:
        recs = [call_records.get(i) for i in ids]
        if not all(recs):
            out.append("a reading's call record is missing from the supplied records")
        else:
            for me, other in ((recs[0], recs[1]), (recs[1], recs[0])):
                other_resp = ((other.get("response") or {}).get("sha256"))
                seen = {d.get("sha256") for d in me.get("input_digests") or []}
                if other_resp and other_resp in seen:
                    out.append(f"reader {me.get('record_id', '?')[:12]} was shown the other reader's response "
                               f"(a confirmer, not an independent second reading)")
    return out


def resolve(readings, adjudications, docs_root, call_records=None, cache=None) -> dict:
    """-> {"independence": [...problems], "fields": {(field, arm): {"status", "value", "problems"}}}"""
    cache = cache if cache is not None else {}
    indep = independence_problems(readings, call_records)
    by_reader = []
    for r in readings if isinstance(readings, list) else []:
        m = {}
        for it in r.get("items") or []:
            if F.FIELDS.get(it.get("field")) is not None and F.FIELDS[it["field"]].role == "OUTCOME":
                m.setdefault(F.key(it), []).append(it)
        by_reader.append(m)
    keys = sorted({k for m in by_reader for k in m}, key=lambda k: (k[0], k[1] or ""))
    reader_ids = {str((r.get("reader") or {}).get("record_id") or "") for r in readings if isinstance(r, dict)} \
        if isinstance(readings, list) else set()
    adj = {}
    for a in adjudications or []:
        adj.setdefault((a.get("field"), a.get("arm")), []).append(a)
    out = {}
    for k in keys:
        vals, probs, reader_candidates = [], [], []
        for n, m in enumerate(by_reader):
            its = m.get(k, [])
            actor = readings[n].get("reader") or {}
            # Do not drop explicit 0 or False through truthiness coercion. The
            # source_checked flag distinguishes a typed, sourced reading from
            # a rejected raw observation; identities here are self-reported.
            candidate = {"reader_family_claimed": actor.get("family"),
                         "reader_record_id_claimed": actor.get("record_id"),
                         "raw_value": its[0].get("value") if len(its) == 1 else None,
                         "source_checked": False}
            reader_candidates.append(candidate)
            if len(its) != 1:
                probs.append(f"reader {n + 1}: {len(its)} values for {k} (need exactly one)")
                vals.append(None)
                continue
            ip = item_problems(its[0], docs_root, cache)
            if ip:
                probs.append(f"reader {n + 1}: " + "; ".join(ip))
                vals.append(None)
            else:
                vals.append(its[0]["value"])
                candidate["source_checked"] = True
        # Even two agreeing models cannot silently override an additional
        # dissenting human/model annotation. No external blinded adjudication
        # receipt is independently verifiable here, so manual review is owed.
        if (not adj.get(k) and not indep and len(vals) == 2 and
                vals[0] is not None and vals[1] is not None and same_value(*vals)):
            out[k] = {"status": "AGREED", "value": vals[0], "problems": []}
            continue
        if not indep and len(vals) == 2 and None not in vals:
            probs.append(f"readers disagree: {vals[0]!r} vs {vals[1]!r}")
        decided = None
        adjudication_proposals = []
        for a in adj.get(k, []):
            who = a.get("adjudicator") or {}
            ap = []
            if who.get("kind") not in ("human", "model") or not str(who.get("name") or "").strip():
                ap.append("adjudicator must be a named human or model")
            if who.get("record_id") and str(who["record_id"]) in reader_ids:
                ap.append("the adjudicator is one of the readers (a reader cannot settle its own disagreement)")
            if not str(a.get("rationale") or "").strip():
                ap.append("adjudication without a rationale")
            ap += item_problems({"field": k[0], "arm": k[1], "value": a.get("decided_value"),
                                 "passage": a.get("passage")}, docs_root, cache)
            adjudication_proposals.append({
                "actor_kind_claimed": who.get("kind"),
                "actor_name_claimed": who.get("name"),
                "actor_record_id_claimed": who.get("record_id"),
                "raw_value": a.get("decided_value"),
                "source_checked": not ap,
            })
            if ap:
                probs.append("adjudication refused: " + "; ".join(ap))
            else:
                decided = a.get("decided_value")
        if indep:
            probs.insert(0, "readings are not independent")
        if adj.get(k):
            # A quoted passage verifies neither blinding nor an actual external
            # reviewer. Do not promote a source-backed self-attestation to PASS.
            probs.append("external blinded adjudication is not authenticated; manual review required")
        out[k] = {"status": "UNRESOLVED", "value": None,
                  "problems": probs or ["no agreement and no adjudication"],
                  "reader_candidates": reader_candidates,
                  "adjudication_proposals": adjudication_proposals}
    return {"independence": indep, "fields": out}
