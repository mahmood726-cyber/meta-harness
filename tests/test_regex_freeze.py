"""V1 regex freeze (Mahmood, 13 Oct, ruling 6): the definition-sentence parsers change only with a logged failure class
whose plant test exists, and the class records the file's new blob. Uncertain sentences abstain rather than parse harder."""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE = os.path.join(ROOT, "registry", "regex_freeze.json")


def _blob(path, root=ROOT):
    return subprocess.run(["git", "hash-object", "--", path], cwd=root, capture_output=True, text=True,
                          check=True).stdout.strip()


def freeze_problems(doc, blob=_blob, root=ROOT):
    """[problem] -- empty when every frozen file's bytes are its last recorded blob and every class names a plant."""
    expected = dict(doc["frozen"])
    out = []
    for i, c in enumerate(doc.get("failure_classes") or []):
        for k in ("id", "file", "found", "what", "plant", "new_blob"):
            if not c.get(k):
                out.append(f"failure class {i} has no {k!r}")
        plant = str(c.get("plant") or "")
        tf, _, name = plant.partition("::")
        if not (tf and name and os.path.exists(os.path.join(root, tf))
                and f"def {name}(" in open(os.path.join(root, tf), encoding="utf-8").read()):
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
