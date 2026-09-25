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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ownership  # noqa: E402  (G7)

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
POP = os.path.join(BASE, "population.json")
WORDS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                    "fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def numbers_in(text):
    """(value, is_not_a_count) for every number token in text. '4,949' and '4 949' are 4949; '47·4%' is a
    percentage. Spelled numbers up to twenty are read ('four of 119'). Not a count (review, 2026-09-25): a percentage
    in words ('20 percent'), a per-mille, a European decimal ('20,5%'), a dose ('10 mg'), a rate denominator
    ('per 100 patient-years'), a name's number ('GLP-1', 'COVID-19'), and 'one' in 'at least one'."""
    t = unicodedata.normalize("NFKC", text).replace(" ", " ").replace(" ", " ")
    out = []
    for m in re.finditer(r"(?<![\d.·])(?<![A-Za-z]-)(\d{1,3}(?:[, ]\d{3})+|\d+)(?:[.·]\d+|,\d{1,2}(?!\d))?"
                         r"(\s*(?:%|‰|percent\b|per\s*cent\b))?", t):
        raw = m.group(1)
        if " " in raw and not re.fullmatch(r"\d{1,3}(?: \d{3})+", raw):
            continue
        whole = m.group(0)
        is_dec = bool(re.search(r"[.·]\d|,\d{1,2}$", whole))
        not_count = re.match(r"\s*(?:mg|µg|mcg|g|ml|mmol|IU|units?)\b|\s*(?:patient|person)-years", t[m.end():], re.I) \
            or re.search(r"\bper\s*$", t[max(0, m.start() - 5):m.start()], re.I)
        out.append((int(re.sub(r"[, ]", "", raw)), bool(m.group(2)) or is_dec or bool(not_count)))
    for m in re.finditer(r"\b(" + "|".join(WORDS) + r")\b(?!-[a-z])", t, flags=re.I):
        if re.search(r"\b(?:at least|more than|fewer than|less than)\s*$", t[max(0, m.start() - 12):m.start()], re.I):
            continue
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
    occ, i = [], at
    while i >= 0:
        occ.append(i)
        i = text.find(span["text"], i + 1)
    return {"document": d["origin"], "document_sha256": d.get("origin_sha256"), "copy_sha256": d["sha256"],
            "file": span["file"], "start": at, "end": at + len(span["text"]), "text": span["text"],
            "occurrences": occ}


def at_occurrence(loc, start):
    out = dict(loc)
    out["start"], out["end"] = start, start + len(loc["text"])
    return out


def own_everywhere(doc, loc, value, partner, j, typed, vals):
    """Ownership for a span whose text may occur more than once. Location-free relations (adjacency, order, versus)
    read only the span text. Location-bound ones (table column, registry group) are evaluated at EVERY occurrence and
    must agree -- a span that is one thing here and another there has no single owner."""
    rels = {ownership.owns(doc, at_occurrence(loc, s), value, partner, j, typed, vals) for s in loc["occurrences"]}
    return rels.pop() if len(rels) == 1 else None


def reg_active_words(a):
    """What a registry arm actively gives: its active interventions, and its label with every 'placebo X' /
    'matching X' / 'dummy X' phrase removed (a placebo arm's label names the drug it imitates)."""
    lab = a.get("label")
    lab = str(lab.get("value") if isinstance(lab, dict) else (lab or "")).lower()
    lab = re.sub(r"\b(?:placebo|matching|dummy)(?:\s+(?:to|for|of))?\s+[\w+-]+", " ", lab)
    return " ".join([lab] + [str(x).lower() for x in (a.get("active_interventions") or [])])


def reg_words(a):
    """The words a registry arm states about itself: its design-group label value, its intervention names."""
    lab = a.get("label")
    drug = a.get("drug")
    bits = [str(lab.get("value") if isinstance(lab, dict) else (lab or ""))]
    bits += [str(x) for x in (a.get("active_interventions") or [])]
    if isinstance(drug, dict):
        bits += [str(x) for x in (drug.get("value") or [])]
    return " ".join(bits).lower()


# Static, disclosed: class words in the review's I-line expanded to the member names a source prints instead.
CLASS_MEMBERS = {
    "corticosteroids": ["hydrocortisone", "methylprednisolone", "prednisone", "prednisolone", "dexamethasone", "corticosteroid", "glucocorticoid", "steroid"],
    "probiotics": ["probiotic", "lactobacillus", "lactobacilli", "saccharomyces", "boulardii", "bifidobacterium", "bifidobacteria", "streptococcus", "yogurt", "yoghurt", "kefir", "synbiotic", "vsl", "clostridium", "bacillus"],
    "dpp-4": ["sitagliptin", "saxagliptin", "alogliptin", "linagliptin", "gliptin"],
    "glp-1": ["liraglutide", "semaglutide", "dulaglutide", "albiglutide", "efpeglenatide", "exenatide", "lixisenatide"],
    "omega-3": ["omega-3", "fish oil", "icosapent", "epa", "dha", "n-3"],
    "crystalloid": ["balanced", "plasma-lyte", "plasmalyte", "ringer", "lactated", "multiple electrolyte"],
}
GENERIC = set("added usual standard care therapy including daily once weekly alone same background regimen trial arms both "
              "specifically solution supportive medical guideline based heart failure receptor antagonist agonist "
              "interleukin development name subcutaneous intranasal newly initiated oral antidepressant systemic "
              "antimicrobial named genera strains fermented products peri operative low dose supplementation acids "
              "fatty marine carboxylic ethyl inhibitor inhibitors buffered ovulation induction low-dose acid "
              "heart failure alone medical therapy guideline newly initiated peri operative once weekly".split())
# control vocabulary, including a NEGATED intervention ('non-probiotic', 'steroid-free', 'without corticosteroids',
# 'heat-killed Lactobacillus', 'vehicle', 'observation') -- review, 2026-09-25: these read as the intervention before
CONTROL = re.compile(r"\b(placebo|usual care|standard care|standard of care|standard treatment|control|no probiotic|"
                     r"no treatment|sham|dummy|vehicle|observation|without|heat[- ]killed|inactivated|pasteuri[sz]ed)\b|"
                     r"\bnon[- ][a-z]|\b[a-z]+-free\b|^\s*no[- ][a-z]|\balone\b", re.I)


def i_terms(iline):
    """Intervention words from the review's I-line. Only what precedes 'added to' / 'in addition to' / 'on top of':
    the background therapy an intervention is added to is not the intervention (review, 2026-09-25)."""
    t = re.split(r"\b(?:added to|in addition to|on top of|alone or)\b", (iline or "").lower())[0]
    words = {w for w in re.findall(r"[a-z][a-z0-9+-]{2,}", t)
             if w not in GENERIC and len(w) >= 4 and not all(p in GENERIC for p in w.split("-") if p)}
    for cls, members in CLASS_MEMBERS.items():
        if cls.split("-")[0] in t:
            words.update(members)
    return words


def side(text, terms):
    """A term matches as a whole word (an optional plural 's'): 'acid' is not in 'acids'-less 'folic acid' unless it
    is a term, and 'omega-3' never matches 'omega-6' (review, 2026-09-25: prefix matching)."""
    return any(re.search(r"(?<![a-z0-9])" + re.escape(w) + r"(?:e?s)?(?![a-z0-9])", text) for w in terms)


def label_side(label_txt, terms):
    """A source arm label is ON the review's intervention line if it names the intervention and is not control vocabulary."""
    return side(label_txt, terms) and not CONTROL.search(label_txt)


def reg_side(a, terms):
    """A registry arm is ON the line by its ACTIVE interventions, or by its own label when that label names the
    intervention and carries no control vocabulary. Never by its drug field: a placebo arm's drug field often names the
    drug it imitates ('Dapagliflozin matching placebo')."""
    lab = a.get("label")
    lab = str(lab.get("value") if isinstance(lab, dict) else (lab or "")).lower()
    return (side(" ".join(str(x) for x in (a.get("active_interventions") or [])).lower(), terms)
            or (side(lab, terms) and not CONTROL.search(lab)))


def abbreviation(label, job, docs):
    """If the label is an abbreviation the source defines ('prolonged-release melatonin (PRM)'), return the expansion
    with its span. Only a definition printed in a held document of this row counts."""
    core = re.sub(r"\b(group|arm)\b", "", label or "", flags=re.I).strip()
    if not core or len(core) > 12:
        return None
    for f in docs:
        text = open(os.path.join(job, f), "rb").read().decode("utf-8", errors="replace")
        m = re.search(r"([A-Za-z][A-Za-z0-9\-]*(?:[ \u00a0][A-Za-z0-9\-]+){0,5})\s*\(\s*" + re.escape(core) + r"\s*\)", text)
        if m:
            return {"expansion": m.group(1), "file": f, "text": m.group(0), "start": m.start(), "end": m.end()}
    return None


def source_label_id(label):
    """A row-local identity from the source's arm name: 'LcS group' and 'LcS' are the same arm. (The blind
    re-extraction found the first version keeping 'group', so one arm got two ids.)"""
    core = re.sub(r"\b(group|arm)s?\b", " ", (label or "").lower())
    return re.sub(r"[^a-z0-9]+", "-", core).strip("-")


def resolve_arm(arm, reg_arms, family_id, iline, fails, idx, expansion=None):
    """-> (arm_id, basis). The extractor's registry_arm_id is a PROPOSAL; the gate re-derives the link itself."""
    terms = i_terms(iline)
    label = (arm.get("arm_label") or "")
    label_txt = (label + " " + ((expansion or {}).get("expansion") or "")).lower()
    lon = label_side(label_txt, terms)
    rid = arm.get("registry_arm_id")
    if not reg_arms:
        lab = source_label_id(label)
        if not lab:
            fails.append(f"G5 arm {idx}: no arm label to derive an id from")
            return None, None
        return f"{family_id}#arm:{lab}", "SOURCE_LABEL (no registry arms held for this family)"
    by = {a.get("arm_id"): a for a in reg_arms}
    if rid is not None and rid not in by:
        fails.append(f"G5 arm {idx}: registry_arm_id {rid!r} is not an arm of family {family_id}")
        return None, None
    toks = [w for w in re.findall(r"[a-z][a-z0-9-]{3,}", label_txt)
            if w not in ("group", "arm", "patients", "participants", "assigned", "receive", "receiving", "with", "plus")]

    def link(a):
        if not CONTROL.search(label_txt):
            # an intervention label is linked by the registry arm's OWN active words -- its active interventions and
            # its label with 'placebo X' / 'matching X' removed -- which is evidence independent of the label's side
            # (review, 2026-09-25); an arm that only imitates the drug ('Placebo Drugx') never matches
            hit = [w for w in toks if re.search(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", reg_active_words(a))]
            if hit:
                return "intervention word match: " + ", ".join(sorted(set(hit)))
        if reg_side(a, terms) != lon:
            return None
        hit = [w for w in toks if re.search(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", reg_words(a))]
        if hit:   # matched only on the label's own side: NOT independent evidence for G6
            return "side-coupled label match: " + ", ".join(sorted(set(hit)))
        if len(reg_arms) == 2 and terms:
            other = [x for x in reg_arms if x is not a][0]
            if reg_side(other, terms) != lon:
                return ("role match via the review's intervention line: source label and registry arm both "
                        f"{'on' if lon else 'off'} it, the family's other arm {'off' if lon else 'on'} it")
        return None
    why = " (source defines the label: " + repr(expansion["text"]) + ")" if expansion else ""
    if rid in by and link(by[rid]):
        return rid, "REGISTRY_ARM (" + link(by[rid]) + ")" + why
    oks = [a for a in reg_arms if link(a)]
    if len(oks) == 1:
        return oks[0]["arm_id"], ("REGISTRY_ARM derived by the gate (" + link(oks[0]) + "); extractor proposed "
                                  + repr(rid)) + why
    same_side = [a for a in reg_arms if reg_side(a, terms) == lon]
    def factors(a):  # the arm's OTHER factor: active interventions that are not the review's intervention
        return frozenset(x.lower() for x in (a.get("active_interventions") or []) if not side(str(x).lower(), terms))
    other_side = [a for a in reg_arms if reg_side(a, terms) != lon]
    is_factorial = (len({factors(a) for a in same_side}) == len(same_side) > 1
                    and {factors(a) for a in same_side} == {factors(a) for a in other_side})
    if len(reg_arms) > 2 and len(oks) > 1 and is_factorial and {a["arm_id"] for a in oks} == {a["arm_id"] for a in same_side}:
        ids = sorted(a["arm_id"] for a in oks)
        return "+".join(ids), ("FACTORIAL_MARGIN: the source arm pools every registry arm on its side of the review's "
                               "intervention line, which differ only by a second factor mirrored on the other side ("
                               + ", ".join(ids) + ")") + why
    sig = {(re.sub(r"\d+", "", reg_words(a)).strip()) for a in reg_arms}
    if len(sig) == 1:
        lab = source_label_id(label)
        return f"{family_id}#arm:{lab}", ("SOURCE_LABEL: registry arms are held but NON-DISCRIMINATING (every arm states "
                                          f"the same interventions: {sorted(sig)[0][:80]!r}); ownership rests on the source")
    fails.append(f"G5 arm {idx}: label {label!r} links to {len(oks)} registry arms of {family_id} (need exactly one)")
    return None, None


def direction(typed, iline, reg_arms):
    """Return (index of experimental arm or None, evidence list). Never reads served slots.
    Score per arm: +1 label on the intervention line, -2 control vocabulary in the label, +1/-1 registry arm on/off the
    line (0 when no registry arm is linked). Resolved only for two arms with a unique best that has no control
    vocabulary, and only if some evidence is non-zero."""
    reg_by_id = {a.get("arm_id"): a for a in (reg_arms or [])}
    terms = i_terms(iline)
    ev = []
    for j, t in enumerate(typed):
        label_txt = ((t.get("arm_label") or "") + " " + ((t.get("abbreviation") or {}).get("expansion") or "")).lower()
        on = label_side(label_txt, terms)
        ctrl = bool(CONTROL.search(label_txt))
        members = [reg_by_id[x] for x in str(t.get("arm_id") or "").split("+") if x in reg_by_id]
        # the registry arm is INDEPENDENT evidence only when it was linked by its own words; a link made through the
        # label's side ('role match') merely echoes the label and is not counted (review, 2026-09-25)
        independent = bool(members) and "word match" in str(t.get("arm_id_basis") or "")
        rs = all(reg_side(m, terms) for m in members) if independent else None
        ev.append({"arm": j, "label_on_intervention_line": on, "control_vocabulary": ctrl, "registry_on_line": rs})
    if len(typed) != 2:
        return None, ev
    # every piece of evidence VOTES for an experimental arm; resolved only with >= 2 votes, all for the same arm
    # (review, 2026-09-25: one matched substring against nothing used to resolve)
    votes = []
    for j, e in enumerate(ev):
        o = 1 - j
        if e["label_on_intervention_line"] and not e["control_vocabulary"]:
            votes.append(["label", j])
        if e["control_vocabulary"] and not e["label_on_intervention_line"]:
            votes.append(["control_vocabulary", o])
        if e["registry_on_line"] is True:
            votes.append(["registry", j])
        elif e["registry_on_line"] is False:
            votes.append(["registry", o])
    ev.append({"votes": votes})
    voted = {j for _, j in votes}
    # an explicit control label on one arm alone is sufficient ('Active' vs 'Control'); any other single vote -- a
    # label merely containing an intervention word -- is not
    if len(voted) == 1 and (len(votes) >= 2 or votes[0][0] == "control_vocabulary"):
        return voted.pop(), ev
    return None, ev


OUTCOME_STOP = set("with from after within during least one episode development primary secondary outcome outcomes "
                   "endpoint endpoints measure measures main rate rates number patients participants those were that this "
                   "events event occurred severe serious any all cause total overall reported study".split())
OUTCOME_SYN = {"death": ("death", "died", "dead", "mortal", "fatal"), "mortal": ("death", "died", "dead", "mortal", "fatal")}


def outcome_stems(*texts):
    """Content-word stems (first 5 letters) of the outcome span and the served outcome name, plus abbreviations
    ('POAF', 'AAD') and a closed death/mortality synonym set."""
    stems = set()
    for t in texts:
        stems.update(a.lower() for a in re.findall(r"\b[A-Z]{2,6}\b", t or ""))   # abbreviations: 'AAD', 'POAF'
        for w in re.findall(r"[A-Za-z][A-Za-z-]{3,}", t or ""):
            lw = w.lower()
            if lw in OUTCOME_STOP:
                continue
            if w.isupper() and len(w) <= 6:
                stems.add(lw)                       # an abbreviation matches whole
                continue
            stems.update(OUTCOME_SYN.get(lw[:5] if lw[:5] in OUTCOME_SYN else lw[:6], ()) or (lw[:5],))
    return stems


def sentence_at(doc, pos):
    """The sentence holding pos. A break is '. ' before a capital or '(', or a newline -- not ';', which also sits
    inside '(6.2%; 95% CI ...)'. A sentence opening with an anaphor ('They', 'These', 'This', 'It', 'Such') is
    joined to the one before it, which names what it refers to."""
    brk = re.compile(r"\.\s+(?=[A-Z(])|\n")
    starts = [0] + [m.end() for m in brk.finditer(doc, 0, pos)]
    a = starts[-1]
    m = brk.search(doc, pos)
    b = m.start() if m else len(doc)
    if re.match(r"\s*(?:They|These|Those|This|It|Such)\b", doc[a:b]) and len(starts) >= 2:
        a = starts[-2]
    return doc[a:b]


def outcome_tied(job, es, oc, outcome_name=None):
    """True when the events span is tied to the outcome (review, 2026-09-25, 'a nausea sentence bound as the death
    count'): the events span's OWN sentence names the outcome (a content-word stem of the outcome span or the served
    outcome name), or the events span overlaps / shares the sentence, <table> or registry measure/AE term of an
    occurrence of the outcome span."""
    doc = open(os.path.join(job, es["file"]), "rb").read().decode("utf-8")
    sent = (sentence_at(doc, es["start"]) + " " + es["text"]).lower()
    for st in outcome_stems(oc["text"], outcome_name):
        if re.search(r"(?<![a-z])" + re.escape(st), sent):
            return True
    if es["file"] != oc["file"]:
        return False
    for o in oc.get("occurrences") or [oc["start"]]:
        oe = o + len(oc["text"])
        if o < es["end"] and es["start"] < oe:
            return True
        a, b = sorted((o, es["start"]))
        if b - a < 600 and not re.search(r"[.;]\s+[A-Z(]|\n\s*\n", doc[a:b]):
            return True
        t0 = doc.rfind("<table", 0, es["start"])
        if t0 >= 0 and t0 == doc.rfind("<table", 0, o) and doc.find("</table>", t0) > max(o, es["start"]):
            return True
        spans = sorted((sp for sp in ownership.object_spans(doc) if sp[0] <= es["start"] < sp[1] and sp[0] <= o < sp[1]),
                       key=lambda sp: sp[1] - sp[0])
        for sa, sb in spans[:1]:
            body = doc[sa:sb]
            if '"groups":' in body or '"term":' in body or '"eventGroups":' in body:
                return True
    return False


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
        abbr = abbreviation(a.get("arm_label"), job, docs)
        aid, basis = resolve_arm(a, r.get("registry_arms"), r["family_id"], r.get("intervention_i_line"), fails, i, abbr)
        typed.append({"arm_id": aid, "arm_id_basis": basis, "arm_label": a.get("arm_label"), "arm_label_span": ls,
                      "events": ev, "total": tot, "total_basis": a.get("total_basis"),
                      "percentage_text": a.get("percentage_text"), "events_span": es, "total_span": ts,
                      "outcome": shared.get("outcome"), "population": shared.get("population"),
                      "window": shared.get("window"), "f4b_slot": None, "abbreviation": abbr,
                      "events_ownership": None, "total_ownership": None})
    # G5: two source arms never share a registry arm (review, 2026-09-25: a code-named arm and 'placebo' both resolved
    # to the placebo arm and bound)
    idsets = [set(str(t["arm_id"]).split("+")) for t in typed if t["arm_id"]]
    if any(idsets[a] & idsets[b] for a in range(len(idsets)) for b in range(a + 1, len(idsets))):
        fails.append("G5 two source arms resolve to the same registry arm")
    # G10: the label span must name the arm it labels (the label feeds G5 and G6)
    for i, t in enumerate(typed):
        ls = t.get("arm_label_span")
        names = [re.sub(r"\b(group|arm)s?\b", "", (t.get("arm_label") or ""), flags=re.I).strip(" ,.:").lower(),
                 ((t.get("abbreviation") or {}).get("expansion") or "").lower()]
        if ls and not any(n and n in re.sub(r"\s+", " ", ls["text"].lower()) for n in names):
            fails.append(f"G10 arm {i}: its label span does not name {t.get('arm_label')!r}")
    # G9: each events span must be tied to the OUTCOME -- it overlaps an occurrence of the outcome span, or shares its
    # sentence, table or registry measure (review, 2026-09-25: a nausea sentence bound as the death count)
    oc = shared.get("outcome") and shared["outcome"].get("span")
    for i, t in enumerate(typed):
        es = t.get("events_span")
        if es and oc and not outcome_tied(job, es, oc, r.get("outcome_name")):
            fails.append(f"G9 arm {i}: the events span is not in the outcome's sentence, table or registry measure")
    # G7: every arm OWNS its events and its denominator in the text, by a named relation (ownership.py)
    docs_text = {}
    def doc_of(loc):
        if loc and loc["file"] not in docs_text:
            docs_text[loc["file"]] = open(os.path.join(job, loc["file"]), "rb").read().decode("utf-8")
        return docs_text.get(loc["file"]) if loc else None
    ev_vals = {j: t["events"] for j, t in enumerate(typed)}
    tot_vals = {j: t["total"] for j, t in enumerate(typed)}
    for j, t in enumerate(typed):
        if t["events_span"] and isinstance(t["events"], int):
            t["events_ownership"] = own_everywhere(doc_of(t["events_span"]), t["events_span"], t["events"], t["total"], j, typed, ev_vals)
            if not t["events_ownership"]:
                fails.append(f"G7 arm {j}: events {t['events']} are printed in the span but the text does not tie them to "
                             f"{t['arm_label']!r} (OWNERSHIP_UNVERIFIED)")
        if not (t["total_span"] and isinstance(t["total"], int)):
            continue
        tdoc = doc_of(t["total_span"])
        if t.get("events_ownership") == "GROUP_ID" and '"groupId"' in t["total_span"]["text"]:
            # registry JSON: the denominator is bound to the occurrence inside the SAME outcome measure as the events.
            # The events' measure must be single-valued; exactly one denominator occurrence may sit in it.
            edefs = {ownership.group_def(doc_of(t["events_span"]), at_occurrence(t["events_span"], s))[0]
                     for s in t["events_span"]["occurrences"]}
            same = [s for s in t["total_span"]["occurrences"]
                    if len(edefs) == 1 and t["total_span"]["file"] == t["events_span"]["file"]
                    and ownership.group_def(tdoc, at_occurrence(t["total_span"], s))[0] in edefs]
            if len(same) == 1:
                t["total_span"] = at_occurrence(t["total_span"], same[0])
                t["total_span"]["occurrences"] = same
                t["total_span"]["located_by"] = "the occurrence inside the events' outcome measure"
                t["total_ownership"] = ownership.owns(tdoc, t["total_span"], t["total"], None, j, typed, tot_vals)
            else:
                t["total_ownership"] = None
                fails.append(f"G7 arm {j}: denominator {t['total']}: {len(same)} occurrences of its quoted text lie in the "
                             f"events' outcome measure (need exactly one)")
                continue
        else:
            t["total_ownership"] = own_everywhere(tdoc, t["total_span"], t["total"], None, j, typed, tot_vals)
        if not t["total_ownership"]:
            fails.append(f"G7 arm {j}: denominator {t['total']} is printed in the span but the text does not tie it to "
                         f"{t['arm_label']!r} (OWNERSHIP_UNVERIFIED)")
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
    elif (len(typed) == 2 and slots["ai/n1i"] == slots["ci/n2i"] and len(match["ai/n1i"]) == 2
          and not any(f.startswith(("G1 arm", "G2 arm", "G3 arm")) for f in fails)):
        # IDENTICAL arms (e.g. 9/120 vs 9/120): numbers cannot say which slot is whose, and need not -- any mapping
        # serves the same numbers. The slots are assigned by G6 direction alone; unresolved direction sets aside.
        exp_j, dev = direction(typed, r.get("intervention_i_line"), r.get("registry_arms"))
        rec["direction_evidence"] = dev
        if exp_j is None:
            fails.append("G6 DIRECTION_UNRESOLVED (identical arm pairs): nothing independent says which arm is experimental")
        else:
            e, c = exp_j, 1 - exp_j
            typed[e]["f4b_slot"], typed[c]["f4b_slot"] = "ai/n1i", "ci/n2i"
            rec["comparator_direction"] = {"experimental_arm_id": typed[e]["arm_id"], "comparator_arm_id": typed[c]["arm_id"],
                                           "experimental_label": typed[e]["arm_label"], "comparator_label": typed[c]["arm_label"],
                                           "basis": "identical (events,total) in both arms; slots assigned by G6 direction evidence"}
    elif any(f.startswith(("G1 arm", "G2 arm", "G3 arm")) for f in fails):
        fails.append("G4 not evaluated: an arm's events or denominator is not bound to a printed number (G1-G3), so no "
                     "comparison with the served slots is made -- SET_ASIDE, not a served-number difference")
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
