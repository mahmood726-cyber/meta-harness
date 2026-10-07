"""Convert HAND_ENTERED served values into RECORDED reads (Mahmood 6 Oct decision, under delegation: keep the shrink-only
burn-down; convert the remaining hand-entered rows by extractor or recorded call).

For every HAND_ENTERED served row in outputs/provenance_census.json: ONE recorded codex call (reproducible_ai.
model_call_live; licence-guarded, leak-scanned, replayable) is shown the trial's held text -- title + abstract, plus a full
text only from a copy marked open -- and asked to LOCATE the outcome's result (scripts/secondary_meta_build LOCATE
instruction and schema). The deterministic gate harness.secondary_meta.gate_locator_claim accepts a number only when it is
printed in a quote that is verbatim in the shown text. When the gated numbers EQUAL the hand-entered value, the value is
backed by a recorded, replayable read: registry/provenance_recorded_reads.json records {record_id, quote, numbers}, and
scripts/provenance_census.py then classes the row RECORDED_MODEL_CALL. Anything else (NOT_REPORTED, a gate refusal, a
different number) is listed for adjudication by quoted span -- never silently accepted, never auto-replaced.

    python scripts/provenance_convert.py [--run] [--only SLUG]     (concurrency G1_CODEX_CONCURRENCY, default 5)
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import os
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
CENSUS = os.path.join(ROOT, "outputs", "provenance_census.json")
READS = os.path.join(ROOT, "registry", "provenance_recorded_reads.json")
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "provenance_convert")
NUM = ("ai", "n1i", "ci", "n2i", "effect", "ci_low", "ci_high")
_LOCK = threading.Lock()


def _j(p, default=None):
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def key(slug, pid, outcome):
    return f"{slug}|{str(pid).replace('PMID ', '').strip()}|{outcome}"


def served_row(slug, outcome, pid):
    r = _j(os.path.join(ROOT, "docs", "reviews", slug, "review.json"))
    for o in r.get("outcomes") or []:
        if o.get("name") == outcome:
            for t in o.get("trials") or []:
                if str(t.get("id")) == str(pid):
                    return o, t
    return None, None


def shown_text(slug, pmid):
    """The text a recorded prompt may carry: title + abstract, plus a held full text only when its copy is marked open."""
    import secondary_meta_build as smb
    from harness import copy_licence as cl
    rec = smb._trial_text(slug, pmid, False) or {}
    ft_path = os.path.join(ROOT, "cache", slug, f"ft_{pmid}.txt")
    ft = open(ft_path, encoding="utf-8", errors="replace").read()[:150000] if os.path.exists(ft_path) else ""
    # the same text + declared-source ref the shared locator uses: full text only from a CC copy (the pre-call licence
    # guard refuses a whole-text block with no declared source -- it refused omega3 21115589 on the first run)
    lic = cl.pmc_licence(pmid, run=False) if ft else None
    return cl.locator_text(rec, ft, lic, pmid)


def wanted(t):
    if t.get("ai") is not None:
        return "counts"
    return f"{(t.get('scale') or 'effect').upper()}"


def prompt(outcome, t, text, slug=None):
    import secondary_meta_build as smb
    w = wanted(t)
    cfg = _j(os.path.join(ROOT, "topics", f"{slug}.json"), {}) if slug else {}
    iv = ", ".join((cfg.get("intervention_terms") or [])[:8])
    cp = ", ".join((cfg.get("comparator_terms") or [])[:6])
    # a factorial or multi-arm report prints several comparisons: name the one the review pools (omega3 21115589, a
    # 2x2 factorial, was read on its B-vitamin comparison when only the outcome was named)
    comp = (f"\nCOMPARISON: {iv} (intervention) versus {cp} (control). In a factorial or multi-arm report, quote THIS "
            f"comparison only.\n" if iv and cp else "")
    ask = ("\nWANTED: the number of participants WITH the outcome and the number randomised (or analysed), in EACH arm "
           "(events_t, n_t, events_c, n_c), copied as printed. If the arm sizes are printed in a different sentence from the "
           "events, make your quote the shortest CONTIGUOUS passage that contains all four numbers.\n" if w == "counts" else
           f"\nWANTED: the {w} with its 95% confidence interval, copied as printed.\n")
    return (smb.LOCATE_INSTR + ask + comp + f"\nOUTCOME: {outcome}\n<<<TEXT\n{text}\nTEXT>>>\n").encode("utf-8")


def agrees(val, t):
    """The gated read equals the served (hand-entered) value: arm counts exactly, or effect + CI at printed precision."""
    def f(x):
        try:
            return float(str(x).replace("−", "-"))
        except (TypeError, ValueError):
            return None
    if t.get("ai") is not None:
        got = [val.get(k) for k in ("events_t", "n_t", "events_c", "n_c")]
        want = [t.get(k) for k in ("ai", "n1i", "ci", "n2i")]
        return all(g is not None for g in got) and [f(g) for g in got] == [f(w) for w in want]
    got = [f(val.get(k)) for k in ("effect", "lower", "upper")]          # the gate's own keys (gate_locator_claim)
    want = [f(t.get(k)) for k in ("effect", "ci_low", "ci_high")]
    return None not in got and None not in want and all(abs(g - w) < 1e-9 for g, w in zip(got, want))


def one(row, run):
    from harness import secondary_meta as sm
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    import k_gap_forest_plot as fp
    slug, outcome, pid = row["slug"], row["outcome"], row["id"]
    pmid = str(pid).replace("PMID ", "").strip()
    o, t = served_row(slug, outcome, pid)
    if not t:
        return {"key": key(slug, pid, outcome), "state": "NO_SERVED_ROW"}
    text, scope = shown_text(slug, pmid)
    p = prompt(outcome, t, text, slug)
    psha = hashlib.sha256(p).hexdigest()
    reads = _j(READS, {"reads": {}})["reads"]
    prev = reads.get(key(slug, pid, outcome)) or {}
    rec_path = os.path.join(REC_DIR, f"{prev.get('record_id')}.json")
    if prev.get("prompt_sha256") == psha and os.path.exists(rec_path):
        rec = ms.load_record(rec_path)
    elif run:
        rec = mcl.call(p, schema=json.loads(json.dumps(__import__("secondary_meta_build").LOCATE_SCHEMA)),
                       model=fp.MODEL, effort=fp.EFFORT,
                       caller={"file": "scripts/provenance_convert.py", "line": "locate",
                               "purpose": f"provenance conversion: locate the served value of {slug} / {outcome} / {pid}"},
                       input_digests=[{"ref": scope,
                                       "sha256": hashlib.sha256(text.encode('utf-8')).hexdigest(),
                                       "what": "title + abstract (+ open full text) shown whole"}],
                       timeout_s=1200)
        ms.write_record(rec, REC_DIR)
    else:
        return {"key": key(slug, pid, outcome), "state": "NOT_RUN"}
    if rec.get("state") != "RAN_OK":
        return {"key": key(slug, pid, outcome), "state": "CALL_" + str(rec.get("state")), "record_id": rec.get("record_id")}
    claim = json.loads(ms.replay(rec).decode("utf-8"))
    val, why = sm.gate_locator_claim(claim, text, prefer="counts" if wanted(t) == "counts" else None)
    out = {"key": key(slug, pid, outcome), "record_id": rec["record_id"], "prompt_sha256": psha, "shown": scope,
           "gate": why, "quote": (claim.get("quote") or "")[:600],
           "read": {k: claim.get(k) for k in ("measure", "point", "lower", "upper", "events_t", "n_t", "events_c", "n_c")},
           "served": {k: t.get(k) for k in NUM}}
    out["state"] = "AGREES" if val and agrees(val, t) else ("DISAGREES" if val else "GATE_REFUSED")
    return out


def main(argv):
    run = "--run" in argv
    only = argv[argv.index("--only") + 1] if "--only" in argv else None
    c = _j(CENSUS)
    rows = [r for r in c["served"]["rows"] if r["class"] == "HAND_ENTERED" and (not only or r["slug"] == only)]
    conc = int(os.environ.get("G1_CODEX_CONCURRENCY", "5"))
    results = []
    with cf.ThreadPoolExecutor(max_workers=conc) as ex:
        futs = {ex.submit(one, r, run): r for r in rows}
        for f in cf.as_completed(futs):
            try:
                res = f.result()
            except Exception as e:  # noqa: BLE001
                res = {"key": key(futs[f]["slug"], futs[f]["id"], futs[f]["outcome"]), "state": "ERROR", "error": str(e)[:300]}
            results.append(res)
            print(res["key"], res["state"], res.get("gate", ""), flush=True)
    with _LOCK:
        d = _j(READS, {"_doc": __doc__.split("\n\n")[0], "reads": {}})
        for r in results:
            if r.get("record_id"):
                d["reads"][r["key"]] = r
        with open(READS, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(d, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    tally = {}
    for r in results:
        tally[r["state"]] = tally.get(r["state"], 0) + 1
    print("TALLY", tally)


if __name__ == "__main__":
    main(sys.argv[1:])
