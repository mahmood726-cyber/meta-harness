"""Repair a lane log whose lines were split by concurrent appends (before reproducible_ai.model_call_live.log_call was
serialised, 6 Oct): a line that is not one whole JSON object is REMOVED from the log and RECORDED -- position, length,
sha256 and its bytes -- in '<log>.repairs.json', so nothing is dropped silently. A split line's head and tail cannot be
re-joined (tested: no line + fragment parses); the record files themselves (registry/model_calls/mc-*.json) are intact.

  python scripts/g1_lane_log_repair.py registry/model_calls/lane_log/search-screen-audit.jsonl
"""
import datetime
import hashlib
import json
import sys


def main(p):
    b = open(p, "rb").read()
    keep, removed = [], []
    for i, x in enumerate(b.split(b"\n")):
        if not x.strip():
            continue
        try:
            json.loads(x)
            keep.append(x)
        except ValueError:
            removed.append({"line_index": i, "bytes": len(x), "sha256": hashlib.sha256(x).hexdigest(),
                            "text": x.decode("utf-8", "replace")})
    rp = p + ".repairs.json"
    try:
        log = json.load(open(rp, encoding="utf-8"))
    except FileNotFoundError:
        log = []
    if removed:
        log.append({"repaired_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "why": "line not one whole JSON object (split by concurrent appends before log_call was serialised)",
                    "removed": removed})
        open(p, "wb").write(b"\n".join(keep) + b"\n")
        json.dump(log, open(rp, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(f"kept {len(keep)} lines, removed {len(removed)}")


if __name__ == "__main__":
    main(sys.argv[1])
