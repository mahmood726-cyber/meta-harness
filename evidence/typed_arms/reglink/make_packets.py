"""Registry-arm linkage packets: one job per ClinicalTrials.gov record WITH posted results whose count rows (held or
served) were owned from prose. The reader links each written arm to the registry's group objects (by JSON pointer)
and searches every results module for a measure of the row's outcome. Usage: make_packets.py <jobs_dir>"""
import glob, hashlib, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TA = os.path.abspath(os.path.join(HERE, ".."))
ACQ = {a["nct"]: a for a in json.load(open(os.path.join(TA, "registry", "ACQUISITIONS.json"), encoding="utf-8"))}
WJOBS = {"held": "C:/mh-lanes/evid2-codex/witness", "served": "C:/mh-lanes/evid2-codex/witness_served"}


def candidates():
    by = {}
    for pop, jobs in WJOBS.items():
        obs = json.load(open(os.path.join(TA, "v2", f"OBSERVATIONS_{pop}.json"), encoding="utf-8"))["rows"]
        k2 = {}
        for rj in glob.glob(jobs + "/*/row.json"):
            r = json.load(open(rj, encoding="utf-8"))
            k2[r.get("held_key") or r.get("row_id")] = r
        for k, row in sorted(obs.items()):
            if all(o["group_id"] is not None for o in row["observations"]):
                continue
            docs = k2.get(k, {}).get("documents", [])
            for n in sorted({m.group(0) for d in docs for m in [re.search(r"NCT\d{8}", d["file"])] if m and "registry" in d["file"]}):
                if ACQ.get(n, {}).get("hasResults"):
                    by.setdefault(n, []).append({"population": pop, "row_key": k, "outcome": row["observations"][0]["outcome"],
                        "arms": [{"role": o["role"], "arm_name": o["arm_name"], "events": o["events"], "total": o["total"]}
                                 for o in row["observations"]]})
    return by


def main(out):
    by = candidates()
    for n, rows in sorted(by.items()):
        j = os.path.join(out, n)
        os.makedirs(j, exist_ok=True)
        src = os.path.join(TA, "registry", f"{n}.json")
        shutil.copyfile(src, os.path.join(j, f"registry_{n}.json"))
        json.dump({"nct": n, "registry_file": f"registry_{n}.json",
                   "registry_sha256": hashlib.sha256(open(src, "rb").read()).hexdigest(), "rows": rows},
                  open(os.path.join(j, "rows.json"), "w", encoding="utf-8"), indent=1)
    print(len(by), "registrations,", sum(len(v) for v in by.values()), "rows")


if __name__ == "__main__":
    main(sys.argv[1])
