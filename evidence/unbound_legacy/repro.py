"""UNBOUND_LEGACY fail-open, reproduced on the REAL producer (external audit, 2026-09-26; BUNDLE limit L10_admit_rows_fail_open).

usage: python evidence/unbound_legacy/repro.py [<ref whose harness/ to run>]   (default: the working tree)
Every row is built from held bytes: the GLP-1 records.json abstract at the pinned candidate 3876a62d. Classification is the real
classify_bound(); the verdict is the real admissibility() and admit_rows(). Nothing is mocked. Prints one JSON line per case."""
import copy
import importlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"      # v1/candidate: the served bytes the rows are read from
SLUG = "glp1-ra-mace-t2d"


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL, check=True).stdout


def load_harness(ref):
    """harness/ from the working tree (ref None) or exported from a commit (the pre-fix producer), imported under its own name."""
    if ref is None:
        base = ROOT
    else:
        base = tempfile.mkdtemp(prefix="unbound_prefix_")
        for path in _git("ls-tree", "-r", "--name-only", ref, "harness").decode().split():
            out = os.path.join(base, *path.split("/"))
            os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, "wb").write(_git("show", f"{ref}:{path}"))
    for m in [m for m in sys.modules if m == "harness" or m.startswith("harness.")]:
        del sys.modules[m]
    sys.path.insert(0, base)
    try:
        return importlib.import_module("harness.target_endpoint")
    finally:
        sys.path.remove(base)


def fixtures():
    recs = {str(r["id"]): r for r in json.loads(_git("show", f"{PINNED}:docs/cache/{SLUG}/records.json"))["records"]}
    spec = json.loads(_git("show", f"{PINNED}:topics/{SLUG}.json"))["primary_outcome"]
    elixa_abs = recs["26630143"]["abstract"]
    elixa_sentence = next(s for s in elixa_abs.split(". ") if "hazard ratio, 1.02" in s) + "."
    leader_abs = recs["27295427"]["abstract"]
    leader_sentence = next(s for s in leader_abs.split(". ") if "hazard ratio, 0.87" in s) + "."
    elixa = {"label": "ELIXA", "id": "PMID 26630143", "effect": 1.02, "ci_low": 0.89, "ci_high": 1.17, "scale": "HR",
             "source": "abstract effect+CI (HR): " + elixa_sentence[:200], "provenance": "abstract"}
    leader = {"label": "LEADER", "id": "PMID 27295427", "effect": 0.87, "ci_low": 0.78, "ci_high": 0.97, "scale": "HR",
              "source": "abstract effect+CI (HR): " + leader_sentence[:200], "provenance": "abstract"}
    return spec, {"26630143": elixa_abs, "27295427": leader_abs}, elixa, leader


def classified(te, spec, abstract, row):
    r = copy.deepcopy(row)
    r.update(te.classify_bound(spec, abstract, r["source"]))
    return r


def verdict(te, spec, row):
    v = te.admissibility(spec, copy.deepcopy(row))
    kept, refused = te.admit_rows(spec, [copy.deepcopy(row)])
    return {"admissible": v.get("admissible"), "verdict": v.get("verdict"), "kept_by_admit_rows": bool(kept),
            "refused_code": refused[0].get("reason_code") if refused else None}


def cases(te):
    spec, abstracts, elixa, leader = fixtures()
    e = classified(te, spec, abstracts["26630143"], elixa)
    l = classified(te, spec, abstracts["27295427"], leader)
    stripped = {k: v for k, v in e.items() if not k.startswith("target_endpoint")}
    return [("authentic 3-point (LEADER), classified", l.get("target_endpoint_class"), verdict(te, spec, l)),
            ("ELIXA 4-point, classified", e.get("target_endpoint_class"), verdict(te, spec, e)),
            ("ELIXA 4-point, endpoint class DELETED", None, verdict(te, spec, stripped)),
            ("ELIXA 4-point, class restored", e.get("target_endpoint_class"), verdict(te, spec, e)),
            ("authentic 3-point (LEADER), class restored", l.get("target_endpoint_class"), verdict(te, spec, l))]


if __name__ == "__main__":
    ref = sys.argv[1] if len(sys.argv) > 1 else None
    te = load_harness(ref)
    print(json.dumps({"producer": ref or "working tree", "target_endpoint_blob":
                      _git("rev-parse", f"{ref}:harness/target_endpoint.py").decode().strip() if ref else
                      _git("hash-object", "harness/target_endpoint.py").decode().strip()}))
    for name, cls, v in cases(te):
        print(json.dumps({"case": name, "class": cls, **v}))
