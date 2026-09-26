"""Which regex sites this lane may hold strictly. Plants and labelling specs cover every harness regex site, but only
the files this lane owns (regex_layer/sites_without_plants.json: owned_files, decided in regex_layer/OWNERSHIP.md) are
held strictly. In the other lane's files a plant describes the site as it was read; when that lane edits or removes a
pattern, the plant is reported STALE and skipped -- it never fails that lane's commit -- and a new site there is not a
failure either. Measuring another lane's code must never become a gate on it.
"""
from __future__ import annotations

import functools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNED = tuple(json.loads((ROOT / "regex_layer" / "sites_without_plants.json").read_text(encoding="utf-8"))["owned_files"])


@functools.lru_cache(maxsize=1)
def current_sites() -> frozenset:
    from regex_layer.inventory import sites
    return frozenset(s["site"] for s in sites())


def owned(site: str) -> bool:
    return site.split(":", 1)[0] in OWNED


def stale_reason(site: str) -> str | None:
    """None when the site is held (owned, or unchanged since it was planted); else why its plant is skipped."""
    if owned(site) or site in current_sites():
        return None
    return (f"STALE: {site} is no longer in harness/ as planted -- the owning lane changed or removed the pattern; "
            "the plant is skipped, never a failure of that lane's commit, and is re-planted from regex_layer/")
