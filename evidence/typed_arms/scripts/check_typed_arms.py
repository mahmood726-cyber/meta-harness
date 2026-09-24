"""Gate for typed per-arm observations (the DATA half of the REWIND arm-swap repair).

Input : evidence/typed_arms/population.json (the frozen served rows) and, per row, the extractor's out.json in its job
        directory together with the held-document copies it was shown.
Output: evidence/typed_arms/records/<row_id>.json -- one typed record per row, BOUND or SET_ASIDE with named reasons --
        and evidence/typed_arms/SUMMARY.json.

A row is BOUND only if ALL of these hold, each checked mechanically against bytes:
  G1  every quoted span is a verbatim substring of the document file it names (the SAME bytes the extractor was shown),
      and that file's sha256 equals the one recorded when the packet was built;
  G2  each arm's event count appears as a number inside its events span;
  G3  each arm's DENOMINATOR appears as a number inside its total span, and not as a percentage -- a percentage may
      corroborate, never stand in (total_basis NOT_STATED, or a total only found next to '%', is a refusal);
  G4  the two arms map one-to-one onto the served F4B slots (ai,n1i) and (ci,n2i) by their (events, total) pairs --
      this is what fixes comparator_direction; an arm swap (events of one arm reported against the other's slot) or
      any source number that differs from the served one is NOT bound, it is SOURCE_DIFFERS and goes to the signature
      queue because binding it would change a served number;
  G6  DIRECTION, decided independently of the served numbers: the arm the served experimental slot (ai,n1i) maps to
      must be the experimental arm on evidence that does not read the served slots -- the review's declared
      intervention line (plus a disclosed static class->member word list), the registry arm's active interventions
      (a placebo arm carries none), and comparator vocabulary (placebo, usual/standard care, control). A one-to-one
      numeric match with the arms reversed is an ARM_SWAP (the REWIND defect), never a binding; evidence that is
      absent or conflicting is DIRECTION_UNRESOLVED and sets the row aside.
  G5  every arm has an arm_id: a registry arm_id that exists in the row's trial family and whose intervention words
      occur in the arm label, or -- when the family holds no registry arms -- a label-derived id typed as such.
The gate never edits a served row."""
import json, os, re, sys, hashlib, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
POP = os.path.join(BASE, "population.json")
WORDS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                    "fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def numbers_in(text):
    """(value, is_percentage) for every number token in text. '4,949' and '4 949' are 4949; '47·4%' is a percentage.
    Spelled numbers up to twenty are read ('four of 119')."""
    t = unicodedata.normalize("NFKC", text).replace(" ", " ").replace(" ", " ")
    out = []
    for m in re.finditer(r"(?<![\d.·])(\d{1,3}(?:[, ]\d{3})+|\d+)(?:[.·]\d+)?(\s*%)?", t):
        raw = m.group(1)
        if " " in raw and not re.fullmatch(r"\d{1,3}(?: \d{3})+", raw):
            continue
        whole = m.group(0)
        is_dec = bool(re.search(r"[.·]\d", whole))
        out.append((int(re.sub(r"[, ]", "", raw)), bool(m.group(2)) or is_dec))
    for m in re.finditer(r"\b(" + "|".join(WORDS) + r")\b", t, flags=re.I):
        out.append((WORDS[m.group(1).lower()], False))
    return out


def has_count(text, value):
    return any(v == value and not pct for v, pct in numbers_in(text or ""))


def span_ok(span, job, docs, fails, what):
    if not isinstance(span, dict) or not span.get("text") or not span.get("file"):
        fails.append(f"G1 {what}: no span")
        return None
    d = docs.get(span["file"])
    if d is None:
        fails.append(f"G1 {what}: names file {span['file']!r} that is not a held document of this row")
        return None
    b = open(os.path.join(job, span["file"]), "rb").read()
    if sha(b) != d["sha256"]:
        fails.append(f"G1 {what}: {span['file']} bytes changed since the packet was built")
        return None
    text = b.decode("utf-8")
    at = text.find(span["text"])
    if at < 0:
        fails.append(f"G1 {what}: quoted text not found verbatim in {span['file']}: {span['text'][:90]!r}")
        return None
    return {"document": d["origin"], "document_sha256": d.get("origin_sha256"), "copy_sha256": d["sha256"],
            "start": at, "end": at + len(span["text"]), "text": span["text"]}


def reg_words(a):
    """The words a registry arm states about itself: its design-group label value, its intervention names."""
    lab = a.get("label")
    drug = a.get("drug")
    bits = [str(lab.get("value") if isinstance(lab, dict) else (lab or ""))]
    bits += [str(x) for x in (a.get("active_interventions") or [])]
    if isinstance(drug, dict):
        bits += [str(x) for x in (drug.get("value") or [])]
    return " ".join(bits).lower()


def arm_id_for(arm, reg_arms, family_id, fails, idx, iline=None):
    rid = arm.get("registry_arm_id")
    if reg_arms:
        by = {a.get("arm_id"): a for a in reg_arms}
        if rid not in by:
            fails.append(f"G5 arm {idx}: registry_arm_id {rid!r} is not an arm of family {family_id}")
            return None, None
        words = reg_words(by[rid])
        label = (arm.get("arm_label") or "").lower()
        toks = [w for w in re.findall(r"[a-z][a-z0-9-]{3,}", label) if w not in ("group", "arm", "patients", "participants", "assigned", "receive", "receiving", "with", "plus")]
        hit = [w for w in toks if w in words]
        if hit:
            return rid, "REGISTRY_ARM (intervention word match: " + ", ".join(hit) + ")"
        # G5b: no shared word, but the source label and the registry arm fall on the SAME side of the review's declared
        # intervention line, and every other registry arm of the family falls on the other side (2-arm families only)
        terms = i_terms(iline)
        def side(t): return any(re.search(r"(?<![a-z])" + re.escape(w), t) for w in terms)
        if len(reg_arms) == 2 and terms:
            other = [a for a in reg_arms if a.get("arm_id") != rid][0]
            if side(label) == side(words) and side(reg_words(other)) != side(words):
                return rid, ("REGISTRY_ARM (role match via the review's intervention line: source label and registry arm "
                             f"both {'on' if side(words) else 'off'} it; the family's other arm {'off' if side(words) else 'on'} it)")
        fails.append(f"G5 arm {idx}: label {arm.get('arm_label')!r} shares no intervention word with registry arm {rid} ({words[:120]!r}) and no role match")
        return None, None
    lab = re.sub(r"[^a-z0-9]+", "-", (arm.get("arm_label") or "").lower()).strip("-")
    if not lab:
        fails.append(f"G5 arm {idx}: no arm label to derive an id from")
        return None, None
    return f"{family_id}#arm:{lab}", "SOURCE_LABEL (no registry arms held for this family)"


# Static, disclosed: class words in the review's I-line expanded to the member names a source prints instead.
CLASS_MEMBERS = {
    "corticosteroids": ["hydrocortisone", "methylprednisolone", "prednisone", "prednisolone", "dexamethasone", "corticosteroid", "glucocorticoid", "steroid"],
    "probiotics": ["probiotic", "lactobacillus", "lactobacilli", "saccharomyces", "boulardii", "bifidobacterium", "bifidobacteria", "streptococcus", "yogurt", "yoghurt", "kefir", "synbiotic", "vsl", "clostridium", "bacillus"],
    "dpp-4": ["sitagliptin", "saxagliptin", "alogliptin", "linagliptin", "gliptin"],
    "glp-1": ["liraglutide", "semaglutide", "dulaglutide", "albiglutide", "efpeglenatide", "exenatide", "lixisenatide"],
    "omega-3": ["omega-3", "omega", "fish oil", "icosapent", "epa", "dha", "n-3"],
    "crystalloid": ["balanced", "plasma-lyte", "plasmalyte", "ringer", "lactated", "multiple electrolyte"],
}
GENERIC = set("added usual standard care therapy including daily once weekly alone same background regimen trial arms both "
              "specifically solution supportive medical guideline based heart failure receptor antagonist agonist "
              "interleukin development name subcutaneous intranasal newly initiated oral antidepressant systemic "
              "antimicrobial named genera strains fermented products peri operative low dose supplementation acids "
              "fatty marine carboxylic ethyl inhibitor inhibitors buffered ovulation induction low-dose".split())
CONTROL = re.compile(r"\b(placebo|usual care|standard care|standard of care|standard treatment|control|no probiotic|"
                     r"no treatment|sham|dummy)\b", re.I)


def i_terms(iline):
    t = (iline or "").lower()
    words = {w for w in re.findall(r"[a-z][a-z0-9+-]{2,}", t) if w not in GENERIC and len(w) >= 4}
    for cls, members in CLASS_MEMBERS.items():
        if cls.split("-")[0] in t:
            words.update(members)
    return words


def arm_text(t, reg_by_id):
    bits = [t.get("arm_label") or ""]
    a = reg_by_id.get(t.get("arm_id")) or {}
    if a:
        bits.append(reg_words(a))
    return " ".join(bits).lower(), a


def direction(typed, iline, reg_arms):
    """Return (index of experimental arm or None, evidence list). Never reads served slots."""
    reg_by_id = {a.get("arm_id"): a for a in (reg_arms or [])}
    terms = i_terms(iline)
    ev = []
    score = []
    for j, t in enumerate(typed):
        txt, a = arm_text(t, reg_by_id)
        hits = sorted(w for w in terms if re.search(r"(?<![a-z])" + re.escape(w), txt))
        ctrl = bool(CONTROL.search(t.get("arm_label") or "")) and not hits
        active = a.get("active_interventions") if a else None
        ev.append({"arm": j, "i_line_hits": hits, "control_vocabulary": ctrl,
                   "registry_active_interventions": active})
        s = (1 if hits else 0) - (1 if ctrl else 0) + (0 if active is None else (1 if active else -1))
        score.append(s)
    best = [j for j, s in enumerate(score) if s == max(score)]
    if len(typed) == 2 and len(best) == 1 and max(score) > 0 and min(score) < max(score):
        other = 1 - best[0]
        if not ev[best[0]]["i_line_hits"] and not ev[other]["control_vocabulary"] and ev[other]["i_line_hits"]:
            return None, ev
        return best[0], ev
    return None, ev


def check_row(r, jobs):
    job = os.path.join(jobs, r["row_id"])
    rowj = json.load(open(os.path.join(job, "row.json"), encoding="utf-8"))
    docs = {d["file"]: d for d in rowj["documents"] if d.get("file")}
    rec = {"row_id": r["row_id"], "slug": r["slug"], "outcome_index": r["outcome_index"], "trial_index": r["trial_index"],
           "outcome_name": r["outcome_name"], "trial_id": r["trial_id"], "family_id": r["family_id"],
           "served_ref": None, "served_row_sha256": r["row_sha256"], "served_f4b": r["served"],
           "state": None, "reasons": [], "comparator_direction": None, "arm_observations": [],
           "extractor": {"out_json_sha256": None, "job": r["row_id"]}}
    outp = os.path.join(job, "out.json")
    if not os.path.exists(outp) or os.path.getsize(outp) == 0:
        rec["state"], rec["reasons"] = "NOT_EXTRACTED", ["no extractor artefact (out.json absent)"]
        return rec
    raw = open(outp, "rb").read()
    rec["extractor"]["out_json_sha256"] = sha(raw)
    try:
        o = json.loads(raw.decode("utf-8-sig"))
    except Exception as e:
        rec["state"], rec["reasons"] = "NOT_EXTRACTED", [f"extractor artefact is not JSON: {e}"]
        return rec
    fails, diffs = [], []
    arms = o.get("arms") or []
    shared = {}
    for key in ("outcome", "population", "window"):
        v = o.get(key)
        if v and v.get("span"):
            loc = span_ok(v["span"], job, docs, fails, key)
            shared[key] = {"text": v.get("text"), "span": loc}
        else:
            shared[key] = None
            if key != "window":
                fails.append(f"G1 {key}: not bound to a span")
    typed = []
    for i, a in enumerate(arms):
        ev, tot = a.get("events"), a.get("total")
        es = span_ok(a.get("events_span"), job, docs, fails, f"arm {i} events")
        ts = span_ok(a.get("total_span"), job, docs, fails, f"arm {i} total")
        ls = span_ok(a.get("arm_label_span"), job, docs, fails, f"arm {i} label")
        if not isinstance(ev, int) or isinstance(ev, bool):
            fails.append(f"G2 arm {i}: events not an integer ({ev!r})")
        elif es and not has_count(es["text"], ev):
            fails.append(f"G2 arm {i}: events {ev} not printed as a count in its span")
        if a.get("total_basis") == "NOT_STATED" or not isinstance(tot, int) or isinstance(tot, bool):
            fails.append(f"G3 arm {i}: denominator not stated as a number (basis {a.get('total_basis')}; a percentage "
                         f"{a.get('percentage_text')!r} does not stand in)")
        elif ts and not has_count(ts["text"], tot):
            fails.append(f"G3 arm {i}: total {tot} not printed as a count in its span (only as a percentage, or absent)")
        aid, basis = arm_id_for(a, r.get("registry_arms"), r["family_id"], fails, i, r.get("intervention_i_line"))
        typed.append({"arm_id": aid, "arm_id_basis": basis, "arm_label": a.get("arm_label"), "arm_label_span": ls,
                      "events": ev, "total": tot, "total_basis": a.get("total_basis"),
                      "percentage_text": a.get("percentage_text"), "events_span": es, "total_span": ts,
                      "outcome": shared.get("outcome"), "population": shared.get("population"),
                      "window": shared.get("window"), "f4b_slot": None})
    s = r["served"]
    slots = {"ai/n1i": (s.get("ai"), s.get("n1i")), "ci/n2i": (s.get("ci"), s.get("n2i"))}
    match = {slot: [j for j, t in enumerate(typed) if (t["events"], t["total"]) == pair] for slot, pair in slots.items()}
    if len(typed) < 2:
        fails.append(f"G4 fewer than two arms extracted ({len(typed)})")
    elif all(len(v) == 1 for v in match.values()) and match["ai/n1i"][0] != match["ci/n2i"][0] and (
            direction(typed, r.get("intervention_i_line"), r.get("registry_arms"))[0] != match["ai/n1i"][0]):
        exp_j, dev = direction(typed, r.get("intervention_i_line"), r.get("registry_arms"))
        rec["direction_evidence"] = dev
        if exp_j is None:
            fails.append("G6 DIRECTION_UNRESOLVED: the arms' labels, registry interventions and comparator vocabulary do not "
                         "independently say which arm is experimental")
        else:
            diffs.append({"kind": "ARM_SWAP", "served": s,
                          "source_arms": [{"arm_label": t["arm_label"], "events": t["events"], "total": t["total"]} for t in typed],
                          "experimental_by_evidence": typed[exp_j]["arm_label"],
                          "served_experimental_slot_holds": typed[match["ai/n1i"][0]]["arm_label"]})
            fails.append(f"G6 ARM_SWAP: the served experimental slot (ai,n1i) holds the numbers of "
                         f"{typed[match['ai/n1i'][0]]['arm_label']!r}, but the experimental arm is {typed[exp_j]['arm_label']!r}")
    elif all(len(v) == 1 for v in match.values()) and match["ai/n1i"][0] != match["ci/n2i"][0]:
        e, c = match["ai/n1i"][0], match["ci/n2i"][0]
        rec["direction_evidence"] = direction(typed, r.get("intervention_i_line"), r.get("registry_arms"))[1]
        typed[e]["f4b_slot"], typed[c]["f4b_slot"] = "ai/n1i", "ci/n2i"
        rec["comparator_direction"] = {"experimental_arm_id": typed[e]["arm_id"], "comparator_arm_id": typed[c]["arm_id"],
                                       "experimental_label": typed[e]["arm_label"], "comparator_label": typed[c]["arm_label"],
                                       "basis": "served (ai,n1i) equals the source's (events,total) for the experimental arm and (ci,n2i) the comparator's; one-to-one"}
    else:
        swapped = [slot for slot, pair in slots.items() for t in typed
                   if (t["events"], t["total"]) != pair and (t["events"] == pair[0] or t["total"] == pair[1])]
        diffs.append({"kind": "NUMBERS_DIFFER", "served": s, "source_arms": [{"arm_label": t["arm_label"], "events": t["events"], "total": t["total"]} for t in typed],
                      "match": match, "note": o.get("notes")})
        fails.append("G4 source (events,total) pairs do not map one-to-one onto the served F4B slots -- "
                     "a served number or the arm direction differs from the held source")
    rec["arm_observations"] = typed
    rec["extractor_notes"] = o.get("notes")
    rec["reasons"] = fails
    if diffs:
        rec["state"] = "SOURCE_DIFFERS"
        rec["source_differs"] = diffs
    elif fails:
        rec["state"] = "SET_ASIDE"
    else:
        rec["state"] = "BOUND"
    return rec


def main():
    jobs = sys.argv[1]
    pop = json.load(open(POP, encoding="utf-8"))
    outdir = os.path.join(BASE, "records")
    os.makedirs(outdir, exist_ok=True)
    counts = {}
    rows = []
    for r in pop["rows"]:
        rec = check_row(r, jobs)
        rec["served_ref"] = pop["ref"]
        json.dump(rec, open(os.path.join(outdir, r["row_id"] + ".json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        counts[rec["state"]] = counts.get(rec["state"], 0) + 1
        rows.append({"row_id": r["row_id"], "state": rec["state"], "reasons": rec["reasons"]})
    summ = {"served_ref": pop["ref"], "N": len(pop["rows"]), "counts": counts, "rows": rows}
    json.dump(summ, open(os.path.join(BASE, "SUMMARY.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps(counts), "of", len(pop["rows"]))


if __name__ == "__main__":
    main()
