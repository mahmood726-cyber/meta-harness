"""Attach every VERIFIED gap span (evidence/gaps/SUMMARY.json) to its row's adjudication draft as evidence
`gap_<field>` and re-submit through adjudicate.py (which re-verifies every span against the held bytes). A span
that did not verify is never attached. The ruling itself is not changed here; the sweeps read `gap_analysis_set`
before the extraction's `analysis_set`."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
import textrep
ROOT = textrep.ROOT


def main():
    s = json.load(open(os.path.join(ROOT, "evidence", "gaps", "SUMMARY.json"), encoding="utf-8"))
    done = 0
    for k, r in s.items():
        p = os.path.join(ROOT, "evidence", "adjudication", "drafts", f"{k}.json")
        d = json.load(open(p, encoding="utf-8"))
        changed = False
        for f in ("analysis_set", "follow_up", "entry_age", "entry_other"):
            v = r.get(f) or {}
            if v.get("state") == "VERIFIED":
                ev = {"ref": v["ref"], "span": v["span"]}
                if d["evidence"].get(f"gap_{f}") != ev:
                    d["evidence"][f"gap_{f}"] = ev; changed = True
                if f == "analysis_set":
                    d.setdefault("gap_scope", {})["analysis_set"] = v.get("scope")
        if changed:
            json.dump(d, open(p, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
            rc = subprocess.call([sys.executable, "-W", "ignore", os.path.join(ROOT, "evidence", "scripts", "adjudicate.py"), p])
            if rc:
                print("REFUSED", k); continue
            done += 1
    print("adjudications updated with verified gap spans:", done)


if __name__ == "__main__":
    main()
