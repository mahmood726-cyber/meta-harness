"""Re-derive stored registry-machine risk-of-bias signals over the served corpus.

Writes docs/rob_rederivation_sweep.json when run with --write.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from harness import embed, rob2  # noqa: E402


def _match(a, b):
    ranked = embed.rank(a, [b])
    return bool(ranked) and ranked[0][1] >= 0.45


def _review_slugs() -> list[str]:
    base = os.path.join(ROOT, "docs", "reviews")
    return [
        slug for slug in sorted(os.listdir(base))
        if os.path.exists(os.path.join(base, slug, "review.json"))
    ]


def sweep() -> dict:
    topics = []
    ratings = []
    violations = []
    by_domain = Counter()
    bad_by_domain = Counter()
    for slug in _review_slugs():
        path = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
        review = json.load(open(path, encoding="utf-8"))
        topics.append(slug)
        for trial_id, entry in (((review.get("rob2") or {}).get("trials") or {}).items()):
            for domain_id in rob2.MACHINE_DOMAINS:
                stored = ((entry or {}).get("domains") or {}).get(domain_id)
                if not stored:
                    continue
                by_domain[domain_id] += 1
                rec = {
                    "topic": slug,
                    "trial": trial_id,
                    "nct": entry.get("nct"),
                    "domain": domain_id,
                    "rule_id": stored.get("rule_id"),
                    "stored_level": stored.get("level"),
                    "stored_basis": stored.get("basis"),
                    "inputs": stored.get("inputs"),
                }
                try:
                    expected = rob2.rederive_domain(stored, _match)
                    rec["rederived_level"] = expected.get("level")
                    rec["rederived_basis"] = expected.get("basis")
                    rec["reproducible"] = expected.get("level") == stored.get("level")
                except Exception as exc:  # noqa: BLE001 - recorded in artefact
                    rec["rederived_level"] = None
                    rec["rederived_basis"] = None
                    rec["reproducible"] = False
                    rec["error"] = str(exc)
                ratings.append(rec)
                if not rec["reproducible"]:
                    bad_by_domain[domain_id] += 1
                    violations.append(rec)
    return {
        "measurement": "registry-machine risk-of-bias re-derivation sweep",
        "output_family": rob2.OUTPUT_FAMILY,
        "topics_n": len(topics),
        "topics": topics,
        "machine_domains": list(rob2.MACHINE_DOMAINS),
        "ratings_total": len(ratings),
        "not_reproducible_total": len(violations),
        "ratings_by_domain": dict(sorted(by_domain.items())),
        "not_reproducible_by_domain": dict(sorted(bad_by_domain.items())),
        "not_reproducible": violations,
        "ratings": ratings,
    }


def main(argv: list[str]) -> int:
    data = sweep()
    if "--write" in argv:
        path = os.path.join(ROOT, "docs", "rob_rederivation_sweep.json")
        with open(path, "w", encoding="utf-8", newline="") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"wrote docs/rob_rederivation_sweep.json")
    print(
        f"{data['not_reproducible_total']} ratings not reproducible from their own rule of "
        f"{data['ratings_total']} machine ratings over {data['topics_n']} topics"
    )
    for domain, total in data["ratings_by_domain"].items():
        print(f"{domain}: {data['not_reproducible_by_domain'].get(domain, 0)} of {total}")
    return 0 if data["not_reproducible_total"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
