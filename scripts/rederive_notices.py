"""Re-derive the result-change notices of a release CANDIDATE from its pages, and check its ledger against them.

  python scripts/rederive_notices.py --prev <served commit> [--cand HEAD] --out DIR

Run it IN A CHECKOUT OF THE CANDIDATE (the rendered-block digests are computed with the candidate's own renderer,
exactly as `sign --expect-digest` will compute them there). PREV is the release readers are served now.

Ground truth is the pages, not the ledger: for every (review, outcome) the result tuple (k, estimate, ci_low,
ci_high) served at PREV is compared with the candidate's. Each served-number change must be covered by exactly one
OPEN-or-signed ledger notice at the candidate whose before == PREV tuple and after == candidate tuple. Reported:
  NOTICED      change covered by a notice (with its ledger index, rendered sha256 and departing trials)
  UNNOTICED    a served number changes with no notice -- a V1 blocker (checklist E), never signable
  ORPHAN       a ledger notice (not superseded in its chain) whose transition the candidate does not make
  OLD-41       for each of the 41 audited on 2026-09-21 (registry/notice_adjudication.json at --audit-ref):
               SAME (identical transition and digest), CHANGED (same outcome, different transition or wording)
               or GONE (no change on that outcome any more)
Exit status 1 if anything is UNNOTICED, AMBIGUOUS or ORPHAN (each would publish an unsigned or false claim).
Writes DIR/rederived.json and DIR/rederived.md. Never writes the repository.
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
from harness import result_changes  # noqa: E402
from scripts import countersign_result_change as countersign  # noqa: E402

RT = result_changes.result_tuple


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True)


def show(ref: str, path: str) -> bytes | None:
    p = git("show", f"{ref}:{path}")
    return p.stdout if p.returncode == 0 else None


def slugs(ref: str) -> list[str]:
    out = git("ls-tree", "--name-only", f"{ref}:docs/reviews").stdout.decode().split()
    return sorted(s for s in out if show(ref, f"docs/reviews/{s}/review.json") is not None)


def outcomes(ref: str, slug: str) -> dict[str, dict]:
    raw = show(ref, f"docs/reviews/{slug}/review.json")
    if raw is None:
        return {}
    return {o["name"]: o for o in json.loads(raw).get("outcomes") or [] if o.get("name")}


def pooled(o: dict | None) -> list[str]:
    return sorted(((o or {}).get("membership") or {}).get("pooled") or [])


def departing(o: dict, left: list[str]) -> list[dict]:
    recs = {t.get("id"): t for t in o.get("declared_absent_trials") or []}
    return [{"trial_id": tid, "reason_code": recs.get(tid, {}).get("reason_code"),
             "absence_code": recs.get(tid, {}).get("absence_code"),
             "failing": ((recs.get(tid, {}).get("admission_verdict") or {}).get("failing"))} for tid in left]


def rederive(prev: str, cand: str, audit_ref: str | None) -> dict:
    ledger = json.loads(show(cand, "docs/result_changes.json") or b'{"notices": []}')["notices"]
    changes, all_slugs = [], sorted(set(slugs(prev)) | set(slugs(cand)))
    for slug in all_slugs:
        a, b = outcomes(prev, slug), outcomes(cand, slug)
        for name in sorted(set(a) | set(b)):
            ta, tb = RT((a.get(name) or {}).get("result")), RT((b.get(name) or {}).get("result"))
            if not result_changes._same(ta, tb):
                changes.append({"slug": slug, "outcome": name, "before": ta, "after": tb,
                                "left": sorted(set(pooled(a.get(name))) - set(pooled(b.get(name)))),
                                "entered": sorted(set(pooled(b.get(name))) - set(pooled(a.get(name)))),
                                "cand_outcome": b.get(name) or {}})
    # a ledger notice is "current" unless a later notice on the same outcome continues from its after
    chains = {(c["slug"], c["outcome"]): c for c in result_changes.chain_integrity(ledger)}
    current = {c["indices"][-1] for c in chains.values() if c["indices"]}
    rows, used = [], set()
    for ch in changes:
        hits = [i for i, n in enumerate(ledger) if n["slug"] == ch["slug"] and n["outcome"] == ch["outcome"]
                and result_changes._same(n.get("before"), ch["before"]) and result_changes._same(n.get("after"), ch["after"])]
        row = {k: v for k, v in ch.items() if k != "cand_outcome"}
        if len(hits) == 1:
            n = ledger[hits[0]]
            used.add(hits[0])
            row.update(status="NOTICED", ledger_index=hits[0], when_utc=n["when_utc"],
                       signature=(n.get("reviewer_countersignature") or {}).get("state", "OPEN"),
                       rendered_sha256=countersign._block_and_sha(n)[2],
                       notice_left=n.get("left_pool"), notice_entered=n.get("entered_pool"),
                       departing=departing(ch["cand_outcome"], ch["left"]))
            row["membership_matches_notice"] = (sorted(n.get("left_pool") or []) == ch["left"]
                                               and sorted(n.get("entered_pool") or []) == ch["entered"])
        else:
            row.update(status="UNNOTICED" if not hits else "AMBIGUOUS", ledger_indices=hits,
                       departing=departing(ch["cand_outcome"], ch["left"]))
        rows.append(row)
    orphans = [{"ledger_index": i, "slug": n["slug"], "outcome": n["outcome"], "before": n.get("before"),
                "after": n.get("after"), "signature": (n.get("reviewer_countersignature") or {}).get("state", "OPEN")}
               for i, n in enumerate(ledger) if i in current and i not in used
               and not any(r["slug"] == n["slug"] and r["outcome"] == n["outcome"] for r in rows)
               and (n.get("reviewer_countersignature") or {}).get("state", "OPEN") == "OPEN"]
    old = []
    if audit_ref:
        audit = json.loads(show(audit_ref, "registry/notice_adjudication.json") or b'{"notices": []}')
        for r in audit.get("notices") or []:
            match = [x for x in rows if x["slug"] == r["slug"] and x["outcome"] == r["outcome"]]
            if not match:
                old.append({"audit_id": r["audit_id"], "fate": "GONE"})
                continue
            x = match[0]
            same = (result_changes._same(x["before"], r["before"]) and result_changes._same(x["after"], r["after"])
                    and x.get("status") == "NOTICED" and x.get("when_utc") == r["when_utc"])
            old.append({"audit_id": r["audit_id"], "fate": "SAME" if same else "CHANGED",
                        "now": {"before": x["before"], "after": x["after"], "status": x["status"]}})
    return {"prev": prev, "cand": cand, "changes": rows, "orphans": orphans, "old_41": old,
            "counts": {"served_number_changes": len(rows),
                       "noticed": sum(r["status"] == "NOTICED" for r in rows),
                       "unnoticed": sum(r["status"] == "UNNOTICED" for r in rows),
                       "ambiguous": sum(r["status"] == "AMBIGUOUS" for r in rows),
                       "orphans": len(orphans),
                       "membership_mismatch": sum(r.get("membership_matches_notice") is False for r in rows),
                       "old_41": {f: sum(o["fate"] == f for o in old) for f in ("SAME", "CHANGED", "GONE")}}}


def resolve(ref: str) -> str:
    p = git("rev-parse", "--verify", f"{ref}^{{commit}}")
    if p.returncode != 0:
        raise SystemExit(f"refused: {ref} is not a commit in this clone")
    return p.stdout.decode().strip()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--prev", required=True)
    ap.add_argument("--cand", default="HEAD")
    ap.add_argument("--audit-ref", default="origin/nr/notice-anchors")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    prev, cand = resolve(args.prev), resolve(args.cand)
    head = resolve("HEAD")
    if cand != head:
        print(f"warning: digests are computed with THIS tree's renderer ({head[:12]}), not {cand[:12]}'s; "
              "run in a checkout of the candidate for signable digests", file=sys.stderr)
    audit_ref = resolve(args.audit_ref) if args.audit_ref else None
    result = rederive(prev, cand, audit_ref)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "rederived.json").write_bytes((json.dumps(result, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    c = result["counts"]
    lines = [f"# Re-derived result-change notices: candidate {cand[:12]} against served {prev[:12]}", "",
             f"- served-number changes: {c['served_number_changes']}; noticed {c['noticed']}; **unnoticed "
             f"{c['unnoticed']}**; ambiguous {c['ambiguous']}; orphan OPEN notices {c['orphans']}; membership "
             f"mismatches {c['membership_mismatch']}",
             f"- the 41 audited on 21 Sep: SAME {c['old_41'].get('SAME', 0)}, CHANGED {c['old_41'].get('CHANGED', 0)}, "
             f"GONE {c['old_41'].get('GONE', 0)}", ""]
    for r in result["changes"]:
        lines.append(f"- {r['status']}: {r['slug']} / {r['outcome']}: {r['before']} -> {r['after']}"
                     + (f" (ledger {r['ledger_index']}, {r['signature']})" if r["status"] == "NOTICED" else ""))
    for o in result["orphans"]:
        lines.append(f"- ORPHAN: ledger {o['ledger_index']} {o['slug']} / {o['outcome']}")
    (out / "rederived.md").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    print(lines[2])
    print(lines[3])
    return 1 if c["unnoticed"] or c["ambiguous"] or c["orphans"] else 0  # each is a V1 blocker


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
