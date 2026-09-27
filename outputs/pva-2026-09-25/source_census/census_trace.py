"""For each (file, pmid) given, walk every commit that touched the file (oldest first) and record each time the held
abstract's bytes CHANGED: the commit, its date and subject, and the non-cache files it changed (the code path)."""
import hashlib
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = "C:/mh-lanes/pva"


def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


targets = [t.split(":") for t in sys.argv[1].split(",")]      # file:pmid,...
report = []
for f, pmid in targets:
    commits = git("log", "--all", "--format=%H", "--reverse", "--", f).split()
    prev, events = None, []
    for c in commits:
        raw = git("show", f"{c}:{f}")
        if not raw:
            continue
        try:
            d = json.loads(raw)
        except ValueError:
            continue
        rec = next((r for r in d.get("records", []) if str(r.get("id")) == pmid), None) if isinstance(d, dict) else None
        ab = rec.get("abstract") if rec else None
        h = hashlib.sha256(ab.encode()).hexdigest()[:12] if ab is not None else None
        if h != prev:
            meta = git("show", "-s", "--format=%h|%ad|%an|%s", "--date=format:%Y-%m-%d %H:%M", c).strip()
            touched = [p for p in git("show", "--name-only", "--format=", c).split() if not p.startswith(("cache/", "docs/"))]
            events.append({"commit": meta, "abstract_sha": h, "len": len(ab) if ab else None,
                           "labelled": bool(ab and ab.split(":")[0].isupper()), "code_touched": touched[:12],
                           "branches": git("branch", "-r", "--contains", c).split()[:4]})
            prev = h
    report.append({"file": f, "pmid": pmid, "events": events})
    print(f"\n### {f} PMID {pmid}: {len(commits)} commits touch the file; abstract changed {len(events)} time(s)")
    for e in events:
        print(f"  {e['commit'][:150]}\n     abstract {e['abstract_sha']} len {e['len']} labelled={e['labelled']} code={e['code_touched'][:6]}")
json.dump(report, open(sys.argv[2], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
