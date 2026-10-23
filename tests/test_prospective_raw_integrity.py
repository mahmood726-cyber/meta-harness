"""Offline structural tests. No external retrieval or independent validation."""
from __future__ import annotations

import base64
import hashlib
import json

import pytest

from harness.prospective_raw_integrity import verify_raw_record


def _pair(body=b'{"result": []}'):
    sha = hashlib.sha256(body).hexdigest()
    fields = {
        "source_id": "pubmed_concept_query#1",
        "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        "params": {"term": "heart failure AND trial"},
        "status": 200,
        "fetched_utc": "2026-10-24T00:00:00Z",
        "adapter": "harness.fetch.run",
        "adapter_blob_sha": "1" * 40,
        "body_sha256": sha,
    }
    envelope = {**fields, "body_bytes_b64": base64.b64encode(body).decode("ascii")}
    return fields, envelope


def test_valid_binary_body_and_empty_body():
    for body in (b'{"result": []}', b'', b'\\x00\\xff'):
        row, envelope = _pair(body)
        verify_raw_record(row, json.dumps(envelope).encode())


@pytest.mark.parametrize("field", [
    "source_id", "url", "params", "status", "fetched_utc", "adapter", "adapter_blob_sha", "body_sha256"
])
def test_index_envelope_disagreement_is_refused(field):
    row, envelope = _pair()
    envelope[field] = {"unexpected": "value"}
    with pytest.raises(ValueError, match="mismatch"):
        verify_raw_record(row, json.dumps(envelope).encode())


@pytest.mark.parametrize("mutate,reason", [
    ("different_bytes", "body SHA256 mismatch"),
    ("bad_base64", "not valid base64"),
    ("no_body", "missing body_bytes_b64"),
    ("no_sha", "missing indexed field"),
    ("invalid_sha", "invalid body_sha256"),
    ("noncanonical", "not canonical base64"),
    ("wrong_envelope_type", "not a JSON object"),
    ("bad_json", "not valid UTF-8 JSON"),
    ("wrong_index_type", "invalid type"),
    ("wrong_type_status", "mismatch"),
])
def test_corrupt_envelopes_are_refused(mutate, reason):
    row, envelope = _pair()
    if mutate == "different_bytes":
        envelope["body_bytes_b64"] = base64.b64encode(b"changed").decode("ascii")
    elif mutate == "bad_base64":
        envelope["body_bytes_b64"] = "???"
    elif mutate == "no_body":
        del envelope["body_bytes_b64"]
    elif mutate == "no_sha":
        del envelope["body_sha256"]
    elif mutate == "invalid_sha":
        envelope["body_sha256"] = row["body_sha256"] = "XYZ"
    elif mutate == "noncanonical":
        # Padding bits are nonzero; still decodes to the byte x.
        envelope["body_bytes_b64"] = "eI=="
    elif mutate == "wrong_envelope_type":
        envelope = []
    elif mutate == "bad_json":
        with pytest.raises(ValueError, match=reason):
            verify_raw_record(row, b"not json")
        return
    elif mutate == "wrong_index_type":
        row = []
    elif mutate == "wrong_type_status":
        envelope["status"] = 200.0
    with pytest.raises(ValueError, match=reason):
        verify_raw_record(row, json.dumps(envelope).encode())


def test_missing_index_field_fails():
    row, envelope = _pair()
    del row["url"]
    with pytest.raises(ValueError, match="missing indexed field"):
        verify_raw_record(row, json.dumps(envelope).encode())
