"""Write the signing list for the audited result-change notices: one row per notice, for the REVIEWER.

  python scripts/notice_signing_list.py --out-md FILE --out-json FILE

This list is a queue, not a signature. Each row gives the one-line before -> after as judged, the rendered-block
sha256 that `sign --expect-digest` checks, the judgement it rests on and the exact command the walker would
print. how_it_reached_the_reviewer says how the notice is QUEUED to reach him; when he signs, --basis records his
own account of what he actually read. Nothing here signs, and no lane may sign: these are served-number changes,
outside the delegated bulk acceptance of 2026-09-24 (which covers AI screening proposals only).

The list is refused, like the walker, if any anchor is DETACHED.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import countersign_result_change as countersign  # noqa: E402
from scripts import notice_anchor  # noqa: E402
from scripts import sign_walk as walk  # noqa: E402


def rows() -> list[dict]:
    audit, notices, _, mapping = walk.load_walk()  # refuses on any detached anchor
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    out = []
    for position, row in enumerate(walk.ordered_notices(audit), 1):
        index = mapping[row["audit_id"]]
        notice = notices[index]
        _, _, sha = countersign._block_and_sha(notice)
        j = notice_anchor.current_judgement(row)
        signed = (notice.get("reviewer_countersignature") or {}).get("state", "OPEN")
        out.append({
            "position": position, "audit_id": row["audit_id"], "ledger_index": index,
            "slug": notice["slug"], "outcome": notice["outcome"], "state": signed,
            "before_after": j["before_after"], "rendered_block_sha256": sha,
            "judgement_id": j["judgement_id"], "lane_verdict": j["lane_verdict"], "defects": j["defects"],
            "lane_notes": j["lane_notes"],
            "gate_requires_individual_signature": row["gate_requires_per_notice_signature"],
            "audit_recommendation": row["recommendation"],
            "how_it_reached_the_reviewer": (
                f"QUEUED, not yet presented: python scripts/sign_walk.py --notice {row['audit_id']} on branch "
                f"nr/notice-anchors at {head[:12]} presents it after verifying judgement {j['judgement_id']} "
                f"({len(j['anchors'])} commit-pinned anchors: served page git:{j['served_commit'][:12]}, page "
                f"carrying the notice git:{j['proposed_commit'][:12]}) and prints the rendered block with sha256 "
                f"{sha}. When he signs, --basis records his own account of what he read."),
            "command": ("python scripts/countersign_result_change.py sign " + walk._ps(notice["slug"]) + " "
                        + walk._ps(notice["outcome"]) + f" --notice-index {index} --expect-digest {sha} --by 'Mahmood'"
                        f" --judgement {j['judgement_id']} --basis (Read-Host 'Describe how this notice reached you "
                        "and what you read')"),
        })
    return out


def markdown(items: list[dict]) -> str:
    lines = ["| # | Notice | Review / outcome | Before → after (as judged) | Rendered-block sha256 | Judgement | "
             "Lane verdict | Signature | Audit recommendation |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in items:
        lines.append(f"| {r['position']} | {r['audit_id']} (ledger {r['ledger_index']}) | {r['slug']} / {r['outcome']} "
                     f"| {r['before_after']} | `{r['rendered_block_sha256']}` | {r['judgement_id']} | "
                     f"{r['lane_verdict']} | {'individual' if r['gate_requires_individual_signature'] else 'batch-eligible'}"
                     f" | {r['audit_recommendation']} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--out-json", required=True)
    args = ap.parse_args(argv)
    try:
        items = rows()
    except (OSError, KeyError, ValueError) as error:
        print(f"refused: {error}", file=sys.stderr)
        return 1
    Path(args.out_md).write_bytes(markdown(items).encode("utf-8"))
    Path(args.out_json).write_bytes((json.dumps({"rows": items}, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    print(f"{len(items)} notices queued; {sum(r['state'] == 'OPEN' for r in items)} OPEN; "
          f"{sum(r['lane_verdict'] == 'HOLDS_WITH_DEFECT' for r in items)} carry a re-judgement defect")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
