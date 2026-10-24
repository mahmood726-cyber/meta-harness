"""Fail-closed provenance and append-only journal primitives.

Research-stage infrastructure; not evidence of clinical validation.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256(data):
    return hashlib.sha256(data).hexdigest()

REQUIRED = ("review_id", "study_id", "document_sha256", "source_uri",
            "source_page_or_locator", "verbatim_passage", "field_name",
            "raw_value", "normalised_value", "unit", "population",
            "outcome", "time_point", "effect_measure", "extractor_identity",
            "extracted_at_utc", "status")

def validate_extraction(record, archive_bytes):
    if not isinstance(record, dict) or any(k not in record for k in REQUIRED):
        raise ValueError("missing required extraction fields")
    if record["status"] not in ("PROPOSED", "SOURCE_CHECKED", "ADJUDICATED", "REFUSED"):
        raise ValueError("unknown extraction status")
    if not isinstance(archive_bytes, bytes):
        raise ValueError("archived source bytes required")
    if record["document_sha256"] != sha256(archive_bytes):
        raise ValueError("source digest mismatch")
    if record["status"] in ("SOURCE_CHECKED", "ADJUDICATED"):
        passage = record["verbatim_passage"]
        if not isinstance(passage, str) or not passage.strip():
            raise ValueError("verified extraction needs a passage")
        if passage.encode("utf-8") not in archive_bytes:
            raise ValueError("passage not present in archived bytes")
        if not record["source_page_or_locator"]:
            raise ValueError("verified extraction needs a locator")
    return True

def append_event(path, event):
    """Append a canonical, hash-chained event; reject a corrupted prior journal."""
    path = Path(path)
    events = read_events(path)
    if not isinstance(event, dict) or "event_sha256" in event:
        raise ValueError("invalid event")
    required = ("event_id", "timestamp_utc", "actor_type", "actor_id",
                "action", "study_id", "source_digest", "reason", "supersedes_event_id")
    if any(k not in event for k in required):
        raise ValueError("incomplete event")
    if any(old["event_id"] == event["event_id"] for old in events):
        raise ValueError("duplicate event ID")
    record = dict(event, previous_event_sha256=events[-1]["event_sha256"] if events else None)
    record["event_sha256"] = sha256(canonical(record))
    with path.open("ab") as stream:
        stream.write(canonical(record) + b"\n")
    return record["event_sha256"]

def read_events(path):
    path = Path(path)
    if not path.exists():
        return []
    records = []
    for line in path.read_bytes().splitlines():
        event = json.loads(line)
        digest = event.pop("event_sha256", None)
        if digest != sha256(canonical(event)):
            raise ValueError("journal event digest mismatch")
        if event.get("previous_event_sha256") != (records[-1]["event_sha256"] if records else None):
            raise ValueError("journal chain broken")
        event["event_sha256"] = digest
        records.append(event)
    return records

def can_pool(analysis, studies):
    """Refuse unresolved decisions and incompatible estimands."""
    if analysis.get("decision") != "ALLOW":
        return False
    measure = analysis.get("estimand")
    selected = analysis.get("studyIds")
    if not measure or not isinstance(selected, list) or not selected:
        return False
    return all(studies.get(sid, {}).get("eligibility") == "INCLUDE"
               and studies[sid].get("extractionReviewed") is True
               and studies[sid].get("estimand") == measure for sid in selected)
