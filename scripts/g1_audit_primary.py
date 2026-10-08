"""AUDIT (Mahmood 5 Oct: "a second, independent codex reader re-verifying every PRIMARY row already counted in matched
topics, as a recorded audit; log any disagreement as a finding"). One RECORDED, replayable codex call per counted PRIMARY
row (reproducible_ai.model_call_live.call, `codex exec` with stdin </dev/null), concurrency from G1_CODEX_CONCURRENCY.

Independence: the reader sees ONLY the held source material of the trial -- its abstract record, any held open text, its
posted CT.gov results (AACT snapshot, rendered as text) and any held regulatory section -- with the topic outcome. It
never sees our value, the comparator's, or the first reader's answer; its instructions and schema are its own (they also
admit per-arm mean / SD / N, so a combined multi-arm row can be re-derived).

Gate (unchanged machinery): harness.secondary_meta.gate_locator_claim -- the quote is verbatim in the held material and
every number copied is printed in the quote. Only a gated reading is compared; the comparison is deterministic:
  COUNTS     events_t, n_t, events_c, n_c equal                         -> CONFIRMED, else DISAGREE
  EFFECT_CI  point and both bounds equal at the printed precision        -> CONFIRMED (a re-expressed interval is compared
             as PRINTED, ci_printed)
  ARMS       the reader's per-arm rows, roled by g1_binding_aact.arm_role and combined by Handbook 6.5.2.10, equal ours
  otherwise  READER_NOT_REPORTED / READER_REFUSED_BY_GATE / NOT_COMPARABLE (named; a finding only when it disagrees)
Prompts that embed non-redistributable full text are written OUTSIDE the repository (AUDIT_PRIVATE_DIR); abstract-,
AACT- and US-government-only prompts are committed under evidence/model_calls/audit.

    python scripts/g1_audit_primary.py SLUG ... [--run]   -> outputs/k_gap/g1_binding/audit_primary.json
    python scripts/g1_audit_primary.py --staged-counts [--run] -> outputs/k_gap/g1_binding/audit_staged_counts.json
      the same independent reader against the STAGED own-trial counts (bindings_counts.json; close-4, D12-gated): the
      reader never sees them, so its answer is compared with them exactly as with a counted row
"""
from __future__ import annotations

import base64
import concurrent.futures as cf
import shutil
import csv
import hashlib
import io
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from harness import secondary_meta as sm  # noqa: E402
from kgap import aact_adapter, runs_store  # noqa: E402
from reproducible_ai import model_call_live as mcl  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402
import g1_binding_aact as ba  # noqa: E402
import g1_extraction_diagnosis as dg  # noqa: E402
import k_gap_forest_plot as fp  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding")
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "audit")
PRIVATE = os.environ.get("AUDIT_PRIVATE_DIR", "C:/mh-tmp/binding/held_records/audit")
MAX_CHARS = 150000
PUBLIC_SOURCES = {"ABSTRACT", "AACT", "REGULATORY"}

INSTR = """You are an independent auditor. You are given the held source material of ONE randomised trial (its abstract,
possibly its open text, its posted ClinicalTrials.gov results rendered as text, possibly a regulatory document section)
and ONE outcome. Find where the material gives the BETWEEN-ARM RESULT for exactly that outcome.
- POPULATION: if EVIDENCE UNIT names a subgroup of the trial, report THAT subgroup's result, not the whole trial;
  otherwise report the whole randomised population (intention-to-treat), not a subgroup or per-protocol analysis.
- TIMEPOINT: if the material reports the outcome at the stated TIMEPOINT (or the nearest equivalent the trial uses,
  e.g. day 28 for 30 days), report that; otherwise the trial's own primary timepoint. Copy the time frame you used into
  timepoint, as printed.
- QUOTE: ONE contiguous passage of the material, character for character (for a table: the consecutive flattened rows
  exactly as they appear). Never stitch text from different places.
Copy the numbers exactly as printed in your quote, never computed: per-arm events and totals (events_t/n_t intervention,
events_c/n_c control) and/or the effect with its confidence limits; for a continuous outcome copy EVERY arm's mean, SD
and N into arms (label as printed). Put in point/lower/upper ONLY an effect in the measure named by ESTIMAND (a risk difference or a percentage
is not one: leave them null then). Use null for anything not printed in your quote. Do not quote a different
endpoint. If the material does not report it, state=NOT_REPORTED."""

SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["state", "quote", "measure", "point", "lower", "upper", "ci_level", "events_t", "n_t", "events_c",
                       "n_c", "arms", "timepoint"],
          "properties": {"state": {"type": "string", "enum": ["REPORTED", "NOT_REPORTED"]},
                         "quote": {"type": ["string", "null"]}, "measure": {"type": ["string", "null"]},
                         "point": {"type": ["string", "null"]}, "lower": {"type": ["string", "null"]},
                         "upper": {"type": ["string", "null"]}, "ci_level": {"type": ["string", "null"]},
                         "timepoint": {"type": ["string", "null"]},
                         "events_t": {"type": ["string", "null"]}, "n_t": {"type": ["string", "null"]},
                         "events_c": {"type": ["string", "null"]}, "n_c": {"type": ["string", "null"]},
                         "arms": {"type": ["array", "null"], "items": {
                             "type": "object", "additionalProperties": False, "required": ["label", "mean", "sd", "n"],
                             "properties": {"label": {"type": "string"}, "mean": {"type": ["string", "null"]},
                                            "sd": {"type": ["string", "null"]}, "n": {"type": ["string", "null"]}}}}}}


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


_POSTED, _DESC = {}, {}


def preload(ncts):
    """ONE pass over the snapshot's measurement / count / outcome tables for every NCT (a pass per trial took minutes
    each on the snapshot drive)."""
    cp = os.environ.get("AUDIT_AACT_CACHE", "C:/mh-tmp/binding/aact_posted_cache.json")
    snap = (aact_adapter.snapshot() or {}).get("id")
    if not _POSTED and cp and os.path.exists(cp):
        c = _j(cp)
        if c.get("snapshot") == snap:                      # a cache of THIS snapshot only
            _POSTED.update({k: tuple(v) for k, v in c["posted"].items()})
            _DESC.update(c["desc"])
    want = sorted(set(ncts) - set(_POSTED))
    if want:
        _POSTED.update(ba._posted_arms(want))
        _DESC.update(ba.outcome_descriptions(want))
        if cp:
            with open(cp, "w", encoding="utf-8") as fh:
                json.dump({"snapshot": snap, "posted": _POSTED, "desc": _DESC}, fh)


def aact_text(nct):
    """The trial's posted results as text: every outcome (type, title, time frame, population, description), each
    group's measurement and count, and every analysis. Public domain (CT.gov)."""
    reg = aact_adapter.registry_for(nct)
    if not reg:
        return ""
    preload([nct])
    meas, counts = _POSTED[nct]
    desc = _DESC
    gt_ = reg.get("group_titles") or {}
    lines = [f"ClinicalTrials.gov posted results {nct} ({(reg.get('_snapshot') or {}).get('id')})"]
    for oid, o in (reg.get("outcomes") or {}).items():
        lines.append(f"OUTCOME [{o.get('type')}] {o.get('title')} | time frame: {o.get('time_frame')} | population: "
                     f"{o.get('population')} | {desc.get(oid, '')}")
        for r in meas.get(oid, []):
            g = r["result_group_id"]
            lines.append(f"  {gt_.get(g, g)}: {r.get('param_type')} {r.get('param_value')}"
                         + (f" ({r.get('dispersion_type')} {r.get('dispersion_value')})" if r.get("dispersion_value") else "")
                         + (f" N={counts.get(oid, {}).get(g)}" if counts.get(oid, {}).get(g) else ""))
        for a in reg.get("analyses") or []:
            if a["outcome_id"] == oid:
                lines.append(f"  analysis: {a.get('param_type')} {a.get('param_value')} [{a.get('ci_lower')}, "
                             f"{a.get('ci_upper')}] groups {[gt_.get(g, g) for g in a.get('groups') or []]}")
    return "\n".join(lines)


def counted_rows(slug, T):
    """Every matched trial on a PRIMARY route with our counted value: (trial dict, our value incl. arms when the pool row
    carries them). The pool's own row is captured where topic() turns it into a pair (as_row), so a continuous pool row
    keeps its mean / SD / N."""
    import g1_tracker as gt
    seen, by_id = {}, {}
    orig, orig_v = gt.as_row, gt.our_value_from_row

    def spy(primary, label, measure_hint=None):
        if primary:
            seen.setdefault(label, primary)
        return orig(primary, label, measure_hint)

    def spy_v(t):
        v = orig_v(t)
        if v:
            by_id.setdefault(str(t.get("id")).replace("PMID ", ""), v)
        return v
    gt.as_row, gt.our_value_from_row = spy, spy_v
    try:
        o = gt.topic(slug, T)
    finally:
        gt.as_row, gt.our_value_from_row = orig, orig_v
    out = []
    for x in o["trials"]:
        if gt.is_matched(x) and x.get("route") in ("PRIMARY", "SECONDARY_SINGLE") and \
                (x.get("our_value") or seen.get(x["label"])):
            v = dict(by_id.get(str(x.get("family") or "").replace("PMID ", "")) or seen.get(x["label"]) or {})
            v.update({k: val for k, val in (x.get("our_value") or {}).items() if val is not None})
            out.append((x, v))
    return o, out


def trial_ncts(slug, x):
    fam = str(x.get("family") or "")
    pmid = fam.replace("PMID ", "")
    recs = {str(r.get("id")): r for r in _j(os.path.join(ROOT, "cache", slug, "records.json")).get("records", [])}
    rec = recs.get(pmid) or {}
    ncts = set(re.findall(r"NCT\d{8}", json.dumps([x.get("registry_binding"), x.get("confirm_binding"), rec.get("nct")])))
    tg = next((t for t in _j(os.path.join(OUT, "targets.json")) if t["slug"] == slug and t["label"] == x["label"]), {})
    return ncts | set(tg.get("ncts") or []) | set(table_row(slug, x["label"]).get("ncts") or []) | set(re.findall(r"NCT\d{8}", fam))


_KROWS = {}


def table_row(slug, label):
    """The trial's k-gap table row (its PMIDs and NCTs), whatever id family the pool used (a trial pooled under its NCT
    has family 'NCT...', not a PMID: TRANSFORM-3)."""
    if not _KROWS:
        for r in _j(os.path.join(ROOT, "outputs", "k_gap", "k_gap_table.json"))["trials"]:
            _KROWS[(r["slug"], r["label"][:60])] = r
    return _KROWS.get((slug, label[:60])) or {}


def held_material(slug, x):
    """[(source kind, text)] for one trial: abstract record, held open text, AACT posted results, regulatory section."""
    fam = str(x.get("family") or "")
    pmid = fam.replace("PMID ", "") if fam.startswith("PMID ") else ((table_row(slug, x["label"]).get("pmids") or [None])[0])
    recs = {str(r.get("id")): r for r in _j(os.path.join(ROOT, "cache", slug, "records.json")).get("records", [])}
    rec = recs.get(pmid) or _j(os.path.join(ROOT, "outputs", "k_gap", "member_records.json")).get(pmid or "")
    if not rec:
        tg = next((t for t in _j(os.path.join(OUT, "targets.json")) if t["slug"] == slug and t["label"] == x["label"]), {})
        pmid = (tg.get("pmids") or [None])[0]
        rec = recs.get(pmid or "") or _j(os.path.join(ROOT, "outputs", "k_gap", "member_records.json")).get(pmid or "")
    texts = list(dg.held_texts(slug, pmid, rec)) if pmid else []
    if rec and (rec.get("abstract") or "").strip():
        texts.append(("ABSTRACT", ((rec.get("title") or "") + "\n" + rec["abstract"]).strip()))
    ncts = set(re.findall(r"NCT\d{8}", json.dumps([x.get("registry_binding"), x.get("confirm_binding"), (rec or {}).get("nct")])))
    tg = next((t for t in _j(os.path.join(OUT, "targets.json")) if t["slug"] == slug and t["label"] == x["label"]), {})
    ncts |= set(tg.get("ncts") or []) | set(table_row(slug, x["label"]).get("ncts") or []) | set(re.findall(r"NCT\d{8}", fam))
    for n in sorted(ncts):
        t = aact_text(n)
        if t:
            texts.append(("AACT", t))
    src = (x.get("confirm_binding") or {}).get("source") or ""
    m = re.search(r"\(held (cache/regulatory/[^)]+)\)", src)
    if m and os.path.exists(os.path.join(ROOT, m.group(1))):
        texts.append(("REGULATORY", open(os.path.join(ROOT, m.group(1)), encoding="utf-8").read()))
    return pmid, texts


def evidence_unit(cfg, x, pmid):
    """The TOPIC PROTOCOL's declared evidence unit for this trial (topics/<slug>.json trial_annotations), never our value:
    e.g. JUPITER's pre-specified >=70-years subgroup. 'whole trial' otherwise."""
    ann = (cfg.get("primary_outcome") or {}).get("trial_annotations") or {}
    a = ann.get(str(pmid)) or next((v for k, v in ann.items() if k in str(x.get("family") or "")), None) or {}
    if a.get("evidence_unit") == "prespecified_subgroup":
        return f"pre-specified subgroup ({a.get('evidence_unit_detail') or ''}; the trial label: {x['label']})"
    return "whole trial"


def item(slug, cfg, x, ours):
    import g1_licence as _lic
    pmid, texts = held_material(slug, x)
    texts, dropped = _lic.gate(pmid, texts, offline=os.environ.get("G1_LICENCE_OFFLINE") == "1")
    po = cfg["primary_outcome"]
    # full text (copyright material, licence-gated) inside the recorder guard's <<<TEXT block, declared in its form;
    # public-domain material (PubMed abstract, CT.gov posted results, FDA text) outside it under explicit headers
    full = [(r, t) for r, t in texts if r not in _lic.ALWAYS]
    pub = [(r, t) for r, t in texts if r in _lic.ALWAYS]
    body = ("\n\n".join(f"=== {ref} (public domain / abstract) ===\n{t}" for ref, t in pub)
            + ("\n\n<<<TEXT\n" + "\n\n".join(f"=== {ref} ===\n{t}" for ref, t in full) + "\nTEXT>>>" if full else ""))[:MAX_CHARS]
    p = (INSTR + f"\n\nOUTCOME: {po['name']}\nWORDS FOR IT: {', '.join(po.get('keywords') or [])}\n"
         f"TIMEPOINT: {po.get('timepoint') or 'as reported'}\nEVIDENCE UNIT: {evidence_unit(cfg, x, pmid)}\nESTIMAND: {po.get('estimand') or 'as reported'}\nINTERVENTION: {', '.join(cfg.get('intervention_terms') or [])}\n"
         f"CONTROL: {', '.join(cfg.get('comparator_terms') or [])}\n<<<MATERIAL\n{body}\nMATERIAL>>>\n").encode("utf-8")
    kinds = sorted({ref for ref, _ in texts})
    return {"slug": slug, "label": x["label"], "pmid": pmid, "ours": ours, "prompt": p, "text": body, "kinds": kinds,
            "public": True, "key": f"audit::{slug}::{x['label']}", "agents": ba.topic_agents(cfg),
            "licence_dropped": dropped, "full_kinds": sorted({r for r, _ in full})}


def digests(it):
    return [{"ref": f"held open text PMID {it['pmid']} ({'+'.join(it['full_kinds'] or ['NONE'])})",
             "sha256": hashlib.sha256(it["text"].encode("utf-8")).hexdigest(),
             "what": f"held material shown, first {MAX_CHARS} chars; outside the TEXT block: "
                     f"{'+'.join(k for k in it['kinds'] if k not in it['full_kinds'])} "
                     f"(PubMed abstract / ClinicalTrials.gov posted results / US FDA text)"}]


def call(it, model):
    rec = mcl.call(it["prompt"], schema=json.loads(json.dumps(SCHEMA)), model=model, effort=fp.EFFORT,
                   caller={"file": "scripts/g1_audit_primary.py", "line": "call",
                           "purpose": f"G1 audit: independent re-read of the counted PRIMARY row {it['slug']} / {it['label']}"},
                   input_digests=[{"ref": f"held open text PMID {it['pmid']} ({'+'.join(it['full_kinds'] or ['NONE'])})",
                                   "sha256": hashlib.sha256(it["text"].encode("utf-8")).hexdigest(),
                                   "what": f"held material shown, first {MAX_CHARS} chars; outside the TEXT block: "
                                           f"{'+'.join(k for k in it['kinds'] if k not in it['full_kinds'])} "
                                           f"(PubMed abstract / ClinicalTrials.gov posted results / US FDA text)"}],
                   timeout_s=1500)
    d = REC_DIR if it["public"] else PRIVATE
    ms.write_record(rec, d)
    return it["key"], {"record_id": rec["record_id"], "state": rec["state"], "dir": "public" if it["public"] else "private",
                       "prompt_sha256": hashlib.sha256(it["prompt"]).hexdigest()}


def gate(claim, text):
    """harness.secondary_meta.gate_locator_claim, unchanged; plus the SAME two rules for per-arm continuous rows (which
    that gate does not read): the quote is verbatim in the material and every arm mean / SD / N copied is printed in the
    quote with its sign."""
    ok, why = sm.gate_locator_claim(claim, text)
    if ok:
        return True, why
    arms = [a for a in claim.get("arms") or [] if a.get("mean") or a.get("sd") or a.get("n")]
    if not arms or why not in ("NO_NUMBERS_COPIED", "INCOMPLETE"):
        return False, why
    q = sm._fold_text(claim["quote"])
    qn = q.replace(",", "")
    for a in arms:
        for k in ("mean", "sd", "n"):
            v = sm._as_number(a.get(k)) if a.get(k) not in (None, "") else None
            if v is None:
                return False, f"ARM_{k.upper()}_MISSING_OR_NON_NUMERIC"
            if not re.search(r"(?<![\d.])" + re.escape(v.lstrip("-")) + r"(?![\d])", qn):
                return False, "ARM_NUMBER_NOT_IN_QUOTE"
            if v.startswith("-") and not re.search(r"-\s?" + re.escape(v.lstrip("-")) + r"(?![\d])", qn):
                return False, "ARM_SIGN_NOT_IN_QUOTE"
    return True, "ACCEPTED_ARMS"


def _eq(a, b):
    return sm._eq_printed(str(a), str(b)) if a is not None and b is not None else False


def _count(v):
    """A count as PRINTED: an integer, thousands separators allowed. A decimal ('100.0') is not a count -- stripping its
    non-digits made '100.0' read 1000 and confirm a denominator ten times too large (codex binding-v8-fe3ed2a7:g1#4)."""
    t = str(v).strip().replace("\u2009", " ").replace("\u202f", " ").replace("\u00a0", " ")
    # thousands grouping must be GROUPING, one separator throughout: '1,000' / '1 000' are 1000; '100,5' is a decimal
    # comma, never 1005 (codex v8-p1-fixes g1#4; v8-round3 g1#2)
    if not re.fullmatch(r"\d{1,3}(?:,\d{3})+|\d{1,3}(?: \d{3})+|\d+", t):
        raise ValueError(f"not a count: {v!r}")
    return int(t.replace(",", "").replace(" ", ""))


_MEASURE = {"HR": "HR", "HAZARD RATIO": "HR", "RR": "RR", "RISK RATIO": "RR", "RELATIVE RISK": "RR", "OR": "OR",
            "ODDS RATIO": "OR", "MD": "MD", "MEAN DIFFERENCE": "MD", "SMD": "SMD", "IRR": "IRR", "RATE RATIO": "IRR"}


def _measure(m):
    return _MEASURE.get(re.sub(r"\s+", " ", str(m or "")).strip().upper())


def compare(claim, ours, agents):
    """Deterministic comparison of a GATED reading with our counted value."""
    c = {k: claim.get(k) for k in ("events_t", "n_t", "events_c", "n_c")}
    if all(c.values()) and ours.get("events_t") is not None:
        try:
            got = [_count(c[k]) for k in ("events_t", "n_t", "events_c", "n_c")]
        except ValueError:
            return "NOT_COMPARABLE", "COUNTS_NOT_INTEGERS"
        same = got == [int(ours[k]) for k in ("events_t", "n_t", "events_c", "n_c")]
        return ("CONFIRMED" if same else "DISAGREE"), "COUNTS"
    if claim.get("events_t") and claim.get("events_c") and ours.get("events_t") is not None:
        try:
            got = [_count(claim[k]) for k in ("events_t", "events_c")]
        except ValueError:
            return "NOT_COMPARABLE", "COUNTS_NOT_INTEGERS"
        same = got == [int(ours["events_t"]), int(ours["events_c"])]
        return ("CONFIRMED_EVENTS_ONLY" if same else "DISAGREE"), "EVENTS"
    arms = [a for a in claim.get("arms") or [] if a.get("mean") and a.get("sd") and a.get("n")]
    if len(arms) >= 2 and ours.get("mean_t") is not None:
        roled = [dict(a, role=ba.arm_role(a["label"], agents), title=a["label"]) for a in arms]
        if sum(a["role"] == "control" for a in roled) == 1 and all(a["role"] for a in roled):
            try:
                # the PRINTED minus may be an en dash / U+2212 ('–19.0', TRANSFORM-1's own table): parsed by the
                # shared number reader, never by float() on the raw string
                v = ba.arms_values([dict(a, mean=sm._as_number(a["mean"]), sd=sm._as_number(a["sd"]),
                                         n=re.sub(r"[^\d]", "", a["n"])) for a in roled])
            except (ValueError, StopIteration):
                return "NOT_COMPARABLE", "ARMS_UNPARSEABLE"
            same = (abs(float(v["mean_t"]) - float(ours["mean_t"])) < 1e-3 and abs(float(v["sd_t"]) - float(ours["sd_t"])) < 1e-3
                    and int(v["n_t"]) == int(ours["n_t"]) and abs(float(v["mean_c"]) - float(ours["mean_c"])) < 1e-3
                    # the control arm's SD too (g1#3: a wrong sd_c was CONFIRMED)
                    and abs(float(v["sd_c"]) - float(ours["sd_c"])) < 1e-3
                    and int(v["n_c"]) == int(ours["n_c"]))
            return ("CONFIRMED" if same else "DISAGREE"), "ARMS"
        return "NOT_COMPARABLE", "ARMS_ROLES_NOT_RESOLVED"
    printed = ours.get("ci_printed") or {}
    lo, hi = printed.get("lower", ours.get("lower")), printed.get("upper", ours.get("upper"))
    if claim.get("point") and claim.get("lower") and claim.get("upper") and ours.get("effect") is not None:
        # the same numbers under different measures are different results (g1#5: an HR 'confirmed' an RR)
        mc, mo = _measure(claim.get("measure")), _measure(ours.get("measure") or ours.get("scale"))
        if mc and mo and mc != mo:                     # stated and different; an unstated measure is not a contradiction
            return "NOT_COMPARABLE", f"MEASURE_DIFFERS:{claim.get('measure')}/{ours.get('measure') or ours.get('scale')}"
        same = _eq(claim["point"], ours["effect"]) and _eq(claim["lower"], lo) and _eq(claim["upper"], hi)
        return ("CONFIRMED" if same else "DISAGREE"), "EFFECT_CI"
    return "NOT_COMPARABLE", "NO_OVERLAPPING_FIELDS"


def staged_rows():
    """{slug: [(trial dict, our value)]} from the STAGED own-trial counts: the trial carries its PMID family and its NCT
    (as a registry candidate, so held_material reads its posted results); the value is the staged count tuple."""
    out = {}
    for b in _j(os.path.join(OUT, "bindings_counts.json")).get("bindings") or []:
        x = {"label": b["label"], "family": f"PMID {b['pmid']}" if b.get("pmid") else None,
             "registry_binding": {"candidates": [{"nct": n} for n in b.get("ncts") or []]}}
        out.setdefault(b["slug"], []).append((x, dict(b["values"], measure="COUNTS")))
    return out


def main(argv):
    import g1_tracker  # noqa: F401  (import before the spy)
    run = "--run" in argv
    model = argv[argv.index("--model") + 1] if "--model" in argv else fp.MODEL
    slugs = [a for a in argv if not a.startswith("--") and a != model]
    T = _j(os.path.join(ROOT, "outputs", "k_gap", "k_gap_table.json"))
    items, states = [], {}
    per = {}
    staged = "--staged-counts" in argv
    if staged:
        per = staged_rows()
        slugs = sorted(per)
        states = {s: "STAGED_COUNTS" for s in slugs}
        for s in slugs:
            print(s, "staged count rows", len(per[s]), flush=True)
    for s in ([] if staged else slugs):
        o, rows = counted_rows(s, T)
        states[s], per[s] = (o.get("g1_status") or {}).get("state"), rows
        print(s, states[s], "counted PRIMARY rows", len(rows), flush=True)
    preload({n for s in slugs for x, _ in per[s] for n in trial_ncts(s, x)})
    for s in slugs:
        cfg = _j(os.path.join(ROOT, "topics", s + ".json"))
        items += [item(s, cfg, x, v) for x, v in per[s]]
    runs = runs_store.load()
    # ledger recovered from the RECORDS (prompt sha256 match): a call whose ledger entry was lost is never paid twice
    want = {hashlib.sha256(it["prompt"]).hexdigest(): it for it in items}
    for d, kind in ((REC_DIR, "public"), (PRIVATE, "private")):
        for f in (sorted(os.listdir(d)) if os.path.isdir(d) else []):
            if not f.endswith(".json"):
                continue
            rec = ms.load_record(os.path.join(d, f))
            sha = hashlib.sha256(base64.b64decode((rec.get("prompt") or {}).get("b64") or "")).hexdigest()
            it = want.get(sha)
            if it and rec.get("state") == "RAN_OK" and (runs.get(it["key"]) or {}).get("prompt_sha256") != sha:
                runs[it["key"]] = {"record_id": rec["record_id"], "state": "RAN_OK", "dir": kind, "prompt_sha256": sha,
                                   "recovered_from_record": True}
    todo = [it for it in items if it["text"].strip() and ((runs.get(it["key"]) or {}).get("prompt_sha256")
                                                         != hashlib.sha256(it["prompt"]).hexdigest()
                                                         or (runs.get(it["key"]) or {}).get("state") != "RAN_OK")]
    if run and todo:
        remote = todo[1::2] if os.environ.get("G1_REMOTE_SHARE") == "1" else []
        local = [it for it in todo if it not in remote]

        def run_remote():
            import g1_remote_codex as rc
            jobs = [{"key": it["key"], "prompt": it["prompt"], "schema": SCHEMA, "model": model, "effort": fp.EFFORT,
                     "caller": {"file": "scripts/g1_audit_primary.py", "line": "call", "purpose":
                                f"G1 audit: independent re-read of the bound row {it['slug']} / {it['label']}"},
                     "input_digests": digests(it), "timeout_s": 1500} for it in remote]
            res = rc.submit(jobs, "audit", concurrency=int(os.environ.get("G1_CODEX_CONCURRENCY", "5"))) if jobs else {}
            out = {}
            for it in remote:
                v = res.get(it["key"]) or {}
                if v.get("record_path"):
                    shutil.copy(v["record_path"], os.path.join(REC_DIR, v["record_id"] + ".json"))
                    out[it["key"]] = {"record_id": v["record_id"], "state": v["state"], "dir": "public", "host": "worker",
                                      "prompt_sha256": hashlib.sha256(it["prompt"]).hexdigest()}
                else:
                    print(it["key"], "WORKER", v.get("error"), flush=True)
            return out
        with cf.ThreadPoolExecutor(max_workers=1) as rex:
            fut = rex.submit(run_remote)
            with cf.ThreadPoolExecutor(max_workers=int(os.environ.get("G1_CODEX_CONCURRENCY", "5"))) as ex:
                for key, r in ex.map(lambda it: call(it, model), local):
                    runs[key] = r
                    print(key, r["state"], r["record_id"], r["dir"], flush=True)
            for key, r in fut.result().items():
                runs[key] = r
                print(key, r["state"], r["record_id"], "worker", flush=True)
    runs_store.save(runs, slugs=set(slugs))
    rows, tally = [], Counter()
    for it in items:
        r = runs.get(it["key"]) or {}
        claim, verdict, basis, why = None, "NOT_RUN", None, "no recorded call for this prompt"
        if not it["text"].strip():
            verdict, why = "NO_HELD_MATERIAL", "nothing held to read"
        elif r.get("prompt_sha256") == hashlib.sha256(it["prompt"]).hexdigest() and r.get("state") == "RAN_OK":
            d = REC_DIR if r.get("dir") == "public" else PRIVATE
            claim = json.loads(ms.replay(ms.load_record(os.path.join(d, r["record_id"] + ".json"))).decode("utf-8"))
            if claim.get("state") != "REPORTED":
                verdict, why = "READER_NOT_REPORTED", "the independent reader found no between-arm result"
            else:
                ok, why = gate(claim, it["text"])
                if not ok and why == "INCOMPLETE":
                    # the gate reached INCOMPLETE only after its quote / number / sign checks passed: the copied numbers ARE
                    # printed in a verbatim quote, just not a full tuple -- compared as a PARTIAL reading, labelled as such
                    verdict, basis = compare(claim, it["ours"], it["agents"])
                    verdict = verdict if verdict == "DISAGREE" else f"PARTIAL_{verdict}"
                    why = "gated partial reading (INCOMPLETE tuple) compared with our counted value"
                elif not ok:
                    verdict = "READER_REFUSED_BY_GATE"
                else:
                    verdict, basis = compare(claim, it["ours"], it["agents"])
                    why = "gated reading compared with our counted value"
        tally[verdict] += 1
        rows.append({"slug": it["slug"], "topic_state": states.get(it["slug"]), "label": it["label"], "pmid": it["pmid"],
                     "sources": it["kinds"], "record_id": r.get("record_id"), "record_dir": r.get("dir"),
                     "verdict": verdict, "basis": basis, "why": why,
                     "ours": {k: it["ours"].get(k) for k in ("measure", "effect", "lower", "upper", "events_t", "n_t", "events_c",
                                                             "n_c", "mean_t", "sd_t", "mean_c", "sd_c", "ci_printed")
                              if it["ours"].get(k) is not None},
                     "reader": claim})
    out = {"n": len(rows), "tally": dict(tally), "findings": [x for x in rows if x["verdict"] == "DISAGREE"], "rows": rows}
    with open(os.path.join(OUT, "audit_staged_counts.json" if staged else "audit_primary.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps({"n": out["n"], "tally": out["tally"]}))
    for x in rows:
        print(f"  {x['verdict']:24s} {x['slug'][:14]} {x['label'][:40]} {x['basis'] or ''} {x['sources']}")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
