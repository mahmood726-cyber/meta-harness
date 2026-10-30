"""Source-only, synthetic-ready REPRO300 pre-draw guard.

Not independent custody, enrolment, source permission verification, or scientific
validation. No published numerical outcome is used by this module.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from typing import Any

STRATA = {"COCHRANE": 100, "OPEN_META": 100, "KNOWN_ERROR": 50, "UNSELECTED": 50}
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
REVIEW_ID = re.compile(r"(?:CD\d{6}|10\.[0-9]{4,9}/[^\s]+)\Z", re.I)
REQUIRED = {
    "review_id", "analysis_id", "family_key", "stratum", "source_sha256",
    "source_version", "rights_checked", "source_download_verified",
    "prior_exposure", "source_checked_without_outcomes", "access_path",
    "license_uri", "rights_scope", "planned_use",
}


class SelectionRefusal(ValueError):
    """A source identity, rights, exposure, or custody declaration is invalid."""


def _canonical(data: Any) -> bytes:
    return json.dumps(
        data, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False
    ).encode("utf-8")


def _nonblank(value: Any) -> bool:
    return type(value) is str and bool(value.strip()) and value == value.strip()


def preflight(frame: list[dict], previously_exposed_families: set[str]) -> dict:
    """Return candidate-only eligibility, never a frozen or enrolled case list.

    The exposure inventory is caller-supplied: this function cannot certify
    that all prior tuning, corrections, source families or studies were found.
    """
    if type(frame) is not list or type(previously_exposed_families) is not set:
        raise SelectionRefusal("frame must be list and exposure inventory must be set")
    if any(not _nonblank(x) for x in previously_exposed_families):
        raise SelectionRefusal("invalid prior exposure family")
    exposure_families = {x.casefold() for x in previously_exposed_families}
    seen_ids: set[tuple[str, str]] = set()
    seen_reviews: set[str] = set()
    seen_families: set[str] = set()
    candidates = []
    refused = Counter()
    for i, row in enumerate(frame):
        if type(row) is not dict or not REQUIRED.issubset(row):
            raise SelectionRefusal(f"row {i}: missing declared source identity fields")
        if type(row["stratum"]) is not str or row["stratum"] not in STRATA:
            raise SelectionRefusal(f"row {i}: invalid stratum")
        for field in (
            "review_id", "analysis_id", "family_key", "source_version",
            "access_path", "license_uri"
        ):
            if not _nonblank(row[field]):
                raise SelectionRefusal(f"row {i}: invalid {field}")
        if not row["license_uri"].startswith(("https://", "http://")):
            raise SelectionRefusal(f"row {i}: license URI required")
        if row["rights_scope"] not in (
            "LOCAL_NUMERIC_ONLY", "AI_PROCESSING_PERMITTED"
        ):
            raise SelectionRefusal(
                f"row {i}: licence permission scope must be explicit"
            )
        if row["planned_use"] not in ("NUMERIC_ONLY", "AI_ASSISTED_EXTRACTION"):
            raise SelectionRefusal(f"row {i}: invalid planned_use")
        if not REVIEW_ID.fullmatch(row["review_id"]):
            raise SelectionRefusal(f"row {i}: noncanonical review identifier")
        if not (
            type(row["source_sha256"]) is str
            and HEX64.fullmatch(row["source_sha256"])
        ):
            raise SelectionRefusal(f"row {i}: missing source SHA256")
        for field in (
            "rights_checked", "source_download_verified", "prior_exposure",
            "source_checked_without_outcomes"
        ):
            if type(row[field]) is not bool:
                raise SelectionRefusal(f"row {i}: {field} must be explicit boolean")
        key = (row["review_id"].casefold(), row["analysis_id"].casefold())
        family = row["family_key"].casefold()
        if key in seen_ids:
            raise SelectionRefusal(f"row {i}: duplicate review/analysis identity")
        seen_ids.add(key)
        # REPRO300 counts REVIEWS. Two analyses of one review do not count as
        # independent selections, even if labelled with different strata/families.
        review_key = row["review_id"].casefold()
        if review_key in seen_reviews:
            raise SelectionRefusal(
                f"row {i}: duplicate review identity across analyses/strata"
            )
        seen_reviews.add(review_key)
        if family in seen_families:
            raise SelectionRefusal(f"row {i}: same-family cases are not independent")
        seen_families.add(family)
        reasons = []
        if family in exposure_families or row["prior_exposure"]:
            reasons.append("TESTED_LEAKAGE")
        if not row["rights_checked"]:
            reasons.append("ACCESS_RIGHTS_UNVERIFIED")
        if not row["source_download_verified"]:
            reasons.append("SOURCE_UNAVAILABLE")
        if (
            row["planned_use"] == "AI_ASSISTED_EXTRACTION"
            and row["rights_scope"] != "AI_PROCESSING_PERMITTED"
        ):
            reasons.append("PROCESSING_RIGHTS_MISMATCH")
        if not row["source_checked_without_outcomes"]:
            reasons.append("OUTCOME_EXPOSURE_UNVERIFIED")
        if reasons:
            for reason in reasons:
                refused[reason] += 1
            continue
        candidates.append({
            k: row[k] for k in (
                "review_id", "analysis_id", "family_key", "stratum",
                "source_sha256", "source_version", "access_path",
                "license_uri", "rights_scope", "planned_use"
            )
        })
    return {
        "status": "SOURCE_ONLY_CANDIDATES_NOT_ENROLLED",
        "frame_rows": len(frame),
        "eligible_candidates": len(candidates),
        "refusals_by_reason": dict(refused),
        "source_only_frame_sha256": hashlib.sha256(_canonical(frame)).hexdigest(),
        "exposure_inventory_sha256": hashlib.sha256(
            _canonical(sorted(exposure_families))
        ).hexdigest(),
        "candidates": candidates,
    }


def pilot_draw(
    preflight_result: dict, seed_commitment: str, *, frame: list[dict],
    previously_exposed_families: set[str], per_stratum: int = 2
) -> dict:
    """Recompute eligibility against original source/exposure inputs before draw.

    Immutable custody, source-byte authentication, independent seed commitment,
    and genuine prospective freeze are external prerequisites.
    """
    if not (
        type(seed_commitment) is str and HEX64.fullmatch(seed_commitment)
    ):
        raise SelectionRefusal("seed commitment must be a 64-hex digest")
    if type(per_stratum) is not int or per_stratum != 2:
        raise SelectionRefusal("pilot is predeclared as 2 candidates per stratum")
    if type(preflight_result) is not dict:
        raise SelectionRefusal("preflight result must be a mapping")
    expected = preflight(frame, previously_exposed_families)
    if preflight_result != expected:
        raise SelectionRefusal(
            "preflight mismatch against original source/exposure inputs"
        )
    selected = []
    counts = {}
    enough = True
    for stratum in STRATA:
        rows = [r for r in expected["candidates"] if r["stratum"] == stratum]
        rows.sort(key=lambda r: hashlib.sha256(
            (seed_commitment + "|" + r["review_id"] + "|" + r["analysis_id"])
            .encode()
        ).hexdigest())
        counts[stratum] = {
            "available_candidates": len(rows), "target": STRATA[stratum],
            "pilot_required": per_stratum
        }
        if len(rows) < per_stratum:
            enough = False
        selected.extend(rows[:per_stratum])
    if not enough:
        return {
            "status": "BLOCKED_INSUFFICIENT_ELIGIBLE_CANDIDATES",
            "selection_frame_sha256": expected["source_only_frame_sha256"],
            "exposure_inventory_sha256": expected["exposure_inventory_sha256"],
            "counts": counts, "candidate_draw": [],
            "candidate_draw_sha256": None,
        }
    return {
        "status": "CANDIDATES_NOT_FROZEN_NOT_EXECUTED",
        "selection_frame_sha256": expected["source_only_frame_sha256"],
        "exposure_inventory_sha256": expected["exposure_inventory_sha256"],
        "counts": counts, "candidate_draw": selected,
        "candidate_draw_sha256": hashlib.sha256(
            _canonical(selected)
        ).hexdigest(),
    }
