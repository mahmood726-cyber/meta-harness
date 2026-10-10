"""Record, for every docs/definition_audit.json row, the served trial-row version it JUDGED (harness/defaudit_binding.py).

The version is recovered from git history, never guessed: the commit that first wrote the row's CURRENT text
(detail + resolution) is found by walking docs/definition_audit.json's commits oldest-first; the served review.json AT
that commit gives the trial row (by outcome name and PMID). Its effect, CI, scale and source-span sha256 become
row["judged"] (with the commit). A row whose trial cannot be found at that commit gets judged = {"state": "NOT_FOUND"},
which audit_state() treats as UNBOUND (not used).

    python scripts/bind_definition_audit.py [--check]      (--check: exit 1 if the file is not already bound this way)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness.defaudit_binding import trial_fingerprint  # noqa: E402
from harness.compat_check import _pid  # noqa: E402  (the SAME trial identity the consumer uses)

PATH = "docs/definition_audit.json"


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, check=True).stdout


def _row_text(row):
    return (row.get("detail"), row.get("resolution"))


def bound(doc):
    commits = _git("log", "--reverse", "--format=%H", "--", PATH).decode().split()
    first = {}
    for c in commits:
        rows = (json.loads(_git("show", f"{c}:{PATH}")).get("by_row") or {})
        for k, v in rows.items():
            if k in doc["by_row"] and _row_text(v) == _row_text(doc["by_row"][k]) and k not in first:
                first[k] = c
    out = json.loads(json.dumps(doc))
    for k, row in out["by_row"].items():
        c = first.get(k)
        slug, outcome, pmid = k.split("::", 2)
        judged = {"state": "NOT_FOUND"}
        if c:
            try:
                rv = json.loads(_git("show", f"{c}:docs/reviews/{slug}/review.json"))
            except subprocess.CalledProcessError:
                rv = {}
            o = next((x for x in rv.get("outcomes") or [] if x.get("name") == outcome), None)
            t = next((x for x in (o or {}).get("trials") or [] if _pid(x.get("id") or x.get("label")) == pmid), None)
            if t:
                judged = {"commit": c[:12], **trial_fingerprint(t)}
        row["judged"] = judged
    return out


def main(argv):
    p = os.path.join(ROOT, PATH)
    doc = json.load(open(p, encoding="utf-8"))
    new = bound(doc)
    if "--check" in argv:
        ok = new == doc
        print("definition_audit.json binding:", "CURRENT" if ok else "STALE (run without --check)")
        return 0 if ok else 1
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(new, indent=1, ensure_ascii=False) + "\n")
    print("bound", sum(1 for r in new["by_row"].values() if "commit" in r["judged"]), "of", len(new["by_row"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
