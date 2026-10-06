"""Derive an OPEN result-change notice for EVERY served outcome that changes between the served base and the candidate
build (docs/reviews/<slug>/review.json), not only the headline outcome. Each notice names both results, every row that
left or entered, and the cause the captain states for that topic (--cause slug=text). Existing notices that already name
the exact change are never duplicated. Derived, never applied: signing_packet.py builds the packet; the guard refuses a
packet that leaves out any changed outcome.

    python scripts/derive_outcome_notices.py --base origin/main --cause dpp4-mace-t2d="..." [--write] <slug> ...
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from harness import result_changes as rc  # noqa: E402
import signing_packet as sp  # noqa: E402


def derive(slugs, base_ref, causes):
    notices = rc.load(ROOT)
    out = []
    for slug in slugs:
        for ch in sp.served_outcome_changes(sp.Path(ROOT), slug, base_ref):
            if rc.notice_for([n for n in notices if not rc.not_applied(n)], slug, ch["outcome"], ch["before"],
                             ch["after"], ch["left_pool"], ch["entered_pool"]):
                continue
            cause = causes.get(slug)
            if not cause:
                raise SystemExit(f"REFUSED: {slug} / {ch['outcome']} changes and no --cause is stated for {slug}")
            moved = []
            if ch["entered_pool"]:
                moved.append("entered the pool: " + ", ".join(ch["entered_pool"]))
            if ch["left_pool"]:
                moved.append("left the pool: " + ", ".join(ch["left_pool"]))
            out.append({"slug": slug, "outcome": ch["outcome"], "before": ch["before"], "after": ch["after"],
                        "left_pool": ch["left_pool"], "entered_pool": ch["entered_pool"],
                        "reason": f"{cause} " + ("; ".join(moved) + "." if moved else
                                                 "No row entered or left; the pooled number changed with the rows' values."),
                        "by": "Claude Opus 5.5 (captain lane, derive_outcome_notices.py); reviewer countersignature owed: Mahmood",
                        "when_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "reviewer_countersignature": {"state": "OPEN", "note": "the reviewer has not yet seen the rendered notice"}})
    return out


def main(argv):
    base = argv[argv.index("--base") + 1] if "--base" in argv else "origin/main"
    causes = {}
    for i, a in enumerate(argv):
        if a == "--cause":
            k, v = argv[i + 1].split("=", 1)
            causes[k] = v
    skip = {i + 1 for i, a in enumerate(argv) if a in ("--base", "--cause")}
    slugs = [a for i, a in enumerate(argv) if not a.startswith("--") and i not in skip]
    new = derive(slugs, base, causes)
    for n in new:
        print(f"{n['slug']} / {n['outcome']}: {n['before']} -> {n['after']} | entered {n['entered_pool']} left {n['left_pool']}")
    if "--write" in argv and new:
        p = os.path.join(ROOT, "docs", "result_changes.json")
        d = json.load(open(p, encoding="utf-8"))
        d["notices"] += new
        open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
        print("appended", len(new), "OPEN notices")


if __name__ == "__main__":
    main(sys.argv[1:])
