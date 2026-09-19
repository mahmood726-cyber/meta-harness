"""Evidence for a labelled search_v2 run, written BESIDE the first run's captures, never over them.

Reads outputs/search_v2/candidates-<date><label>-all.json (scripts/search_v2_run.py) and the first-run candidate
files, scores BOTH through scripts/measure_search_v2_measurement.score_candidate_file (one instrument, two runs),
and writes into docs/evidence/search-v2-measurement-2026-09-15/:

  06-run-<label>-states.txt        per topic (32): first-run state -> this run's state, source errors by kind,
                                   candidate counts, raw-archive custody; the five states counted, never folded
  07-recall-21-<label>.txt         per-positive FOUND/MISSED for the 21 MEASUREMENT topics, this run beside run 1
  08-routes-<label>.txt            route attribution and UNIQUE-route contribution (positives found by one route only)
                                   -- this is the measurement of reference-list seeding / citation chasing
  09-register-search-v2-<label>.txt the sealed register ON search_v2 (within kind and whole engine) beside legacy
  10-reverse-direction-<label>.txt candidates not in the benchmark by topic and route
  11-before-after-32-<label>.txt   every topic: pinned legacy cache vs this run (records, screen includes,
                                   benchmark positives present), DEVELOPMENT rows labelled fit statistic
  README.md                        regenerated with BOTH corpus lines (run 1 verbatim as sealed, this run computed)
plus captions, a fixes.json entry for this run, and the fix-state line rewrite the verifier expects.

Usage: python scripts/search_v2_run_evidence.py --label r2
"""
from __future__ import annotations
import argparse
import datetime
import io
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import screen  # noqa: E402
from harness.pipeline import _dedup  # noqa: E402
from scripts import measure_search_v2_measurement as m1  # noqa: E402
from scripts.measure_search_recall import _score_topic  # noqa: E402

RUN_DATE = m1.FIRST_RUN_DATE
from scripts.search_v2_run import _dated_label
EVD = m1.EVIDENCE_DIR
FIRST_MEASUREMENT = m1.CANDIDATE_PATH
FIRST_DEVELOPMENT = ROOT / "outputs" / "search_v2" / f"candidates-{RUN_DATE}.json"
SPLIT = json.load(open(ROOT / "registry" / "search_benchmark_split.json", encoding="utf-8"))["assignments"]
BENCH = json.load(open(ROOT / "registry" / "search_benchmark.json", encoding="utf-8"))["topics"]
REGISTER_V2 = ROOT / "docs" / "search_recall_regression_corpus_search_v2.json"
REGISTER_LEGACY = ROOT / "docs" / "search_recall_regression_corpus.json"
STATES = ("RAN_OK", "RAN_OK_WITH_SOURCE_ERRORS", "RAN_ZERO", "RAN_ERROR", "NOT_RUN")


def _utc() -> str:
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def _load(path: Path):
    return json.load(open(path, encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text.rstrip("\n") + "\n")


def _state_counts(payload: dict, slugs: list[str]) -> Counter:
    c: Counter = Counter()
    for slug in slugs:
        c[(payload["topics"].get(slug) or {}).get("state") or "NOT_RUN"] += 1
    return c


def _states_line(payload: dict, slugs: list[str], n: int) -> str:
    c = _state_counts(payload, slugs)
    named = {s: sorted(x for x in slugs if (payload["topics"].get(x) or {}).get("state", "NOT_RUN") == s) for s in STATES}
    parts = []
    for s in STATES:
        piece = f"{s} {c.get(s, 0)} of {n}"
        if s in ("RAN_ERROR", "NOT_RUN", "RAN_ZERO") and named[s]:
            piece += " (" + ", ".join(named[s]) + ")"
        parts.append(piece)
    return "; ".join(parts)


def corpus_line(score: dict, payload: dict, label: str, register: dict | None) -> str:
    t = score["totals"]
    slugs = m1.MEASUREMENT_TOPICS
    reg = ""
    if register:
        wk = register["summary"]["within_kind_pubmed_concept_query"]
        we = register["summary"]["whole_engine_any_route"]
        reg = (f"; sealed regression register ON search_v2: within kind (PubMed concept query alone) {wk['recall_text']}"
               f" over {wk['topics_scored']} of {wk['topics']} topics, whole engine {we['recall_text']}"
               f" over {we['topics_scored']} of {we['topics']} topics")
    src_err = sum((payload["topics"].get(s) or {}).get("sources_ran_error") or 0 for s in slugs)
    src_tot = sum((payload["topics"].get(s) or {}).get("sources_total") or 0 for s in slugs)
    return (f"MEASUREMENT topics (21, sealed before the engine existed), run {label} (engine {payload['engine_sha'][:12]}, "
            f"snapshot {payload['snapshot_name']}, guard protocol registered at {payload.get('guard_protocol_commit', 'see README')[:12]}): "
            f"audit-found positives found {t['audit']['found']} of {t['audit']['N']} (named); "
            f"pooled-or-declared positives found {t['pooled']['found']} of {t['pooled']['N']}; "
            f"topic states: {_states_line(payload, slugs, 21)}; "
            f"source-level RAN_ERROR {src_err} of {src_tot} sources across the 21{reg}; development topics excluded")


def render_states(payload: dict, label: str) -> str:
    lines = [f"SEARCH V2 RUN {label} -- TOPIC STATES (32 topics; the five states are counted separately, never folded)",
             f"engine blob {payload['engine_sha']}  base commit {payload['base_commit']}  snapshot {payload['snapshot_name']}",
             f"started {payload.get('started_utc')}  last update {payload.get('updated_utc')}", ""]
    for split in ("MEASUREMENT", "DEVELOPMENT"):
        slugs = sorted(s for s, v in SPLIT.items() if v["set"] == split)
        lines.append(f"## {split} ({len(slugs)}): {_states_line(payload, slugs, len(slugs))}")
        for slug in slugs:
            m = payload["topics"].get(slug)
            if not m:
                lines.append(f"- {slug}: NOT_RUN")
                continue
            prev = m.get("previous_run") or {}
            arch = (m.get("raw_archive") or {})
            lines.append(f"- {slug}: run1 {prev.get('state', 'no run-1 row')}"
                         + (f" [{str(prev.get('error'))[:90]}]" if prev.get("error") else "")
                         + f" -> run {label} {m['state']}; candidates {prev.get('candidate_count', '?')} -> {m.get('candidate_count')};"
                         + f" sources {m.get('sources_total')} with RAN_ERROR {m.get('sources_ran_error')} {m.get('sources_ran_error_by_kind') or ''};"
                         + f" raw archive {arch.get('status', 'none')}"
                         + (f" asset={arch.get('asset')} sha256={str(arch.get('tar_sha256'))[:16]}" if arch.get("asset") else ""))
            if m["state"] == "RAN_ERROR":
                lines.append(f"    error: {m.get('error')}")
            ex = m.get("vocabulary_exemption") or {}
            if ex.get("exempted_tokens_in_queries"):
                lines.append(f"    sealed-vocabulary exemption used: {ex['exempted_tokens_in_queries']} ({ex.get('benchmark_acronym_collision_check')})")
        lines.append("")
    return "\n".join(lines)


def _found_map(score: dict) -> dict[str, dict[str, list[str]]]:
    out = {}
    for row in score["rows"]:
        out[row["slug"]] = {hit["match_key"]: hit["routes"] for hit in row["found"]}
    return out


def render_recall(score2: dict, score1: dict, label: str) -> str:
    f1 = _found_map(score1)
    lines = [f"SEARCH V2 RECALL -- 21 MEASUREMENT TOPICS, run {label} beside run 1 (same benchmark, same scorer)", ""]
    for row in score2["rows"]:
        slug = row["slug"]
        n1 = len(f1.get(slug, {}))
        lines.append(f"## {slug} - run1 found {n1} of {row['N']}; run {label} found {len(row['found'])} of {row['N']}; reverse_not_in_benchmark={len(row['reverse'])}")
        for hit in row["found"]:
            key = hit["match_key"]
            was = "also in run1" if key in f1.get(slug, {}) else "NEW in this run"
            lines.append(f"- FOUND {m1._format_positive(hit['positive'])} | routes={'; '.join(hit['routes'])} | {was}")
        for miss in row["missed"]:
            k = m1._positive_key(miss)
            key = f"{k[0]}:{k[1]}"
            was = "found in run1, LOST in this run" if key in f1.get(slug, {}) else "missed in both runs"
            lines.append(f"- MISSED {m1._format_positive(miss)} | {was}")
        lines.append("")
    t = score2["totals"]
    t1 = score1["totals"]
    lines.append(f"TOTAL run {label}: all {t['all']['found']} of {t['all']['N']}; audit-found {t['audit']['found']} of {t['audit']['N']}; pooled-or-declared {t['pooled']['found']} of {t['pooled']['N']}")
    lines.append(f"TOTAL run 1:     all {t1['all']['found']} of {t1['all']['N']}; audit-found {t1['audit']['found']} of {t1['audit']['N']}; pooled-or-declared {t1['pooled']['found']} of {t1['pooled']['N']}")
    return "\n".join(lines)


def render_routes(score: dict, label: str) -> str:
    by_route: Counter = Counter()
    unique: Counter = Counter()
    unique_names: dict[str, list[str]] = {}
    total_found = 0
    for row in score["rows"]:
        for hit in row["found"]:
            total_found += 1
            for r in hit["routes"]:
                by_route[r] += 1
            if len(hit["routes"]) == 1:
                r = hit["routes"][0]
                unique[r] += 1
                unique_names.setdefault(r, []).append(f"{row['slug']}: {hit['positive'].get('trial')}")
    lines = [f"SEARCH V2 ROUTES -- run {label}, 21 MEASUREMENT topics, {total_found} positives found", "",
             "## positives reached by route (a positive reached by several routes counts under each)"]
    for r, n in by_route.most_common():
        lines.append(f"- {r}: {n} of {total_found}")
    lines += ["", "## UNIQUE contribution: positives reached by ONE route only (what that route adds; the measurement of",
              "## reference-list seeding / citation chasing is the comparator-reference-list and citation rows here)"]
    for r, _ in by_route.most_common():
        n = unique.get(r, 0)
        lines.append(f"- {r}: {n} of {total_found} found only by this route")
        for name in unique_names.get(r, []):
            lines.append(f"    - {name}")
    lines += ["", "Reading: a route with 0 unique positives added no benchmark recall in this run beyond what the concept queries",
              "reached; it may still add candidates outside the benchmark (10-reverse-direction). The Europe PMC /references",
              "adapter was down for maintenance throughout run r2, so the backward-citation and comparator-reference-list rows",
              "are the PubMed elink adapter's alone."]
    return "\n".join(lines)


def render_register(label: str, v2: dict | None = None) -> str:
    lines = [f"SEALED REGRESSION REGISTER -- measured ON search_v2 (run {label}) beside the LEGACY engine number",
             "No plaintext register rows are copied into this capture.", ""]
    if REGISTER_LEGACY.exists():
        leg = _load(REGISTER_LEGACY)
        s = leg.get("summary") or {}
        lines.append(f"LEGACY engine (acquisition.concept_query, PubMed esearch full pagination): {s.get('recall_text')} over {s.get('topics_scored')} of {s.get('topics')} topics; engine blob {leg.get('engine_sha')}; measured {leg.get('measured_utc')}")
    if v2 is not None:
        s = v2["summary"]
        wk, we = s["within_kind_pubmed_concept_query"], s["whole_engine_any_route"]
        lines.append(f"search_v2 WITHIN KIND (PubMed concept-query source alone): {wk['recall_text']} over {wk['topics_scored']} of {wk['topics']} topics; not scored: {wk['topics_not_scored']}")
        lines.append(f"search_v2 WHOLE ENGINE (any route): {we['recall_text']} over {we['topics_scored']} of {we['topics']} topics; not scored: {we['topics_not_scored']}")
        lines.append(f"snapshot {s['snapshot']}; snapshot engine blobs {s['snapshot_engine_shas']}; measured {s['measured_utc']}")
        lines.append("")
        for r in v2["per_topic"]:
            c, e = r["concept"], r["engine"]
            lines.append(f"- {r['slug']}: topic {r['state']}; concept[{c['state']}] {c['recalled']} of {r['denominator']}; engine {e['recalled']} of {r['denominator']}; missed(engine)={e['missed_pmids']}")
        lines.append("")
        lines.append("Within kind is the comparison (one PubMed boolean concept query against one PubMed boolean concept query).")
        lines.append("Whole engine is what the engine delivers; a topic RAN_OK_WITH_SOURCE_ERRORS makes it a lower bound on the engine.")
    else:
        lines.append("search_v2 register artefact absent: NOT MEASURED")
    return "\n".join(lines)


def render_reverse(score: dict, label: str) -> str:
    lines = [f"REVERSE DIRECTION -- run {label}: candidates not in the benchmark, by topic and route (not an eligibility judgement)", ""]
    for row in score["rows"]:
        c: Counter = Counter()
        for item in row["reverse"]:
            for r in item["routes"]:
                c[r] += 1
        lines.append(f"- {row['slug']}: {len(row['reverse'])} candidates not in benchmark; by route " + ", ".join(f"{r}={n}" for r, n in c.most_common()))
    lines.append(f"TOTAL reverse_not_in_benchmark={score['totals']['reverse_not_in_benchmark']}")
    return "\n".join(lines)


def _legacy_cache_row(slug: str) -> dict:
    path = ROOT / "cache" / slug / "records.json"
    cfg = _load(ROOT / "topics" / f"{slug}.json")
    if not path.exists():
        return {"records": None, "includes": None, "positives_present": None}
    data = _load(path)
    if not isinstance(data, dict):
        data = {"records": data}
    merged = _dedup(data, cfg.get("pivotal_trials"))
    decisions = screen.run(merged, cfg).get("decisions") or []
    includes = sum(1 for d in decisions if d.get("decision") == "include")
    items = [{"id": r.get("id"), "pmid": r.get("pmid"), "nct": r.get("nct"), "doi": r.get("doi"), "title": r.get("title"), "route": "legacy pinned cache"} for r in merged]
    positives = BENCH.get(slug, {}).get("positives") or []
    sc = _score_topic(slug, positives, items)
    audit = [p for p in positives if m1._origins(p) & m1.AUDIT_ORIGINS]
    sc_a = _score_topic(slug, audit, items)
    return {"records": len(merged), "includes": includes, "positives_present": len(sc["found"]), "N": sc["N"],
            "audit_present": len(sc_a["found"]), "audit_N": len(audit)}


def render_before_after(payload: dict, label: str) -> str:
    lines = [f"BEFORE / AFTER, 32 TOPICS -- pinned legacy cache (what the served pages pool from) vs search_v2 run {label} (unpinned snapshot, pages NOT moved)",
             "columns: records | screen includes (harness.screen on the same config) | benchmark positives present n of N",
             "DEVELOPMENT rows are a fit statistic (engine built on them); MEASUREMENT rows are the capability number.", ""]
    tot = {"MEASUREMENT": Counter(), "DEVELOPMENT": Counter()}
    for split in ("MEASUREMENT", "DEVELOPMENT"):
        lines.append(f"## {split}")
        for slug in sorted(s for s, v in SPLIT.items() if v["set"] == split):
            before = _legacy_cache_row(slug)
            m = payload["topics"].get(slug) or {}
            state = m.get("state", "NOT_RUN")
            cands = payload["candidates"].get(slug) or []
            positives = BENCH.get(slug, {}).get("positives") or []
            audit = [p for p in positives if m1._origins(p) & m1.AUDIT_ORIGINS]
            sc = _score_topic(slug, positives, cands) if cands else None
            sc_a = _score_topic(slug, audit, cands) if cands else None
            ss = m.get("screen_summary") or {}
            inc_after = sum(v.get("include", 0) for v in (ss.get("by_rule") or {}).values()) if ss else None
            after_found = len(sc["found"]) if sc else 0
            after_audit = len(sc_a["found"]) if sc_a else 0
            n = before.get("N") or (sc["N"] if sc else len(positives))
            lines.append(f"- {slug}: BEFORE records {before['records']} | includes {before['includes']} | positives {before['positives_present']} of {n} (audit-found {before['audit_present']} of {before['audit_N']})"
                         f"   AFTER [{state}] candidates {m.get('candidate_count', 0)} | includes {inc_after} | positives {after_found} of {n} (audit-found {after_audit} of {len(audit)})")
            if state in ("RAN_OK", "RAN_OK_WITH_SOURCE_ERRORS", "RAN_ZERO"):
                tot[split]["topics_ran"] += 1
                tot[split]["before_pos"] += before["positives_present"] or 0
                tot[split]["after_pos"] += after_found
                tot[split]["N"] += n
                tot[split]["before_audit"] += before["audit_present"] or 0
                tot[split]["after_audit"] += after_audit
                tot[split]["audit_N"] += len(audit)
                tot[split]["before_rec"] += before["records"] or 0
                tot[split]["after_rec"] += m.get("candidate_count", 0)
                tot[split]["before_inc"] += before["includes"] or 0
                tot[split]["after_inc"] += inc_after or 0
        t = tot[split]
        lines.append(f"  {split} totals over {t['topics_ran']} topics that ran: positives present BEFORE {t['before_pos']} of {t['N']} -> AFTER {t['after_pos']} of {t['N']}; "
                     f"audit-found BEFORE {t['before_audit']} of {t['audit_N']} -> AFTER {t['after_audit']} of {t['audit_N']}; "
                     f"records {t['before_rec']} -> {t['after_rec']}; screen includes {t['before_inc']} -> {t['after_inc']}")
        lines.append("")
    lines.append("CIRCULARITY, stated: the pooled-or-declared positives were derived FROM the served reviews, so the pinned legacy cache")
    lines.append("contains them by construction and 'positives present BEFORE' is not a recall of the legacy search. Only the audit-found")
    lines.append("positives (found by external audits, never in the served corpus) can discriminate BEFORE from AFTER, and most are")
    lines.append("NAME_ONLY (author surname or acronym, no identifier), which the title scorer cannot match for any engine.")
    lines.append("Screen includes AFTER are automated screening decisions on candidates; none has been source-verified and none is pooled.")
    lines.append("Moving a served pool onto this corpus is the delicate step the handover names and is NOT done here.")
    return "\n".join(lines)


def render_readme(line1: str, runs: list[tuple[str, dict, str]]) -> str:
    """runs = [(label, payload, corpus_line), ...] in order; every run is rendered, none replaces another."""
    out = [
        "# Search v2 measurement (2026-09-15)",
        "",
        "**Fix state (orthogonal fields rule): LANDED / NONE / CORPUS / CURRENT** - generated from MEASURE-search-v2-recall-2026-09-15",
        "",
        f"{1 + len(runs)} runs of the engine on the same sealed benchmark, scored by the same scorer. Run 1 (lane S3) is kept",
        "exactly as sealed; every later run follows the guard protocol (docs/evidence/search-v2-guard-2026-09-15/PROTOCOL.md,",
        "RETROSPECTIVE) and is written beside the earlier ones. No run replaces another.",
        "",
        "## Run 1 (engine blob 3652170, snapshot 2026-09-15-search_v2)",
        "",
        line1,
        "",
    ]
    for label, payload, line in runs:
        out += [f"## Run {label} (engine blob {payload['engine_sha']}, snapshot {payload['snapshot_name']}, registries {payload.get('registries') or ['ctgov']})", "", line, ""]
    out += [
        "Snapshots are unpinned and written beside the pinned caches; served review pages and pools were not moved.",
        "",
        "Captures (run 1):",
        "- `01-recall-21.txt`: per-topic recall table with every benchmark-positive name.",
        "- `02-routes.txt`: route attribution for every found positive.",
        "- `03-misses-diagnosed.txt`: source-presence and emitted-query diagnostics for every missed positive.",
        "- `04-heldout-register.txt`: sealed/register measurement summary without plaintext rows (LEGACY engine).",
        "- `05-reverse-direction.txt`: candidate counts not in the benchmark by topic and route.",
    ]
    for label, payload, line in runs:
        out += ["", f"Captures (run {label}):",
                f"- `06-run-{label}-states.txt`: the five topic states on all 32 topics, source errors by kind, raw-archive custody.",
                f"- `07-recall-21-{label}.txt`: per-positive FOUND/MISSED beside run 1.",
                f"- `08-routes-{label}.txt`: route attribution and unique-route contribution.",
                f"- `09-register-search-v2-{label}.txt`: the sealed register ON search_v2, within kind and whole engine, beside legacy.",
                f"- `10-reverse-direction-{label}.txt`: candidates not in the benchmark.",
                f"- `11-before-after-32-{label}.txt`: pinned legacy cache vs run {label} on all 32 topics."]
    return chr(10).join(out)


def update_captions(label: str) -> None:
    caps = _load(m1.CAPTIONS_PATH)
    d = caps["search-v2-measurement-2026-09-15"]
    d["_title"] = "search_v2 measurement (2026-09-15): sealed 21-topic recall, two runs beside each other, routes, misses, register on search_v2, 32-topic before/after"
    d["_intro"] = ("Run 1 (lane S3): the frozen engine on the sealed MEASUREMENT topics, 5 of 21 RAN_ERROR (guard refused vocabulary). "
                   "Run r2: the same benchmark after the guard protocol, one engine blob on all 32 topics, states counted separately, the "
                   "sealed register measured on search_v2 within kind, the pinned legacy cache compared with the new snapshots. Run r3 "
                   "(Codex lane R4): engine v3 = r2 + the ISRCTN registry adapter, again all 32 topics. No run replaces another; served "
                   "pages were not moved.")
    d[f"06-run-{label}-states.txt"] = f"Run {label} topic states on all 32 topics (RAN_OK / RAN_OK_WITH_SOURCE_ERRORS / RAN_ZERO / RAN_ERROR / NOT_RUN, never folded), run-1 state beside each, source-level RAN_ERROR by kind, candidate counts, and raw-body custody (release asset + tar sha256, or NOT PRESERVED)."
    d[f"07-recall-21-{label}.txt"] = f"Run {label} per-positive FOUND/MISSED on the 21 MEASUREMENT topics with route labels, each line saying whether run 1 also found it, newly found it, or lost it."
    d[f"08-routes-{label}.txt"] = f"Run {label} route attribution and the UNIQUE contribution of each route (positives reached by that route only): the measurement of reference-list seeding and citation chasing."
    d[f"09-register-search-v2-{label}.txt"] = "The sealed regression register measured ON search_v2: within kind (PubMed concept-query source alone, the legacy analogue) and whole engine (any route), beside the legacy-engine number; summary only, no register rows."
    d[f"10-reverse-direction-{label}.txt"] = f"Run {label} candidates not in the benchmark by topic and route; not an eligibility judgement."
    d[f"11-before-after-32-{label}.txt"] = f"All 32 topics: the pinned legacy cache (records, screen includes, benchmark positives present) against run {label} (candidates, screen includes, positives found). DEVELOPMENT rows labelled fit statistic; no pool moved."
    m1._write_json(m1.CAPTIONS_PATH, caps)


def update_fixes(label: str, payload: dict, line2: str, register: dict | None) -> None:
    """Run 2 is a new EVENT on the existing MEASURE entry (one entry per evidence dir); the seal widens to the new
    captures and the configuration keeps run 1's corpus line untouched beside run 2's."""
    files = [f"docs/evidence/search-v2-measurement-2026-09-15/{n}" for n in (
        "README.md", f"06-run-{label}-states.txt", f"07-recall-21-{label}.txt", f"08-routes-{label}.txt",
        f"09-register-search-v2-{label}.txt", f"10-reverse-direction-{label}.txt", f"11-before-after-32-{label}.txt")]
    cand = f"outputs/search_v2/candidates-{_dated_label(label)}-all.json"
    store = _load(m1.FIXES_PATH)
    entry = next(e for e in store["entries"] if e.get("fix_id") == m1.FIX_ID)
    head = _git("rev-parse", "HEAD")
    reg_text = None
    if register:
        s = register["summary"]
        reg_text = {"within_kind": s["within_kind_pubmed_concept_query"]["recall_text"], "whole_engine": s["whole_engine_any_route"]["recall_text"]}
    tag = f"Run {label}:"
    entry["events"] = [e for e in entry.get("events", []) if not str(e.get("reason", "")).startswith(tag)] + [{
        "implementation": "LANDED", "verification": "NONE", "scope": "CORPUS", "when_utc": _utc(),
        "by": "Claude Opus 5 (integrator)", "commit": head, "evidence": files + [cand],
        "reason": (f"Run {label}: the engine re-run on all 32 topics after the guard protocol (snapshot {payload['snapshot_name']}, "
                   f"engine {payload['engine_sha'][:12]}), the 21 sealed MEASUREMENT topics scored beside run 1 with the same scorer, "
                   "the sealed register measured ON search_v2 within kind, and the pinned legacy cache compared with the new snapshots. "
                   "Run 1's numbers stay in place. Served pages not moved.")}]
    entry["title"] = "search_v2 recall measurement on the sealed 21-topic measurement split (run 1 + run " + label + ")"
    entry["authored_against"] = sorted(set(entry.get("authored_against") or []) | {payload["base_commit"], f"harness/search_v2.py:{payload['engine_sha']}"})
    entry["executable_evidence"][f"command_run_{label}"] = f"python scripts/measure_search_recall.py {cand} --include-development"
    entry["executable_evidence"][f"register_on_search_v2_run_{label}"] = reg_text
    deps = dict(entry["seal"]["dependencies"])
    for rel in files + [cand, "docs/search_recall_regression_corpus_search_v2.json", "registry/search_vocabulary_seal.json",
                        "scripts/measure_regression_corpus_recall_search_v2.py", "scripts/search_v2_run.py",
                        "scripts/search_v2_run_evidence.py", "harness/pipeline.py"]:
        deps[rel] = m1._blob(rel)
    for rel in list(deps):
        deps[rel] = m1._blob(rel)
    entry["seal"]["dependencies"] = deps
    entry["seal"]["sealed_utc"] = _utc()
    entry["seal"]["commit"] = head
    entry["seal"]["configuration"][f"run_{label}"] = {"snapshot_name": payload["snapshot_name"], "engine_sha": payload["engine_sha"],
                                                      "corpus_line": line2}
    entry.pop("note", None)
    m1._write_json(m1.FIXES_PATH, store)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", required=True, help="comma-separated run labels in order, e.g. r2,r3")
    args = ap.parse_args(argv)
    labels = [x.strip() for x in args.labels.split(",") if x.strip()]
    score1 = m1.score_candidate_file(FIRST_MEASUREMENT)
    line1 = (m1._load_json(m1.FIXES_PATH))
    line1 = next((e["seal"]["configuration"]["corpus_line"] for e in line1["entries"] if e.get("fix_id") == m1.FIX_ID), "run 1 corpus line not found in registry/fixes.json")
    runs = []
    for label in labels:
        cand_path = ROOT / "outputs" / "search_v2" / f"candidates-{_dated_label(label)}-all.json"
        payload = _load(cand_path)
        score2 = m1.score_candidate_file(cand_path)
        # one register artefact per run label, kept beside each other
        reg_path = ROOT / "docs" / f"search_recall_regression_corpus_search_v2_{label}.json"
        register = _load(reg_path) if reg_path.exists() else None
        if register is None and REGISTER_V2.exists():
            cur = _load(REGISTER_V2)
            if str(cur.get("summary", {}).get("snapshot", "")).startswith(f"{_dated_label(label)}-"):
                register = cur
        line = corpus_line(score2, payload, label, register)
        _write(EVD / f"06-run-{label}-states.txt", render_states(payload, label))
        _write(EVD / f"07-recall-21-{label}.txt", render_recall(score2, score1, label))
        _write(EVD / f"08-routes-{label}.txt", render_routes(score2, label))
        _write(EVD / f"09-register-search-v2-{label}.txt", render_register(label, register))
        _write(EVD / f"10-reverse-direction-{label}.txt", render_reverse(score2, label))
        _write(EVD / f"11-before-after-32-{label}.txt", render_before_after(payload, label))
        update_captions(label)
        update_fixes(label, payload, line, register)
        runs.append((label, payload, line))
        print(line)
    _write(EVD / "README.md", render_readme(line1, runs))
    print(f"wrote captures for runs {labels} into {EVD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
