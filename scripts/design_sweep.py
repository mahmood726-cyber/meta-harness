"""Write the design-key sweep over the served review objects.

Usage: python scripts/design_sweep.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "docs" / "reviews"
OUT = ROOT / "docs" / "evidence" / "design-key-2026-09-14" / "01-sweep-32.txt"


def _trial_name(t: dict) -> str:
    known = {"29485925": "SMART", "27749094": "SALT", "26444692": "SPLIT",
             "34375394": "BaSICS", "21115589": "Alpha Omega"}
    raw = str(t.get("id") or t.get("label") or "")
    pid = raw.replace("PMID ", "").replace("PMID:", "").strip()
    return known.get(pid) or str(t.get("label") or raw)


def _direction(design: str) -> str:
    if design == "CLUSTER":
        return "OPTIMISTIC"
    if design == "CLUSTER_CROSSOVER":
        return "OPTIMISTIC"
    if design == "CROSSOVER":
        return "PESSIMISTIC"
    if design == "STEPPED_WEDGE":
        return "OPTIMISTIC"
    if design in {"PARALLEL", "FACTORIAL"}:
        return "NONE"
    return "UNKNOWN"


def _basis_sources(d: dict) -> str:
    return "; ".join(str(b.get("source")) for b in (d.get("basis") or []) if b.get("source")) or "NONE"


def _row(slug: str, t: dict, refused: bool) -> str:
    d = t.get("design") or {}
    design = d.get("design") or "UNKNOWN"
    corr = d.get("correlation_handling") or {}
    action = (d.get("design_action") or {}).get("action") or "UNKNOWN"
    return " | ".join([
        slug,
        _trial_name(t),
        design,
        d.get("unit_of_randomisation") or "UNKNOWN",
        d.get("estimator_source") or "UNKNOWN",
        corr.get("method") or "UNKNOWN",
        action,
        t.get("derivation") or ("reconstructed" if d.get("estimator_source") == "RECONSTRUCTED" else "UNKNOWN"),
        "YES" if refused else "NO",
        _direction(design),
        _basis_sources(d),
    ])


def main() -> int:
    lines = [
        "AACT intervention_model: sees factorial/crossover/parallel where the registration states it; blind to cluster randomisation and to unregistered trials.",
        "Abstract/title text: sees only strong design phrases listed in harness.unit_of_analysis; blind to designs stated only in full text.",
        "Both methods are blind to a trial with no committed source; UNKNOWN means not observed, not safe parallel.",
        "",
        "slug | trial | design | unit | estimator_source | correlation_method | typed_action | derivation | refused? | naive-error-direction | basis_sources",
    ]
    topics_nonparallel: dict[str, set[str]] = {}
    refused_trials: set[str] = set()
    unknown_trials: set[str] = set()
    topics_seen: set[str] = set()
    unknown_by_topic: dict[str, set[str]] = {}
    basics_source = "NOT_FOUND"
    n_rows = 0

    for review_path in sorted(REVIEWS.glob("*/review.json")):
        slug = review_path.parent.name
        topics_seen.add(slug)
        review = json.loads(review_path.read_text(encoding="utf-8"))
        for outcome in review.get("outcomes") or []:
            for t in outcome.get("trials") or []:
                n_rows += 1
                d = t.get("design") or {}
                design = d.get("design") or "UNKNOWN"
                if design not in {"PARALLEL", "UNKNOWN"}:
                    topics_nonparallel.setdefault(slug, set()).add(_trial_name(t))
                if design == "UNKNOWN":
                    unknown_trials.add(f"{slug}:{_trial_name(t)}")
                    unknown_by_topic.setdefault(slug, set()).add(_trial_name(t))
                if _trial_name(t) == "BaSICS":
                    basics_source = _basis_sources(d)
                lines.append(_row(slug, t, refused=False))
            for t in outcome.get("declared_absent_trials") or []:
                if not t.get("design"):
                    continue
                n_rows += 1
                d = t.get("design") or {}
                design = d.get("design") or "UNKNOWN"
                if design not in {"PARALLEL", "UNKNOWN"}:
                    topics_nonparallel.setdefault(slug, set()).add(_trial_name(t))
                if design == "UNKNOWN":
                    unknown_trials.add(f"{slug}:{_trial_name(t)}")
                    unknown_by_topic.setdefault(slug, set()).add(_trial_name(t))
                refused_trials.add(f"{slug}:{_trial_name(t)}")
                lines.append(_row(slug, t, refused=True))

    topic_bits = [f"{slug} ({', '.join(sorted(names))})" for slug, names in sorted(topics_nonparallel.items())]
    observed_topics = set(topics_nonparallel)
    no_design_only_topics = sorted(topics_seen - observed_topics)
    not_registry_swept_topics: list[str] = []
    unknown_bits = [f"{slug} ({', '.join(sorted(names))})" for slug, names in sorted(unknown_by_topic.items())]
    summary = [
        "",
        f"SUMMARY rows={n_rows}",
        "prevalence UNKNOWN: "
        f"{len(topics_nonparallel)} topics observed non-parallel by AACT intervention_model and/or committed title-abstract text: "
        + (", ".join(topic_bits) if topic_bits else "none")
        + f"; {len(unknown_trials)} trial-topic pairs with no design evidence: "
        + (", ".join(sorted(unknown_trials)) if unknown_trials else "none")
        + f"; {len(not_registry_swept_topics)} topics not yet swept by registry design fields: "
        + (", ".join(not_registry_swept_topics) if not_registry_swept_topics else "none"),
        "full topic accounting (exclusive; prevalence still UNKNOWN): "
        f"observed_non_parallel_topics={len(observed_topics)} "
        + (", ".join(sorted(observed_topics)) if observed_topics else "none")
        + f"; no_design_evidence_only_topics={len(no_design_only_topics)} "
        + (", ".join(no_design_only_topics) if no_design_only_topics else "none")
        + f"; not_yet_registry_swept_topics={len(not_registry_swept_topics)} "
        + (", ".join(not_registry_swept_topics) if not_registry_swept_topics else "none")
        + f"; accounting_sum={len(observed_topics) + len(no_design_only_topics) + len(not_registry_swept_topics)}",
        f"{len(refused_trials)} trials refused: " + (", ".join(sorted(refused_trials)) if refused_trials else "none"),
        f"{len(unknown_trials)} trial-topic pairs UNKNOWN: " + (", ".join(sorted(unknown_trials)) if unknown_trials else "none"),
        "UNKNOWN by topic: " + (", ".join(unknown_bits) if unknown_bits else "none"),
        f"BaSICS factorial found_by: {basics_source}",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines + summary) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
