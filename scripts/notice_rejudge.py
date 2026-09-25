"""Re-judge audited result-change notices against pinned page versions, and append the judgement (decision B).

  packets --served <commit> --proposed <commit> --out DIR
      For every notice in registry/notice_adjudication.json, read the SERVED page (the version a reader gets now;
      origin/main) and the PROPOSED page (the version that carries the notice) from git -- never from the working
      tree -- and write DIR/<audit_id>.json: the ledger notice, both outcome objects, the pooled memberships, the
      rendered notice block and the audit's claims. Also run the mechanical checks below and write DIR/checks.json.
      Writes nothing in the repository.

  append --served <commit> --proposed <commit> --verdicts FILE [--judged-by TEXT]
      Append ONE judgement per notice to registry/notice_adjudication.json. Refuses, writing nothing, unless every
      audited notice has a verdict entry that (a) names exactly the anchor digests this command recomputes -- a
      verdict is bound to the bytes judged, as `sign --expect-digest` binds a signature -- (b) is HOLDS or
      HOLDS_WITH_DEFECT from both the bulk reader and the lane (a DIFFERS from either refuses), and (c) every
      mechanical check passes. HOLDS_WITH_DEFECT means the notice records the transition between the judged pages
      correctly but its rendered words carry a defect the reviewer must be shown (`defects`); the walker prints it
      above the signing command. It is never a recommendation to sign. Prior judgements are kept unchanged
      (append-only); the previous working-tree digests are kept under `superseded_anchors` as history.

Mechanical checks (each must be True for HOLDS):
  ledger_identity    the notice is the one OPEN ledger entry with this (slug, outcome, when_utc) at --proposed
  audit_fields       the audit row's copy of every ledger field equals the ledger at --proposed
  served_is_before   the served page's result tuple equals notice.before
  baseline_is_before the 38c04411 page's tuple equals notice.before (the history the notice was raised against)
  proposed_is_after  the proposed page's result tuple equals notice.after
  left_pool_exact    notice.left_pool == served pooled ids - proposed pooled ids
  entered_pool_exact notice.entered_pool == proposed pooled ids - served pooled ids
  departing_retained every departing trial is still named on the proposed outcome with a P5 set-aside reason
  departing_audit    the audit's departing-trial records resolve on the proposed page (id, family, tuple, code)
  block_in_page      the canonical rendered block occurs in the proposed index.html (whitespace-normalised)
                     (the same test scripts/notice_anchor.guard repeats on every walk and every `sign`)
  block_signable     the block's rendered_sha256 (the digest `sign --expect-digest` checks) is recorded. The audit's
                     own page_evidence.notice_block_sha256 is NOT used: no committed version reproduces it (found
                     2026-09-25, 0 of 41, eleven candidate derivations at four commits) and nothing reads it.
  direction          the direction recomputed here from the tuples equals the audit's
  chain_ok           the (slug, outcome) chain is intact at --proposed
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from harness import result_changes  # noqa: E402
from scripts import countersign_result_change as countersign  # noqa: E402
from scripts import notice_anchor as anchor  # noqa: E402

AUDIT = ROOT / "registry" / "notice_adjudication.json"
BASELINE = "38c04411484dbea035a8e4c8e22c57c2794f9495"
CODE = ("harness/result_changes.py", "harness/page.py", "harness/harms.py")
VERDICTS = ("HOLDS", "HOLDS_WITH_DEFECT")
HIGHER_IS_FAVOURABLE = {("metformin-pcos-ovulation", "Ovulation with metformin added to clomifene")}


def _show(commit: str, path: str) -> bytes:
    proc = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=ROOT, capture_output=True)
    if proc.returncode != 0:
        raise anchor.AnchorRefused(f"git:{commit}:{path} unreadable: {proc.stderr.decode(errors='replace').strip()}")
    return proc.stdout


def _resolve(commit: str) -> str:
    proc = subprocess.run(["git", "rev-parse", "--verify", f"{commit}^{{commit}}"], cwd=ROOT, capture_output=True)
    if proc.returncode != 0:
        raise anchor.AnchorRefused(f"commit {commit!r} not in this clone")
    return proc.stdout.decode().strip()


def _outcome(review: dict, name: str) -> dict:
    hits = [o for o in review.get("outcomes") or [] if o.get("name") == name]
    if len(hits) != 1:
        raise anchor.AnchorRefused(f"{len(hits)} outcomes named {name!r}")
    return hits[0]


def _pooled(outcome: dict) -> list[str]:
    return sorted((outcome.get("membership") or {}).get("pooled") or [])


def _trim(outcome: dict) -> dict:
    res = outcome.get("result") or {}
    return {
        "name": outcome.get("name"), "kind": outcome.get("kind"), "primary": outcome.get("primary"),
        "estimand": outcome.get("estimand"),
        "result": {k: res.get(k) for k in ("k", "estimate", "ci_low", "ci_high", "scale", "claim", "ci_note")},
        "membership": {k: (outcome.get("membership") or {}).get(k) for k in ("pooled", "declared_absent", "refused",
                                                                          "screened_in_not_pooled")},
        "pooled_trials": [{k: t.get(k) for k in ("id", "effect", "ci_low", "ci_high", "scale", "admission_verdict")}
                          for t in outcome.get("trials") or []],
        "set_aside_or_absent": [{k: t.get(k) for k in ("id", "state", "reason_code", "reason", "absent_kind")}
                                for t in outcome.get("declared_absent_trials") or []],
    }


def _norm(text: str) -> str:
    return " ".join(text.split())


def _log(x: float, scale: str | None) -> float:
    return x if (scale or "").upper() in ("MD", "SMD") else math.log(x)


def direction(before: dict, after: dict, scale: str | None, higher_favourable: bool, members_changed: bool) -> str:
    """Independent re-implementation of the audit's direction_policy (registry/notice_adjudication.json)."""
    b, a = before.get("estimate"), after.get("estimate")
    if b is not None and a is None:
        return "RESULT_REMOVED"
    if b is None and a is not None:
        return "RESULT_ADDED"
    if b is None and a is None:
        return "NO_DIRECTION"
    null = 0.0  # distances from the null on the analysis scale: MD as is, ratios on the log scale
    lb, la = _log(b, scale), _log(a, scale)
    sign = 1 if higher_favourable else -1
    larger = abs(la - null) > abs(lb - null)
    favourable = sign * (la - lb) > 0
    both_ci = all(r.get(k) is not None for r in (before, after) for k in ("ci_low", "ci_high"))
    narrower = both_ci and (after["ci_high"] - after["ci_low"]) < (before["ci_high"] - before["ci_low"])

    def fav_ci(r):
        if r.get("ci_low") is None or r.get("ci_high") is None:
            return False
        lo, hi = _log(r["ci_low"], scale), _log(r["ci_high"], scale)
        return lo > 0 if higher_favourable else hi < 0
    new_fav = fav_ci(after) and not fav_ci(before)
    if larger or narrower or favourable or new_fav:
        return "AWAY_FROM_NULL"
    if a == b and members_changed:
        return "MEMBERSHIP_ONLY"
    return "TOWARD_NULL"


def build(served: str, proposed: str) -> tuple[list[dict], list[dict]]:
    audit = json.loads(_show(proposed, "registry/notice_adjudication.json"))
    ledger = json.loads(_show(proposed, "docs/result_changes.json"))["notices"]
    chains = {(c["slug"], c["outcome"]): c for c in result_changes.chain_integrity(ledger)}
    cache: dict[tuple[str, str], dict] = {}

    def review(commit, slug):
        if (commit, slug) not in cache:
            cache[(commit, slug)] = json.loads(_show(commit, f"docs/reviews/{slug}/review.json"))
        return cache[(commit, slug)]
    packets, checks = [], []
    for row in audit["notices"]:
        hits = [i for i, n in enumerate(ledger) if all(n[k] == row[k] for k in ("slug", "outcome", "when_utc"))]
        c: dict[str, bool | str] = {"audit_id": row["audit_id"]}
        c["ledger_identity"] = len(hits) == 1 and (ledger[hits[0]].get("reviewer_countersignature") or {}).get(
            "state", "OPEN") == "OPEN"
        if len(hits) != 1:
            checks.append(c)
            continue
        idx = hits[0]
        n = ledger[idx]
        fields = set(n) | set(result_changes.REQUIRED)
        c["audit_fields"] = all(row.get(k) == n.get(k) for k in fields if k != "reviewer_countersignature")
        s_out = _outcome(review(served, n["slug"]), n["outcome"])
        p_out = _outcome(review(proposed, n["slug"]), n["outcome"])
        b_out = _outcome(review(BASELINE, n["slug"]), n["outcome"])
        rt = result_changes.result_tuple
        c["served_is_before"] = result_changes._same(rt(s_out.get("result")), n["before"])
        c["baseline_is_before"] = result_changes._same(rt(b_out.get("result")), n["before"])
        c["proposed_is_after"] = result_changes._same(rt(p_out.get("result")), n["after"])
        sp, pp = set(_pooled(s_out)), set(_pooled(p_out))
        c["left_pool_exact"] = sorted(n["left_pool"]) == sorted(sp - pp)
        c["entered_pool_exact"] = sorted(n["entered_pool"]) == sorted(pp - sp)
        absent = {t.get("id"): t for t in p_out.get("declared_absent_trials") or []}
        c["departing_retained"] = all(
            tid in absent and "P5_family_eligible" in json.dumps(absent[tid], ensure_ascii=False)
            for tid in n["left_pool"])
        prev = review(proposed, n["slug"])
        ok = {t["trial_id"] for t in row["departing_trials"]} == set(n["left_pool"])
        for t in row["departing_trials"]:
            rec = prev
            for tok in t["current_pointer"].strip("/").split("/"):
                rec = rec[int(tok)] if isinstance(rec, list) else rec[tok]
            ok = ok and rec.get("id") == t["trial_id"] and rec.get("family_id") == t["family_id"] \
                and rec.get("candidate_tuple") == t["candidate_tuple"] and rec.get("absence_code") == t["absence_code"]
        c["departing_audit"] = ok
        html = _show(proposed, f"docs/reviews/{n['slug']}/index.html").decode("utf-8")
        _, block, sha = countersign._block_and_sha(n)
        c["block_in_page"] = _norm(block) in _norm(html)
        c["rendered_block_sha256"] = sha
        c["block_signable"] = bool(sha) and c["block_in_page"]
        scale = (p_out.get("result") or {}).get("scale") or (s_out.get("result") or {}).get("scale") \
            or row.get("scale_before")
        c["direction_recomputed"] = direction(n["before"], n["after"], scale,
                                              (n["slug"], n["outcome"]) in HIGHER_IS_FAVOURABLE, sp != pp)
        c["direction"] = c["direction_recomputed"] == row["direction"]
        c["chain_ok"] = chains[(n["slug"], n["outcome"])]["ok"]
        checks.append(c)
        packets.append({
            "audit_id": row["audit_id"], "ledger_index": idx, "ledger_notice": n,
            "served": {"commit": served, "outcome": _trim(s_out), "pooled": sorted(sp)},
            "proposed": {"commit": proposed, "outcome": _trim(p_out), "pooled": sorted(pp)},
            "rendered_block_text": _norm(__import__("re").sub(r"<[^>]+>", " ", block)),
            "rendered_block_sha256": sha,
            "audit_claims": {k: row.get(k) for k in ("direction", "direction_explanation", "mechanism",
                                                     "mechanism_detail", "departing_trials", "recommendation")},
            "direction_policy": audit["direction_policy"],
            "orientation": "higher is favourable" if (n["slug"], n["outcome"]) in HIGHER_IS_FAVOURABLE
            else "lower is favourable",
        })
    return packets, checks


def anchors_for(row: dict, served: str, proposed: str) -> list[dict]:
    slug = row["slug"]
    out = [anchor.make(ROOT, "served", served, f"docs/reviews/{slug}/review.json"),
           anchor.make(ROOT, "served", served, f"docs/reviews/{slug}/index.html"),
           anchor.make(ROOT, "proposed", proposed, f"docs/reviews/{slug}/review.json"),
           anchor.make(ROOT, "proposed", proposed, f"docs/reviews/{slug}/index.html"),
           anchor.make(ROOT, "record", proposed, "docs/result_changes.json")]
    out += [anchor.make(ROOT, "code", proposed, path) for path in CODE]
    return out


def cmd_packets(args) -> int:
    served, proposed = _resolve(args.served), _resolve(args.proposed)
    packets, checks = build(served, proposed)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for p in packets:
        (out / f"{p['audit_id']}.json").write_bytes((json.dumps(p, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    (out / "checks.json").write_bytes((json.dumps({"served": served, "proposed": proposed, "checks": checks},
                                                  ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    failing = [c["audit_id"] for c in checks
               if not all(v for k, v in c.items() if k not in ("audit_id", "direction_recomputed", "rendered_block_sha256"))]
    print(f"{len(packets)} packets; {len(checks) - len(failing)} of {len(checks)} pass every mechanical check"
          + (f"; failing: {', '.join(failing)}" if failing else ""))
    return 0


def cmd_append(args) -> int:
    served, proposed = _resolve(args.served), _resolve(args.proposed)
    audit_bytes = AUDIT.read_bytes()
    if _show(proposed, "registry/notice_adjudication.json") != audit_bytes:
        raise anchor.AnchorRefused("the working registry differs from the proposed commit's; judge committed bytes")
    verdicts = {v["audit_id"]: v for v in json.loads(Path(args.verdicts).read_text(encoding="utf-8"))["verdicts"]}
    _, checks = build(served, proposed)
    by_id = {c["audit_id"]: c for c in checks}
    new = json.loads(audit_bytes)
    problems = []
    when = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for row in new["notices"]:
        aid = row["audit_id"]
        v = verdicts.get(aid)
        c = by_id.get(aid, {})
        anchors = anchors_for(row, served, proposed)
        if row["audit_id"] in new.get("specific_conflicts", {}):
            anchors.append(anchor.make(ROOT, "held", proposed, new["specific_conflicts"][aid]["cache_path"]))
        if v is None:
            problems.append(f"{aid}: no verdict")
            continue
        if {a["ref"]: a["sha256"] for a in anchors} != v.get("anchors"):
            problems.append(f"{aid}: verdict names different bytes from the ones this command pins")
        if not all(val for k, val in c.items() if k not in ("audit_id", "direction_recomputed", "rendered_block_sha256")):
            problems.append(f"{aid}: a mechanical check fails: "
                            + ", ".join(k for k, val in c.items() if val is False))
        if v.get("bulk_verdict") not in VERDICTS or v.get("lane_verdict") not in VERDICTS:
            problems.append(f"{aid}: bulk {v.get('bulk_verdict')} / lane {v.get('lane_verdict')}")
        if v.get("lane_verdict") == "HOLDS_WITH_DEFECT" and not v.get("defects"):
            problems.append(f"{aid}: HOLDS_WITH_DEFECT names no defect")
        if v.get("rendered_block_sha256") != c.get("rendered_block_sha256"):
            problems.append(f"{aid}: verdict names a different rendered block")
        row.setdefault("judgements", []).append({
            "judgement_id": f"{args.judgement_prefix}-{aid}", "kind": "RE_JUDGEMENT_DECISION_B",
            "judged_utc": when, "judged_by": args.judged_by, "served_commit": served, "proposed_commit": proposed,
            "anchors": anchors, "mechanical_checks": {k: val for k, val in c.items() if k != "audit_id"},
            "bulk_reader": v.get("bulk_reader"), "bulk_verdict": v["bulk_verdict"],
            "lane_verdict": v["lane_verdict"], "lane_notes": v.get("lane_notes", ""),
            "defects": v.get("defects", []), "bulk_concerns": v.get("bulk_concerns", []),
            "before_after": v["before_after"], "rendered_block_sha256": v["rendered_block_sha256"],
        })
    if problems:
        print("refused; nothing written:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    old = json.loads(audit_bytes)
    why = anchor.append_only_problem(old, new)
    if why:
        print(f"refused; nothing written: {why}", file=sys.stderr)
        return 1
    if "superseded_anchors" not in new:
        new["superseded_anchors"] = {
            "note": ("The working-tree digests recorded before decision B, kept as history. They name no version; "
                     "after the page rebuilds they could not say what had been judged. Superseded by the "
                     f"commit-pinned judgements {args.judgement_prefix}-*, which re-judged every notice."),
            "recorded_at_head_commit": old.get("head_commit"),
            "source_digests": old["source_digests"]}
    new["anchor_policy"] = ("DECISION_B (Dispatch under Mahmood's delegation, 2026-09-24): every anchor is "
                            "git:<commit>:<path> with blob id and sha256 (scripts/notice_anchor.py); the walker and "
                            "`sign` refuse a DETACHED anchor; anchors change only by appending a judgement "
                            "(scripts/notice_rejudge.py append), never by refreshing a digest.")
    new["source_digests"] = anchor.source_digest_map(new)
    AUDIT.write_bytes((json.dumps(new, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))  # LF on every OS
    print(f"appended {len(new['notices'])} judgements ({args.judgement_prefix}-*); served {served[:12]}, "
          f"proposed {proposed[:12]}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("packets")
    p.add_argument("--served", required=True); p.add_argument("--proposed", required=True); p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_packets)
    a = sub.add_parser("append")
    a.add_argument("--served", required=True); a.add_argument("--proposed", required=True)
    a.add_argument("--verdicts", required=True); a.add_argument("--judgement-prefix", default="B1")
    a.add_argument("--judged-by", required=True)
    a.set_defaults(fn=cmd_append)
    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except anchor.AnchorRefused as error:
        print(f"refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
