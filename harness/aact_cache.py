"""Topic-scoped, cache-only AACT inputs for deterministic review builds.

Only scripts/aact_measure.py opens a snapshot. Missing or invalid measurements
are typed absences, never a request to discover an off-tree database.
"""
from contextvars import ContextVar
from functools import wraps
import json
from pathlib import Path

from .canonical import canonical_json, sha256_text

ROOT = Path(__file__).resolve().parents[1]
NOT_MEASURED = "AACT_NOT_MEASURED"
_current = ContextVar("aact_measurement", default=None)
KINDS = ("study_dates", "sponsors", "arm_index")


def load(slug, root=None):
    path = Path(root or ROOT) / "cache" / slug / "aact_inputs.json"
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        if (doc.get("version") != 1 or doc.get("slug") != slug
                or doc.get("status") != "MEASURED" or not doc.get("snapshot")
                or any(not isinstance(doc.get("values", {}).get(k), dict) for k in KINDS)
                or doc.get("sha256") != sha256_text(canonical_json(
                    {k: v for k, v in doc.items() if k != "sha256"}))):
            return None
        return doc
    except (OSError, ValueError, TypeError, AttributeError):
        return None


def values(kind, slug=None):
    doc = _current.get()
    if doc is None and slug:
        doc = load(slug)
    return (doc or {}).get("values", {}).get(kind, {})


def cache_only_build(function):
    @wraps(function)
    def wrapped(slug, *args, **kwargs):
        doc = load(slug)
        token = _current.set(doc)
        try:
            review = function(slug, *args, **kwargs)
            if doc is None:
                review["aact_status"] = NOT_MEASURED
            return review
        finally:
            _current.reset(token)
    return wrapped
