"""The lane's one gate. Exit 0 only when (1) every held file matches its acquisition sha256, (2) every
adjudication's cited spans are still verbatim in the same bytes they were pinned to (same sha256), and (3) every
CANDIDATE_REJECTED ruling is still marked unlanded, and (4) the served row each ruling judged is still the row the
served tree holds (a ruling on a number main has since changed is stale), and (5) the derived owner-facing files
equal their regeneration. Extraction records that fail verification are REPORTED
(they are candidates, not claims) but do not fail the gate; an adjudication is a claim and does."""
import json, os, re, sys, glob, hashlib
sys.path.insert(0, os.path.dirname(__file__))
import textrep, verify_records as V, stale_check
ROOT = textrep.ROOT


DERIVED = ("evidence/SIGNATURE_QUEUE.md", "evidence/OPEN_QUESTIONS.md", "evidence/LABEL_CORRECTIONS.md")


def derived_drift():
    """(5) The derived owner-facing files must equal what their generators produce from the committed records: a hand
    edit would be wiped on the next regeneration, and a stale file shows the owner a queue that no longer exists.
    Regenerate, compare bytes, and put the originals back either way (the gate never rewrites the tree)."""
    import contextlib, io, signature_queue, label_corrections
    before = {f: open(os.path.join(ROOT, f), "rb").read() for f in DERIVED}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            signature_queue.main(); label_corrections.main()
        return [f"{f}: differs from its regeneration (hand-edited or stale)"
                for f in DERIVED if open(os.path.join(ROOT, f), "rb").read() != before[f]]
    except SystemExit as e:
        return [f"derived files: a generator refused: {e}"]
    finally:
        for f, b in before.items():
            open(os.path.join(ROOT, f), "wb").write(b)


def decision_witnesses():
    """(6) Every witness in a result-level decision file (evidence/glp1_adjudication/<TRIAL>.json) still has the
    sha256 it was cut from and is still verbatim in that file's render."""
    out, n = [], 0
    files = glob.glob(os.path.join(ROOT, "evidence/glp1_adjudication/*.json")) + glob.glob(os.path.join(ROOT, "evidence/rob2_glp1/*.json"))
    for p in sorted(files):
        if os.path.basename(p) in ("BEFORE_AFTER.json", "SPEC.json", "SUMMARY.json"):
            continue
        stack = [json.load(open(p, encoding="utf-8"))]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                if "span" in o and "ref" in o and "sha256" in o:
                    n += 1
                    if o["ref"].startswith("evidence/held_local/") and not os.path.exists(os.path.join(ROOT, o["ref"])):
                        pass   # local-only, not redistributable: absent on a fresh clone; re-fetch from LOCAL_ACQUISITIONS
                    elif V.file_sha(o["ref"]) != o["sha256"]:
                        out.append(f"{os.path.basename(p)}: witness source changed: {o['ref']}")
                    elif o["span"] not in textrep.render(o["ref"]):
                        out.append(f"{os.path.basename(p)}: witness no longer verbatim in {o['ref']}")
                stack.extend(o.values())
            elif isinstance(o, list):
                stack.extend(o)
    return out


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
        pk = json.load(open(os.path.join(V.ROOT, f"evidence/packets/{a['key']}.json"), encoding="utf-8"))
        try:   # a ruling on a served row main has since changed is stale (evidence/scripts/stale_check.py)
            d = stale_check.diff(a.get("served_row_at_adjudication") or {}, stale_check.resolve(pk["json_ref"]), pk["trial"])
        except (KeyError, IndexError, ValueError, OSError) as e:
            d = {"json_ref": repr(e)[:120]}
        if d:
            bad.append(f"{a['key']}: served row changed since the ruling {json.dumps(d, ensure_ascii=False)[:200]}")
    bad += derived_drift()
    bad += decision_witnesses()
    print(f"held files {len(led)}; adjudications {len(adj)}; refusals {len(bad)}; local-only files absent here: {len(absent_local)} {absent_local}")
    for b in bad:
        print("  REFUSED", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
