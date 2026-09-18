"""Landing hash check: a landing that touches a review must MOVE that review's content hash, and the chain must name
old and new. `manifest.json commit_sha` is a container property; only `review_sha256` / `html_sha256` say whether the
reader's page changed. Two landings on 2026-09-17 were reported as corrections while the served review object was
unchanged (D 3cf73885) or read from a stale surface -- this script settles that in one line.

Usage: python scripts/landing_hash_check.py <prev_commit> <new_commit> [--require-change SLUG ...]
Prints, for every review whose files the commit touched, old -> new review_sha256 and html_sha256 (from the committed
manifests). Exit 1 if a touched review's manifest shows neither hash moved, or if any --require-change slug is unchanged.
"""
import json
import subprocess
import sys


def _show(ref, path):
    p = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True, encoding="utf-8")
    return p.stdout if p.returncode == 0 else None


def _manifest(ref, slug):
    txt = _show(ref, f"docs/reviews/{slug}/manifest.json")
    if not txt:
        return {}
    try:
        return json.loads(txt)
    except ValueError:
        return {}


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    prev, new = argv[0], argv[1]
    required = []
    if "--require-change" in argv:
        required = argv[argv.index("--require-change") + 1:]
    files = subprocess.run(["git", "diff", "--name-only", prev, new], capture_output=True, text=True, encoding="utf-8").stdout.split()
    touched = sorted({f.split("/")[2] for f in files if f.startswith("docs/reviews/") and f.count("/") >= 3})
    bad = []
    print(f"landing {prev[:8]} -> {new[:8]}: {len(touched)} review(s) touched of 32")
    for slug in touched:
        a, b = _manifest(prev, slug), _manifest(new, slug)
        ra, rb = (a.get("review_sha256") or "")[:16], (b.get("review_sha256") or "")[:16]
        ha, hb = (a.get("html_sha256") or "")[:16], (b.get("html_sha256") or "")[:16]
        moved = (ra != rb) or (ha != hb)
        print(f"  {slug:45s} review_sha256 {ra or '-':16s} -> {rb or '-':16s}  html_sha256 {ha or '-':16s} -> {hb or '-':16s}  {'MOVED' if moved else 'UNCHANGED'}")
        if not moved:
            bad.append(slug)
    for slug in required:
        if slug not in touched:
            bad.append(slug)
            print(f"  {slug}: REQUIRED to change but not touched by this landing")
    if bad:
        print(f"LANDING HASH CHECK REFUSED: {len(bad)} review(s) touched or required without a content-hash change: {', '.join(bad)}")
        return 1
    print("LANDING HASH CHECK PASS: every touched review moved its content hash")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
