"""Compare HRM2 state, source-backed rows and statistics to the explicit lane base."""
import ast
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import gate, harms

BASE = "3cf73885ffc83f6fcc4db273c6510a5416cdcde0"


def base_file(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def main():
    rows = []
    for path in sorted((ROOT / "docs/reviews").glob("*/review.json")):
        before = json.loads(base_file(path.relative_to(ROOT).as_posix()))
        after = json.loads(path.read_text(encoding="utf-8"))
        checks = []
        for old, new in zip(before["outcomes"], after["outcomes"], strict=True):
            assert old["name"] == new["name"]
            # Every original input, identifier, date, source span and refusal field survives.
            for collection in ("trials", "declared_absent_trials"):
                for a, b in zip(old.get(collection, []), new.get(collection, []), strict=True):
                    for key in a:
                        if key == "study_effect":
                            derived = {"estimator_method", "correlation_handling"}
                            assert {k: v for k, v in a[key].items() if k not in derived} == {
                                k: v for k, v in b[key].items() if k not in derived}, (path.parent.name, old["name"], key)
                        elif key != "design":
                            assert a[key] == b.get(key), (path.parent.name, old["name"], key)
            a, b = old.get("result", {}), new.get("result", {})
            old_reporting = {r["id"]: r["state"] for r in a.get("harm_reporting_trials", [])}
            new_reporting = {r["id"]: r["state"] for r in b.get("harm_reporting_trials", [])}
            assert all(new_reporting.get(key) == value for key, value in old_reporting.items()), (
                path.parent.name, old["name"], "reporting states")
            added_reporting = sorted(set(new_reporting) - set(old_reporting))
            for key in added_reporting:
                trial = next(t for t in new.get("declared_absent_trials", [])
                             if harms._id_key(t.get("id")) == key)
                assert trial.get("harm_source_reported") is True
                assert new_reporting[key] == trial["harm_absence_state"]
            for key in ("state", "harms_incomplete", "known_reported_not_yet_extracted",
                        "k", "estimate", "ci_low", "ci_high", "tau2", "scale"):
                assert a.get(key) == b.get(key), (path.parent.name, old["name"], key)
            checks.append({"outcome": new["name"], "kind": new.get("kind"),
                           "suppressed": harms.synthesis_incomplete(new),
                           "additional_source_flagged_reporting_rows": added_reporting,
                           "inputs_states_debt_statistics_unchanged": True})
        assert not gate.check_harms_complete(str(path.parent))
        rows.append({"slug": path.parent.name, "outcomes": checks, "harms_complete": "PASS"})
    def function(source, name):
        tree = ast.parse(source)
        return ast.dump(next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name))
    assert function(base_file("harness/gate.py"), "check_harms_complete") == function(
        (ROOT / "harness/gate.py").read_text(encoding="utf-8"), "check_harms_complete")
    for path in ("harness/synth.py", "harness/membership.py"):
        assert base_file(path).decode().splitlines() == (ROOT / path).read_text(encoding="utf-8").splitlines()
    result = {"base": BASE, "N_pages": len(rows),
              "n_harm_outcomes_suppressed": sum(o["suppressed"] for r in rows for o in r["outcomes"]),
              "N_harm_outcomes": sum(o["kind"] == "harm" for r in rows for o in r["outcomes"]),
              "n_pages_with_suppression": sum(any(o["suppressed"] for o in r["outcomes"]) for r in rows),
              "topics": rows}
    output = ROOT / "outputs/hrm2/second-pass-audit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "topics"}))
    print("PASS: original trial inputs, debt states, refusal codes, source spans and statistical results preserved; design-derived labels excluded")


if __name__ == "__main__":
    main()
