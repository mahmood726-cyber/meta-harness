"""Write one lane adjudication, refusing it unless every span it cites verifies against the packet's sources
(same textrep.render, same sha256 pinning as verify_records). Usage: python adjudicate.py <draft.json>
Rulings:
  SERVED_CONFIRMED            the served number is what the authentic source states for this endpoint/population
  CANDIDATE_REJECTED          the served number is not the source's number for this endpoint; the correct span is
                              bound in `correct` and a derived notice is queued (never landed unsigned)
  SET_ASIDE                   no authentic span can be bound; `reason_code` names why
"""
import json, os, re, sys, datetime
sys.path.insert(0, os.path.dirname(__file__))
import textrep, verify_records as V
ROOT = textrep.ROOT
RULINGS = ("SERVED_CONFIRMED", "CANDIDATE_REJECTED", "SET_ASIDE")


def check_spans(d, packet):
    allowed = {s["ref"] for s in packet["sources"]}
    pinned, errs = {}, []
    def walk(node, path):
        if isinstance(node, dict):
            if "ref" in node and "span" in node:
                if node["ref"] not in allowed:
                    errs.append(f"{path}: ref not in packet")
                    return
                offs = [m.start() for m in re.finditer(re.escape(node["span"]), textrep.render(node["ref"]))]
                if not offs:
                    errs.append(f"{path}: span not verbatim in render({node['ref']})")
                else:
                    pinned[path] = {"ref": node["ref"], "sha256": V.file_sha(node["ref"]), "offsets": offs}
                return
            for k, v in node.items():
                walk(v, f"{path}/{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}/{i}")
    walk(d.get("evidence"), "evidence")
    return pinned, errs


def main(p):
    d = json.load(open(p, encoding="utf-8"))
    assert d["ruling"] in RULINGS, d["ruling"]
    packet = json.load(open(os.path.join(ROOT, f"evidence/packets/{d['key']}.json"), encoding="utf-8"))
    pinned, errs = check_spans(d, packet)
    if errs:
        print("REFUSED:", *errs, sep="\n  "); return 1
    if d["ruling"] == "CANDIDATE_REJECTED":
        assert d.get("proposed_row") and d.get("notice"), "a rejected candidate needs a proposed row and a derived notice"
        d["notice"]["state"] = "QUEUED_FOR_MAHMOOD_SIGNATURE_NOT_LANDED"
    d["served_row_at_adjudication"] = V.served_row(packet)
    d["pinned_spans"] = pinned
    d.setdefault("by", "Claude Opus 5.5 (evidence lane evid/evidence-records)")
    d.setdefault("when_utc", datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z")
    os.makedirs(os.path.join(ROOT, "evidence/adjudication"), exist_ok=True)
    json.dump(d, open(os.path.join(ROOT, f"evidence/adjudication/{d['key']}.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("WRITTEN", d["key"], d["ruling"], f"{len(pinned)} spans pinned"); return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
