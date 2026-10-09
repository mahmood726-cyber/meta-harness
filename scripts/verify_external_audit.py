"""Run the external auditors' own scripts (audit/external/, kept byte-for-byte as received) against what is SERVED now.

For every script:
  1. its bytes must match audit/external/SHA256SUMS (an edited auditor script is refused, never run);
  2. it must exit 0 -- its own assertions must hold;
  3. where the auditor also supplied the JSON it produced, our run must reproduce it (floats to 1e-9);
  4. its independently recomputed pooled numbers must equal the CURRENTLY SERVED docs/reviews/<slug>/review.json
     (served values are rounded to 4 dp, so agreement is |auditor - served| <= 6e-5).
A disagreement that a SIGNED served change explains is listed in audit/external/superseded.json with the item that
signed it; it is reported as SUPERSEDED, never silently passed. Anything else fails.

    python scripts/verify_external_audit.py [--json]
Exit 0 iff every check passes or is a recorded supersession.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.path.join(ROOT, "audit", "external")
TOL = 6e-5


def _served(slug, outcome=None):
    r = json.load(open(os.path.join(ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8"))
    for o in r.get("outcomes") or []:
        if (outcome is None and o.get("primary")) or o.get("name") == outcome:
            return o.get("result") or {}
    raise KeyError(f"{slug}: outcome {outcome or '<primary>'} not served")


# (script, args, auditor json or None, [(label, slug, outcome, served field, path into the auditor output)])
CHECKS = [
    ("review05_recalculation.py", [], None, [
        ("doac primary estimate", "doac-vte-recurrence", None, "estimate", ("mixed_primary", "estimate")),
        ("doac primary CI low", "doac-vte-recurrence", None, "ci_low", ("mixed_primary", "ci_low")),
        ("doac primary CI high", "doac-vte-recurrence", None, "ci_high", ("mixed_primary", "ci_high")),
    ]),
    ("review06_checks.py", [], "review06_checks.json", [
        ("dpp4 MACE estimate", "dpp4-mace-t2d", None, "estimate", ("mace_current", "estimate")),
        ("dpp4 MACE CI low", "dpp4-mace-t2d", None, "ci_low", ("mace_current", "calculated_hksj_95_ci", 0)),
        ("dpp4 MACE CI high", "dpp4-mace-t2d", None, "ci_high", ("mace_current", "calculated_hksj_95_ci", 1)),
        ("dpp4 HHF estimate", "dpp4-mace-t2d", "Hospitalization for heart failure", "estimate", ("hf_current", "estimate")),
    ]),
    ("review08_checks.py", ["--output", "{out}"], "review08_checks.json", [
        ("esketamine MD", "esketamine-trd-madrs", None, "estimate", ("primary", "mean_difference")),
        ("esketamine CI low", "esketamine-trd-madrs", None, "ci_low", ("primary", "hksj_95_ci", 0)),
        ("esketamine CI high", "esketamine-trd-madrs", None, "ci_high", ("primary", "hksj_95_ci", 1)),
    ]),
    ("review09_checks.py", [], "review09_checks.json", [
        ("finerenone estimate", "finerenone-ckd-t2d-renal", None, "estimate", ("kidney_composite_recalculation", "estimate")),
    ]),
    ("review09b_check_topic9.py", [], None, [
        ("finerenone estimate (9b)", "finerenone-ckd-t2d-renal", None, "estimate", ("pooled_hr",)),
    ]),
]


def _signed_items():
    """Every SEEN_AND_SIGNED packet item recorded in registry/v*_signatures.json."""
    import glob
    out = set()
    for f in glob.glob(os.path.join(ROOT, "registry", "v*_signatures.json")):
        d = json.load(open(f, encoding="utf-8"))
        for item, rec in (d.get("items") or {}).items():
            if isinstance(rec, dict) and rec.get("state") == "SEEN_AND_SIGNED":
                out.add(item)
    return out


def _valid_supersession(entry, served_value, signed):
    """codex ext-audit-r1 P0: a supersession excuses a disagreement only if it names a SEEN_AND_SIGNED item and pins the
    exact served value it excuses (so a later drift fails again). A bare label excuses nothing."""
    if not entry or entry.get("signed_item") not in signed:
        return False
    pinned = entry.get("served")
    return served_value is not None and isinstance(pinned, (int, float)) and abs(float(pinned) - float(served_value)) <= 1e-9


def _dig(obj, path):
    for p in path:
        obj = obj[p]
    return obj


def _same_json(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            return [f"{path}: keys differ"]
        return [d for k in a for d in _same_json(a[k], b[k], f"{path}/{k}")]
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} != {len(b)}"]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in _same_json(x, y, f"{path}[{i}]")]
    if isinstance(a, float) and isinstance(b, (int, float)) and not isinstance(b, bool):
        return [] if abs(a - b) <= 1e-9 * max(1.0, abs(b)) else [f"{path}: {a} != {b}"]
    return [] if a == b else [f"{path}: {str(a)[:60]} != {str(b)[:60]}"]


def run():
    sums = {}
    for line in open(os.path.join(EXT, "SHA256SUMS"), encoding="utf-8"):
        h, name = line.split(maxsplit=1)
        sums[name.strip().lstrip("*")] = h
    superseded = {}
    sp = os.path.join(EXT, "superseded.json")
    if os.path.exists(sp):
        superseded = {s["check"]: s for s in json.load(open(sp, encoding="utf-8")).get("superseded") or []}
    rows, bad = [], 0
    signed = _signed_items()
    for script, args, aud_json, compares in CHECKS:
        for f in [script] + ([aud_json] if aud_json else []):
            got = hashlib.sha256(open(os.path.join(EXT, f), "rb").read()).hexdigest()
            if sums.get(f) != got:
                rows.append({"check": f"{f} bytes", "verdict": "FAIL", "detail": f"sha256 {got} != SHA256SUMS {sums.get(f)}"})
                bad += 1
        if any(r["verdict"] == "FAIL" and r["check"].startswith(script) for r in rows):
            continue
        with tempfile.TemporaryDirectory() as td:
            out_path = os.path.join(td, "out.json")
            argv = [sys.executable, os.path.join(EXT, script)] + [a.replace("{out}", out_path) for a in args]
            p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace",
                               cwd=td, env=dict(os.environ, PYTHONIOENCODING="utf-8"), timeout=600)
            if p.returncode != 0:
                key = f"{script} run"
                ent = superseded.get(key)
                v = "SUPERSEDED" if (ent and ent.get("signed_item") in signed) else "FAIL"
                rows.append({"check": key, "verdict": v,
                             "detail": (f"superseded by {ent['signed_item']}" if v == "SUPERSEDED" else "")
                             + (p.stderr or p.stdout)[-600:]})
                bad += v == "FAIL"
                continue
            out = json.load(open(out_path, encoding="utf-8")) if "{out}" in " ".join(args) else json.loads(p.stdout)
        if aud_json:
            diffs = _same_json(out, json.load(open(os.path.join(EXT, aud_json), encoding="utf-8")))
            rows.append({"check": f"{script} reproduces {aud_json}", "verdict": "PASS" if not diffs else "FAIL",
                         "detail": "; ".join(diffs[:5])})
            bad += bool(diffs)
        for label, slug, outcome, field, path in compares:
            aud = float(_dig(out, path))
            srv = _served(slug, outcome).get(field)
            ok = srv is not None and math.isfinite(aud) and abs(aud - float(srv)) <= TOL
            sup_ok = _valid_supersession(superseded.get(label), srv, signed)
            v = "PASS" if ok else ("SUPERSEDED" if sup_ok else "FAIL")
            rows.append({"check": label, "verdict": v, "auditor": round(aud, 6), "served": srv,
                         "detail": f"superseded by {superseded[label]['signed_item']}" if v == "SUPERSEDED" else ""})
            bad += v == "FAIL"
    return rows, bad


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    rows, bad = run()
    if "--json" in argv:
        print(json.dumps({"rows": rows, "failures": bad}, indent=1))
    else:
        for r in rows:
            extra = f" auditor={r['auditor']} served={r['served']}" if "auditor" in r else ""
            print(f"[{r['verdict']:>10}] {r['check']}{extra} {r.get('detail') or ''}".rstrip())
        print(f"EXTERNAL-AUDIT: {len(rows)} checks, {bad} failing")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
