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


SEP = ",\u2008\u202f"


def token_value(t):
    t = (t or "").strip()
    if re.fullmatch(r"\d{1,3}(?:,\d{3})+|\d+", t):
        return int(t.replace(",", ""))
    # a typographic thousands separator (U+2008 punctuation space, U+202F narrow no-break space) -- The Lancet prints
    # "10<U+2008>033". Only these two: neither is turned into a plain space by the normaliser, and neither ever
    # separates two different numbers. A plain space never counts (it would join "10 033" = ten and thirty-three).
    if re.fullmatch(r"\d{1,3}(?:[\u2008\u202f]\d{3})+", t):
        return int(re.sub(r"[\u2008\u202f]", "", t))
    return WORDS.get(t.lower())


_TA = None
STRONG_CONTROL = re.compile(r"\b(placebo|sham|dummy|no treatment|no probiotic)\b|^\s*no[- ][a-z]", re.I)


def _typed_arms():
    """check_typed_arms.py's G6 vocabulary (i_terms, side, CONTROL), so both gates share one definition of a control arm."""
    global _TA
    if _TA is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("check_typed_arms", os.path.join(HERE, "..", "scripts", "check_typed_arms.py"))
        _TA = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_TA)
    return _TA


def _served_i_line(row_id):
    p = os.path.join(HERE, "..", "population.json")
    if not row_id or not os.path.exists(p):
        return None
    pop = json.load(open(p, encoding="utf-8"))
    rows = pop["rows"] if isinstance(pop, dict) else pop
    return next((r.get("intervention_i_line") for r in rows if r.get("row_id") == row_id), None)


def role_anchor(rec, row, arms):
    """T6: the DECLARED role must agree with the protocol, not only with the object. Reported by the F4 lane
    (2026-09-25): T5 proves number -> groupId -> title, and the tuple comparison is keyed by the object's own role, so a
    consistently reversed object -- placebo declared 'intervention', tuple reversed to match -- was WITNESSED.
    Protocol side of an arm name: control vocabulary (incl. a named absence 'no-X') -> comparator; the topic's
    intervention terms -> intervention; the topic's comparator terms -> comparator. Terms: the packet's
    intervention_terms/comparator_terms (held packets), else the served row's review I-line (population.json).
    A declared role on the other side is ARM_ROLE_MISMATCH (refused). No terms -> ROLE_UNANCHORED; a name on neither
    side -> ROLE_UNMATCHED: both flagged, never a silent pass."""
    ta = _typed_arms()
    i_terms = {t.lower() for t in (row.get("intervention_terms") or []) if t}
    c_terms = {t.lower() for t in (row.get("comparator_terms") or []) if t}
    i_terms |= ta.i_terms(" ".join(i_terms)) if i_terms else ta.i_terms(_served_i_line(row.get("row_id")))
    if not i_terms:
        rec["flags"].append("ROLE_UNANCHORED: no protocol terms for this row; the declared role was not checked")
        return
    bad = [a.get("role") for a in arms if a.get("role") not in ("intervention", "comparator")]
    if bad:
        rec["reasons"].append(f"ARM_ROLE_INVALID: role must be exactly 'intervention' or 'comparator', got {bad!r}")
    if len(arms) == 2 and arms[0].get("role") == arms[1].get("role"):
        rec["reasons"].append(f"ARM_ROLE_DUPLICATE: both arms declared {arms[0].get('role')!r}")
    sides = []
    for a in arms:
        name = str(a.get("arm_name") or "").lower()
        on_i, on_c = ta.side(name, i_terms), ta.side(name, c_terms)
        strong = STRONG_CONTROL.search(name)   # placebo / sham / dummy / a named absence: never the intervention
        weak = ta.CONTROL.search(name)         # 'usual care', 'control': an add-on arm can carry these words
        if strong or (weak and not on_i):
            sides.append("comparator")
        elif on_i and on_c:
            sides.append(None)                 # shares vocabulary with both (valsartan vs sacubitril/valsartan)
        elif on_i:
            sides.append("intervention")
        elif on_c:
            sides.append("comparator")
        else:
            sides.append(None)
    for i, (a, side) in enumerate(zip(arms, sides)):
        role = a.get("role")
        if side is None:
            # a two-arm row whose OTHER arm is anchored fixes this arm's role by elimination; otherwise flag it
            other = sides[1 - i] if len(arms) == 2 else None
            if other and role in ("intervention", "comparator") and other == role:
                rec["reasons"].append(f"ARM_ROLE_MISMATCH arm {i}: declared {role!r}, but the other arm is the protocol's "
                                      f"{other}, so this one cannot be")
            elif not other:
                rec["flags"].append(f"ROLE_UNMATCHED arm {i}: {a.get('arm_name')!r} matches neither the protocol's "
                                    f"intervention nor its comparator vocabulary, and nor does the other arm")
        elif role in ("intervention", "comparator") and side != role:
            rec["reasons"].append(f"ARM_ROLE_MISMATCH arm {i}: declared {role!r} but {a.get('arm_name')!r} is the protocol's "
                                  f"{side}; role must come from the protocol, not from the object")
    if len(arms) == 2 and sides[0] and sides[0] == sides[1]:
        rec["flags"].append(f"ROLE_AMBIGUOUS: both arm names read as the protocol's {sides[0]}")


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
            # a thousands group on either side makes this a PART of a grouped number ("10" or "033" of "10,033" /
            # "10<U+2008>033"): found by review, 2026-09-25
            if not spelled and ((e + 4 <= len(text) and text[e] in SEP and text[e + 1:e + 4].isdigit()
                                 and (e + 4 == len(text) or not text[e + 4].isdigit()))
                                or (s >= 2 and text[s - 1] in SEP and text[s - 2].isdigit() and len(w["text"]) == 3)):
                rec["reasons"].append(f"T3 {what}: {w['text']!r} at {s} is one group of a grouped number")
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
    role_anchor(rec, row, arms)
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
