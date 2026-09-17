"""Offline measurement of held pools; never rebuilds or edits served pages."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import effect_type as ty


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sweep(root=ROOT, write_types=False):
    topics = []
    for path in sorted((root / "docs/reviews").glob("*/review.json")):
        slug = path.parent.name
        review = read(path)
        config = read(root / "topics" / (slug + ".json"))
        records = read(root / "cache" / slug / "records.json")
        by_id = {str(r["id"]): r for r in records["records"]}
        protocol = (root / "protocols" / (slug + ".md")).read_text(encoding="utf-8")
        coercions = ty.load_coercions(root / "cache" / slug / "coercions.json")
        specs = [dict(config["primary_outcome"], primary=True)] + config.get("secondary_outcomes", []) + config.get("harm_outcomes", [])
        measured, outcomes = [], []
        for o in review.get("outcomes", []):
            res = o.get("result") or {}
            if res.get("present") is False or res.get("suppressed_incompatible") or not res.get("k"):
                continue
            spec = next((s for s in specs if s["name"] == o["name"]), o)
            target = ty.protocol_target(spec, protocol)
            kept, refused, effects = ty.type_rows(o.get("trials", []), target, by_id, coercions)
            for e in effects:
                measured.append(dict(e, outcome=o["name"], primary=o.get("primary", False),
                                     unknown_binding_axes=[a for a in target["binding_axes"] if a in e["unknown_axes"]]))
            outcomes.append({"name": o["name"], "effect_type_target": target, "effect_types": effects})
        n = len(measured)
        full = sum(e["known_axes"] == 12 for e in measured)
        unknown = sum(bool(e["unknown_binding_axes"]) for e in measured)
        refused = sum(e["unification"]["status"] not in ty.ACCEPTED for e in measured)
        summary = {"N": n, "denominator": "candidate effect rows in currently served, non-suppressed pooled outcomes",
                   "fully_typed": full, "unknown_binding": unknown, "would_be_refused": refused}
        inputs = [path, root / "topics" / (slug + ".json"), root / "cache" / slug / "records.json",
                  root / "protocols" / (slug + ".md")]
        topics.append({"slug": slug,
                       "input_sha256": {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
                       "before": summary,
                       "after": dict(summary, accepted_on_rebuild=n-refused,
                                     note="Same held evidence after typing; no page rebuild performed."),
                       "rows": measured, "targets": [{"outcome": o["name"], **o["effect_type_target"]} for o in outcomes]})
        if write_types:
            ty.persist(root / "cache" / slug / "effect_types.json", outcomes)
    return {"classification": "MEASURED from held bytes; rebuild acceptance is a dry-run unification result",
            "topic_count": len(topics), "pages_modified": False,
            "summary": {k: sum(t["before"][k] for t in topics) for k in ("N", "fully_typed", "unknown_binding", "would_be_refused")},
            "topics": topics}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--write-types", action="store_true")
    args = p.parse_args()
    data = sweep(write_types=args.write_types)
    (ROOT / "docs/effect_type_sweep.json").write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"topics": data["topic_count"], **data["summary"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
