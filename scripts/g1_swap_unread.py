"""The comparator-swap screen for C1-PASS candidates that were NEVER READ (sglt2-ckd, 8 Oct: 39 candidates pass C1 on a
CC BY Unpaywall location, fail nothing, and stay C2-C6 UNCLEAR 'not read: no open JATS' -- scripts/g1_swap.cmd_screen
reads only PMC JATS, `if v["verdict"] == "PASS" and pmcid`).

The procedure is g1_swap's, unchanged: the PRE-REGISTERED rule (registry/comparator_selection/<slug>.rule.json and the
topic, both read from the ref they were committed on), STAGE A's prompt and schema, and the quote gate (gate_screen: a
verdict counts only with its quote verbatim in the text read). Recorded codex calls only.

  STAGE A (this script, now): the candidate's TITLE + ABSTRACT (Europe PMC REST; an abstract is always promptable). A
          gated FAIL on C2-C5 excludes; a candidate with no gated FAIL survives to the full read.
  FULL   (not run here): survivors need their CC BY full text in a prompt. Their CC BY evidence is Unpaywall's location
          licence + the publisher page's own licence tag, while D8's prompt guard (scripts/g1_licence.py) requires
          Europe PMC's article licence, which records none for them. Listed for the captain's ruling; never sent.

Codex level, applied before every call (dispatch 8 Oct): 8 while free RAM > 6 GB and free disk > 10 GB and no error in
the last 10 minutes; 5 while RAM 3-6 GB or disk 5-10 GB; 2 after an error; NO new call below 5 GB free disk.

    python scripts/g1_swap_unread.py SLUG [--ref=origin/main] [--run]
"""
from __future__ import annotations

import concurrent.futures as cf
import ctypes
import datetime
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_swap as sw  # noqa: E402  (main's, unchanged: rule, prompts, schemas, gates)

REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "swap_screen")
OUT = os.path.join(ROOT, "registry", "comparator_selection")
MODEL, EFFORT = "gpt-6-astra", "medium"           # k_gap_forest_plot.MODEL / EFFORT on main (the screen's own)
_LAST_ERR = [0.0]


def _git(ref, path):
    p = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True, stdin=subprocess.DEVNULL)
    if p.returncode != 0:
        raise FileNotFoundError(f"{ref}:{path}")
    return p.stdout


def protocol_at(slug, ref):
    """g1_swap.protocol(), from the topic file AT THE REF the rule was committed against (this lane's copy differs)."""
    c = json.loads(_git(ref, f"topics/{slug}.json"))
    po = c.get("primary_outcome") or {}
    return {"file": f"topics/{slug}.json@{ref}", "question": c.get("question") or c.get("title"),
            "eligibility": c.get("eligibility_summary") or None,
            "intervention_terms": c.get("intervention_terms") or [], "comparator_terms": c.get("comparator_terms") or [],
            "primary_outcome": po.get("name"), "estimand": (po.get("estimand") or "").upper(),
            "timepoint": po.get("timepoint"), "analysis_population": po.get("population"),
            "current_comparator": str(c.get("comparator_pmid"))}


def unread(selection):
    """C1 PASS, no criterion FAIL, and no PMC copy: the candidates the screen never read."""
    return [x for x in selection["per_candidate"]
            if x["verdicts"].get("C1_OPEN_LICENCE") == "PASS" and not any(v == "FAIL" for v in x["verdicts"].values())]


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
    """The dispatch's codex ceiling: 0 (no new call), 2, 5 or 8."""
    ram = free_ram_gb() if ram is None else ram
    disk = min(shutil.disk_usage("C:\\").free, shutil.disk_usage("F:\\").free) / 2 ** 30 if disk is None else disk
    now = time.time() if now is None else now
    if disk < 5:
        return 0
    if now - _LAST_ERR[0] < 600:
        return 2
    if ram > 6 and disk > 10:
        return 8
    return 5


def abstract(pmid):
    """(title + abstract text, sha256) from Europe PMC REST (cached under outputs/k_gap/_open/)."""
    import g1_open_sources as osrc
    cp = os.path.join(osrc.TEXTS, "europepmc_abstracts.json")
    c = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}
    if pmid not in c:
        st, _ct, b, _u = osrc.fetch("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:"
                                    f"{urllib.parse.quote(pmid)}%20AND%20SRC:MED&resultType=core&format=json", timeout=40)
        r = ((json.loads(b).get("resultList") or {}).get("result") or [{}])[0] if st == 200 else {}
        c[pmid] = {"title": r.get("title") or "", "abstract": r.get("abstractText") or ""}
        os.makedirs(osrc.TEXTS, exist_ok=True)
        with open(cp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(c, fh, indent=1, sort_keys=True, ensure_ascii=False)
    import re
    t = re.sub(r"<[^>]+>", " ", c[pmid]["title"] + "\n" + c[pmid]["abstract"]).strip()
    return t, hashlib.sha256(t.encode("utf-8")).hexdigest()


def stage_a_prompt(p, rule_, text):
    crit = "\n".join(f"{c['id']}: PASS if {c['pass_if']}" for c in rule_["criteria"] if c["id"] in sw.A_CRIT)
    return (sw.A_INSTR + f"\n\nPROTOCOL: {p['question']}\nPRIMARY OUTCOME: {p['primary_outcome']} (estimand "
            f"{p['estimand']})\nCRITERIA:\n{crit}\n=== TITLE AND ABSTRACT ===\n{text}\n").encode("utf-8")


def run_calls(items, ledger):
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    lock = threading.Lock()
    pending = list(items)
    os.makedirs(REC_DIR, exist_ok=True)

    def one(it):
        rec = mcl.call(it["prompt"], schema=json.loads(json.dumps(sw.A_SCHEMA)), model=MODEL, effort=EFFORT,
                       caller={"file": "scripts/g1_swap_unread.py", "line": "stage_a",
                               "purpose": f"G1 comparator swap: screen candidate {it['pmid']} for {it['slug']} "
                                          f"(stage A abstract C2-C5, rule; acq/k-gap lane)"},
                       input_digests=it["digests"], timeout_s=1500)
        ms.write_record(rec, REC_DIR)
        return it, rec
    running = {}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        while pending or running:
            lv = level()
            while pending and len(running) < lv:
                it = pending.pop(0)
                running[ex.submit(one, it)] = it
            if not running:
                print(f"CODEX LEVEL 0 (free disk < 5 GB): {len(pending)} calls not started", flush=True)
                break
            done, _ = cf.wait(list(running), timeout=30, return_when=cf.FIRST_COMPLETED)
            for f in done:
                it = running.pop(f)
                try:
                    _it, rec = f.result()
                    st = rec["state"]
                    if st != "RAN_OK":
                        _LAST_ERR[0] = time.time()
                    with lock:
                        ledger[it["key"]] = {"record_id": rec["record_id"], "state": st,
                                             "prompt_sha256": hashlib.sha256(it["prompt"]).hexdigest()}
                    print(it["key"], st, rec["record_id"], f"level {lv}", flush=True)
                except Exception as exc:  # noqa: BLE001 - a refused call is named, never dropped
                    _LAST_ERR[0] = time.time()
                    ledger[it["key"]] = {"state": f"CALL_FAILED:{type(exc).__name__}", "why": str(exc)[:300]}
                    print(it["key"], "CALL_FAILED", type(exc).__name__, str(exc)[:200], flush=True)


def main(argv):
    ref = next((a.split("=", 1)[1] for a in argv if a.startswith("--ref=")), "origin/main")
    slug = next(a for a in argv if not a.startswith("--"))
    p = protocol_at(slug, ref)
    rule_ = json.loads(_git(ref, f"registry/comparator_selection/{slug}.rule.json"))
    sel = json.loads(_git(ref, f"registry/comparator_selection/{slug}.selection.json"))
    outp = os.path.join(OUT, f"{slug}.unread_reads.json")
    prev = json.load(open(outp, encoding="utf-8")) if os.path.exists(outp) else {}
    ledger = dict(prev.get("runs") or {})
    items = []
    for x in unread(sel):
        text, sha = abstract(x["pmid"])
        pr = stage_a_prompt(p, rule_, text)
        items.append({"key": f"swapunreadA::{slug}::{x['pmid']}", "pmid": x["pmid"], "slug": slug, "prompt": pr,
                      "text": text, "digests": [{"ref": f"PubMed record PMID {x['pmid']} title + abstract (Europe PMC REST)",
                                                 "sha256": sha, "what": "the candidate meta's own title and abstract"}]})
    todo = [it for it in items if (ledger.get(it["key"]) or {}).get("prompt_sha256") !=
            hashlib.sha256(it["prompt"]).hexdigest() or (ledger.get(it["key"]) or {}).get("state") != "RAN_OK"]
    print(f"{slug}: {len(items)} never-read C1-PASS candidates; stage A calls to make: {len(todo)}; level now {level()}",
          flush=True)
    if "--run" in argv and todo:
        run_calls(todo, ledger)
    from reproducible_ai import model_source as ms
    rows = []
    for it in items:
        r = ledger.get(it["key"]) or {}
        row = {"pmid": it["pmid"], "stage_a": None, "survives_to_full_read": None, "record_id": r.get("record_id")}
        if r.get("state") == "RAN_OK" and os.path.exists(os.path.join(REC_DIR, r["record_id"] + ".json")):
            claim = json.loads(ms.replay(ms.load_record(os.path.join(REC_DIR, r["record_id"] + ".json"))).decode("utf-8"))
            crit, _pl, _k = sw.gate_screen(claim, it["text"])
            row["stage_a"] = crit
            row["survives_to_full_read"] = not any(v["verdict"] == "FAIL" for v in crit.values())
        rows.append(row)
    out = {"slug": slug, "ref": ref, "rule_commit": sel.get("rule_commit"),
           "written": datetime.date.today().isoformat(), "writer": "scripts/g1_swap_unread.py",
           "population": "C1 PASS, no FAIL, no PMC copy: never read by g1_swap.cmd_screen", "runs": ledger, "rows": rows,
           "survivors": [r["pmid"] for r in rows if r["survives_to_full_read"]],
           "full_read": "NOT RUN: survivors' CC BY evidence is Unpaywall + host page; D8's prompt guard needs Europe PMC's "
                        "licence (none recorded). For the captain's ruling."}
    os.makedirs(OUT, exist_ok=True)
    with open(outp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(f"stage A read: {sum(r['stage_a'] is not None for r in rows)} of {len(rows)}; survivors: {out['survivors']}")
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
