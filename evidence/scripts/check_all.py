"""The lane's one gate. Exit 0 only when (1) every held file matches its acquisition sha256, (2) every
adjudication's cited spans are still verbatim in the same bytes they were pinned to (same sha256), and (3) every
CANDIDATE_REJECTED ruling is still marked unlanded. Extraction records that fail verification are REPORTED
(they are candidates, not claims) but do not fail the gate; an adjudication is a claim and does."""
import json, os, re, sys, glob, hashlib
sys.path.insert(0, os.path.dirname(__file__))
import textrep, verify_records as V
ROOT = textrep.ROOT


def main():
    bad = []
    led = json.load(open(os.path.join(ROOT, "evidence/held/ACQUISITIONS.json"), encoding="utf-8"))
    for rel, m in led.items():
        p = os.path.join(ROOT, "evidence/held", rel)
        if not os.path.exists(p) or hashlib.sha256(open(p, "rb").read()).hexdigest() != m["sha256"]:
            bad.append(f"held file changed or missing: {rel}")
    local = json.load(open(os.path.join(ROOT, "evidence/LOCAL_ACQUISITIONS.json"), encoding="utf-8"))
    absent_local = []
    for rel, m in local.items():
        if rel.startswith("_"):
            continue
        p = os.path.join(ROOT, "evidence/held_local", rel)
        if not os.path.exists(p):
            absent_local.append(rel)
        elif hashlib.sha256(open(p, "rb").read()).hexdigest() != m["sha256"]:
            bad.append(f"local-only file changed: {rel}")
    adj = sorted(glob.glob(os.path.join(ROOT, "evidence/adjudication/*.json")))
    for p in adj:
        a = json.load(open(p, encoding="utf-8"))
        for path, pin in a.get("pinned_spans", {}).items():
            node = a
            for part in path.split("/"):
                node = node[part]
            if pin["ref"].startswith("evidence/held_local/") and pin["ref"][len("evidence/held_local/"):] in absent_local:
                continue   # not redistributable; named below, verifiable by re-fetch against the ledger sha256
            if V.file_sha(pin["ref"]) != pin["sha256"]:
                bad.append(f"{a['key']} {path}: source sha256 changed")
            elif node["span"] not in textrep.render(pin["ref"]):
                bad.append(f"{a['key']} {path}: span no longer verbatim in render")
        if a["ruling"] == "CANDIDATE_REJECTED" and a["notice"].get("state") != "QUEUED_FOR_MAHMOOD_SIGNATURE_NOT_LANDED":
            bad.append(f"{a['key']}: rejected candidate not marked unlanded")
    print(f"held files {len(led)}; adjudications {len(adj)}; refusals {len(bad)}; local-only files absent here: {len(absent_local)} {absent_local}")
    for b in bad:
        print("  REFUSED", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
