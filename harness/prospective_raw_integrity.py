"""Prospective-only verification of archived HTTP response bytes.

A hash of the JSON envelope alone does not authenticate its embedded API body:
this checker binds the decoded body to the body digest and index metadata.
It proves internal consistency, not completeness or external data authenticity.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
from typing import Any

_INDEX_FIELDS = (
    "source_id", "url", "params", "status", "fetched_utc",
    "adapter", "adapter_blob_sha", "body_sha256",
)
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def verify_raw_record(index_row: dict[str, Any], raw_envelope_bytes: bytes) -> None:
    """Raise ValueError when an indexed raw response cannot be authenticated.

    This check must follow the caller's index-SHA and envelope-file-SHA checks.
    A successful result verifies internal custody links only, not an API search.
    """
    if not isinstance(index_row, dict) or not isinstance(raw_envelope_bytes, bytes):
        raise ValueError("raw index row/envelope has an invalid type")
    try:
        envelope = json.loads(raw_envelope_bytes.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError("archived raw response is not valid UTF-8 JSON") from exc
    if not isinstance(envelope, dict):
        raise ValueError("archived raw response is not a JSON object")
    for field in _INDEX_FIELDS:
        if field not in index_row or field not in envelope:
            raise ValueError(f"archived raw response missing indexed field: {field}")
        if type(index_row[field]) is not type(envelope[field]) or index_row[field] != envelope[field]:
            raise ValueError(f"archived raw response/index mismatch: {field}")
    digest = envelope["body_sha256"]
    if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
        raise ValueError("archived raw response has invalid body_sha256")
    encoded = envelope.get("body_bytes_b64")
    if not isinstance(encoded, str):
        raise ValueError("archived raw response is missing body_bytes_b64")
    try:
        body_bytes = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("archived raw response body is not valid base64") from exc
    if base64.b64encode(body_bytes).decode("ascii") != encoded:
        raise ValueError("archived raw response body is not canonical base64")
    if hashlib.sha256(body_bytes).hexdigest() != digest:
        raise ValueError("archived raw response body SHA256 mismatch")
