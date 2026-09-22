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

SCRIPT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(os.getcwd())
sys.path.insert(0, SCRIPT_ROOT)
from harness.target import TargetUnresolvable, describe_target, refusal as target_refusal  # noqa: E402

PASS, REFUSED, NOEXEC = "PASS", "REFUSED", "COULD-NOT-EXECUTE"


def _run(cmd):
    """Run a subprocess from ROOT; return (returncode, combined output)."""
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def _rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def _glob(rel_pattern):
    return sorted(_rel(p) for p in glob.glob(os.path.join(ROOT, *rel_pattern.split("/"))))


def _target(label, paths, refs=()):
    try:
        return describe_target(ROOT, refs=refs, paths=paths, label=label), None
    except TargetUnresolvable as exc:
        return target_refusal(label, str(exc)), str(exc)


def _append_target(target_line, detail):
    return target_line if not detail else target_line + "\n" + detail


def _target_tests():
    return _glob("tests/*.py")


def _target_review_pages():
    return sorted(
        _rel(os.path.join(d, "index.html"))
        for d in glob.glob(os.path.join(ROOT, "docs", "reviews", "*"))
        if os.path.isfile(os.path.join(d, "index.html"))
    )


def _target_review_objects():
    return sorted(
        _rel(os.path.join(d, "review.json"))
        for d in glob.glob(os.path.join(ROOT, "docs", "reviews", "*"))
        if os.path.isfile(os.path.join(d, "review.json"))
    )


def _target_evidence_files():
    out = []
    root = os.path.join(ROOT, "docs", "evidence")
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            out.append(_rel(os.path.join(dirpath, name)))
    return sorted(out)


def _target_docs_json():
    return _glob("docs/*.json")


def limb_unit_tests():
    target_line, err = _target("verify_all.limb_unit_tests", _target_tests())
    if err:
        return NOEXEC, target_line
    rc, out = _run([sys.executable, "-m", "pytest", "tests/", "-q"])
    tail = "\n".join(out.strip().splitlines()[-15:])
    return (PASS if rc == 0 else REFUSED), _append_target(target_line, tail)


def limb_reproduction():
    paths = [os.path.join("scripts", "reproduce_review.py"), *_target_review_objects()]
    target_line, err = _target("verify_all.limb_reproduction", paths)
    if err:
        return NOEXEC, target_line
    rc, out = _run([sys.executable, os.path.join("scripts", "reproduce_review.py")])
    tail = "\n".join(out.strip().splitlines()[-40:])
    return (PASS if rc == 0 else REFUSED), _append_target(target_line, tail)


def limb_gate_every_page():
    paths = _target_review_objects()
    target_line, err = _target("verify_all.limb_gate_every_page", paths)
    if err:
        return NOEXEC, target_line
    from harness.gate import gate_page
    dirs = sorted(d for d in glob.glob(os.path.join(ROOT, "docs", "reviews", "*"))
                  if os.path.isfile(os.path.join(d, "review.json")))
    if not dirs:
        return NOEXEC, _append_target(target_line, "no docs/reviews/*/review.json found -- nothing gated is a refusal, not a pass")
    bad = []
    for d in dirs:
        ok, reasons = gate_page(d)
        if not ok:
            bad.append(f"{os.path.basename(d)}: " + "; ".join(reasons))
    from harness.gate import admission_scope
    detail = (f"{len(dirs)} pages gated; " + admission_scope(dirs[0])) if not bad else "\n".join(bad)
    return (PASS if not bad else REFUSED), _append_target(target_line, detail)


def limb_index_currency():
    paths = ["docs/index.html", "docs/evidence/CAPTIONS.json", *_target_evidence_files()]
    target_line, err = _target("verify_all.limb_index_currency", paths)
    if err:
        return NOEXEC, target_line
    # The index is generated, never hand-maintained: the committed docs/index.html must equal build_index.
    from harness.index import build_index
    want = build_index(os.path.join(ROOT, "docs"))
    p = os.path.join(ROOT, "docs", "index.html")
    try:
        cur = io.open(p, encoding="utf-8").read()
    except OSError as exc:
        return REFUSED, _append_target(target_line, f"docs/index.html unreadable: {exc}")
    if cur != want:
        return REFUSED, _append_target(
            target_line,
            "docs/index.html is stale or hand-edited (differs from build_index). "
            "Regenerate & stage: python -m harness.index docs && git add docs/index.html",
        )
    # The evidence entry pages are generated from docs/evidence/CAPTIONS.json under the same rule: a capture with no
    # caption, a caption with no file, or a stale index page refuses (an auditor must never open an unexplained file).
    rc, out = _run([sys.executable, os.path.join("scripts", "build_evidence_index.py"), "--check"])
    if rc != 0:
        detail = out.strip().splitlines()[-1] if out.strip() else "evidence index check failed"
        return REFUSED, _append_target(target_line, detail)
    return PASS, _append_target(target_line, "generated index == committed docs/index.html; evidence indexes current")


def limb_leak_scan():
    paths = _target_docs_json() + _target_review_objects()
    target_line, err = _target("verify_all.limb_leak_scan", paths)
    if err:
        return NOEXEC, target_line
    # Also enforced by tests/test_leakscan.py::test_shipped_corpus_has_no_suppressed_leak (unit tests);
    # named here so a leak is refused under its own name, not as a test-failure line.
    from harness.leakscan import scan
    leaks = scan(os.path.join(ROOT, "docs"))
    if leaks:
        detail = "\n".join(f"{lk['artefact']}: {lk['slug']} {lk['leak']} (states {lk['states']})" for lk in leaks)
        return REFUSED, _append_target(target_line, detail)
    return PASS, _append_target(target_line, "no served aggregate publishes a pooled statistic for a suppressed-state topic")


def limb_heldout():
    paths = ["registry/heldout_sealed.json", "docs/search_recall_regression_corpus.json", "harness/acquisition.py"]
    target_line, err = _target("verify_all.limb_heldout", paths)
    if err:
        return NOEXEC, target_line
    from harness import heldout
    ok, reasons = heldout.check(ROOT)
    if not ok:
        verdict = NOEXEC if heldout.MISSING_KEY_REASON in reasons else REFUSED
        return verdict, _append_target(target_line, "\n".join(reasons))
    registry = heldout.load(ROOT)
    _, detail = heldout.measurement_current(ROOT, registry)
    return PASS, _append_target(target_line, detail)


def limb_search_completeness():
    """Search completeness as its own gated stage (SEARCH_REBUILD_HANDOVER item 4, 2026-09-15): the published
    search_v2 measurement must be current for the engine blob, every measurement topic and every source must carry
    an explicit state, and a zero may never come from an exit code. Reads artefacts only; never runs a search."""
    paths = ["registry/search_completeness.json", "harness/search_v2.py", "harness/search_completeness.py"]
    target_line, err = _target("verify_all.limb_search_completeness", paths)
    if err:
        return NOEXEC, target_line
    from harness import search_completeness
    ok, detail = search_completeness.check(ROOT)
    if not ok:
        return (NOEXEC if detail.startswith("COULD-NOT-EXECUTE") else REFUSED), _append_target(target_line, detail)
    return PASS, _append_target(target_line, detail)


def limb_fixstate():
    paths = ["registry/fixes.json", "docs/fix_ledger.json", "scripts/render_fix_ledger.py"]
    target_line, err = _target("verify_all.limb_fixstate", paths)
    if err:
        return NOEXEC, target_line
    from harness import fixstate
    ok, reasons = fixstate.check(ROOT)
    if not ok:
        return REFUSED, _append_target(target_line, "\n".join(reasons))
    registry = fixstate.load(ROOT)
    impl = {}
    verification = {}
    scope = {}
    freshness = {}
    for entry in fixstate.entries(registry):
        impl[entry["implementation"]] = impl.get(entry["implementation"], 0) + 1
        verification[entry["verification"]] = verification.get(entry["verification"], 0) + 1
        scope[entry["scope"]] = scope.get(entry["scope"], 0) + 1
        state = fixstate.freshness_state(entry, ROOT)
        freshness[state] = freshness.get(state, 0) + 1
    detail = (
        "implementation "
        + ", ".join(f"{value}={impl.get(value, 0)}" for value in fixstate.CONTROL_IMPLEMENTATIONS)
        + "; verification "
        + ", ".join(f"{value}={verification.get(value, 0)}" for value in fixstate.VERIFICATIONS)
        + "; scope "
        + ", ".join(f"{value}={scope.get(value, 0)}" for value in fixstate.SCOPES)
        + "; freshness "
        + ", ".join(f"{value}={freshness.get(value, 0)}" for value in fixstate.FRESHNESS)
    )
    return PASS, _append_target(target_line, f"registry/fixes.json object store, generated views, and transitions pass ({detail})")


def limb_honest_ratchet():
    paths = ["docs/index.html", "docs/ratchet_acknowledgements.json", *_target_review_pages()]
    target_line, err = _target("verify_all.limb_honest_ratchet", paths)
    if err:
        return NOEXEC, target_line
    from harness import honest_ratchet
    ratchet_target = honest_ratchet.describe_check_target(ROOT)
    if ratchet_target.startswith("TARGET honest_ratchet: COULD-NOT-EXECUTE"):
        return NOEXEC, _append_target(target_line, ratchet_target)
    ok, reasons = honest_ratchet.check(ROOT)
    if ok:
        return PASS, _append_target(target_line, ratchet_target + "\nrendered honest-state marker counts did not decrease")
    detail = "\n".join(reasons)
    verdict = NOEXEC if any(str(r).startswith(NOEXEC) for r in reasons) else REFUSED
    return verdict, _append_target(target_line, ratchet_target + "\n" + detail)


def limb_gate_scorecard():
    paths = ["registry/gate_scorecard.json", "docs/gate_scorecard.json", "harness/gate_scorecard.py"]
    target_line, err = _target("verify_all.limb_gate_scorecard", paths)
    if err:
        return NOEXEC, target_line
    from harness import gate_scorecard
    scorecard_target = gate_scorecard.describe_check_target(ROOT)
    if scorecard_target.startswith("TARGET gate_scorecard: COULD-NOT-EXECUTE"):
        return NOEXEC, _append_target(target_line, scorecard_target)
    ok, reasons = gate_scorecard.check(ROOT)
    if ok:
        s = gate_scorecard.summary(ROOT)
        detail = (f"{scorecard_target}\n"
                  f"{s['gate_count']} gates accounted for; "
                  f"{s['event_count']} events; "
                  f"{s['unresolved_event_count']} UNRESOLVED; "
                  f"{s['plant_validation_count']} adjudicated plant validations; "
                  f"{s['production_true_refusal_gate_count']} with adjudicated production true refusals")
        return PASS, _append_target(target_line, detail)
    return REFUSED, _append_target(target_line, scorecard_target + "\n" + "\n".join(reasons))


def limb_gate_gaps():
    rc, out = _run([sys.executable, os.path.join("scripts", "render_gate_gaps.py"), "--check"])
    tail = "\n".join(out.strip().splitlines()[-10:])
    return (PASS if rc == 0 else REFUSED), tail


LIMBS = [
    ("unit tests (pytest tests/)", limb_unit_tests),
    ("offline reproduction (every live page replays from committed cache)", limb_reproduction),
    ("publication gate on every live review page", limb_gate_every_page),
    ("index currency (generated == committed docs/index.html)", limb_index_currency),
    ("served-artefact leak scan (docs/*.json)", limb_leak_scan),
    ("held-out leak detector (registry/heldout_sealed.json)", limb_heldout),
    ("search completeness (search_v2 measurement current; every state explicit; no zero from an exit code)", limb_search_completeness),
    ("fix-state discipline (registry/fixes.json)", limb_fixstate),
    ("honest-state ratchet (no page may get quieter)", limb_honest_ratchet),
    ("gate scorecard (every gate accounted for)", limb_gate_scorecard),
    ("gate gaps table (sealed what-it-would-not-stop rows)", limb_gate_gaps),
]


def main():
    top_target, top_err = _target("verify_all", [os.path.join("scripts", "verify_all.py")])
    print(top_target)
    if top_err:
        print("VERIFY-ALL: COULD-NOT-EXECUTE -- target cannot be named.")
        return 1
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
        target_lines = [line for line in str(detail).splitlines() if line.startswith("TARGET ")]
        for line in target_lines:
            print(f"        {line}")
        if verdict != PASS:
            for line in str(detail).splitlines():
                if line.startswith("TARGET "):
                    continue
                print(f"        {line}")
    n_bad = sum(1 for _, v, _ in results if v != PASS)
    if n_bad:
        print(f"VERIFY-ALL: REFUSED -- {n_bad} of {len(LIMBS)} limbs not PASS. Fix the harness, never the gate.")
        return 1
    print(f"VERIFY-ALL: all {len(LIMBS)} limbs PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
