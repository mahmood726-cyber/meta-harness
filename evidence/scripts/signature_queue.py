"""Render every CANDIDATE_REJECTED adjudication as a derived notice awaiting Mahmood's signature. Nothing here is
landed on a served page; the queue is the hand-off. Each block's sha256 is printed so a signature can name the
exact bytes that were shown."""
import json, os, glob, hashlib, sys
sys.path.insert(0, os.path.dirname(__file__))
import textrep
ROOT = textrep.ROOT


def block(a):
    n = a["notice"]
    lines = [f"### {a['key']}: {n['slug']} / {n['outcome']} / {n['trial']}",
             f"- state: {n['state']}",
             f"- served now: {n['before_row']}",
             f"- proposed (derived, unsigned): {n['after_row']}",
             f"- pooled effect: {n['pooled_effect']}",
             f"- mechanism: {n['mechanism']}",
             f"- reason: {a['reason']}",
             "- evidence (verbatim, re-verified against held bytes when the adjudication was written):"]
    for k, v in a["evidence"].items():
        lines.append(f"  - {k}: `{v['ref']}` (sha256 {a['pinned_spans']['evidence/' + k]['sha256'][:12]}): \"{v['span']}\"")
    return "\n".join(lines) + "\n"


def main():
    rows = [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(os.path.join(ROOT, "evidence/adjudication/*.json")))]
    rej = [a for a in rows if a["ruling"] == "CANDIDATE_REJECTED"]
    out = ["# Signature queue: served numbers the evidence lane proposes to change (NONE LANDED)\n",
           f"{len(rej)} of {len(rows)} adjudicated rows reject the served candidate. Each block is DERIVED and UNSIGNED. "
           "A served number moves only after Mahmood signs the block's sha256 and a rebuild runs.\n"]
    for a in rej:
        b = block(a)
        out.append(b + f"- block sha256: {hashlib.sha256(b.encode('utf-8')).hexdigest()}\n")
    open(os.path.join(ROOT, "evidence/SIGNATURE_QUEUE.md"), "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print(f"queued {len(rej)} of {len(rows)} adjudications")


if __name__ == "__main__":
    main()
