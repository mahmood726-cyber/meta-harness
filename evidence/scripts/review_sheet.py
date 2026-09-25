"""Compact per-row sheet for hand adjudication: served row, each bound span, the extractor's entry reading and
mismatch note. Read-only."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import verify_records as V
ROOT = V.ROOT
for k in sys.argv[1:]:
    rec = json.load(open(os.path.join(ROOT, f"evidence/extractions/raw/{k}.json"), encoding="utf-8"))
    pk = json.load(open(os.path.join(ROOT, f"evidence/packets/{k}.json"), encoding="utf-8"))
    s = V.served_row(pk)
    v = V.verify(rec, pk)
    print(f"=== {k} {pk['slug']} {pk['trial']} | outcome: {pk['served_outcome']['name']} | tp: {pk['served_outcome'].get('timepoint')}")
    print("  served:", {x: s.get(x) for x in ("effect", "ci_low", "ci_high", "scale", "ai", "n1i", "ci", "n2i", "analysis_set") if s.get(x) is not None})
    print("  verify:", v["errors"] or "OK", (v["served_compare"] or {}).get("state"), rec.get("verdict"), rec.get("set_aside_reason"))
    for f in V.FIELDS:
        x = (rec.get("fields") or {}).get(f)
        print(f"  {f:18}", (x["ref"].split("/")[-1][:22] + ": " + x["span"][:230]) if x else "-- " + str((rec.get("absent_reason") if isinstance(rec.get("absent_reason"), dict) else {f: rec.get("absent_reason")}).get(f))[:150])
    e = rec.get("entry_population_matches_question") or {}
    print("  ENTRY:", e.get("value"), "|", (e.get("why") or "")[:250])
    print("  MISMATCH:", (rec.get("served_mismatch") or "")[:400])
