"""Measure (never change) how often a served X1 exclusion says "not a randomized controlled trial" while the span it
cites as evidence lists the publication type "Randomized Controlled Trial" -- and name the clause of
harness.screen._is_rct that actually fired. Read-only: reads docs/reviews/*/review.json and cache/*/records.json.

Found 2026-09-24 on COPPS AF (PMID 22090167, colchicine-postop-af): reason "not a randomized controlled trial", span
"publication types: ... Randomized Controlled Trial ...", real trigger the title word "substudy".
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import screen  # noqa: E402


def trigger(rec: dict) -> str:
    title = rec.get("title") or ""
    text = (rec.get("abstract") or "") + " " + title
    pts = [p.lower() for p in rec.get("pubtypes", [])]
    if screen._is_review(rec):
        return "review"
    if any(any(np in p for np in screen._NONPRIMARY_PT) for p in pts):
        return "non-primary publication type"
    m = screen._QUASI.search(text)
    if m:
        return "quasi-allocation: " + m.group(0).lower()
    m = screen._TITLE_RCT_NOT.search(title)
    if m:
        return "title word: " + m.group(0).lower()
    return "other"


def measure() -> dict:
    n, rows, by = 0, [], collections.Counter()
    for p in sorted((ROOT / "docs" / "reviews").glob("*/review.json")):
        slug = p.parent.name
        review = json.loads(p.read_text(encoding="utf-8"))
        recs = None
        for x in (review.get("screening") or {}).get("records") or []:
            if x.get("rule_id") != "X1":
                continue
            n += 1
            if "randomized controlled trial" not in (x.get("span") or "").lower():
                continue
            if recs is None:
                recs = {str(y.get("id")): y for y in
                        json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8"))["records"]}
            t = trigger(recs.get(str(x["id"])) or {})
            by[t.split(":")[0]] += 1
            rows.append({"slug": slug, "id": x["id"], "trigger": t})
    return {"x1_exclusions": n, "reason_contradicts_span": len(rows), "by_trigger": dict(by.most_common()), "rows": rows}


if __name__ == "__main__":
    out = measure()
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in out["rows"][:40]:
        print(f"  {r['slug']}  {r['id']}  {r['trigger']}")
