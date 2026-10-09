"""V13-04Q pre-screen (scratch, run in F:/captain3-k1): which NOT_CC / UNKNOWN tracked full texts does a SERVED number depend on?
Per topic: delete the candidate files in the working tree, rebuild the topic, diff every served number against HEAD's review.json,
then restore the tree. A topic with any served change is bisected file by file. Writes v13_04_prescreen.json beside this script."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "registry", "v13_04_prescreen.json")
ENV = dict(os.environ, PYTHONIOENCODING="utf-8", AACT_SNAPSHOT="F:/AACT-storage/AACT/2026-08-30",
           AACT_DIR="F:/AACT-storage/AACT/2026-08-30")
KEYS = ("k", "estimate", "ci_low", "ci_high", "tau2")
TK = ("label", "effect", "ci_low", "ci_high", "ai", "n1i", "ci", "n2i", "mean1", "mean2", "e1i", "e2i")


def git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True, encoding="utf-8", errors="replace")


def served(review):
    out = {}
    for o in review.get("outcomes") or []:
        res = o.get("result") or {}
        out[o["name"]] = ({k: res.get(k) for k in KEYS}, [tuple(t.get(k) for k in TK) for t in o.get("trials") or []],
                          o.get("served_estimand"))
    return out


def tree_clean():
    return git("status", "--porcelain", "--untracked-files=all").stdout.strip() == ""


def run_slug(slug, files):
    """Delete the candidates, rebuild, read the served numbers, and ALWAYS restore (codex v13-04-r1 P2). Every candidate must
    exist before anything is deleted; the caller guarantees a clean tree, so restoring the whole tree touches nothing else."""
    missing = [f for f in files if not os.path.exists(os.path.join(ROOT, f))]
    if missing:
        return 2, f"candidate(s) missing: {missing}", None
    try:
        for f in files:
            os.remove(os.path.join(ROOT, f))
        p = subprocess.run([sys.executable, "scripts/build_topic.py", slug, "--now", "2026-09-11"], cwd=ROOT, env=ENV,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        after = None
        if p.returncode == 0:
            after = served(json.load(open(os.path.join(ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8")))
        return p.returncode, (p.stderr or p.stdout)[-400:], after
    finally:
        git("checkout", "-q", "--", ".")
        git("clean", "-fdq", "docs", "outputs", "registry/build_deps")


def diff(before, after):
    if after is None:
        return ["BUILD FAILED"]
    d = []
    for name in sorted(set(before) | set(after)):
        if before.get(name) != after.get(name):
            d.append({"outcome": name, "before": before.get(name), "after": after.get(name)})
    return d


def main():
    if not tree_clean():
        sys.exit("refusing: the tree is not clean -- the pre-screen restores by checkout and would discard unrelated work")
    led = json.load(open(os.path.join(ROOT, "registry", "tracked_fulltext_licences.json"), encoding="utf-8"))
    cand = {}
    for r in led["rows"]:
        if r["verdict"] in ("NOT_CC", "UNKNOWN"):
            cand.setdefault(r["slug"], []).append(r["file"])
    report = {}
    for slug, files in sorted(cand.items()):
        rv = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
        if not os.path.exists(rv):
            report[slug] = {"files": files, "state": "NO_SERVED_REVIEW"}
            continue
        before = served(json.load(open(rv, encoding="utf-8")))
        rc, tail, after = run_slug(slug, files)
        d = diff(before, after)
        entry = {"files": files, "rc": rc, "served_changes": d}
        if d:
            entry["per_file"] = {}
            for f in files:
                rc1, _, a1 = run_slug(slug, [f])
                entry["per_file"][f] = diff(before, a1)
        report[slug] = entry
        print(slug, len(files), "changes" if d else "none", flush=True)
        json.dump(report, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
    print("DONE")


if __name__ == "__main__":
    main()
