"""V1 regex freeze (Mahmood, 13 Oct, ruling 6): the definition-sentence parsers change only with a logged failure class
whose plant test exists, and the class records the file's new blob. Uncertain sentences abstain rather than parse harder."""
import ast
import json
import os
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE = os.path.join(ROOT, "registry", "regex_freeze.json")
# The baseline commit is pinned IN THE GATE, not only in the registry it checks: re-anchoring the freeze is then an edit
# to this file, visible in review (codex pr98-cap-r2 #1; known limit: any in-repo gate can itself be edited).
FROZEN_AT = "c715a5d59e5d2f246042776b1f16df0fcd34a3af"


def _blob(path, root=ROOT):
    return subprocess.run(["git", "hash-object", "--", path], cwd=root, capture_output=True, text=True,
                          check=True).stdout.strip()


def _test_functions(path):
    """Top-level function names DEFINED in a test file (parsed, so a name inside a string or comment is not one)."""
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except (OSError, SyntaxError):
        return set()
    # a COLLECTED test only: a helper (`_blob`) is never run, so it can never fail first (codex pr98-cap-r2 #2)
    return {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and n.name.startswith("test")}


def _baseline(doc, root):
    """{file: blob} as git stored it at `frozen_at` -- the registry's own `frozen` map is a claim checked against this."""
    out = {}
    for f in doc["frozen"]:
        r = subprocess.run(["git", "rev-parse", f"{doc.get('frozen_at')}:{f}"], cwd=root, capture_output=True, text=True)
        out[f] = r.stdout.strip() if r.returncode == 0 else None
    return out


def freeze_problems(doc, blob=_blob, root=ROOT, baseline=None):
    """[problem] -- empty when every frozen file's bytes are its last recorded blob, the recorded baseline is what git
    held at `frozen_at`, and every class names a plant that is a real test function."""
    expected = dict(doc["frozen"])
    out = []
    if root == ROOT and doc.get("frozen_at") != FROZEN_AT:
        out.append(f"frozen_at {doc.get('frozen_at')!r} != the gate's pinned {FROZEN_AT[:12]}: the baseline is never "
                   "re-anchored; a parser change is a logged failure class")
    if baseline is None and root == ROOT:
        baseline = _baseline(doc, root)
    for f, b in (baseline or {}).items():
        if doc["frozen"].get(f) != b:
            out.append(f"{f}: the frozen baseline {str(doc['frozen'].get(f))[:12]} is not what git held at frozen_at "
                       f"({str(b)[:12]}) -- the baseline is never rewritten; a change is a logged failure class")
    for i, c in enumerate(doc.get("failure_classes") or []):
        for k in ("id", "file", "found", "what", "plant", "new_blob"):
            if not c.get(k):
                out.append(f"failure class {i} has no {k!r}")
        plant = str(c.get("plant") or "")
        tf, _, name = plant.partition("::")
        if not (tf and name and name in _test_functions(os.path.join(root, tf))):
            out.append(f"failure class {c.get('id')}: plant {plant!r} does not exist")
        if c.get("file") in expected:
            expected[c["file"]] = c.get("new_blob")
        else:
            out.append(f"failure class {c.get('id')}: {c.get('file')!r} is not a frozen file")
    for f, b in expected.items():
        got = blob(f)
        if got != b:
            out.append(f"{f} changed ({got[:12]} != recorded {str(b)[:12]}): a frozen parser changes only with a "
                       "logged failure class and its plant (registry/regex_freeze.json)")
    return out


def test_frozen_parsers_are_unchanged_or_logged():
    assert freeze_problems(json.load(open(FREEZE, encoding="utf-8"))) == []


def test_plant_an_unlogged_change_is_refused():
    doc = json.load(open(FREEZE, encoding="utf-8"))
    edited = lambda f: "0" * 40 if f == "harness/components.py" else _blob(f)  # noqa: E731
    probs = freeze_problems(doc, blob=edited)
    assert len(probs) == 1 and "harness/components.py changed" in probs[0]


def test_plant_a_class_without_an_existing_plant_is_refused():
    doc = json.load(open(FREEZE, encoding="utf-8"))
    doc["failure_classes"] = [{"id": "X", "file": "harness/components.py", "found": "2026-10-13", "what": "x",
                               "plant": "tests/test_regex_freeze.py::test_no_such_plant",
                               "new_blob": _blob("harness/components.py")}]
    assert any("does not exist" in p for p in freeze_problems(doc))


def test_a_logged_class_with_its_plant_admits_the_new_blob():
    doc = json.load(open(FREEZE, encoding="utf-8"))
    doc["failure_classes"] = [{"id": "X", "file": "harness/components.py", "found": "2026-10-13", "what": "x",
                               "plant": "tests/test_regex_freeze.py::test_plant_an_unlogged_change_is_refused",
                               "new_blob": "f" * 40}]
    edited = lambda f: "f" * 40 if f == "harness/components.py" else _blob(f)  # noqa: E731
    assert freeze_problems(doc, blob=edited) == []


def test_mirrors_are_frozen_with_their_sources():
    fr = json.load(open(FREEZE, encoding="utf-8"))["frozen"]
    for f in ("components.py", "target_endpoint.py"):
        assert fr[f"harness/{f}"] == fr[f"docs/harness/{f}"]


def test_an_ambiguous_definition_abstains_rather_than_picking_one():
    """Route uncertain definition sentences to unresolved: two definitions that conflict on timepoint and a result
    that names neither leave the row UNBOUND with both candidates listed (never 'the first one')."""
    from harness import target_endpoint as te
    pool = [{"span": "The primary endpoint was death or MI at 30 days.", "components": {"death", "mi"},
             "ordinal": None, "timepoint": "30 days", "population": None},
            {"span": "The primary endpoint was death or MI at 36 months.", "components": {"death", "mi"},
             "ordinal": None, "timepoint": "36 months", "population": None}]
    res = te._resolve_reference("The primary endpoint occurred in 10% v 12%.", pool)
    assert res["selected"] is None and len(res["record"]["unresolved_alternatives"]) == 2


def test_plant_a_plant_named_only_inside_a_string_is_refused(tmp_path):
    """codex pr98-cap-r1 #1: 'def {name}(' as TEXT (a string literal, a comment) passed the plant check."""
    tf = tmp_path / "tests" / "test_x.py"
    tf.parent.mkdir()
    tf.write_text('S = "def test_ghost(): pass"\n# def test_ghost2():\n', encoding="utf-8")
    doc = {"frozen": {}, "failure_classes": [{"id": "X", "file": "f.py", "found": "d", "what": "w",
                                              "plant": "tests/test_x.py::test_ghost", "new_blob": "a" * 40}]}
    assert any("does not exist" in p for p in freeze_problems(doc, blob=lambda f: "a" * 40, root=str(tmp_path)))


def test_plant_a_rewritten_baseline_is_refused():
    """codex pr98-cap-r1 #2: rewriting `frozen` itself admitted a changed parser with no failure class. The baseline is
    whatever the files were at `frozen_at`, read from git -- never the registry's own claim."""
    doc = json.load(open(FREEZE, encoding="utf-8"))
    doc["frozen"]["harness/components.py"] = doc["frozen"]["docs/harness/components.py"] = "f" * 40
    probs = freeze_problems(doc, blob=lambda f: "f" * 40 if f.endswith("components.py") else _blob(f))
    assert any("baseline" in p for p in probs), probs


def test_plant_a_helper_is_not_a_plant():
    """codex pr98-cap-r2 #2: `_blob` (a helper, never collected) was accepted as a plant."""
    doc = json.load(open(FREEZE, encoding="utf-8"))
    doc["failure_classes"] = [{"id": "X", "file": "harness/components.py", "found": "d", "what": "w",
                               "plant": "tests/test_regex_freeze.py::_blob", "new_blob": "f" * 40}]
    probs = freeze_problems(doc, blob=lambda f: "f" * 40 if f == "harness/components.py" else _blob(f))
    assert any("does not exist" in p for p in probs), probs


def test_plant_moving_frozen_at_with_the_hashes_is_refused():
    """codex pr98-cap-r2 #1: rewriting frozen_at AND frozen together re-anchored the baseline. frozen_at is pinned HERE,
    in the gate: moving it is an edit to this file, visible in review (known limit: any in-repo gate can be edited)."""
    doc = json.load(open(FREEZE, encoding="utf-8"))
    doc["frozen_at"] = "HEAD"
    assert any("frozen_at" in p for p in freeze_problems(doc))


# Round 3 of 3 (codex pr98-cap-r3; review stops at three): recorded as KNOWN LIMITS, not fixed.
@pytest.mark.xfail(strict=True, reason="KNOWN LIMIT (codex pr98-cap-r3 #1): a test pytest excludes from collection "
                                       "(__test__ = False) is still accepted as a plant")
def test_known_limit_an_uncollected_test_is_accepted_as_a_plant(tmp_path):
    tf = tmp_path / "tests" / "test_x.py"
    tf.parent.mkdir()
    tf.write_text("def test_ghost():\n    pass\ntest_ghost.__test__ = False\n", encoding="utf-8")
    doc = {"frozen": {}, "failure_classes": [{"id": "X", "file": "f.py", "found": "d", "what": "w",
                                              "plant": "tests/test_x.py::test_ghost", "new_blob": "a" * 40}]}
    assert any("does not exist" in p for p in freeze_problems(doc, blob=lambda f: "a" * 40, root=str(tmp_path)))


@pytest.mark.xfail(strict=True, reason="KNOWN LIMIT (codex pr98-cap-r3 #2): the failure-class history is not "
                                       "append-only -- rewriting a logged class's new_blob admits a further change")
def test_known_limit_a_logged_class_can_be_rewritten():
    doc = json.load(open(FREEZE, encoding="utf-8"))
    doc["failure_classes"] = [{"id": "X", "file": "harness/components.py", "found": "d", "what": "w",
                               "plant": "tests/test_regex_freeze.py::test_plant_an_unlogged_change_is_refused",
                               "new_blob": "e" * 40}]
    # the registry as committed has NO class X: a class whose blob was rewritten in place must be refused
    probs = freeze_problems(doc, blob=lambda f: "e" * 40 if f == "harness/components.py" else _blob(f))
    assert probs, "a class absent from the committed history admitted a changed parser"


@pytest.mark.xfail(strict=True, reason="KNOWN LIMIT (agy pr98-cap-r3-agy): the mirror check compares the two static "
                                       "baseline entries, so a logged change to a source alone lets its mirror diverge")
def test_known_limit_a_logged_source_change_can_leave_its_mirror_behind():
    doc = json.load(open(FREEZE, encoding="utf-8"))
    doc["failure_classes"] = [{"id": "X", "file": "harness/components.py", "found": "d", "what": "w",
                               "plant": "tests/test_regex_freeze.py::test_plant_an_unlogged_change_is_refused",
                               "new_blob": "f" * 40}]
    probs = freeze_problems(doc, blob=lambda f: "f" * 40 if f == "harness/components.py" else _blob(f))
    assert any("mirror" in p for p in probs), "source and mirror diverged with no problem reported"
