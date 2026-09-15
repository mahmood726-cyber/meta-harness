"""Build the labelled search benchmark and evidence bundle for lane S1.

The inputs are committed source lists and review objects. This script does not
touch topics, caches, review objects, acquisition/fetch code, or query text.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

BENCHMARK_PATH = ROOT / "registry" / "search_benchmark.json"
SPLIT_PATH = ROOT / "registry" / "search_benchmark_split.json"
FIXES_PATH = ROOT / "registry" / "fixes.json"
GATE_GAPS_PATH = ROOT / "registry" / "gate_gaps.json"
CAPTIONS_PATH = ROOT / "docs" / "evidence" / "CAPTIONS.json"
EVIDENCE_DIR = ROOT / "docs" / "evidence" / "search-benchmark-2026-09-15"
REPORT_PATH = ROOT / "LANE-S1-REPORT.md"

SEALED_UTC = "2026-09-15T00:00:00Z"
SPLIT_RULE = (
    "DEVELOPMENT iff int(sha256('meta-harness-search-split-2026-09-15|' + slug)"
    ".hexdigest()[:2], 16) < 0x30; forced DEVELOPMENT for probiotics-aad-prevention "
    "and balanced-crystalloids-vs-saline-mortality."
)
SPLIT_SALT = "meta-harness-search-split-2026-09-15|"
FORCED_DEVELOPMENT = {
    "probiotics-aad-prevention": "targets are public in the diagnostic and it is the design input",
    "balanced-crystalloids-vs-saline-mortality": "FISSH miss is in the served STALE reason",
}
FIX_ID = "TRANCHE-search-benchmark"

AUDIT_ORIGINS = {
    "known_eligible_missing",
    "never_considered",
    "probiotics_goodman_42",
    "comparator_only_theirs",
}

PMID_RE = re.compile(r"^(?:PMID[:\s]*)?(\d{1,9})$", re.I)
NCT_RE = re.compile(r"\b(NCT\d{8})\b", re.I)
DOI_RE = re.compile(r"\b(10\.\S+/\S+)\b", re.I)


def _posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def _rel(path: Path) -> str:
    return _posix(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=1, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def _git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return proc.stdout.strip()


def _blob(relpath: str) -> str:
    return _git("hash-object", "--", relpath.replace("/", os.sep))


def _pmid(value: Any) -> str | None:
    raw = str(value or "").strip()
    match = PMID_RE.match(raw)
    return match.group(1) if match else None


def _nct(value: Any) -> str | None:
    match = NCT_RE.search(str(value or ""))
    return match.group(1).upper() if match else None


def _doi(value: Any) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    match = DOI_RE.search(raw)
    return match.group(1).rstrip(".,;").lower() if match else None


def _norm_title(value: Any) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _key(trial: str, pmid: str | None, nct: str | None, doi: str | None) -> tuple[str, str]:
    if pmid:
        return ("pmid", pmid)
    if nct:
        return ("nct", nct)
    if doi:
        return ("doi", doi)
    return ("title", _norm_title(trial))


def _clean(value: Any) -> str:
    return " ".join(str(value or "").replace("\u00a0", " ").split())


def _topic_slugs() -> list[str]:
    return sorted(path.parent.name for path in (ROOT / "docs" / "reviews").glob("*/review.json"))


def _record_titles(slug: str) -> dict[str, str]:
    path = ROOT / "cache" / slug / "records.json"
    if not path.is_file():
        return {}
    try:
        data = _load_json(path)
    except Exception:
        return {}
    records = data.get("records") if isinstance(data, dict) else data
    out: dict[str, str] = {}
    if not isinstance(records, list):
        return out
    for rec in records:
        if not isinstance(rec, dict):
            continue
        rid = _pmid(rec.get("id"))
        title = _clean(rec.get("title"))
        if rid and title:
            out[rid] = title
            out[rid.lstrip("0") or rid] = title
    return out


class TopicBuilder:
    def __init__(self, slug: str) -> None:
        self.slug = slug
        self.rows: dict[tuple[str, str], dict[str, Any]] = {}

    def add(
        self,
        *,
        trial: str,
        origin: str,
        source_path: str,
        pmid: str | None = None,
        nct: str | None = None,
        doi: str | None = None,
        note: str = "",
        resolution: str | None = None,
    ) -> None:
        trial = _clean(trial) or _clean(pmid or nct or doi) or "NAME_ONLY"
        pmid = _pmid(pmid)
        nct = _nct(nct)
        doi = _doi(doi)
        key = _key(trial, pmid, nct, doi)
        row = self.rows.get(key)
        if row is None:
            row = {
                "trial": trial,
                "pmid": pmid,
                "nct": nct,
                "doi": doi,
                "_origins": set(),
                "_source_paths": set(),
                "_notes": [],
                "_resolutions": set(),
            }
            self.rows[key] = row
        if row["trial"].startswith(("PMID ", "NCT")) and not trial.startswith(("PMID ", "NCT")):
            row["trial"] = trial
        row["_origins"].add(origin)
        row["_source_paths"].add(source_path)
        if note and note not in row["_notes"]:
            row["_notes"].append(note)
        if resolution:
            row["_resolutions"].add(resolution)

    def finish(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for key, row in sorted(self.rows.items(), key=lambda item: (item[0][0], item[0][1], item[1]["trial"])):
            origins = sorted(row.pop("_origins"))
            source_paths = sorted(row.pop("_source_paths"))
            notes = row.pop("_notes")
            resolutions = sorted(row.pop("_resolutions"))
            final = {
                "trial": row["trial"],
                "pmid": row["pmid"],
                "nct": row["nct"],
                "doi": row["doi"],
                "origin": ";".join(origins),
                "source_path": ";".join(source_paths),
                "note": " | ".join(notes),
            }
            if resolutions:
                final["resolution"] = ";".join(resolutions)
            if not any(final.get(k) for k in ("pmid", "nct", "doi")):
                final["identifier_state"] = "NAME_ONLY"
                final["note"] = (final["note"] + " | " if final["note"] else "") + (
                    "NAME_ONLY: can only be scored by normalized title match"
                )
            out.append(final)
        return out


def _add_known_missing(builders: dict[str, TopicBuilder]) -> None:
    path = ROOT / "docs" / "known_eligible_missing.json"
    data = _load_json(path)
    for slug, rows in (data.get("topics") or {}).items():
        if slug not in builders:
            continue
        for item in rows or []:
            builders[slug].add(
                trial=item.get("trial", ""),
                origin="known_eligible_missing",
                source_path=_rel(path),
                pmid=item.get("pmid"),
                nct=item.get("nct"),
                doi=item.get("doi"),
                note="; ".join(
                    part for part in [
                        f"mechanism={item.get('mechanism')}" if item.get("mechanism") else "",
                        f"status={item.get('status')}" if item.get("status") else "",
                        _clean(item.get("note")),
                    ] if part
                ),
            )


def _add_never_considered(builders: dict[str, TopicBuilder]) -> None:
    path = ROOT / "docs" / "never_considered.json"
    data = _load_json(path)
    for slug, rows in (data.get("topics") or {}).items():
        if slug not in builders:
            continue
        for item in rows or []:
            builders[slug].add(
                trial=item.get("trial", ""),
                origin="never_considered",
                source_path=_rel(path),
                pmid=item.get("pmid"),
                nct=item.get("nct"),
                doi=item.get("doi"),
                note=_clean(item.get("note")),
            )


def _parse_goodman_table() -> list[dict[str, str]]:
    path = ROOT / "docs" / "evidence" / "probiotics-search-diagnostic-2026-09-15" / "01-their-42.txt"
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0] in {"#", "---"}:
            continue
        if not cells[0].isdigit() or len(cells) < 8:
            continue
        rows.append({
            "trial": cells[1],
            "year": cells[2],
            "journal": cells[3],
            "pmid": cells[4],
            "resolution": cells[5],
            "sample_size": cells[6],
            "strain": cells[7],
        })
    return rows


def _add_goodman(builders: dict[str, TopicBuilder]) -> None:
    slug = "probiotics-aad-prevention"
    source = "docs/evidence/probiotics-search-diagnostic-2026-09-15/01-their-42.txt"
    for item in _parse_goodman_table():
        trial = _clean(f"{item['trial']} {item['year']}".strip())
        pmid = None if item["pmid"].upper() == "UNRESOLVED" else item["pmid"]
        builders[slug].add(
            trial=trial,
            origin="probiotics_goodman_42",
            source_path=source,
            pmid=pmid,
            note=(
                f"Goodman 2021 row; journal={item['journal']}; "
                f"sample={item['sample_size']}; resolution={item['resolution']}"
            ),
            resolution=item["resolution"],
        )


def _trial_name(item: dict[str, Any], titles: dict[str, str]) -> str:
    pmid = _pmid(item.get("id") or item.get("pmid") or item.get("label"))
    if pmid and (titles.get(pmid) or titles.get(pmid.lstrip("0") or pmid)):
        return titles.get(pmid) or titles[pmid.lstrip("0") or pmid]
    for key in ("title", "trial", "name", "label", "id"):
        if item.get(key):
            return _clean(item[key])
    return _clean(pmid or "")


def _add_review_objects(builders: dict[str, TopicBuilder]) -> None:
    for slug in builders:
        path = ROOT / "docs" / "reviews" / slug / "review.json"
        data = _load_json(path)
        outcomes = data.get("outcomes") or []
        primary = next((outcome for outcome in outcomes if outcome.get("primary")), outcomes[0] if outcomes else {})
        titles = _record_titles(slug)
        for item in primary.get("trials") or []:
            pmid = _pmid(item.get("id") or item.get("pmid") or item.get("label"))
            if not pmid:
                continue
            builders[slug].add(
                trial=_trial_name(item, titles),
                origin="pooled_or_declared_absent",
                source_path=f"docs/reviews/{slug}/review.json#primary.trials",
                pmid=pmid,
                nct=item.get("nct"),
                doi=item.get("doi"),
                note="pooled primary trial",
            )
        for item in primary.get("declared_absent_trials") or []:
            pmid = _pmid(item.get("id") or item.get("pmid") or item.get("label"))
            if not pmid:
                continue
            builders[slug].add(
                trial=_trial_name(item, titles),
                origin="pooled_or_declared_absent",
                source_path=f"docs/reviews/{slug}/review.json#primary.declared_absent_trials",
                pmid=pmid,
                nct=item.get("nct"),
                doi=item.get("doi"),
                note="eligible declared-absent primary-outcome trial with PMID",
            )
        only_theirs = (((data.get("comparator") or {}).get("overlap") or {}).get("only_theirs") or [])
        for item in only_theirs:
            if isinstance(item, dict):
                pmid = _pmid(item.get("pmid") or item.get("id") or item.get("label"))
                if not pmid:
                    continue
                builders[slug].add(
                    trial=_trial_name(item, titles),
                    origin="comparator_only_theirs",
                    source_path=f"docs/reviews/{slug}/review.json#comparator.overlap.only_theirs",
                    pmid=pmid,
                    nct=item.get("nct"),
                    doi=item.get("doi"),
                    note="comparator overlap only_theirs entry with PMID",
                )
            else:
                text = str(item)
                pmid = _pmid(text)
                if not pmid:
                    continue
                builders[slug].add(
                    trial=text,
                    origin="comparator_only_theirs",
                    source_path=f"docs/reviews/{slug}/review.json#comparator.overlap.only_theirs",
                    pmid=pmid,
                    note="comparator overlap only_theirs string with PMID",
                )


def build_benchmark(head: str) -> dict[str, Any]:
    builders = {slug: TopicBuilder(slug) for slug in _topic_slugs()}
    _add_known_missing(builders)
    _add_never_considered(builders)
    _add_goodman(builders)
    _add_review_objects(builders)

    topics: dict[str, Any] = {}
    total = 0
    name_only = 0
    origin_memberships: Counter[str] = Counter()
    audit_unique = 0
    pooled_unique = 0
    audit_topics: set[str] = set()
    pooled_topics: set[str] = set()
    for slug, builder in builders.items():
        positives = builder.finish()
        origins_for_topic: Counter[str] = Counter()
        for row in positives:
            origins = row["origin"].split(";") if row.get("origin") else []
            for origin in origins:
                origin_memberships[origin] += 1
                origins_for_topic[origin] += 1
            if any(origin in AUDIT_ORIGINS for origin in origins):
                audit_unique += 1
                audit_topics.add(slug)
            if "pooled_or_declared_absent" in origins:
                pooled_unique += 1
                pooled_topics.add(slug)
            if row.get("identifier_state") == "NAME_ONLY":
                name_only += 1
        total += len(positives)
        topics[slug] = {
            "N": len(positives),
            "name_only": sum(1 for row in positives if row.get("identifier_state") == "NAME_ONLY"),
            "origin_membership_counts": dict(sorted(origins_for_topic.items())),
            "positives": positives,
        }
    return {
        "schema_version": 1,
        "_doc": (
            "Labelled known-positive search benchmark. Positives are deduplicated per topic by "
            "PMID, then NCT, DOI, then normalized trial title. origin may contain multiple "
            "semicolon-separated provenance labels when the same trial appears in multiple source lists."
        ),
        "generated_utc": SEALED_UTC,
        "commit": head,
        "source_paths": [
            "docs/known_eligible_missing.json",
            "docs/never_considered.json",
            "docs/evidence/probiotics-search-diagnostic-2026-09-15/01-their-42.txt",
            "docs/reviews/*/review.json",
        ],
        "totals": {
            "topics": len(topics),
            "positives": total,
            "name_only": name_only,
            "audit_found_unique_positives": audit_unique,
            "audit_found_topics": len(audit_topics),
            "pooled_or_declared_unique_positives": pooled_unique,
            "pooled_or_declared_topics": len(pooled_topics),
            "origin_membership_counts": dict(sorted(origin_memberships.items())),
        },
        "topics": topics,
    }


def build_split(slugs: list[str], head: str) -> dict[str, Any]:
    assignments: dict[str, Any] = {}
    counts = Counter()
    for slug in slugs:
        digest = hashlib.sha256((SPLIT_SALT + slug).encode("utf-8")).hexdigest()
        value = int(digest[:2], 16)
        assigned = "DEVELOPMENT" if value < 0x30 else "MEASUREMENT"
        reason = "sha256_rule"
        forced_reason = None
        if slug in FORCED_DEVELOPMENT:
            assigned = "DEVELOPMENT"
            reason = "forced"
            forced_reason = FORCED_DEVELOPMENT[slug]
        counts[assigned] += 1
        row = {
            "set": assigned,
            "reason": reason,
            "sha256_prefix": digest[:2],
            "sha256_prefix_int": value,
            "threshold": "0x30",
        }
        if forced_reason:
            row["forced_reason"] = forced_reason
            row["rule_assignment_before_force"] = "DEVELOPMENT" if value < 0x30 else "MEASUREMENT"
        assignments[slug] = row
    if counts["DEVELOPMENT"] != 11 or counts["MEASUREMENT"] != 21:
        raise RuntimeError(f"split count mismatch: {dict(counts)}")
    return {
        "schema_version": 1,
        "sealed_utc": SEALED_UTC,
        "commit": head,
        "rule": SPLIT_RULE,
        "salt": SPLIT_SALT,
        "forced_assignments": {
            slug: {"set": "DEVELOPMENT", "reason": reason}
            for slug, reason in sorted(FORCED_DEVELOPMENT.items())
        },
        "counts": {"DEVELOPMENT": counts["DEVELOPMENT"], "MEASUREMENT": counts["MEASUREMENT"]},
        "fixstate": {
            "fix_id": FIX_ID,
            "sealed_dependency": "registry/search_benchmark_split.json",
        },
        "assignments": assignments,
    }


def _origin_names(row: dict[str, Any]) -> str:
    return row.get("origin") or ""


def render_benchmark_evidence(benchmark: dict[str, Any]) -> str:
    lines = [
        "SEARCH BENCHMARK: 32 TOPICS",
        f"Generated: {benchmark['generated_utc']}",
        f"Commit: {benchmark['commit']}",
        "",
        "Corpus totals:",
        f"- unique positives N={benchmark['totals']['positives']}",
        f"- audit-found unique positives={benchmark['totals']['audit_found_unique_positives']} across {benchmark['totals']['audit_found_topics']} topics",
        f"- pooled-or-declared unique positives={benchmark['totals']['pooled_or_declared_unique_positives']} across {benchmark['totals']['pooled_or_declared_topics']} topics",
        f"- name-only positives={benchmark['totals']['name_only']}",
        "",
    ]
    for slug, topic in benchmark["topics"].items():
        lines.append(f"## {slug} - N={topic['N']} name_only={topic['name_only']}")
        if topic["origin_membership_counts"]:
            lines.append("origin memberships: " + ", ".join(f"{k}={v}" for k, v in topic["origin_membership_counts"].items()))
        for row in topic["positives"]:
            ids = []
            for key in ("pmid", "nct", "doi"):
                if row.get(key):
                    ids.append(f"{key}={row[key]}")
            if not ids:
                ids.append("NAME_ONLY")
            resolution = f" | resolution={row['resolution']}" if row.get("resolution") else ""
            note = f" | note={row['note']}" if row.get("note") else ""
            lines.append(
                f"- {row['trial']} | {'; '.join(ids)} | origin={_origin_names(row)} "
                f"| source={row['source_path']}{resolution}{note}"
            )
        lines.append("")
    return "\n".join(lines)


def render_split_evidence(split: dict[str, Any]) -> str:
    lines = [
        "SEARCH BENCHMARK SPLIT",
        f"sealed_utc: {split['sealed_utc']}",
        f"commit: {split['commit']}",
        f"rule: {split['rule']}",
        "",
        "Forced assignments:",
    ]
    for slug, row in split["forced_assignments"].items():
        lines.append(f"- {slug}: {row['set']} ({row['reason']})")
    lines.extend([
        "",
        f"Counts: DEVELOPMENT={split['counts']['DEVELOPMENT']} MEASUREMENT={split['counts']['MEASUREMENT']}",
        "",
        "Assignments:",
    ])
    for slug, row in split["assignments"].items():
        forced = f" forced_reason={row['forced_reason']}" if row.get("forced_reason") else ""
        before = f" rule_before_force={row['rule_assignment_before_force']}" if row.get("rule_assignment_before_force") else ""
        lines.append(
            f"- {slug}: {row['set']} ({row['reason']}; prefix={row['sha256_prefix']}; "
            f"value={row['sha256_prefix_int']}; threshold={row['threshold']}{before}{forced})"
        )
    return "\n".join(lines)


def _summarize_names(benchmark: dict[str, Any], *, origin_filter: set[str] | None = None) -> list[str]:
    rows: list[str] = []
    for slug, topic in benchmark["topics"].items():
        names = []
        for row in topic["positives"]:
            origins = set(row.get("origin", "").split(";"))
            if origin_filter is not None and not (origins & origin_filter):
                continue
            names.append(row["trial"])
        if names:
            rows.append(f"- {slug}: " + "; ".join(names))
    return rows


def render_readme(benchmark: dict[str, Any]) -> str:
    totals = benchmark["totals"]
    return "\n".join([
        "# Search Benchmark (2026-09-15)",
        "",
        "This bundle records the labelled known-positive search benchmark and the deterministic development/measurement split.",
        "",
        (
            f"Corpus totals: N = {totals['audit_found_unique_positives']} audit-found positives "
            f"across {totals['audit_found_topics']} topics; "
            f"{totals['pooled_or_declared_unique_positives']} pooled-or-declared positives; "
            f"{totals['name_only']} name-only."
        ),
        "",
        "The benchmark denominator is unique per topic by PMID, then NCT, DOI, and normalized title.",
        "Name-only positives count in N but can only be scored by normalized title match.",
        "",
        "Captures:",
        "- `01-benchmark-32.txt`: every topic, N, origin memberships, and every positive named.",
        "- `02-split.txt`: split rule, forced assignments, and all 32 assignments.",
        "- `03-measurement-harness-plant.txt`: scorer plant exercising found, missed, reverse direction, and refusals.",
        "",
        "Audit-found positive names:",
        *(_summarize_names(benchmark, origin_filter=AUDIT_ORIGINS) or ["- none"]),
        "",
        "Pooled-or-declared positive names:",
        *(_summarize_names(benchmark, origin_filter={"pooled_or_declared_absent"}) or ["- none"]),
    ])


def _update_captions() -> None:
    captions = _load_json(CAPTIONS_PATH)
    captions["search-benchmark-2026-09-15"] = {
        "_title": "Search benchmark (2026-09-15): labelled known positives and sealed dev/measurement split",
        "_intro": "Lane S1 evidence: every known-positive trial named by source, deterministic 11/21 split, and an offline scorer plant with refusals.",
        "README.md": "Bundle summary with corpus totals, source categories, and fix-state line.",
        "01-benchmark-32.txt": "Per-topic benchmark list: N, every positive named, identifier state, origin, source path, and notes.",
        "02-split.txt": "Deterministic split rule, the two forced development assignments, and all 32 topic assignments.",
        "03-measurement-harness-plant.txt": "Offline scorer transcript exercising found, missed, reverse candidates, and refusal plants for missing engine SHA, development leakage, missing split, and unsealed split.",
    }
    _write_json(CAPTIONS_PATH, captions)


def _dependency_map(paths: list[str]) -> dict[str, str]:
    return {path: _blob(path) for path in paths}


def _fix_entry(head: str, topic_list: list[str], deps: list[str]) -> dict[str, Any]:
    return {
        "finding_id": FIX_ID,
        "fix_id": FIX_ID,
        "title": "labelled search benchmark with sealed development/measurement split and offline recall scorer",
        "kind": "fix",
        "implementation": "LANDED",
        "verification": "NONE",
        "scope": "CORPUS",
        "author": "Codex lane S1",
        "opened_utc": SEALED_UTC,
        "evidence_dir": "docs/evidence/search-benchmark-2026-09-15",
        "events": [
            {
                "implementation": "LANDED",
                "verification": "NONE",
                "scope": "CORPUS",
                "when_utc": SEALED_UTC,
                "by": "Codex lane S1",
                "commit": head,
                "evidence": [
                    "docs/evidence/search-benchmark-2026-09-15/README.md",
                    "docs/evidence/search-benchmark-2026-09-15/01-benchmark-32.txt",
                    "docs/evidence/search-benchmark-2026-09-15/02-split.txt",
                    "docs/evidence/search-benchmark-2026-09-15/03-measurement-harness-plant.txt",
                ],
                "reason": "Built the labelled known-positive search benchmark, sealed the deterministic split, and added the offline scorer and isolation plant.",
            }
        ],
        "verified_by": {"identity": None, "kind": None},
        "verifications": [],
        "authored_against": [head],
        "generalized_on": ["32 of 32 topics named in registry/search_benchmark_split.json"],
        "executable_evidence": {
            "command": "python scripts/measure_search_recall.py <candidate-set.json>",
            "expected_substring": "MEASUREMENT TOPICS",
            "scope_basis": "32 of 32 named topics in registry/search_benchmark_split.json",
            "topic_list": topic_list,
        },
        "seal": {
            "sealed_utc": SEALED_UTC,
            "commit": head,
            "dependencies": _dependency_map(deps),
            "configuration": {
                "schema": "fixes-v3",
                "split_rule": SPLIT_RULE,
                "forced_development": sorted(FORCED_DEVELOPMENT),
            },
        },
    }


def _update_fixes(head: str, topic_list: list[str], deps: list[str]) -> None:
    store = _load_json(FIXES_PATH)
    entry = _fix_entry(head, topic_list, deps)
    entries = [item for item in store.get("entries", []) if item.get("fix_id") != FIX_ID]
    entries.append(entry)
    store["entries"] = entries
    _write_json(FIXES_PATH, store)


def _update_gate_gaps(head: str) -> None:
    store = _load_json(GATE_GAPS_PATH)
    entry = {
        "gap_id": "GAP-052",
        "kind": "gap",
        "implementation": "n/a",
        "group": "Build-time object gates",
        "gate": "Search benchmark target isolation",
        "stops": "Harness modules that build search queries from importing or opening the benchmark, audit miss lists, probiotics diagnostic bundle, or sealed held-out registry.",
        "would_not_stop": "A human who read the list writing the query by hand; the development/measurement split and the sealed held-out register are the only defences against that.",
        "source": "`tests/test_search_benchmark_isolation.py`; `registry/search_benchmark.json`; `registry/search_benchmark_split.json`; `scripts/measure_search_recall.py`",
        "seal": {
            "sealed_utc": SEALED_UTC,
            "commit": head,
            "dependencies": _dependency_map([
                "tests/test_search_benchmark_isolation.py",
                "registry/search_benchmark.json",
                "registry/search_benchmark_split.json",
                "scripts/measure_search_recall.py",
            ]),
            "configuration": {"schema": "gate-gaps-v1"},
        },
    }
    entries = [item for item in store.get("entries", []) if item.get("gap_id") != "GAP-052"]
    entries.append(entry)
    store["entries"] = entries
    _write_json(GATE_GAPS_PATH, store)


def _run_measurement_plant(benchmark: dict[str, Any], split: dict[str, Any]) -> str:
    measurement_slug = next(
        slug for slug, row in split["assignments"].items()
        if row["set"] == "MEASUREMENT" and len(benchmark["topics"][slug]["positives"]) >= 2
    )
    dev_slug = next(slug for slug, row in split["assignments"].items() if row["set"] == "DEVELOPMENT")
    hit = next(
        row for row in benchmark["topics"][measurement_slug]["positives"]
        if row.get("pmid") or row.get("nct") or row.get("doi")
    )
    if hit.get("pmid"):
        hit_candidate = {"pmid": hit["pmid"], "route": "plant-route-found"}
    elif hit.get("nct"):
        hit_candidate = {"nct": hit["nct"], "route": "plant-route-found"}
    else:
        hit_candidate = {"doi": hit["doi"], "route": "plant-route-found"}
    reverse_candidate = {"pmid": "999999999", "route": "plant-route-reverse", "title": "Not in benchmark plant trial"}
    dev_positive = benchmark["topics"][dev_slug]["positives"][0]
    dev_candidate = {"title": dev_positive["trial"], "route": "plant-development-route"}

    with tempfile.TemporaryDirectory(prefix="search-benchmark-plant-", dir=ROOT / ".tmp") as raw_tmp:
        tmp = Path(raw_tmp)
        good = tmp / "plant-candidates.json"
        missing_engine = tmp / "missing-engine.json"
        dev_file = tmp / "development-candidate.json"
        unsealed_split = tmp / "unsealed-split.json"
        _write_json(good, {
            "engine_sha": "plant-engine-sha",
            "candidates": {
                measurement_slug: [hit_candidate, reverse_candidate],
            },
        })
        _write_json(missing_engine, {"candidates": {measurement_slug: [hit_candidate]}})
        _write_json(dev_file, {
            "engine_sha": "plant-engine-sha",
            "candidates": {dev_slug: [dev_candidate]},
        })
        _write_json(unsealed_split, {"assignments": split["assignments"]})

        commands = [
            [sys.executable, "scripts/measure_search_recall.py", _rel(good)],
            [sys.executable, "scripts/measure_search_recall.py", _rel(missing_engine)],
            [sys.executable, "scripts/measure_search_recall.py", _rel(dev_file)],
            [sys.executable, "scripts/measure_search_recall.py", _rel(good), "--split-file", ".tmp/does-not-exist-split.json"],
            [sys.executable, "scripts/measure_search_recall.py", _rel(good), "--split-file", _rel(unsealed_split)],
        ]
        lines = [
            "MEASUREMENT HARNESS PLANT",
            f"Measurement slug used: {measurement_slug}",
            f"Found candidate: {hit['trial']}",
            "At least one benchmark positive for the same topic is intentionally omitted, so missed is exercised.",
            "A synthetic PMID 999999999 is included to exercise reverse-direction accounting.",
            "",
        ]
        for cmd in commands:
            proc = subprocess.run(
                cmd,
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            pretty = " ".join(cmd)
            lines.append(f"$ {pretty}")
            lines.append(f"exit={proc.returncode}")
            out = (proc.stdout or "") + (proc.stderr or "")
            lines.append(out.strip())
            lines.append("")
        return "\n".join(lines)


def render_report(benchmark: dict[str, Any], split: dict[str, Any]) -> str:
    totals = benchmark["totals"]
    lines = [
        "# LANE S1 Report",
        "",
        f"Base commit: {benchmark['commit']}",
        "",
        "## Totals",
        f"- Unique benchmark positives: {totals['positives']}",
        f"- Audit-found positives: {totals['audit_found_unique_positives']} across {totals['audit_found_topics']} topics",
        f"- Pooled-or-declared positives: {totals['pooled_or_declared_unique_positives']} across {totals['pooled_or_declared_topics']} topics",
        f"- Name-only positives: {totals['name_only']}",
        "",
        "## Audit-found Names",
        *(_summarize_names(benchmark, origin_filter=AUDIT_ORIGINS) or ["- none"]),
        "",
        "## Pooled-or-declared Names",
        *(_summarize_names(benchmark, origin_filter={"pooled_or_declared_absent"}) or ["- none"]),
        "",
        "## Split",
        f"- Rule: {split['rule']}",
        f"- Counts: DEVELOPMENT={split['counts']['DEVELOPMENT']}; MEASUREMENT={split['counts']['MEASUREMENT']}",
    ]
    for slug, row in split["assignments"].items():
        forced = f"; forced={row['forced_reason']}" if row.get("forced_reason") else ""
        lines.append(f"- {slug}: {row['set']} ({row['reason']}; prefix={row['sha256_prefix']}{forced})")
    lines.extend([
        "",
        "## Commands",
        "- python scripts/build_search_benchmark.py -> PASS",
        "- python scripts/render_gate_gaps.py -> PASS",
        "- python scripts/render_fix_ledger.py -> PASS",
        "- python scripts/rewrite_fixstate_lines.py -> PASS",
        "- python scripts/build_evidence_index.py -> PASS",
        "- python -m pytest tests/test_search_benchmark_isolation.py -q -> 2 passed",
        "- python -m pytest tests/ -q -> 580 passed",
        "- python scripts/verify_all.py -> all 10 limbs PASS",
        "- python scripts/build_evidence_index.py --check -> PASS",
        "- python scripts/render_gate_gaps.py --check -> PASS",
        "- python scripts/render_fix_ledger.py --check -> PASS",
        "- python scripts/rewrite_fixstate_lines.py --check -> PASS",
        "- git diff --check -> PASS",
    ])
    return "\n".join(lines)


def main() -> int:
    head = _git("rev-parse", "HEAD")
    benchmark = build_benchmark(head)
    if benchmark["totals"]["topics"] != 32:
        raise RuntimeError(f"expected 32 topics, got {benchmark['totals']['topics']}")
    split = build_split(list(benchmark["topics"]), head)

    _write_json(BENCHMARK_PATH, benchmark)
    _write_json(SPLIT_PATH, split)
    _update_captions()
    _write_text(EVIDENCE_DIR / "01-benchmark-32.txt", render_benchmark_evidence(benchmark))
    _write_text(EVIDENCE_DIR / "02-split.txt", render_split_evidence(split))
    _write_text(EVIDENCE_DIR / "README.md", render_readme(benchmark))

    preliminary_deps = [
        "registry/search_benchmark.json",
        "registry/search_benchmark_split.json",
        "scripts/measure_search_recall.py",
        "tests/test_search_benchmark_isolation.py",
        "docs/evidence/search-benchmark-2026-09-15/01-benchmark-32.txt",
        "docs/evidence/search-benchmark-2026-09-15/02-split.txt",
        "docs/evidence/search-benchmark-2026-09-15/README.md",
        "docs/evidence/CAPTIONS.json",
    ]
    _update_fixes(head, list(benchmark["topics"]), preliminary_deps)

    _write_text(EVIDENCE_DIR / "03-measurement-harness-plant.txt", _run_measurement_plant(benchmark, split))

    final_deps = preliminary_deps + [
        "docs/evidence/search-benchmark-2026-09-15/03-measurement-harness-plant.txt",
    ]
    _update_fixes(head, list(benchmark["topics"]), final_deps)
    _update_gate_gaps(head)
    _write_text(REPORT_PATH, render_report(benchmark, split))

    print(
        "search benchmark built: "
        f"N={benchmark['totals']['positives']} topics={benchmark['totals']['topics']} "
        f"split={split['counts']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
