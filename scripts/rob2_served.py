"""RoB 2 for the SERVED trial-topic pairs (D11 serving; Mahmood 13 Oct: "continue to the served trial-topic pairs").

Each served review's PRIMARY outcome trials (scripts/rob2_dual.served_primary) that have no v3.1 object yet are read by
the frozen pipelines themselves, UNCHANGED:
  1. the v3.1 dual reading (scripts/rob2_dual: typed answers, codex + agy blind readers, adjudicator, D8 licence gate);
  2. the contextual pass under the A3 base (scripts/rob2_contextual; never a variant).
Only their STORES are redirected, at run time and restored afterwards, so this lane never writes a frozen calibration
object, a frozen record store or manifest, or a served page:
  records   evidence/model_calls/rob2_served/ (dual) and evidence/model_calls/rob2_served_ctx/ (contextual)
  manifests registry/model_proposals/rob2_served_runs.json and rob2_served_ctx_runs.json
  objects   outputs/robgrade/served/rob2/<slug>.json, then outputs/robgrade/served/rob2_ctx/<slug>.json

    python scripts/rob2_served.py [--run] [--dual-only] [SLUG ...]   (no --run: replay, no model call)
"""
import concurrent.futures as cf
import contextlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import rob2_contextual as rc  # noqa: E402
import rob2_dual as rd  # noqa: E402
from robgrade import contextual as cx  # noqa: E402
from robgrade import rob2_typed as rt  # noqa: E402

SERVED = os.path.join(ROOT, "outputs", "robgrade", "served")
REVIEWS = os.path.join(ROOT, "docs", "reviews")         # READ only: the served reviews define the pairs
STORES = {
    "dual_rec": os.path.join(ROOT, "evidence", "model_calls", "rob2_served"),
    "dual_runs": os.path.join(ROOT, "registry", "model_proposals", "rob2_served_runs.json"),
    "dual_out": os.path.join(SERVED, "rob2"),
    "ctx_rec": os.path.join(ROOT, "evidence", "model_calls", "rob2_served_ctx"),
    "ctx_runs": os.path.join(ROOT, "registry", "model_proposals", "rob2_served_ctx_runs.json"),
    "ctx_out": os.path.join(SERVED, "rob2_ctx"),
}
V31_OBJECTS = [os.path.join(ROOT, "outputs", "robgrade", "rob2"), os.path.join(ROOT, "outputs", "robgrade", "rob2", "dev")]


def served_pairs():
    """{slug: [pmid, ...]}: the primary-outcome trials of every served review."""
    out = {}
    for slug in sorted(os.listdir(REVIEWS)):
        if os.path.exists(os.path.join(REVIEWS, slug, "review.json")):
            out[slug] = rd.served_primary(slug)[1]
    return out


def work_list():
    """(todo, covered): the served pairs without a v3.1 object yet, and those that have one (calibration or DEV)."""
    have = {}                                          # (slug, outcome) -> trials with a v3.1 object
    for d in V31_OBJECTS:
        for f in os.listdir(d):
            if f.endswith(".json"):
                doc = rd._j(os.path.join(d, f))
                have.setdefault((f[:-5], doc.get("outcome")), set()).update(doc.get("trials") or {})
    todo, covered = {}, {}
    for slug, pm in served_pairs().items():
        outcome = rd.served_primary(slug)[0]           # an object of ANOTHER outcome covers nothing (codex r28)
        for p in pm:
            (covered if p in have.get((slug, outcome), set()) else todo).setdefault(slug, []).append(p)
    return todo, covered


@contextlib.contextmanager
def redirected():
    """The frozen pipelines with their stores moved to the served ones; every store restored afterwards, even when a
    run fails half way."""
    saved_rd = (rd.REC_DIR, rd.OUT_DIR, rd.RUNS)
    saved_rc = (rc.OBJ_DIR, rc.BASE_OUT_DIR, rc.BASE_REC_DIR, rc.BASE_RUNS, rc.OUT_DIR, rc.REC_DIR, rc.RUNS,
                list(rc.REC_READ_DIRS), rc.VARIANT)
    try:
        rd.REC_DIR, rd.OUT_DIR, rd.RUNS = STORES["dual_rec"], STORES["dual_out"], STORES["dual_runs"]
        rc.OBJ_DIR = STORES["dual_out"]
        rc.BASE_OUT_DIR, rc.BASE_REC_DIR, rc.BASE_RUNS = STORES["ctx_out"], STORES["ctx_rec"], STORES["ctx_runs"]
        rc.configure(None)                              # the A3 base, never a variant
        yield
    finally:
        rd.REC_DIR, rd.OUT_DIR, rd.RUNS = saved_rd
        (rc.OBJ_DIR, rc.BASE_OUT_DIR, rc.BASE_REC_DIR, rc.BASE_RUNS, rc.OUT_DIR, rc.REC_DIR, rc.RUNS,
         rc.REC_READ_DIRS, rc.VARIANT) = saved_rc


def _pools():
    """(pools, driver): the frozen pipeline's worker pools, as rob2_dual.main makes them."""
    return ({"codex": cf.ThreadPoolExecutor(rd.CODEX_WORKERS), "agy": cf.ThreadPoolExecutor(rd.AGY_WORKERS),
             "adjudicator": None}, cf.ThreadPoolExecutor(max(rd.CODEX_WORKERS, rd.AGY_WORKERS)))


class _Done:
    def __init__(self, v):
        self.v = v

    def result(self):
        return self.v


class _DeferAdjudication:
    """The codex pool for PHASE 1 of a live run (codex r32): reader calls go through; an adjudication is DEFERRED (no
    call), so no adjudicator is ever called on a disagreement an unreadable or ambiguous reader manufactured."""
    def __init__(self, pool):
        self.pool = pool

    def submit(self, fn, item, who, p):
        if who == "adjudicator":
            return _Done({"state": "DEFERRED", "record_id": None, "prompt_sha256": None})
        return self.pool.submit(fn, item, who, p)


def run_dual(todo, live):
    """The v3.1 dual reading of the todo pairs, by rob2_dual.process, saved per topic as each topic completes. LIVE runs
    in two phases (codex r32): readers only, then the reader checks (quarantine), then adjudication for the trials that
    passed. Every kept trial passes item_verdict; a quarantined one gets no object."""
    runs = rd._j(rd.RUNS) if os.path.exists(rd.RUNS) else {}
    pools, driver = _pools()
    rd.prefetch_registry(sorted(todo.items()))
    batches = [(slug, rd.items(slug, pm)) for slug, pm in sorted(todo.items())]
    qpath = os.path.join(SERVED, "QUARANTINE.json")
    quarantine = rd._j(qpath) if os.path.exists(qpath) else {}
    try:
        early = {}                                     # (slug, pmid) -> reason, from the reader checks of phase 1
        if live:
            p1 = dict(pools, codex=_DeferAdjudication(pools["codex"]))
            f1 = {(slug, n): driver.submit(rd.process, it, runs, True, p1) for slug, its in batches
                  for n, it in enumerate(its)}
            for slug, its in batches:
                for n, it in enumerate(its):
                    _, r = f1[(slug, n)].result()
                    runs[it["key"]] = r
                    rd._save(rd.RUNS, runs)            # after EVERY trial: a kill orphans as little as possible
                    why = reader_verdict(it, r, rd.REC_DIR)
                    if why:
                        early[(slug, it["pmid"])] = why
        futs = {(slug, n): driver.submit(rd.process, it, runs, live, pools) for slug, its in batches
                for n, it in enumerate(its) if (slug, it["pmid"]) not in early}
        for slug, its in batches:
            done = []
            for n, it in enumerate(its):
                if (slug, it["pmid"]) in early:
                    continue
                obj, r = futs[(slug, n)].result()
                runs[it["key"]] = r
                rd._save(rd.RUNS, runs)                # after EVERY trial
                rd.redact_closed_spans(obj, it)
                done.append((it, obj, r))
                print("dual", slug, it["pmid"], obj["overall"]["judgement"],
                      {w: (x or {}).get("state") for w, x in r.items()}, flush=True)
            rd._save(rd.RUNS, runs)
            results, q = keep_or_quarantine(done, rd.REC_DIR)       # codex r29: never resolved by row order
            q.update({pm: why for (sl, pm), why in early.items() if sl == slug})
            quarantine[slug] = q
            rd._save(qpath, quarantine)
            for pm, why in sorted(q.items()):
                print("QUARANTINED", slug, pm, why, flush=True)
            rd._save(os.path.join(rd.OUT_DIR, f"{slug}.json"), {"slug": slug, "family": rd.rf.FAMILY,
                                                                "outcome": its[0]["outcome"] if its else None,
                                                                "trials": results})
    finally:
        for p in pools.values():
            if p:
                p.shutdown()
        driver.shutdown()


def run_ctx(slugs, live):
    """The contextual pass (A3 base) over the served objects, by rob2_contextual.main itself."""
    rc.main((["--run"] if live else []) + sorted(slugs))


def _die(code):
    os._exit(code)                                     # no unwinding: in-flight workers die with the process


def _record_prompt_sha256(rec_dir, rid):
    import hashlib
    from reproducible_ai import model_source as ms
    p = os.path.join(rec_dir, rid + ".json")
    return hashlib.sha256(ms._unblob(ms.load_record(p)["prompt"], "prompt")).hexdigest() if os.path.exists(p) else None


ROLES = ("codex", "agy", "adjudicator")


def _record_bound(rec_dir, rid):
    """(trial pmid, outcome) a held record's prompt names (its TRIAL: / OUTCOME: lines), or None."""
    import re
    from reproducible_ai import model_source as ms
    p = os.path.join(rec_dir, str(rid) + ".json")
    if not rid or not os.path.exists(p):
        return None
    t = ms._unblob(ms.load_record(p)["prompt"], "prompt").decode("utf-8", "replace")
    m, o = re.search(r"^TRIAL: (\S+)", t, re.M), re.search(r"^OUTCOME: (.*)$", t, re.M)
    return (m.group(1), o.group(1).strip()) if m and o else None


def _record_role(rec_dir, rid):
    """The role a held record was MADE for (its caller line, call:<role>), or None."""
    p = os.path.join(rec_dir, str(rid) + ".json")
    return str(((rd._j(p).get("caller") or {}).get("line") or "")).split(":")[-1] if rid and os.path.exists(p) else None


def _entries(runs):
    """Every (key, role, entry) of a manifest: the dual one (key -> role -> entry) or the contextual one (with passes)."""
    for key, who, x, _ in _grouped(runs):
        yield key, who, x


def _grouped(runs):
    """(key, role, entry, group): the group is one pass (contextual) or the trial (dual)."""
    for key, r in runs.items():
        for n, p in enumerate((r.get("passes") or [r]) if isinstance(r, dict) else []):
            for who, x in p.items():
                if isinstance(x, dict) and "record_id" in x:
                    yield key, who, x, (key, n)


def check_manifest_records(runs, rec_dir):
    """(codex r28, r31) Every entry a served manifest names -- dual or contextual, in ANY state -- is a HELD record in
    the state the manifest gives, and a RAN_OK one carries the manifest's prompt: a stale record never answers a
    different prompt, and a success is never relabelled as a failure (which the frozen pipelines would trust)."""
    readers = {}
    for key, who, x, group in _grouped(runs):
        if who not in ROLES:                           # an entry the pipeline never reads hides a decision (codex r32)
            raise SystemExit(f"REFUSED: {key}: an entry under the unknown role {who!r}")
        if not x.get("record_id"):
            continue                                   # a call that was never made carries no record
        if _record_role(rec_dir, x["record_id"]) != who:   # a record answers only for the role it was made for (r32)
            raise SystemExit(f"REFUSED: {key} {who}: record {x['record_id']} was not made by the {who} call")
        parts = str(key).split("::")
        if len(parts) == 3 and _record_bound(rec_dir, x["record_id"]) != (parts[1], parts[2].strip()):
            # (codex r34) a record answers only for the trial and outcome its prompt names
            raise SystemExit(f"REFUSED: {key} {who}: record {x['record_id']} is about another trial or outcome")
        if who in ("codex", "agy"):
            if x["record_id"] in readers.setdefault(group, set()):
                raise SystemExit(f"REFUSED: {key}: one record stands for both readers")
            readers[group].add(x["record_id"])
        if _record_state(rec_dir, x["record_id"]) != x.get("state"):
            raise SystemExit(f"REFUSED: {key} {who}: record {x['record_id']} is not held in the state {x.get('state')}")
        if x.get("state") == "RAN_OK" and _record_prompt_sha256(rec_dir, x["record_id"]) != x.get("prompt_sha256"):
            raise SystemExit(f"REFUSED: {key} {who}: record {x['record_id']} answers another prompt")


def served_keys(todo):
    """The pipeline's own trial keys (rob2_dual.items: slug::pmid::served primary outcome) for the served pairs."""
    return {f"{slug}::{p}::{rd.served_primary(slug)[0]}" for slug, pm in todo.items() for p in pm}


def check_accounted(runs, rec_dir, consumed=False, keys=None):
    """(codex r31) Every HELD successful record in a served store is accounted for: named by the manifest (dual) or
    READ by the replay (contextual: consumed=True). Deleting a manifest entry can never erase a decision silently.
    (codex r33) Only the served trials' own keys count: an entry parked under a key of no served trial is REFUSED."""
    import glob
    if keys is not None:
        stray = sorted(set(runs) - set(keys))
        if stray:
            raise SystemExit(f"REFUSED: manifest keys of no served trial in {rec_dir}: {stray}")
    ok = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(rec_dir, "mc-*.json"))
          if rd._j(f).get("state") == "RAN_OK"}
    if consumed:
        seen = {rid for r in runs.values() if isinstance(r, dict) for rid in r.get("consumed") or []}
    else:
        seen = {x["record_id"] for _, _, x in _entries(runs) if x.get("record_id")}
    missing = sorted(ok - seen)
    if missing:
        raise SystemExit(f"REFUSED: held successful records not accounted for in {rec_dir}: {missing}")


def conflicting_rows(reply):
    """(codex r28) Questions a reply answers in two rows with DIFFERENT answers (the frozen v3.1 verifier keeps the
    first): reported for every served reply, never silently resolved by order."""
    seen = {}
    for row in (reply or {}).get("answers") or []:
        if isinstance(row, dict):
            seen.setdefault(row.get("qid"), set()).add(row.get("answer"))
    return sorted(q for q, a in seen.items() if q is not None and len(a) > 1)


def _sha(b):
    import hashlib
    return hashlib.sha256(b).hexdigest()


def _record_state(rec_dir, rid):
    """The held record's own state (RAN_OK / RAN_ERROR / ...), or None when it is not held."""
    p = os.path.join(rec_dir, str(rid) + ".json")
    return rd._j(p).get("state") if rid and os.path.exists(p) else None


def _fresh(entry, want, rec_dir, what, who=None):
    """An entry must be a HELD record in the state the manifest says (codex r30), made for its role (r32), answering
    THE CURRENT prompt in the manifest and in the record; else REFUSED (a stale or relabelled store)."""
    if who and _record_role(rec_dir, entry.get("record_id")) != who:
        raise SystemExit(f"REFUSED: {what}: record {entry.get('record_id')} was not made by the {who} call")
    if _record_state(rec_dir, entry.get("record_id")) != entry.get("state"):
        raise SystemExit(f"REFUSED: {what}: record {entry.get('record_id')} is not held in the state "
                         f"{entry.get('state')} the manifest gives")
    if entry.get("prompt_sha256") != want or _record_prompt_sha256(rec_dir, entry.get("record_id")) != want:
        raise SystemExit(f"REFUSED: {what}: record {entry.get('record_id')} does not answer the current prompt (stale)")


def _reply_problem(entry, who):
    rep = rd.replay(entry)               # the frozen replay returns the PARSED reply, or None (codex/agy r30)
    if rep is None:
        return f"unreadable reply: {who}"
    c = conflicting_rows(rep)
    return f"conflicting rows {c}: {who}" if c else None


def item_verdict(item, r, rec_dir):
    """(codex r29) The served dual reading of one trial, checked with the frozen pipeline's OWN functions:
    - every RAN_OK reader entry answers the prompt built NOW from the item's current evidence, and an adjudication
      answers exactly the disagreement those fresh readers make (none when they agree) -- else REFUSED (a stale store);
    - a reader or adjudicator reply that is unreadable, or answers one question twice differently, QUARANTINES the
      trial (returned reason): the frozen v3.1 pipeline would resolve it by row order or as a manufactured NI.
    None when the trial's object may be kept."""
    if not rd.open_sources(item):
        return None
    why = reader_verdict(item, r, rec_dir)
    if why:
        return why
    dis = {}
    if (r.get("codex") or {}).get("state") == "RAN_OK" and (r.get("agy") or {}).get("state") == "RAN_OK":
        typed, _ = rt.typed_answers(item["sources"], item.get("machine_d5"), outcome=item.get("outcome"))
        a = rd.verify_answers(rd.replay(r.get("codex")), item)
        b = rd.verify_answers(rd.replay(r.get("agy")), item)
        dis = {q: v for q, v in rd.agree(a, b)[1].items() if q not in typed}
    adj = r.get("adjudicator")
    if not dis:
        if adj:
            raise SystemExit(f"REFUSED: {item['key']}: an adjudication is recorded but the fresh readers agree")
        return None
    pa = _sha(rd.prompt_bytes(item, "adjudicator", {q: {"reader 1": x, "reader 2": y} for q, (x, y) in dis.items()}))
    if not adj or adj.get("prompt_sha256") != pa:
        raise SystemExit(f"REFUSED: {item['key']}: no adjudication of the disagreement the fresh readers make")
    _fresh(adj, pa, rec_dir, f"{item['key']} adjudicator", "adjudicator")   # a FAILED attempt: a held failed record
    if adj.get("state") == "RAN_OK":
        return _reply_problem(adj, "adjudicator")
    return None                                        # a held, recorded FAILED adjudication: an honest NI


def reader_verdict(item, r, rec_dir):
    """The READER half of item_verdict: each reader held, made for its role, in its stated state, for the current
    prompt (else REFUSED); a missing or failed reader (agy r32: the contextual pipeline's rule -- a missing reader voids
    the reading), or an unreadable or ambiguous reply, QUARANTINES the trial. None when both readings may be used."""
    if not rd.open_sources(item):
        return None
    ps = _sha(rd.prompt_bytes(item))
    if (r.get("codex") or {}).get("record_id") and (r.get("codex") or {}).get("record_id") == \
            (r.get("agy") or {}).get("record_id"):
        raise SystemExit(f"REFUSED: {item['key']}: one record stands for both readers")
    for who in ("codex", "agy"):
        x = r.get(who) or {}
        if not x.get("record_id"):
            return f"missing reader: {who}"
        _fresh(x, ps, rec_dir, f"{item['key']} {who}", who)
        if x.get("state") != "RAN_OK":
            return f"failed reader ({x.get('state')}): {who}"
        why = _reply_problem(x, who)
        if why:
            return why
    return None


def adopt_orphans(items, runs, rec_dir):
    """(the run killed on 14 Oct) Held SUCCESSFUL reader records that no manifest entry names -- a run killed before its
    manifest was saved -- are adopted into a trial's slot ONLY when provably that slot's: made for that reader role,
    about that trial and outcome, for the CURRENT reader prompt, the ONLY such record, and the slot holds no fresh entry.
    Each adopted entry is exactly what rob2_dual._call writes. Anything else stays unaccounted, and check_accounted then
    REFUSES the run. [(key, role, record id)] adopted."""
    import glob
    named = {x["record_id"] for _, _, x in _entries(runs) if x.get("record_id")}
    want = {(it["pmid"], it["outcome"]): (it["key"], _sha(rd.prompt_bytes(it))) for it in items if rd.open_sources(it)}
    cands = {}
    for f in sorted(glob.glob(os.path.join(rec_dir, "mc-*.json"))):
        rid, rec = os.path.basename(f)[:-5], rd._j(f)
        if rec.get("state") != "RAN_OK" or rid in named:
            continue
        role = _record_role(rec_dir, rid)
        key_ps = want.get(_record_bound(rec_dir, rid) or ())
        if role not in ("codex", "agy") or not key_ps or _record_prompt_sha256(rec_dir, rid) != key_ps[1]:
            continue
        cands.setdefault((key_ps[0], role), []).append((rid, rec, key_ps[1]))
    adopted = []
    for (key, role), c in sorted(cands.items()):
        slot = (runs.get(key) or {}).get(role) or {}
        if len(c) != 1 or (slot.get("state") == "RAN_OK" and slot.get("prompt_sha256") == c[0][2]):
            continue                                   # two candidates, or a fresh entry already: not provable
        rid, rec, ps = c[0]
        runs.setdefault(key, {})[role] = {"record_id": rid, "state": "RAN_OK", "error": rec.get("error"),
                                          "prompt_sha256": ps, "model": (rec.get("model") or {}).get("id_reported")}
        adopted.append((key, role, rid))
    return adopted


def adopt_stage(todo):
    """Adopt the provable orphans of a killed run into the served dual manifest (saved); [(key, role, record id)]."""
    rd.prefetch_registry(sorted(todo.items()))
    items = [it for slug, pm in sorted(todo.items()) for it in rd.items(slug, pm)]
    runs = rd._j(rd.RUNS) if os.path.exists(rd.RUNS) else {}
    adopted = adopt_orphans(items, runs, rd.REC_DIR)
    if adopted:
        rd._save(rd.RUNS, runs)
    print(f"orphaned reader records adopted: {len(adopted)}", flush=True)
    return adopted


def keep_or_quarantine(done, rec_dir):
    """({pmid: object} kept, {pmid: reason} quarantined) for one topic's [(item, object, run)]."""
    kept, quarantined = {}, {}
    for item, obj, r in done:
        why = item_verdict(item, r, rec_dir)
        if why:
            quarantined[item["pmid"]] = why
        else:
            kept[item["pmid"]] = obj
    return kept, quarantined


def audit(rec_dir):
    """[(record id, [question ids])] of the served replies with conflicting duplicate rows."""
    import glob
    from reproducible_ai import model_source as ms
    from robgrade import contextual as cx
    out = []
    for f in sorted(glob.glob(os.path.join(rec_dir, "mc-*.json"))):
        r = ms.load_record(f)
        if r["state"] == "RAN_OK":
            c = conflicting_rows(cx.parse_reply(ms.replay(r)))
            if c:
                out.append((os.path.basename(f)[:-5], c))
    return out


FLAGS = ("--run", "--dual-only")


def main(argv):
    bad = [a for a in argv if a.startswith("--") and a not in FLAGS]
    if bad:                      # no --ctx-only: the contextual stage never runs without the guarded dual stage (r30)
        raise SystemExit(f"REFUSED: unknown option(s) {bad}; options: {', '.join(FLAGS)}")
    live = "--run" in argv
    todo, covered = work_list()
    want = [a for a in argv if not a.startswith("--")]
    if want:
        todo = {s: p for s, p in todo.items() if s in want}
    print(f"served primary pairs: {sum(len(v) for v in todo.values()) + sum(len(v) for v in covered.values())}; "
          f"with a v3.1 object: {sum(len(v) for v in covered.values())}; to read: {sum(len(v) for v in todo.values())} "
          f"in {len(todo)} topics", flush=True)
    # every served trial's key (not only this run's selection): a store may hold earlier topics' trials
    all_keys = served_keys(served_pairs())
    with redirected():
        try:
            adopt_stage(todo)                          # a killed run's provable orphans (14 Oct), before any check
            # every existing manifest is checked BEFORE its stage runs (codex r31: a stale entry must never reach a
            # prompt) and again after it
            for when in ("before", "after"):
                if when == "after":
                    run_dual(todo, live)
                runs = rd._j(rd.RUNS) if os.path.exists(rd.RUNS) else {}
                check_manifest_records(runs, rd.REC_DIR)
                check_accounted(runs, rd.REC_DIR, keys=all_keys)
            if "--dual-only" not in argv:
                for when in ("before", "after"):
                    if when == "after":
                        run_ctx(todo, live)
                    runs = rd._j(rc.RUNS) if os.path.exists(rc.RUNS) else {}
                    check_manifest_records(runs, rc.REC_DIR)
                    check_accounted(runs, rc.REC_DIR, consumed=True, keys=all_keys)
        except BaseException:                          # never unwind into a restore while workers may be alive (r28)
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            _die(1)
    for name, d in (("dual", STORES["dual_rec"]), ("contextual", STORES["ctx_rec"])):
        a = audit(d) if os.path.isdir(d) else []
        print(f"{name} replies with conflicting duplicate rows: {len(a)}" + (f" {a}" if a else ""), flush=True)


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
