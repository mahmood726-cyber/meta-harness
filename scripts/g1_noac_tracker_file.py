"""Write outputs/k_gap/g1/noac-vs-warfarin-af-stroke.json in the G1 tracker schema (kgap/G1_INTERFACES.md section 4),
from THIS branch's outputs/g1_noac/g1_noac.json, using the k-gap lane's own converter (scripts/g1_import_lanes.py ::
from_g1_noac) so the routes mean exactly what the tracker means: TWO_SOURCE_VERIFIED -> PRIMARY, anything else ->
UNVERIFIED with this lane's reasons kept. Requested by the k-gap lane (outputs/k_gap/DISPATCH_FROM_KGAP.md).

    python scripts/g1_noac_tracker_file.py
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import g1_import_lanes as gi  # noqa: E402
import g1_tracker as gt  # noqa: E402

SLUG = "noac-vs-warfarin-af-stroke"
SRC = os.path.join(ROOT, "outputs", "g1_noac", "g1_noac.json")


def main():
    lanes = json.load(open(gi.LANES, encoding="utf-8"))
    spec = dict(lanes[SLUG], format="g1_noac_v1", path="outputs/g1_noac/g1_noac.json")
    raw = open(SRC, "rb").read()
    T = json.load(open(os.path.join(gt.OUT, "k_gap_table.json"), encoding="utf-8"))
    o = gi.from_g1_noac(SLUG, json.loads(raw.decode("utf-8")), spec, T)
    import subprocess
    head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    o["lane_source"] = {"branch": spec["branch"], "commit": head, "path": spec["path"],
                        "format": "g1_noac_v1 -> tracker_v1", "sha256": hashlib.sha256(raw).hexdigest(),
                        "writer": "scripts/g1_noac_tracker_file.py",
                        "commit_note": "the HEAD this file was BUILT ON; the importer re-stamps lane_source from git"}
    p = os.path.join(gt.G1_DIR, f"{SLUG}.json")
    tmp = f"{p}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(o, fh, indent=1, ensure_ascii=False)
    os.replace(tmp, p)  # atomic: a killed run never leaves a partial tracker file
    print(json.dumps({k: o.get(k) for k in ("k_matched", "N_comparator_trials", "routes", "g1_status")}, indent=1))


if __name__ == "__main__":
    main()
