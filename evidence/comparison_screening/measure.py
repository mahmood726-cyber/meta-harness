"""Offline, read-only git comparison against the requested candidate."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from harness import screen, arm_parse

BASE = "c15ed111"
SERVED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"


def baseline():
    raw = subprocess.check_output(["git", "show", f"{BASE}:harness/screen.py"], cwd=ROOT)
    module = types.ModuleType("harness._comparison_baseline")
    module.__package__ = "harness"
    exec(compile(raw, f"{BASE}:harness/screen.py", "exec"), module.__dict__)
    return module, hashlib.sha256(raw).hexdigest()


def served_matches(row, record_id):
    """Served IDs can have human labels; match the complete typed identifier."""
    key = str(record_id)
    return (str(row.get("trial_family_id")) == key or str(row.get("id")) == key
            or bool(re.search(r"(?<![A-Za-z0-9])" + re.escape(key) + r"(?![A-Za-z0-9])", str(row.get("id", "")))))


def measure():
    old, base_sha = baseline()
    totals = {"records": 0, "ctgov": 0}
    topics, changes, unresolved, missing = [], [], [], []
    for path in sorted((ROOT / "topics").glob("*.json")):
        config = json.loads(path.read_text(encoding="utf-8"))
        slug = config.get("slug", path.stem)
        cache = ROOT / "cache" / slug / "records.json"
        if not cache.exists():
            missing.append(slug)
            topics.append({"topic": slug, "records": 0, "ctgov": 0, "cache": "MISSING"})
            continue
        data = json.loads(cache.read_text(encoding="utf-8"))
        counts = {kind: len(data.get(kind, [])) for kind in totals}
        topics.append({"topic": slug, **counts, "cache_sha256": hashlib.sha256(cache.read_bytes()).hexdigest(),
                       "config_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        inc = config.get("include", {})
        neg = config.get("negative_control_pmids", [])
        topic_changes = []
        for kind in totals:
            totals[kind] += counts[kind]
            for index, rec in enumerate(data.get(kind, [])):
                before = screen.ScreenDecision(*old.screen_record(rec, inc, neg))
                after = screen.screen_record(rec, inc, neg)
                identity = {"topic": slug, "kind": kind, "index": index, "id": rec["id"],
                            "title": rec.get("title", "")}
                if (before.decision, before.rule_id) != (after[0], after[1]) or getattr(after, "comparison", None):
                    topic_changes.append({**identity, "old_decision": before.decision, "old_rule": before.rule_id,
                                          "old_reason": before.reason, "new_decision": after[0],
                                          "new_rule": after[1], "comparison": getattr(after, "comparison", None),
                                          "second_screener": screen.screen_record_2(rec, inc)})
                haystack = screen._text(rec) if inc.get("prevention") else screen._poptext(rec)
                term = screen.screen_entry.population_exclusion(haystack, inc, screen._has, screen._all_occurrences_qualified)
                if term and not arm_parse.allocation_arms(rec) and after[0] == "exclude":
                    unresolved.append({**identity, "population_term": term,
                                       "reason": "randomized arms unreadable; no arm exemption applied", "rule": after[1]})
        if topic_changes:
            result = subprocess.run(["git", "show", f"{SERVED}:docs/reviews/{slug}/review.json"], cwd=ROOT,
                                    capture_output=True)
            if result.returncode:
                # Prove absence, rather than treating an arbitrary git failure as not served.
                listing = subprocess.check_output(["git", "ls-tree", "--name-only", SERVED,
                                                   f"docs/reviews/{slug}/review.json"], cwd=ROOT)
                if listing.strip():
                    raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
                rows = []
            else:
                rows = json.loads(result.stdout)["screening"]["records"]
            for change in topic_changes:
                served = [r for r in rows if served_matches(r, change["id"])]
                change["served"] = bool(served)
                change["served_decisions"] = [{k: r.get(k) for k in ("id", "decision", "rule_id")} for r in served]
                change["notice"] = "SERVED-CHANGE NOTICE" if served else "NOT_SERVED"
            changes.extend(topic_changes)
    return {"baseline": BASE, "baseline_screen_sha256": base_sha, "served_revision": SERVED,
            "current_screen_sha256": hashlib.sha256((ROOT / "harness/screen.py").read_bytes()).hexdigest(),
            "current_arm_parse_sha256": hashlib.sha256((ROOT / "harness/arm_parse.py").read_bytes()).hexdigest(),
            "unit": "topic/cache array entry; no deduplication", "change_definition": "decision/rule_id changes or newly attached comparison metadata",
            "denominators_by_kind": totals, "N": sum(totals.values()), "n": len(changes),
            "topics": topics, "missing_caches": missing, "changes": changes, "unreadable_arms_excluded": unresolved}


if __name__ == "__main__":
    result = measure()
    (Path(__file__).parent / "measurement.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("n", "N", "denominators_by_kind", "missing_caches")}, indent=2))
    for change in result["changes"]:
        print(change["notice"], change["topic"], change["id"], change["old_rule"], "->", change["new_decision"])
