"""Landing hash check: a landing that touches a review must MOVE that review's OBJECT hash, and the chain must name old and new.

`manifest.json commit_sha` is a container property; `html_sha256` is the WRAPPER's bytes (renderer, CSS, banners); only
`review_sha256` says whether the review OBJECT a reader is being shown changed. Two landings on 2026-09-17 were reported as
corrections while the served review object was unchanged (D 3cf73885) or read from a stale surface. On 2026-09-18 the first
version of this script counted an html-only movement as MOVED (`(ra != rb) or (ha != hb)`) and `--require-change` only checked
that the slug was TOUCHED -- so a landing that changed only the page wrapper was certified "32 MOVED" (measured on 75cc9a46:
glp1 html fede8d29 -> 72fadf26, review_sha256 98726cc1 -> 98726cc1). That is the container-as-contents defect this script exists
to catch; the plant in tests/test_landing_hash_check.py holds it.

Rule (Mahmood, 18 Sep): per review, assert `review_sha256` old -> new with BOTH values named. Never a count. Never an html hash.
Never an aggregate. A landing claiming to change a review whose object hash is identical FAILS.

Usage: python scripts/landing_hash_check.py <prev_commit> <new_commit> [--require-change SLUG ...] [--allow-wrapper-only SLUG ...]
Exit 1 if any touched review's review_sha256 is unchanged, or any --require-change slug's review_sha256 is unchanged (touched or not).
`--allow-wrapper-only SLUG` is the ONLY way to land a renderer-only change to SLUG: it must be declared per review, by name, and is
printed as WRAPPER-ONLY (never as MOVED); it cannot be combined with --require-change for the same slug.
"""
import json
import subprocess
import sys


def _show(ref, path, cwd=None):
    p = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True, encoding="utf-8", cwd=cwd)
    return p.stdout if p.returncode == 0 else None


def _manifest(ref, slug, cwd=None):
    txt = _show(ref, f"docs/reviews/{slug}/manifest.json", cwd=cwd)
    if not txt:
        return {}
    try:
        return json.loads(txt)
    except ValueError:
        return {}


def check(prev, new, required=(), wrapper_only=(), cwd=None, out=print):
    """Return (exit_code, rows). Each row: (slug, review_old, review_new, verdict). Verdict is per review, never aggregated:
    MOVED (review_sha256 differs), UNCHANGED (identical -> refusal unless declared wrapper-only), WRAPPER-ONLY (declared),
    MISSING (no manifest on one side)."""
    files = subprocess.run(["git", "diff", "--name-only", prev, new], capture_output=True, text=True, encoding="utf-8",
                           cwd=cwd).stdout.split()
    touched = sorted({f.split("/")[2] for f in files if f.startswith("docs/reviews/") and f.count("/") >= 3})
    required = list(required)
    wrapper_only = set(wrapper_only)
    both = sorted(set(required) & wrapper_only)
    if both:
        out(f"LANDING HASH CHECK REFUSED: {', '.join(both)} declared both --require-change and --allow-wrapper-only")
        return 1, []
    rows, bad = [], []
    out(f"landing {prev[:8]} -> {new[:8]}: per-review review_sha256 (the OBJECT; html_sha256 is the wrapper and is not a verdict input)")
    for slug in sorted(set(touched) | set(required)):
        a, b = _manifest(prev, slug, cwd), _manifest(new, slug, cwd)
        ra, rb = (a.get("review_sha256") or ""), (b.get("review_sha256") or "")
        ha, hb = (a.get("html_sha256") or "")[:16], (b.get("html_sha256") or "")[:16]
        if not ra or not rb:
            verdict = "MISSING"
        elif ra != rb:
            verdict = "MOVED"
        elif slug in wrapper_only:
            verdict = "WRAPPER-ONLY"
        else:
            verdict = "UNCHANGED"
        rows.append((slug, ra, rb, verdict))
        out(f"  {slug:45s} review_sha256 {ra[:16] or '-':16s} -> {rb[:16] or '-':16s}  {verdict}"
            f"   (html {ha or '-'} -> {hb or '-'}, informational)")
        if verdict == "UNCHANGED" and slug in touched:
            bad.append(f"{slug}: touched but review_sha256 unchanged ({ra[:16]})")
        if verdict == "MISSING":
            bad.append(f"{slug}: manifest missing on one side")
        if slug in required and verdict != "MOVED":
            bad.append(f"{slug}: REQUIRED to change but review_sha256 {verdict.lower()} ({ra[:16]} -> {rb[:16] or '-'})")
    for line in bad:
        out("  REFUSAL " + line)
    if bad:
        out("LANDING HASH CHECK REFUSED: a review named above did not move its review_sha256")
        return 1, rows
    out("LANDING HASH CHECK PASS: every touched review moved its review_sha256 (each named above)")
    return 0, rows


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    prev, new = argv[0], argv[1]
    rest = argv[2:]
    required, wrapper_only, mode = [], [], None
    for tok in rest:
        if tok == "--require-change":
            mode = "req"
        elif tok == "--allow-wrapper-only":
            mode = "wrap"
        elif mode == "req":
            required.append(tok)
        elif mode == "wrap":
            wrapper_only.append(tok)
        else:
            print(f"unexpected argument {tok!r}")
            return 2
    code, _rows = check(prev, new, required, wrapper_only)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
