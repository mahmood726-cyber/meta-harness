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
    sp = os.path.join(ROOT, "evidence/second_adjudication/SUMMARY.json")
    if os.path.exists(sp):
        s2 = json.load(open(sp, encoding="utf-8"))
        ver2 = {k: v for k, v in s2.items() if not v["quote_errors"]}
        L += ["## Second, cross-family adjudication (codex / OpenAI family)", "",
              f"- rulings second-adjudicated: {len(s2)} of {len(adj)} (the highest-stakes: rejected candidates, entry rulings short of ESTABLISHED, confirmations that overrule a candidate or rest on a derivation)",
              f"- quotes verbatim in held bytes: {len(ver2)} of {len(s2)}",
              f"- number: " + ", ".join(f"{a} {b}" for a, b in sorted(collections.Counter(v['number'] for v in ver2.values()).items())) +
              f"; entry: " + ", ".join(f"{a} {b}" for a, b in sorted(collections.Counter(v['entry'] for v in ver2.values()).items())),
              "- each disagreement was tested against the source; resolutions: " + "; ".join(
                  f"{k}: {x['second_adjudication']['resolution']}" for k, x in sorted(adj.items()) if x.get("second_adjudication")), ""]
    swp = os.path.join(ROOT, "evidence/sweeps/entry_age_and_analysis_set.json")
    if os.path.exists(swp):
        sw = json.load(open(swp, encoding="utf-8"))["summary"]
        L += ["## Uniform sweeps (mechanical, all adjudicated rows; `evidence/sweeps/entry_age_and_analysis_set.json`)", "",
              f"- adult age floor, of {sw['age']['N']} rows whose question says 'adults': stated {sw['age']['STATED']}, "
              f"not stated {sw['age']['NOT_STATED']}, floor explicitly removed {sw['age'].get('FLOOR_REMOVED', 0)}",
              f"- served 'intention-to-treat' label, of {sw['served_itt_label']['N']} rows carrying it: supported by a span "
              f"{sw['served_itt_label']['SUPPORTED']}, contradicted by a span {sw['served_itt_label']['CONTRADICTED']}, "
              f"unsupported (no span states a set) {sw['served_itt_label']['UNSUPPORTED']} -- labels only; no number moves", ""]
    oq = [x for x in adj.values() if x.get("open_question")]
    L += [f"## Open questions for Mahmood: {len(oq)} (`evidence/OPEN_QUESTIONS.md`)", ""] + [f"- {x['key']}: {x['open_question'][:300]}" for x in oq] + [""]
    L += ["## Limits (stated so a clean count cannot imply more than it measured)", "",
          f"- Rulings are this lane's (Anthropic family); the extractor was codex (OpenAI family). A second, cross-family "
          f"adjudication covers only the highest-stakes subset (above); the remaining SERVED_CONFIRMED rulings rest on one "
          f"adjudicator plus the mechanical span and number gates.",
          "- 'Entry ESTABLISHED' means the trial's own text states an entry population inside the question. It is "
          "evidence for Mahmood's D04, not an admission; no route that admits a row exists or was created.",
          "- Most held sources are abstracts or registry records; open-access full text was held or acquired for a "
          "minority. 'Analysis set NOT STATED' usually means 'not in an abstract', not 'not in the paper'.",
          "- One source is held LOCAL-ONLY (not redistributable): URL and sha256 in evidence/LOCAL_ACQUISITIONS.json.", ""]
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1])
