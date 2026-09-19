"""Landing hash check: a landing that touches a review must MOVE that review's OBJECT hash, and the chain must name
old and new. `manifest.json commit_sha` is a container property; `html_sha256` is the wrapper; only `review_sha256`
says whether the review object a reader is reviewing changed. Two landings on 2026-09-17 were reported as corrections
while the served review object was unchanged (D 3cf73885) or read from a stale surface -- and on 2026-09-18 this
script itself certified increment 2 (237e9094 -> 75cc9a46) as "32 MOVED ... PASS" while review_sha256 was identical
on 32 of 32: it had read html movement as content movement, a container property read as a contents property (found
by Dispatch on fetched bytes and by the parallel workshop; plant kept in outputs/audit/landing_hash_check_plant_prefix_2026-09-19.txt).

Per touched review the verdict is one of:
  OBJECT_MOVED   review_sha256 old != new (the html normally moves with it)
  WRAPPER_ONLY   review_sha256 identical, html_sha256 moved -- a rendering-only change; REFUSED unless the landing
                 declares it with --allow-wrapper-only SLUG (a rendering fix that leaves the object alone must say so)
  UNCHANGED      neither moved -- REFUSED (a touched review that did not change is serialisation noise or a mistake)
--require-change SLUG ... : that review's OBJECT must move (touched-but-wrapper-only and untouched both refuse).

Usage: python scripts/landing_hash_check.py <prev_commit> <new_commit> [--require-change SLUG ...]
                                             [--allow-wrapper-only SLUG ...]
Exit 1 on any refusal. Every line names old -> new review_sha256 and html_sha256.
"""
import json
import subprocess
import sys

OBJECT_MOVED = "OBJECT_MOVED"
WRAPPER_ONLY = "WRAPPER_ONLY"
UNCHANGED = "UNCHANGED"


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


def classify(prev_manifest: dict, new_manifest: dict) -> dict:
    """The verdict for one review from its two committed manifests. Pure: the OBJECT hash decides."""
    ra = prev_manifest.get("review_sha256") or ""
    rb = new_manifest.get("review_sha256") or ""
    ha = prev_manifest.get("html_sha256") or ""
    hb = new_manifest.get("html_sha256") or ""
    if ra != rb:
        verdict = OBJECT_MOVED
    elif ha != hb:
        verdict = WRAPPER_ONLY
    else:
        verdict = UNCHANGED
    return {"verdict": verdict, "review_old": ra, "review_new": rb, "html_old": ha, "html_new": hb}


def _parse(argv):
    prev, new = argv[0], argv[1]
    required, allowed = [], []
    bucket = None
    for a in argv[2:]:
        if a == "--require-change":
            bucket = required
        elif a == "--allow-wrapper-only":
            bucket = allowed
        elif bucket is not None:
            bucket.append(a)
    return prev, new, required, allowed


def check(prev, new, touched, manifests, required=(), allowed=()):
    """Verdicts for a landing. `manifests(ref, slug)` -> committed manifest dict. Returns (ok, lines, refusals)."""
    lines, refusals = [], []
    lines.append(f"landing {prev[:8]} -> {new[:8]}: {len(touched)} review(s) touched")
    verdicts = {}
    for slug in touched:
        v = classify(manifests(prev, slug), manifests(new, slug))
        verdicts[slug] = v
        tag = v["verdict"]
        if tag == WRAPPER_ONLY and slug in allowed:
            tag = "WRAPPER_ONLY (declared)"
        lines.append(f"  {slug:45s} review_sha256 {v['review_old'][:16] or '-':16s} -> {v['review_new'][:16] or '-':16s}  "
                     f"html_sha256 {v['html_old'][:16] or '-':16s} -> {v['html_new'][:16] or '-':16s}  {tag}")
        if v["verdict"] == UNCHANGED:
            refusals.append(f"{slug}: touched but review object and html unchanged")
        elif v["verdict"] == WRAPPER_ONLY and slug not in allowed:
            refusals.append(f"{slug}: html moved but review_sha256 {v['review_old'][:16]} is unchanged -- a rendering-only "
                            f"change must be declared with --allow-wrapper-only {slug}")
    for slug in required:
        v = verdicts.get(slug)
        if v is None:
            refusals.append(f"{slug}: REQUIRED to change but not touched by this landing")
        elif v["verdict"] != OBJECT_MOVED:
            refusals.append(f"{slug}: REQUIRED to change but review_sha256 {v['review_old'][:16]} -> {v['review_new'][:16]} "
                            f"is unchanged ({v['verdict']})")
        else:
            lines.append(f"  REQUIRED {slug}: review_sha256 {v['review_old'][:16]} -> {v['review_new'][:16]} OBJECT_MOVED")
    return (not refusals), lines, refusals


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    prev, new, required, allowed = _parse(argv)
    files = subprocess.run(["git", "diff", "--name-only", prev, new], capture_output=True, text=True, encoding="utf-8").stdout.split()
    touched = sorted({f.split("/")[2] for f in files if f.startswith("docs/reviews/") and f.count("/") >= 3})
    ok, lines, refusals = check(prev, new, touched, _manifest, required, allowed)
    for line in lines:
        print(line)
    if not ok:
        print(f"LANDING HASH CHECK REFUSED: {len(refusals)} review(s):")
        for r in refusals:
            print(f"  {r}")
        return 1
    print("LANDING HASH CHECK PASS: every touched review moved its OBJECT hash (or declared a wrapper-only change by name)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
