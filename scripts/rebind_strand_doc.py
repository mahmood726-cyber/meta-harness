"""Rebind a strand doc written outside harness/strand_pool (pcsk9, sglt2-ckd: written by hand in earlier landings)
through the ONE strand path -- external review 11.

Each member's effect and interval are READ from its held source at the quote in registry/strand_member_quotes.json
(the quote must occur in the held text; a held full text is tag-stripped first). This script types no number. Pools
run synth.pool then the k=2 rule. Every other field of the doc is carried over unchanged.

    python scripts/rebind_strand_doc.py docs/pcsk9_mace_strands.json [--out PATH]     (default: overwrite the doc)
"""
import argparse
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import strand_pool as sp  # noqa: E402

QUOTES = os.path.join(ROOT, "registry", "strand_member_quotes.json")


def _held(root, slug, which):
    if which == "abstract":
        recs = json.load(open(os.path.join(root, "cache", slug, "records.json"), encoding="utf-8"))
        return {str(r.get("id")): r.get("abstract") or "" for r in recs.get("records") or []}
    return re.sub(r"<[^>]+>", " ", open(os.path.join(root, "cache", slug, which), encoding="utf-8").read())


def rebind(doc_rel, root=ROOT):
    spec = json.load(open(QUOTES, encoding="utf-8"))[doc_rel]
    slug = spec["slug"]
    doc = json.load(open(os.path.join(root, doc_rel), encoding="utf-8"))
    abstracts = _held(root, slug, "abstract")
    # one paper can serve two strands (two endpoints): a PMID used more than once needs a strand-specific quote key
    # 'pmid|strand', never the shared bare-PMID quote (codex strands-r1#6)
    uses = {}
    for s in doc.get("strands") or []:
        for m in s.get("members") or []:
            uses[str(m.get("pmid"))] = uses.get(str(m.get("pmid")), 0) + 1
    for s in doc.get("strands") or []:
        members = []
        sid = str(s.get("strand") or s.get("id"))
        for m in s.get("members") or []:
            pid = str(m.get("pmid"))
            q = spec["members"].get(f"{pid}|{sid}") or (spec["members"].get(pid) if uses[pid] == 1 else None)
            if not q:
                raise SystemExit(f"REFUSED: no quote registered for {m.get('trial')} (PMID {pid}) in strand {sid} of "
                                 f"{doc_rel}" + (" -- this PMID serves several strands, so its key must be "
                                                 f"'{pid}|{sid}'" if uses[pid] > 1 else ""))
            text = abstracts.get(pid) if q["text"] == "abstract" else _held(root, slug, q["text"])
            got = sp.read_member(text, q["quote"])
            if not got:
                raise SystemExit(f"REFUSED: {m.get('trial')} quote not in its held source, or its numbers do not parse")
            where = (f"cache/{slug}/records.json PMID {pid}" if q["text"] == "abstract" else f"cache/{slug}/{q['text']}")
            members.append(dict(m, effect=got["effect"], ci_low=got["ci_low"], ci_high=got["ci_high"],
                                ci_level=got["ci_level"], source_span=got["source_span"], source=f"held {where}"))
        s["members"] = members
        s["k"] = len(members)
        s["pool"] = sp.pool_strand(members, s.get("effect_measure") or "HR") if len(members) >= 2 else None
    doc["generated_by"] = "scripts/rebind_strand_doc.py"
    return doc


if __name__ == "__main__":
    # only when run as a script: an importer (a test) keeps its own stdout (lessons: module-level stdout reassignment)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("doc")
    ap.add_argument("--out")
    a = ap.parse_args()
    d = rebind(a.doc)
    out = a.out or os.path.join(ROOT, a.doc)
    json.dump(d, open(out, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print("wrote", out)
    for s in d["strands"]:
        p = s.get("pool") or {}
        print(f"  {s.get('strand') or s.get('id')} k={s['k']}: {p.get('estimate')} CI {p.get('ci_low')}-{p.get('ci_high')}"
              f" ({(p.get('pooled_ci_refused') or {}).get('code')})")
