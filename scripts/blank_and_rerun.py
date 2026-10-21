"""Blank a function, re-run the pytest selection that claims to cover it: if it stays green, the tests are HOLLOW for it.

The bluntest mutation test -- one mutant per function, the whole body gone. A passing suite plus "matches metafor" is
two true statements that prove nothing when the test compares a stored number to itself, is skipped, reads a cached
file, or takes its expected value from the function under test. Blanking the function and watching the selection is
the cheapest way to tell those apart from a test that calls the code. Ported (2026-10-21, brief M-C) from
e156-ecosystem-starter scripts/blank-and-rerun.py; adapted to pytest and to editing the file IN PLACE.

    python scripts/blank_and_rerun.py --file harness/secondary_meta.py --function reml_tau2 --function pool \
        --tests tests/test_secondary_meta.py
    python scripts/blank_and_rerun.py --targets my_targets.json [--json]
        # [{"file": "harness/synth.py", "functions": ["pool", "_wmean"], "tests": ["tests/test_synth.py", "-k", "pool"]}]

Per function:
    BITES    the selection FAILS with the body blanked: it depends on the function
    HOLLOW   the selection still PASSES with the body blanked: whatever it checks, it is not this function
    ERROR    could not tell -- the selection is red BEFORE blanking, collects no tests, timed out, the function is not
             in the file, or the blanked file does not compile. "Could not check" is never a pass.
Exit: 0 every function BITES; 1 at least one HOLLOW; 2 an ERROR and no HOLLOW; 3 refused to start, or the file could not
be restored byte-for-byte (the message says which; `git checkout -- <file>` recovers, since a dirty file is refused).

Safety, because the edit is in place: the file must be tracked by git and unmodified (`git status --porcelain` empty for
it) or the tool refuses to start; the original bytes and mtime are restored in a `finally` after every mutant, and the
file's sha256 is checked against the original after each restore and again at the end. Bytecode is not written
(PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider) so no blanked .pyc can outlive the run.

What it does NOT check: BITES means the selection notices the function is gone, not that its numbers are right (a test
asserting "returns a float" bites). Pair it with a known-answer test against R. Python functions only.

Opt-in and standalone: nothing in verify_all, CI or harness/ runs or imports it. Standard library + pytest; no model call.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
import subprocess
import sys

__version__ = "1.0.0"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BITES, HOLLOW, ERROR = "BITES", "HOLLOW", "ERROR"
EXIT_OK, EXIT_HOLLOW, EXIT_ERROR, EXIT_REFUSED = 0, 1, 2, 3
MARK = "blanked by blank_and_rerun"
STUBS = {"raise": 'raise NotImplementedError("%s")' % MARK, "return-none": "return None  # %s" % MARK}
# pytest exit codes: 0 all passed, 1 some failed, 2 interrupted / collection error, 5 no tests collected
PYTEST_FAILED = (1, 2)


class Refused(Exception):
    """The tool will not touch the file (dirty, untracked, missing) or could not put it back."""


def sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def find_function(tree: ast.AST, dotted: str):
    """The FunctionDef for `name` or `Class.method` at module level, or None. The LAST definition wins, as at import."""
    nodes = tree.body
    parts = dotted.split(".")
    for i, part in enumerate(parts):
        found = None
        for n in nodes:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == part:
                found = n
        if found is None:
            return None
        if i < len(parts) - 1:
            if not isinstance(found, ast.ClassDef):
                return None
            nodes = found.body
        elif isinstance(found, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return found
    return None


def blank_function(src: str, dotted: str, mode: str = "raise") -> str:
    """`src` with the body of `dotted` replaced by one stub line. Signature, decorators, the rest of the file and its line
    endings are left as they were. KeyError if the function is absent; SyntaxError if the result does not compile."""
    tree = ast.parse(src)
    node = find_function(tree, dotted)
    if node is None:
        raise KeyError(dotted)
    lines = io.StringIO(src, newline="").readlines()  # ast's line breaks (splitlines also splits on )
    first = node.body[0]
    start = min([first.lineno] + [d.lineno for d in getattr(first, "decorator_list", [])]) - 1
    end = node.end_lineno - 1
    if start + 1 == node.lineno:            # one-liner `def f(x): return x`: keep everything up to the body
        prefix = lines[start].encode("utf-8")[:first.col_offset].decode("utf-8")
    else:
        prefix = lines[start][: len(lines[start]) - len(lines[start].lstrip())]
    last = lines[end]
    newline = last[len(last.rstrip("\r\n")):] or ("\n" if end + 1 < len(lines) else "")
    out = "".join(lines[:start]) + prefix + STUBS[mode] + newline + "".join(lines[end + 1:])
    ast.parse(out)
    return out


def _git(root: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


def preflight(root: str, rel_file: str) -> None:
    """Refuse unless the file exists, is tracked, and is byte-identical to HEAD/index in the working tree."""
    if not os.path.isfile(os.path.join(root, rel_file)):
        raise Refused("file not found: %s" % rel_file)
    if _git(root, "ls-files", "--error-unmatch", "--", rel_file).returncode != 0:
        raise Refused("%s is not tracked by git: an in-place edit could not be recovered with git checkout" % rel_file)
    st = _git(root, "status", "--porcelain", "--", rel_file)
    if st.returncode != 0:
        raise Refused("git status failed for %s: %s" % (rel_file, st.stderr.strip()))
    if st.stdout.strip():
        raise Refused("%s is already modified in the working tree (%s): commit or discard first; the tool only edits a "
                      "clean file so `git checkout -- %s` is always a recovery" % (rel_file, st.stdout.strip(), rel_file))


def run_selection(root: str, tests: list, timeout: int):
    """(pytest exit code or None on timeout, last lines of output, whether the blank's marker reached the output)."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", *tests],
                           cwd=root, capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return None, "timed out after %ds" % timeout, False
    out = r.stdout + r.stderr
    return r.returncode, " | ".join(out.strip().splitlines()[-3:]), MARK in out


def _restore(path: str, original: bytes, stat: os.stat_result, digest: str) -> None:
    with open(path, "wb") as fh:
        fh.write(original)
    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    if sha256(path) != digest:
        raise Refused("RESTORE FAILED: %s sha256 differs from the original; run `git checkout -- %s`" % (path, path))


def check(root: str, rel_file: str, functions: list, tests: list, timeout: int = 900, mode: str = "raise",
          runner=run_selection) -> dict:
    """Baseline the selection, then blank each function in place, run, and restore. Raises Refused (file untouched)."""
    root = os.path.abspath(root)
    path = os.path.join(root, rel_file)
    preflight(root, rel_file)
    with open(path, "rb") as fh:
        original = fh.read()
    stat, digest = os.stat(path), hashlib.sha256(original).hexdigest()
    src = original.decode("utf-8")
    res = dict(version=__version__, file=rel_file, tests=list(tests), mode=mode, sha256_before=digest,
               baseline=None, functions=[])
    code, tail, _ = runner(root, tests, timeout)
    res["baseline"] = dict(exit_code=code, tail=tail)
    baseline_green = code == 0
    for fn in functions:
        row = dict(function=fn, verdict=ERROR, exit_code=None, reason="", tail="")
        res["functions"].append(row)
        if not baseline_green:
            row["reason"] = ("the selection is not green BEFORE blanking (exit %s; 5 = no tests collected): blanking "
                             "cannot show anything" % code)
            continue
        try:
            blanked = blank_function(src, fn, mode)
        except KeyError:
            row["reason"] = "function not found in %s" % rel_file
            continue
        except SyntaxError as exc:
            row["reason"] = "blanked file does not compile: %s" % str(exc)[:160]
            continue
        try:
            with open(path, "wb") as fh:
                fh.write(blanked.encode("utf-8"))
            code, tail, marked = runner(root, tests, timeout)
        finally:
            _restore(path, original, stat, digest)
        row.update(exit_code=code, tail=tail, marker_seen=marked)
        if code is None:
            row["reason"] = "timed out"
        elif code == 0:
            row.update(verdict=HOLLOW, reason="the selection passed with the body blanked")
        elif code in PYTEST_FAILED:
            row.update(verdict=BITES, reason="the selection failed with the body blanked")
        else:
            row["reason"] = "pytest exit %s (not a test failure)" % code
    if sha256(path) != digest:
        raise Refused("RESTORE FAILED at end: %s sha256 differs; run `git checkout -- %s`" % (rel_file, rel_file))
    res["sha256_after"] = digest
    return res


def exit_code(results: list) -> int:
    verdicts = [r["verdict"] for res in results for r in res["functions"]]
    if HOLLOW in verdicts:
        return EXIT_HOLLOW
    if not verdicts or ERROR in verdicts:
        return EXIT_ERROR
    return EXIT_OK


def load_targets(path: str) -> list:
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    if not isinstance(doc, list) or not all(isinstance(t, dict) and {"file", "functions", "tests"} <= set(t) for t in doc):
        raise ValueError("targets file must be a JSON list of {file, functions, tests} objects")
    return doc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 epilog="Exit: 0 all BITES, 1 any HOLLOW, 2 ERROR, 3 refused / restore failed.")
    ap.add_argument("--root", default=ROOT, help="repository root; pytest runs here (default: this repo)")
    ap.add_argument("--file", help="Python file holding the functions, relative to --root")
    ap.add_argument("--function", action="append", default=[], help="name or Class.method; repeatable")
    ap.add_argument("--tests", nargs="+", default=[], help="pytest selection (paths, node ids, -k EXPR ...)")
    ap.add_argument("--targets", help="JSON list of {file, functions, tests}")
    ap.add_argument("--mode", choices=sorted(STUBS), default="raise", help="stub: raise NotImplementedError or return None")
    ap.add_argument("--timeout", type=int, default=900, help="seconds per pytest run")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--version", action="version", version=__version__)
    args = ap.parse_args(argv)
    if args.targets:
        targets = load_targets(args.targets)
    elif args.file and args.function and args.tests:
        targets = [dict(file=args.file, functions=args.function, tests=args.tests)]
    else:
        ap.error("give --targets, or --file with --function and --tests")
    results = []
    try:
        for t in targets:
            results.append(check(args.root, t["file"], t["functions"], t["tests"], args.timeout, args.mode))
    except Refused as exc:
        print("REFUSED: %s" % exc, file=sys.stderr)
        return EXIT_REFUSED
    if args.json:
        print(json.dumps(dict(version=__version__, results=results), indent=2, sort_keys=True))
    else:
        print("blank_and_rerun v%s (mode %s)" % (__version__, args.mode))
        for res in results:
            print("%s   pytest %s   baseline exit %s" % (res["file"], " ".join(res["tests"]), res["baseline"]["exit_code"]))
            for r in res["functions"]:
                print("  %-7s %-28s %s" % (r["verdict"], r["function"], r["reason"]))
            print("  restored: sha256 %s unchanged" % res["sha256_after"][:12])
    return exit_code(results)


if __name__ == "__main__":
    sys.exit(main())
