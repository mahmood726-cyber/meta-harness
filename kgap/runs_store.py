"""RUN LEDGER for recorded model calls of the secondary tier, ONE FILE PER TOPIC. SHARED G1 INTERFACE.

Several lanes build topics on top of acq/k-gap at once. A single registry/secondary_meta/runs.json written by every build
made every pair of lanes conflict on merge. The ledger is the same dict as before ({key: run}), stored as
registry/secondary_meta/runs/<topic>.json, where <topic> is the slug the key belongs to:

    "<slug>::<meta_pmid>"            a forest-figure read            -> runs/<slug>.json
    "locate::<slug>::<trial_pmid>"   a primary-value locator call    -> runs/<slug>.json
    "audit::<slug>::<trial label>"   an independent audit re-read    -> runs/<slug>.json
    anything else                    -> runs/_other.json

    load()                 every topic's runs merged into one dict (what the build has always taken)
    save(runs, slugs=None) write back only the topic files whose content changed (only `slugs` when given), so a
                           lane building NOAC never rewrites the GLP-1 file
"""
from __future__ import annotations

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS_DIR = os.path.join(ROOT, "registry", "secondary_meta", "runs")
_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def topic_of(key: str) -> str:
    parts = str(key).split("::")
    slug = parts[1] if parts[0] in ("locate", "audit", "swapscreen", "swapscreenA", "swapenum") and len(parts) > 2 else parts[0]
    return slug if (_SLUG.match(slug) and len(parts) > 1) else "_other"


def _path(topic):
    return os.path.join(RUNS_DIR, f"{topic}.json")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def load() -> dict:
    out = {}
    if os.path.isdir(RUNS_DIR):
        for f in sorted(os.listdir(RUNS_DIR)):
            if f.endswith(".json"):
                out.update(_j(os.path.join(RUNS_DIR, f)))
    return out


def save(runs: dict, slugs=None) -> list:
    """Returns the topic files written."""
    by = {}
    for k, v in runs.items():
        by.setdefault(topic_of(k), {})[k] = v
    wrote = []
    os.makedirs(RUNS_DIR, exist_ok=True)
    for topic, d in sorted(by.items()):
        if slugs is not None and topic not in slugs:
            continue
        p = _path(topic)
        # MERGE, never replace: a caller holding a stale dict (loaded before another process saved) must not delete the
        # entries written in between. Its own entries win on a shared key (it ran those calls most recently).
        on_disk = _j(p) if os.path.exists(p) else {}
        merged = {**on_disk, **d}
        if merged == on_disk:
            continue
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(dict(sorted(merged.items())), fh, indent=1, ensure_ascii=False)
        os.replace(tmp, p)
        wrote.append(p)
    return wrote
