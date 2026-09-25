"""Build the audit registry (registry/notice_adjudication.json) for a release CANDIDATE from a clean re-derivation.

  python scripts/v1_notice_registry.py --rederived DIR/rederived.json --out registry/notice_adjudication.json
      [--audit-ref origin/nr/notice-anchors]

Refuses unless the re-derivation is clean (0 UNNOTICED, 0 AMBIGUOUS, 0 ORPHAN): a blocker is never papered over by
an audit. One row per NOTICED change that is still OPEN (a notice already signed needs no signing list):
  - a notice the 21 Sep audit covered with the IDENTICAL transition (same slug, outcome, when_utc, before, after)
    keeps its audit row -- recommendation, direction, grouping and every earlier judgement (append-only);
  - any other notice gets a NEW row (audit_id V1-NN) marked for individual review, with its direction computed
    by scripts/notice_rejudge.direction and its mechanism read from the departing trials' absence codes.
Every row's departing_trials is re-read from the CANDIDATE's page (pointers move when a page is rebuilt).
The registry then needs a judgement appended against the candidate (scripts/notice_rejudge.py packets / append)
before the walker will present anything: until then every notice refuses -- as it should.
"""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import notice_rejudge  # noqa: E402

ROW_FIELDS_FROM_NOTICE = ("slug", "outcome", "before", "after", "left_pool", "entered_pool", "reason", "by",
                          "when_utc", "before_note", "after_note", "reason_locked", "record_note")


def show(ref: str, path: str) -> bytes | None:
    p = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True)
    return p.stdout if p.returncode == 0 else None


def departing_from_page(review: dict, outcome: str, left: list[str]) -> list[dict]:
    oi, o = next((i, o) for i, o in enumerate(review["outcomes"]) if o.get("name") == outcome)
    out = []
    for tid in left:
        j, rec = next(((j, t) for j, t in enumerate(o.get("declared_absent_trials") or []) if t.get("id") == tid),
                      (None, {}))
        out.append({"trial_id": tid, "family_id": rec.get("family_id"),
                    "eligibility_label": rec.get("eligibility_state") or rec.get("state"),
                    "absence_code": rec.get("absence_code"), "reason_code": rec.get("reason_code"),
                    "candidate_tuple": rec.get("candidate_tuple"),
                    "current_pointer": f"/outcomes/{oi}/declared_absent_trials/{j}" if j is not None else None,
                    "source_excerpt": str(rec.get("source") or "")[:200]})
    return out


def build(rederived: dict, audit_ref: str | None) -> dict:
    c = rederived["counts"]
    if c["unnoticed"] or c["ambiguous"] or c["orphans"]:
        raise SystemExit(f"refused: the re-derivation is not clean ({c}); fix the candidate first")
    cand, prev = rederived["cand"], rederived["prev"]
    ledger = json.loads(show(cand, "docs/result_changes.json"))["notices"]
    old = json.loads(show(audit_ref, "registry/notice_adjudication.json") or b'{"notices": []}') if audit_ref else {"notices": []}
    old_rows = {(r["slug"], r["outcome"], r["when_utc"]): r for r in old.get("notices") or []}
    reviews: dict[str, dict] = {}
    rows, new_n = [], 0
    for ch in rederived["changes"]:
        if ch["status"] != "NOTICED" or ch.get("signature") != "OPEN":
            continue
        n = ledger[ch["ledger_index"]]
        key = (n["slug"], n["outcome"], n["when_utc"])
        if n["slug"] not in reviews:
            reviews[n["slug"]] = json.loads(show(cand, f"docs/reviews/{n['slug']}/review.json"))
        prior = old_rows.get(key)
        if prior and all(prior.get(k) == n.get(k) for k in ROW_FIELDS_FROM_NOTICE):
            row = copy.deepcopy(prior)
        else:
            new_n += 1
            o = next(o for o in reviews[n["slug"]]["outcomes"] if o.get("name") == n["outcome"])
            scale = (o.get("result") or {}).get("scale") or (n.get("before") or {}).get("scale")
            higher = (n["slug"], n["outcome"]) in notice_rejudge.HIGHER_IS_FAVOURABLE
            direction = notice_rejudge.direction(n["before"], n["after"], scale, higher,
                                                 bool(n.get("left_pool") or n.get("entered_pool")))
            row = {"audit_id": f"V1-{new_n:02d}", "scale_before": scale, "scale_after": scale,
                   "declared_estimand": o.get("estimand"), "null_value": 0 if str(scale).upper() in ("MD", "SMD") else 1,
                   "direction": direction,
                   "direction_explanation": f"computed from the tuples by scripts/notice_rejudge.direction: {direction}",
                   "mechanism": "NOT_AUDITED",
                   "individual_review_required_by_lane": True,
                   "individual_review_triggers": ["NEW_OR_CHANGED_BY_V1"],
                   "additional_individual_review_reason": ("this notice is new or changed by the V1 candidate and "
                                                           "was not covered by the 21 Sep audit"),
                   "gate_requires_per_notice_signature": True, "decision_group": None,
                   "recommendation": "NEEDS_MAHMOOD_JUDGEMENT",
                   "recommendation_reason": "new or changed in the V1 candidate: read it in full before signing",
                   "recovery_evidence": [], "page_evidence": {}}
            if prior:
                row["supersedes_audit_id"] = prior["audit_id"]
        for k in ROW_FIELDS_FROM_NOTICE:
            if k in n:
                row[k] = n[k]
        row["departing_trials"] = departing_from_page(reviews[n["slug"]], n["outcome"], n.get("left_pool") or [])
        codes = sorted({t["absence_code"] or t["eligibility_label"] or "?" for t in row["departing_trials"]})
        row["mechanism_detail"] = "; ".join(f"{t['trial_id']}: {t['absence_code'] or t['eligibility_label']}"
                                            for t in row["departing_trials"]) or "no departing trial"
        if row.get("mechanism") == "NOT_AUDITED":
            row["mechanism"] = "+".join(codes) if codes else "NO_DEPARTURE"
        row["page_evidence"] = dict(row.get("page_evidence") or {},
                                    review_path=f"docs/reviews/{n['slug']}/review.json",
                                    html_path=f"docs/reviews/{n['slug']}/index.html",
                                    notice_block_sha256=ch["rendered_sha256"])
        rows.append(row)
    ids = {r["audit_id"] for r in rows}
    for r in rows:  # a new row is its own singleton group
        if not r.get("decision_group") or not r["decision_group"].startswith("G"):
            r["decision_group"] = "I-" + r["audit_id"]
    groups = []
    for g in old.get("decision_groups") or []:
        members = [m for m in g["members"] if m in ids and next(r for r in rows if r["audit_id"] == m)
                   .get("decision_group") == g["group_id"]]
        if members:
            groups.append(dict(g, members=members, count=len(members)))
    for r in rows:  # a row still pointing at a group that lost all members becomes a singleton
        if r["decision_group"].startswith("G") and not any(g["group_id"] == r["decision_group"] for g in groups):
            r["decision_group"] = "I-" + r["audit_id"]
    reg = {k: v for k, v in old.items() if k not in ("notices", "decision_groups", "source_digests",
                                                     "superseded_anchors", "specific_conflicts")}
    reg.update(audit_progress="complete", notices=rows, decision_groups=groups,
               specific_conflicts={k: v for k, v in (old.get("specific_conflicts") or {}).items() if k in ids},
               source_digests={}, v1_candidate={"cand": cand, "prev": prev,
                                                "carried_from_21_sep": sum(not r["audit_id"].startswith("V1-") for r in rows),
                                                "new_or_changed": new_n})
    return reg


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rederived", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--audit-ref", default="origin/nr/notice-anchors")
    args = ap.parse_args(argv)
    reg = build(json.loads(Path(args.rederived).read_text(encoding="utf-8")), args.audit_ref)
    Path(args.out).write_bytes((json.dumps(reg, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    v = reg["v1_candidate"]
    print(f"{len(reg['notices'])} OPEN notices: {v['carried_from_21_sep']} carried from the 21 Sep audit, "
          f"{v['new_or_changed']} new or changed; {len(reg['decision_groups'])} shared-reason groups kept")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
