"""Gate scorecard inventory and checks.

The scorecard is a measured registry, not a firing count: every production gate
must appear, including gates that have never been exercised.
"""
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from typing import Any

from harness.target import TargetUnresolvable, describe_target, refusal as target_refusal


REGISTRY_PATH = "registry/gate_scorecard.json"
SERVED_PATH = "docs/gate_scorecard.json"
AUDITOR_SENTENCE = (
    "A gate architecture that gets noisy teaches people to bypass it, and the "
    "pressure to bypass always arrives as impatience."
)
UNVALIDATED_SENTENCE = "a gate with no adjudicated true refusal in production is UNVALIDATED, not green"
EVENT_LISTS = ("plant_validations", "true_refusals", "false_refusals", "known_misses", "unresolved")
PRODUCTION_EVENT_LISTS = ("true_refusals", "false_refusals")
PLACEHOLDER_UTC = "2026-09-14T00:00:00Z"
ISO_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _root_path(root) -> str:
    return os.path.abspath(os.fspath(root))


def _read_ast(root: str, rel: str) -> ast.Module:
    with open(os.path.join(root, *rel.split("/")), encoding="utf-8") as f:
        return ast.parse(f.read(), filename=rel)


def _docline(node: ast.AST, fallback: str) -> str:
    doc = ast.get_docstring(node)
    if not doc:
        return fallback
    return " ".join(doc.strip().split()).split(". ")[0].rstrip(".") + "."


def _verify_all_gates(root: str) -> list[dict[str, str]]:
    tree = _read_ast(root, "scripts/verify_all.py")
    fn_names = {
        node.name: _docline(node, f"Verification limb {node.name}.")
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }
    out: list[dict[str, str]] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "LIMBS" for t in node.targets):
            continue
        if not isinstance(node.value, (ast.List, ast.Tuple)):
            continue
        for item in node.value.elts:
            if not (isinstance(item, ast.Tuple) and len(item.elts) >= 2):
                continue
            label, fn = item.elts[0], item.elts[1]
            if isinstance(label, ast.Constant) and isinstance(label.value, str) and isinstance(fn, ast.Name):
                out.append({
                    "gate_id": f"verify_all.{fn.id}",
                    "where": f"scripts/verify_all.py:{fn.id}",
                    "what_it_refuses": label.value,
                })
        break
    return out


def _gate_py_gates(root: str) -> list[dict[str, str]]:
    tree = _read_ast(root, "harness/gate.py")
    out = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("check_"):
            out.append({
                "gate_id": f"gate.{node.name}",
                "where": f"harness/gate.py:{node.name}",
                "what_it_refuses": _docline(node, f"Page gate {node.name}."),
            })
    return sorted(out, key=lambda x: x["gate_id"])


def _census_gates(root: str) -> list[dict[str, str]]:
    text = open(os.path.join(root, "harness", "census.py"), encoding="utf-8").read()
    required = {
        "census.claim_check": (
            "_claim_check",
            "harness/census.py:_claim_check",
            "Build-time refusal when rendered significance wording contradicts the canonical claim object.",
        ),
        "census.proposition_check": (
            "proposition.contradictions",
            "harness/census.py:build_review_dir",
            "Build-time refusal on categorical, membership, or methodological proposition contradictions.",
        ),
        "census.compatibility_check": (
            "compat.check",
            "harness/census.py:build_review_dir",
            "Build-time refusal when a pooled outcome mixes incompatible effect classes.",
        ),
        "census.interval_provenance": (
            "_interval_provenance_check",
            "harness/census.py:_interval_provenance_check",
            "Build-time refusal when a rendered confidence interval lacks canonical-engine provenance.",
        ),
    }
    out = []
    for gate_id, (needle, where, what) in required.items():
        if needle in text:
            out.append({"gate_id": gate_id, "where": where, "what_it_refuses": what})
    return out


def _hook_gates(root: str) -> list[dict[str, str]]:
    hooks = os.path.join(root, ".githooks")
    out = []
    if not os.path.isdir(hooks):
        return out
    for name in sorted(os.listdir(hooks)):
        path = os.path.join(hooks, name)
        if os.path.isfile(path):
            out.append({
                "gate_id": "hook." + name.replace("-", "_"),
                "where": f".githooks/{name}:hook",
                "what_it_refuses": f"Local git {name} hook refusal.",
            })
    return out


def _static_gates() -> list[dict[str, str]]:
    return [
        {
            "gate_id": "ruleset.required_verify",
            "where": "docs/evidence/gate-authority-2026-09-14/05-ruleset-created.txt:ruleset",
            "what_it_refuses": "A main-branch update without the required verify status check.",
        },
        {
            "gate_id": "deploy.check_artifact",
            "where": "scripts/production_record.py:cmd_check_artifact",
            "what_it_refuses": "A Pages artifact whose file set or digests differ from the verified manifest.",
        },
        {
            "gate_id": "deploy.attest",
            "where": "scripts/production_record.py:cmd_attest",
            "what_it_refuses": "A deployment whose served bytes do not hash back to the verified manifest.",
        },
        {
            "gate_id": "evidence_index.check",
            "where": "scripts/build_evidence_index.py:main(--check)",
            "what_it_refuses": "Uncaptioned evidence captures, stale evidence indexes, or captions for missing files.",
        },
        {
            "gate_id": "honest_ratchet.compare_blocks",
            "where": "harness/honest_ratchet.py:compare_blocks",
            "what_it_refuses": "Absent/banner honest-state blocks that vanish without a reviewed replacement acknowledgement.",
        },
        {
            "gate_id": "pipeline.structural_query_classifier",
            "where": "harness/pipeline.py:classify_query/classify_retrieval",
            "what_it_refuses": (
                "Retrieval-state underclassification from committed query structure: known-item, "
                "title-seeded, hand-written keyword, or concept search."
            ),
        },
    ]


def enumerate_gates(root) -> list[dict[str, str]]:
    """Enumerate production gates from the repository code and gate configuration."""
    root = _root_path(root)
    gates = []
    gates.extend(_verify_all_gates(root))
    gates.extend(_gate_py_gates(root))
    gates.extend(_census_gates(root))
    gates.extend(_hook_gates(root))
    gates.extend(_static_gates())
    seen = set()
    out = []
    for gate in gates:
        gid = gate["gate_id"]
        if gid in seen:
            continue
        seen.add(gid)
        out.append(gate)
    return out


def _registry_data(root: str) -> dict[str, Any]:
    with open(os.path.join(root, *REGISTRY_PATH.split("/")), encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return {"gates": data}
    return data


def _target_paths(root: str) -> list[str]:
    _ = root
    return [
        REGISTRY_PATH,
        SERVED_PATH,
        "scripts/verify_all.py",
        "harness/gate.py",
        "harness/census.py",
        "harness/gate_scorecard.py",
    ]


def describe_check_target(root) -> str:
    """Return the target line for the scorecard registry check."""

    root = _root_path(root)
    for rel in (REGISTRY_PATH, SERVED_PATH):
        if not os.path.isfile(_rel_path(root, rel)):
            return target_refusal("gate_scorecard", f"missing required path: {rel}")
    try:
        return describe_target(root, paths=_target_paths(root), label="gate_scorecard")
    except TargetUnresolvable as exc:
        return target_refusal("gate_scorecard", str(exc))


def _entries_by_id(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = data.get("gates")
    if not isinstance(entries, list):
        raise ValueError("registry/gate_scorecard.json must contain a 'gates' list")
    out = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("every gate scorecard entry must be an object")
        gid = entry.get("gate_id")
        if not isinstance(gid, str) or not gid:
            raise ValueError("every gate scorecard entry needs gate_id")
        if gid in out:
            raise ValueError(f"duplicate gate scorecard entry: {gid}")
        out[gid] = entry
    return out


def _evidence_values(event: dict[str, Any]) -> list[str]:
    raw = event.get("evidence", [])
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, str)]
    return []


def _rel_path(root: str, rel: str) -> str:
    return os.path.join(root, *rel.replace("\\", "/").split("/"))


def _commit_exists(root: str, sha: str) -> bool:
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", sha or ""):
        return False
    p = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    return p.returncode == 0


def _commit_utc_dates(root: str, sha: str) -> set[str]:
    p = subprocess.run(
        ["git", "show", "-s", "--format=%aI%n%cI", sha],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if p.returncode != 0:
        return set()
    out = set()
    for line in p.stdout.splitlines():
        try:
            dt = datetime.fromisoformat(line.strip().replace("Z", "+00:00"))
        except ValueError:
            continue
        out.add(dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    return out


def _evidence_exists(root: str, ev: str) -> bool:
    if ev.startswith("commit:"):
        return _commit_exists(root, ev.split(":", 1)[1])
    return os.path.exists(_rel_path(root, ev))


def _timestamp_in_evidence(root: str, when_utc: str, evidence: list[str]) -> bool:
    for ev in evidence:
        if ev.startswith("commit:"):
            if when_utc in _commit_utc_dates(root, ev.split(":", 1)[1]):
                return True
            continue
        try:
            text = open(_rel_path(root, ev), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if when_utc in text:
            return True
    return False


def _event_dates(entry: dict[str, Any]) -> list[str]:
    dates = []
    for name in PRODUCTION_EVENT_LISTS:
        for event in entry.get(name) or []:
            if isinstance(event, dict) and isinstance(event.get("when_utc"), str):
                dates.append(event["when_utc"])
    return sorted(dates)


def _expected_view(root: str) -> str:
    return json.dumps(served_view(root), indent=1, sort_keys=True) + "\n"


def check(root) -> tuple[bool, list[str]]:
    """Check registry coverage, evidence paths, precision counts, and served-view currency."""
    root = _root_path(root)
    target_line = describe_check_target(root)
    if target_line.startswith("TARGET gate_scorecard: COULD-NOT-EXECUTE"):
        return False, [target_line]
    reasons: list[str] = []
    enumerated = {gate["gate_id"]: gate for gate in enumerate_gates(root)}
    try:
        data = _registry_data(root)
        entries = _entries_by_id(data)
    except Exception as exc:  # noqa: BLE001
        return False, [f"{REGISTRY_PATH} unreadable or malformed: {exc}"]

    for gate_id in sorted(set(enumerated) - set(entries)):
        reasons.append(f"{REGISTRY_PATH} missing entry for enumerated gate {gate_id}")
    for gate_id in sorted(set(entries) - set(enumerated)):
        reasons.append(f"{REGISTRY_PATH} has entry for non-enumerated gate {gate_id}")

    for gate_id, entry in sorted(entries.items()):
        for field in (
            "where",
            "what_it_refuses",
            "validation",
            "production_status",
            "exercised",
            "precision_among_adjudicated",
        ):
            if field not in entry:
                reasons.append(f"{gate_id}: missing {field}")
        true_events = entry.get("true_refusals") if isinstance(entry.get("true_refusals"), list) else []
        false_events = entry.get("false_refusals") if isinstance(entry.get("false_refusals"), list) else []
        plant_events = entry.get("plant_validations") if isinstance(entry.get("plant_validations"), list) else []
        has_exercise = bool(true_events or false_events)
        expected_validation = "PRODUCTION" if has_exercise else ("PLANT_ONLY" if plant_events else "NO_VALIDATION")
        expected_production_status = "EXERCISED" if has_exercise else "UNVALIDATED"
        if entry.get("validation") != expected_validation:
            reasons.append(f"{gate_id}: validation must be {expected_validation}")
        if entry.get("production_status") != expected_production_status:
            reasons.append(f"{gate_id}: production_status must be {expected_production_status}")
        for name in EVENT_LISTS:
            events = entry.get(name)
            if not isinstance(events, list):
                reasons.append(f"{gate_id}: {name} must be a list")
                continue
            for idx, event in enumerate(events):
                if not isinstance(event, dict):
                    reasons.append(f"{gate_id}: {name}[{idx}] must be an object")
                    continue
                if name == "plant_validations":
                    if not isinstance(event.get("test"), str) or not event.get("test"):
                        reasons.append(f"{gate_id}: plant_validations[{idx}] needs test")
                    if "when_utc" in event:
                        reasons.append(f"{gate_id}: plant_validations[{idx}] must not carry when_utc")
                elif name in PRODUCTION_EVENT_LISTS:
                    when = event.get("when_utc")
                    if not isinstance(when, str):
                        reasons.append(f"{gate_id}: {name}[{idx}] needs dated when_utc")
                    elif when == PLACEHOLDER_UTC:
                        reasons.append(f"{gate_id}: {name}[{idx}] uses placeholder timestamp {PLACEHOLDER_UTC}")
                    elif not ISO_UTC_RE.fullmatch(when):
                        reasons.append(f"{gate_id}: {name}[{idx}] timestamp must be ISO UTC seconds")
                    else:
                        evidence = _evidence_values(event)
                        if not _timestamp_in_evidence(root, when, evidence):
                            reasons.append(f"{gate_id}: {name}[{idx}] timestamp {when} not found in cited evidence")
                    if name == "true_refusals":
                        bad_tests = [ev for ev in _evidence_values(event) if ev.replace("\\", "/").startswith("tests/")]
                        if bad_tests:
                            reasons.append(f"{gate_id}: pytest/test evidence cannot be counted as a true production refusal: {bad_tests}")
                else:
                    when = event.get("when_utc")
                    if when == PLACEHOLDER_UTC:
                        reasons.append(f"{gate_id}: {name}[{idx}] uses placeholder timestamp {PLACEHOLDER_UTC}")
                    elif isinstance(when, str) and not ISO_UTC_RE.fullmatch(when):
                        reasons.append(f"{gate_id}: {name}[{idx}] timestamp must be ISO UTC seconds")
                for ev in _evidence_values(event):
                    if not _evidence_exists(root, ev):
                        reasons.append(f"{gate_id}: cited evidence does not exist: {ev}")
        if bool(entry.get("exercised")) != has_exercise:
            reasons.append(f"{gate_id}: exercised must be {has_exercise} based on production true/false refusals")
        dates = _event_dates(entry)
        if has_exercise and not entry.get("last_exercised_utc"):
            reasons.append(f"{gate_id}: last_exercised_utc required when exercised")
        if dates and entry.get("last_exercised_utc") != dates[-1]:
            reasons.append(f"{gate_id}: last_exercised_utc must equal latest event date {dates[-1]}")
        if not has_exercise and entry.get("last_exercised_utc") is not None:
            reasons.append(f"{gate_id}: last_exercised_utc must be null when never exercised")

        prec = entry.get("precision_among_adjudicated")
        if not isinstance(prec, dict):
            reasons.append(f"{gate_id}: precision_among_adjudicated must be an object")
            continue
        if "true" not in prec or "false" not in prec:
            reasons.append(f"{gate_id}: precision stated without both true and false counts")
            continue
        true_n, false_n = prec.get("true"), prec.get("false")
        if not isinstance(true_n, int) or not isinstance(false_n, int):
            reasons.append(f"{gate_id}: precision counts must be integers")
            continue
        if true_n != len(entry.get("true_refusals") or []) or false_n != len(entry.get("false_refusals") or []):
            reasons.append(f"{gate_id}: precision counts must match true_refusals/false_refusals list lengths")
        value = prec.get("value")
        denom = true_n + false_n
        if denom == 0:
            if value is not None:
                reasons.append(f"{gate_id}: precision value must be null with zero adjudicated refusals")
        elif not isinstance(value, (int, float)) or abs(value - (true_n / denom)) > 1e-9:
            reasons.append(f"{gate_id}: precision value must equal true/(true+false)")

    prior = data.get("prior_precision_measurement")
    if isinstance(prior, dict):
        if prior.get("when_utc") == PLACEHOLDER_UTC:
            reasons.append(f"prior_precision_measurement uses placeholder timestamp {PLACEHOLDER_UTC}")
        for ev in _evidence_values(prior):
            if not _evidence_exists(root, ev):
                reasons.append(f"prior_precision_measurement evidence does not exist: {ev}")

    if data.get("generated_utc") == PLACEHOLDER_UTC:
        reasons.append(f"generated_utc uses placeholder timestamp {PLACEHOLDER_UTC}")

    served = os.path.join(root, *SERVED_PATH.split("/"))
    try:
        current = open(served, encoding="utf-8").read()
    except OSError as exc:
        reasons.append(f"{SERVED_PATH} unreadable: {exc}")
    else:
        want = _expected_view(root)
        if current != want:
            reasons.append(f"{SERVED_PATH} is stale; run python scripts/render_gate_scorecard.py")
    return not reasons, reasons


def summary(root) -> dict[str, Any]:
    """Return the compact scorecard summary rendered on the site index."""
    root = _root_path(root)
    data = _registry_data(root)
    entries = _entries_by_id(data)
    unvalidated = sorted(g for g, e in entries.items() if not e.get("exercised"))
    plant_only = sorted(g for g, e in entries.items() if e.get("validation") == "PLANT_ONLY")
    true_gates = sorted(g for g, e in entries.items() if e.get("true_refusals"))
    false_gates = sorted(g for g, e in entries.items() if e.get("false_refusals"))
    return {
        "gate_count": len(entries),
        "plant_only_count": len(plant_only),
        "plant_only": plant_only,
        "unvalidated_count": len(unvalidated),
        "unvalidated": unvalidated,
        "production_true_refusal_gate_count": len(true_gates),
        "production_true_refusal_gates": true_gates,
        "false_refusal_gate_count": len(false_gates),
        "false_refusal_gates": false_gates,
        "named_pessimistic_incident": (
            "fix-state checker refused an evidence-only commit because the subject contained "
            "'refusing' (commit 6b1039cd records the incident)"
        ),
        "auditor_sentence": AUDITOR_SENTENCE,
        "unvalidated_sentence": UNVALIDATED_SENTENCE,
        "prior_precision_measurement": data.get("prior_precision_measurement", "not found in this repository"),
    }


def served_view(root) -> dict[str, Any]:
    """Generated JSON view served from docs/gate_scorecard.json."""
    root = _root_path(root)
    data = _registry_data(root)
    entries = _entries_by_id(data)
    return {
        "_doc": "Generated from registry/gate_scorecard.json; do not hand-edit.",
        "source": REGISTRY_PATH,
        "auditor_sentence": AUDITOR_SENTENCE,
        "unvalidated_sentence": UNVALIDATED_SENTENCE,
        "summary": summary(root),
        "gates": [entries[k] for k in sorted(entries)],
    }


def write_served_view(root) -> str:
    root = _root_path(root)
    out = os.path.join(root, *SERVED_PATH.split("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(_expected_view(root))
    return out


def main(argv: list[str] | None = None) -> int:
    root = _root_path(os.getcwd())
    target_line = describe_check_target(root)
    print(target_line)
    if target_line.startswith("TARGET gate_scorecard: COULD-NOT-EXECUTE"):
        print("gate scorecard: COULD-NOT-EXECUTE")
        return 1
    ok, reasons = check(root)
    if ok:
        s = summary(root)
        print(
            "gate scorecard: PASS "
            f"({s['gate_count']} gates; {s['plant_only_count']} PLANT_ONLY; "
            f"{s['unvalidated_count']} UNVALIDATED; "
            f"{s['production_true_refusal_gate_count']} with production true refusals; "
            f"{s['false_refusal_gate_count']} with false refusals)"
        )
        return 0
    print("gate scorecard: REFUSED")
    for reason in reasons:
        print(f"  - {reason}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
