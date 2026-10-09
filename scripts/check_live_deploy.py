"""Fetch the live site and compare it, byte for byte, with a commit: is that commit what the site serves?

  python scripts/check_live_deploy.py --commit <sha> --out live_check.json

For every docs/reviews/<slug>/index.html and docs/audit/index.html at the commit: GET the served URL, sha256 the body,
compare with the committed blob. Records the time, the commit, per-URL status and match, and whether the served review
pages carry the rapidmeta-v1 tab contract. A network error is recorded as such, never as a match.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://mahmood726-cyber.github.io/meta-harness/"


def git(*a, binary=False):
    p = subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, check=True)
    return p.stdout if binary else p.stdout.decode("utf-8", "replace")


def fetch(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"Cache-Control": "no-cache"}), timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:  # noqa: BLE001 -- recorded, never treated as a match
        return f"ERROR {type(e).__name__}", b""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    c = git("rev-parse", a.commit).strip()
    paths = sorted(p for p in git("ls-tree", "-r", "--name-only", c, "docs/reviews").split() if p.endswith("/index.html"))
    paths.append("docs/audit/index.html")
    rows = []
    for p in paths:
        try:
            want = git("show", f"{c}:{p}", binary=True)
        except subprocess.CalledProcessError:
            want = None
        status, body = fetch(SITE + p[len("docs/"):])
        rows.append({"path": p, "status": status, "committed": want is not None,
                     "match": want is not None and status == 200 and hashlib.sha256(body).digest() == hashlib.sha256(want).digest(),
                     "tab_contract": b"<meta name='tab-contract' content='rapidmeta-v1'>" in body})
    reviews = [r for r in rows if r["path"].startswith("docs/reviews/")]
    out = {"commit": c, "checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "reviews_match": sum(r["match"] for r in reviews), "reviews_n": len(reviews),
           "reviews_with_tab_contract": sum(r["tab_contract"] for r in reviews),
           "audit_status": next(r["status"] for r in rows if r["path"] == "docs/audit/index.html"),
           "audit_match": next(r["match"] for r in rows if r["path"] == "docs/audit/index.html"), "rows": rows}
    out["live"] = out["reviews_match"] == out["reviews_n"] and out["audit_match"]
    Path(a.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"{out['reviews_match']}/{out['reviews_n']} review pages match {c[:12]}; tab contract on {out['reviews_with_tab_contract']}; "
          f"/audit/ {out['audit_status']} match={out['audit_match']}; LIVE={out['live']}")
    return 0 if out["live"] else 1


if __name__ == "__main__":
    sys.exit(main())
