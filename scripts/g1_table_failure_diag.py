"""Offline structural diagnostics; no extracted text or numeric results are emitted.

Fixed precedence (first applicable): NONE_TABLE_TUPLE_BINDS, NO_TABLE,
NO_OUTCOME_TABLE, NO_ARM_HEADER, MULTI_POPULATION_UNRESOLVED,
MULTI_TIMEPOINT_UNRESOLVED, ARM_HEADER_NOT_MAPPED, DISTRIBUTION_ROWS,
PCT_ONLY, EFFECT_ONLY_NO_COUNTS, OTHER. Splits precede mapping because they
explain repeated arm columns. A successful parser result always wins; this is
not an admission decision. All failure classes are structural heuristics.

Best outcome table: exact row match, partial row match, both arm names,
count-bearing cells, then earliest document order (descending first four).
Numeric runs require two consecutive lines with at least three numeric tokens.
Up to three immediately preceding nonblank lines supply caption/header context.

Hardcode disclosure:
Item                         Static / dynamic
Patterns, precedence, limits Static diagnostic rules, not research findings
Outcome and arm vocabulary   Dynamic protocol configuration
Features and counts          Dynamic deterministic parsing of supplied text
Held-copy paths              Existing PMC/Unpaywall cache conventions

CLI only reads held copies; it never calls fetchers, models, or pipeline runners.
--census accepts one or more phase3 directories (or census JSON files).
--labels accepts a JSON list or the path to a JSON list of {slug,label}.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import g1_trial_acquire as ta  # noqa: E402

NUMBER = r"\d[\d,]*(?:\.\d+)?"
NUM = re.compile(r"(?<!\w)" + NUMBER + r"(?!\w)")
COUNT = re.compile(r"^\s*\d[\d,]*\s*(?:\(\s*\d+(?:\.\d+)?\s*%?\s*\)|/\s*\d[\d,]*)(?:\s*\([^)]*%\))?\s*[*†‡]?\s*$")
PCT = re.compile(r"^\s*\(?\s*\d+(?:\.\d+)?\s*%\s*\)?\s*[*†‡]?\s*$")
TIME = re.compile(r"\b(day|week|month|year)s?\s*[-:]?\s*(\d+)\b|\b(\d+)\s*[- ]\s*(day|week|month|year)s?\b", re.I)
CI = re.compile(r"\bCI\b|confidence\s+interval", re.I)
EFFECT = re.compile(r"\b(?:RR|OR|HR|MD|SMD)\b|(?:risk|odds|hazard)\s+ratio|mean\s+difference", re.I)


def _norm(value):
    return re.sub(r"\s+", " ", value.casefold()).strip(" .:;\t")


def _matches(value, terms):
    return any(re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", value, re.I)
               for t in terms if t)


def _cells(line):
    if " | " in line:
        return [c.strip() for c in line.strip().strip("|").split("|")]
    cells = re.split(r"\s{2,}|\t+", line.strip())
    if len(cells) == 1:
        m = NUM.search(line)
        if m:
            return [line[:m.start()].strip()] + line[m.start():].split()
    return cells


def _blocks(text):
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        pipe = " | " in lines[i]
        numeric = len(NUM.findall(lines[i])) >= 3
        if not (pipe or numeric):
            i += 1
            continue
        start = i
        while i < len(lines) and ((" | " in lines[i]) if pipe else
                                  (" | " not in lines[i] and len(NUM.findall(lines[i])) >= 3)):
            i += 1
        if not pipe and i - start < 2:
            continue
        before = start
        while before > max(0, start - 3) and lines[before - 1].strip() and " | " not in lines[before - 1]:
            if len(NUM.findall(lines[before - 1])) >= 3:
                break
            before -= 1
            if re.match(r"\s*Table\b", lines[before], re.I):
                break
        yield lines[before:start], [_cells(x) for x in lines[start:i]]


def _features(context, rows, terms, cfg):
    # Data starts at the first row with a numeric-leading cell after its label.
    # Header Ns and timepoint names therefore remain header rows.
    first = next((i for i, r in enumerate(rows)
                  if any(re.match(r"^\s*\(?\d", c) and not CI.search(c)
                         and not TIME.search(c) for c in r[1:])), len(rows))
    # Numeric runs may have a whitespace-delimited header just before the run.
    # Keep its column boundaries; single-space prose never establishes mapping.
    context_headers = [_cells(line) for line in context
                       if re.search(r"\S(?: {2,}|\t+)\S", line)
                       and not re.match(r"\s*Table\b", line, re.I)]
    headers, data = context_headers + rows[:first], rows[first:]
    head = "\n".join(context + [" | ".join(r) for r in headers])
    labels = [r[0] for r in data if r]
    matching = [r for r in data if r and _matches(r[0], terms)]
    relevant = matching or data
    exact = any(_norm(r[0]) == _norm(t) for r in matching for t in terms)
    partial = any(_matches(r[0], terms) and not any(_norm(r[0]) == _norm(t) for t in terms)
                  for r in matching)
    outcome = bool(matching) or _matches(head, terms)
    intervention = cfg.get("intervention_terms") or []
    comparator = list(cfg.get("comparator_terms") or []) + ["placebo", "control"]
    has_arm = _matches(head, intervention) and _matches(head, comparator)
    width = max((len(r) for r in headers + data), default=0)
    columns = [" ".join(r[j] for r in headers if j < len(r)) for j in range(width)]
    exp = {j for j, c in enumerate(columns) if _matches(c, intervention)}
    ctrl = {j for j, c in enumerate(columns) if _matches(c, comparator)}
    mapped = len(exp) == len(ctrl) == 1 and not exp & ctrl
    times = {(a.lower() or d.lower(), int(b or c)) for a, b, c, d in TIME.findall(head)}
    itt = bool(re.search(r"\bITT\b|intent(?:ion)?[- ]to[- ]treat", head, re.I))
    pp = bool(re.search(r"\bPP\b|per[- ]protocol", head, re.I))
    body = "\n".join(" | ".join(r) for r in relevant)
    all_cells = [c for r in data for c in r[1:]]
    target_cells = [c for r in relevant for c in r[1:]]
    counts = sum(bool(COUNT.fullmatch(c)) for c in target_cells)
    # A '%' column heading permits unadorned decimal percentages, but CI/effect
    # columns do not imply percentages merely because '95%' occurs there.
    pct_columns = {j for j, c in enumerate(columns) if "%" in c and not CI.search(c)}
    pct_only = sum(bool(PCT.fullmatch(c)) or (j in pct_columns and bool(re.fullmatch(NUMBER, c)))
                   for r in relevant for j, c in enumerate(r) if j > 0)
    integer_counts = any(re.fullmatch(r"\d[\d,]*", c)
                         for r in relevant for j, c in enumerate(r)
                         if j > 0 and j not in pct_columns)
    episode_labels = {int(m.group(1)) for label in labels
                      if (m := re.match(r"^\s*([012])\s*(?:episodes?\b|$)", label, re.I))}
    distribution = len(episode_labels) >= 2 and bool(re.search(r"\bepisodes?\b", head + "\n" + body, re.I))
    return {
        "has_arm_header": bool(has_arm), "arm_header_mapped": bool(mapped),
        "has_n_header": bool(re.search(r"\bn\s*=\s*\d", head, re.I)),
        "cells_count_pct": sum(bool(COUNT.fullmatch(c)) for c in all_cells),
        "cells_pct_only": pct_only, "has_ci": bool(CI.search(head + "\n" + body)),
        "has_multiple_timepoint_columns": len(times) > 1,
        "has_itt_pp_split_columns": itt and pp,
        "has_stratified_subgroup_rows": any(re.search(
            r"\bsubgroup|\bstrat(?:um|a|ified)\b|\b(?:male|female|men|women)\b|\bage\s*[<>≤≥]", s, re.I)
            for s in labels),
        "row_label_exact": exact, "row_label_partial": partial,
        "distribution_rows": distribution,
        "_outcome": outcome, "_pct_only": pct_only > 0 and counts == 0 and not integer_counts,
        "_effect_only": bool(EFFECT.search(head + "\n" + body)) and counts == 0 and not integer_counts,
    }


def diagnose(text, cfg):
    """Return only counts, booleans, fixed class names, and tuple field names.

    No source strings are returned, even when short. table_tuple_result is the
    sorted keys of table_tuple(...)[1], never its label, span, or count values.
    """
    terms = ta.outcome_row_terms(cfg)
    tt = ta.table_tuple(text, terms, (cfg.get("primary_outcome") or {}).get("timepoint"))
    features = [_features(c, r, terms, cfg) for c, r in _blocks(text)]
    candidates = [(i, f) for i, f in enumerate(features) if f["_outcome"]]
    best_index, best = max(candidates, key=lambda item: (
        item[1]["row_label_exact"], item[1]["row_label_partial"], item[1]["has_arm_header"],
        item[1]["cells_count_pct"], -item[0]), default=(None, _features([], [], terms, cfg)))
    cases = [
        (tt is not None, "NONE_TABLE_TUPLE_BINDS"),
        (not features, "NO_TABLE"), (not candidates, "NO_OUTCOME_TABLE"),
        (not best["has_arm_header"], "NO_ARM_HEADER"),
        (best["has_itt_pp_split_columns"], "MULTI_POPULATION_UNRESOLVED"),
        (best["has_multiple_timepoint_columns"], "MULTI_TIMEPOINT_UNRESOLVED"),
        (not best["arm_header_mapped"], "ARM_HEADER_NOT_MAPPED"),
        (best["distribution_rows"], "DISTRIBUTION_ROWS"),
        (best["_pct_only"], "PCT_ONLY"),
        (best["_effect_only"], "EFFECT_ONLY_NO_COUNTS"), (True, "OTHER"),
    ]
    return dict(n_tables=len(features), tables_with_outcome_term=len(candidates),
                best_table_index=best_index,
                **{k: v for k, v in best.items() if not k.startswith("_")},
                failure_class=next(name for condition, name in cases if condition),
                table_tuple_result=sorted(tt[1]) if tt is not None else None)


def _short(value):
    value = str(value)
    return value if len(value) <= 40 else value[:29] + "~" + hashlib.sha256(value.encode()).hexdigest()[:10]


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _held_text(row):
    """Runtime-only, read-only equivalent of open_fill's PMC-then-UPW lookup."""
    base = ROOT / "outputs" / "k_gap"
    pmid = str(row.get("pmid") or "")
    epmc, source = row.get("europepmc") or {}, row.get("source") or {}
    if pmid and not re.fullmatch(r"\d+", pmid):
        raise ValueError("INVALID_PMID")
    if pmid:
        path = base / "_ft" / (pmid + ".txt")
        if path.is_file() and path.stat().st_size:
            return path.read_text(encoding="utf-8"), "PMC"
        index = base / "fulltext_index.json"
        entry = (_json(index).get(pmid) or {}) if index.is_file() else {}
        if entry.get("copy_licence") == "CC" and entry.get("sha256"):
            for path in sorted((ROOT / "cache").glob("*/ft_" + pmid + ".txt")):
                raw = path.read_bytes()
                if hashlib.sha256(raw).hexdigest() == entry["sha256"]:
                    return raw.decode("utf-8"), "PMC"
    doi = str(epmc.get("doi") or source.get("doi") or row.get("doi") or "").lower()
    if doi:
        key = hashlib.sha1(doi.encode("utf-8")).hexdigest()[:16]
        path = base / "_upw" / (key + ".txt")
        if path.is_file():
            return path.read_text(encoding="utf-8"), "UNPAYWALL"
    return "", None


def run(census_paths, labels):
    """CLI runtime only. Fail closed on malformed metadata or parser errors."""
    import g1_registry_fill as rf
    selected = {(r["slug"], r["label"]) for r in labels}
    if any(not re.fullmatch(r"[a-zA-Z0-9_-]+", slug) for slug, _ in selected):
        raise ValueError("INVALID_SLUG")
    census_names = {"phase3": "PHASE3_OPEN_CENSUS.json",
                    "phase3_registered": "PHASE3_OPEN_CENSUS_REGISTERED.json",
                    "phase3_companions": "PHASE3_OPEN_CENSUS_COMPANIONS.json"}
    rows = []
    seen = set()
    configs = {}
    for raw_path in census_paths:
        path = Path(raw_path)
        if path.is_dir():
            canonical = path.parent / census_names.get(path.name, "PHASE3_OPEN_CENSUS.json")
            files = [canonical] if canonical.is_file() else [path / (s + ".json")
                     for s in sorted({s for s, _ in selected}) if (path / (s + ".json")).is_file()]
            if not files:
                raise ValueError("CENSUS_NOT_FOUND")
        else:
            files = [path]
        for file in files:
            document = _json(file)
            for row in document["rows"]:
                slug = row.get("slug") or document.get("slug")
                if (slug, row["label"]) not in selected:
                    continue
                identity = (slug, row["label"], str(row.get("pmid") or ""))
                if identity in seen:
                    continue
                text, origin = _held_text(row)
                if not text.strip():
                    continue
                seen.add(identity)
                if slug not in configs:
                    configs[slug] = rf.config(slug)
                rows.append(dict(slug=_short(slug), label=_short(row["label"]),
                                 pmid=_short(row.get("pmid") or ""), origin=origin,
                                 **diagnose(text, configs[slug])))
    rows.sort(key=lambda r: (r["slug"], r["label"], r["pmid"]))
    counts = Counter((r["slug"], r["failure_class"]) for r in rows)
    summary = [dict(topic=s, failure_class=f, count=n) for (s, f), n in sorted(counts.items())]
    output = ROOT / "outputs" / "k_gap" / "registry_fill" / "TABLE_FAILURE_DIAG.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(dict(rows=rows, counts=summary), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("topic | failure_class | count")
    for row in summary:
        print(row["topic"], row["failure_class"], row["count"], sep=" | ")
    print("held_copies", len(rows), sep=" | ")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    cli = sub.add_parser("run")
    cli.add_argument("--census", nargs="+", action="extend", required=True)
    cli.add_argument("--labels", required=True)
    args = parser.parse_args(argv)
    try:
        labels = json.loads(args.labels) if args.labels.lstrip().startswith("[") else _json(Path(args.labels))
        if not isinstance(labels, list) or any(not isinstance(r, dict) or
                not isinstance(r.get("slug"), str) or not isinstance(r.get("label"), str) for r in labels):
            raise ValueError("INVALID_LABELS")
        return run(args.census, labels)
    except Exception:  # Do not leak exception messages containing source text.
        print("DIAGNOSTIC_FAILED", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
