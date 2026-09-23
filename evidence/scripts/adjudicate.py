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


def confirm_check(d, served):
    """A confirmation must be checkable: the served numbers either equal the recorded derivation, or every served
    number is printed in the cited evidence spans. Returns None when it holds, else the reason."""
    keys = [k for k in ("effect", "ci_low", "ci_high") if served.get(k) is not None] or            [k for k in ("ai", "n1i", "ci", "n2i", "mean1", "sd1", "nc1", "mean2", "sd2", "nc2") if served.get(k) is not None]
    vals = [float(served[k]) for k in keys]
    if not vals:
        return "served row carries no number to confirm"
    der = (d.get("derivation") or {}).get("result")
    if der is not None:
        if len(der) != len(vals) or any(abs(a - b) > 5e-3 for a, b in zip(der, vals)):
            return f"derivation result {der} != served {vals}"
        return None
    toks = set()
    def walk(n):
        if isinstance(n, dict):
            if "span" in n: toks.update(V.num_tokens(n["span"]))
            else: [walk(v) for v in n.values()]
    walk(d.get("evidence"))
    fl = {float(t) for t in toks}
    missing = [v for v in vals if not any(abs(v - f) < 1e-9 for f in fl)]
    return f"served numbers {missing} are not printed in any cited span" if missing else None


def main(p):
    d = json.load(open(p, encoding="utf-8"))
    assert d["ruling"] in RULINGS, d["ruling"]
    packet = json.load(open(os.path.join(ROOT, f"evidence/packets/{d['key']}.json"), encoding="utf-8"))
    pinned, errs = check_spans(d, packet)
    if errs:
        print("REFUSED:", *errs, sep="\n  "); return 1
    if d["ruling"] == "SERVED_CONFIRMED":
        why = confirm_check(d, V.served_row(packet))
        if why:
            print("REFUSED:", why); return 1
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
