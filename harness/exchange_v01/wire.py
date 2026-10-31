"""Fail-closed raw JSON boundary for the opt-in v0.1 exchange contract.

The historical certificate code scope must not import this optional package.
A decoded Python dict cannot reveal duplicate wire JSON members.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import validate_exchange, validate_manifest


def _unique_members(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object member: {key}")
        result[key] = value
    return result


def _reject_nonstandard_constant(value: str) -> None:
    raise ValueError(f"nonstandard JSON constant: {value}")


def _decode(raw: str | bytes, label: str) -> object:
    if isinstance(raw, bytes):
        try:
            raw = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"{label} JSON must be UTF-8") from exc
    if not isinstance(raw, str) or raw.startswith("\ufeff"):
        raise ValueError(f"{label} JSON must be UTF-8 without a BOM")
    try:
        raw.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{label} JSON has invalid Unicode") from exc
    try:
        return json.loads(
            raw,
            object_pairs_hook=_unique_members,
            parse_constant=_reject_nonstandard_constant,
        )
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed {label} JSON") from exc


def validate_manifest_json(raw: str | bytes, manifest_dir: Path) -> None:
    """Preparse every member, then apply the versioned manifest contract.

    This checks local syntax, pins and file bytes, not remote Actions truth.
    """
    validate_manifest(_decode(raw, "benchmark manifest"), manifest_dir)


def validate_exchange_json(raw: str | bytes, archive_root: Path) -> None:
    """Reject shadowed REFUSE, trial/source identity or estimand before handoff.

    Structural acceptance is NOT independent eligibility or permission to pool.
    """
    validate_exchange(_decode(raw, "exchange"), archive_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate pinned synthetic manifest raw JSON (not scientific validation)"
    )
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args(argv)
    validate_manifest_json(args.manifest.read_bytes(), args.manifest.parent)
    print("MANIFEST VERIFIED: pins and fixture SHA-256; cases retain their stated statuses")
    return 0
