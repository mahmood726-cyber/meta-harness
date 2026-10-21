"""A function whose ROLE is a gate must be able to refuse. The name is a promise.

  python scripts/gate_can_fail.py                         # lint harness/ and scripts/ under the repo root
  python scripts/gate_can_fail.py --baseline registry/gate_can_fail_baseline.json   # the ratchet: only NEW findings count
  python scripts/gate_can_fail.py --json                  # machine-readable, carries the denominator
  python scripts/gate_can_fail.py --selftest              # prove every rule fires on a plant and stays silent on a good one
  python scripts/gate_can_fail.py --write-baseline registry/gate_can_fail_baseline.json   # re-record current findings

Ported from e156-ecosystem-starter scripts/gate-can-fail.py (2026-10-21, lane M-B). The source lints FILES named
`*_gate.py` for a reachable non-zero exit, and its own docstring names its largest limitation: a rule scoped to a
filename convention retires itself as the names drift (43 `*_gate.py` files, 0 defects; 230 verdict-returning files
under other names, 42 defects). meta-harness's gates are FUNCTIONS, not files -- `limb_*` in scripts/verify_all.py,
`check_*`/`verify_*`/`gate_*`/`assess_*`/`compare_*` across harness/ and scripts/ -- so this port is scoped by ROLE:

  IN SCOPE   a function (module-level, method or nested) whose name, leading underscores stripped, starts with one of
             PREFIXES, in a .py file under harness/ or scripts/, that RETURNS A VALUE somewhere (a verdict, a bool, an
             exit code, a problem list). One that returns nothing is counted and named as `no_verdict`, not judged.
  DEFECT     no reachable refusing path. A refusing path is any of: `raise`, `assert`, sys.exit/exit/os._exit with a
             non-zero or unresolvable code, a call to a same-module function that itself has a refusing raise/exit
             path (resolved transitively), or a `return` whose value can refuse -- False, a non-zero int, a non-empty
             list/tuple/set literal of refusals, a string outside PASSING_WORDS, a dict whose verdict key can refuse,
             or anything this cannot evaluate (a call, a comparison, a comprehension). `return name` is resolved
             when the local is only ever bound to constants/empty literals and never mutated or passed anywhere.

  "Unproven is not proven-safe": a value the lint cannot evaluate counts as able to refuse. A lint must not
  manufacture a failure it cannot demonstrate, so every finding is a function whose EVERY return is provably passing.

VERDICTS (the source's three, the same exit codes)
  CLEAN          0   every in-scope function can refuse (with --baseline: no finding outside the baseline)
  DEFECTS-FOUND  1   at least one cannot (with --baseline: at least one NEW one)
  INCONCLUSIVE   2   a file in scope could not be parsed, or a scanned directory / the baseline is missing.
                     "I could not check this" never collapses into "this is fine".

NOT CHECKED, named rather than implied. Reachability is SYNTACTIC: `if False: return False` passes. An exception from
an imported callee is not seen (only same-module helpers are resolved), so a function that delegates its refusal to an
imported helper is flagged; that is what the baseline's `reason` field is for. Proving a gate fires on a real input is a
known-answer plant test, a different instrument (this repo's tests/ plants are exactly that).

OPT-IN. Nothing imports this; harness/ must never import it. Running the CLI is opt-in. The ratchet
(tests/test_gate_can_fail.py) runs in the unit-test limb and was recorded so that every function on main at port time
passes it unchanged: it fails only on a finding NOT in registry/gate_can_fail_baseline.json. Offline, stdlib only.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import sys
import tempfile
from pathlib import Path

__version__ = "1.0.0"

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "registry" / "gate_can_fail_baseline.json"
SCAN_DIRS = ("harness", "scripts")
PREFIXES = ("check_", "gate_", "verify_", "limb_", "assess_", "compare_")
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".tox", ".mypy_cache", ".pytest_cache"}
# A returned string that means "let it through". Anything else returned as a constant string is read as a refusal
# reason (the `Optional[str]` error-message idiom) -- the conservative direction.
PASSING_WORDS = {"", "pass", "passed", "ok", "okay", "clean", "accept", "accepted", "allow", "allowed", "match",
                 "matched", "matches", "valid", "green", "yes", "true", "success", "succeeded", "verified", "fine"}
VERDICT_KEYS = ("verdict", "status", "ok", "pass", "passed", "result", "valid", "accepted")

CLEAN, DEFECTS_FOUND, INCONCLUSIVE = 0, 1, 2
VERDICT_CODE = {"CLEAN": CLEAN, "DEFECTS-FOUND": DEFECTS_FOUND, "INCONCLUSIVE": INCONCLUSIVE}

PASS, REFUSE, UNKNOWN = "pass", "refuse", "unknown"
_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)


def _in_scope(name: str) -> bool:
    return name.lstrip("_").startswith(PREFIXES)


def _own_nodes(fn):
    """Every node in fn's body, NOT descending into nested defs/lambdas/classes (their returns are theirs)."""
    stack = [n for n in fn.body if not isinstance(n, _SCOPES)]
    while stack:
        node = stack.pop()
        yield node
        for child in ast.iter_child_nodes(node):
            if not isinstance(child, _SCOPES):
                stack.append(child)


def _join(kinds) -> str:
    kinds = set(kinds)
    return REFUSE if REFUSE in kinds else UNKNOWN if UNKNOWN in kinds else PASS


def _classify(expr, bindings=None) -> str:
    """Can this returned value be a refusal? PASS (provably not), REFUSE (yes), UNKNOWN (cannot tell: treated as yes)."""
    if expr is None:
        return PASS
    if isinstance(expr, ast.Constant):
        v = expr.value
        if v is None or v is True:
            return PASS
        if v is False:
            return REFUSE
        if isinstance(v, (int, float)):
            return PASS if v == 0 else REFUSE
        if isinstance(v, str):
            return PASS if v.strip().lower().replace("-", "_") in PASSING_WORDS else REFUSE
        return UNKNOWN
    if isinstance(expr, (ast.List, ast.Tuple, ast.Set)):
        if not expr.elts:
            return PASS
        if isinstance(expr, ast.Tuple):   # (verdict, detail) pairs, verdict first: the verdict decides
            return _classify(expr.elts[0], bindings)
        kinds = [_classify(e, bindings) for e in expr.elts]
        return REFUSE if all(k != UNKNOWN for k in kinds) else UNKNOWN   # a non-empty problem list is a refusal
    if isinstance(expr, ast.Dict):
        if not expr.keys:
            return PASS
        for k, v in zip(expr.keys, expr.values):
            if isinstance(k, ast.Constant) and k.value in VERDICT_KEYS:
                return _classify(v, bindings)
        return UNKNOWN
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id in ("list", "tuple", "set",
                                                                                            "dict") and not expr.args \
            and not expr.keywords:
        return PASS
    if isinstance(expr, ast.IfExp):
        return _join([_classify(expr.body, bindings), _classify(expr.orelse, bindings)])
    if isinstance(expr, ast.Name) and bindings is not None and expr.id in bindings:
        return _join(_classify(v, bindings=None) for v in bindings[expr.id])
    if isinstance(expr, ast.Name) and expr.id in _MODULE_CONSTANTS:
        return _classify(_MODULE_CONSTANTS[expr.id])
    return UNKNOWN


_MODULE_CONSTANTS: dict = {}   # set per module by scan(): the verdict vocabulary a gate returns by name (PASS = "PASS")


def module_constants(tree) -> dict:
    """Module-level names bound EXACTLY ONCE, to a literal (`PASS = "PASS"`, `CLEAN, FAIL = 0, 1`) -> that literal.

    A name bound twice, or rebound anywhere through `global`, is not a constant and stays unresolved.
    """
    seen, out = {}, {}
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            value = node.value
            for t in targets:
                if isinstance(t, ast.Name):
                    seen[t.id] = seen.get(t.id, 0) + 1
                    if value is not None and _literal(value):
                        out[t.id] = value
                elif isinstance(t, ast.Tuple) and isinstance(value, ast.Tuple) and len(t.elts) == len(value.elts):
                    for tn, tv in zip(t.elts, value.elts):
                        if isinstance(tn, ast.Name):
                            seen[tn.id] = seen.get(tn.id, 0) + 1
                            if _literal(tv):
                                out[tn.id] = tv
                else:
                    for n in ast.walk(t):
                        if isinstance(n, ast.Name):
                            seen[n.id] = seen.get(n.id, 0) + 2
    for node in ast.walk(tree):
        if isinstance(node, ast.Global):
            for n in node.names:
                seen[n] = 2
    return {k: v for k, v in out.items() if seen.get(k) == 1}


def _constant_bindings(fn) -> dict:
    """Locals only ever bound to literal values and never mutated, passed, or otherwise touched -> their values.

    `ok = True ... return ok` with nothing setting it False is the variable-shaped version of the source's motivating
    case (`sys.exit(main())` whose main can only return 0). Any other use of the name (an attribute call such as
    `.append`, an augmented assignment, a subscript store, being passed to a call, a for/with/walrus target, a
    `global`/`nonlocal`) disqualifies it: unresolved, so UNKNOWN.
    """
    values, tainted = {}, set()
    args = fn.args
    for a in args.posonlyargs + args.args + args.kwonlyargs + [args.vararg, args.kwarg]:
        if a is not None:
            tainted.add(a.arg)
    returned_names = {id(n.value) for n in _own_nodes(fn) if isinstance(n, ast.Return) and isinstance(n.value, ast.Name)}
    for node in _own_nodes(fn):
        if isinstance(node, ast.Assign):
            simple = len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
            if simple and _literal(node.value):
                values.setdefault(node.targets[0].id, []).append(node.value)
            else:
                for t in node.targets:
                    for n in ast.walk(t):
                        if isinstance(n, ast.Name):
                            tainted.add(n.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.value is not None and _literal(node.value):
                values.setdefault(node.target.id, []).append(node.value)
            elif node.value is not None:
                tainted.add(node.target.id)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            tainted.update(node.names)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and id(node) not in returned_names:
            tainted.add(node.id)          # read anywhere but a bare `return name`: could be mutated through
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            pass                          # Assign targets handled above; other stores (for/with/walrus/aug) below
        if isinstance(node, (ast.AugAssign, ast.For, ast.AsyncFor, ast.NamedExpr, ast.withitem, ast.comprehension)):
            target = getattr(node, "target", None) or getattr(node, "optional_vars", None)
            for n in ast.walk(target) if target is not None else ():
                if isinstance(n, ast.Name):
                    tainted.add(n.id)
        if isinstance(node, ast.ExceptHandler) and node.name:
            tainted.add(node.name)
    # nested scopes may close over a local and rebind it via nonlocal: taint every name they mention
    for node in _own_nodes(fn):
        if isinstance(node, _SCOPES):
            for n in ast.walk(node):
                if isinstance(n, ast.Name):
                    tainted.add(n.id)
    return {k: v for k, v in values.items() if k not in tainted}


def _literal(expr) -> bool:
    if isinstance(expr, ast.Constant):
        return True
    if isinstance(expr, (ast.List, ast.Tuple, ast.Set)):
        return all(_literal(e) for e in expr.elts)
    if isinstance(expr, ast.Dict):
        return all(k is not None and _literal(k) for k in expr.keys) and all(_literal(v) for v in expr.values)
    return False


def _exit_refuses(call) -> bool:
    fn = call.func
    name = getattr(fn, "attr", None) or getattr(fn, "id", None)
    if name not in ("exit", "_exit"):
        return False
    if not call.args:
        return False                      # exit() == exit(0)
    a = call.args[0]
    if isinstance(a, ast.Constant):
        return a.value not in (0, None)   # exit(None) == 0; exit("msg") prints and exits 1
    return True                           # exit(<expr>): cannot resolve, not convicted


def _direct_refusal(fn) -> str | None:
    """A raise / assert / non-zero exit / SystemExit in fn's own body -> a short description, else None."""
    for node in _own_nodes(fn):
        if isinstance(node, ast.Raise):
            return "raise"
        if isinstance(node, ast.Assert):
            return "assert"
        if isinstance(node, ast.Call) and _exit_refuses(node):
            return "exit"
    return None


def _module_functions(tree) -> dict:
    """name -> def for module-level functions and methods (methods keyed by bare name, for self.x() calls)."""
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.setdefault(node.name, node)
        elif isinstance(node, ast.ClassDef):
            for m in node.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out.setdefault(m.name, m)
    return out


def _helper_refuses(fn, funcs, seen) -> str | None:
    """Does fn call a same-module function (by name, or self./cls.) that has a refusing raise/exit path?"""
    for node in _own_nodes(fn):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        callee = f.id if isinstance(f, ast.Name) else (
            f.attr if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in ("self", "cls")
            else None)
        target = funcs.get(callee)
        if target is None or id(target) in seen:
            continue
        seen.add(id(target))
        if _direct_refusal(target) or _helper_refuses(target, funcs, seen):
            return "via %s()" % callee
    return None


def judge(fn, funcs) -> dict:
    """{'in_scope': bool, 'refusal': str|None, 'returns': [...]} for one function."""
    returns = [n for n in _own_nodes(fn) if isinstance(n, ast.Return)]
    if any(isinstance(n, (ast.Yield, ast.YieldFrom)) for n in _own_nodes(fn)):
        return {"verdict_returning": True, "refusal": "generator (yields are not judged)"}
    valued = [r for r in returns if r.value is not None and not (isinstance(r.value, ast.Constant)
                                                                 and r.value.value is None)]
    if not valued:
        direct = _direct_refusal(fn)
        return {"verdict_returning": False, "refusal": direct}
    direct = _direct_refusal(fn)
    if direct:
        return {"verdict_returning": True, "refusal": direct}
    bindings = _constant_bindings(fn)
    for r in valued:
        k = _classify(r.value, bindings)
        if k != PASS:
            return {"verdict_returning": True, "refusal": "return (%s, line %d)" % (k, r.lineno)}
    via = _helper_refuses(fn, funcs, {id(fn)})
    if via:
        return {"verdict_returning": True, "refusal": via}
    shown = sorted({ast.unparse(r.value)[:40] for r in valued})
    return {"verdict_returning": True, "refusal": None,
            "reason": "every return is provably passing (%s); no raise, assert, non-zero exit, or refusing same-module "
                      "helper" % ", ".join(shown)}


def _qualnames(tree):
    """(qualname, def) for every function in the module, methods and nested defs included."""
    def walk(body, prefix):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = prefix + node.name
                yield q, node
                yield from walk(node.body, q + ".")
            elif isinstance(node, ast.ClassDef):
                yield from walk(node.body, prefix + node.name + ".")
            else:
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        yield from walk([child], prefix)
    yield from walk(tree.body, "")


def scan(root, dirs=SCAN_DIRS) -> dict:
    """Lint every in-scope function under root/<dir> for each dir. Carries the denominator, not only the hits."""
    root = Path(root)
    findings, unparsable, no_verdict, missing_dirs, refuse_only = [], [], [], [], []
    checked = files = 0
    for d in dirs:
        base = root / d
        if not base.is_dir():
            missing_dirs.append(d)
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(x for x in dirnames if x not in SKIP_DIRS and not x.startswith("."))
            for name in sorted(filenames):
                if not name.endswith(".py"):
                    continue
                path = Path(dirpath) / name
                rel = path.relative_to(root).as_posix()
                try:
                    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
                except (SyntaxError, ValueError, OSError) as exc:   # reported, never silently skipped
                    unparsable.append({"file": rel, "error": str(exc)[:160]})
                    continue
                files += 1
                funcs = _module_functions(tree)
                _MODULE_CONSTANTS.clear()
                _MODULE_CONSTANTS.update(module_constants(tree))
                for qual, fn in _qualnames(tree):
                    if not _in_scope(fn.name):
                        continue
                    j = judge(fn, funcs)
                    if not j["verdict_returning"]:
                        (no_verdict if j["refusal"] is None else refuse_only).append("%s::%s" % (rel, qual))
                        continue
                    checked += 1
                    if j["refusal"] is None:
                        findings.append({"file": rel, "function": qual, "line": fn.lineno, "reason": j["reason"]})
    if findings:
        verdict = "DEFECTS-FOUND"
    elif unparsable or missing_dirs:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "CLEAN"
    return {"verdict": verdict, "lint_version": __version__, "root": str(root.resolve()), "dirs": list(dirs),
            "prefixes": list(PREFIXES), "files_parsed": files, "functions_checked": checked,
            "cannot_refuse": findings, "unparsable": unparsable, "missing_dirs": missing_dirs,
            "no_verdict_not_judged": no_verdict, "no_verdict_but_refuses": refuse_only,
            "not_checked": "Reachability is syntactic (`if False: return False` passes); exceptions from imported "
                           "callees are not seen. Proving a gate fires on a real input is a known-answer plant test."}


def _key(f) -> tuple:
    return (f["file"], f["function"])


def load_baseline(path) -> list:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = doc["entries"]
    for e in entries:
        if not (e.get("file") and e.get("function") and e.get("reason")):
            raise ValueError("baseline entry lacks file/function/reason: %r" % (e,))
    return entries


def apply_baseline(result: dict, entries: list) -> dict:
    """The ratchet: only findings NOT in the baseline count. Stale entries are reported, never counted as passes."""
    known = {_key(e) for e in entries}
    found = {_key(f) for f in result["cannot_refuse"]}
    new = [f for f in result["cannot_refuse"] if _key(f) not in known]
    out = dict(result)
    out["new_findings"] = new
    out["baselined"] = len(found & known)
    out["stale_baseline_entries"] = sorted("%s::%s" % k for k in known - found)
    out["verdict"] = "DEFECTS-FOUND" if new else ("INCONCLUSIVE" if result["unparsable"] or result["missing_dirs"]
                                                  else "CLEAN")
    return out


def write_baseline(result: dict, path) -> None:
    doc = {"lint": "scripts/gate_can_fail.py", "lint_version": __version__,
           "note": "Ratchet baseline: in-scope functions (role-named check_/gate_/verify_/limb_/assess_/compare_ under "
                   "harness/ and scripts/) whose every return is provably passing, recorded at port time so main does "
                   "not break. tests/test_gate_can_fail.py fails only on a finding NOT listed here. Shrink this list; "
                   "never grow it to admit a new gate -- give the gate a refusing path, or rename it if it is "
                   "advisory by design.",
           "entries": [{"file": f["file"], "function": f["function"], "reason": f["reason"]}
                       for f in sorted(result["cannot_refuse"], key=_key)]}
    Path(path).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")


def report(result: dict) -> int:
    shown = result.get("new_findings", result["cannot_refuse"])
    for f in shown:
        print("%s:%d  %s" % (f["file"], f["line"], f["function"]))
        print("      named a gate but cannot refuse: %s" % f["reason"])
    for row in result["unparsable"]:
        print("%s  UNPARSABLE (%s) -- reported, not skipped" % (row["file"], row["error"]))
    for d in result["missing_dirs"]:
        print("%s/  MISSING -- not scanned" % d)
    print()
    print("gate_can_fail %s   %d file(s) parsed, %d verdict-returning gate function(s) checked, %d unparsable"
          % (result["lint_version"], result["files_parsed"], result["functions_checked"], len(result["unparsable"])))
    print("named a gate, return no verdict: %d refuse by raise/exit, %d cannot refuse (counted, not judged)"
          % (len(result["no_verdict_but_refuses"]), len(result["no_verdict_not_judged"])))
    print("cannot refuse: %d" % len(result["cannot_refuse"]))
    if "new_findings" in result:
        print("  of which baselined: %d   NEW: %d   stale baseline entries (fixed or gone; remove them): %d"
              % (result["baselined"], len(result["new_findings"]), len(result["stale_baseline_entries"])))
        for s in result["stale_baseline_entries"]:
            print("   stale: %s" % s)
    print("NOT CHECKED: %s" % result["not_checked"])
    print()
    v = result["verdict"]
    if v == "DEFECTS-FOUND":
        print("DEFECTS-FOUND: %d gate function(s) cannot refuse%s." % (len(shown), " (new)" if "new_findings" in result
                                                                       else ""))
        print("FIX: give it a reachable refusing path, or RENAME it if it is advisory by design. Do not add it to the")
        print("     baseline to make this pass -- the baseline only records what was on main when the lint landed.")
    elif v == "INCONCLUSIVE":
        print("INCONCLUSIVE: something in scope could not be checked. A check that could not run is not a pass.")
    elif result["functions_checked"] == 0:
        print("CLEAN over an EMPTY SET -- no verdict-returning gate function was found, so nothing was checked.")
    else:
        print("CLEAN")
    return VERDICT_CODE[v]


# ---------------------------------------------------------------------------------------------- selftest
# BOTH DIRECTIONS for every rule: a detector with only a positive test passes while matching everything; with only a
# negative test, while matching nothing.
KNOWN_BAD = {   # function name -> source; each must be flagged
    "check_always_true": "def check_always_true(x):\n    print(x)\n    return True\n",
    "verify_exit_zero": "def verify_exit_zero():\n    print('fine')\n    return 0\n",
    "limb_pass_string": "def limb_pass_string():\n    return 'PASS'\n",
    "gate_empty_problems": "def gate_empty_problems(rows):\n    for r in rows:\n        print(r)\n    return []\n",
    "assess_ok_var": "def assess_ok_var(x):\n    ok = True\n    return ok\n",
    "compare_dict_pass": "def compare_dict_pass(a, b):\n    return {'verdict': 'PASS', 'n': 2}\n",
    "_check_private_pair": "def _check_private_pair(x):\n    return True, []\n",
    "check_ifexp_both_pass": "def check_ifexp_both_pass(x):\n    return 'ok' if x else 'PASS'\n",
    "verify_swallows": "def verify_swallows(x):\n    try:\n        int(x)\n    except ValueError:\n        return True\n"
                       "    return True\n",
    "limb_named_pass_pair": "PASS, REFUSED = 'PASS', 'REFUSED'\ndef limb_named_pass_pair():\n    return PASS, "
                            "'all 3 pages reproduce'\n",
    "check_nested_raise_is_not_mine": "def check_nested_raise_is_not_mine():\n    def inner():\n        raise "
                                      "ValueError\n    return True\n",
}
KNOWN_GOOD = {  # must NOT be flagged
    "check_returns_false": "def check_returns_false(x):\n    if x:\n        return False\n    return True\n",
    "verify_raises": "def verify_raises(x):\n    if not x:\n        raise ValueError('refused')\n    return True\n",
    "limb_exit_code": "def limb_exit_code(rc):\n    if rc:\n        return 1\n    return 0\n",
    "gate_problem_list": "def gate_problem_list(rows):\n    problems = []\n    for r in rows:\n        if not r:\n"
                         "            problems.append(r)\n    return problems\n",
    "assess_asserts": "def assess_asserts(x):\n    assert x, 'refused'\n    return True\n",
    "compare_computed": "def compare_computed(a, b):\n    return a == b\n",
    "check_error_message": "def check_error_message(x):\n    if not x:\n        return 'missing x'\n    return None\n",
    "verify_sys_exit": "import sys\ndef verify_sys_exit(x):\n    if not x:\n        sys.exit(2)\n    return True\n",
    "check_via_helper": "def _require(x):\n    if not x:\n        raise SystemExit(1)\ndef check_via_helper(x):\n"
                        "    _require(x)\n    return True\n",
    "gate_ok_reassigned": "def gate_ok_reassigned(xs):\n    ok = True\n    for x in xs:\n        if not x:\n"
                          "            ok = False\n    return ok\n",
    "limb_named_verdict_pair": "PASS, REFUSED = 'PASS', 'REFUSED'\ndef limb_named_verdict_pair(rc):\n    return "
                               "(PASS if rc == 0 else REFUSED), 'tail'\n",
    "compare_dict_fail": "def compare_dict_fail(a, b):\n    return {'verdict': 'PASS' if a == b else 'FAIL'}\n",
    # not in scope: wrong name, or returns no verdict -- must not be judged at all
    "summarise": "def summarise(x):\n    return True\n",
    "check_prints_only": "def check_prints_only(x):\n    print(x)\n",
}
UNPARSABLE = "def check_broken(:\n"


def _plant(tmp: Path, sources: dict) -> None:
    for i, (name, src) in enumerate(sorted(sources.items())):
        (tmp / "scripts" / ("plant_%02d.py" % i)).write_text(src, encoding="utf-8")


def selftest() -> int:
    failures = []
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        (tmp / "harness").mkdir()
        (tmp / "scripts").mkdir()

        _plant(tmp, KNOWN_BAD)
        bad = scan(tmp)
        fired = {f["function"] for f in bad["cannot_refuse"]}
        for name in KNOWN_BAD:
            if name not in fired:
                failures.append("MISSED a planted defect: %s was not flagged" % name)
        if bad["verdict"] != "DEFECTS-FOUND":
            failures.append("verdict on the planted-bad set was %s, not DEFECTS-FOUND" % bad["verdict"])
        if fired - set(KNOWN_BAD):
            failures.append("flagged something not planted: %s" % sorted(fired - set(KNOWN_BAD)))

        for p in (tmp / "scripts").iterdir():
            p.unlink()
        _plant(tmp, KNOWN_GOOD)
        good = scan(tmp)
        for f in good["cannot_refuse"]:
            failures.append("FALSE POSITIVE: %s was flagged" % f["function"])
        if good["verdict"] != "CLEAN":
            failures.append("verdict on the known-good set was %s, not CLEAN" % good["verdict"])
        if any(n.endswith("::summarise") for n in good["no_verdict_not_judged"]):
            failures.append("judged a function not named a gate: summarise")
        if not any(n.endswith("::check_prints_only") for n in good["no_verdict_not_judged"]):
            failures.append("a gate-named function returning no verdict was not counted as no_verdict")
        if good["functions_checked"] != len(KNOWN_GOOD) - 2:
            failures.append("denominator wrong: functions_checked=%d" % good["functions_checked"])

        # the ratchet: a baselined finding is not counted, a new one is
        _plant(tmp, KNOWN_BAD)
        both = scan(tmp)
        base = [{"file": f["file"], "function": f["function"], "reason": f["reason"]} for f in both["cannot_refuse"]]
        if apply_baseline(both, base)["verdict"] != "CLEAN":
            failures.append("a fully baselined tree did not read CLEAN under --baseline")
        if apply_baseline(both, base[1:])["verdict"] != "DEFECTS-FOUND":
            failures.append("a finding missing from the baseline did not read DEFECTS-FOUND")

        # "I could not check this" is INCONCLUSIVE, never CLEAN
        for p in (tmp / "scripts").iterdir():
            p.unlink()
        _plant(tmp, KNOWN_GOOD)
        (tmp / "scripts" / "zz_broken.py").write_text(UNPARSABLE, encoding="utf-8")
        if scan(tmp)["verdict"] != "INCONCLUSIVE":
            failures.append("an unparsable file did not produce INCONCLUSIVE")
        (tmp / "scripts" / "zz_broken.py").unlink()
        (tmp / "harness").rmdir()
        if scan(tmp)["verdict"] != "INCONCLUSIVE":
            failures.append("a missing scan directory did not produce INCONCLUSIVE")

    if failures:
        for f in failures:
            print("SELFTEST FAIL: %s" % f)
        print("DEFECTS-FOUND")
        return DEFECTS_FOUND
    print("selftest OK -- %d planted defects fired (DEFECTS-FOUND), %d known-good stayed silent (CLEAN), the ratchet"
          % (len(KNOWN_BAD), len(KNOWN_GOOD)))
    print("counted only an unbaselined finding, and an unparsable file / missing dir read INCONCLUSIVE.")
    return CLEAN


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="A function whose role is a gate must be able to refuse.",
                                 epilog="Verdicts: CLEAN=0, DEFECTS-FOUND=1, INCONCLUSIVE=2.")
    ap.add_argument("root", nargs="?", default=str(ROOT), help="repo root (default: this repo)")
    ap.add_argument("--dirs", nargs="+", default=list(SCAN_DIRS), help="directories under root to scan")
    ap.add_argument("--baseline", help="ratchet: count only findings not in this baseline JSON")
    ap.add_argument("--write-baseline", metavar="PATH", help="record the current findings as the baseline")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--selftest", action="store_true", help="prove each rule fires on a plant and stays silent")
    ap.add_argument("--version", action="version", version="gate_can_fail " + __version__)
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not Path(args.root).is_dir():
        print("INCONCLUSIVE: not a directory: %s" % args.root)
        return INCONCLUSIVE
    result = scan(args.root, args.dirs)
    if args.write_baseline:
        write_baseline(result, args.write_baseline)
        print("wrote %d baseline entr%s to %s" % (len(result["cannot_refuse"]),
                                                 "y" if len(result["cannot_refuse"]) == 1 else "ies",
                                                 args.write_baseline))
        return VERDICT_CODE["INCONCLUSIVE"] if result["unparsable"] or result["missing_dirs"] else CLEAN
    if args.baseline:
        try:
            result = apply_baseline(result, load_baseline(args.baseline))
        except (OSError, ValueError, KeyError) as exc:
            print("INCONCLUSIVE: baseline unreadable: %s" % exc)
            return INCONCLUSIVE
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return VERDICT_CODE[result["verdict"]]
    return report(result)


if __name__ == "__main__":
    sys.exit(main())
