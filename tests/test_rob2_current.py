"""Every committed cache/<slug>/rob2.json describes the review it is served with (8 Oct): its recorded input set (the
primary outcome name and pooled trials) equals the review's, and it rates exactly the pooled trials. Before this, 7
topics' RoB objects were stale against reviews rebuilt since 17 Sep (outputs/d11/ROB_DRIFT.md) and nothing failed."""
from __future__ import annotations

import glob
import json
import os

from harness import rob2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_every_committed_rob_object_is_current():
    bad = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "cache", "*", "rob2.json"))):
        slug = os.path.basename(os.path.dirname(p))
        rp = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
        if not os.path.exists(rp):
            continue
        reasons = rob2.staleness(json.load(open(rp, encoding="utf-8")), json.load(open(p, encoding="utf-8")))
        if reasons:
            bad[slug] = reasons
    assert bad == {}
