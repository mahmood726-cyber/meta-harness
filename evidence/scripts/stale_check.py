"""Has main changed a served row since the lane ruled on it? Every adjudication records the served row it judged
(served_row_at_adjudication); this compares that record with the row the served tree holds NOW at the packet's
json_ref. A ruling on a number that is no longer served is stale: it must be re-read, never carried forward.
Run after every main landing. Exit 1 if any row changed or its json_ref no longer resolves to the same trial."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import verify_records as V
ROOT = V.ROOT
FIELDS = ("effect", "ci_low", "ci_high", "scale", "ai", "n1i", "ci", "n2i", "mean1", "sd1", "mean2", "sd2",
          "m1i", "sd1i", "m2i", "sd2i", "analysis_set")


def resolve(ref):
    f, _, ptr = ref.partition("#")
    o = json.load(open(os.path.join(ROOT, f), encoding="utf-8"))
    for part in ptr.strip("/").split("/"):
        o = o[int(part)] if isinstance(o, list) else o[part]
    return o


def diff(then, now, trial):
    d = {f: [then.get(f), now.get(f)] for f in FIELDS if f in then and then.get(f) != now.get(f)}
    if str(now.get("id")) != str(trial):
        d["id"] = [trial, now.get("id")]
    return d


def main():
    stale = {}
    files = sorted(glob.glob(os.path.join(ROOT, "evidence/adjudication/*.json")))
    for p in files:
        a = json.load(open(p, encoding="utf-8"))
        pk = json.load(open(os.path.join(ROOT, f"evidence/packets/{a['key']}.json"), encoding="utf-8"))
        try:
            d = diff(a.get("served_row_at_adjudication") or {}, resolve(pk["json_ref"]), pk["trial"])
        except (KeyError, IndexError, ValueError, OSError) as e:
            d = {"json_ref": f"no longer resolves: {e!r}"[:160]}
        if d:
            stale[a["key"]] = d
    print(f"adjudications {len(files)}; served row unchanged since the ruling {len(files) - len(stale)}; STALE {len(stale)}")
    for k, d in stale.items():
        print("  STALE", k, json.dumps(d, ensure_ascii=False)[:300])
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
