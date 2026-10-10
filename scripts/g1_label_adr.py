"""FDA LABEL ADVERSE-REACTION ADAPTER (R9-4, binding lane, 9 Oct 2026). Typed; no model; US-government text only.

A drugs@FDA label's section 6 table ('Table 3: Adverse reactions reported in >= 1% of patients on <BRAND> and more
frequently than placebo in the phase 3 study FIDELIO-DKD') prints, for ONE trial's SAFETY population, each adverse
reaction's per-arm 'n (%)' under an 'N = ...' header. This adapter reads such a table from a HELD label
(registry/regulatory_sources.json; text digest-checked by g1_regulatory_source.doc_text) and proposes, for each of the
topic's harm outcomes, an ADR binding -- its own endpoint ('<harm> (FDA label adverse reaction, <TRIAL> safety
population)'), never the trial's published outcome.

A row is proposed only when ALL hold (each refusal is recorded by name):
  - the caption names exactly ONE trial, and that trial is one of the topic's named pivotal trials; a pooled table
    ('Pooled', 'pooled analysis', two trial names) is refused -- it is no single trial's tuple;
  - the header gives both arms, each with 'N = ...', the treatment arm named by the BRAND the label itself defines
    ('KERENDIA (finerenone)') or by the agent, the control by a comparator term; the arm order comes from the header;
  - the row label matches a harm outcome keyword (word boundary), and its two cells are 'n (p)' with p = 100 n / N at
    the printed precision;
  - the caption, header and row lie within one table's reach, in that order.
Served change: none here. A proposed binding is a V14 item (before/after) for Mahmood; the captain builds the notice.

    python scripts/g1_label_adr.py [--sweep]   -> outputs/k_gap/g1_binding/label_adr.json
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "label_adr.json")
REACH = 4000
# the table HEAD only: its caption is cut from the text up to the arm header (codex r9-4-label-r1 #5: a lookahead for a
# blank line found no table at all when none followed within 400 characters)
_CAP = re.compile(r"Table\s+(\d+)\s*[:.]\s*Adverse\s+reactions?\b", re.I)
_CELL = r"(\d{1,3}(?:,\d{3})*|\d+)\s*\(\s*(\d+(?:\.\d+)?)\s*%?\s*\)"


def _ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


def brand_of(text, agents):
    """The brand the label itself defines for one of the agents: 'KERENDIA (finerenone)' -> 'kerendia'."""
    for a in agents:
        m = re.search(r"\b([A-Z][A-Za-z\-]{2,})\s*(?:®|\(R\))?\s*\(\s*" + re.escape(a) + r"\s*\)", text, re.I)
        if m and m.group(1).lower() != a.lower():
            return m.group(1).lower()
    return None


def _pct_ok(n, N, p):
    dec = len(p.split(".")[1]) if "." in p else 0
    return abs(100.0 * n / N - float(p)) <= 0.5 * 10 ** (-dec) + 1e-9


_HEADER = re.compile(r"([A-Za-z][A-Za-z \-]{1,40}?)\s*N\s*=\s*([\d,]+)\s*n\s*\(%\)\s*([A-Za-z][A-Za-z \-]{1,40}?)\s*N\s*="
                     r"\s*([\d,]+)\s*n\s*\(%\)", re.I)
_NEXT_TABLE = re.compile(r"\bTable\s+\d+\s*[:.]", re.I)
_TRIAL_SHAPED = re.compile(r"\b[A-Z][A-Z0-9]{2,}(?:-[A-Z0-9]{2,})+\b|\b[A-Z]{4,}\b")
_NOT_SAFETY = re.compile(r"\brandomi[sz]ed\b|\bintent(?:ion)?[- ]to[- ]treat\b|\bITT\b|\bfull analysis\b", re.I)


def tables(text, cfg, names):
    """[(proposal | None, why, context)] for every adverse-reaction table in a label's text. names: {registered
    acronym (upper case): trial PMID} for the topic's pivotal trials (trial_names).
    Codex r9-4-label-r1: a table's rows end at the NEXT table (#1); a caption naming any other trial-shaped name refuses
    the table (#2); a caption / header stating a randomised or ITT set is not the safety contract (#3); the caption ends
    where the arm header begins, blank line or not (#5); a zero N is a recorded refusal (#6)."""
    agents = [a.lower() for v in (cfg.get("intervention_agents") or {}).values() for a in v] or \
        [a.lower() for a in cfg.get("intervention_terms") or []]
    brand = brand_of(text, agents)
    trt = set(agents) | ({brand} if brand else set())
    ctl = {c.lower() for c in cfg.get("comparator_terms") or []}
    out = []
    starts = [m.start() for m in _CAP.finditer(text)]
    for i, st in enumerate(starts):
        m = _CAP.match(text, st)
        nxt = _NEXT_TABLE.search(text, m.end())
        end = min(st + REACH, nxt.start() if nxt else len(text))
        span = _ws(text[st:end])
        hm = _HEADER.search(span)
        # the arm name is the LAST word before 'N =': the lazy group may start inside the caption ('...ALPHA-ONE a|nd
        # GAMMA-THREE ... Kerendia N =') -- the caption runs up to that word (codex r9-4-label-r1 #2)
        cut = (hm.start(1) + hm.group(1).rstrip().rfind(" ") + 1) if hm else len(span)
        cap = _ws(span[:cut])[:600]
        ctx = {"table": m.group(1), "caption": cap}
        named = [k for k in names if re.search(r"(?<![A-Z0-9])" + re.escape(k) + r"(?![A-Z0-9])", cap.upper())]
        others = {t for t in _TRIAL_SHAPED.findall(cap) if t.upper() not in names
                  and t.lower() not in trt and t.upper() not in ("FDA", "TABLE")}
        if re.search(r"\bpool", cap, re.I):
            out.append((None, "NOT_ONE_TRIAL:POOLED", ctx))
            continue
        if len(named) != 1 or others:
            out.append((None, f"NOT_ONE_TRIAL:{named}" + (f"+OTHERS:{sorted(others)}" if others else ""), ctx))
            continue
        if not hm:
            out.append((None, "NO_ARM_HEADER_WITH_N", ctx))
            continue
        if _NOT_SAFETY.search(cap) or _NOT_SAFETY.search(hm.group(0)):
            out.append((None, "POPULATION_NOT_SAFETY", ctx))
            continue
        a1, n1, a2, n2 = hm.group(1).strip().lower(), int(hm.group(2).replace(",", "")), hm.group(3).strip().lower(), \
            int(hm.group(4).replace(",", ""))
        if n1 <= 0 or n2 <= 0:
            out.append((None, "INVALID_DENOMINATOR", ctx))
            continue
        last = lambda s_: s_.split()[-1] if s_.split() else s_  # noqa: E731 -- 'Adverse reactions Kerendia' -> 'kerendia'
        r1, r2 = last(a1), last(a2)
        if r1 in trt and r2 in ctl:
            orient = "TC"
        elif r1 in ctl and r2 in trt:
            orient = "CT"
        else:
            out.append((None, f"ARMS_NOT_ORIENTED:{r1}|{r2}", ctx))
            continue
        ctx.update(trial=named[0], pmid=names[named[0]], header=hm.group(0), brand=brand)
        body = span[hm.end():]                       # rows of THIS table only: span ends at the next table
        rows = re.findall(r"([A-Z][A-Za-z ,/\-]{2,60}?)\s+" + _CELL + r"\s+" + _CELL, body)
        out.append(({"rows": rows, "n": (n1, n2), "orient": orient}, None, ctx))
    return out


def propose(slug, cfg, url, text, names):
    props, refused = [], []
    for got, why, ctx in tables(text, cfg, names):
        if not got:
            refused.append(dict(ctx, url=url, why=why))
            continue
        (n1, n2), orient = got["n"], got["orient"]
        for h in cfg.get("harm_outcomes") or []:
            kws = [k.lower() for k in h.get("keywords") or []] + [h["name"].lower()]
            hits = [r for r in got["rows"] if any(re.fullmatch(re.escape(k), r[0].strip().lower()) for k in kws)]
            if len(hits) != 1:
                refused.append(dict(ctx, url=url, harm=h["name"], why=f"ROWS_MATCHING:{len(hits)}"))
                continue
            lab, e1, p1, e2, p2 = hits[0]
            e1, e2 = int(e1.replace(",", "")), int(e2.replace(",", ""))
            if not (_pct_ok(e1, n1, p1) and _pct_ok(e2, n2, p2)):
                refused.append(dict(ctx, url=url, harm=h["name"], why="PERCENT_NOT_N_OVER_N"))
                continue
            et, nt, ec, nc = (e1, n1, e2, n2) if orient == "TC" else (e2, n2, e1, n1)
            props.append({"slug": slug, "harm_outcome": h["name"],
                          "endpoint": f"{h['name']} (FDA label adverse reaction, {ctx['trial']} safety population)",
                          "trial": ctx["trial"], "pmid": ctx["pmid"],
                          "population": "SAFETY (label adverse-reaction table)",
                          "values": {"events_t": et, "n_t": nt, "events_c": ec, "n_c": nc},
                          "row_span": f"{lab.strip()} {e1:,} ({p1}) {e2:,} ({p2})".replace(",", ""),
                          "caption_span": ctx["caption"], "header_span": ctx["header"], "brand": ctx.get("brand"),
                          "url": url, "licence": "US_GOV_PUBLIC_DOMAIN"})
    return props, refused


def trial_names(slugs, snap=None):
    """{slug: {registered acronym (upper): PMID}} for each topic's pivotal trials: PMID -> the held record's NCT -> the
    AACT snapshot's studies.txt acronym (one pass). No snapshot -> {} for every topic (fail closed: nothing is named)."""
    import csv
    snap = snap or os.environ.get("AACT_SNAPSHOT") or "F:/AACT-storage/AACT/2026-08-30"
    want = {}
    for slug in slugs:
        cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
        rp = os.path.join(ROOT, "cache", slug, "records.json")
        recs = {str(r.get("id")): r for r in json.load(open(rp, encoding="utf-8")).get("records", [])} \
            if os.path.exists(rp) else {}
        for pm in cfg.get("pivotal_trials") or []:
            nct = (recs.get(str(pm)) or {}).get("nct")
            if nct:
                want.setdefault(nct, []).append((slug, str(pm)))
    out = {s_: {} for s_ in slugs}
    p_ = os.path.join(snap, "studies.txt")
    if not want or not os.path.isfile(p_):
        return out
    csv.field_size_limit(10 ** 9)
    with open(p_, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="|"):
            for slug, pm in want.get(row.get("nct_id"), []):
                acr = (row.get("acronym") or "").strip().upper()
                if len(acr) >= 4:
                    out[slug][acr] = pm
    return out


def hold_labels(slug, cfg, per_agent=12):
    """Hold a topic's FDA LABELS only (typed discovery by the topic's agents; never a review, never an ANDA), with the
    same record shape and digest discipline as g1_regulatory_source.hold_topic. Returns the records written."""
    import g1_regulatory_source as rs
    import g1_trial_acquire as ga
    import k_gap_regulatory_probe as rp
    cur = rs._load(rs.SOURCES)
    held = []
    for a in rs.topic_agents(cfg):
        urls = [u for u in rs.fda_review_urls(a) if "/label/" in u][:per_agent]
        for u in urls:
            if not ga.disk_ok():
                return held
            if (cur.get(u) or {}).get("state") == "TEXT" and slug in (cur[u].get("topics") or []):
                continue
            txt, rec = rp.fetch_text(u)
            r = {"url": u, "agency": rs.agency_of(u), "licence": rs.licence_from_text(u, txt), "state": rec.get("state"),
                 "doc_sha256": rec.get("sha256"), "bytes": rec.get("bytes"),
                 "text_sha256": rs.text_sha256(txt) if txt else None, "text_chars": len(txt or ""),
                 "topics": sorted(set((cur.get(u) or {}).get("topics") or []) | {slug})}
            cur[u] = r
            held.append(r)
    rs._dump(rs.SOURCES, cur)
    return held


def held_labels(slug):
    import g1_regulatory_source as rs
    src = json.load(open(rs.SOURCES, encoding="utf-8"))
    return [u for u, r in sorted(src.items()) if slug in (r.get("topics") or []) and r.get("agency") == "FDA"
            and "/label/" in u and r.get("state") == "TEXT"]


def run(slugs):
    import g1_regulatory_source as rs
    res = {"rule": __doc__.split("\n\n")[0], "topics": {}}
    names = trial_names([s_ for s_ in slugs if held_labels(s_)])
    for slug in slugs:
        cfg = json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))
        if not cfg.get("harm_outcomes"):
            continue
        t = {"labels_held": 0, "proposals": [], "refused": []}
        for u in held_labels(slug):
            txt = rs.doc_text(u)
            if not txt:
                t["refused"].append({"url": u, "why": "TEXT_NOT_HELD_OR_DIGEST_CHANGED"})
                continue
            t["labels_held"] += 1
            p, r = propose(slug, cfg, u, txt, names.get(slug) or {})
            t["proposals"] += p
            t["refused"] += r
        # one proposal per (harm, trial): the same table reprinted in later labels must agree, else none
        by = {}
        for p in t["proposals"]:
            by.setdefault((p["harm_outcome"], p["trial"]), []).append(p)
        t["proposals"] = []
        for (h, tr), ps in sorted(by.items()):
            vals = {json.dumps(p["values"], sort_keys=True) for p in ps}
            if len(vals) == 1:
                t["proposals"].append(dict(ps[0], labels_agreeing=[p["url"] for p in ps]))
            else:
                t["refused"].append({"harm": h, "trial": tr, "why": f"LABELS_DISAGREE:{sorted(vals)}"})
        res["topics"][slug] = t
    res["sweep"] = {s: {"labels_held": t["labels_held"], "proposals": len(t["proposals"])} for s, t in res["topics"].items()}
    return res


READER_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["state", "quote", "events_t", "n_t", "events_c", "n_c", "population"],
    "properties": {"state": {"type": "string", "enum": ["FOUND", "NOT_REPORTED"]}, "quote": {"type": "string"},
                   "events_t": {"type": ["integer", "null"]}, "n_t": {"type": ["integer", "null"]},
                   "events_c": {"type": ["integer", "null"]}, "n_c": {"type": ["integer", "null"]},
                   "population": {"type": "string"}}}
READERS = {
    "A": "You are reader A. Below is a window of a US FDA drug label (US-government text, public domain). Find the "
         "adverse-reaction table for the named trial and the named adverse reaction. Quote, character for character, "
         "the table's arm header (with each arm's N) and the reaction's row. Copy: events_t / n_t for the drug arm, "
         "events_c / n_c for the placebo arm, exactly as printed; never compute. population: the analysis set as the "
         "label names it. If the table or row is not printed, state=NOT_REPORTED.",
    "B": "You are reader B, an independent second reader; another reader's answer exists but you are not shown it. "
         "Read the FDA label window below sceptically: check that the table belongs to the named trial alone (not a "
         "pooled analysis), which column is the drug and which is placebo, and that each number is a count of "
         "patients (not a percentage). Quote the header and the row verbatim; copy numbers exactly; never compute. "
         "events_t/n_t = drug arm, events_c/n_c = placebo. If not printed, state=NOT_REPORTED."}
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "label_adr")


def reader_gate(ans, shown):
    """FOUND counts only when every quoted passage is verbatim in the shown window and each count is printed in the
    quote as a whole number (not a percentage or a decimal)."""
    if ans.get("state") != "FOUND":
        return "NOT_REPORTED_BY_READER"
    parts = [_ws(x) for x in str(ans.get("quote") or "").splitlines() if _ws(x)]
    if not parts or any(len(x) < 12 or x not in shown for x in parts):
        return "QUOTE_NOT_VERBATIM"
    q = " ".join(parts)
    # the '(p)' after a count in an 'n (%)' cell is a percentage, integer or not (codex r9-4-label-r1 #4)
    q = re.sub(r"(?<=\d)\s*\(\s*\d+(?:\.\d+)?\s*%?\s*\)", " ", q)
    toks = {int(m.group(1).replace(",", "")) for m in
            re.finditer(r"(?<![\d.,])(\d{1,3}(?:,\d{3})+(?!\d)|\d+)((?:[.,]\d+)?)(\s*%)?", q)
            if not m.group(2) and not m.group(3)}
    miss = [k for k in ("events_t", "n_t", "events_c", "n_c") if ans.get(k) not in toks]
    return f"NUMBER_NOT_IN_QUOTE:{','.join(miss)}" if miss else "GATED"


def readers(res, run=False, workers=8):
    """Two recorded codex readers per proposal over the label's table window (caption -> REACH)."""
    import concurrent.futures as cf
    import hashlib
    import g1_regulatory_source as rs
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    jobs = []
    for slug, t in res["topics"].items():
        for p in t["proposals"]:
            txt = rs.doc_text(p["url"]) or ""
            i = _ws(txt).find(p["caption_span"][:60])
            win = _ws(txt)[max(0, i):i + REACH] if i >= 0 else ""
            for who, instr in READERS.items():
                prompt = (f"{instr}\n\nTRIAL: {p['trial']}\nADVERSE REACTION: {p['harm_outcome']}\n\n<<<FDA LABEL WINDOW "
                          f"({p['url']})\n{win}\nWINDOW>>>\n").encode("utf-8")
                jobs.append((p, who, win, prompt))

    def one(job):
        p, who, win, prompt = job
        rec = mcl.call(prompt, schema=READER_SCHEMA, model="gpt-6-astra", effort="high",
                       caller={"file": "scripts/g1_label_adr.py", "line": "readers", "lane": "g1/binding",
                               "purpose": f"R9-4 label ADR second reader {who} {p['trial']} {p['harm_outcome']}"},
                       input_digests=[{"ref": f"FDA label {p['url']} (US government work, public domain)",
                                       "sha256": hashlib.sha256(win.encode("utf-8")).hexdigest(),
                                       "what": "the label's adverse-reaction table window shown"}], timeout_s=1200)
        ms.write_record(rec, REC_DIR)
        ans = json.loads(ms.replay(rec).decode("utf-8")) if rec["state"] == "RAN_OK" else {}
        return p, who, rec["record_id"], rec["state"], ans, reader_gate(ans, win) if ans else "RAN_ERROR"
    if not run:
        # replay: the readers recorded for the SAME prompt are read back from their records and re-gated now
        prev = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"topics": {}}
        old = {(q["url"], q["trial"], q["harm_outcome"]): q.get("second_readers") or {}
               for t in prev.get("topics", {}).values() for q in t.get("proposals", [])}
        for p, who, win, prompt in jobs:
            r = (old.get((p["url"], p["trial"], p["harm_outcome"])) or {}).get(who) or {}
            fp = os.path.join(REC_DIR, f"{r.get('record_id')}.json")
            if not os.path.exists(fp):
                continue
            rec = ms.load_record(fp)
            if (rec.get("prompt") or {}).get("sha256") not in (None, hashlib.sha256(prompt).hexdigest()):
                continue                                    # the prompt changed: that record answers another question
            ans = json.loads(ms.replay(rec).decode("utf-8")) if rec.get("state") == "RAN_OK" else {}
            verdict = reader_gate(ans, win) if ans else "RAN_ERROR"
            p.setdefault("second_readers", {})[who] = {
                "record_id": r["record_id"], "state": rec.get("state"), "gate": verdict,
                "agrees": verdict == "GATED" and all(ans.get(k) == p["values"][k] for k in p["values"])}
        return
    os.makedirs(REC_DIR, exist_ok=True)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for p, who, rid, st, ans, verdict in ex.map(one, jobs):
            agree = verdict == "GATED" and all(ans.get(k) == p["values"][k] for k in p["values"])
            p.setdefault("second_readers", {})[who] = {"record_id": rid, "state": st, "gate": verdict,
                                                       "agrees": agree}
            print(who, rid, st, verdict, "AGREES" if agree else "DIFFERS", p["trial"], p["harm_outcome"], flush=True)


def main(argv):
    slugs = sorted(f[:-5] for f in os.listdir(os.path.join(ROOT, "topics")) if f.endswith(".json")) \
        if "--sweep" in argv else [a for a in argv if not a.startswith("--")]
    if "--hold" in argv:
        for s in slugs:
            cfg = json.load(open(os.path.join(ROOT, "topics", f"{s}.json"), encoding="utf-8"))
            if cfg.get("harm_outcomes"):
                h = hold_labels(s, cfg)
                print("HELD", s, len(h), sum(1 for r in h if r["state"] == "TEXT"), flush=True)
    res = run(slugs)
    readers(res, run="--readers" in argv)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
    print(json.dumps(res["sweep"], indent=1))
    for s, t in res["topics"].items():
        for p in t["proposals"]:
            print("PROPOSED", s, p["endpoint"], p["values"], p["row_span"])


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
