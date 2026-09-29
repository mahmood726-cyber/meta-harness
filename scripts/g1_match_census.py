"""Deterministic offline G1 census; every numerator has named items."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from harness.comparator_extract import extract
from harness.meta_match import match


def census(root=ROOT):
    root = Path(root)
    topics = sorted((root / "topics").glob("*.json"))
    sets, ks, kmatch, errors, trial_items, proposals = [], [], [], [], [], []
    for topic in topics:
        slug = topic.stem
        try:
            c = extract(slug, root)
        except (ValueError, OSError, UnicodeError) as exc:
            errors.append({"item": slug, "reason": str(exc)})
            continue
        if c["trial_set"]:
            sets.append(slug)
        if c["pooled"]["k"]["status"] == "PARSED":
            ks.append(slug)
        proposals.append({"item": slug, "proposals": len(c["proposals"]), "parsed_rows": len(c["trial_set"])})
        path = root / "docs/reviews" / slug / "review.json"
        if not path.exists():
            errors.append({"item": slug, "reason": "REFUSED_MISSING_REVIEW"})
            continue
        result = match(json.loads(path.read_text(encoding="utf-8")), c)
        if result["K_MATCH"] == "yes":
            kmatch.append(slug)
        for i, row in enumerate(result["trials"]):
            trial_items.append({"item": f"{slug}::{row['label']}::{i}", **row})
    def metric(items, denominator):
        return {"n": len(items), "N": denominator, "n_of_N": f"{len(items)} of {denominator}", "items": items}
    ncomp = sum(r["side"] == "comparator" for r in trial_items)
    nours = sum(r["side"] == "ours" for r in trial_items)
    rules = {}
    for status in ("MATCH", "VALUE_DIFFERS", "MISSING_FROM_OURS", "EXTRA_IN_OURS", "ABSTAIN"):
        selected = [r for r in trial_items if r["status"] == status]
        rules[status] = metric(selected, nours if status == "EXTRA_IN_OURS" else len(trial_items) if status == "ABSTAIN" else ncomp)
        for reason in sorted({r.get("reason") or r.get("our_state") for r in selected} - {None}):
            rules[status + "/" + reason] = metric([r for r in selected if (r.get("reason") or r.get("our_state")) == reason], ncomp if status != "ABSTAIN" else len(trial_items))
    return {"denominator_note": "Topics includes absent/unheld comparator panels. Trial comparator N includes primary-bound and outcome-unresolved rows; secondary-bound rows excluded. EXTRA N is unmatched ours rows; incomplete comparator membership abstains.", "parsed_trial_set": metric(sets, len(topics)), "parsed_pooled_k": metric(ks, len(topics)), "K_MATCH": metric(kmatch, len(topics)), "rules": rules, "refusals": errors, "proposal_counts": proposals}


if __name__ == "__main__":
    print(json.dumps(census(), ensure_ascii=False, indent=2, sort_keys=True))
