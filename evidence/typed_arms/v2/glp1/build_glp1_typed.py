"""Typed per-arm / per-field witnesses (schema v2) for the two 3-point MACE rows the evidence lane adjudicated for
admission to the GLP-1 primary pool: FLOW and ELIXA (evidence/glp1_adjudication/{FLOW,ELIXA}.json, queued for
Mahmood's signature -- this file serves nothing and changes no number).

What it adds to those decisions: their witnesses are quoted spans with a file hash; the per-arm counts were assigned
to arms by reading a table's COLUMN ORDER. Here every count and denominator is a character range in the ONE text
representation (evidence/scripts/textrep.py render, pinned PDF extractor), each arm's role is read from TWO
independent anchors that must agree, and each per-field witness (contrast, population, analysis, timepoint) becomes
a located range. It REFUSES -- writes nothing for that trial -- when:
  * a held file's sha256 differs from the one the decision recorded;
  * an anchor span is absent or occurs more than once;
  * a number is not a whole token inside its anchor, or the column header is not the nearest one above the row;
  * the two role anchors disagree, or disagree with the decision's per-arm events;
  * the four arm coordinates are not distinct.
usage: python evidence/typed_arms/v2/glp1/build_glp1_typed.py [--check]"""
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "evidence", "scripts"))
import textrep  # noqa: E402  (the evidence lane's one text representation)

OUT = os.path.join(HERE, "OBSERVATIONS_glp1_mace.json")
REP = f"evidence/scripts/textrep.py render ({textrep.PDF_EXTRACTOR[0]} {textrep.PDF_EXTRACTOR[1]} for PDF)"
LABEL = "outputs/handover/glp1_regulatory/held/209637s025lbl.pdf"
STATR = "outputs/handover/glp1_regulatory/held/208471Orig1s000StatR.pdf"
FLOW_REG = "evidence/held/registry/NCT03819153.json"


class Refused(Exception):
    pass


_cache = {}


def doc(ref):
    if ref not in _cache:
        raw = open(os.path.join(ROOT, ref), "rb").read()
        _cache[ref] = (hashlib.sha256(raw).hexdigest(), textrep.render(ref))
    return _cache[ref]


def once(ref, span, lo=0, hi=None):
    """(start, end) of the ONE occurrence of span in render(ref)[lo:hi]."""
    t = doc(ref)[1]
    hi = len(t) if hi is None else hi
    i = t.find(span, lo, hi)
    if i < 0:
        raise Refused(f"{ref}: anchor absent: {span[:80]!r}")
    if t.find(span, i + 1, hi) >= 0:
        raise Refused(f"{ref}: anchor occurs more than once: {span[:80]!r}")
    return i, i + len(span)


def token(ref, value, lo, hi, nth=0, pattern=None):
    """Range of the nth whole-token occurrence of `value` in render(ref)[lo:hi]."""
    t = doc(ref)[1]
    pat = pattern or r"(?<![\d.,])" + re.escape(value) + r"(?![\d.,]\d)"
    hits = [m for m in re.finditer(pat, t[lo:hi])]
    if len(hits) <= nth:
        raise Refused(f"{ref}: token {value!r} (occurrence {nth}) not in anchor [{lo}:{hi}]")
    m = hits[nth]
    return lo + m.start(), lo + m.end()


def witness(ref, rng, role, **extra):
    sha, t = doc(ref)
    return dict(role=role, document_ref=ref, document_sha256=sha, representation=REP, text=t[rng[0]:rng[1]],
                start=rng[0], end=rng[1], **extra)


def field(ref, recorded_sha, span):
    """A decision's quoted field witness, located: exact and unique in the same representation."""
    sha, _ = doc(ref)
    if sha != recorded_sha:
        raise Refused(f"{ref}: held bytes changed (recorded {recorded_sha[:12]}, now {sha[:12]})")
    s, e = once(ref, span)
    return witness(ref, (s, e), "field")


def num(text):
    return int(text.replace(",", ""))


def check_sha(ref, recorded):
    if doc(ref)[0] != recorded:
        raise Refused(f"{ref}: held bytes changed (recorded {recorded[:12]}, now {doc(ref)[0][:12]})")


# ------------------------------------------------------------------------------------------------ FLOW
# Anchors are found by their LABEL TEXT only; every number is parsed from the held bytes, so two anchors that read
# different numbers disagree and the trial is refused (never "agree" because the expected numbers were typed in).
def once_re(ref, pattern, lo=0, hi=None):
    """The ONE regex match of pattern in render(ref)[lo:hi] (positions absolute)."""
    t = doc(ref)[1]
    hi = len(t) if hi is None else hi
    ms = list(re.compile(pattern).finditer(t, lo, hi))
    if len(ms) != 1:
        raise Refused(f"{ref}: anchor {pattern[:70]!r} matched {len(ms)} times (need exactly 1)")
    return ms[0]


def flow(dec):
    br = dec["bound_result"]
    check_sha(LABEL, br["endpoint"]["sha256"])
    t = doc(LABEL)[1]
    # anchor A: the label table. The label carries a MACE row for two trials (SUSTAIN 6 and FLOW), so the table is
    # found by its caption naming FLOW; the row is the first MACE row after that header, with no header between.
    HEAD = re.compile(r"(Placebo|OZEMPIC[\w ]*?) N=(\d+) \(%\) (Placebo|OZEMPIC[\w ]*?) N=(\d+)")
    head = once_re(LABEL, r"in FLOW Trial " + HEAD.pattern)
    head = HEAD.search(t, head.start())
    row = re.compile(r"Composite of cardiovascular death, non-fatal myocardial infarction, non-fatal stroke "
                     r"\(time to first occurrence\) (\d+) \([\d.]+\) (\d+) \([\d.]+\)").search(t, head.end())
    if row is None or HEAD.search(t, head.end(), row.start()):
        raise Refused("FLOW label: no MACE row directly under the FLOW table header")
    role_of = lambda label: ("comparator" if re.search(r"placebo", label, re.I) else
                             "intervention" if re.search(r"ozempic|semaglutide", label, re.I) else None)
    col_roles = [role_of(head.group(1)), role_of(head.group(3))]
    if sorted(col_roles, key=str) != ["comparator", "intervention"]:
        raise Refused(f"FLOW label: header columns {head.group(1)!r}/{head.group(3)!r} do not name both arms")
    a_events = {col_roles[0]: int(row.group(1)), col_roles[1]: int(row.group(2))}
    ev_rng = {col_roles[0]: row.span(1), col_roles[1]: row.span(2)}
    totals = {col_roles[0]: int(head.group(2)), col_roles[1]: int(head.group(4))}
    tot_rng = {col_roles[0]: head.span(2), col_roles[1]: head.span(4)}
    # anchor B: the registry's MACE measure, where each count sits beside its own group label
    R = doc(FLOW_REG)[1]
    title = once_re(FLOW_REG, r"RESULT OUTCOME (\d+) \[\w+\]: [^\n]*Time to First Occurrence of a Major Adverse "
                              r"Cardiovascular Event \(MACE\)")
    n_out = title.group(1)
    # every line of an outcome block carries its number ('RESULT OUTCOME 11 GROUP ...'); the block ends at the
    # first line with a DIFFERENT number
    later = [m.start() for m in re.finditer(r"\nRESULT OUTCOME (\d+)\b", R[title.end():]) if m.group(1) != n_out]
    nxt = title.end() + later[0] if later else len(R)
    meas = once_re(FLOW_REG, rf"RESULT OUTCOME {n_out} MEASUREMENT : Semaglutide=(\d+); Placebo=(\d+)", title.end(), nxt)
    den = once_re(FLOW_REG, rf"RESULT OUTCOME {n_out} DENOM Participants: Semaglutide=(\d+); Placebo=(\d+)",
                  title.end(), nxt)
    b = {"intervention": int(meas.group(1)), "comparator": int(meas.group(2))}
    b_tot = {"intervention": int(den.group(1)), "comparator": int(den.group(2))}
    return build("FLOW", dec, "semaglutide 1 mg once weekly", "placebo", a_events, ev_rng, totals, tot_rng, LABEL,
                 anchors=[{"kind": "COLUMN_ORDER_UNDER_HEADER", "document_ref": LABEL,
                           "header": witness(LABEL, head.span(), "header"), "row": witness(LABEL, row.span(), "row"),
                           "roles": a_events},
                          {"kind": "GROUP_LABELLED_REGISTRY_MEASURE", "document_ref": FLOW_REG,
                           "outcome": f"RESULT OUTCOME {n_out}",
                           "measurement": witness(FLOW_REG, meas.span(), "measurement"),
                           "denominator": witness(FLOW_REG, den.span(), "denominator"),
                           "roles": b, "totals": b_tot}],
                 fields={k: br[k]["witness"] for k in ("contrast", "population")} | {
                     "analysis": br["analysis"]["witness"], "timepoint": br["timepoint"]["witness"]},
                 extra_checks=[(b_tot, totals, "registry denominators vs the label header")])


# ------------------------------------------------------------------------------------------------ ELIXA
def elixa(dec):
    br = dec["bound_result"]
    check_sha(STATR, br["endpoint"]["sha256"])
    t = doc(STATR)[1]
    # anchor A: the prose 'respectively' sentence (the bound, unrounded source); the order of the arm NAMES decides
    pr = once_re(STATR, r"(\d+) and (\d+) in (placebo|lixisenatide) and (placebo|lixisenatide) group, respectively")
    if pr.group(3) == pr.group(4):
        raise Refused("ELIXA prose: the 'respectively' sentence names one arm twice")
    name_role = {"placebo": "comparator", "lixisenatide": "intervention"}
    a_events = {name_role[pr.group(3)]: int(pr.group(1)), name_role[pr.group(4)]: int(pr.group(2))}
    ev_rng = {name_role[pr.group(3)]: pr.span(1), name_role[pr.group(4)]: pr.span(2)}
    # anchor B: Table 8 -- its header names the columns; the on-study MACE row below it, no other header between
    hd = once_re(STATR, r"Table 8: Analysis of the MACE Endpoint (Placebo|Lixisenatide) \(N=([\d,]+)\) "
                        r"(Placebo|Lixisenatide) \(N=([\d,]+)\)")
    row = once_re(STATR, r"MACE endpoint \(on-study\) [\d.]+ \([\d.]+, [\d.]+\) No\. of patients with event \(%\) "
                         r"(\d+) \([\d.]+%\) (\d+) \([\d.]+%\)", hd.end())
    if re.search(r"\(N=[\d,]+\)", t[hd.end():row.start()]):
        raise Refused("ELIXA Table 8: the column header is not the nearest header above the MACE row")
    cols = [name_role[hd.group(1).lower()], name_role[hd.group(3).lower()]]
    if sorted(cols) != ["comparator", "intervention"]:
        raise Refused("ELIXA Table 8: header does not name both arms")
    b = {cols[0]: int(row.group(1)), cols[1]: int(row.group(2))}
    totals = {cols[0]: num(hd.group(2)), cols[1]: num(hd.group(4))}
    tot_rng = {cols[0]: hd.span(2), cols[1]: hd.span(4)}
    return build("ELIXA", dec, "lixisenatide", "placebo", a_events, ev_rng, totals, tot_rng, STATR,
                 anchors=[{"kind": "PARALLEL_ORDER_RESPECTIVELY", "document_ref": STATR,
                           "sentence": witness(STATR, pr.span(), "sentence"), "roles": a_events},
                          {"kind": "COLUMN_ORDER_UNDER_HEADER", "document_ref": STATR,
                           "header": witness(STATR, hd.span(), "header"), "row": witness(STATR, row.span(), "row"),
                           "roles": b}],
                 fields={k: br[k]["witness"] for k in ("contrast", "population", "analysis")})


# ------------------------------------------------------------------------------------------------ common
def build(trial, dec, i_name, c_name, events, ev_rng, totals, tot_rng, ev_ref, anchors, fields, extra_checks=()):
    for a in anchors:
        if a["roles"] != events:
            raise Refused(f"{trial}: role anchors disagree: {a['kind']} reads {a['roles']}, the bound source {events}")
    want = {"intervention": dec["bound_result"]["events"][i_name.split()[0]],
            "comparator": dec["bound_result"]["events"]["placebo"]}
    if want != events:
        raise Refused(f"{trial}: the decision's per-arm events {want} differ from the witnessed {events}")
    for got, exp, what in extra_checks:
        if got != exp:
            raise Refused(f"{trial}: {what} {got} differ from {exp}")
    obs = []
    for role, name in (("intervention", i_name), ("comparator", c_name)):
        ew = witness(ev_ref, ev_rng[role], f"{role}.events")
        tw = witness(ev_ref, tot_rng[role], f"{role}.total", derivation=None)
        if num(ew["text"]) != events[role] or num(tw["text"]) != totals[role]:
            raise Refused(f"{trial} {role}: witnessed token is not the value")
        obs.append({"role": role, "arm_name": name, "arm_id": name.lower().strip(), "events": events[role],
                    "total": totals[role], "n": totals[role], "event_witness": ew, "total_witness": tw,
                    "role_anchors": [a["kind"] for a in anchors]})
    coords = {(w["document_ref"], w["start"], w["end"]) for o in obs for w in (o["event_witness"], o["total_witness"])}
    if len(coords) != 4:
        raise Refused(f"{trial}: arm coordinates are not distinct ({len(coords)} of 4)")
    located = {}
    for k, w in fields.items():
        located[k] = field(w["ref"], w["sha256"], w["span"])
    return {"trial": trial, "nct": dec["nct"], "pmid": dec["pmid"], "outcome": "3-point MACE",
            "decision": f"evidence/glp1_adjudication/{trial}.json", "decision_status": dec["status"],
            "estimate": dec["bound_result"]["estimate"], "ci": dec["bound_result"]["ci"],
            "observations": obs, "role_anchors": anchors, "field_witnesses": located}


def main(check=False):
    out, refused = {"schema": "count-observations-v2 (typed arms) + role anchors + located field witnesses",
                    "serves": "nothing: admission of FLOW and ELIXA waits on Mahmood's signature",
                    "rows": {}}, {}
    for trial, fn in (("FLOW", flow), ("ELIXA", elixa)):
        dec = json.load(open(os.path.join(ROOT, "evidence", "glp1_adjudication", f"{trial}.json"), encoding="utf-8"))
        try:
            out["rows"][trial] = fn(dec)
        except Refused as e:
            refused[trial] = str(e)
    out["refused"] = refused
    text = json.dumps(out, indent=1, ensure_ascii=False) + "\n"
    if check:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else None
        if cur != text:
            print("STALE: OBSERVATIONS_glp1_mace.json differs from a rebuild")
            return 1
        print("current")
        return 0
    open(OUT, "w", encoding="utf-8", newline="\n").write(text)
    print(f"written {sorted(out['rows'])}; refused {refused}")
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
