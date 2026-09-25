"""REHEARSAL ONLY: write a verdict file for judgement B3 on the rehearsal sign branch, bound to the anchors
notice_rejudge will pin. Labelled synthetic: no reader read anything; used only to exercise the pipeline."""
import json
import sys
from pathlib import Path

T = Path(r"C:/mh-lanes/nr/rehwt")
sys.path.insert(0, str(T))
from scripts import notice_anchor as anchor  # noqa: E402
from scripts import notice_rejudge as rj  # noqa: E402

served, proposed = sys.argv[1], sys.argv[2]
checks = {c["audit_id"]: c for c in json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))["checks"]}
audit = json.loads(rj.AUDIT.read_text(encoding="utf-8"))
out = []
for row in audit["notices"]:
    anchors = rj.anchors_for(row, served, proposed)
    if row["audit_id"] in audit.get("specific_conflicts", {}):
        anchors.append(anchor.make(rj.ROOT, "held", proposed, audit["specific_conflicts"][row["audit_id"]]["cache_path"]))
    c = checks[row["audit_id"]]
    out.append({"audit_id": row["audit_id"], "anchors": {a["ref"]: a["sha256"] for a in anchors},
                "bulk_reader": "REHEARSAL-SYNTHETIC (no reader)", "bulk_verdict": "HOLDS", "lane_verdict": "HOLDS",
                "lane_notes": "REHEARSAL-SYNTHETIC", "defects": [],
                "before_after": f"{row['before']} -> {row['after']}", "rendered_block_sha256": c["rendered_block_sha256"],
                "departure_binding": []})
Path(sys.argv[4]).write_text(json.dumps({"served": served, "proposed": proposed, "verdicts": out}), encoding="utf-8")
print(len(out), "verdicts")
