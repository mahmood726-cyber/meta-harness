"""RECORDED DUAL CODEX SCREEN of records the regex screen leaves undecided or newly includes (evidence-completeness sprint,
9 Oct): two independent readers (gpt-6-astra, gpt-5.5) judge ONE record against the topic's REGISTERED eligibility.
Each verdict counts only with a quote VERBATIM in the record text it was shown (whitespace / case folded). Prompts carry
only a PubMed record (title + abstract) or a CT.gov registry record (US Government work): D8-clean, no full text.

  ELIGIBLE      both readers INCLUDE, each with a verbatim quote
  EXCLUDED      both EXCLUDE, each with a verbatim quote (the rule each names is recorded)
  DISAGREE      anything else -- listed for the captain, never counted either way

Codex level before every call (dispatch 8 Oct): 8 while free RAM > 6 GB and free disk > 10 GB and no error in 10 min;
5 at RAM 3-6 GB or disk 5-10 GB; 2 after an error; no new call below 5 GB free disk.

    python scripts/g1_dual_screen.py --items=<items.json> --out=<ledger.json> [--run]
    items.json: [{"key", "slug", "record": {...}}]   (from g1_shadow_rescreen flips or g1_concept_search new records)
"""
from __future__ import annotations

import concurrent.futures as cf
import ctypes
import hashlib
import io
import json
import os
import re
import shutil
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "dual_screen")
READERS = (("A", "gpt-6-astra", "medium"), ("B", "gpt-5.5", "medium"))
# NON-DECIDING third reader (Captain ruling 4, 10 Oct): agy routed to Gemini, recorded the same way, run only with --third.
# It never changes `verdict` (the pre-registered 2-reader rule); it feeds `sensitivity_2of3` only.
THIRD = ("C", "agy", None)
_LAST_ERR = [0.0]
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["decision", "rule", "quote", "why"],
          "properties": {"decision": {"type": "string", "enum": ["INCLUDE", "EXCLUDE", "UNCLEAR"]},
                         "rule": {"type": "string", "enum": ["MEETS_ALL", "NOT_RCT", "POPULATION", "INTERVENTION",
                                                             "COMPARATOR", "DESIGN", "DUPLICATE_OR_SECONDARY_REPORT",
                                                             "NOT_DECIDABLE_FROM_RECORD", "LITERAL_ONLY"]},
                         "quote": {"type": "string"}, "why": {"type": "string"}}}
INSTR = """You screen ONE record (a PubMed abstract or a ClinicalTrials.gov registration) against a systematic review's
REGISTERED eligibility, below. Use only the record; no memory of the trial.
Apply the protocol text EXACTLY as written, including any criterion on how the outcome was specified or ascertained.
INCLUDE only if the record shows EVERY criterion of that text is met (reading the arms this way: a placebo arm counts as
placebo; 'placebo for X' / 'matching placebo' is a placebo arm, not an X arm; a development code of the drug is the drug).
EXCLUDE if the record shows one criterion is NOT met (name it in 'rule'). A secondary/sub-study/design paper of a trial is
DUPLICATE_OR_SECONDARY_REPORT. UNCLEAR if the record cannot decide.
'quote' must be copied CHARACTER FOR CHARACTER from the record: the passage that decides (for INCLUDE, the passage naming
the randomised comparison)."""


def free_ram_gb():
    class M(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = M()
    m.dwLength = ctypes.sizeof(M)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 2 ** 30


def level(ram=None, disk=None, now=None):
    ram = free_ram_gb() if ram is None else ram
    disk = min(shutil.disk_usage("C:\\").free, shutil.disk_usage("F:\\").free) / 2 ** 30 if disk is None else disk
    now = time.time() if now is None else now
    if disk < 5:
        return 0
    if now - _LAST_ERR[0] < 600:
        return 2
    return 8 if (ram > 6 and disk > 10) else 5


def record_text(rec):
    parts = [f"TITLE: {rec.get('title') or ''}"]
    if rec.get("acronym"):
        parts.append(f"ACRONYM: {rec['acronym']}")
    for k in ("conditions", "interventions", "arms"):
        if rec.get(k):
            parts.append(f"{k.upper()}: " + "; ".join(str(x.get('name') if isinstance(x, dict) else x) for x in rec[k]))
    for k in ("masking", "allocation"):
        if rec.get(k):
            parts.append(f"{k.upper()}: {rec[k]}")
    if rec.get("pubtypes"):
        parts.append("PUBLICATION TYPES: " + "; ".join(rec["pubtypes"]))
    parts.append(f"ABSTRACT / SUMMARY: {rec.get('abstract') or ''}")
    return "\n".join(parts)


def protocol_eligibility_text(slug):
    """The REGISTERED protocol's own eligibility text, VERBATIM (protocols/<slug>.md): the PICO block, the Eligibility
    section, and every dated amendment's eligibility clause (a later amendment governs: GLP-1 'B-prime' 16 Sep). Never a
    summary of the config -- the reader applies the protocol as written."""
    md = open(os.path.join(ROOT, "protocols", slug + ".md"), encoding="utf-8").read()
    secs = re.split(r"(?m)^(?=## )", md)
    keep = [s for s in secs if re.match(r"## (?:PICO|Eligibility)", s)]
    for s in secs:
        if s.startswith("## Amendment"):
            head = s.splitlines()[0]
            elig = [l for l in s.splitlines() if re.search(r"(?i)\beligib|\bquestion\b|\bestimand\b", l)]
            if elig:
                keep.append(head + "\n" + "\n".join(elig))
    return "\n\n".join(x.strip() for x in keep)


# OPERATING READINGS the Captain has ruled for a protocol whose text is ambiguous (quoted into the prompt beside the
# verbatim protocol; the protocol itself is Mahmood's and is not edited here).
OPERATING = {
    "glp1-ra-mace-t2d": (
        "OPERATING READING (Captain ruling 1, 10 Oct; GLP-1 operating reading per signed V14-07): the B-prime criterion is read "
        "as reading (ii): 3-point MACE (or its exact three components) must be prespecified as a PRIMARY or KEY-SECONDARY "
        "EFFICACY endpoint of the trial. Line 79 of the same signed amendment states this intent (glycaemic trials such as "
        "SUSTAIN-1, PIONEER-1, AWARD-8 are outside). A trial whose MACE was only adjudicated as a SAFETY endpoint (e.g. under "
        "regulatory cardiovascular-safety adjudication) meets the literal line-78 wording only: answer EXCLUDE with rule "
        "LITERAL_ONLY when the record shows that, and every other criterion is met. If the record does not show how MACE was "
        "specified, answer UNCLEAR with rule NOT_DECIDABLE_FROM_RECORD."),
}


def protocol(slug):
    from harness import served_comparator as sc
    c = sc.served_config(slug, json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8")))
    op = OPERATING.get(slug)
    return (f"QUESTION: {c.get('question') or c.get('title')}\n\nTHE REGISTERED PROTOCOL'S ELIGIBILITY, VERBATIM "
            f"(a dated amendment governs the text before it):\n{protocol_eligibility_text(slug)}"
            + (f"\n\n{op}" if op else ""))


def prompt_for(it, third=False):
    """The exact prompt bytes for one item (shared by the call and by the record recovery). The agy reader (third=True)
    gets the output schema IN the prompt: codex receives it as --output-schema, agy only sees what the prompt states
    (10 Oct pilot: without it agy answered 'DECISION: INCLUDE / QUOTE: ...' free text)."""
    p = (INSTR + "\n\n=== REGISTERED ELIGIBILITY ===\n" + protocol(it["slug"]) + "\n\n=== RECORD ===\n"
         + record_text(it["record"]))
    if third:
        p += ("\n\n=== ANSWER FORMAT ===\nAnswer with ONLY one JSON object (no prose, no code fence) matching this JSON "
              "schema exactly:\n" + json.dumps(SCHEMA, sort_keys=True))
    return p.encode("utf-8")


def parse_answer(b):
    """The reader's JSON object, or None. Tolerates a ``` fence (agy wraps JSON in fences); anything else is
    UNPARSEABLE -- never guessed from prose."""
    t = b.decode("utf-8", "replace").strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", t, re.S)
    t = m.group(1) if m else t
    try:
        o = json.loads(t)
    except ValueError:
        return None
    return o if isinstance(o, dict) else None


def _norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def gated(resp, text):
    q = _norm(resp.get("quote"))
    ok = bool(q) and len(q) >= 12 and q in _norm(text)
    return resp.get("decision") if ok else "UNGATED"


def verdict(a, b):
    if a == b == "INCLUDE":
        return "ELIGIBLE"
    if a == b == "EXCLUDE":
        return "EXCLUDED"
    return "DISAGREE"


def main(argv):
    items_p = next(a.split("=", 1)[1] for a in argv if a.startswith("--items="))
    out_p = next(a.split("=", 1)[1] for a in argv if a.startswith("--out="))
    items = json.load(open(items_p, encoding="utf-8"))
    led = json.load(open(out_p, encoding="utf-8")) if os.path.exists(out_p) else {"runs": {}, "rows": {}}
    # RECOVER from the records by prompt sha256: a run stopped between ledger saves never pays for a call twice
    import base64
    want = {}
    for it in items:
        want[hashlib.sha256(prompt_for(it)).hexdigest()] = it["key"]
        want[hashlib.sha256(prompt_for(it, third=True)).hexdigest()] = it["key"]
    if os.path.isdir(REC_DIR):
        for f in os.listdir(REC_DIR):
            try:
                rec = json.load(open(os.path.join(REC_DIR, f), encoding="utf-8"))
            except (OSError, ValueError):
                continue
            sha = hashlib.sha256(base64.b64decode((rec.get("prompt") or {}).get("b64") or "")).hexdigest()
            key = want.get(sha)
            if key and rec.get("state") == "RAN_OK":
                mdl = rec.get("model") or {}
                mid = mdl.get("id_requested") if isinstance(mdl, dict) else mdl
                tag = next((t for t, m, _e in READERS if m == mid), None) or (
                    "C" if str(mid or "").startswith("Gemini") else None)
                if tag and (led["runs"].get(f"{key}::{tag}") or {}).get("state") != "RAN_OK":
                    led["runs"][f"{key}::{tag}"] = {"record_id": rec["record_id"], "state": "RAN_OK", "prompt_sha256": sha,
                                                    "recovered_from_record": True}
    readers = READERS + ((THIRD,) if "--third" in argv else ())
    calls = []
    for it in items:
        text = record_text(it["record"])
        for tag, model, eff in readers:
            prompt = prompt_for(it, third=(tag == "C"))
            psha = hashlib.sha256(prompt).hexdigest()
            k = f"{it['key']}::{tag}"
            r = led["runs"].get(k) or {}
            if not (r.get("state") == "RAN_OK" and r.get("prompt_sha256") == psha):
                calls.append((k, it, tag, model, eff, prompt, psha, text))
    print(f"{len(items)} records; calls to make {len(calls)}; level {level()}", flush=True)
    if "--run" in argv and calls:
        from reproducible_ai import model_call_live as mcl
        from reproducible_ai import model_source as ms
        os.makedirs(REC_DIR, exist_ok=True)
        lock = threading.Lock()

        def one(c):
            k, it, tag, model, eff, prompt, psha, _t = c
            fn = mcl.agy_call if model == "agy" else (
                lambda p, **kw: mcl.call(p, model=model, effort=eff, **kw))
            rec = fn(prompt, schema=json.loads(json.dumps(SCHEMA)),
                           caller={"file": "scripts/g1_dual_screen.py", "line": f"reader {tag}",
                                   "purpose": f"evidence completeness: dual screen {it['slug']} / {it['record'].get('id')} "
                                              f"(reader {tag}; acq/k-gap lane)"},
                           input_digests=[{"ref": f"record {it['record'].get('id')} (PubMed abstract or CT.gov registry)",
                                           "sha256": hashlib.sha256(_t.encode('utf-8')).hexdigest(),
                                           "what": "one bibliographic / registry record + the registered eligibility"}],
                           timeout_s=1200)
            ms.write_record(rec, REC_DIR)
            return k, rec, psha
        pending, running = list(calls), {}
        with cf.ThreadPoolExecutor(max_workers=int(next((a.split("=", 1)[1] for a in argv if a.startswith("--workers=")), "2"))) as ex:
            while pending or running:
                lv = level()
                while pending and len(running) < lv:
                    c = pending.pop(0)
                    running[ex.submit(one, c)] = c
                if not running:
                    print(f"LEVEL 0: {len(pending)} calls not started (disk floor)", flush=True)
                    break
                done, _ = cf.wait(list(running), timeout=30, return_when=cf.FIRST_COMPLETED)
                for f in done:
                    c = running.pop(f)
                    try:
                        k, rec, psha = f.result()
                        if rec["state"] != "RAN_OK":
                            _LAST_ERR[0] = time.time()
                        with lock:
                            led["runs"][k] = {"record_id": rec["record_id"], "state": rec["state"], "prompt_sha256": psha}
                        print(k, rec["state"], rec["record_id"], f"level {lv}", flush=True)
                    except Exception as exc:  # noqa: BLE001 - named, never dropped
                        _LAST_ERR[0] = time.time()
                        led["runs"][c[0]] = {"state": f"CALL_FAILED:{type(exc).__name__}", "why": str(exc)[:300]}
                        print(c[0], "CALL_FAILED", str(exc)[:200], flush=True)
                    if len(led["runs"]) % 20 == 0:
                        json.dump(led, open(out_p, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    from reproducible_ai import model_source as ms
    for it in items:
        text = record_text(it["record"])
        res = {}
        for tag, _m, _e in READERS + (THIRD,):
            r = led["runs"].get(f"{it['key']}::{tag}") or {}
            if r.get("state") == "RAN_OK" and os.path.exists(os.path.join(REC_DIR, r["record_id"] + ".json")):
                resp = parse_answer(ms.replay(ms.load_record(os.path.join(REC_DIR, r["record_id"] + ".json"))))
                if resp is None:
                    res[tag] = {"decision": None, "gated": "UNPARSEABLE", "rule": None, "quote": None,
                                "record_id": r["record_id"]}
                    continue
                res[tag] = {"decision": resp.get("decision"), "gated": gated(resp, text), "rule": resp.get("rule"),
                            "quote": resp.get("quote"), "record_id": r["record_id"]}
        row = {"slug": it["slug"], "id": it["record"].get("id"), "title": (it["record"].get("title") or "")[:200],
               "readers": res, "origin": it.get("origin")}
        if "A" in res and "B" in res:
            row["verdict"] = verdict(res["A"]["gated"], res["B"]["gated"])
        if len(res) == 3:                       # NON-DECIDING 2-of-3 sensitivity; never replaces `verdict`
            g = [res[t]["gated"] for t in ("A", "B", "C")]
            row["sensitivity_2of3"] = ("ELIGIBLE" if g.count("INCLUDE") >= 2 else
                                       "EXCLUDED" if g.count("EXCLUDE") >= 2 else "SPLIT")
        led["rows"][it["key"]] = row
    json.dump(led, open(out_p, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    from collections import Counter
    print(Counter(r.get("verdict", "NOT_READ") for r in led["rows"].values()))
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
