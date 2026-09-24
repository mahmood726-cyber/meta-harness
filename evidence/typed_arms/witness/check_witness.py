"""Mechanical check of token-level witnesses (WITNESS_BRIEF.md) for the 34 held count entries.

Per arm field (arm_name, events, total) the witness must:
  T1  name a document of this packet whose bytes still have the packet's sha256, and content[start:end] == text;
  T2  for events/total: `text` is exactly the number token (digits with optional thousands commas, or a spelled
      number <= twenty) and equals the claimed value;
  T3  be a whole token: the characters just outside [start, end) are not digits (or letters, for a spelled number);
  T4  be DISTINCT: no source occurrence (file, start, end) witnesses two different arm fields;
  T5  registry ownership: when the entry's registry record has posted results, ownership_source must be
      REGISTRY_GROUPS unless the extractor says the outcome is absent from them (flagged REGISTRY_NOT_USED for eye
      review); for REGISTRY_GROUPS, each event/total token must sit inside a flat JSON object whose "groupId" is the
      arm's group_id, and the registry defines that groupId with a title equal to the arm_name.
Outputs witness/records/<job>.json and witness/SUMMARY.json. States: WITNESSED (every field of both arms passes),
DIFFERS (all witnessed, a value differs from the held tuple), INCOMPLETE (a field null or refused).

usage: python check_witness.py <witness jobs dir>"""
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                    "fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}


def token_value(t):
    t = (t or "").strip()
    if re.fullmatch(r"\d{1,3}(?:,\d{3})+|\d+", t):
        return int(t.replace(",", ""))
    return WORDS.get(t.lower())


def check_job(job):
    row = json.load(open(os.path.join(job, "row.json"), encoding="utf-8"))
    docs = {d["file"]: d for d in row["documents"] if d.get("file")}
    rec = {"job": os.path.basename(job), "held_key": row["held_key"], "held_tuple": row.get("served"),
           "registry_results": [r["nct"] for r in row.get("registry_results") or []], "state": None, "reasons": [],
           "flags": [], "arms": []}
    p = os.path.join(job, "out.json")
    if not os.path.exists(p):
        rec.update(state="NOT_EXTRACTED", reasons=["no out.json"])
        return rec
    o = json.loads(open(p, "rb").read().decode("utf-8-sig"))
    rec["ownership_source"] = o.get("ownership_source")
    rec["registry"] = o.get("registry")
    rec["notes"] = o.get("notes")
    texts, used = {}, {}

    def load(f):
        if f not in texts:
            b = open(os.path.join(job, f), "rb").read()
            texts[f] = (hashlib.sha256(b).hexdigest(), b.decode("utf-8"))
        return texts[f]

    def witness(w, what, value=None):
        if not isinstance(w, dict) or w.get("start") is None:
            rec["reasons"].append(f"{what}: no witness")
            return None
        f = w.get("file")
        if f not in docs:
            rec["reasons"].append(f"T1 {what}: file {f!r} is not a document of this packet")
            return None
        sha, text = load(f)
        if sha != docs[f]["sha256"]:
            rec["reasons"].append(f"T1 {what}: {f} bytes changed")
            return None
        s, e = int(w["start"]), int(w["end"])
        if text[s:e] != w.get("text"):
            rec["reasons"].append(f"T1 {what}: content[{s}:{e}] is {text[s:e][:40]!r}, not {str(w.get('text'))[:40]!r}")
            return None
        if value is not None:
            v = token_value(w["text"])
            if v != value:
                rec["reasons"].append(f"T2 {what}: token {w['text']!r} is not the number {value}")
                return None
            spelled = not w["text"].strip()[0].isdigit()
            edge = r"[A-Za-z0-9]" if spelled else r"[0-9]"
            if (s > 0 and re.match(edge, text[s - 1])) or (e < len(text) and re.match(edge, text[e])):
                rec["reasons"].append(f"T3 {what}: {w['text']!r} at {s} is part of a longer token")
                return None
        key = (f, s, e)
        if key in used and used[key] != what:
            rec["reasons"].append(f"T4 {what}: the same occurrence ({f} {s}-{e}) already witnesses {used[key]}")
            return None
        used[key] = what
        return {"file": f, "document": docs[f]["origin"], "document_sha256": docs[f].get("origin_sha256"),
                "start": s, "end": e, "text": w["text"]}

    def enclosing_group(f, s):
        _, text = load(f)
        a, b = text.rfind("{", 0, s), text.find("}", s)
        if a < 0 or b < 0 or "}" in text[a:s]:
            return None
        g = re.search(r'"groupId":\s*"(\w+)"', text[a:b])
        if g:
            return g.group(1)
        # an eventGroups / groups object IS the group: it carries "id" and "title" (e.g. seriousNumAffected lives there)
        g = re.search(r'"id":\s*"(\w+)"', text[a:b])
        return g.group(1) if g and re.search(r'"title":', text[a:b]) else None

    def group_title(f, gid, at):
        """The title of group `gid` as defined in the innermost JSON object that CONTAINS the witness and defines a
        "groups" or "eventGroups" list -- group ids are per outcome measure (OG000 is 'Aspirin' in one measure and
        'Omega-3' in the next), and in a sorted-keys record a measure's groups may come before or after its counts,
        so neither the file's first definition nor the nearest one is safe."""
        _, text = load(f)
        for a, b in sorted((sp for sp in object_spans(f) if sp[0] <= at < sp[1]), key=lambda sp: sp[1] - sp[0]):
            body = text[a:b]
            if '"groups":' in body or '"eventGroups":' in body:
                m = re.search(r'\{[^{}]*?"id":\s*"%s"[^{}]*?\}' % re.escape(gid), body)
                t = m and re.search(r'"title":\s*"([^"]*)"', m.group(0))
                return t.group(1) if t else None
        return None

    spans_cache = {}

    def object_spans(f):
        """[start, end) of every JSON object in the file, by a brace scanner that skips string contents."""
        if f not in spans_cache:
            _, text = load(f)
            out, stack, i, n, in_str = [], [], 0, len(text), False
            while i < n:
                c = text[i]
                if in_str:
                    if c == "\\":
                        i += 1
                    elif c == '"':
                        in_str = False
                elif c == '"':
                    in_str = True
                elif c == "{":
                    stack.append(i)
                elif c == "}" and stack:
                    out.append((stack.pop(), i + 1))
                i += 1
            spans_cache[f] = out
        return spans_cache[f]

    arms = o.get("arms") or []
    for i, a in enumerate(arms):
        role = a.get("role")
        out = {"role": role, "group_id": a.get("group_id"), "arm_name": a.get("arm_name"), "events": a.get("events"),
               "total": a.get("total")}
        out["arm_name_witness"] = witness(a.get("arm_name_witness"), f"arm {i} ({role}) arm_name")
        out["event_witness"] = witness(a.get("event_witness"), f"arm {i} ({role}) events", a.get("events")) \
            if isinstance(a.get("events"), int) else None
        out["total_witness"] = witness(a.get("total_witness"), f"arm {i} ({role}) total", a.get("total")) \
            if isinstance(a.get("total"), int) else None
        if not isinstance(a.get("events"), int):
            rec["reasons"].append(f"arm {i} ({role}) events: not stated")
        if not isinstance(a.get("total"), int):
            rec["reasons"].append(f"arm {i} ({role}) total: not stated")
        if o.get("ownership_source") == "REGISTRY_GROUPS":
            gid = a.get("group_id")
            for fld in ("event_witness", "total_witness"):
                w = out[fld]
                if w and not w["file"].startswith("doc_registry_"):
                    rec["reasons"].append(f"T5 arm {i} {fld}: REGISTRY_GROUPS ownership but witness is in {w['file']}")
                elif w and enclosing_group(w["file"], w["start"]) != gid:
                    rec["reasons"].append(f"T5 arm {i} {fld}: enclosing groupId is {enclosing_group(w['file'], w['start'])!r}, "
                                          f"not the arm's {gid!r}")
            reg_file = (out["event_witness"] or out["total_witness"] or {}).get("file")
            if reg_file and gid:
                title = group_title(reg_file, gid, (out["event_witness"] or out["total_witness"])["start"])
                out["registry_group_title"] = title
                if title != a.get("arm_name"):
                    rec["reasons"].append(f"T5 arm {i}: registry group {gid} is titled {title!r}, not {a.get('arm_name')!r}")
        rec["arms"].append(out)
    if len(arms) != 2:
        rec["reasons"].append(f"{len(arms)} arms (need 2)")
    if rec["registry_results"] and o.get("ownership_source") != "REGISTRY_GROUPS":
        rec["flags"].append("REGISTRY_NOT_USED: the entry's registry record has posted results; the extractor used prose -- "
                            "its notes must say the outcome is absent from the registry results (read by eye)")
    s = row.get("served")  # absent in a BLIND packet: no comparison with a held tuple is possible there
    got = {a.get("role"): (a.get("events"), a.get("total")) for a in arms}
    want = {"intervention": (s["ai"], s["n1i"]), "comparator": (s["ci"], s["n2i"])} if s else got
    if rec["reasons"]:
        rec["state"] = "INCOMPLETE"
    elif got != want:
        rec["state"] = "DIFFERS"
        rec["reasons"].append(f"printed {got} vs held {want}")
    else:
        rec["state"] = "WITNESSED"
    return rec


def main():
    jobs = sys.argv[1]
    os.makedirs(os.path.join(HERE, "records"), exist_ok=True)
    counts, rows = {}, []
    for j in sorted(os.listdir(jobs)):
        if not os.path.isdir(os.path.join(jobs, j)):
            continue
        rec = check_job(os.path.join(jobs, j))
        json.dump(rec, open(os.path.join(HERE, "records", j + ".json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
        counts[rec["state"]] = counts.get(rec["state"], 0) + 1
        rows.append({"job": j, "state": rec["state"], "ownership_source": rec.get("ownership_source"),
                     "flags": rec["flags"], "reasons": rec["reasons"]})
    json.dump({"counts": counts, "rows": rows}, open(os.path.join(HERE, "SUMMARY.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps(counts), "of", len(rows))


if __name__ == "__main__":
    main()
