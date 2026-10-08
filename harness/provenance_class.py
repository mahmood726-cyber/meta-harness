"""Provenance class of one SERVED value (a pooled trial row of docs/reviews/<slug>/review.json), shared by the provenance
census gate (scripts/provenance_census.py) and the page's Data-extraction tab (harness/review_tabs.py), so the page states
exactly the class the gate computes. Moved verbatim from scripts/provenance_census.py (2026-10-08).

  EXTRACTOR            a deterministic regex / typed extractor over a held source, with the span it read
  RECORDED_MODEL_CALL  a recorded model call that replays offline: every cited record (mc-<32 hex>) is in the tree
  HAND_ENTERED         a value entered outside the harness, bound to a held span (burn-down list only)
  UNTRACED             none of the above -> refused by the gate
"""
from __future__ import annotations

import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MC = re.compile(r"mc-[0-9a-f]{32}")
EXTRACTOR_PROV = {"abstract", "pmc_fulltext", "pmc_fulltext_effect", "ctgov_results", "aact_verified", "published_rate",
                  "pre_specified_dose"}


def _records_in(obj) -> list[str]:
    return sorted(set(MC.findall(json.dumps(obj, ensure_ascii=False))))


def classify_served(t: dict, held) -> tuple[str, str]:
    """held(record_id) -> bool is supplied by the caller: the census checks the record store; a served page
    passes a constant True because it has passed the provenance gate, which refuses any row citing a record
    that is not in the tree (this module never names the store)."""
    prov = str(t.get("provenance") or "")
    if prov == "served_pool_signed_notice":
        adm = t.get("served_pool_admission") or {}
        ids = _records_in(adm)
        missing = [i for i in ids if not held(i)]
        if missing:
            return "UNTRACED", f"signed row cites record(s) not in the tree: {missing}"
        if ids:
            return "RECORDED_MODEL_CALL", f"signed row: {ids}"
        if t.get("source") and _deterministic_basis(json.dumps(adm)):
            return "EXTRACTOR", f"signed row: {adm.get('basis')}"
        return "UNTRACED", "signed row with neither a record nor a typed registry source"
    if "_verified" in prov:
        return "HAND_ENTERED", f"verified input ({prov}), bound to a held span"
    if prov in EXTRACTOR_PROV:
        if not str(t.get("source") or "").strip():
            return "UNTRACED", f"{prov} row with no source span"
        return "EXTRACTOR", prov
    ids = _records_in(t)
    if ids:
        missing = [i for i in ids if not held(i)]
        return ("UNTRACED", f"cites record(s) not in the tree: {missing}") if missing else ("RECORDED_MODEL_CALL", str(ids))
    return "UNTRACED", f"provenance {prov!r} is not a known extractor and cites no record"


_DET = re.compile(r"(?<![A-Za-z])AACT(?![A-Za-z])|PRIMARY_TEXT|\bTEXT\b|trial's own text|states the counts|"
                  r"supplementary table \(sha256 [0-9a-f]+\), row|TYPED_(?:TABLE|COMPARATOR_ROW)|"
                  r"verbatim \(level printed\)|NDA\d+")


def _deterministic_basis(b: str) -> bool:
    """A basis naming a deterministic source of the value: the trial's own held text or registry (AACT), a typed table
    read over held bytes (sha256 + row), or a verbatim span of a held regulatory document."""
    return bool(_DET.search(b or ""))


def recorded_reads(root: str = ROOT) -> dict:
    p = os.path.join(root, "registry", "provenance_recorded_reads.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as fh:
        return json.load(fh).get("reads") or {}


def served_class(t: dict, slug: str, outcome_name: str, held, reads: dict | None = None, root: str = ROOT) -> tuple[str, str, list]:
    """The census's class for one served row: classify_served, then a HAND_ENTERED row converted by a recorded,
    replayable locator read (scripts/provenance_convert.py) whose gated numbers EQUAL the served value becomes
    RECORDED_MODEL_CALL. Returns (class, why, record ids the class rests on)."""
    cls, why = classify_served(t, held)
    recs = _records_in(t)
    if cls == "HAND_ENTERED":
        reads = recorded_reads(root) if reads is None else reads
        rr = reads.get(f"{slug}|{str(t.get('id')).replace('PMID ', '').strip()}|{outcome_name}") or {}
        if rr.get("state") == "AGREES" and rr.get("record_id") and held(rr["record_id"]):
            cls, why = "RECORDED_MODEL_CALL", f"recorded read {rr['record_id']} agrees with the served value"
            recs = sorted(set(recs) | {rr["record_id"]})
    return cls, why, recs
