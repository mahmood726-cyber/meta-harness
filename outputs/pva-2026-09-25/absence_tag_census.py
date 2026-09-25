"""PVA-D15 census: does harness/absence.py's tag strip (_TAG = '<[^>]+>') manufacture SERVED absence claims?
A literal '<' in an abstract ('P<0.001') opens a fake tag that deletes text up to the next '>' -- and _strip_markup runs on any
text containing '<', abstracts included (its docstring says the abstract path is a no-op; the guard is `"<" not in text`).
For every served declared_absent entry on <commit>: take its record's abstract; if the defective strip deletes non-space text,
re-run the harness's own _outcome_number_present with the defective and the corrected strip (real tags only: '<' + letter,
'/' or '!'), using the outcome's configured keywords. A FLIP (defective: no number, corrected: number present) is a served
absence manufactured by the defect. usage: absence_tag_census.py <worktree_at_commit> <commit>"""
import json
import re
import subprocess
import sys
from pathlib import Path

WT, C = Path(sys.argv[1]).resolve(), sys.argv[2]
sys.path[:0] = [str(WT)]
sys.dont_write_bytecode = True
from harness import absence  # noqa: E402

DEFECT = re.compile(r"<[^>]+>")
FIXED = re.compile(r"<(?=[A-Za-z/!])[^>]*>")
assert absence._TAG.pattern == DEFECT.pattern, f"harness _TAG is {absence._TAG.pattern!r}, not the defective pattern"
git = lambda *a: subprocess.run(["git", "-C", "C:/mh-lanes/pva", *a], capture_output=True, stdin=subprocess.DEVNULL).stdout  # noqa: E731


def present(text, kws, tag):
    absence._TAG = tag
    try:
        return absence._outcome_number_present(text, kws)
    finally:
        absence._TAG = DEFECT


def nonspace(s):
    return len(re.sub(r"\s+", "", s))


slugs = [n.split("/")[-1] for n in git("ls-tree", "--name-only", C, "docs/reviews/").decode().split()]
tot = with_lt = deleting = flips = no_abs = 0
flip_list, delete_list = [], []
for slug in slugs:
    rv_raw = git("show", f"{C}:docs/reviews/{slug}/review.json")
    rec_raw = git("show", f"{C}:cache/{slug}/records.json")
    top_raw = git("show", f"{C}:topics/{slug}.json")
    if not rv_raw or not rec_raw:
        continue
    rv, recs = json.loads(rv_raw), json.loads(rec_raw)["records"]
    by_id = {str(r.get("id")): r for r in recs}
    kw_by_outcome = {}
    if top_raw:
        top = json.loads(top_raw)
        for o in top.get("outcomes", []):
            if isinstance(o, dict) and o.get("name"):
                kw_by_outcome[o["name"]] = o.get("keywords") or o.get("terms") or [o["name"]]
    for o in rv.get("outcomes", []):
        kws = kw_by_outcome.get(o["name"]) or [o["name"]]
        for a in o.get("declared_absent_trials") or []:
            tot += 1
            pid = str(a.get("id") or a.get("label") or "").replace("PMID ", "")
            ab = (by_id.get(pid) or {}).get("abstract")
            if not ab:
                no_abs += 1
                continue
            if "<" not in ab:
                continue
            with_lt += 1
            if nonspace(DEFECT.sub(" ", ab)) < nonspace(FIXED.sub(" ", ab)):
                deleting += 1
                lost = nonspace(FIXED.sub(" ", ab)) - nonspace(DEFECT.sub(" ", ab))
                delete_list.append((slug, o["name"], pid, a.get("reason_code") or a.get("state"), lost))
                d, f = present(ab, kws, DEFECT), present(ab, kws, FIXED)
                if (not d) and f:
                    flips += 1
                    flip_list.append((slug, o["name"], pid, a.get("reason_code") or a.get("state"), a.get("absent_kind")))
print(f"{C[:12]}: served declared_absent entries {tot}; abstract not held {no_abs}; abstract contains '<' {with_lt}; "
      f"defective strip DELETES text {deleting}; absence decision FLIPS (number present once text restored) {flips}")
for x in delete_list[:25]:
    print("  deletes:", x)
for x in flip_list:
    print("  FLIP:", x)
