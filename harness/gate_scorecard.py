"""Gate scorecard inventory, event adjudications, and checks.

The auditor correction is now the scorecard's organizing rule: if the same
environment labels its own gate outputs true or false, the shape is system
produces output -> system labels its own output correct -> agreement read as
validation. That is the 6/6 recall error in gate form. Every refusal is
therefore an event with an adjudication object, UNRESOLVED is first-class, and
gate numbers are computed only from those adjudication objects.
"""
from __future__ import annotations

import argparse
import ast
import copy
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from typing import Any

from harness.target import TargetUnresolvable, describe_target, refusal as target_refusal


REGISTRY_PATH = "registry/gate_scorecard.json"
SERVED_PATH = "docs/gate_scorecard.json"
SCHEMA_VERSION = 2

AUDITOR_CORRECTION = (
    "If the same environment labels its own gate outputs true or false, that is: "
    "system produces output -> system labels its own output correct -> agreement "
    "read as validation (the 6/6 recall shape). So every refusal is an EVENT "
    "with an ADJUDICATION OBJECT, and a gate's numbers are computed only from "
    "those objects."
)
AUDITOR_SENTENCE = AUDITOR_CORRECTION
UNVALIDATED_SENTENCE = "a gate with no adjudicated true refusal in production is UNVALIDATED, not green"
PRECISION_COVERAGE_SENTENCE = (
    "precision is reported only beside its adjudication coverage; an UNRESOLVED refusal is neither"
)
INDEPENDENCE_SENTENCE = (
    "adjudicator_independence is the share of adjudications made by an external_auditor; "
    "today it is expected to be 0 because no external-auditor adjudication is recorded"
)

LEGACY_EVENT_LISTS = ("plant_validations", "true_refusals", "false_refusals", "known_misses", "unresolved")
LEGACY_FIELDS = set(LEGACY_EVENT_LISTS) | {
    "validation",
    "production_status",
    "exercised",
    "last_exercised_utc",
    "precision_among_adjudicated",
}
STORED_METRIC_FIELDS = {
    "adjudicated_precision",
    "adjudication_coverage",
    "coverage",
    "precision",
    "precision_among_adjudicated",
}
EVENT_KINDS = {"PLANT", "PRODUCTION"}
REFUSAL_VERDICTS = {"TRUE_POSITIVE", "FALSE_POSITIVE", "UNRESOLVED"}
MISS_VERDICTS = {"TRUE_MISS", "UNRESOLVED"}
RESOLVED_VERDICTS = {"TRUE_POSITIVE", "FALSE_POSITIVE", "TRUE_MISS"}
ADJUDICATOR_KINDS = {"author", "internal_agent", "external_auditor", None}
PLACEHOLDER_UTC = "2026-09-14T00:00:00Z"
ISO_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SHA_RE = re.compile(r"\b[0-9a-fA-F]{7,40}\b")
EXTERNAL_EVIDENCE_PREFIXES = ("github-actions-run:", "github-actions-job:", "external-record:")

HARVESTED_EVENTS = (
    {
        "gate_id": "verify_all.limb_index_currency",
        "event_id": "verify-all-limb-index-currency-harvest-34880195507",
        "kind": "PRODUCTION",
        "when_utc": "2026-09-14T18:32:09Z",
        "where": "CI run 34880195507 on branch evidence-indexes",
        "commit": "7d5cda77",
        "what_refused": (
            "CI refused evidence-index digest rows that hashed Windows CRLF working-tree bytes "
            "instead of the LF-normalized bytes served from committed text blobs."
        ),
        "evidence": ["commit:17a75f75", "github-actions-run:34880195507"],
        "dedupe_tokens": ("7d5cda77", "CRLF"),
    },
    {
        "gate_id": "verify_all.limb_unit_tests",
        "event_id": "verify-all-limb-unit-tests-harvest-34854763935",
        "kind": "PLANT",
        "when_utc": "2026-09-14T14:19:20Z",
        "where": "CI run 34854763935 on main for plant a74b5c42",
        "commit": "a74b5c42",
        "what_refused": "The verify workflow refused a deliberately failing unit-test plant.",
        "evidence": [
            "docs/evidence/gate-authority-2026-09-14/03-refusal-plant-failing-test-not-deployed.txt",
            "github-actions-run:34854763935",
        ],
    },
    {
        "gate_id": "ruleset.required_verify",
        "event_id": "ruleset-required-verify-harvest-34855242632",
        "kind": "PLANT",
        "when_utc": "2026-09-14T14:23:45Z",
        "where": "CI run 34855242632 on branch plant/item2 for plant bd57e490",
        "commit": "bd57e490",
        "what_refused": (
            "The main ruleset refused a branch-tested red plant SHA because the required verify "
            "status check was failing."
        ),
        "evidence": [
            "docs/evidence/gate-authority-2026-09-14/07-refusal-branch-route-red-check.txt",
            "github-actions-run:34855242632",
        ],
    },
    {
        "gate_id": "verify_all.limb_index_currency",
        "event_id": "verify-all-limb-index-currency-harvest-34856706877",
        "kind": "PLANT",
        "when_utc": "2026-09-14T14:37:49Z",
        "where": "CI run 34856706877 on branch plant/item3-index-new",
        "commit": "c022cf46",
        "what_refused": "The new verify workflow refused a hand-edited docs/index.html plant under index currency.",
        "evidence": [
            "docs/evidence/gate-authority-2026-09-14/11-postfix-ci-refuses-hand-edited-index.txt",
            "github-actions-run:34856706877",
        ],
    },
    {
        "gate_id": "verify_all.limb_heldout",
        "event_id": "verify-all-limb-heldout-harvest-34871203144",
        "kind": "PLANT",
        "when_utc": "2026-09-14T16:52:59Z",
        "where": "CI run 34871203144 on branch plant/leak-and-fixstate",
        "commit": "fe8252cd",
        "what_refused": "The held-out leak detector refused a sealed-identifier plant in a tracked test file.",
        "evidence": [
            "docs/evidence/search-states-2026-09-14/04-ci-refuses-sealed-leak-and-missing-fixstate.txt",
            "github-actions-run:34871203144",
        ],
    },
    {
        "gate_id": "verify_all.limb_fixstate",
        "event_id": "verify-all-limb-fixstate-harvest-34871203144",
        "kind": "PLANT",
        "when_utc": "2026-09-14T16:52:59Z",
        "where": "CI run 34871203144 on branch plant/leak-and-fixstate",
        "commit": "fe8252cd",
        "what_refused": "The fix-state discipline limb refused the same plant commit because it had no Fix-State trailer.",
        "evidence": [
            "docs/evidence/search-states-2026-09-14/04-ci-refuses-sealed-leak-and-missing-fixstate.txt",
            "github-actions-run:34871203144",
        ],
    },
)


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
        {
            "gate_id": "invalidation.identifier_scope",
            "where": "harness/invalidation.py:identifier_scope/assess",
            "what_it_refuses": (
                "An agent-named page identifier whose included intervention pool maps to a broader "
                "class, another declared agent, or an unresolved intervention declaration."
            ),
        },
    ]


def enumerate_gates(root) -> list[dict[str, str]]:
    """Enumerate production gates from repository code and gate configuration."""
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


def register_gates(root, incoming: dict[str, Any]) -> None:
    """Merge a lane registry by identity; refuse conflicting rows before writing."""
    root = _root_path(root)
    current = _registry_data(root)
    merged = _entries_by_id(current)
    for gid, entry in _entries_by_id(incoming).items():
        if gid in merged and merged[gid] != entry:
            raise ValueError(f"gate scorecard conflict: {gid}")
        merged[gid] = entry
    current["gates"] = [merged[gid] for gid in sorted(merged)]
    path = os.path.join(root, *REGISTRY_PATH.split("/"))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(current, indent=1, sort_keys=True) + "\n")


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


def _evidence_values(raw: Any) -> list[str]:
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, str)]
    return []


def _event_evidence_values(event: dict[str, Any]) -> list[str]:
    evidence = _evidence_values(event.get("evidence"))
    adjudication = event.get("adjudication")
    if isinstance(adjudication, dict):
        evidence.extend(_evidence_values(adjudication.get("evidence")))
    return evidence


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
    if ev.startswith(EXTERNAL_EVIDENCE_PREFIXES):
        return True
    if ev.startswith("commit:"):
        return _commit_exists(root, ev.split(":", 1)[1])
    return os.path.exists(_rel_path(root, ev))


def _timestamp_in_evidence(root: str, when_utc: str, evidence: list[str]) -> bool:
    for ev in evidence:
        if ev.startswith(EXTERNAL_EVIDENCE_PREFIXES):
            continue
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


def _expected_view(root: str) -> str:
    return json.dumps(served_view(root), indent=1, sort_keys=True) + "\n"


def _null_adjudication() -> dict[str, Any]:
    return {
        "verdict": "UNRESOLVED",
        "adjudicated_by": {"identity": None, "kind": None},
        "evidence": [],
        "architecture_identity": None,
        "when_utc": None,
    }


def _adjudicator_from_legacy(raw: dict[str, Any]) -> dict[str, Any] | None:
    adjudicated_by = raw.get("adjudicated_by") or raw.get("adjudicator")
    if not isinstance(adjudicated_by, dict):
        return None
    identity = adjudicated_by.get("identity") or adjudicated_by.get("name")
    kind = adjudicated_by.get("kind")
    if not identity or kind not in ADJUDICATOR_KINDS or kind is None:
        return None
    return {"identity": identity, "kind": kind}


def _architecture_identity(root: str) -> str | None:
    try:
        from harness import architecture_identity

        return architecture_identity.identity(root)
    except Exception:
        return None


def _infer_commit(raw: dict[str, Any], text_fields: list[str]) -> str | None:
    commit = raw.get("commit")
    if isinstance(commit, str) and commit:
        return commit
    for ev in _evidence_values(raw.get("evidence")):
        if ev.startswith("commit:"):
            return ev.split(":", 1)[1]
    joined = " ".join(x for x in text_fields if isinstance(x, str))
    match = SHA_RE.search(joined)
    return match.group(0) if match else None


def _looks_like_branch_plant(raw: dict[str, Any], text_fields: list[str]) -> bool:
    joined = " ".join(x for x in text_fields if isinstance(x, str)).lower()
    plant_needles = (
        "branch plant",
        "branch plant/",
        " on branch plant/",
        "plant/",
        "planted branch",
        "plant sha",
        "docs/index.html plant",
        "unit-test plant",
        "failing unit test",
        "held-out topic",
    )
    return any(needle in joined for needle in plant_needles)


def _legacy_event_id(gate_id: str, list_name: str, idx: int) -> str:
    stem = re.sub(r"[^a-zA-Z0-9]+", "-", gate_id).strip("-").lower()
    return f"{stem}-v1-{list_name.replace('_', '-')}-{idx + 1}"


def _legacy_event(
    root: str,
    entry: dict[str, Any],
    list_name: str,
    raw: dict[str, Any],
    idx: int,
    arch: str | None,
) -> dict[str, Any]:
    evidence = _evidence_values(raw.get("evidence"))
    when = raw.get("when_utc") if isinstance(raw.get("when_utc"), str) else None
    where = raw.get("where") if isinstance(raw.get("where"), str) and raw.get("where") else entry.get("where")
    what = raw.get("what") or raw.get("test") or raw.get("what_got_through")
    text_fields = [str(x) for x in (what, where, " ".join(evidence))]
    commit = _infer_commit(raw, text_fields)
    miss = list_name == "known_misses"
    status_gap = list_name == "unresolved"
    if list_name == "plant_validations":
        kind = "PLANT"
    elif _looks_like_branch_plant(raw, text_fields):
        kind = "PLANT"
    else:
        kind = "PRODUCTION"

    event: dict[str, Any] = {
        "event_id": _legacy_event_id(entry["gate_id"], list_name, idx),
        "kind": kind,
        "when_utc": when,
        "where": where,
        "commit": commit,
        "what_refused": None if miss else what,
        "evidence": evidence,
        "adjudication": _null_adjudication(),
        "source_list": list_name,
    }
    if miss:
        event["miss"] = True
        event["what_got_through"] = raw.get("what_got_through") or raw.get("what")
    if status_gap:
        event["status_gap"] = True

    adjudicator = _adjudicator_from_legacy(raw)
    if list_name == "true_refusals" and adjudicator:
        event["adjudication"] = {
            "verdict": "TRUE_POSITIVE",
            "adjudicated_by": {**adjudicator, "kind": "author"},
            "evidence": evidence,
            "architecture_identity": arch,
            "when_utc": when,
        }
    elif list_name == "false_refusals" and adjudicator:
        event["adjudication"] = {
            "verdict": "FALSE_POSITIVE",
            "adjudicated_by": {**adjudicator, "kind": "author"},
            "evidence": evidence,
            "architecture_identity": arch,
            "when_utc": when,
        }
    elif list_name == "known_misses" and adjudicator:
        event["adjudication"] = {
            "verdict": "TRUE_MISS",
            "adjudicated_by": {**adjudicator, "kind": "author"},
            "evidence": evidence,
            "architecture_identity": arch,
            "when_utc": when,
        }
    elif list_name == "plant_validations":
        event["adjudication"] = {
            "verdict": "TRUE_POSITIVE",
            "adjudicated_by": {"identity": "v1 plant-validation test harness", "kind": "internal_agent"},
            "evidence": evidence,
            "architecture_identity": arch,
            "when_utc": when,
        }
    return event


def _harvest_event(raw: dict[str, Any]) -> dict[str, Any]:
    event = {k: copy.deepcopy(v) for k, v in raw.items() if k not in {"gate_id", "dedupe_tokens"}}
    event["adjudication"] = _null_adjudication()
    event["source_list"] = "harvested"
    return event


def _same_refusal(existing: dict[str, Any], harvest: dict[str, Any]) -> bool:
    commit = harvest.get("commit")
    if commit and existing.get("commit") == commit:
        return True
    haystack = " ".join(
        str(x)
        for x in (
            existing.get("what_refused"),
            existing.get("where"),
            " ".join(_evidence_values(existing.get("evidence"))),
        )
        if x
    )
    tokens = harvest.get("dedupe_tokens") or ()
    return bool(tokens) and all(str(token) in haystack for token in tokens)


def _merge_harvests(entries: dict[str, dict[str, Any]]) -> dict[str, int]:
    added = 0
    enriched = 0
    for harvest in HARVESTED_EVENTS:
        gate = entries.get(harvest["gate_id"])
        if gate is None:
            continue
        events = gate.setdefault("events", [])
        if any(event.get("event_id") == harvest["event_id"] for event in events):
            continue
        match = next((event for event in events if _same_refusal(event, harvest)), None)
        if match is not None:
            match["where"] = harvest["where"]
            if not match.get("commit"):
                match["commit"] = harvest.get("commit")
            if match.get("kind") != harvest["kind"]:
                match["kind"] = harvest["kind"]
            for ev in harvest.get("evidence") or []:
                match.setdefault("evidence", [])
                if ev not in match["evidence"]:
                    match["evidence"].append(ev)
            match.setdefault("harvested_from", [])
            if harvest["event_id"] not in match["harvested_from"]:
                match["harvested_from"].append(harvest["event_id"])
            enriched += 1
        else:
            events.append(_harvest_event(harvest))
            added += 1
    return {"added": added, "enriched": enriched}


def migrate_data_v1_to_v2(root: str, data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return a v2 registry and a deterministic before/after migration report."""
    if data.get("schema_version") == SCHEMA_VERSION:
        entries = _entries_by_id(data)
        harvest = _merge_harvests(entries)
        after_events = sum(len(e.get("events") or []) for e in entries.values())
        after_unresolved = sum(
            1
            for e in entries.values()
            for event in e.get("events") or []
            if event.get("adjudication", {}).get("verdict") == "UNRESOLVED"
        )
        return data, {
            "already_v2": True,
            "before_events": after_events,
            "before_unresolved": after_unresolved,
            "after_events": after_events,
            "after_unresolved": after_unresolved,
            "harvest_added": harvest["added"],
            "harvest_enriched": harvest["enriched"],
            "lost_apparent_precision_gates": [],
        }

    old_entries = _entries_by_id(data)
    arch = _architecture_identity(root)
    new_entries: list[dict[str, Any]] = []
    before_events = 0
    before_unresolved = 0
    old_precision_gates = []

    for gate_id in sorted(old_entries):
        entry = old_entries[gate_id]
        events = []
        for list_name in LEGACY_EVENT_LISTS:
            rows = entry.get(list_name) or []
            if not isinstance(rows, list):
                rows = []
            before_events += len(rows)
            if list_name == "unresolved":
                before_unresolved += len(rows)
            for idx, raw in enumerate(rows):
                if isinstance(raw, dict):
                    events.append(_legacy_event(root, entry, list_name, raw, idx, arch))
        if isinstance(entry.get("precision_among_adjudicated"), dict) and entry["precision_among_adjudicated"].get("value") is not None:
            old_precision_gates.append(gate_id)
        new_entries.append({
            "gate_id": gate_id,
            "where": entry.get("where"),
            "what_it_refuses": entry.get("what_it_refuses"),
            "events": events,
        })

    new_data: dict[str, Any] = {
        "_doc": (
            "Measured gate scorecard schema v2. Events are source records; all precision, "
            "coverage, validation, and status fields are computed by harness.gate_scorecard."
        ),
        "schema_version": SCHEMA_VERSION,
        "auditor_correction": AUDITOR_CORRECTION,
        "unvalidated_sentence": UNVALIDATED_SENTENCE,
        "precision_coverage_sentence": PRECISION_COVERAGE_SENTENCE,
        "adjudicator_independence_sentence": INDEPENDENCE_SENTENCE,
        "gates": new_entries,
        "generated_utc": data.get("generated_utc"),
    }
    entries = _entries_by_id(new_data)
    harvest = _merge_harvests(entries)
    after_events = sum(len(e.get("events") or []) for e in entries.values())
    after_unresolved = sum(
        1
        for e in entries.values()
        for event in e.get("events") or []
        if event.get("adjudication", {}).get("verdict") == "UNRESOLVED"
    )
    lost = [gate_id for gate_id in old_precision_gates if compute(entries[gate_id])["adjudicated_precision"] is None]
    report = {
        "already_v2": False,
        "before_events": before_events,
        "before_unresolved": before_unresolved,
        "after_events": after_events,
        "after_unresolved": after_unresolved,
        "harvest_added": harvest["added"],
        "harvest_enriched": harvest["enriched"],
        "lost_apparent_precision_gates": lost,
    }
    return new_data, report


def migrate_v1_to_v2(root) -> dict[str, Any]:
    root = _root_path(root)
    data = _registry_data(root)
    new_data, report = migrate_data_v1_to_v2(root, data)
    with open(os.path.join(root, *REGISTRY_PATH.split("/")), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(new_data, indent=1, sort_keys=True) + "\n")
    return report


def _production_refusals(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        event
        for event in events
        if event.get("kind") == "PRODUCTION" and not event.get("miss") and not event.get("status_gap")
    ]


def compute(gate: dict[str, Any]) -> dict[str, Any]:
    """Compute all scorecard numbers for one gate from adjudication objects."""
    events = gate.get("events") or []
    production_refusals = _production_refusals(events)
    tp = sum(1 for e in production_refusals if e.get("adjudication", {}).get("verdict") == "TRUE_POSITIVE")
    fp = sum(1 for e in production_refusals if e.get("adjudication", {}).get("verdict") == "FALSE_POSITIVE")
    unresolved = sum(1 for e in events if e.get("adjudication", {}).get("verdict") == "UNRESOLVED")
    adjudicated = tp + fp
    production_total = len(production_refusals)
    resolved_events = [
        e for e in events if e.get("adjudication", {}).get("verdict") in RESOLVED_VERDICTS
    ]
    external = sum(
        1
        for event in resolved_events
        if event.get("adjudication", {}).get("adjudicated_by", {}).get("kind") == "external_auditor"
    )
    plant_validations = sum(
        1
        for event in events
        if event.get("kind") == "PLANT" and event.get("adjudication", {}).get("verdict") == "TRUE_POSITIVE"
    )
    true_misses = sum(1 for event in events if event.get("adjudication", {}).get("verdict") == "TRUE_MISS")
    precision = None if adjudicated == 0 else tp / adjudicated
    coverage = None if production_total == 0 else adjudicated / production_total
    independence = None if not resolved_events else external / len(resolved_events)
    return {
        "adjudicated_precision": precision,
        "adjudication_coverage": coverage,
        "true_positive_production_refusals": tp,
        "false_positive_production_refusals": fp,
        "adjudicated_production_refusals": adjudicated,
        "production_refusals": production_total,
        "plant_validations": plant_validations,
        "plant_events": sum(1 for event in events if event.get("kind") == "PLANT"),
        "unresolved": unresolved,
        "true_misses": true_misses,
        "miss_events": sum(1 for event in events if event.get("miss")),
        "status_gap_events": sum(1 for event in events if event.get("status_gap")),
        "adjudicator_independence": independence,
        "adjudications": len(resolved_events),
        "external_auditor_adjudications": external,
        "production_status": "EXERCISED" if production_total else "UNVALIDATED",
        "validation": "PRODUCTION_ADJUDICATED" if adjudicated else "UNVALIDATED",
        "unvalidated": tp == 0,
    }


def _fmt_value(value: float | None, none_text: str) -> str:
    if value is None:
        return none_text
    return f"{value:.3f}"


def format_computed_metrics(metrics: dict[str, Any]) -> str:
    """Render the required precision+coverage pair, refusing split precision."""
    if "adjudicated_precision" in metrics and "adjudication_coverage" not in metrics:
        raise ValueError("precision is reported only beside its adjudication coverage")
    precision = metrics.get("adjudicated_precision")
    coverage = metrics.get("adjudication_coverage")
    precision_text = _fmt_value(precision, "no adjudicated production refusal - UNVALIDATED, not green")
    coverage_text = _fmt_value(coverage, "no production refusals")
    return (
        "adjudicated precision TP/(TP+FP) = "
        f"{precision_text} ({metrics.get('adjudicated_production_refusals')} adjudicated of "
        f"{metrics.get('production_refusals')} production refusals = coverage {coverage_text}); "
        f"plants: {metrics.get('plant_validations')}; UNRESOLVED: {metrics.get('unresolved')}"
    )


def render_gate_line(gate: dict[str, Any]) -> str:
    return format_computed_metrics(compute(gate))


def _validate_event(root: str, gate_id: str, event: Any, idx: int, seen_events: set[str]) -> list[str]:
    reasons: list[str] = []
    if not isinstance(event, dict):
        return [f"{gate_id}: events[{idx}] must be an object"]
    event_id = event.get("event_id")
    if not isinstance(event_id, str) or not event_id:
        reasons.append(f"{gate_id}: events[{idx}] needs event_id")
    elif event_id in seen_events:
        reasons.append(f"{gate_id}: duplicate event_id {event_id}")
    else:
        seen_events.add(event_id)

    kind = event.get("kind")
    if kind not in EVENT_KINDS:
        reasons.append(f"{gate_id}: {event_id}: kind must be PLANT or PRODUCTION")
    if event.get("counts_as_production") and kind == "PLANT":
        reasons.append(f"{gate_id}: {event_id}: a PLANT event must not be counted as PRODUCTION")

    for field in ("when_utc", "where", "commit", "what_refused", "evidence", "adjudication"):
        if field not in event:
            reasons.append(f"{gate_id}: {event_id}: missing {field}")
    if not event.get("miss") and not isinstance(event.get("what_refused"), str):
        reasons.append(f"{gate_id}: {event_id}: what_refused must be a string unless miss=true")
    if not isinstance(event.get("where"), str) or not event.get("where"):
        reasons.append(f"{gate_id}: {event_id}: where must be a non-empty string")
    if event.get("commit") is not None and not isinstance(event.get("commit"), str):
        reasons.append(f"{gate_id}: {event_id}: commit must be a string or null")

    when = event.get("when_utc")
    if when is not None:
        if not isinstance(when, str):
            reasons.append(f"{gate_id}: {event_id}: when_utc must be an ISO UTC string or null")
        elif when == PLACEHOLDER_UTC:
            reasons.append(f"{gate_id}: {event_id}: uses placeholder timestamp {PLACEHOLDER_UTC}")
        elif not ISO_UTC_RE.fullmatch(when):
            reasons.append(f"{gate_id}: {event_id}: timestamp must be ISO UTC seconds")
        else:
            evidence = _event_evidence_values(event)
            if (
                evidence
                and not event.get("miss")
                and not event.get("status_gap")
                and not _timestamp_in_evidence(root, when, evidence)
            ):
                reasons.append(f"{gate_id}: {event_id}: timestamp {when} not found in cited evidence")
    if kind == "PRODUCTION" and not event.get("miss") and not event.get("status_gap") and when is None:
        reasons.append(f"{gate_id}: {event_id}: production refusal events need dated when_utc")

    evidence = event.get("evidence")
    if not isinstance(evidence, list):
        reasons.append(f"{gate_id}: {event_id}: evidence must be a list")
    else:
        for ev in _evidence_values(evidence):
            if not _evidence_exists(root, ev):
                reasons.append(f"{gate_id}: {event_id}: cited evidence does not exist: {ev}")

    adj = event.get("adjudication")
    if not isinstance(adj, dict):
        reasons.append(f"{gate_id}: {event_id}: every event needs an adjudication object")
        return reasons
    for field in ("verdict", "adjudicated_by", "evidence", "architecture_identity", "when_utc"):
        if field not in adj:
            reasons.append(f"{gate_id}: {event_id}: adjudication missing {field}")
    verdict = adj.get("verdict")
    allowed = MISS_VERDICTS if event.get("miss") else REFUSAL_VERDICTS
    if verdict not in allowed:
        reasons.append(f"{gate_id}: {event_id}: verdict must be one of {sorted(allowed)}")
    if verdict == "UNRESOLVED" and str(event.get("counts_as", "")).upper() in {"TP", "FP", "TRUE_POSITIVE", "FALSE_POSITIVE"}:
        reasons.append(f"{gate_id}: {event_id}: UNRESOLVED events must not be counted into TP or FP")

    by = adj.get("adjudicated_by")
    if not isinstance(by, dict):
        reasons.append(f"{gate_id}: {event_id}: adjudicated_by must be an object")
    else:
        by_kind = by.get("kind")
        by_identity = by.get("identity")
        if by_kind not in ADJUDICATOR_KINDS:
            reasons.append(f"{gate_id}: {event_id}: adjudicated_by.kind is invalid")
        if verdict in RESOLVED_VERDICTS:
            if by_kind is None:
                reasons.append(f"{gate_id}: {event_id}: {verdict} requires adjudicated_by.kind")
            if not isinstance(by_identity, str) or not by_identity:
                reasons.append(f"{gate_id}: {event_id}: {verdict} requires adjudicated_by.identity")
        if verdict == "UNRESOLVED" and by_kind is not None:
            reasons.append(f"{gate_id}: {event_id}: UNRESOLVED adjudication must keep adjudicated_by.kind null")

    adj_evidence = adj.get("evidence")
    if not isinstance(adj_evidence, list):
        reasons.append(f"{gate_id}: {event_id}: adjudication.evidence must be a list")
    else:
        if verdict in RESOLVED_VERDICTS and not _evidence_values(adj_evidence):
            reasons.append(f"{gate_id}: {event_id}: {verdict} requires adjudication evidence")
        for ev in _evidence_values(adj_evidence):
            if not _evidence_exists(root, ev):
                reasons.append(f"{gate_id}: {event_id}: cited adjudication evidence does not exist: {ev}")

    adj_when = adj.get("when_utc")
    if adj_when is not None:
        if not isinstance(adj_when, str) or not ISO_UTC_RE.fullmatch(adj_when):
            reasons.append(f"{gate_id}: {event_id}: adjudication.when_utc must be ISO UTC seconds or null")
    arch = adj.get("architecture_identity")
    if arch is not None and (not isinstance(arch, str) or not arch):
        reasons.append(f"{gate_id}: {event_id}: architecture_identity must be a string or null")
    return reasons


def _registry_has_stored_metrics(value: Any, path: str = "registry") -> list[str]:
    reasons: list[str] = []
    if isinstance(value, dict):
        for key, sub in value.items():
            here = f"{path}.{key}"
            if key in STORED_METRIC_FIELDS:
                reasons.append(f"{here}: stored precision/coverage numbers are refused; compute them")
            reasons.extend(_registry_has_stored_metrics(sub, here))
    elif isinstance(value, list):
        for idx, sub in enumerate(value):
            reasons.extend(_registry_has_stored_metrics(sub, f"{path}[{idx}]"))
    return reasons


def check(root) -> tuple[bool, list[str]]:
    """Check v2 event schema, evidence paths, computed metrics, and served-view currency."""
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

    if data.get("schema_version") != SCHEMA_VERSION:
        reasons.append(f"{REGISTRY_PATH} must declare schema_version {SCHEMA_VERSION}; run python -m harness.gate_scorecard --migrate-v1-to-v2")
    reasons.extend(_registry_has_stored_metrics(data))

    for gate_id in sorted(set(enumerated) - set(entries)):
        reasons.append(f"{REGISTRY_PATH} missing entry for enumerated gate {gate_id}")
    for gate_id in sorted(set(entries) - set(enumerated)):
        reasons.append(f"{REGISTRY_PATH} has entry for non-enumerated gate {gate_id}")

    seen_events: set[str] = set()
    for gate_id, entry in sorted(entries.items()):
        for field in ("where", "what_it_refuses", "events"):
            if field not in entry:
                reasons.append(f"{gate_id}: missing {field}")
        for field in sorted(LEGACY_FIELDS & set(entry)):
            reasons.append(f"{gate_id}: legacy field {field} is refused in schema v2")
        events = entry.get("events")
        if not isinstance(events, list):
            reasons.append(f"{gate_id}: events must be a list")
            continue
        for idx, event in enumerate(events):
            reasons.extend(_validate_event(root, gate_id, event, idx, seen_events))
        try:
            format_computed_metrics(compute(entry))
        except ValueError as exc:
            reasons.append(f"{gate_id}: {exc}")

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


def _enriched_gate(entry: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(entry)
    metrics = compute(entry)
    out["computed"] = metrics
    out["scorecard_line"] = format_computed_metrics(metrics)
    return out


def summary(root) -> dict[str, Any]:
    """Return the compact scorecard summary rendered on the site index."""
    root = _root_path(root)
    data = _registry_data(root)
    entries = _entries_by_id(data)
    computed = {gid: compute(entry) for gid, entry in entries.items()}
    unvalidated = sorted(g for g, metrics in computed.items() if metrics["unvalidated"])
    plant_only = sorted(
        g
        for g, entry in entries.items()
        if any(event.get("kind") == "PLANT" for event in entry.get("events") or [])
        and computed[g]["production_refusals"] == 0
    )
    true_gates = sorted(g for g, metrics in computed.items() if metrics["true_positive_production_refusals"])
    false_gates = sorted(g for g, metrics in computed.items() if metrics["false_positive_production_refusals"])
    production_refusal_gates = sorted(g for g, metrics in computed.items() if metrics["production_refusals"])
    total_adjudications = sum(metrics["adjudications"] for metrics in computed.values())
    external = sum(metrics["external_auditor_adjudications"] for metrics in computed.values())
    independence = None if total_adjudications == 0 else external / total_adjudications
    gate_lines = [
        {
            "gate_id": gid,
            "line": format_computed_metrics(computed[gid]),
            "computed": computed[gid],
        }
        for gid in sorted(entries)
    ]
    # Overall adjudication coverage, rendered FIRST on every surface (auditor, 2026-09-15): the dashboard must
    # not hide the unresolved. Coverage over all events, over PRODUCTION refusal events, and the independent
    # (external-auditor) share -- a precision shown without these reads as if the unresolved had disappeared.
    all_events = [e for entry in entries.values() for e in (entry.get("events") or []) if isinstance(e, dict)]
    def _adjudicated(e):
        return ((e.get("adjudication") or {}).get("verdict") or "UNRESOLVED") != "UNRESOLVED"
    def _external(e):
        return ((e.get("adjudication") or {}).get("adjudicated_by") or {}).get("kind") == "external_auditor"
    production_events = [e for e in all_events if e.get("kind") == "PRODUCTION" and not e.get("status_gap")]
    overall = {
        "events": len(all_events),
        "adjudicated": sum(1 for e in all_events if _adjudicated(e)),
        "independently_adjudicated": sum(1 for e in all_events if _adjudicated(e) and _external(e)),
        "production_events": len(production_events),
        "production_adjudicated": sum(1 for e in production_events if _adjudicated(e)),
        "production_independently_adjudicated": sum(1 for e in production_events if _adjudicated(e) and _external(e)),
    }
    overall["adjudication_coverage"] = None if not all_events else overall["adjudicated"] / len(all_events)
    overall["independent_adjudication_coverage"] = None if not all_events else overall["independently_adjudicated"] / len(all_events)
    overall["production_adjudication_coverage"] = None if not production_events else overall["production_adjudicated"] / len(production_events)
    overall["production_independent_adjudication_coverage"] = None if not production_events else overall["production_independently_adjudicated"] / len(production_events)
    return {
        "overall_adjudication": overall,
        "gate_count": len(entries),
        "plant_only_count": len(plant_only),
        "plant_only": plant_only,
        "unvalidated_count": len(unvalidated),
        "unvalidated": unvalidated,
        "production_refusal_gate_count": len(production_refusal_gates),
        "production_refusal_gates": production_refusal_gates,
        "production_true_refusal_gate_count": len(true_gates),
        "production_true_refusal_gates": true_gates,
        "false_refusal_gate_count": len(false_gates),
        "false_refusal_gates": false_gates,
        "event_count": sum(len(entry.get("events") or []) for entry in entries.values()),
        "unresolved_event_count": sum(metrics["unresolved"] for metrics in computed.values()),
        "plant_validation_count": sum(metrics["plant_validations"] for metrics in computed.values()),
        "adjudicator_independence": independence,
        "adjudications": total_adjudications,
        "external_auditor_adjudications": external,
        "auditor_sentence": AUDITOR_CORRECTION,
        "unvalidated_sentence": UNVALIDATED_SENTENCE,
        "precision_coverage_sentence": PRECISION_COVERAGE_SENTENCE,
        "adjudicator_independence_sentence": INDEPENDENCE_SENTENCE,
        "gate_lines": gate_lines,
    }


def served_view(root) -> dict[str, Any]:
    """Generated JSON view served from docs/gate_scorecard.json."""
    root = _root_path(root)
    data = _registry_data(root)
    entries = _entries_by_id(data)
    return {
        "_doc": "Generated from registry/gate_scorecard.json; do not hand-edit.",
        "source": REGISTRY_PATH,
        "schema_version": SCHEMA_VERSION,
        "auditor_correction": AUDITOR_CORRECTION,
        "auditor_sentence": AUDITOR_CORRECTION,
        "unvalidated_sentence": UNVALIDATED_SENTENCE,
        "precision_coverage_sentence": PRECISION_COVERAGE_SENTENCE,
        "adjudicator_independence_sentence": INDEPENDENCE_SENTENCE,
        "summary": summary(root),
        "gates": [_enriched_gate(entries[k]) for k in sorted(entries)],
    }


def write_served_view(root) -> str:
    root = _root_path(root)
    out = os.path.join(root, *SERVED_PATH.split("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(_expected_view(root))
    return out


def _print_migration_report(report: dict[str, Any]) -> None:
    state = "already schema v2" if report.get("already_v2") else "migrated v1 to schema v2"
    print(f"gate scorecard: {state}")
    print(
        "events: "
        f"{report['before_events']} before -> {report['after_events']} after; "
        f"UNRESOLVED: {report['before_unresolved']} before -> {report['after_unresolved']} after; "
        f"harvest added={report['harvest_added']} enriched={report['harvest_enriched']}"
    )
    lost = report.get("lost_apparent_precision_gates") or []
    if lost:
        print("gates losing apparent precision because no adjudicator was recorded:")
        for gate_id in lost:
            print(f"  - {gate_id}")
    else:
        print("gates losing apparent precision because no adjudicator was recorded: none")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check or migrate the gate scorecard.")
    parser.add_argument("--migrate-v1-to-v2", action="store_true", help="Mechanically migrate registry/gate_scorecard.json.")
    parser.add_argument("--merge-registry", help="Merge lane gates by gate_id; refuse conflicting rows.")
    args = parser.parse_args(argv)

    root = _root_path(os.getcwd())
    if args.merge_registry:
        with open(args.merge_registry, encoding="utf-8") as f:
            register_gates(root, json.load(f))
        return 0
    if args.migrate_v1_to_v2:
        _print_migration_report(migrate_v1_to_v2(root))
        return 0

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
            f"({s['gate_count']} gates; {s['event_count']} events; "
            f"{s['unresolved_event_count']} UNRESOLVED; "
            f"{s['production_true_refusal_gate_count']} with adjudicated production true refusals; "
            f"adjudicator_independence={_fmt_value(s['adjudicator_independence'], 'no adjudications')})"
        )
        return 0
    print("gate scorecard: REFUSED")
    for reason in reasons:
        print(f"  - {reason}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
