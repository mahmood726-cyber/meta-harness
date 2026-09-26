"""The R1-R4 scorecard, DERIVED from the tree it runs in -- never written by hand.

Per compiled pattern of harness/extract.py (23):
  R1 typed values   the value its consumer builds is a NamedTuple from harness/extract_values.py (checked in that
                    function's source), or not applicable with the reason (a classifier returns a bool; a dead pattern
                    has no consumer)
  R2 measured       precision / recall measured against recorded labels (outputs/regex_layer/MEASUREMENT.json)
  R3 planted        at least one accept and one refuse plant (regex_layer/specs.py), held by tests/test_regex_plants.py
  R4 refusal        the served object refuses number fragments (harness.whole_numbers.WholeNumbers), or not applicable
                    with the reason (a classifier captures no number; _EFFECT is also read by other lanes' modules)
Harness-wide: R3 sites with plants (regex_layer.inventory) and R2 sites measured (outputs/regex_layer/SITE_MEASUREMENT.json).

  python -m regex_layer.scorecard   -> outputs/regex_layer/SCORECARD.{json,md}
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

from harness import extract
from regex_layer.specs import ROLES, SPECS

ROOT = Path(__file__).resolve().parents[1]
# pattern -> (consumer function in extract.py, the typed value it must build)
R1_CONSUMER = {
    "_ARM": ("extract_arm_counts", "ArmHit"), "_ARM2": ("extract_arm_counts", "ArmHit"),
    "_ARM3": ("extract_arm_counts", "ArmHit"), "_ARM4": ("extract_arm_counts", "ArmHit"),
    "_ARMP": ("extract_arm_counts", "ArmPercentHit"), "_EFFECT": ("extract_effect>_effect_from_match", "Effect"),
    "_MEAN_SD": ("extract_continuous", "MeanSDHit"), "_MED_IQR": ("extract_continuous", "MeanSDHit"),
    "_RATE_EVPT": ("extract_rate", "RateHit"),
}
R1_SCALAR = {"_DENOM_EACH": "one integer (a denominator), not a tuple", "_NEQ": "integers (sample sizes), not a tuple",
             "_K": "one integer (a trial count), not a tuple"}


def r1(name: str) -> tuple[str, str]:
    if ROLES.get(name) == "dead":
        return "n/a", "dead: no reader in harness/"
    if SPECS[name]["kind"] == "classifier":
        return "n/a", "classifier: returns a bool"
    if name in R1_SCALAR:
        return "n/a", R1_SCALAR[name]
    fn, typ = R1_CONSUMER[name]
    reader, _, builder = fn.partition(">")          # 'reader>builder' when the match is read and typed in two functions
    builder = builder or reader
    ok = name in inspect.getsource(getattr(extract, reader)) and f"{typ}(" in inspect.getsource(getattr(extract, builder))
    return ("yes" if ok else "NO"), f"{fn} builds {typ}" if ok else f"{fn} does not build {typ}"


def r2(name: str, meas: dict) -> tuple[str, str]:
    row = meas.get(name)
    if not row or not row.get("measured_n"):
        return "NO", "not measured"
    return "yes", f"P {row['precision']}, sampled R {row['sampled_recall']} ({row['measured_n']} labels)"


def r3(name: str) -> tuple[str, str]:
    p = SPECS[name]["plants"]
    ok = bool(p.get("accept")) and bool(p.get("refuse"))
    return ("yes" if ok else "NO"), f"{len(p.get('accept', []))} accept / {len(p.get('refuse', []))} refuse plants"


def r4(name: str) -> tuple[str, str]:
    from harness.whole_numbers import WholeNumbers
    if ROLES.get(name) == "dead":
        return "n/a", "dead: no reader in harness/"
    if SPECS[name]["kind"] == "classifier":
        return "n/a", "classifier: captures no number"
    if isinstance(getattr(extract, name), WholeNumbers):
        return "yes", "number fragments refused (whole_numbers)"
    if name == "_EFFECT":
        return "n/a", "left unwrapped: also read by absence.py / reason_audit.py (other lane); 0 fragments in held text"
    return "NO", "fragments not refused"


def main() -> int:
    meas_p = ROOT / "outputs" / "regex_layer" / "MEASUREMENT.json"
    meas = {r["pattern"]: r for r in json.loads(meas_p.read_text(encoding="utf-8"))["rows"]} if meas_p.exists() else {}
    rows = []
    for name in sorted(SPECS):
        rows.append({"pattern": name, "kind": SPECS[name]["kind"], "role": ROLES.get(name),
                     **{k: dict(zip(("state", "why"), f(name) if k != "R2" else f(name, meas)))
                        for k, f in (("R1", r1), ("R2", r2), ("R3", r3), ("R4", r4))}})
    n = len(rows)

    def tally(k):
        yes = sum(r[k]["state"] == "yes" for r in rows)
        na = sum(r[k]["state"] == "n/a" for r in rows)
        return {"yes": yes, "n/a": na, "no": n - yes - na, "of": n,
                "line": f"{yes} of {n} ({na} not applicable, {n - yes - na} open)" if na else f"{yes} of {n}"}
    tot = {k: tally(k) for k in ("R1", "R2", "R3", "R4")}
    from regex_layer.inventory import planted, sites
    s_all = sites()
    wide = {"R3_harness_sites_planted": f"{sum(s['site'] in planted() for s in s_all)} of {len(s_all)}"}
    sm = ROOT / "outputs" / "regex_layer" / "SITE_MEASUREMENT.json"
    if sm.exists():
        d = json.loads(sm.read_text(encoding="utf-8"))
        wide["R2_other_sites_measured"] = f"{d['measured']} of {d['sites']}"
    out = ROOT / "outputs" / "regex_layer" / "SCORECARD"
    out.with_suffix(".json").write_text(json.dumps({"extract_py": tot, "harness_wide": wide, "rows": rows}, indent=1)
                                        + "\n", encoding="utf-8")
    md = ["# Regex layer scorecard (derived by `python -m regex_layer.scorecard`)", "",
          "| property | harness/extract.py (23 compiled patterns) |", "|---|---|"]
    md += [f"| {k} | **{tot[k]['line']}** |" for k in ("R1", "R2", "R3", "R4")]
    md += ["", "Harness-wide: " + "; ".join(f"{k} {v}" for k, v in wide.items()), "",
           "| pattern | kind / role | R1 | R2 | R3 | R4 |", "|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| `{r['pattern']}` | {r['kind']} / {r['role']} | " +
                  " | ".join(f"{r[k]['state']}: {r[k]['why']}" for k in ("R1", "R2", "R3", "R4")) + " |")
    out.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    for k in ("R1", "R2", "R3", "R4"):
        print(f"{k}: {tot[k]['line']}")
    print("harness-wide:", wide)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
