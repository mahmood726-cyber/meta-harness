"""Offline census/replay. Only git read commands; never builds served pages."""
import json
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from harness import comparison_blinding, screen

PIN = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
BASE = "c15ed11156de6be09fe516cdf348aa247b07ea13"


def show(path, ref=PIN):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT).decode("utf-8")


def source_id(value):
    # Served IDs can be display labels, e.g. "PIONEER-HF · NCT02554890".
    # Extract only a terminal typed identifier, not incidental digits in names.
    match = re.search(r"(?:NCT\d{8}|(?<!\d)\d{7,8})$", str(value))
    return match.group() if match else str(value)


def measure():
    old = types.ModuleType("harness._comparison_baseline")
    old.__package__ = "harness"
    exec(compile(show("harness/screen.py", BASE), "screen@c15ed111", "exec"), old.__dict__)
    files = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", PIN], cwd=ROOT).decode().splitlines()
    topics = sorted(p for p in files if p.startswith("topics/") and p.endswith(".json"))
    candidates, changes, screened_changes, counts, missing = [], [], [], {}, []
    hashes = {}
    include_audit = dict(total=0, matched=0, unmatched=[], refused_by_comparison_gate=[])
    for path in topics:
        config = json.loads(show(path))
        slug = config["slug"]
        raw = show(f"cache/{slug}/records.json")
        hashes[slug] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        data = json.loads(raw)
        review_path = f"docs/reviews/{slug}/review.json"
        served = {}
        if review_path in files:
            served = {source_id(r["id"]): r for r in json.loads(show(review_path))["screening"]["records"]}
        else:
            missing.append(slug)
        counts[slug] = {kind: len(data[kind]) for kind in ("records", "ctgov")}
        source_ids = {str(r["id"]) for kind in ("records", "ctgov") for r in data[kind]}
        for rid, row in served.items():
            if row["decision"] == "include":
                include_audit["total"] += 1
                if rid in source_ids:
                    include_audit["matched"] += 1
                else:
                    include_audit["unmatched"].append(dict(topic=slug, id=rid))
        for kind in ("records", "ctgov"):
            for rec in data[kind]:
                text = " ".join(str(rec.get(k) or "") for k in
                                ("title", "abstract", "conditions", "interventions", "acronym"))
                # Deliberately broad candidate search; semantic adjudication is
                # documented separately. Masking fields are not text evidence.
                has_open = re.search(r"open[- ]label|unblind|unmask|non[- ]blind|not blind|not mask", text, re.I)
                has_blind = re.search(r"\b(?:double[- ]blind|blind(?:ed|ing)?|mask(?:ed|ing)?)\b", text, re.I)
                prev = old.screen_record(rec, config["include"], set(config.get("negative_control_pmids", [])))
                curr = screen.screen_record(rec, config["include"], set(config.get("negative_control_pmids", [])))
                served_row = served.get(str(rec["id"])) or served.get("NCT:" + str(rec["id"]))
                row = dict(topic=slug, kind=kind, id=rec["id"], title=rec["title"],
                           served=served_row, baseline=list(prev), current=list(curr))
                if served_row and served_row["decision"] == "include":
                    refusal = comparison_blinding.screening_refusal(rec, config["include"])
                    if refusal:
                        include_audit["refused_by_comparison_gate"].append(dict(row, refusal=refusal))
                degrees = (re.search(r"single[- ]blind|partially[- ]blind|partially[- ]mask", text, re.I)
                           and re.search(r"double[- ]blind|open[- ]label", text, re.I))
                if (has_open and has_blind) or degrees:
                    candidates.append(dict(row, abstract=rec.get("abstract", ""),
                                           reading=comparison_blinding.read_blinding(text)))
                if prev[:2] != curr[:2]:
                    screened_changes.append(row)
                    if served_row and served_row["decision"] == "include":
                        changes.append(row)
    return dict(pin=PIN, baseline=BASE, topic_count=len(topics), counts=counts, cache_sha256=hashes,
                total=sum(sum(x.values()) for x in counts.values()),
                candidates=candidates, screening_changes=screened_changes,
                served_include_changes=changes, served_include_audit=include_audit,
                missing_served_reviews=missing)


if __name__ == "__main__":
    result = measure()
    Path(__file__).with_name("measurement.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: len(v) if isinstance(v, list) else v for k, v in result.items()
                      if k not in ("counts", "cache_sha256")}, ensure_ascii=True, indent=2))
