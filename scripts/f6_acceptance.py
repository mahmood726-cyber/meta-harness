"""F6 controlled-input audit. No enforcement code is replaced or edited.

Run with Python 3.13 from this checkout. Every case rebuilds ONLY the named
topic, calls its publication gate, and runs the independent bundle verifier.
The --worker mode is internal. A trace hook plants DATA at the pooling call
boundary; the original producer, renderer, gate and statistics execute.
Unsupported representations are reported, never replaced by a passing no-op.
All transient files and the byte-for-byte restoration archive live in .tmp/.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import dataclasses
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import traceback
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SLUG = "glp1-ra-mace-t2d"
WORK = ROOT / ".tmp" / "f6"
REVIEW = ROOT / "docs" / "reviews" / SLUG
REG = "outputs/handover/glp1_regulatory/regulatory_sources_glp1.json"
FIELDS = ("artifact_integrity", "state_reproduction", "input_linkage",
          "scientific_admission", "publication_eligibility")
CASES = [
    "baseline", "reorder_records", "reorder_pool_records", "display_columns",
    "reversed_target", "rotated_ids", "unknown_id", "duplicate_id", "omitted_id",
    "altered_inputs_updated_aggregate", "rewind_arm_swap", "estimand_missing",
    "estimand_malformed", "estimand_false_semantics", "freedom_wrong_row",
    "freedom_mixed_row", "freedom_numeric_prefix", "freedom_decimal_normalisation",
    "schema_detector_control",
]
POOL_CASES = {"reorder_pool_records", "reversed_target", "rotated_ids", "unknown_id",
              "duplicate_id", "omitted_id", "altered_inputs_updated_aggregate",
              "estimand_missing", "estimand_malformed", "estimand_false_semantics",
              "schema_detector_control"}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compact(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in {"stdout", "stderr"} and isinstance(v, str) and len(v) > 4000:
                out[k] = v[:2000] + "\n[F6C middle omitted]\n" + v[-2000:]
                out[k + "_original_chars"] = len(v)
            else:
                out[k] = compact(v)
        return out
    if isinstance(obj, list):
        return [compact(v) for v in obj]
    return obj


def write(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    obj = compact(obj)
    data = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    if Path(path).name == "f6_repaired.json" and len(data.encode("utf-8")) > 19_000_000:
        obj["detail_dropped_for_cap"] = True
        for row in obj["cases"]:
            for item in (row, row.get("restored_acceptance", {})):
                for key in ("all_pool_calls", "selected_records_by_outcome", "rendered_results", "regulatory_facts"):
                    item.pop(key, None)
        data = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n"
    if Path(path).name == "f6_repaired.json" and len(data.encode("utf-8")) > 20_000_000:
        raise RuntimeError("F6C size cap reached; stop without oversized write")
    Path(path).write_text(data, encoding="utf-8", newline="\n")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def command(args):
    if args and args[0] == "python":
        args = [args[0], "-X", "utf8", *args[1:]]
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
               TMP=str(WORK), TEMP=str(WORK))
    started = time.monotonic()
    proc = subprocess.run(args, cwd=ROOT, env=env, capture_output=True,
                          encoding="utf-8", errors="replace")
    return {"command": [str(a) for a in args], "returncode": proc.returncode,
            "stdout": proc.stdout, "stderr": proc.stderr,
            "elapsed_seconds": round(time.monotonic() - started, 3)}


def call(name, fn):
    out, err = io.StringIO(), io.StringIO()
    started = time.monotonic()
    result = {"command": name, "returncode": 0}
    write(WORK / "worker-progress.json", {"stage": name, "state": "RUNNING"})
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            value = fn()
            if isinstance(value, int):
                result["returncode"] = value
    except Exception as exc:
        result.update(returncode=1, exception=type(exc).__name__, message=str(exc))
        traceback.print_exc(file=err)
    result.update(stdout=out.getvalue(), stderr=err.getvalue(), elapsed_seconds=round(time.monotonic() - started, 3))
    write(WORK / "worker-progress.json", {"stage": name, "state": "FINISHED", "returncode": result["returncode"]})
    return result


def discard_scratch():
    """Only delete our named temporary files after confirming exact restoration."""
    assert restore()
    for name in ("restore.zip", "restore.json", "case.json", "restored.json", "worker-progress.json"):
        p = (WORK / name).resolve()
        assert p.is_relative_to((ROOT / ".tmp").resolve())
        if p.is_file():
            p.unlink()


def snapshot():
    """Back up only the known single-topic write set, never copy the corpus."""
    if (WORK / "restore.zip").exists():
        raise RuntimeError("Pending restoration archive: use --restore first")
    bundle = read(REVIEW / "BUNDLE.json")
    paths = {"docs/index.html", "registry/blind_map.json", REG,
             f"topics/{SLUG}.json", f"cache/{SLUG}/records.json",
             f"cache/{SLUG}/verified_arms.json"}
    for artefact in bundle["artefacts"]:
        if artefact.get("state") == "SERVED":
            paths.add("docs/" + artefact["ref"])
    paths.add("docs/scripts/verify_bundle.py")
    for role in ("harness", "comparator"):
        token = "m" + hashlib.sha1(f"{SLUG}|{role}|mh-blind-v1".encode()).hexdigest()[:8]
        paths.add(f"docs/m/{token}/index.html")
    for p in REVIEW.rglob("*"):
        if p.is_file():
            paths.add(p.relative_to(ROOT).as_posix())
    paths.add(f"docs/reviews/{SLUG}/EXECUTION_RECORD.json")
    entries = {}
    with zipfile.ZipFile(WORK / "restore.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for rel in sorted(paths):
            p = ROOT / rel
            if p.is_file():
                data = p.read_bytes()
                archive.writestr(rel, data)
                entries[rel] = digest(data)
            else:
                entries[rel] = None
    write(WORK / "restore.json", entries)
    return {"files": len(entries), "archive_bytes": (WORK / "restore.zip").stat().st_size}


def restore():
    entries = read(WORK / "restore.json")
    with zipfile.ZipFile(WORK / "restore.zip") as archive:
        for rel, expected in entries.items():
            p = (ROOT / rel).resolve()
            if not p.is_relative_to(ROOT):
                raise RuntimeError(f"Unsafe restoration target: {p}")
            if expected is None:
                if p.is_file():
                    p.unlink()
            else:
                data = archive.read(rel)
                assert digest(data) == expected
                if not p.exists() or p.read_bytes() != data:
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(data)
    return all((not (ROOT / rel).exists()) if expected is None else
               digest((ROOT / rel).read_bytes()) == expected for rel, expected in entries.items())


def disk_plant(case):
    evidence = {"case": case, "applied": False, "kind": "none"}
    if case == "rewind_arm_swap":
        p = ROOT / "cache" / SLUG / "verified_arms.json"
        obj = read(p)
        row = obj["31189511"]
        keys = ("ai", "n1i", "ci", "n2i")
        evidence["before"] = {k: row[k] for k in keys}
        row["ai"], row["ci"] = row["ci"], row["ai"]
        row["n1i"], row["n2i"] = row["n2i"], row["n1i"]
        evidence["after"] = {k: row[k] for k in keys}
        evidence["source_span_unchanged"] = row["source_span"]
    elif case.startswith("freedom_"):
        p = ROOT / REG
        obj = read(p)
        row = next(d for src in obj["sources"] for d in src.get("decisions", [])
                   if d["trial"] == "FREEDOM-CVO")
        eff = row["effect"]
        evidence["before"] = copy.deepcopy(eff)
        # These values are extracted from the retained Table 19 text, not
        # supplied as research results by the harness.
        triples = re.findall(r"(\d+\.\d+) \((\d+\.\d+), (\d+\.\d+)\)", row["span"])
        assert len(triples) == 2, triples
        correct, wrong = [tuple(float(v) for v in t) for t in triples]
        evidence["source_table_tuples"] = triples
        if case == "freedom_wrong_row":
            values = wrong
        elif case == "freedom_mixed_row":
            values = (correct[0], correct[1], wrong[2])
        elif case == "freedom_numeric_prefix":
            values = (float(str(correct[0])[:-1]), correct[1], correct[2])
        else:
            values = tuple(float(f"{v:.2f}") for v in correct)
        eff.update(zip(("estimate", "ci_low", "ci_high"), values))
        evidence["after"] = copy.deepcopy(eff)
        evidence["source_span_unchanged"] = row["span"]
    else:
        return evidence
    write(p, obj)
    if case == "freedom_decimal_normalisation":
        text = p.read_text(encoding="utf-8")
        old = f'"estimate": {correct[0]},'
        new = f'"estimate": {correct[0]:.3f},'
        assert text.count(old) == 1, "Decimal spelling control must target exactly one decision"
        p.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
        evidence["json_numeric_lexeme"] = {"before": old, "after": new, "parsed_equal": read(p) == obj}
    evidence.update(applied=True, kind="on-disk input", path=p.relative_to(ROOT).as_posix())
    return evidence


class PoolPlant:
    """Trace DATA arguments; do not patch a function or alter a predicate.

    The selected trial objects stay untouched for ID/numeric substitution
    probes. This is precisely the selected-to-statistical-input join under test.
    The same deterministic input fixture runs during publication-gate replay.
    """
    def __init__(self, case, primary):
        from harness import pipeline
        from scripts import build_bundle
        self.pool_code = pipeline._pool_result.__code__
        self.bundle_code = build_bundle.pooled_reference.__code__
        self.producer_code = pipeline.build_review_core.__wrapped__.__code__
        self.case = case
        self.ids = {t["label"] for t in primary["trials"]}
        self.id_map = {t["label"]: t["id"] for t in primary["trials"]}
        self.calls = []
        self.actual_primary = None
        self.selected = None
        self.schema_before = None
        self.schema_after = None
        self.selected_outcomes = {}
        self.record_permutations = []
        self.native_reports = []

    def records(self, studies):
        result = []
        for s in studies:
            row = dataclasses.asdict(s)
            row["id"] = self.id_map.get(s.label, s.label)
            try:
                y, v = s.yi_vi()
                row.update(yi=y, vi=v, standard_error=math.sqrt(v))
            except Exception as exc:
                row["derivation_error"] = str(exc)
            result.append(row)
        return result

    def trace(self, frame, event, arg):
        if frame.f_code.co_name == "run" and Path(frame.f_code.co_filename).resolve() == ROOT / "scripts/verify_bundle.py":
            if event == "return" and isinstance(arg, dict):
                self.native_reports.append(copy.deepcopy(arg))
            return self.trace
        if event != "call":
            return None
        if frame.f_code is self.producer_code and self.case == "reorder_records":
            records = copy.deepcopy(frame.f_locals["records"])
            before = [r["id"] for r in records["records"]]
            records["records"].reverse()
            self.record_permutations.append({"before": before, "after": [r["id"] for r in records["records"]]})
            frame.f_locals["records"] = records
            return None
        if frame.f_code is self.pool_code:
            studies = frame.f_locals["studies"]
            caller = frame.f_back
            outcome_name = caller.f_locals.get("spec", {}).get("name") if caller.f_code.co_name == "_build_outcome" else None
            if outcome_name and frame.f_locals.get("require_study_effect"):
                self.selected_outcomes[outcome_name] = copy.deepcopy(caller.f_locals["trials"])
            is_primary = (caller.f_code.co_name == "_build_outcome"
                          and bool(caller.f_locals.get("spec", {}).get("primary"))
                          and {s.label for s in studies} == self.ids)
            before = self.records(studies)
            if is_primary:
                self.selected = copy.deepcopy(caller.f_locals["trials"])
            if is_primary and self.case in POOL_CASES:
                assert {s.label for s in studies} == self.ids
                if self.case == "reorder_pool_records":
                    studies.reverse()
                elif self.case == "rotated_ids":
                    labels = [s.label for s in studies]
                    for s, label in zip(studies, labels[1:] + labels[:1]):
                        s.label = label
                elif self.case == "unknown_id":
                    studies[0].label = "F6_SYNTHETIC_UNKNOWN_ID"
                elif self.case == "duplicate_id":
                    studies[1].label = studies[0].label
                elif self.case == "omitted_id":
                    studies.pop()
                elif self.case == "altered_inputs_updated_aggregate":
                    studies[0].effect *= 1.01
                elif self.case == "reversed_target":
                    for s in studies:
                        s.effect, s.ci_low, s.ci_high = 1 / s.effect, 1 / s.ci_high, 1 / s.ci_low
                elif self.case.startswith("estimand_") or self.case == "schema_detector_control":
                    # Copy before mutating: Study.study_effect aliases the selected
                    # row's object, which is not the boundary being tested here.
                    studies[0].study_effect = copy.deepcopy(studies[0].study_effect)
                    self.schema_before = copy.deepcopy(studies[0].study_effect)
                    if self.case == "estimand_missing":
                        studies[0].study_effect.pop("estimand")
                    elif self.case == "estimand_malformed":
                        studies[0].study_effect["estimand"] = {"unexpected": [None, 7]}
                    elif self.case == "estimand_false_semantics":
                        # OR is a supported measure spelling, deliberately false
                        # for this source-reported HR. Do not conflate an
                        # unknown enum spelling with a clinical mismatch.
                        studies[0].study_effect["estimand"] = "OR"
                        studies[0].study_effect["analysis_population"] = "per-protocol"
                    else:
                        studies[0].study_effect.pop("source_provenance")
                    self.schema_after = copy.deepcopy(studies[0].study_effect)
            after = self.records(studies)
            self.calls.append({"primary": is_primary, "outcome": outcome_name, "selected_inputs": before, "derived_inputs": after})
            if is_primary:
                self.actual_primary = after
            return None
        if frame.f_code is self.bundle_code:
            return self.bundle_trace
        return None

    def bundle_trace(self, frame, event, arg):
        if event == "line" and "primary" in frame.f_locals:
            if self.case in POOL_CASES and self.actual_primary:
                primary = copy.deepcopy(frame.f_locals["primary"])
                # The canonical bundle builder derives its aggregate normally
                # from the SAME planted inputs used by the producer. This is
                # input fixture propagation, not digest editing or re-signing.
                propagated = []
                for r in self.actual_primary:
                    # Preserve the full value-owning record, including identity
                    # fields a later repaired producer may inspect. Source text
                    # is only a fixture propagation key, never an admission rule.
                    owners = [t for t in primary["trials"] if t.get("source", "") == r.get("source", "")]
                    owner = copy.deepcopy(owners[0]) if len(owners) == 1 else {}
                    owner.update(id=r["id"], effect=r["effect"], ci_low=r["ci_low"], ci_high=r["ci_high"], scale="HR")
                    if "label" in r:
                        owner["label"] = r["label"]
                    if "study_effect" in r:
                        owner["study_effect"] = copy.deepcopy(r["study_effect"])
                    propagated.append(owner)
                primary["trials"] = propagated
                frame.f_locals["primary"] = primary
            frame.f_trace = None
            return None
        return self.bundle_trace


def evaluate_linkage(selected, derived):
    """Audit oracle only. NEVER feeds the producer/gate a decision."""
    if selected is None or derived is None:
        return {"verdict": "NOT_REACHED", "native_verdict": "NOT_IMPLEMENTED"}
    expected = {r["id"]: r for r in selected}
    ids = [r["id"] for r in derived]
    reasons = []
    for rid in ids:
        if rid not in expected:
            reasons.append(f"UNKNOWN_INPUT_ID {rid}")
    for rid in sorted(set(ids)):
        if ids.count(rid) > 1:
            reasons.append(f"DUPLICATE_INPUT_ID {rid}")
    for rid in expected:
        if rid not in ids:
            reasons.append(f"OMITTED_INPUT_ID {rid}")
    for row in derived:
        src = expected.get(row["id"])
        if src and any(row[k] != src.get(k) for k in ("effect", "ci_low", "ci_high")):
            reasons.append(f"INPUT_TUPLE_MISMATCH {row['id']}")
    return {"verdict": "FAIL" if reasons else "PASS", "native_verdict": "NOT_IMPLEMENTED",
            "basis": "F6 audit oracle: exact ID multiset and ID-owned tuple comparison", "reasons": reasons}


def worker(case, output):
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "scripts"))
    from scripts import build_topic, build_bundle
    from harness import gate
    primary = next(o for o in read(REVIEW / "review.json")["outcomes"] if o.get("primary"))
    plant = disk_plant(case)
    tracer = PoolPlant(case, primary)
    result = {"case": case, "plant": plant, "stages": [], "route": "complete topic producer -> renderer -> bundle -> publication gate; independent verifier after gate"}
    result["implementation_sha256"] = {f: digest((ROOT / f).read_bytes()) for f in ("scripts/build_topic.py", "scripts/build_bundle.py", "scripts/verify_bundle.py", "harness/gate.py")}
    sys.settrace(tracer.trace)
    try:
        build = call(f"scripts.build_topic.main({SLUG!r}, '2026-09-11')",
                     lambda: build_topic.main(SLUG, "2026-09-11", ["python", "scripts/f6_acceptance.py", "--worker", case]))
        result["stages"].append(dict(stage="producer_renderer", **build))
        if build["returncode"] == 0:
            bundle = call(f"scripts.build_bundle.main([{SLUG!r}])", lambda: build_bundle.main([SLUG]))
            result["stages"].append(dict(stage="bundle", **bundle))
            publication = call(f"python -m harness.gate docs/reviews/{SLUG}",
                               lambda: gate.main([str(REVIEW.relative_to(ROOT))]))
            result["stages"].append(dict(stage="publication_gate", **publication))
            if bundle["returncode"] == 0:
                verify = command(["python", "scripts/verify_bundle.py", "--root", "docs", "--slug", SLUG, "--json"])
                result["stages"].append(dict(stage="independent_verifier", **verify))
                try:
                    result["verifier"] = json.loads(verify["stdout"])
                except ValueError:
                    result["verifier"] = {"verdict": "UNPARSEABLE", "failures": [verify["stderr"]]}
        else:
            result["route"] = "producer refused/crashed before completed render; bundle and gate NOT_REACHED (no stale-output evaluation)"
    finally:
        sys.settrace(None)
    result["selected_records"] = tracer.selected
    result["derived_statistical_inputs"] = tracer.actual_primary
    result["all_pool_calls"] = tracer.calls
    result["selected_records_by_outcome"] = tracer.selected_outcomes
    if case == "reorder_records":
        plant.update(applied=bool(tracer.record_permutations), kind="complete fetched-record permutation at producer entry; source bytes and source locators unchanged",
                     permutations=tracer.record_permutations,
                     fixture_correction="Initial on-disk permutation invalidated comparator alias hashes/offsets and was an uncredited harness failure. Input enumeration is now permuted after cache load, before production screening/extraction.")
    if case in POOL_CASES:
        plant.update(applied=bool(tracer.actual_primary), kind="in-memory DATA at pipeline._pool_result call; same inputs propagated to bundle pooled_reference",
                     schema_before=tracer.schema_before, schema_after=tracer.schema_after)
    if case == "estimand_false_semantics":
        plant["fixture_correction"] = "The initial attempt used the noncanonical spelling ODDS_RATIO. The corrected fixture uses supported OR and per-protocol values against the held source-reported HR and registered ITT target, to isolate semantic mismatch rather than unknown-enum syntax."
    if case == "display_columns":
        plant.update(unsupported="This checkout has no configurable arm-owned display column object. No data-only column permutation could be applied; the baseline route ran, but it is NOT a positive-control demonstration.")
    if case == "reversed_target":
        plant.update(transformation={"distinct_target": "placebo vs GLP-1 RA", "basis": "Reciprocal ratio contrast: effect'=1/effect; lower'=1/upper; upper'=1/lower; yi'=-yi; vi'=vi; original arm observations remain owned by their source arms."},
                     unsupported="This fixture proves transformed statistical inputs only. No supported registered reversed-target representation was found; acceptance as a distinct target analysis is NOT demonstrated.")
    result["input_linkage_audit"] = evaluate_linkage(tracer.selected, tracer.actual_primary)
    if case == "reversed_target":
        result["input_linkage_audit"]["verdict"] = "UNPROVEN_TARGET_REPRESENTATION"
    if (REVIEW / "review.json").exists() and build["returncode"] == 0:
        review = read(REVIEW / "review.json")
        result["rendered_results"] = [{"outcome": o["name"], "primary": o.get("primary"), "result": o.get("result"), "trials": o.get("trials")} for o in review["outcomes"]]
        result["release_sha256"] = read(REVIEW / "CERTIFICATE.json")["release_sha256"]
        if result.get("verifier"):
            b = read(REVIEW / "BUNDLE.json")
            result["bundle_inputs"] = b["pooled_reference"]
            result["regulatory_facts"] = [r for r in b["regulatory_facts"] if r["trial"] == "FREEDOM-CVO"]
            result["artifact_sha256"] = {p.name: digest(p.read_bytes()) for p in REVIEW.iterdir() if p.is_file()}
    result["gate_native_reports"] = tracer.native_reports
    result["first_refusal"] = first_refusal(result)
    result["five_verdicts"] = verdicts(result)
    result["verdict_provenance"] = {
        "artifact_integrity": "Projection of independent verifier artefacts/supporting/certificate booleans; native named verdict absent.",
        "state_reproduction": "Independent verifier pool.reproduced_to_1e-9; native named verdict absent.",
        "input_linkage": "NOT_IMPLEMENTED on this tree. input_linkage_audit is a separate harness oracle, never a native refusal.",
        "scientific_admission": "Projection of primary-row final states; not clinical certification, and excludes unpooled regulatory facts.",
        "publication_eligibility": "Exact return code and stdout of harness.gate.main; full verify_all/CI/deploy not run."}
    native = result.get("verifier", {}).get("verdicts")
    if native:
        result["five_verdicts"] = dict(native)
        result["verdict_provenance"] = {k: "Exact independent verifier report.verdicts." for k in FIELDS}
    else:
        result["five_verdicts"]["input_linkage"] = "NOT_REACHED"
        result["verdict_provenance"]["input_linkage"] = "Independent verifier NOT_REACHED; gate_native_reports separately retains any native verifier report returned inside the gate (may inspect stale bundle after bundle refusal). No oracle substituted."
    result["publication_gate_verdict"] = next((s["stdout"].strip() for s in result["stages"] if s["stage"] == "publication_gate"), "NOT_REACHED")
    write(output, result)
    print(json.dumps({"case": case, "five_verdicts": result["five_verdicts"], "first_refusal": result["first_refusal"]}, ensure_ascii=True))
    return 0


def first_refusal(result):
    for stage in result["stages"]:
        if stage["returncode"] == 0:
            continue
        if stage["stage"] == "publication_gate":
            messages = [s.strip()[2:] for s in stage["stdout"].splitlines() if s.strip().startswith("- ")]
            message = messages[0] if messages else stage["stderr"]
        elif stage["stage"] == "independent_verifier":
            message = (result.get("verifier", {}).get("failures") or ["No named refusal"])[0]
        else:
            message = stage.get("message") or stage["stderr"].strip() or stage["stdout"].strip()
        prefix = message.split(":", 1)[0].split(" ", 1)[0]
        # Do not invent a semantic code from the first word of an exception
        # sentence (e.g. "study"). Preserve the native exception class instead.
        code = prefix if re.fullmatch(r"[A-Z][A-Z0-9_-]*", prefix) else stage.get("exception")
        if stage["stage"] == "bundle" and stage["stderr"].startswith("REFUSED"):
            lines = stage["stderr"].splitlines()
            first_problem = next((line.strip() for line in lines[1:] if line.strip()), "")
            code = first_problem.split(" ", 1)[0]
        return {"stage": stage["stage"], "code": code, "message": message,
                "stdout": stage["stdout"], "stderr": stage["stderr"]}
    return None


def verdicts(result):
    rep = result.get("verifier", {})
    integrity = "NOT_REACHED"
    if rep.get("certificate"):
        checks = [v for k, v in rep["certificate"].items() if isinstance(v, bool)]
        checks += [v for row in rep.get("artefacts", []) for k, v in row.items() if k in {"bytes_ok", "declared_digest_ok"}]
        checks += [r["ok"] for r in rep.get("supporting", [])]
        integrity = "PASS" if checks and all(checks) else "FAIL"
    reproduced = rep.get("pool", {}).get("reproduced_to_1e-9")
    rows = rep.get("rows", [])
    scientific = ("PASS" if all(r["final"] == "ADMISSIBLE" for r in rows) else "FAIL") if rows else "NOT_REACHED"
    pub = next((s for s in result["stages"] if s["stage"] == "publication_gate"), None)
    return dict(zip(FIELDS, [integrity, "PASS" if reproduced is True else "FAIL" if reproduced is False else "NOT_REACHED",
                            "NOT_IMPLEMENTED", scientific,
                            "PASS" if pub and pub["returncode"] == 0 else "REFUSED" if pub else "NOT_REACHED"]))


def run(cases, rerun=False):
    WORK.mkdir(parents=True, exist_ok=True)
    status = command(["git", "status", "--porcelain"])
    tracked_dirty = [s for s in status["stdout"].splitlines() if not s.startswith("??")]
    expected_file = ROOT / ".tmp/f6c-patched.json"
    expected = read(expected_file) if expected_file.exists() else read(ROOT / "f6_repaired.json")["measurement_setup"]["patched_sha256"]
    if any(digest((ROOT / f).read_bytes()) != h for f, h in expected.items()):
        raise RuntimeError("F6C patched source bytes changed")
    if any(line[3:].replace("\\", "/") not in expected for line in tracked_dirty):
        raise RuntimeError(f"Unexpected tracked edits: {tracked_dirty}")
    doc = command(["git", "show", "origin/enforcement-gate:docs/evidence/enforcement-gate-2026-09-21/18-release-acceptance-checklist.md"])
    report = {"head": command(["git", "rev-parse", "HEAD"])["stdout"].strip(), "topic": SLUG,
              "contract": doc, "contract_has_section_F": "## F" in doc["stdout"],
              "preflight_status": status, "disk_free_before": shutil.disk_usage(ROOT).free,
              "snapshot": snapshot(), "cases": [],
              "measurement_setup": {"patched_sha256": expected},
              "source_review": (read(ROOT / "f6_repaired.json").get("source_review", {})
                                if (ROOT / "f6_repaired.json").exists() else {})}
    if rerun:
        previous = read(ROOT / "f6_repaired.json")
        assert previous["head"] == report["head"]
        report["prior_attempts"] = previous.get("prior_attempts", []) + [r for r in previous["cases"] if r["case"] in cases]
        report["cases"] = [r for r in previous["cases"] if r["case"] not in cases]
        report["original_run_preflight"] = {k: previous[k] for k in ("preflight_status", "disk_free_before", "snapshot")}
    try:
        for case in cases:
            assert restore()
            run_cmd = command(["python", "scripts/f6_acceptance.py", "--worker", case, "--output", str(WORK / "case.json")])
            if run_cmd["returncode"]:
                raise RuntimeError(f"Harness worker failed: {run_cmd}")
            result = read(WORK / "case.json")
            result["worker_command"] = run_cmd
            assert restore()
            restore_cmd = command(["python", "scripts/f6_acceptance.py", "--worker", "baseline", "--output", str(WORK / "restored.json")])
            if restore_cmd["returncode"]:
                raise RuntimeError(f"Restored worker failed: {restore_cmd}")
            restored = read(WORK / "restored.json")
            result["restored_acceptance"] = restored
            result["restored_command"] = restore_cmd
            report["cases"].append(result)
            assert restore()
            write(ROOT / "f6_repaired.json", report)
            print(json.dumps({"case": case, "verdicts": result["five_verdicts"], "first_refusal": result["first_refusal"],
                              "restored": restored["five_verdicts"]}, ensure_ascii=True), flush=True)
    finally:
        report["original_bytes_restored"] = restore()
        report["disk_free_after"] = shutil.disk_usage(ROOT).free
        report["final_status"] = command(["git", "status", "--short"])
        write(ROOT / "f6_repaired.json", report)
    discard_scratch()
    return 0


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cases", nargs="+", choices=CASES)
    ap.add_argument("--rerun", nargs="+", choices=CASES, help="Replace named final cases while preserving their earlier attempts")
    ap.add_argument("--worker", choices=CASES)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--restore", action="store_true")
    args = ap.parse_args()
    if args.restore:
        print("RESTORED", restore())
        return 0
    if args.worker:
        return worker(args.worker, args.output)
    return run(args.rerun or args.cases or CASES, rerun=bool(args.rerun))


if __name__ == "__main__":
    raise SystemExit(main())
