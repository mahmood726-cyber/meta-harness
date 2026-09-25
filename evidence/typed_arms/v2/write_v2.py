"""Write schema-v2 count observations (SCHEMA-count-observations-v2, F4 repair lane) from evid2's checked witnesses.

Input : witness records produced by ../witness/check_witness.py (one per row; only WITNESSED rows are written) and
        the packets they were checked against (to map packet documents back to HELD documents).
Output: v2/OBSERVATIONS_<population>.json -- per row, two observations (intervention then comparator):
        {role, group_id, arm_name, arm_id (alias), events, total, n (alias), event_witness, total_witness,
         outcome, population, window, percentage_corroboration, context_state}
        plus the rows NOT written, each with its reason.

Coordinates address the held document exactly as hand_binding.resolve_document returns it, after
extract._norm + hand_binding._EN_DASH. Both are one-character-for-one-character substitutions, so normalized offsets
equal raw offsets; the writer re-resolves every held document and REFUSES a witness whose normalized
text[start:end] is not the token. Packet -> held mapping:
  doc_records_pmid_<P>.txt  -> cache/<slug>/records.json#PMID-<P>   (the record's abstract; the packet prefixed
                               'TITLE: <title>\\n\\n', so offsets shift by that prefix; a token in the title is refused)
  doc_registry_<NCT>.json   -> evidence/typed_arms/registry/<NCT>.json   (byte-identical)
  doc_<name> (full texts)   -> its origin path in the packet's row.json (byte-identical)
  doc_ctgov_results_*.json  -> refused (a re-serialisation, not a held document)
Injectivity (ARM_WITNESS_NOT_INJECTIVE): the four role-specific witnesses must have four distinct coordinates.

usage: python write_v2.py <population name> <witness records dir> <packets dir> <out.json>"""
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REP = "extract._norm + hand_binding._EN_DASH"
TRANS = str.maketrans({"–": "-", "—": "-", "−": "-", "·": ".", " ": " ", " ": " ", "‧": ".", "∙": "."})


def norm(t):
    return (t or "").translate(TRANS)


def held(ref):
    """Mirror of hand_binding.resolve_document for the refs this writer emits."""
    path, _, frag = ref.partition("#")
    raw = open(os.path.join(ROOT, path), "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    if path.endswith("records.json"):
        want = frag.replace("PMID-", "").strip()
        data = json.loads(raw.decode("utf-8"))
        lists = [data.get("records") or []] + [v for k, v in data.items() if k != "records" and isinstance(v, list)
                                               and v and all(isinstance(x, dict) and "abstract" in x for x in v)]
        rec = next((r for lst in lists for r in lst if str(r.get("id")) == want), None)
        return sha, norm((rec or {}).get("abstract") or ""), rec
    return sha, norm(raw.decode("utf-8", errors="replace")), None


def to_held(w, packet, row, role_field):
    f = w["file"]
    if f.startswith("doc_records_pmid_"):
        pid = re.sub(r"\D", "", f)
        ref = f"cache/{row['slug']}/records.json#PMID-{pid}"
        sha, text, rec = held(ref)
        prefix = f"TITLE: {(rec or {}).get('title') or ''}\n\n"
        s, e = w["start"] - len(prefix), w["end"] - len(prefix)
        if s < 0:
            return None, f"{role_field}: token lies in the title, not in the held abstract"
    elif f.startswith("doc_registry_"):
        ref = f"evidence/typed_arms/registry/{f[len('doc_registry_'):]}"
        sha, text, _ = held(ref)
        s, e = w["start"], w["end"]
    elif f.startswith("doc_ctgov_results_"):
        return None, f"{role_field}: witness is in a re-serialised ctgov_results packet file, not a held document"
    else:
        origin = next((d["origin"] for d in row["documents"] if d.get("file") == f), None)
        if not origin:
            return None, f"{role_field}: packet file {f} has no held origin"
        ref = origin
        sha, text, _ = held(ref)
        s, e = w["start"], w["end"]
    if text[s:e] != norm(w["text"]):
        return None, f"{role_field}: held normalized text[{s}:{e}] is {text[s:e]!r}, not {w['text']!r}"
    return {"role": role_field, "document_ref": ref, "document_sha256": sha, "text": text[s:e],
            "representation": REP, "start": s, "end": e,
            "context": text[max(0, s - 80):e + 80], "after": text[e:e + 40]}, None


def pct_corroboration(after, events, total):
    """Only the percentage printed immediately after THIS event token ('26 (14.5%)', '26 patients (14.5%)'):
    a wider window picks up the other arm's percentage."""
    m = re.match(r"\s*(?:[A-Za-z-]+\s+){0,2}?[\[(]\s*(\d+(?:\.\d+)?)\s*%", after or "")
    if not m:
        return []
    p = m.group(1)
    dec = len(p.partition(".")[2])
    return [{"reported": p, "agrees": f"{100 * events / total:.{dec}f}" == p}]


def main():
    pop_name, recdir, packets, out_path = sys.argv[1:5]
    written, refused = {}, {}
    for f in sorted(os.listdir(recdir)):
        rec = json.load(open(os.path.join(recdir, f), encoding="utf-8"))
        key = rec["held_key"]
        if rec["state"] != "WITNESSED":
            refused[key] = {"state": rec["state"], "reasons": rec["reasons"]}
            continue
        packet = os.path.join(packets, rec["job"])
        row = json.load(open(os.path.join(packet, "row.json"), encoding="utf-8"))
        obs, why = [], []
        for arm in sorted(rec["arms"], key=lambda a: 0 if a["role"] == "intervention" else 1):
            ew, er = to_held(arm["event_witness"], packet, row, f"{arm['role']}.events")
            tw, tr = to_held(arm["total_witness"], packet, row, f"{arm['role']}.total")
            why += [x for x in (er, tr) if x]
            if ew and tw:
                obs.append({"role": arm["role"], "group_id": arm["group_id"], "arm_name": arm["arm_name"],
                            "arm_id": arm["arm_name"].lower().strip(), "events": int(arm["events"]),
                            "total": int(arm["total"]), "n": int(arm["total"]),
                            "event_witness": ew, "total_witness": tw, "outcome": row.get("outcome_name"),
                            "population": None, "window": None,
                            "percentage_corroboration": pct_corroboration(ew["after"], arm["events"], arm["total"]),
                            "context_state": {"population": "NO_EVIDENCE", "window": "NO_EVIDENCE"}})
        keys = [(w["document_ref"], w["start"], w["end"]) for o in obs for w in (o["event_witness"], o["total_witness"])]
        if len(obs) == 2 and len(set(keys)) != 4:
            why.append("ARM_WITNESS_NOT_INJECTIVE: two role-specific fields share one source coordinate")
        for o in obs:
            for w in (o["event_witness"], o["total_witness"]):
                w.pop("after", None)
        if why or len(obs) != 2:
            refused[key] = {"state": "NOT_WRITTEN", "reasons": why or ["fewer than two observations"]}
            continue
        written[key] = {"ownership_source": rec.get("ownership_source"), "observations": obs,
                        "held_tuple": rec["held_tuple"]}
    doc = {"schema": "SCHEMA-count-observations-v2 (F4 repair lane)", "population": pop_name,
           "written": len(written), "not_written": len(refused), "rows": written, "not_written_rows": refused,
           "note": ("population/window are left null with context_state NO_EVIDENCE: evid2 binds them per row in its "
                    "typed records, but v2's 'null unless exactly ONE is found' is the producer's own test; supplying "
                    "them would have to equal its re-extraction.")}
    json.dump(doc, open(out_path, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(f"{pop_name}: written {len(written)}, not written {len(refused)}")


if __name__ == "__main__":
    main()
