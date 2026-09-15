"""Write the hazard-consumer sweep evidence bundle.

The pre-wiring sweep reads review.json files from the supplied base ref and
annotates them in PHASE_BASE, so it stays reproducible after the lane wiring is
present in the working tree.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import hazard_consumers  # noqa: E402
from harness.page import render_page  # noqa: E402


EVIDENCE_DIR = ROOT / "docs" / "evidence" / "hazard-consumers-2026-09-14"
HAZARD_SEVERITIES = {"BLOCKS_CLAIM", "QUALIFIES_CLAIM"}


def _git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise SystemExit(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout.strip()


def _head() -> str:
    return _git(["rev-parse", "HEAD"])


def _clean(value: Any) -> str:
    return " ".join(str(value if value is not None else "").replace("|", "/").split())


def _base_reviews(ref: str) -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    for rel in hazard_consumers.review_paths_at_ref(ref):
        review = hazard_consumers.load_review_at_ref(ref, rel)
        if review is not None:
            reviews.append(review)
    return sorted(reviews, key=lambda r: str(r.get("slug") or ""))


def _worktree_reviews() -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    for path in sorted((ROOT / "docs" / "reviews").glob("*/review.json")):
        try:
            reviews.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"cannot read {path.relative_to(ROOT)}: {exc}") from exc
    return sorted(reviews, key=lambda r: str(r.get("slug") or ""))


def _rows(reviews: list[dict[str, Any]], phase: str) -> list[dict[str, str]]:
    acknowledgements = hazard_consumers.load_acknowledgements()
    rows: list[dict[str, str]] = []
    for review in reviews:
        slug = str(review.get("slug") or "")
        for obj in review.get("limitations") or []:
            if not isinstance(obj, dict):
                continue
            ann = hazard_consumers.annotate_object(review, obj, acknowledgements, phase)
            consumer = ann.get("consumer")
            wired = isinstance(consumer, dict)
            rows.append({
                "slug": slug,
                "limitation_id": str(ann.get("limitation_id") or ""),
                "kind": str(ann.get("kind") or ""),
                "severity": str(ann.get("severity") or ""),
                "evidence_state": str(ann.get("evidence_state") or ""),
                "consumer_gate": str(consumer.get("gate_id") if wired else "null"),
                "gate_verdict_at_build": str(consumer.get("gate_verdict_at_build") if wired else "null"),
                "status": "WIRED" if wired else "UNWIRED",
                "acknowledged": "ACKNOWLEDGED" if ann.get("unwired_acknowledged") else "",
            })
    return rows


def _unwired_hazards(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row for row in rows
        if row["status"] == "UNWIRED" and row["severity"] in HAZARD_SEVERITIES
    ]


def _pair(row: dict[str, str]) -> tuple[str, str]:
    return row["kind"], row["evidence_state"]


def _pair_list(rows: list[dict[str, str]]) -> str:
    pairs = sorted({_pair(row) for row in rows})
    return ", ".join(f"({kind},{state})" for kind, state in pairs) or "none"


def _topic_list(rows: list[dict[str, str]]) -> str:
    topics = sorted({row["slug"] for row in rows})
    return ", ".join(topics) or "none"


def _write_table(path: Path, intro: list[str], rows: list[dict[str, str]]) -> None:
    fields = [
        "slug",
        "limitation_id",
        "kind",
        "severity",
        "evidence_state",
        "consumer_gate",
        "gate_verdict_at_build",
        "status",
    ]
    lines = intro + ["", " | ".join(fields)]
    lines.extend(" | ".join(_clean(row.get(field, "")) for field in fields) for row in rows)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


def _write_01(base_ref: str, before: list[dict[str, str]]) -> None:
    unwired = _unwired_hazards(before)
    n_topics = len({row["slug"] for row in before})
    n_unwired_topics = len({row["slug"] for row in unwired})
    intro = [
        "Hazard consumer sweep, before lane AD wiring",
        f"base_ref: {base_ref}",
        f"rows: {len(before)}",
        f"SUMMARY: {n_unwired_topics} of {n_topics} topics with at least one UNWIRED hazard severity BLOCKS_CLAIM or QUALIFIES_CLAIM: {_topic_list(unwired)}",
        f"UNWIRED hazard pairs: {_pair_list(unwired)}",
    ]
    _write_table(EVIDENCE_DIR / "01-sweep-32.txt", intro, before)


def _plant_uoa_obj() -> dict[str, Any]:
    return {
        "limitation_id": "topic:plant:riskofbias:unit-of-analysis",
        "kind": "UNIT_OF_ANALYSIS",
        "limitation_class": "VALIDITY_THREATENING",
        "severity": "QUALIFIES_CLAIM",
        "claim_affected": "primary pooled variance and precision",
        "evidence_state": "NOT_ASSESSED",
        "source_fields": ["/unit_of_analysis"],
        "rendered_text": "<div class='absent'>unit of analysis plant</div>",
        "text_sha256": "plant",
        "linked_decision": {
            "action": "ALLOW_WITH_LABEL",
            "gate_id": "limitation:unit-of-analysis",
            "decision_state": "design state is labelled",
        },
        "consumer": None,
        "unwired": True,
    }


def _write_02() -> None:
    lines = [
        "Hazard consumer executable plants",
        "",
        "kind | evidence_state | gate_id | gate_function | gate_input_path | baseline | planted | changed",
    ]
    for row in hazard_consumers.plant_results():
        lines.append(
            " | ".join(
                _clean(row.get(field, ""))
                for field in [
                    "kind",
                    "evidence_state",
                    "gate_id",
                    "gate_function",
                    "gate_input_path",
                    "baseline_verdict",
                    "planted_verdict",
                    "changed",
                ]
            )
        )
    obj = _plant_uoa_obj()
    no_ack = hazard_consumers.check_consumers({"limitations": [obj]}, {"acknowledgements": []})
    ack = {
        "acknowledgements": [
            {
                "limitation_id": obj["limitation_id"],
                "signed_by": "Codex lane AD plant",
                "date": "2026-09-15",
                "reason": "plant acknowledgement",
                "tranche": "TRANCHE-hazard-consumers",
            }
        ]
    }
    with_ack = hazard_consumers.check_consumers({"limitations": [obj]}, ack)
    obj["unwired_acknowledged"] = ack["acknowledgements"][0]
    html = render_page({
        "slug": "plant",
        "title": "Plant",
        "question": "Plant?",
        "limitations": [obj],
        "outcomes": [{"primary": True, "result": {"present": False, "reason": "none"}}],
    })
    lines.extend([
        "",
        "consumer-null refusal plant:",
        "without_ack: " + "; ".join(no_ack),
        "with_ack: " + ("PASS" if not with_ack else "; ".join(with_ack)),
        "ack_rendered_from_object: " + str("Hazard acknowledgements" in html and "plant acknowledgement" in html),
    ])
    (EVIDENCE_DIR / "02-plants.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def _pair_summary(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = defaultdict(lambda: {
        "count": 0,
        "statuses": set(),
        "gates": set(),
        "verdicts": set(),
        "acknowledged": 0,
    })
    for row in rows:
        bucket = out[_pair(row)]
        bucket["count"] += 1
        bucket["statuses"].add(row["status"])
        if row["consumer_gate"] != "null":
            bucket["gates"].add(row["consumer_gate"])
        if row["gate_verdict_at_build"] != "null":
            bucket["verdicts"].add(row["gate_verdict_at_build"])
        if row.get("acknowledged"):
            bucket["acknowledged"] += 1
    return out


def _acked_pairs() -> set[tuple[str, str]]:
    return {
        (str(item.get("kind")), str(item.get("evidence_state")))
        for item in hazard_consumers.load_acknowledgements().get("acknowledgements", [])
        if isinstance(item, dict)
    }


def _status_text(bucket: dict[str, Any] | None) -> str:
    if not bucket:
        return "ABSENT"
    statuses = ",".join(sorted(bucket["statuses"]))
    gates = ",".join(sorted(bucket["gates"])) or "null"
    return f"{statuses} count={bucket['count']} gate={gates}"


def _write_03(before: list[dict[str, str]], after: list[dict[str, str]]) -> None:
    bsum = _pair_summary(before)
    asum = _pair_summary(after)
    acks = _acked_pairs()
    lines = [
        "Before/after hazard consumer wiring table",
        "",
        "kind | evidence_state | before | after | outcome",
    ]
    for pair in sorted(set(bsum) | set(asum)):
        before_text = _status_text(bsum.get(pair))
        after_text = _status_text(asum.get(pair))
        before_wired = bsum.get(pair) and "WIRED" in bsum[pair]["statuses"]
        after_wired = asum.get(pair) and "WIRED" in asum[pair]["statuses"]
        if before_wired and after_wired:
            outcome = "pre-existing executable consumer"
        elif after_wired:
            outcome = "wired in TRANCHE-hazard-consumers"
        elif pair in acks:
            outcome = "left UNWIRED and acknowledged"
        else:
            outcome = "left UNWIRED without acknowledgement"
        lines.append(" | ".join([
            _clean(pair[0]),
            _clean(pair[1]),
            _clean(before_text),
            _clean(after_text),
            outcome,
        ]))
    lines.append("")
    lines.append("Final UNWIRED pairs: " + _pair_list([row for row in after if row["status"] == "UNWIRED"]))
    (EVIDENCE_DIR / "03-before-after-wiring.txt").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_04(after: list[dict[str, str]]) -> None:
    pair_counts = Counter(_pair(row) for row in after if row["status"] == "UNWIRED")
    lines = [
        "Hazard consumer acknowledgements",
        "",
        "ack_id | kind | evidence_state | matched_unwired_objects | signed_by | date | tranche | reason",
    ]
    for item in hazard_consumers.load_acknowledgements().get("acknowledgements", []):
        if not isinstance(item, dict):
            continue
        pair = (str(item.get("kind") or ""), str(item.get("evidence_state") or ""))
        lines.append(" | ".join([
            _clean(item.get("ack_id")),
            _clean(pair[0]),
            _clean(pair[1]),
            str(pair_counts.get(pair, 0)),
            _clean(item.get("signed_by")),
            _clean(item.get("date")),
            _clean(item.get("tranche")),
            _clean(item.get("reason")),
        ]))
    (EVIDENCE_DIR / "04-acknowledgements.txt").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_readme(before: list[dict[str, str]], after: list[dict[str, str]], base_ref: str) -> None:
    by_slug_before = defaultdict(list)
    by_slug_after = defaultdict(list)
    for row in before:
        by_slug_before[row["slug"]].append(row)
    for row in after:
        by_slug_after[row["slug"]].append(row)
    lines = [
        "# Hazard Consumers (2026-09-14)",
        "",
        "**Fix state (orthogonal fields rule): LANDED / NONE / CORPUS / CURRENT** - generated from TRANCHE-hazard-consumers",
        "",
        f"Base ref for the reproducible pre-wiring sweep: `{base_ref}`.",
        "",
        "This bundle records the diagnostic-decision decoupling sweep for all 32 served review topics. `01-sweep-32.txt` is computed from the base ref in base phase; the later files read the current working tree after lane AD wiring.",
        "",
        "slug | before limitation objects | before unwired BLOCKS/QUALIFIES | after limitation objects | after unwired BLOCKS/QUALIFIES",
    ]
    for slug in sorted(set(by_slug_before) | set(by_slug_after)):
        b_rows = by_slug_before.get(slug, [])
        a_rows = by_slug_after.get(slug, [])
        b_unwired = _unwired_hazards(b_rows)
        a_unwired = _unwired_hazards(a_rows)
        lines.append(" | ".join([
            _clean(slug),
            str(len(b_rows)),
            str(len(b_unwired)),
            str(len(a_rows)),
            str(len(a_unwired)),
        ]))
    lines.extend([
        "",
        "Before UNWIRED hazard pairs: " + _pair_list(_unwired_hazards(before)),
        "After UNWIRED hazard pairs: " + _pair_list(_unwired_hazards(after)),
    ])
    (EVIDENCE_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=None, help="base git ref for the pre-wiring review sweep")
    args = parser.parse_args(argv)
    base_ref = args.base or _head()
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    before = _rows(_base_reviews(base_ref), hazard_consumers.PHASE_BASE)
    after = _rows(_worktree_reviews(), hazard_consumers.PHASE_FINAL)
    _write_01(base_ref, before)
    _write_02()
    _write_03(before, after)
    _write_04(after)
    _write_readme(before, after, base_ref)
    print(f"wrote {EVIDENCE_DIR.relative_to(ROOT).as_posix()} ({len(before)} before rows, {len(after)} after rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
