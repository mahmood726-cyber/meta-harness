"""FINAL-5 recorded readers (binding lane, 8 Oct 2026; Mahmood: "use codex hard"). TWO independent recorded readers per
staged item -- reader A extracts, reader B is a second reader with its own framing that never sees A's answer -- run at
the ceiling (8 concurrent) with bounded back-off on a rate limit, and stopped for the run on a quota/credit error.

Every call goes through reproducible_ai.model_call_live.call, so the licence guard runs at call time: a prompt may carry
only CC / public-domain text (D8). Non-CC holdings (RECOVERY NEJM, CoDEX JAMA) are therefore NEVER read here; their items
are typed by regex only and second-read by an independent deterministic reader (scripts/g1_final5_typed.py).

A reader's answer is evidence only after the gate: the quote is verbatim in the held text shown (whitespace-normalised,
tags stripped, the SAME bytes that were shown), and every number it reports is a token of its quote. Image items (a
figure) record the image sha256 in the call's input digests; their answers are never admitted, only compared.

    python scripts/g1_final5_readers.py [--run] [--workers 8]   -> outputs/k_gap/g1_binding/final5_readers.json
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import html
import io
import json
import os
import re
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from reproducible_ai import model_call_live as mcl  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "final5_readers.json")
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "final5")
MODEL, EFFORT = "gpt-6-astra", "high"
_QUOTA = re.compile(r"usage limit|quota|insufficient[_ ]credits|out of credits|You've hit your", re.I)
_RATE = re.compile(r"rate limit|429|too many requests|overloaded|503", re.I)

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["state", "quote", "events_t", "n_t", "events_c", "n_c", "count_units", "population", "notes"],
    "properties": {
        "state": {"type": "string", "enum": ["FOUND", "NOT_REPORTED"]},
        "quote": {"type": "string"},
        "events_t": {"type": ["integer", "null"]}, "n_t": {"type": ["integer", "null"]},
        "events_c": {"type": ["integer", "null"]}, "n_c": {"type": ["integer", "null"]},
        "count_units": {"type": "string", "enum": ["PARTICIPANTS", "EVENTS", "UNCLEAR", "NONE"]},
        "population": {"type": "string"},
        "notes": {"type": "string"},
    },
}

READER_A = """You are reader A. You are given the held open-access (CC BY) text of ONE randomised trial report and ONE
question. Answer only from the text. Quote, character for character, the shortest passage or table row that answers it
(for a table row, include the row label and the arm header it falls under). Copy the per-arm numbers exactly as printed
in your quote: events_t / n_t for the intervention arm, events_c / n_c for the control arm. count_units says whether the
event numbers count PARTICIPANTS (patients with at least one event) or EVENTS (total events, a patient can count more
than once). population names the analysis set the denominators belong to, as the text names it. Never compute, convert or
round. Use null for anything not printed in your quote. If the text does not print it, state=NOT_REPORTED."""

READER_B = """You are reader B, an independent second reader. Another reader's answer exists but you are NOT shown it. Read
the trial report below from the start and answer the question yourself, sceptically: check the column headers (a table can
print both a count of events and a count of patients with an event), the analysis set (full analysis set, safety set,
per protocol), and the arm order. Quote verbatim the passage or row your numbers come from, copy numbers exactly as
printed, and never compute. events_t / n_t = intervention arm, events_c / n_c = control arm. count_units: PARTICIPANTS if
the numbers count patients with at least one event, EVENTS if they count total events. Use null when not printed; if the
text does not print it, state=NOT_REPORTED."""


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def plain(s):
    """The rendered text a reader is shown and the gate searches: tags stripped, entities decoded, whitespace collapsed."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def held_text(slug, pmid):
    p = os.path.join(ROOT, "cache", slug, f"ft_{pmid}.txt")
    if not os.path.exists(p):
        p = os.path.join(ROOT, "outputs", "k_gap", "_ft", f"{pmid}.txt")
    return plain(open(p, encoding="utf-8").read())


def items():
    """(key, prompt, shown_text, images, digests, meta) per reader call. shown_text is EXACTLY what the gate searches."""
    out = []
    cfm = held_text("iv-iron-hfref-hosp", "25176939")
    eff = held_text("iv-iron-hfref-hosp", "28701470")
    q_cfm = ("QUESTION (CONFIRM-HF, ferric carboxymaltose v placebo): hospitalisation due to worsening heart failure over "
             "the study. How many PATIENTS in each arm had at least one such hospitalisation, out of how many patients "
             "in that arm's analysis set? Report the total number of such EVENTS per arm in notes.")
    q_eff = ("QUESTION (EFFECT-HF, ferric carboxymaltose v standard of care): hospitalisation for worsening heart "
             "failure during the study. How many PATIENTS in each arm had at least one such hospitalisation, and out of "
             "how many patients in each arm of the full analysis set (FAS)? Quote the FAS size too, in notes.")
    for slug, pmid, label, text, q in (("iv-iron-hfref-hosp", "25176939", "CONFIRM-HF", cfm, q_cfm),
                                       ("iv-iron-hfref-hosp", "28701470", "EFFECT-HF", eff, q_eff)):
        for who, instr in (("A", READER_A), ("B", READER_B)):
            p = f"{instr}\n\n{q}\n\n<<<TEXT PMID {pmid} (CC BY, PMC OA)\n{text}\nTEXT>>>\n"
            out.append({"key": f"final5::{label}::{who}", "slug": slug, "pmid": pmid, "label": label, "reader": who,
                        "prompt": p.encode("utf-8"), "shown": text, "images": (),
                        "digests": [{"ref": f"PMID {pmid} PMC OA full text (CC BY)",
                                     "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                                     "what": "held CC BY full text, tags stripped (the gate searches these bytes)"}]})
    # CANVAS: the comparator's cited report (Radholm 2018, CC BY) -- text AND its figures -- for printed HHF counts
    rad = held_text("sglt2-primary-prevention-hf", "29526832")
    figdir = os.path.join(ROOT, "cache", "comparators", "_final5_radholm")
    figs = [os.path.join(figdir, f) for f in ("cir-138-458-g002.jpg", "cir-138-458-g003.jpg")]
    q_can = ("QUESTION (CANVAS Program, canagliflozin v placebo): hospitalised heart failure (hospitalization for heart "
             "failure) as its own outcome. Does this report -- its text OR the two attached figures (Figure 1, Figure 2) "
             "-- print the NUMBER of participants (or events) with hospitalised heart failure in each arm? If yes, quote "
             "it and copy the numbers. If it prints only rates per 1000 patient-years, hazard ratios or numbers at risk, "
             "state=NOT_REPORTED and list in notes exactly what it does print for hospitalised heart failure (with the "
             "figure panel). Numbers at risk are NOT event counts.")
    for who, instr in (("A", READER_A), ("B", READER_B)):
        p = f"{instr}\n\n{q_can}\n\n<<<TEXT PMID 29526832 (CC BY, PMC OA)\n{rad}\nTEXT>>>\n"
        out.append({"key": f"final5::CANVAS-Radholm::{who}", "slug": "sglt2-primary-prevention-hf", "pmid": "29526832",
                    "label": "CANVAS (Radholm 2018)", "reader": who, "prompt": p.encode("utf-8"), "shown": rad,
                    "images": tuple(figs),
                    "digests": [{"ref": "PMID 29526832 PMC OA full text (CC BY)",
                                 "sha256": hashlib.sha256(rad.encode("utf-8")).hexdigest(),
                                 "what": "held CC BY full text, tags stripped"}]})
    # ENGAGE (D16 C): AACT posted analyses -- public-domain registry rows, no licence question
    ap = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", "engage_aact_rows.json")
    if os.path.exists(ap):
        rows = open(ap, encoding="utf-8").read()
        q_eng = ("QUESTION (ENGAGE AF-TIMI 48, NCT00781391): below are the trial's posted ClinicalTrials.gov results rows "
                 "(AACT snapshot 2026-08-30). Is there a posted analysis of the PRIMARY outcome, stroke or systemic "
                 "embolism, comparing HIGH-DOSE edoxaban (60 mg, dose-reduced to 30 mg) with warfarin, whose confidence "
                 "interval is a 95% interval? Quote the analysis row (param type, value, ci_percent, limits, the groups "
                 "it compares, the population/time frame) exactly. Put the HR in notes as 'HR=<v> CI<pct>=<lo>-<hi> "
                 "groups=<...> population=<...>'. If the only posted interval is 97.5% or the analysis is a different "
                 "arm/population, state=NOT_REPORTED and say what is posted. events/n fields: null.")
        for who, instr in (("A", READER_A), ("B", READER_B)):
            p = f"{instr}\n\n{q_eng}\n\n<<<AACT ROWS (public domain)\n{rows}\nAACT>>>\n"
            out.append({"key": f"final5::ENGAGE-AACT::{who}", "slug": "noac-af-stroke", "pmid": "24251359",
                        "label": "ENGAGE AF-TIMI 48", "reader": who, "prompt": p.encode("utf-8"), "shown": rows,
                        "images": (),
                        "digests": [{"ref": "AACT 2026-08-30 rows NCT00781391 (registry, public domain)",
                                     "sha256": hashlib.sha256(rows.encode("utf-8")).hexdigest(),
                                     "what": "outcomes / outcome_analyses / groups rows for the trial"}]})
    for it in out:
        it["prompt_sha256"] = hashlib.sha256(it["prompt"]).hexdigest()
    return out


_NUM = re.compile(r"(?<![\d.,])(\d{1,3}(?:,\d{3})+(?![\d])|\d+)((?:[.,]\d+)?)(\s*%)?")


def count_tokens(q):
    """The whole numbers a quote prints AS numbers that can be counts: '1,274' is 1274; a decimal ('7.6', decimal comma
    '0,5') or a percentage ('10%', '0,5 %') is never a count (codex final5-binding-r1a g1#2, r2 g1#1)."""
    return {int(m.group(1).replace(",", "")) for m in _NUM.finditer(q or "") if not m.group(2) and not m.group(3)}


def gate(ans, shown):
    """FOUND counts only if the quote is verbatim in the SAME bytes shown and every reported count is a token of it."""
    if ans.get("state") != "FOUND":
        return "NOT_REPORTED_BY_READER"
    # a reader may join several passages (a table header and its row) with newlines: EACH passage must be verbatim in
    # the shown bytes, and long enough to be a passage (a bare '150' occurs anywhere and would smuggle a number in)
    parts = [plain(p) for p in str(ans.get("quote") or "").splitlines() if plain(p)]
    if not parts or any(len(p) < 20 or p not in shown for p in parts):
        return "QUOTE_NOT_VERBATIM"
    q = " ".join(parts)
    toks = count_tokens(q)
    miss = [k for k in ("events_t", "n_t", "events_c", "n_c") if ans.get(k) is not None and ans[k] not in toks]
    return f"NUMBER_NOT_IN_QUOTE:{','.join(miss)}" if miss else "GATED"


def run(todo, workers):
    stop = threading.Event()

    def one(it):
        if stop.is_set():
            return it["key"], {"state": "SKIPPED_BUDGET", "prompt_sha256": it["prompt_sha256"]}
        for attempt in range(4):
            try:
                rec = mcl.call(it["prompt"], schema=SCHEMA, model=MODEL, effort=EFFORT, images=it["images"],
                               caller={"file": "scripts/g1_final5_readers.py", "line": "run", "lane": "g1/binding",
                                       "purpose": f"final5 reader {it['reader']} {it['label']} (binding lane)"},
                               input_digests=it["digests"], timeout_s=1800)
            except mcl.LicenceRefused as exc:
                return it["key"], {"state": "REFUSED_LICENCE", "why": str(exc)[:300], "prompt_sha256": it["prompt_sha256"]}
            err = json.dumps(rec.get("error") or "")
            if rec["state"] == "RAN_OK":
                break
            if _QUOTA.search(err):
                stop.set()
                break
            if _RATE.search(err) and attempt < 3:
                time.sleep(30 * 2 ** attempt)          # bounded back-off: 30, 60, 120 s
                continue
            break
        ms.write_record(rec, REC_DIR)
        return it["key"], {"state": rec["state"], "record_id": rec["record_id"], "prompt_sha256": it["prompt_sha256"]}

    res = {}
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for k, r in ex.map(one, todo):
            res[k] = r
            print(r["state"], r.get("record_id"), k, flush=True)
    return res


def main(argv):
    workers = int(argv[argv.index("--workers") + 1]) if "--workers" in argv else 8
    led = _j(OUT) if os.path.exists(OUT) else {"runs": {}}
    its = items()
    todo = [it for it in its if (led["runs"].get(it["key"]) or {}).get("prompt_sha256") != it["prompt_sha256"]
            or (led["runs"].get(it["key"]) or {}).get("state") != "RAN_OK"]
    if "--run" in argv and todo:
        led["runs"].update(run(todo, workers))
    rows = []
    for it in its:
        r = led["runs"].get(it["key"]) or {}
        ans, verdict = None, "NOT_RUN"
        if r.get("state") == "RAN_OK" and r.get("prompt_sha256") == it["prompt_sha256"]:
            ans = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, r["record_id"] + ".json"))).decode("utf-8"))
            verdict = gate(ans, it["shown"])
        rows.append({"key": it["key"], "label": it["label"], "pmid": it["pmid"], "reader": it["reader"],
                     "record_id": r.get("record_id"), "verdict": verdict, "answer": ans})
    led["rows"] = rows
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(led, fh, indent=1, ensure_ascii=False)
    for x in rows:
        a = x["answer"] or {}
        print(x["verdict"], x["key"], {k: a.get(k) for k in ("state", "events_t", "n_t", "events_c", "n_c", "count_units")})


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
