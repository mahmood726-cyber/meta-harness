"""Read-only census. Run from any cwd; all evidence comes from this clone."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.measure_identity import (Measure, check_pool, normalize,
                                     protocol_specs, row_span, word_measures)


def census(root=ROOT):
    rules = {name: {"n": 0, "N": 0, "items": []} for name in
             ("served_scale_differs_from_protocol", "mixed_measure_pools", "span_scale_disagreement")}
    coverage = {"topics": 0, "reviews": 0, "missing_reviews": [],
                "unserved_outcomes": 0, "unknown_scale_or_target": [],
                "unknown_pool_rows": [], "ambiguous_span_rows": [], "rows_without_word_or_label": 0}
    for path in sorted((root / "topics").glob("*.json")):
        coverage["topics"] += 1
        config = json.loads(path.read_text(encoding="utf-8"))
        slug = path.stem
        review_path = root / "docs" / "reviews" / slug / "review.json"
        if not review_path.exists():
            coverage["missing_reviews"].append(slug)
            continue
        review = json.loads(review_path.read_text(encoding="utf-8"))
        coverage["reviews"] += 1
        specs = {s.get("name"): s for s in protocol_specs(config)}
        for index, outcome in enumerate(review.get("outcomes", [])):
            name = outcome.get("name", "<unnamed>")
            item = {"topic": slug, "outcome": name, "outcome_index": index}
            result = outcome.get("result") or {}
            active = (result.get("estimate") is not None and result.get("present") is not False
                      and not result.get("suppressed"))
            rows = outcome.get("trials") or []
            if active:
                rule = rules["served_scale_differs_from_protocol"]
                rule["N"] += 1
                target = normalize(specs.get(name, {}).get("estimand"))
                scale = normalize(result.get("measure") or result.get("scale"))
                if Measure.UNKNOWN in (target, scale):
                    coverage["unknown_scale_or_target"].append(item)
                if target != scale:
                    rule["items"].append({**item, "target": target.value, "served_label": scale.value,
                                          "protocol_estimand": specs.get(name, {}).get("estimand"),
                                          "result_scale": result.get("measure") or result.get("scale")})
                # A pool is a served multi-input outcome; singleton outcomes are
                # included above but cannot mix classes.
                if len(rows) >= 2:
                    rule = rules["mixed_measure_pools"]
                    rule["N"] += 1
                    problems = check_pool(rows, name)
                    for problem in problems:
                        if problem["code"] == "MEASURE_MIX_POOLED":
                            rule["items"].append({**item, "measures": problem["measures"], "rows": problem["rows"]})
                        else:
                            coverage["unknown_pool_rows"].append({**item, "rows": problem["rows"]})
            else:
                coverage["unserved_outcomes"] += 1
            for row_index, row in enumerate(rows):
                rule = rules["span_scale_disagreement"]
                rule["N"] += 1
                words = word_measures(row_span(row))
                label = normalize(row.get("measure") or row.get("scale"))
                row_item = {**item, "row_index": row_index, "row": str(row.get("id") or row.get("label") or row_index)}
                if len(words) > 1:
                    coverage["ambiguous_span_rows"].append(row_item)
                elif len(words) == 1 and label != Measure.UNKNOWN:
                    word = next(iter(words))
                    if word != label:
                        rule["items"].append({**row_item, "span_measure": word.value, "label_measure": label.value})
                else:
                    coverage["rows_without_word_or_label"] += 1
    for rule in rules.values():
        rule["n"] = len(rule["items"])
        rule["n_of_N"] = f"{rule['n']} of {rule['N']}"
    return {"rules": rules, "coverage": coverage}


if __name__ == "__main__":
    print(json.dumps(census(), indent=2, ensure_ascii=True))
