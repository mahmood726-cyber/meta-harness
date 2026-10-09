"""The effect-measure CONTRACT (external audit review 2 F1 / review 4 #1): a served outcome is served on the estimand its
protocol REGISTERS. source_hierarchy.estimand_decision otherwise lets a declared OR fall back to the scale of the only
published effect ('declared OR, but the target outcome's only published effect+CI is RR'), which served RECOVERY's
age-adjusted RATE ratio as the corticosteroids topic's RR although its protocol registers an odds ratio.

registry/estimand_contract.json lists the outcomes whose served scale is held to the declared estimand, each SIGNED by
Mahmood (a ratified block naming the packet item and its sha256). Only a signed entry changes what is served; an outcome
without one keeps today's behaviour and is reported by the sweep for a decision (never changed unsigned)."""
from __future__ import annotations

import json
import os
import re
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "registry", "estimand_contract.json")


_SHA256 = re.compile(r"[0-9a-f]{64}")


def _load(path: str | None = None) -> list[dict[str, Any]]:
    """Fails closed: a missing registry raises (codex gate-v12-11-r1 P2) -- losing the file must not silently serve
    every outcome without its signed contract."""
    p = path or REG
    if not os.path.exists(p):
        raise FileNotFoundError(f"effect-measure contract registry missing: {p}")
    return list((json.load(open(p, encoding="utf-8")) or {}).get("contracts") or [])


def _signed(entry: dict[str, Any]) -> bool:
    r = entry.get("ratified") or {}
    return (r.get("state") == "SEEN_AND_SIGNED" and r.get("by") == "Mahmood" and bool(r.get("quote"))
            and bool(r.get("item"))
            and bool(_SHA256.fullmatch(str(r.get("packet_sha256") or "")))
            and bool(_SHA256.fullmatch(str(r.get("item_section_sha256") or ""))))


def signed(slug: str | None, outcome: str | None, *, path: str | None = None) -> dict[str, Any] | None:
    """The signed contract for (slug, outcome), or None. An unsigned or malformed entry is never honoured."""
    if not slug or not outcome:
        return None
    for e in _load(path):
        if e.get("slug") == slug and e.get("outcome") == outcome and _signed(e):
            return e
    return None
