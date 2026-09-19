"""Canonical serialization + hashing.

The review object is the single source of truth for a page. Its canonical JSON
form is hashed; the served HTML is a pure, deterministic function of that JSON.
Two things must agree for a page to be publishable:
  review_sha256  = sha256(canonical_json(review))         # the data
  html_sha256    = sha256(render_page(review).encode())   # the served artifact
Any hand-edit of the HTML changes html_sha256 without changing review_sha256,
so the reproduction census catches it.
"""
from __future__ import annotations
import hashlib
import json
from typing import Any


def canonical_json(obj: Any) -> str:
    """Deterministic JSON: sorted keys, no insignificant whitespace, UTF-8."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def review_core(review: dict) -> dict:
    """The review MINUS the self-referential 'reproduction' block.

    The reproduction block records the census outcome (including hashes), so it
    cannot be part of what those hashes cover. review_sha256 is defined over the
    core; the census then re-derives the core on a fresh clone and compares.
    """
    return {k: v for k, v in review.items() if k != "reproduction"}


def review_sha256(review: dict) -> str:
    return sha256_text(canonical_json(review_core(review)))
