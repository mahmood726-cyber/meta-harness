"""Measure proposition contradictions before and after the CG2 fix."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import propositions  # noqa: E402


PREFIX = "ad5e7c66"


def _git_json(ref: str, path: str) -> dict:
    data = subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT)
    return json.loads(data)


def _prefix_slugs(ref: str) -> list[str]:
    out = subprocess.check_output(
        ["git", "ls-tree", "-d", "--name-only", f"{ref}:docs/reviews"],
        cwd=ROOT,
        text=True,
    )
    return sorted(x for x in out.splitlines() if x.strip())


def _summarize(items: dict[str, list[dict]]) -> dict:
    by_code: Counter[str] = Counter()
    pages_by_code: dict[str, list[str]] = {}
    for slug, violations in items.items():
        seen = set()
        for violation in violations:
            code = str(violation.get("code"))
            by_code[code] += 1
            seen.add(code)
        for code in seen:
            pages_by_code.setdefault(code, []).append(slug)
    return {
        "pages_with_violations": sum(1 for v in items.values() if v),
        "by_code_occurrences": dict(sorted(by_code.items())),
        "pages_by_code": {k: sorted(v) for k, v in sorted(pages_by_code.items())},
        "per_page": {slug: [v.get("code") for v in violations] for slug, violations in sorted(items.items()) if violations},
    }


def main() -> int:
    prefix_slugs = _prefix_slugs(PREFIX)
    pre = {
        slug: propositions.check_propositions(_git_json(PREFIX, f"docs/reviews/{slug}/review.json"))
        for slug in prefix_slugs
    }
    current_paths = sorted((ROOT / "docs" / "reviews").glob("*/review.json"))
    post = {
        p.parent.name: propositions.check_propositions(json.loads(p.read_text(encoding="utf-8")))
        for p in current_paths
    }
    doc = {
        "prefix_ref": PREFIX,
        "postfix_source": "workspace docs/reviews after CG2 rebuild",
        "denominator_pages": len(prefix_slugs),
        "pre_fix": _summarize(pre),
        "post_fix": _summarize(post),
        "plants": {
            "publication_bias_state": [
                "sglt2-ckd-progression",
                "colchicine-secondary-cv-prevention",
                "metformin-pcos-ovulation",
            ],
            "declared_equals_enforced": [
                "sglt2-ckd-progression",
                "sglt2-primary-prevention-hf",
                "colchicine-secondary-cv-prevention",
                "metformin-pcos-ovulation",
            ],
            "byte_reproducible": "all 32 prefix pages",
            "pooled_count": ["sglt2-primary-prevention-hf", "esketamine-trd-madrs"],
            "search_found": ["colchicine-postop-af"],
            "refused_and_pooled": "aa8ed28a metformin-pcos-ovulation is covered by tests/test_propositions.py",
            "controls": ["esketamine monotherapy exclusion", "omega3 endpoint-identity refusal"],
            "synthetic_clean": "tests/test_propositions.py::test_synthetic_clean_page_has_no_proposition_violation",
        },
    }
    out = ROOT / "docs" / "proposition_sweep.json"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="")
    print(f"wrote {out.relative_to(ROOT)}")
    print(f"pre_fix {doc['pre_fix']['pages_with_violations']} of {doc['denominator_pages']} pages")
    print(f"post_fix {doc['post_fix']['pages_with_violations']} of {len(post)} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
