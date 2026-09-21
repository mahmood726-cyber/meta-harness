"""Refresh docs/result_changes.json from the objects: for every (slug, outcome) whose served result (at the base
commit) differs from the working tree's, a notice with before/after tuples, the rows that left/entered, interval
or pool-refusal notes, and a reason built from the set-aside records (specific reason first, mechanism after, the
surviving sentence last). Existing notices are kept where before/after/left/entered still match; a notice whose
numbers or rows changed is rebuilt and its countersignature reset to OPEN (a signature is on bytes; the bytes
moved). A notice with `reason_locked: true` keeps its hand-written reason. Notices for outcomes that no longer
differ are dropped. Run after every regeneration, before the census is read.

Usage: python scripts/refresh_result_change_notices.py <base_commit> [--by NAME] [--when UTC]
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import result_changes  # noqa: E402

PATH = ROOT / "docs" / "result_changes.json"
MECH = ("Mechanism: the hand-row binder landing (m2/bind-hand-rows) binds every hand-extracted row to held bytes or sets it "
        "aside; a set-aside trial stays eligible evidence awaiting adjudication; the numbers are not asserted wrong.")
CODE_WORD = {"ENDPOINT_UNBOUND": "set aside", "RESULT_INCOMPATIBLE": "refused", "KNOWN_REPORTED_NOT_YET_EXTRACTED": "set aside"}


def _before(commit, slug):
    p = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:docs/reviews/{slug}/review.json"], capture_output=True)
    return json.loads(p.stdout.decode("utf-8")) if p.returncode == 0 else None


def _after(slug):
    p = ROOT / "docs" / "reviews" / slug / "review.json"
    return json.load(open(p, encoding="utf-8")) if p.exists() else None


def _note(res):
    r = res or {}
    pr = r.get("pool_refused") or {}
    if pr.get("code"):
        return f"pool refused at k = {r.get('k')}, {pr['code']}: {pr.get('detail') or ''}".rstrip(": ")
    if r.get("suppressed_incompatible"):
        return f"pool suppressed: incompatible estimands, {r.get('scale')}"
    c = (r.get("pooled_ci_refused") or {}).get("code")
    return f"refused at k = {r.get('k')}, {c}" if c else None


def _reason(left, absent):
    parts = []
    for tid in left:
        x = absent.get(tid) or {}
        code = x.get("reason_code") or x.get("state") or "ABSENT"
        why = (x.get("endpoint_binding_reason") or x.get("reason") or "").strip().rstrip(".")
        parts.append(f"{tid} {CODE_WORD.get(code, 'set aside')} ({code}): {why}.")
    return " ".join(parts) + (" " if parts else "") + MECH


def refresh(commit, by, when):
    data = json.load(open(PATH, encoding="utf-8")) if PATH.exists() else {"_doc": "", "notices": []}
    old = {(n["slug"], n["outcome"]): n for n in data.get("notices", [])}
    new, kept, rebuilt, added, dropped = [], [], [], [], []
    for slug in sorted(os.listdir(ROOT / "docs" / "reviews")):
        b, a = _before(commit, slug), _after(slug)
        if not b or not a:
            continue
        an = {o["name"]: o for o in a["outcomes"]}
        for o in b["outcomes"]:
            n = an.get(o["name"])
            if n is None:
                continue
            tb, ta = result_changes.result_tuple(o.get("result")), result_changes.result_tuple(n.get("result"))
            if result_changes._same(tb, ta):
                continue
            bp = [t["id"] for t in o.get("trials") or []]
            ap = [t["id"] for t in n.get("trials") or []]
            left, entered = sorted(set(bp) - set(ap)), sorted(set(ap) - set(bp))
            absent = {x["id"]: x for x in n.get("declared_absent_trials") or []}
            key = (slug, o["name"])
            prev = old.get(key)
            same = (prev is not None and result_changes._same(prev.get("before"), tb) and result_changes._same(prev.get("after"), ta)
                    and sorted(map(str, prev.get("left_pool") or [])) == left and sorted(map(str, prev.get("entered_pool") or [])) == entered)
            notice = dict(prev) if prev else {"slug": slug, "outcome": o["name"]}
            notice.update({"before": tb, "after": ta, "left_pool": left, "entered_pool": entered})
            for k, v in (("before_note", _note(o.get("result"))), ("after_note", _note(n.get("result")))):
                if v:
                    notice[k] = v
                else:
                    notice.pop(k, None)
            if not same or not prev.get("reason"):
                if not notice.get("reason_locked"):
                    notice["reason"] = _reason(left, absent)
                notice["by"] = by
                notice["when_utc"] = when
                notice["reviewer_countersignature"] = {"state": "OPEN", "note": "the reviewer has not yet seen the rendered notice; "
                                                       "sign with scripts/countersign_result_change.py after reading it"}
                (rebuilt if prev else added).append(key)
            else:
                kept.append(key)
            if "reviewer_countersignature" not in notice:
                notice["reviewer_countersignature"] = {"state": "OPEN"}
            new.append(notice)
    for key in old:
        if key not in {(n["slug"], n["outcome"]) for n in new}:
            dropped.append(key)
    data["notices"] = new
    json.dump(data, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    open(PATH, "a", encoding="utf-8").write("\n")
    return kept, rebuilt, added, dropped


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("base_commit")
    ap.add_argument("--by", default="Claude Opus 5 (lane m2/bind-hand-rows); reviewer countersignature owed: Mahmood")
    ap.add_argument("--when", default=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    args = ap.parse_args(argv)
    kept, rebuilt, added, dropped = refresh(args.base_commit, args.by, args.when)
    print(f"notices kept {len(kept)}, rebuilt {len(rebuilt)}, added {len(added)}, dropped {len(dropped)}")
    for tag, items in (("REBUILT", rebuilt), ("ADDED", added), ("DROPPED", dropped)):
        for k in items:
            print(f"  {tag} {k[0]} | {k[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
