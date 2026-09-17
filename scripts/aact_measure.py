"""Explicit offline measurement: python scripts/aact_measure.py [<slug> ...].

No arguments measures every live topic. AACT_DIR selects the source snapshot.
Snapshot table rows are scanned once per batch and never opened during replay.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import aact, armcontrast, funding, pipeline, screen
from harness.canonical import canonical_json, sha256_text

TABLES = ("studies", "sponsors", "responsible_parties", "design_groups",
          "interventions", "design_group_interventions")
REQUIRED_COLUMNS = {
    "studies": {"nct_id", "start_date", "completion_date", "primary_completion_date",
                "study_first_submitted_date", "results_first_posted_date", "overall_status"},
    "sponsors": {"id", "nct_id", "agency_class", "lead_or_collaborator", "name"},
    "responsible_parties": {"id", "nct_id", "responsible_party_type", "name", "title",
                            "organization", "affiliation", "old_name_title"},
    "design_groups": {"id", "nct_id"},
    "interventions": {"id", "nct_id", "name"},
    "design_group_interventions": {"nct_id", "design_group_id", "intervention_id"},
}


def topic_ncts(slug):
    records = json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8"))
    config = json.loads((ROOT / "topics" / (slug + ".json")).read_text(encoding="utf-8"))
    merged = pipeline._dedup(records, config.get("pivotal_trials"))
    recs = {str(r["id"]): r for r in merged}
    ncts = {screen._nct_id(r) for r in merged if screen._nct_id(r)}
    # Funding may use a trial's explicit registry linkage; use identifiers only,
    # never published numerical results as measurement inputs.
    path = ROOT / "docs" / "reviews" / slug / "review.json"
    if path.exists():
        for trial in funding._pooled_trials(json.loads(path.read_text(encoding="utf-8"))):
            raw = str(trial.get("id", "")).replace("PMID ", "").strip()
            nct = funding._trial_nct(raw, trial, recs.get(raw) or {})
            if nct:
                ncts.add(nct)
    return sorted(ncts)


def measure(slugs):
    snapshot = aact.snapshot_dir()
    if not snapshot or any(not (Path(snapshot) / (t + ".txt")).is_file() for t in TABLES):
        raise ValueError("AACT_NOT_MEASURED: complete local snapshot required; caches unchanged")
    for table, required in REQUIRED_COLUMNS.items():
        with (Path(snapshot) / (table + ".txt")).open(encoding="utf-8") as source:
            columns = set(source.readline().rstrip("\n").split("|"))
        if missing := required - columns:
            raise ValueError(f"AACT_NOT_MEASURED: {table} missing columns {sorted(missing)}; caches unchanged")
    topics = {slug: topic_ncts(slug) for slug in slugs}
    want = set().union(*(set(ns) for ns in topics.values()))
    provenance = {t: [] for t in TABLES}
    original_rows = aact._iter_rows

    def measured_rows(path):
        table = Path(path).stem
        for row in original_rows(path):
            if (row.get("nct_id") or "").upper() not in want:
                continue
            provenance[table].append({
                "keys": {k: row[k] for k in ("nct_id", "id", "design_group_id", "intervention_id") if k in row},
                "sha256": sha256_text(canonical_json(row)),
            })
            yield row

    # Instrument the original measure-time adapters, retaining their exact
    # transformations and row order. This patch exists only inside this script.
    with patch.object(aact, "_iter_rows", measured_rows):
        dates = aact.study_dates(want)
        sponsors = aact.sponsor_records(want)
        arms = armcontrast.measure_arm_index(want)
    for slug, ncts in topics.items():
        ids = set(ncts)
        doc = {
            "version": 1, "slug": slug, "status": "MEASURED",
            "snapshot": Path(snapshot).name,
            "row_hash_method": "sha256(canonical_json(header-keyed source row)); UTF-8",
            "requested_ncts": ncts,
            "source_rows": {t: [r for r in rows if r["keys"]["nct_id"].upper() in ids]
                            for t, rows in provenance.items()},
            "values": {
                "study_dates": {n: dates[n] for n in ncts if n in dates},
                "sponsors": {n: sponsors[n] for n in ncts if n in sponsors},
                "arm_index": {n: [sorted(arms[n][0]), sorted(arms[n][1])] for n in ncts if n in arms},
            },
        }
        doc["sha256"] = sha256_text(canonical_json(doc))
        path = ROOT / "cache" / slug / "aact_inputs.json"
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="")
        print(f"MEASURED {slug}: {len(ncts)} requested NCT identifiers; snapshot {doc['snapshot']}", flush=True)
    print(f"MEASURED {len(topics)} of {len(slugs)} requested topics", flush=True)


if __name__ == "__main__":
    measure(sys.argv[1:] or sorted(p.name for p in (ROOT / "docs" / "reviews").iterdir()
                                  if (p / "review.json").is_file()))
