"""Sweep comparator-truth checks over served review objects."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import comparator_truth  # noqa: E402


OUT = ROOT / "docs" / "comparator_truth_sweep.json"


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _topic_config(slug: str) -> dict:
    path = ROOT / "topics" / f"{slug}.json"
    return _read_json(path) if path.is_file() else {}


def _review_paths() -> list[Path]:
    return sorted((ROOT / "docs" / "reviews").glob("*/review.json"))


def run() -> dict:
    pages = []
    n_recon_denom = 0
    n_recon_refuted = 0
    value_total = 0
    value_missing = 0
    recency_refuted = 0

    for path in _review_paths():
        review = _read_json(path)
        slug = str(review.get("slug") or path.parent.name)
        comp = review.get("comparator") or {}
        text = comparator_truth.load_cached_comparator_text(
            str(ROOT), slug, comp.get("pmid"), ""
        )
        truth = comparator_truth.assess_review(slug, review, _topic_config(slug), text)
        nrec = truth.get("participant_reconciliation") or {}
        if nrec.get("code") not in (None, "NOT_ASSESSED", "N_NOT_IN_HELD_TEXT", "OURS_N_NOT_COMPUTABLE"):
            n_recon_denom += 1
            if nrec.get("code") == "PARITY_REFUTED_BY_N":
                n_recon_refuted += 1
        spans = truth.get("rendered_comparator_value_spans") or []
        value_total += len(spans)
        value_missing += sum(1 for row in spans if row.get("status") != "FOUND")
        recency = truth.get("recency") or {}
        predates = recency.get("predates") or []
        if predates:
            recency_refuted += 1
        pages.append(
            {
                "slug": slug,
                "pmid": comp.get("pmid"),
                "participant_reconciliation": nrec,
                "agent_scope": truth.get("agent_scope"),
                "completeness": truth.get("completeness"),
                "recency": recency,
                "rendered_values_total": len(spans),
                "rendered_values_without_span": sum(1 for row in spans if row.get("status") != "FOUND"),
                "rendered_value_spans": spans,
            }
        )

    out = {
        "_doc": (
            "Comparator-truth sweep: participant-n reconciliation, rendered comparator value spans, "
            "and comparator recency versus named eligible trials. All comparator values are located in "
            "held cache text or marked NOT_IN_HELD_TEXT."
        ),
        "summary": {
            "parity_or_overlap_refuted_by_n_reconciliation": {
                "n": n_recon_refuted,
                "N": n_recon_denom,
                "denominator": "pages with comparator n in held text and our participant n computable",
            },
            "rendered_comparator_values_without_span": {
                "n": value_missing,
                "N": value_total,
                "denominator": "rendered comparator numeric values swept from comparator.reported and comparator.overlap/truth",
            },
            "comparators_predating_known_eligible_trial": {
                "n": recency_refuted,
                "N": len(pages),
                "denominator": "served review pages",
            },
        },
        "pages": pages,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(
        "comparator truth sweep: "
        f"n-refuted {n_recon_refuted}/{n_recon_denom}; "
        f"rendered values without span {value_missing}/{value_total}; "
        f"predating known eligible {recency_refuted}/{len(pages)}"
    )
    return out


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
