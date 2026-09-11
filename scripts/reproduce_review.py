"""The standing reproduction test: a review is reproducible iff re-running the pipeline from
its committed protocol + cache regenerates the served page byte-for-byte.

    python scripts/reproduce_review.py                 # replay every live review in-place
    python scripts/reproduce_review.py <slug>          # one review
    python scripts/reproduce_review.py --fresh-clone    # gold standard: git clone HEAD to a
                                                        # temp dir, rebuild, byte-compare pages

Replay mode (default) is Level B: from the COMMITTED cache + protocol SHA it re-runs
build_review_core -> render_page and checks the regenerated review_sha256 and the served
index.html against what is committed. This proves the NUMBERS (not just the HTML) regenerate
deterministically — every capability (round-trip validation, dedup, CT.gov guard, extraction)
has to survive it. Fresh-clone mode is the same claim end to end from a clean checkout.

Exit code 0 iff every reviewed page reproduces; non-zero (and a printed diff) otherwise. This
is meant to be run in CI and mirrors what the pre-commit gate enforces per page.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from harness import fetch  # noqa: E402
from harness.canonical import review_sha256, sha256_text  # noqa: E402
from harness.pipeline import build_review_core  # noqa: E402
from harness.page import render_page  # noqa: E402


def _protocol_sha(slug):
    out = subprocess.check_output(
        ["git", "-C", ROOT, "log", "-1", "--format=%H", "--", f"protocols/{slug}.md"], text=True).strip()
    return out or None


def replay_core(slug):
    """Re-run the pipeline from the committed cache + protocol SHA (no network)."""
    config = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    records = fetch.ensure(config, "")  # committed cache is present -> no network
    return build_review_core(slug, config, records, _protocol_sha(slug))


def reproduce(slug):
    """Return (ok, reasons). Regenerate the core + page and compare to what is committed."""
    d = os.path.join(ROOT, "docs", "reviews", slug)
    manifest = json.load(open(os.path.join(d, "manifest.json"), encoding="utf-8"))
    served = open(os.path.join(d, "index.html"), encoding="utf-8").read()
    reasons = []

    core = replay_core(slug)
    regen_sha = review_sha256(core)
    if regen_sha != manifest.get("review_sha256"):
        reasons.append(f"review_sha256 mismatch: replay {regen_sha} vs committed {manifest.get('review_sha256')} "
                       "(the pipeline no longer regenerates the committed numbers)")

    # Render the served page exactly as build_topic does: core + reproduction block.
    final = dict(core, reproduction={"failures": 0, "protocol_sha": _protocol_sha(slug),
                                     "review_sha256": regen_sha, "from_cache": True})
    if sha256_text(render_page(final)) != sha256_text(served):
        reasons.append("served index.html does not byte-match a re-render from the replayed core")
    return (not reasons), reasons


def _fresh_clone_check():
    import tempfile
    import shutil
    head = subprocess.check_output(["git", "-C", ROOT, "rev-parse", "HEAD"], text=True).strip()
    tmp = tempfile.mkdtemp(prefix="mh-repro-")
    try:
        subprocess.check_call(["git", "clone", "-q", ROOT, tmp])
        subprocess.check_call(["git", "-C", tmp, "checkout", "-q", head])
        slugs = sorted(os.listdir(os.path.join(ROOT, "docs", "reviews")))
        bad = []
        for slug in slugs:
            subprocess.check_call([sys.executable, os.path.join(tmp, "scripts", "build_topic.py"),
                                   slug, "--now", "2026-09-11"], cwd=tmp,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            a = open(os.path.join(ROOT, "docs", "reviews", slug, "index.html"), encoding="utf-8").read()
            b = open(os.path.join(tmp, "docs", "reviews", slug, "index.html"), encoding="utf-8").read()
            ok = sha256_text(a) == sha256_text(b)
            print(f"  {'OK ' if ok else 'DIFF'} {slug}")
            if not ok:
                bad.append(slug)
        return bad
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    if "--fresh-clone" in argv:
        print("FRESH-CLONE reproduction (git clone HEAD -> rebuild -> byte-compare):")
        bad = _fresh_clone_check()
        print(f"\n{'REPRODUCIBLE' if not bad else 'NOT REPRODUCIBLE: ' + ', '.join(bad)}")
        return 1 if bad else 0
    slugs = [a for a in argv if not a.startswith("-")] or sorted(os.listdir(os.path.join(ROOT, "docs", "reviews")))
    bad = []
    for slug in slugs:
        ok, reasons = reproduce(slug)
        print(f"  {'OK ' if ok else 'FAIL'} {slug}" + ("" if ok else ": " + "; ".join(reasons)))
        if not ok:
            bad.append(slug)
    print(f"\n{len(slugs) - len(bad)}/{len(slugs)} reproduce" + (f" — FAILED: {', '.join(bad)}" if bad else " (all reproducible)"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
