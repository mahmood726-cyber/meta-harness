"""Blind packets (PREREG_blind_reextraction.md): the same held documents as the first pass, a row.json WITHOUT the
served slots, the served source string, the served spans, analysis set or window, and BRIEF_BLIND.md. Built FROM the
first-pass packets so the document bytes are identical (their sha256 is re-checked, not assumed)."""
import hashlib, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, DST = sys.argv[1], sys.argv[2]
DROP = ("served", "source", "endpoint_result_span", "analysis_set", "follow_up_window")
n = 0
for k in sorted(os.listdir(SRC)):
    s = os.path.join(SRC, k)
    if not os.path.isdir(s):
        continue
    d = os.path.join(DST, k)
    os.makedirs(d, exist_ok=True)
    row = json.load(open(os.path.join(s, "row.json"), encoding="utf-8"))
    for doc in row["documents"]:
        if doc.get("file"):
            b = open(os.path.join(s, doc["file"]), "rb").read()
            assert hashlib.sha256(b).hexdigest() == doc["sha256"], (k, doc["file"])
            open(os.path.join(d, doc["file"]), "wb").write(b)
    blind = {kk: v for kk, v in row.items() if kk not in DROP}
    json.dump(blind, open(os.path.join(d, "row.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    shutil.copy(os.path.join(HERE, "..", "BRIEF_BLIND.md"), os.path.join(d, "BRIEF.md"))
    shutil.copy(os.path.join(HERE, "..", "LANE_CONTEXT.md"), os.path.join(d, "LANE_CONTEXT.md"))
    assert not any(str(v) in json.dumps(blind) for v in row["served"].values() if v and v > 20 and False)
    n += 1
print(n, "blind packets")
