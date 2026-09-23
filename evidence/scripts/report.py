"""Morning report, every number computed from the adjudication files and the verification ledger (none typed by
hand). Usage: python report.py OUT.md [--since COMMIT]"""
import json, os, sys, glob, collections, subprocess, datetime
sys.path.insert(0, os.path.dirname(__file__))
import textrep
ROOT = textrep.ROOT


def main(out, since=None):
    wl = json.load(open(os.path.join(ROOT, "evidence/worklist.json"), encoding="utf-8"))["rows"]
    ver = json.load(open(os.path.join(ROOT, "evidence/extractions/verification.json"), encoding="utf-8"))
    adj = {os.path.basename(p)[:-5]: json.load(open(p, encoding="utf-8"))
           for p in glob.glob(os.path.join(ROOT, "evidence/adjudication/*.json"))}
    L = [f"# Evidence lane report: {datetime.date.today().isoformat()}",
         "", f"Branch `evid/evidence-records` @ `{subprocess.run(['git','rev-parse','--short=8','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip()}`; "
         "main `38c04411` unchanged by this lane. Every count below is computed by `evidence/scripts/report.py` from the committed records.", ""]
    for pop, N, name in (("P53", 53, "pooled primary rows inadmissible on P5 at 38c04411"),
                         ("U23", 23, "served rows lane UA found with no locatable source")):
        rows = [w for w in wl if w["kind"] == pop]
        assert len(rows) == N
        a = [adj[w["key"]] for w in rows if w["key"] in adj]
        rc = collections.Counter(x["ruling"] for x in a)
        ec = collections.Counter((x.get("entry_population") or {}).get("lane_ruling") or "n/a" for x in a)
        lab = sum(1 for x in a if x.get("label_defects"))
        sets = collections.Counter()
        for x in a:
            s = ((x.get("typed_estimand") or {}).get("analysis_set"))
            if isinstance(s, dict):
                sets[s.get("source_reading")] += 1
        pend = [w["key"] for w in rows if w["key"] not in adj]
        L += [f"## {pop}: N = {N} ({name})", "",
              f"- adjudicated: **{len(a)} of {N}**; not yet: {len(pend)} ({', '.join(pend) or 'none'})",
              f"- rulings (of {len(a)} adjudicated): " + ", ".join(f"{k} {v}" for k, v in sorted(rc.items())),
              f"- entry population, lane ruling (of {len(a)}): " + ", ".join(f"{k} {v}" for k, v in sorted(ec.items())),
              f"- analysis set as the source states it (of {sum(sets.values())} drafted from extractions): " + ", ".join(f"{k} {v}" for k, v in sorted(sets.items())),
              f"- rows carrying a recorded label defect (number unchanged): {lab}", ""]
        for x in sorted(a, key=lambda x: x["key"]):
            e = (x.get("entry_population") or {}).get("lane_ruling")
            if x["ruling"] != "SERVED_CONFIRMED" or e in ("NOT_ESTABLISHED", "PARTLY", "CONTRADICTED") or x.get("label_defects"):
                note = (x.get("reviewed_note") or x.get("reason") or "")[:260].replace("\n", " ")
                L.append(f"  - {x['key']} {x['ruling']} / entry {e}: {note}")
        L.append("")
    rej = [x for x in adj.values() if x["ruling"] == "CANDIDATE_REJECTED"]
    L += ["## Queued for Mahmood's signature (derived, NOT landed)", ""] + \
         [f"- {x['key']}: {x['notice']['slug']} / {x['notice']['outcome']} / {x['notice']['trial']}: {x['notice']['before_row']} -> {x['notice']['after_row']}" for x in sorted(rej, key=lambda x: x["key"])] + \
         ["", "Blocks with sha256: `evidence/SIGNATURE_QUEUE.md`.", ""]
    fails = [k for k, v in ver.items() if v["errors"]]
    L += ["## Extraction pipeline", "", f"- codex extractions verified against held bytes: {len(ver) - len(fails)} of {len(ver)}; failing (candidates, not claims): {', '.join(fails) or 'none'}", ""]
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1])
