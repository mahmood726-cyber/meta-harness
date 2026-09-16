"""Sweep served reviews for publication records counted as missing trials.

This is intentionally offline: it reads served review artefacts plus committed cache files.

Examples:
  python scripts/publication_unit_sweep.py
  python scripts/publication_unit_sweep.py --ref aa8ed28a
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from copy import deepcopy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from harness import identity  # noqa: E402


def _load_json(path, ref=None):
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    if ref:
        data = subprocess.check_output(["git", "show", f"{ref}:{rel}"], cwd=ROOT)
        return json.loads(data.decode("utf-8"))
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_text(path, ref=None):
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    if ref:
        try:
            data = subprocess.check_output(["git", "show", f"{ref}:{rel}"], cwd=ROOT)
        except subprocess.CalledProcessError:
            return ""
        return data.decode("utf-8", errors="replace")
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _served_slugs():
    paths = glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "review.json"))
    return sorted(os.path.basename(os.path.dirname(p)) for p in paths)


def _norm_id(value):
    text = str(value or "").strip()
    if "·" in text:
        text = text.split("·")[-1].strip()
    if "Â·" in text:
        text = text.split("Â·")[-1].strip()
    text = text.replace("PMID ", "").replace("PMID:", "").strip()
    parts = text.split()
    return parts[-1] if parts else text


def _screened_in_not_pooled_records(review):
    pooled = {
        _norm_id(t.get("id") or t.get("label"))
        for outcome in review.get("outcomes") or []
        for t in outcome.get("trials") or []
        if _norm_id(t.get("id") or t.get("label"))
    }
    out = []
    for rec in ((review.get("screening") or {}).get("records") or []):
        if rec.get("decision") == "include" and _norm_id(rec.get("id")) not in pooled:
            out.append(rec)
    return out


def _companion_rows(slug, study_families):
    return list(((study_families.get("topics") or {}).get(slug)) or [])


def _record_rows(records):
    if isinstance(records, list):
        return records
    if not isinstance(records, dict):
        return []
    return list(records.get("records") or []) + list(records.get("ctgov") or [])


def _count_sentences(html):
    patterns = [
        r"Screened-in[^<]{0,180}",
        r"k = \d+:[^<]{0,220}",
        r"\d+ further screened-in trial\(s\)[^<]{0,120}",
    ]
    found = []
    for pattern in patterns:
        for match in re.findall(pattern, html):
            clean = re.sub(r"\s+", " ", match).strip()
            if clean and clean not in found:
                found.append(clean)
    return found[:4]


def sweep(ref=None):
    study_families = _load_json(os.path.join(ROOT, "docs", "study_families.json"))
    rows = []
    total_not_pooled = 0
    total_secondary = 0
    for slug in _served_slugs():
        review_path = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
        records_path = os.path.join(ROOT, "cache", slug, "records.json")
        html_path = os.path.join(ROOT, "docs", "reviews", slug, "index.html")
        try:
            review = _load_json(review_path, ref=ref)
        except (OSError, subprocess.CalledProcessError):
            continue
        try:
            records = _load_json(records_path)
        except OSError:
            records = {}
        annotated = deepcopy(review)
        identity.annotate_review(annotated, _record_rows(records), _companion_rows(slug, study_families))
        not_pooled = _screened_in_not_pooled_records(annotated)
        flagged = identity.classify_screened_in_not_pooled(annotated)
        total_not_pooled += len(not_pooled)
        total_secondary += len(flagged)
        if flagged:
            rows.append({
                "slug": slug,
                "screened_in_not_pooled_records": len(not_pooled),
                "flagged": flagged,
                "count_sentences": _count_sentences(_load_text(html_path, ref=ref)),
            })
    return {
        "source": ref or "current",
        "topics": len(_served_slugs()),
        "secondary_or_economic_publications": total_secondary,
        "screened_in_not_pooled_records": total_not_pooled,
        "rows": rows,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", help="optional git ref for served review/html artefacts")
    args = ap.parse_args(argv)
    result = sweep(ref=args.ref)
    print(
        "SWEEP source={source} topics={topics} secondary_or_economic_of_pooled="
        "{secondary_or_economic_publications} of screened_in_not_pooled_records="
        "{screened_in_not_pooled_records}".format(**result)
    )
    for row in result["rows"]:
        print(
            "{slug}: {n} flagged of {denom} screened-in-not-pooled records".format(
                slug=row["slug"],
                n=len(row["flagged"]),
                denom=row["screened_in_not_pooled_records"],
            )
        )
        for item in row["flagged"]:
            print(
                "  {id} family={trial_family_id} role={publication_role} state={publication_state}".format(
                    **item
                )
            )
        for sentence in row["count_sentences"]:
            print(f"  count_sentence: {sentence}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
