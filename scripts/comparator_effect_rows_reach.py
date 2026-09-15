"""Whose limit is "per-trial effects machine-readable on 0 of 21"? Theirs (figures only) or ours (parse reach)?

For every cached comparator full text, count table rows that carry a per-trial effect with a confidence interval
(an effect-with-CI pattern beside an author-year token) that the correctness sweep did NOT parse. A comparator with
such rows is PARSE_LIMIT (ours); one with none in any table is FIGURE_ONLY (theirs: per-trial effects live in the
forest-plot figure); one with no full text obtained is NOT_OBSERVED (ours: fetch reach). Written to
docs/evidence/comparator-correctness-2026-09-15/05-effect-rows-reach.txt; every row named with its counts.
"""
from __future__ import annotations
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "evidence", "comparator-correctness-2026-09-15", "05-effect-rows-reach.txt")
EFFECT = re.compile(r"\d\.\d{1,3}\s*[\(\[]\s*\d\.\d{1,3}\s*(?:to|–|-|,)\s*\d\.\d{1,3}\s*[\)\]]|95%\s*CI")
AUTHOR_YEAR = re.compile(r"[A-Z][a-z]+\s+(?:et al|\d{4})")


def assess(pmid_dir: str) -> tuple[str, int, int, int, list[str]]:
    xml = [f for f in glob.glob(os.path.join(pmid_dir, "*fulltext*.xml")) + glob.glob(os.path.join(pmid_dir, "*pmc_oai*.xml"))
           if os.path.getsize(f) > 2000]
    if not xml:
        return "NOT_OBSERVED", 0, 0, 0, []
    text = open(xml[0], encoding="utf-8", errors="replace").read()
    tables = re.findall(r"<table-wrap.*?</table-wrap>", text, flags=re.S)
    figures = len(re.findall(r"<fig\b", text))
    hits: list[str] = []
    for table in tables:
        for row in re.findall(r"<tr.*?</tr>", table, flags=re.S):
            flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", row)).strip()
            if EFFECT.search(flat) and AUTHOR_YEAR.search(flat):
                hits.append(flat[:200])
    verdict = "PARSE_LIMIT_CANDIDATE" if hits else "FIGURE_ONLY"
    return verdict, len(tables), figures, len(hits), hits


def main() -> int:
    lines = ["Whose limit is 'per-trial effects machine-readable on 0 of 21'?",
             "Method: for each cached comparator full text (JATS), every <table-wrap> row is scanned for an effect-with-CI pattern beside an",
             "author-year token; such a row is a per-trial effect row our sweep did not parse (PARSE_LIMIT, ours). None in any table ->",
             "FIGURE_ONLY (theirs: the forest plot is a figure). No full text obtained -> NOT_OBSERVED (ours: fetch reach). Each row is named.",
             "", "pmid | verdict | tables | figures | candidate effect rows | candidate row text"]
    counts: dict[str, int] = {}
    for d in sorted(glob.glob(os.path.join(ROOT, "cache", "comparators", "*"))):
        if not os.path.isdir(d):
            continue
        pmid = os.path.basename(d)
        verdict, n_tables, n_fig, n_hits, hits = assess(d)
        counts[verdict] = counts.get(verdict, 0) + 1
        lines.append(f"{pmid} | {verdict} | {n_tables} | {n_fig} | {n_hits} | {' || '.join(hits) if hits else '-'}")
    lines += ["", "TOTALS: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
              "Reading: a PARSE_LIMIT_CANDIDATE row is shown verbatim so a reader can judge whether it is a per-trial effect row",
              "(ours to parse) or a characteristics row with confidence intervals (not an effect row). NOT_OBSERVED comparators",
              "say nothing about the paper: the limit is our fetch."]
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("effect-rows reach: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
