"""Value-bound human decisions for terminal reported/count discrepancies."""
from copy import deepcopy
import json
from pathlib import Path


def load(path=None):
    path = Path(path) if path is not None else Path(__file__).resolve().parents[1] / "registry/a7_adjudications.json"
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    for entry in data["adjudications"].values():
        if entry["decision"] != "POOL_COUNTS":
            raise ValueError(f"Unknown A7 adjudication decision: {entry['decision']!r}")
    return data


def resolve(slug, outcome_name, trial_id, typed):
    entry = load()["adjudications"].get(f"{slug}::{outcome_name}::{trial_id}")
    if entry is None:
        return None
    if entry["decision"] != "POOL_COUNTS":
        raise ValueError(f"Unknown A7 adjudication decision: {entry['decision']!r}")
    fields = {"reported": ("scale", "effect", "ci_low", "ci_high"),
              "count_derived": ("ai", "n1i", "ci", "n2i")}
    if any(key not in typed.get(section, {}) or key not in entry[section]
           or typed[section][key] != entry[section][key]
           for section, keys in fields.items() for key in keys):
        return {"state": "A7_ADJUDICATION_STALE",
                "reason": "Recorded A7 adjudication values differ from current extraction; refusal retained"}
    counts = typed["count_derived"]
    record = {key: deepcopy(typed[key]) for key in fields}
    record.update({key: entry[key] for key in ("decision", "decided_by", "date")})
    row = {key: counts[key] for key in fields["count_derived"]}
    row.update(source=counts["span"], provenance=typed["provenance"],
               reported_vs_count_derived=record, selection_rule="ADJUDICATED_POOL_COUNTS")
    return {"state": "ADJUDICATED_POOL_COUNTS", "row": row}
