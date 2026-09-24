"""Witness packets: each held-entry packet (../f4b/make_held_packets.py output) plus the acquired ClinicalTrials.gov
record(s) for the entry's registry id(s) (../registry/<NCT>.json), with WITNESS_BRIEF.md as the brief.

usage: python make_witness_packets.py <held jobs dir> <witness jobs dir> <held_ncts.json>"""
import hashlib, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TA = os.path.abspath(os.path.join(HERE, ".."))
src, dst, nct_map = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3], encoding="utf-8"))
acq = {a["nct"]: a for a in json.load(open(os.path.join(TA, "registry", "ACQUISITIONS.json"), encoding="utf-8"))}
os.makedirs(dst, exist_ok=True)
for job in sorted(os.listdir(src)):
    s = os.path.join(src, job)
    if not os.path.isdir(s):
        continue
    d = os.path.join(dst, job)
    os.makedirs(d, exist_ok=True)
    row = json.load(open(os.path.join(s, "row.json"), encoding="utf-8"))
    for doc in row["documents"]:
        if doc.get("file"):
            b = open(os.path.join(s, doc["file"]), "rb").read()
            assert hashlib.sha256(b).hexdigest() == doc["sha256"], (job, doc["file"])
            open(os.path.join(d, doc["file"]), "wb").write(b)
    reg = []
    for nct in nct_map.get(row["held_key"], []):
        a = acq.get(nct)
        if not a or a.get("status") != 200:
            continue
        b = open(os.path.join(TA, "registry", a["file"]), "rb").read()
        assert hashlib.sha256(b).hexdigest() == a["file_sha256"], nct
        name = f"doc_registry_{nct}.json"
        open(os.path.join(d, name), "wb").write(b)
        row["documents"].append({"file": name, "sha256": a["file_sha256"], "origin": f"evidence/typed_arms/registry/{a['file']}",
                                 "origin_sha256": a["file_sha256"], "acquired": {"url": a["url"], "retrieved_utc": a["retrieved_utc"]}})
        reg.append({"nct": nct, "file": name, "hasResults": a.get("hasResults"), "modules": a.get("modules")})
    row["registry_results"] = [r for r in reg if r["hasResults"]]
    row["registry_records_without_results"] = [r["nct"] for r in reg if not r["hasResults"]]
    json.dump(row, open(os.path.join(d, "row.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    shutil.copy(os.path.join(HERE, "WITNESS_BRIEF.md"), os.path.join(d, "BRIEF.md"))
    shutil.copy(os.path.join(TA, "LANE_CONTEXT.md"), os.path.join(d, "LANE_CONTEXT.md"))
    print(job[:52].ljust(52), [r["nct"] for r in row["registry_results"]])
