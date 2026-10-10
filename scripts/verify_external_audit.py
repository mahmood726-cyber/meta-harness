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


# Bundles received 9-10 Oct (reviews 10, 12-16, 18-21): each is a FOLDER kept byte-for-byte under audit/external/<dir>.
# The whole folder is pinned (every file in SHA256SUMS; an unlisted file fails), copied to a temp dir and run there (the
# scripts write their results next to themselves -- never into the committed bytes), with UTF-8 mode on (review 16
# writes text without an encoding, which is cp1252 on Windows). The regenerated output must equal the auditor's committed
# one except for the named version-report paths; the pooled numbers must equal the served ones (or a SIGNED supersession).
# Reviews 11, 17 and 22-24 arrived as reports only (no executable bundle; r22's was mentioned, not attached).
# (dir, script, auditor output file, ignored output paths, [(label, slug, outcome, served field, path)])
BUNDLES = [
    ("review10", "review10_check_topic10.py", ("calculation_results.json", "review10_calculation_results.json"), [], [
        ("glp1 MACE estimate (r10)", "glp1-ra-mace-t2d", None, "estimate", ("eight_trial_pool", "hr")),
        ("glp1 MACE CI low (r10)", "glp1-ra-mace-t2d", None, "ci_low", ("eight_trial_pool", "ci95_modified_HKSJ", 0)),
        ("glp1 MACE CI high (r10)", "glp1-ra-mace-t2d", None, "ci_high", ("eight_trial_pool", "ci95_modified_HKSJ", 1)),
    ]),
    ("review12", "checks.py", "results.json", [], [
        ("melatonin SOL MD (r12)", "melatonin-primary-insomnia-sol", None, "estimate", ("arithmetic", "mean_difference_minutes")),
        ("melatonin SOL CI low (r12)", "melatonin-primary-insomnia-sol", None, "ci_low", ("arithmetic", "ci95_minutes", 0)),
        ("melatonin SOL CI high (r12)", "melatonin-primary-insomnia-sol", None, "ci_high", ("arithmetic", "ci95_minutes", 1)),
    ]),
    ("review13", "audit.py", "results.json", [("environment",)], [
        ("noac primary estimate (r13)", "noac-vs-warfarin-af-stroke", None, "estimate", ("primary", "estimate")),
        ("noac primary CI low (r13)", "noac-vs-warfarin-af-stroke", None, "ci_low", ("primary", "ci_low")),
        ("noac primary CI high (r13)", "noac-vs-warfarin-af-stroke", None, "ci_high", ("primary", "ci_high")),
    ]),
    # review 14 recomputes a pool the harness WITHHOLDS (sacubitril composite, k=2 refused): nothing served to compare;
    # the script's own assertions and its reproduced output are still checked
    ("review14", "audit.py", "results.json", [("runtime",)], []),
    ("review15", "audit_checks.py", "results.json", [], [
        ("semaglutide discontinuation RR (r15)", "semaglutide-obesity-mace",
         "Adverse events leading to permanent discontinuation", "estimate", ("discontinuation_reconstruction", "rr")),
    ]),
    ("review16", "audit_checks.py", "results.json", [], [
        ("semaglutide weight MD (r16)", "semaglutide-obesity-weight", None, "estimate", ("primary_reconstruction", "PM_estimate")),
    ]),
    ("review18", "audit.py", "results.json", [("scipy_version",)], [
        ("sglt2 HFrEF composite (r18)", "sglt2-hfref-hosp-cvdeath", None, "estimate", ("primary_reconstruction", "pooled_ratio")),
    ]),
    ("review19", "audit_topic19.py", "audit_results.json", [], [
        ("sglt2 hHF estimate (r19)", "sglt2-primary-prevention-hf", None, "estimate", ("primary", "pooled_hr")),
        ("sglt2 hHF CI low (r19)", "sglt2-primary-prevention-hf", None, "ci_low", ("primary", "hksj_floored_ci95", 0)),
        ("sglt2 hHF CI high (r19)", "sglt2-primary-prevention-hf", None, "ci_high", ("primary", "hksj_floored_ci95", 1)),
    ]),
    ("review20", "audit.py", "results.json", [("output",)], [
        ("MRA mortality estimate (r20)", "spironolactone-hfref-mortality", None, "estimate", ("primary_analysis", "effect")),
        ("MRA mortality CI low (r20)", "spironolactone-hfref-mortality", None, "ci_low", ("primary_analysis", "hksj_ci", 0)),
        ("MRA mortality CI high (r20)", "spironolactone-hfref-mortality", None, "ci_high", ("primary_analysis", "hksj_ci", 1)),
    ]),
    ("review21", "audit_topic21.py", "results.json", [("runtime",), ("output",)], [
        ("statins MVE estimate (r21)", "statins-primary-prevention-elderly", None, "estimate", ("current_two_inputs", "estimate")),
    ]),
    # reviews 27-29: received as zips; the zip and its unmodified topicNN_audit/ folder are both pinned
    ("review27", "topic27_audit/audit.py", ("topic27_audit/results.json", "topic27_audit/results.json"), [], [
        ("metformin ovulation OR (r27)", "metformin-pcos-ovulation", None, "estimate", ("primary", "OR")),
        ("metformin ovulation CI low (r27)", "metformin-pcos-ovulation", None, "ci_low", ("primary", "ci_low")),
        ("metformin ovulation CI high (r27)", "metformin-pcos-ovulation", None, "ci_high", ("primary", "ci_high")),
    ]),
    ("review28", "topic28_audit/audit.py", ("topic28_audit/results.json", "topic28_audit/results.json"), [], [
        ("omega3 MACE HR (r28)", "omega3-cardiovascular-events", None, "estimate", ("primary", "HR")),
        ("omega3 MACE CI low (r28)", "omega3-cardiovascular-events", None, "ci_low", ("primary", "ci_low")),
        ("omega3 MACE CI high (r28)", "omega3-cardiovascular-events", None, "ci_high", ("primary", "ci_high")),
    ]),
    # review 29's served pool is k=2 with the CI not served: only the point estimate is compared
    ("review29", "topic29_audit/audit.py", ("topic29_audit/results.json", "topic29_audit/results.json"), [], [
        ("pcsk9 MACE HR (r29)", "pcsk9-mace", None, "estimate", ("primary_independent_reconstruction", "HR")),
    ]),
    ("review25", "audit.py", "results.json", [], [
        ("colchicine secondary estimate (r25)", "colchicine-secondary-cv-prevention", None, "estimate", ("pooled", "estimate")),
        ("colchicine secondary CI low (r25)", "colchicine-secondary-cv-prevention", None, "ci_low", ("pooled", "lower")),
        ("colchicine secondary CI high (r25)", "colchicine-secondary-cv-prevention", None, "ci_high", ("pooled", "upper")),
    ]),
]


def _drop(obj, paths):
    import copy
    obj = copy.deepcopy(obj)
    for path in paths:
        cur = obj
        for p in path[:-1]:
            cur = cur.get(p) if isinstance(cur, dict) else None
        if isinstance(cur, dict):
            cur.pop(path[-1], None)
    return obj


def _compare(out, compares, superseded, signed, rows):
    bad = 0
    for label, slug, outcome, field, path in compares:
        aud = float(_dig(out, path))
        srv = _served(slug, outcome).get(field)
        ok = srv is not None and math.isfinite(aud) and abs(aud - float(srv)) <= TOL
        sup_ok = _valid_supersession(superseded.get(label), srv, signed)
        v = "PASS" if ok else ("SUPERSEDED" if sup_ok else "FAIL")
        rows.append({"check": label, "verdict": v, "auditor": round(aud, 6), "served": srv,
                     "detail": f"superseded by {superseded[label]['signed_item']}" if v == "SUPERSEDED" else ""})
        bad += v == "FAIL"
    return bad


def run_bundles(sums, superseded, signed):
    import shutil
    rows, bad = [], 0
    for d, script, outspec, ignore, compares in BUNDLES:
        base = os.path.join(EXT, d)
        files = sorted(os.path.relpath(os.path.join(r, f), EXT).replace(os.sep, "/")
                       for r, _, fs in os.walk(base) for f in fs)
        listed = sorted(n for n in sums if n.startswith(d + "/"))
        wrong = [f for f in files if sums.get(f) != hashlib.sha256(open(os.path.join(EXT, f), "rb").read()).hexdigest()]
        if wrong or files != listed or not files:
            rows.append({"check": f"{d} bundle bytes", "verdict": "FAIL",
                         "detail": f"changed: {wrong[:3]}; unlisted: {sorted(set(files) - set(listed))[:3]}; "
                                   f"missing: {sorted(set(listed) - set(files))[:3]}"})
            bad += 1
            continue
        produced, committed = outspec if isinstance(outspec, tuple) else (outspec, outspec)
        with tempfile.TemporaryDirectory() as td:
            work = os.path.join(td, d)
            shutil.copytree(base, work)
            p = subprocess.run([sys.executable, os.path.join(work, script)], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", cwd=work, timeout=600,
                               env=dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1"))
            if p.returncode != 0:
                rows.append({"check": f"{d}/{script} run", "verdict": "FAIL", "detail": (p.stderr or p.stdout)[-600:]})
                bad += 1
                continue
            out = json.load(open(os.path.join(work, produced), encoding="utf-8"))
        diffs = _same_json(_drop(out, ignore), _drop(json.load(open(os.path.join(base, committed), encoding="utf-8")), ignore))
        rows.append({"check": f"{d}/{script} reproduces {committed}", "verdict": "PASS" if not diffs else "FAIL",
                     "detail": "; ".join(diffs[:5])})
        bad += bool(diffs)
        bad += _compare(out, compares, superseded, signed, rows)
    return rows, bad


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
                # codex ext-audit-r2 P0: a script failing its own assertion after a SIGNED served change is excused only
                # when the entry (a) names a SEEN_AND_SIGNED item, (b) names the expected failure text, found in this
                # run's output, and (c) pins the served value of EVERY comparison this script makes, all still current.
                pins = (ent or {}).get("served") if isinstance((ent or {}).get("served"), dict) else {}
                expect = (ent or {}).get("failure_contains")
                v = "FAIL"
                if (ent and ent.get("signed_item") in signed and expect and expect in (p.stderr + p.stdout)
                        and compares and all(_valid_supersession({"signed_item": ent["signed_item"], "served": pins.get(lbl)},
                                                                 _served(sl, oc).get(fd), signed)
                                             for lbl, sl, oc, fd, _ in compares)):
                    v = "SUPERSEDED"
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
        bad += _compare(out, compares, superseded, signed, rows)
    brows, bbad = run_bundles(sums, superseded, signed)
    return rows + brows, bad + bbad


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
