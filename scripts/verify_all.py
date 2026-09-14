"""ONE STANDARD. The complete verification a commit must pass, executed identically by the local
pre-commit hook and by CI (.github/workflows/verify.yml). Before 2026-09-14 the two disagreed: the hook
ran no unit tests and gated only STAGED pages; CI ran no index-currency check -- so a hand-edited
docs/index.html (a served page) passed CI and would have deployed, and a failing test committed
cleanly from a hooked clone. Evidence: evidence/gate-authority-2026-09-14/08-*, 09-*.

Every limb runs (no early exit) so one run names every refusal. Fail-closed: a limb that cannot
execute is a REFUSAL, not a skip. Exit 0 only when every limb is PASS.

Usage: python scripts/verify_all.py            (from the repo root; prints a ledger, exits 0/1)
"""
from __future__ import annotations
import glob
import io
import os
import subprocess
import sys
import time

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PASS, REFUSED, NOEXEC = "PASS", "REFUSED", "COULD-NOT-EXECUTE"


def _run(cmd):
    """Run a subprocess from ROOT; return (returncode, combined output)."""
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def limb_unit_tests():
    rc, out = _run([sys.executable, "-m", "pytest", "tests/", "-q"])
    tail = "\n".join(out.strip().splitlines()[-15:])
    return (PASS if rc == 0 else REFUSED), tail


def limb_reproduction():
    rc, out = _run([sys.executable, os.path.join("scripts", "reproduce_review.py")])
    tail = "\n".join(out.strip().splitlines()[-40:])
    return (PASS if rc == 0 else REFUSED), tail


def limb_gate_every_page():
    from harness.gate import gate_page
    dirs = sorted(d for d in glob.glob(os.path.join(ROOT, "docs", "reviews", "*"))
                  if os.path.isfile(os.path.join(d, "review.json")))
    if not dirs:
        return NOEXEC, "no docs/reviews/*/review.json found -- nothing gated is a refusal, not a pass"
    bad = []
    for d in dirs:
        ok, reasons = gate_page(d)
        if not ok:
            bad.append(f"{os.path.basename(d)}: " + "; ".join(reasons))
    return (PASS if not bad else REFUSED), (f"{len(dirs)} pages gated" if not bad else "\n".join(bad))


def limb_index_currency():
    # The index is generated, never hand-maintained: the committed docs/index.html must equal build_index.
    from harness.index import build_index
    want = build_index(os.path.join(ROOT, "docs"))
    p = os.path.join(ROOT, "docs", "index.html")
    try:
        cur = io.open(p, encoding="utf-8").read()
    except OSError as exc:
        return REFUSED, f"docs/index.html unreadable: {exc}"
    if cur != want:
        return REFUSED, ("docs/index.html is stale or hand-edited (differs from build_index). "
                         "Regenerate & stage: python -m harness.index docs && git add docs/index.html")
    return PASS, "generated index == committed docs/index.html"


def limb_leak_scan():
    # Also enforced by tests/test_leakscan.py::test_shipped_corpus_has_no_suppressed_leak (unit tests);
    # named here so a leak is refused under its own name, not as a test-failure line.
    from harness.leakscan import scan
    leaks = scan(os.path.join(ROOT, "docs"))
    if leaks:
        return REFUSED, "\n".join(f"{lk['artefact']}: {lk['slug']} {lk['leak']} (states {lk['states']})"
                                  for lk in leaks)
    return PASS, "no served aggregate publishes a pooled statistic for a suppressed-state topic"


def limb_heldout():
    from harness import heldout
    ok, reasons = heldout.check(ROOT)
    if not ok:
        verdict = NOEXEC if heldout.MISSING_KEY_REASON in reasons else REFUSED
        return verdict, "\n".join(reasons)
    registry = heldout.load(ROOT)
    _, detail = heldout.measurement_current(ROOT, registry)
    return PASS, detail


def limb_fixstate():
    from harness import fixstate
    registry = fixstate.load(ROOT)
    ok, reasons = fixstate.check(ROOT)
    if not ok:
        return REFUSED, "\n".join(reasons)
    if registry.get("enforced_since") is None:
        return PASS, "registry/fixstate.json enforced_since is null; commit scan inert; ledgers pass"
    return PASS, "registry/fixstate.json commit scan and ledgers pass"


def limb_honest_ratchet():
    from harness import honest_ratchet
    ok, reasons = honest_ratchet.check(ROOT)
    if ok:
        return PASS, "rendered honest-state marker counts did not decrease"
    detail = "\n".join(reasons)
    verdict = NOEXEC if any(str(r).startswith(NOEXEC) for r in reasons) else REFUSED
    return verdict, detail


LIMBS = [
    ("unit tests (pytest tests/)", limb_unit_tests),
    ("offline reproduction (every live page replays from committed cache)", limb_reproduction),
    ("publication gate on every live review page", limb_gate_every_page),
    ("index currency (generated == committed docs/index.html)", limb_index_currency),
    ("served-artefact leak scan (docs/*.json)", limb_leak_scan),
    ("held-out leak detector (registry/heldout_sealed.json)", limb_heldout),
    ("fix-state discipline (registry/fixstate.json)", limb_fixstate),
    ("honest-state ratchet (no page may get quieter)", limb_honest_ratchet),
]


def main():
    print(f"VERIFY-ALL: {len(LIMBS)} limbs, all run, fail-closed. root={ROOT}")
    results = []
    for name, fn in LIMBS:
        t0 = time.time()
        try:
            verdict, detail = fn()
        except Exception as exc:  # a limb that blows up has NO verdict -> refusal
            verdict, detail = NOEXEC, f"{type(exc).__name__}: {exc}"
        dt = time.time() - t0
        results.append((name, verdict, detail))
        print(f"  [{verdict:>17}] {name}  ({dt:.0f}s)")
        if verdict != PASS:
            for line in str(detail).splitlines():
                print(f"        {line}")
    n_bad = sum(1 for _, v, _ in results if v != PASS)
    if n_bad:
        print(f"VERIFY-ALL: REFUSED -- {n_bad} of {len(LIMBS)} limbs not PASS. Fix the harness, never the gate.")
        return 1
    print(f"VERIFY-ALL: all {len(LIMBS)} limbs PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
