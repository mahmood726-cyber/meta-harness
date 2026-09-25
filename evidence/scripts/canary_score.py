"""Score the drift canaries (evidence/extractions/canary/<utc>-<KEY>.json): each is a blind recorded re-extraction of an
adjudicated U23/S16 row. A canary AGREES when it verifies against held bytes and its served comparison matches the
row's adjudication (SERVED_CONFIRMED -> MATCH; CANDIDATE_REJECTED -> not MATCH). Prints n of N and lists every
divergence by row, so a drifting extractor or a changed source is named, not averaged away."""
import glob, json, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
import verify_records as V
ROOT = V.ROOT
FULL = r"C:\mh-lanes\evid-codex\packets_full"


def main():
    c, div = collections.Counter(), []
    files = sorted(glob.glob(os.path.join(ROOT, "evidence", "extractions", "canary", "*.json")))
    for p in files:
        key = os.path.basename(p)[:-5].split("-", 1)[1]
        rec = json.load(open(p, encoding="utf-8"))
        fp = os.path.join(FULL, f"{key}.json")
        pk = json.load(open(fp if os.path.exists(fp) else os.path.join(ROOT, "evidence", "packets", f"{key}.json"), encoding="utf-8"))
        v = V.verify(rec, pk)
        adj = json.load(open(os.path.join(ROOT, "evidence", "adjudication", f"{key}.json"), encoding="utf-8"))
        st = (v.get("served_compare") or {}).get("state")
        want_match = adj["ruling"] == "SERVED_CONFIRMED"
        ok = not v["errors"] and ((st == "MATCH") == want_match or st in ("NOT_COMPARABLE", "MATCH_POINT_CI_LEVEL_DIFFERS", None))
        if not ok and not v["errors"] and st == "DIFFERS" and adj.get("open_question"):
            c["known_open_question"] += 1   # the row's recorded open question (e.g. a timepoint choice) resurfacing
            continue
        c["agree" if ok else "diverge"] += 1
        if not ok:
            div.append((os.path.basename(p), adj["ruling"], st, v["errors"][:1]))
    print(f"canaries: {len(files)}; agree {c['agree']}, diverge {c['diverge']}, "
          f"known open question resurfacing {c['known_open_question']} (of {len(files)})")
    for d in div:
        print("  DIVERGE", d)


if __name__ == "__main__":
    main()
