"""Read-only census of the pinned operational cache (not superseded search snapshots)."""
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from harness.arm_parse import regimen_frequencies, parse_regimen

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"


def measure(ref=PINNED):
    paths = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", ref, "cache"], cwd=ROOT).decode().splitlines()
    paths = [p for p in paths if p.count("/") == 2 and p.endswith(("/records.json", "/dose_selection.json"))]
    data = subprocess.check_output(["git", "cat-file", "--batch"], cwd=ROOT,
                                  input="".join(f"{ref}:{p}\n" for p in paths).encode())
    offset = 0
    counts = {"records": 0, "ctgov": 0, "record_files": 0}
    candidates, selections = [], []
    for path in paths:
        end = data.index(b"\n", offset)
        size = int(data[offset:end].split()[-1])
        obj = json.loads(data[end + 1:end + 1 + size])
        offset = end + 2 + size
        if path.endswith("dose_selection.json"):
            for rid, entry in obj.items():
                selections.append({"path": path, "id": rid, "dose": entry["dose"],
                                   "frequency": parse_regimen(entry["dose"])["frequency"]})
            continue
        counts["record_files"] += 1
        for section in ("records", "ctgov"):
            rows = obj.get(section) or []
            counts[section] += len(rows)
            for r in rows:
                text = (r.get("abstract") or "") + " " + "; ".join(r.get("interventions") or [])
                # 'weekly visits'/'daily diary' are deliberately overcaptured for manual adjudication.
                frequencies = regimen_frequencies(text)
                for code, pattern in {
                    "TWICE_WEEKLY": r"\btwice[ -]weekly\b",
                    "MONTHLY": r"\bmonthly\b|\bevery month\b",
                    "EVERY_3_MONTHS": r"\bevery (?:3|three) months\b",
                }.items():
                    if re.search(pattern, text, re.I):
                        frequencies.add(code)
                if len(frequencies) > 1:
                    candidates.append({"path": path, "section": section, "id": r["id"],
                                       "title": r.get("title"), "frequencies": sorted(frequencies),
                                       "nct": r.get("nct"),
                                       "abstract": r.get("abstract"), "interventions": r.get("interventions")})
    return {"ref": ref, "scope": "cache/*/records.json and cache/*/dose_selection.json",
            "counts": counts, "dose_selections": selections, "candidates": candidates}


if __name__ == "__main__":
    result = measure()
    (Path(__file__).parent / "census.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"counts": result["counts"], "candidate_count": len(result["candidates"]),
                      "candidates": [[r["path"].split("/")[1], r["id"], r["title"]] for r in result["candidates"]]}))
