"""Sweep all served topics for hand parity status vs computed trial-set relation.

Writes docs/parity_relation_sweep.json. Topics without a parity row are named so
the denominator is the whole served corpus, not only the rows that happened to be
enumerated.
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import parity_relation  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build():
    docs = os.path.join(ROOT, "docs")
    rows_by_slug = {r.get("slug"): r for r in parity_relation.load_parity_rows(ROOT)}
    out_rows = []
    missing = []
    disagreements = []
    for rp in sorted(glob.glob(os.path.join(docs, "reviews", "*", "review.json"))):
        slug = os.path.basename(os.path.dirname(rp))
        review = json.load(open(rp, encoding="utf-8"))
        row = rows_by_slug.get(slug)
        if not row:
            missing.append(slug)
            out_rows.append({"slug": slug, "has_parity_row": False})
            continue
        enriched = parity_relation.enrich(row, review, strict=False)
        rel = enriched["parity_relation"]
        rec = {
            "slug": slug,
            "has_parity_row": True,
            "hand_status": row.get("status"),
            "computed_relation": rel.get("relation"),
            "computed_label": rel.get("label"),
            "hand_status_disagrees": rel.get("hand_status_disagrees"),
            "our_k": rel.get("our_k"),
            "their_k": rel.get("their_k"),
            "their_k_source": rel.get("their_k_source"),
        }
        out_rows.append(rec)
        if rel.get("hand_status_disagrees"):
            disagreements.append(slug)
    return {
        "n_topics": len(out_rows),
        "n_with_parity_row": sum(1 for r in out_rows if r.get("has_parity_row")),
        "n_without_parity_row": len(missing),
        "topics_without_parity_row": missing,
        "n_disagreements": len(disagreements),
        "disagreement_denominator": len(out_rows),
        "disagreement_slugs": disagreements,
        "rows": out_rows,
    }


if __name__ == "__main__":
    data = build()
    out = os.path.join(ROOT, "docs", "parity_relation_sweep.json")
    with open(out, "w", encoding="utf-8", newline="") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(
        f"parity relation disagreements: {data['n_disagreements']} of "
        f"{data['disagreement_denominator']} topics; "
        f"without parity row: {data['n_without_parity_row']}"
    )
