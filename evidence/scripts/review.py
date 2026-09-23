"""Apply the lane's hand review to a draft and submit it through adjudicate.py (which re-verifies every span).
Usage: python review.py KEY ENTRY_RULING "reviewed note" [--ruling R] [--reason "..."]"""
import json, os, sys, subprocess, argparse
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ap = argparse.ArgumentParser()
ap.add_argument("key"); ap.add_argument("entry", choices=["ESTABLISHED", "PARTLY", "NOT_ESTABLISHED", "CONTRADICTED"])
ap.add_argument("note"); ap.add_argument("--ruling"); ap.add_argument("--reason")
a = ap.parse_args()
p = os.path.join(ROOT, f"evidence/adjudication/drafts/{a.key}.json")
d = json.load(open(p, encoding="utf-8"))
d["entry_population"]["lane_ruling"] = a.entry
d["reviewed_note"] = a.note
if a.ruling: d["ruling"] = a.ruling
d["reason"] = a.reason or d.get("reason") or a.note
json.dump(d, open(p, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
sys.exit(subprocess.call([sys.executable, "-W", "ignore", os.path.join(ROOT, "evidence/scripts/adjudicate.py"), p]))
