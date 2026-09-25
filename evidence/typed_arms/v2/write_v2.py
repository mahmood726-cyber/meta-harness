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
        pf = os.path.join(packet, f)
        if os.path.exists(pf) and norm(open(pf, encoding="utf-8").read()) != prefix + text + "\n":
            return None, f"{role_field}: the packet document is not the held record rebuilt (title + abstract) -- held source changed"
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
    m = re.match(r"\s*(?:(?!(?:versus|vs|and|or|compared|than)\b)[A-Za-z-]+\s+){0,2}?[\[(]\s*(\d+(?:\.\d+)?)\s*%(?!\s*(?:CI|confidence))",
                 after or "", re.I)
    if not m:
        return []
    from decimal import Decimal, ROUND_HALF_UP
    p = m.group(1)
    q = Decimal(1).scaleb(-len(p.partition(".")[2]))
    return [{"reported": p, "agrees": (Decimal(100) * events / total).quantize(q, rounding=ROUND_HALF_UP) == Decimal(p)}]


CLOSED_MARKERS = ("in each group", "in both groups", "in each arm", "in both arms", "per group", "per arm")


def object_spans(text):
    """[start, end) of every JSON object, by a brace scanner that skips string contents."""
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
    return out


def scope_of(text, pos):
    """group_id_scope: the outcome measure (by its title) or the eventGroups list the witness's group id is defined in."""
    for a, b in sorted((sp for sp in object_spans(text) if sp[0] <= pos < sp[1]), key=lambda sp: sp[1] - sp[0]):
        body = text[a:b]
        if '"groups":' in body:
            try:
                return "outcomeMeasuresModule: " + json.loads(body).get("title", "?")
            except ValueError:
                return None
        if '"eventGroups":' in body:
            return "adverseEventsModule.eventGroups"
    return None


def measure_components(text, title):
    """Per group of the outcome measure titled `title`: (group_id, group title, events, events offset, total, total offset)."""
    out = []
    for a, b in object_spans(text):
        body = text[a:b]
        if '"groups":' not in body or not re.search(r'"title":\s*"%s"' % re.escape(title), body):
            continue
        try:
            obj = json.loads(body)
        except ValueError:
            continue
        if obj.get("title") != title:
            continue
        titles = {g["id"]: g.get("title") for g in obj.get("groups", [])}
        ci, di, gi = body.find('"classes":'), body.find('"denoms":'), body.find('"groups":')
        meas = {m.group(1): (int(m.group(2)), a + m.start(2)) for m in re.finditer(r'"groupId":\s*"(\w+)",\s*"value":\s*"(\d+)"', body[ci:di])} if 0 <= ci < di else {}
        meas = {k: (v, o + ci) for k, (v, o) in meas.items()}
        den = {m.group(1): (int(m.group(2)), a + di + m.start(2)) for m in re.finditer(r'"groupId":\s*"(\w+)",\s*"value":\s*"(\d+)"', body[di:gi])} if 0 <= di < gi else {}
        for gid, t in titles.items():
            if gid in meas and gid in den:
                out.append({"group_id": gid, "title": t, "events": meas[gid][0], "events_at": meas[gid][1],
                            "total": den[gid][0], "total_at": den[gid][1]})
        break
    return out


def union_components(row, title, held_tuple):
    """S1: an arm that is the UNION of registered groups across registrations. Returns per-role components if, taking
    exactly one group per role in every registry file, the sums equal the held tuple; else None."""
    import itertools
    files = [d for d in row["documents"] if (d.get("file") or "").startswith("doc_registry_")]
    per_file = []
    for d in files:
        ref = d["origin"]
        _, text, _ = held(ref)
        comps = measure_components(text, title)
        if len(comps) != 2:
            continue
        per_file.append((ref, text, comps))
    if len(per_file) < 2:
        return None
    for choice in itertools.product((0, 1), repeat=len(per_file)):
        roles = {"intervention": [], "comparator": []}
        for (ref, text, comps), c in zip(per_file, choice):
            roles["intervention"].append((ref, text, comps[c]))
            roles["comparator"].append((ref, text, comps[1 - c]))
        s = {r: (sum(x[2]["events"] for x in v), sum(x[2]["total"] for x in v)) for r, v in roles.items()}
        if s == {"intervention": (held_tuple["ai"], held_tuple["n1i"]), "comparator": (held_tuple["ci"], held_tuple["n2i"])}:
            out = {}
            for r, v in roles.items():
                out[r] = [{"group_id": c["group_id"], "group_id_scope": "outcomeMeasuresModule: " + title, "group_title": c["title"],
                           "document_ref": ref, "events": {"value": c["events"], "start": c["events_at"], "end": c["events_at"] + len(str(c["events"]))},
                           "total": {"value": c["total"], "start": c["total_at"], "end": c["total_at"] + len(str(c["total"]))}}
                          for ref, text, c in v]
                for comp, (ref, text, c) in zip(out[r], v):
                    for k in ("events", "total"):
                        assert text[comp[k]["start"]:comp[k]["end"]] == str(comp[k]["value"])
            return out
    return None


def component_problem(text, w, gid):
    """A component witness must be a whole number token (not a digit of a longer number) that is the "value" of a flat
    object whose groupId is the component's group. None when sound."""
    s, e = w["start"], w["end"]
    if (s > 0 and (text[s - 1].isdigit() or text[s - 1] in ",.")) or (e < len(text) and (text[e].isdigit() or text[e] in ",.")):
        return "not a whole number token"
    if not re.search(r'"value":\s*"$', text[max(0, s - 20):s]):
        return "token is not the value of a 'value' key"
    spans = sorted((sp for sp in object_spans(text) if sp[0] <= s < sp[1]), key=lambda sp: sp[1] - sp[0])
    try:
        g = json.loads(text[spans[0][0]:spans[0][1]]).get("groupId") if spans else None
    except ValueError:
        g = None
    return None if g == gid else f"token sits in group {g!r}, not {gid!r}"


def licensed_distributive(w):
    """Schema v2 S3: a shared witness is licensed only by a closed-list marker lying INSIDE the witness text."""
    d = w.get("distributive")
    if not d or d.get("marker") not in CLOSED_MARKERS:
        return False
    ms, me = d["span"]
    return w["start"] <= ms < me <= w["end"] and w["text"][ms - w["start"]:me - w["start"]] == d["marker"]


def distributive_fill(rec, packet, row):
    """The one arm whose events are 'not stated' because the source states ONE count for both arms: take the other
    arm's event token, and require a closed-list marker to follow it within the same clause (<= 40 characters, no
    sentence break). The shared witness spans token..marker; its value is the token's."""
    have = [a for a in rec["arms"] if a.get("event_witness")]
    if len(have) != 1:
        return None
    w, err = to_held(have[0]["event_witness"], packet, row, "shared.events")
    if err:
        return None
    text = held(w["document_ref"])[1]
    tail = text[w["end"]:w["end"] + 60]
    for m in CLOSED_MARKERS:
        i = tail.find(m)
        # between the count and the marker: nothing but an optional closed-list noun ("one PATIENT in each group");
        # any other word could put a different number or arm in between (found by review, 2026-09-25)
        if 0 <= i and re.fullmatch(r"\s+(?:(?:patients?|participants?|subjects?|deaths?|cases?|events?|women|men|"
                                   r"children|infants|people|persons?)\s+)?", tail[:i]):
            ms, me = w["end"] + i, w["end"] + i + len(m)
            sw = {"document_ref": w["document_ref"], "document_sha256": w["document_sha256"], "text": text[w["start"]:me],
                  "representation": REP, "start": w["start"], "end": me, "context": w["context"],
                  "distributive": {"marker": m, "span": [ms, me]}, "after": text[me:me + 40]}
            return {"value": int(have[0]["events"]), "witness": sw}
    return None


def main():
    pop_name, recdir, packets, out_path = sys.argv[1:5]
    written, refused = {}, {}
    for f in sorted(os.listdir(recdir)):
        rec = json.load(open(os.path.join(recdir, f), encoding="utf-8"))
        key = rec["held_key"]
        packet = os.path.join(packets, rec["job"])
        row = json.load(open(os.path.join(packet, "row.json"), encoding="utf-8"))
        # S1 (schema owner, 2026-09-25): an arm that is the union of registered groups -> derived denominator ->
        # refused under the reported-only contract; recorded with its located components, never written
        if rec["state"] == "DIFFERS" and (rec.get("registry") or {}).get("item_title") and rec.get("held_tuple"):
            u = union_components(row, rec["registry"].get("item_title"), rec["held_tuple"])
            if u:
                refused[key] = {"state": "COUNT_DENOMINATOR_DERIVED_UNION", "components": u,
                                "reasons": ["the held numbers are exactly the per-arm sums of several registrations' groups; "
                                            "a union denominator is DERIVED, refused under the reported-only contract"]}
                continue
        # S3: a single printed count stated distributively ('one patient in each group') for BOTH arms
        dist = None
        if rec["state"] == "INCOMPLETE" and len(rec["reasons"]) == 1 and rec["reasons"][0].endswith("events: not stated"):
            dist = distributive_fill(rec, packet, row)
            if dist is None:
                refused[key] = {"state": rec["state"], "reasons": rec["reasons"]}
                continue
        elif rec["state"] != "WITNESSED":
            refused[key] = {"state": rec["state"], "reasons": rec["reasons"]}
            continue
        if dist and rec.get("held_tuple"):
            t = rec["held_tuple"]
            if (t["ai"], t["ci"]) != (dist["value"], dist["value"]):
                refused[key] = {"state": "DISTRIBUTIVE_DIFFERS", "reasons": [f"the shared count {dist['value']} is not the held "
                                                                              f"events ({t['ai']}, {t['ci']})"]}
                continue
        o_out = json.loads(open(os.path.join(packet, "out.json"), "rb").read().decode("utf-8-sig"))
        comps, why = {}, []
        for a in o_out.get("arms") or []:
            cs = []
            for c in a.get("component_corroboration") or []:
                w, err = to_held(c.get("witness") or {}, packet, row, f"{a.get('role')}.component")
                if err or str(c.get("value")) != (w or {}).get("text"):
                    why.append(f"{a.get('role')} component_corroboration: {err or 'value token mismatch'}")
                    continue
                ctext = held(w["document_ref"])[1]
                bad = component_problem(ctext, w, c.get("group_id"))
                if bad:
                    why.append(f"{a.get('role')} component_corroboration {c.get('group_id')}: {bad}")
                    continue
                w.pop("after", None)
                w["group_id_scope"] = scope_of(ctext, w["start"])
                cs.append({"group_id": c.get("group_id"), "class_title": c.get("class_title"), "value": int(c["value"]), "witness": w})
            if cs:
                if len({c["witness"]["group_id_scope"] for c in cs}) != 1:
                    why.append(f"{a.get('role')} component_corroboration: components sit in different scopes")
                comps[a.get("role")] = cs
        shared_g = {(c["witness"]["group_id_scope"], c["group_id"]) for c in comps.get("intervention", [])} & \
                   {(c["witness"]["group_id_scope"], c["group_id"]) for c in comps.get("comparator", [])}
        if shared_g:
            why.append(f"component_corroboration: one registry group corroborates both arms {sorted(shared_g)}")
        obs = []
        for arm in sorted(rec["arms"], key=lambda a: 0 if a["role"] == "intervention" else 1):
            if dist:
                arm = dict(arm, events=dist["value"])
                ew, er = dict(dist["witness"], role=f"{arm['role']}.events"), None
            else:
                ew, er = to_held(arm["event_witness"], packet, row, f"{arm['role']}.events")
            tw, tr = to_held(arm["total_witness"], packet, row, f"{arm['role']}.total")
            why += [x for x in (er, tr) if x]
            if ew and tw:
                tw["derivation"] = None   # reported: located verbatim (schema v2: required on every *.total witness)
                scope = None
                if arm["group_id"]:
                    src = ew if ew["document_ref"].startswith("evidence/typed_arms/registry/") else None
                    corr_w = [c for c in comps.get(arm["role"], []) if c.get("witness")]
                    if src:
                        scope = scope_of(held(src["document_ref"])[1], src["start"])
                    elif corr_w:
                        scope = corr_w[0]["witness"]["group_id_scope"]
                    if not scope:
                        why.append(f"{arm['role']}: group_id {arm['group_id']} has no locatable group_id_scope")
                obs.append({"role": arm["role"], "group_id": arm["group_id"], "group_id_scope": scope, "arm_name": arm["arm_name"],
                            "arm_id": arm["arm_name"].lower().strip(), "events": int(arm["events"]),
                            "total": int(arm["total"]), "n": int(arm["total"]),
                            "event_witness": ew, "total_witness": tw, "outcome": row.get("outcome_name"),
                            "population": None, "window": None,
                            "percentage_corroboration": pct_corroboration(ew["after"], arm["events"], arm["total"]),
                            "context_state": {"population": "NO_EVIDENCE", "window": "NO_EVIDENCE"},
                            **({"component_corroboration": comps[arm["role"]],
                                "component_corroboration_agrees": sum(c["value"] for c in comps[arm["role"]]) == int(arm["events"])}
                               if comps.get(arm["role"]) else {})})
        keys = [(w["document_ref"], w["start"], w["end"]) for o in obs for w in (o["event_witness"], o["total_witness"])]
        shared = len(obs) == 2 and len(set(keys)) != 4
        licensed = (shared and len(set(keys)) == 3 and keys[0] == keys[2]
                    and all(licensed_distributive(o["event_witness"]) for o in obs))
        if shared and not licensed:
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
