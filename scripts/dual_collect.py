"""Merge the Fable-written span-map files scratchpad/dual_out_*.json into scratchpad/dual_spans.json.
Each lane writes its own JSON {key: span}; this just merges them (reliable, no transcript parsing)."""
import glob
import json
import os
import sys

SCRATCH = sys.argv[1]
merged = {}
for p in sorted(glob.glob(os.path.join(SCRATCH, "dual_out_*.json"))):
    try:
        d = json.load(open(p, encoding="utf-8"))
        if isinstance(d, dict):
            merged.update(d)
    except Exception as e:
        print("skip", os.path.basename(p), repr(e)[:60])
json.dump(merged, open(os.path.join(SCRATCH, "dual_spans.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("merged", len(merged), "spans from", len(glob.glob(os.path.join(SCRATCH, "dual_out_*.json"))), "files")
