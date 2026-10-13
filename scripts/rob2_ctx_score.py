"""Score the PRE-REGISTERED contextual-answer rule on TEST (outputs/robgrade/CONTEXTUAL_POLICY.md section 3):
agreement with the published per-trial domain judgements, n of N, in the NI policy's three columns -- all pairs,
excluding NI-driven pairs, NI-driven pairs alone -- beside the same table for v3.1.

Refuses unless
  (a) the anchor is the commit that first added CONTEXTUAL_POLICY.md, an ancestor of HEAD, and every policy file and
      frozen input (split, comparator transcriptions, the v3.1 objects and calibration) is byte-identical to it;
  (b) the contextual objects keep the v3.1 cohort, and every answer equals v3.1's EXCEPT an asked NI that became a
      contextual PY/PN carrying a quote, its source sha256, and records made after the pre-registration;
  (c) every judgement and label is recomputed from the stored answers and matches; no TEST-external trial, duplicate.
git output is decoded as UTF-8 (the NI scorer's cp1252 false refusal, 12 Oct).

    python scripts/rob2_ctx_score.py PREREG_SHA   -> outputs/robgrade/CTX_SCORE.md + ctx_score.json
"""
import collections
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from robgrade import contextual as cx  # noqa: E402
from robgrade import ni_policy as nip  # noqa: E402
from robgrade import rob2_formal as rf  # noqa: E402
import rob2_calibrate as cal  # noqa: E402

TOPICS = ["balanced-crystalloids-vs-saline-mortality", "iv-iron-hfref-hosp", "probiotics-aad-prevention",
          "ticagrelor-vs-clopidogrel-acs"]
POLICY_FILES = ["outputs/robgrade/CONTEXTUAL_POLICY.md", "robgrade/contextual.py", "scripts/rob2_contextual.py",
                "scripts/rob2_ctx_score.py", "robgrade/rob2_formal.py", "robgrade/ni_policy.py",
                "tests/test_rob2_contextual.py",
                # everything the score depends on (codex review round 1): pairing, evidence, typed answers, licences,
                # and the label the served page shows
                "scripts/rob2_calibrate.py", "scripts/rob2_dual.py", "robgrade/rob2_typed.py", "robgrade/prompt_licence.py",
                "robgrade/rob2_tab.py", "tests/test_rob2_tab.py",
                # and the NI policy the labels apply, and the record store's verifier/replayer (codex round 4)
                "outputs/robgrade/NI_POLICY.md", "reproducible_ai/model_source.py"]
INPUT_FILES = ["outputs/robgrade/split.json", "outputs/robgrade/calibration_v31.json"] + \
              [f"outputs/robgrade/reference/{t}.json" for t in TOPICS] + [f"outputs/robgrade/rob2/{t}.json" for t in TOPICS]
CTX_DIR = os.path.join(ROOT, "outputs", "robgrade", "rob2_ctx")
REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "rob2_ctx")
V31 = os.path.join(ROOT, "outputs", "robgrade", "calibration_v31.json")
DISCLOSURE = ("A comparator row is matched to our trial by PMID only: result identity (the same outcome, time point and "
              "numerical result) is NOT verified, so these counts do not establish agreement on the same result "
              "(RoB 2 rates a result; Handbook 8.2.1).")


def _git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True, encoding="utf-8")


def check_prereg(sha):
    full = _git("rev-parse", sha).stdout.strip()
    added = [x for x in _git("log", "--diff-filter=A", "--format=%H", "--", POLICY_FILES[0]).stdout.split() if x]
    if not added or full != added[-1]:
        raise SystemExit(f"REFUSED: {sha} is not the commit that added {POLICY_FILES[0]}")
    if _git("merge-base", "--is-ancestor", sha, "HEAD").returncode != 0:
        raise SystemExit(f"REFUSED: {sha} is not an ancestor of HEAD")
    # every frozen file must EXIST in the pre-registration: git diff ignores untracked files (codex round 2)
    absent = [f for f in POLICY_FILES + INPUT_FILES if _git("cat-file", "-e", f"{sha}:{f}").returncode != 0]
    if absent:
        raise SystemExit(f"REFUSED: frozen files not in the pre-registration {sha}: {absent}")
    changed = [f for f in POLICY_FILES + INPUT_FILES if _git("diff", "--quiet", sha, "--", f).returncode != 0]
    if changed:
        raise SystemExit(f"REFUSED: files differ from the pre-registration {sha}: {changed}")
    return full


def prereg_time(sha):
    return _git("show", "-s", "--format=%cI", sha).stdout.strip()


def _utc(iso):
    import datetime
    return datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(datetime.timezone.utc)


def load_record(rid):
    """A contextual-pass record as the checks need it: state, caller, the EXACT prompt bytes (sha-checked by
    model_source), the stored reply, input digests and request time. None when the record is not held."""
    from reproducible_ai import model_source as ms
    p = os.path.join(REC_DIR, rid + ".json")
    if not os.path.exists(p):
        return None
    r = ms.load_record(p)
    return {"state": r["state"], "caller": r["caller"], "prompt_text": ms._unblob(r["prompt"], "prompt").decode("utf-8"),
            "reply": ms.replay(r).decode("utf-8") if r["state"] == "RAN_OK" else "",
            "input_digests": r["input_digests"], "request_utc": r["request_utc"]}


def _sources(rec):
    """The sources a recorded call was SHOWN (its prompt's evidence block), each with the sha256 the call recorded as
    its input digest: the only material a recorded answer may rest on."""
    t = rec["prompt_text"]
    block = json.loads(t[t.index("=== EVIDENCE ===") + len("=== EVIDENCE ==="):])
    sha = {d.get("ref"): d.get("sha256") for d in rec.get("input_digests") or []}
    return [{"id": s["id"], "text": s.get("text") or s.get("abstract") or "", "sha256": sha.get(s["id"]),
             "open_for_prompt": True} for s in block["sources"]]


def _bound_to(rec, trial, outcome):
    """The TRIAL and OUTCOME a recorded prompt was about (codex round 2: a record is bound to its assessment)."""
    import re
    t = re.search(r"^TRIAL: (\S+)", rec["prompt_text"], re.M)
    o = re.search(r"^OUTCOME: (.*)$", rec["prompt_text"], re.M)
    return (t.group(1) if t else None) == str(trial) and (o.group(1).strip() if o else None) == str(outcome).strip()


def _verified(rec, qid):
    """The recorded reply put through the SAME verify() as the pipeline (codex round 2): an empty quote, a generic or
    unreferenced rationale, a quote not in the shown source -- all NI here as there."""
    t = rec["reply"].strip()
    try:
        reply = json.loads(t[t.index("{"):t.rindex("}") + 1])
    except ValueError:
        reply = None
    return cx.verify(reply, _sources(rec), [qid])[qid]


def registered(rec, kind):
    """(targets, readings) when the recorded prompt's head is EXACTLY what the pipeline's prompt_head builds from its
    own trial, outcome, targets (and readings) -- nothing inserted, no question reworded (codex round 4); else None."""
    import re
    import rob2_contextual as rc
    t = rec["prompt_text"]
    if rc.EVIDENCE_MARK not in t:
        return None
    head = t[:t.index(rc.EVIDENCE_MARK)]
    m = re.search(r"^TRIAL: (\S+) \((.*)\)$", head, re.M)
    o = re.search(r"^OUTCOME: (.*)$", head, re.M)
    if not m or not o or "SIGNALLING QUESTIONS:\n" not in head:
        return None
    block = head[head.index("SIGNALLING QUESTIONS:\n") + len("SIGNALLING QUESTIONS:\n"):].split("\n\n")[0]
    targets = [ln.split(" ", 1)[0] for ln in block.split("\n") if ln.strip()]
    readings = None
    if kind == "adjudicator":
        if "\nTHE TWO READINGS:\n" not in head:
            return None
        try:
            readings = json.loads(head[head.index("\nTHE TWO READINGS:\n") + len("\nTHE TWO READINGS:\n"):])
        except ValueError:
            return None
    nct = None if m.group(2) == "no registry id" else m.group(2)
    try:
        expect = rc.prompt_head(m.group(1), nct, o.group(1), targets, kind, readings)
    except KeyError:                                   # a question id the tool does not have
        return None
    return (targets, readings) if head == expect else None


def verify_records(qid, a, load=None, trial=None, outcome=None):
    """A contextual answer stands only on its RECORDS (codex/agy rounds 1-2):
      - both readers' records, and the adjudicator's when it decided, all held and RAN_OK, all about THIS trial and
        outcome;
      - each reply re-verified by contextual.verify against the sources its own prompt showed;
      - agreement: both readers verify as this answer; adjudication: the readers verified DIFFERENTLY and the
        adjudicator verifies as this answer;
      - the stored context is exactly the deciding verified context(s), its first entry the stored span and source."""
    load = load or load_record
    recs = {rid: load(rid) for rid in a.get("records") or []}
    if any(r is None or r["state"] != "RAN_OK" for r in recs.values()):
        raise SystemExit(f"REFUSED: {qid}: a cited record is missing or not RAN_OK")
    if trial is not None and not all(_bound_to(r, trial, outcome) for r in recs.values()):
        raise SystemExit(f"REFUSED: {qid}: a cited record is about another trial or outcome")
    adjudicated = str(a.get("note") or "").startswith("adjudicator")
    roles = [r["caller"]["line"].split(":")[1] for r in recs.values()]
    # a role VOCABULARY is a tuple (reproducible_ai.model_inventory: a list headed by a CLI name is an argv)
    want_roles = ("codex", "agy") + (("adjudicator",) if adjudicated else ())
    if not {"codex", "agy"} <= set(roles) or (adjudicated and "adjudicator" not in roles):
        raise SystemExit(f"REFUSED: {qid}: a contextual answer needs both readers' records{' and the adjudicator' if adjudicated else ''}")
    if sorted(roles) != sorted(want_roles):            # no duplicate or extraneous record (agy round 4)
        raise SystemExit(f"REFUSED: {qid}: exactly one record per role is required ({', '.join(want_roles)}); got {roles}")
    by = {r["caller"]["line"].split(":")[1]: r for r in recs.values()}
    # blind and registered (codex rounds 3-4): both readers saw the SAME prompt, and its head is EXACTLY the registered
    # reader prompt for its trial, outcome and targets (rebuilt by the pipeline's own prompt_head)
    reg = registered(by["codex"], "reader")
    if by["codex"]["prompt_text"] != by["agy"]["prompt_text"] or reg is None or qid not in reg[0]:
        raise SystemExit(f"REFUSED: {qid}: the two readers did not see the same registered prompt")
    v1, v2 = _verified(by["codex"], qid), _verified(by["agy"], qid)
    if adjudicated:
        if v1["answer"] == v2["answer"]:
            raise SystemExit(f"REFUSED: {qid}: the readers agreed ({v1['answer']}): there was nothing to adjudicate")
        regj = registered(by["adjudicator"], "adjudicator")
        if regj is None or qid not in regj[0] or (regj[1] or {}).get(qid) != {"reader 1": v1, "reader 2": v2}:
            raise SystemExit(f"REFUSED: {qid}: the adjudicator was not shown these two readings under the registered prompt")
        deciding = [("adjudicator", _verified(by["adjudicator"], qid))]
    else:
        deciding = [("reader 1", v1), ("reader 2", v2)]
    for who, v in deciding:
        if v["answer"] != a["answer"]:
            why = (v.get("dropped") or {}).get("why", "")
            raise SystemExit(f"REFUSED: {qid}: the {who} reply does not verify as {a['answer']} ({v['answer']} {why})")
        if not v.get("source_sha256"):
            raise SystemExit(f"REFUSED: {qid}: the {who} call recorded no sha256 for its cited source")
    keys = ("quote", "source_id", "source_sha256", "rationale")
    want = [{k: v.get(k) for k in keys} for _, v in deciding]
    have = [{k: c.get(k) for k in keys} for c in a.get("context") or []]
    if have != want:
        raise SystemExit(f"REFUSED: {qid}: the stored context (quote, source, sha256, rationale) differs from the verified replies")
    if (a.get("span"), a.get("source_ref"), a.get("source_sha256")) != (want[0]["quote"], want[0]["source_id"],
                                                                        want[0]["source_sha256"]):
        raise SystemExit(f"REFUSED: {qid}: the stored span, source or sha256 differs from the deciding verified reply")


def check_contextual_doc(slug, base, ctx, after_iso, record_time=None, verify_records=None):
    """(b) and (c): the cohort, the domains, every answer key; every answer equal to v3.1 except an asked NI become a
    contextual PY/PN that its records verify; the eligibility, each judgement, label and overall recomputed."""
    record_time = record_time or (lambda rid: (load_record(rid) or {}).get("request_utc"))
    check = verify_records or globals()["verify_records"]
    if set(base["trials"]) != set(ctx["trials"]):
        raise SystemExit(f"REFUSED: {slug}: trials differ from v3.1")
    n = collections.Counter()
    for pmid, o in ctx["trials"].items():
        b = base["trials"][pmid]
        if (o.get("trial"), o.get("outcome"), set(o["domains"])) != (b.get("trial"), b.get("outcome"), set(b["domains"])):
            raise SystemExit(f"REFUSED: {slug} {pmid}: trial, outcome or domains differ from v3.1")
        targets = set(cx.ni_targets(b))
        for d, dom in o["domains"].items():
            bd = b["domains"][d]
            if (dom["judgement"] == rf.INSUFFICIENT) != (bd["judgement"] == rf.INSUFFICIENT):
                raise SystemExit(f"REFUSED: {slug} {pmid} {d}: eligibility (INSUFFICIENT_OPEN_SOURCE) changed from v3.1")
            if set(dom["answers"]) != set(bd["answers"]):
                raise SystemExit(f"REFUSED: {slug} {pmid} {d}: answers differ from v3.1 (a question added or deleted)")
            asked_now = rf.applicable(d, dom["answers"])
            for q, a in dom["answers"].items():
                if a == bd["answers"][q]:
                    continue
                # a contextual answer upstream can close a branch: a question no longer asked, NI before, is NA now
                # (agy round 2) -- allowed only when some contextual answer in this domain closed it
                if (a.get("answer") == "NA" and q not in asked_now and rf._a(bd["answers"], q) == "NI"
                        and any(x.get("basis") == "contextual" for x in dom["answers"].values())):
                    continue
                # ... or OPEN one (codex round 3): a question asked now, NA before, is NI now -- never guessed, and
                # only when some contextual answer in this domain opened it
                if (a.get("answer") == "NI" and q in asked_now and (bd["answers"][q] or {}).get("answer") == "NA"
                        and any(x.get("basis") == "contextual" for x in dom["answers"].values())):
                    continue
                # a contextual answer may replace a v3.1 NI target, or a question a contextual answer OPENED (NA in
                # v3.1, asked now) -- answered in a later pass (codex round 4)
                opened = (bd["answers"][q] or {}).get("answer") == "NA" and q in asked_now
                if not ((q in targets or opened) and a.get("basis") == "contextual" and a.get("answer") in cx.CONTEXTUAL
                        and a.get("span") and a.get("source_sha256") and a.get("records")):
                    raise SystemExit(f"REFUSED: {slug} {pmid} {q}: changed from v3.1 other than NI -> documented contextual PY/PN")
                for rid in a["records"]:
                    t = record_time(rid)
                    if t is None:                       # refused, never a crash (agy round 4)
                        raise SystemExit(f"REFUSED: {slug} {pmid} {q}: cited record {rid} is missing")
                    if _utc(t) <= _utc(after_iso):
                        raise SystemExit(f"REFUSED: {slug} {pmid} {q}: record {rid} predates the pre-registration")
                check(q, a, trial=pmid, outcome=o.get("outcome"))
                n[q] += 1
            if dom["judgement"] != rf.INSUFFICIENT:
                lab = rf.ni_label(d, dom["answers"])
                if lab["judgement"] != dom["judgement"] or {k: v for k, v in lab.items() if k != "judgement"} != dom.get("ni"):
                    raise SystemExit(f"REFUSED: {slug} {pmid} {d}: stored judgement/label != recomputed")
        ov = rf.overall({d: x["judgement"] for d, x in o["domains"].items()})
        ov["ni"] = rf.overall_ni(o["domains"])
        if ov != o["overall"]:
            raise SystemExit(f"REFUSED: {slug} {pmid}: stored overall != recomputed")
        # the decision audit agrees with the answers (codex round 4): a recorded PY/PN decision stands in the answers
        # (or on a branch since closed), a stored contextual answer has its decision, an NI decision left no answer
        stored = {q: x for dom in o["domains"].values() for q, x in dom["answers"].items()}
        audit = o.get("contextual_audit") or {}
        for q, x in stored.items():
            if x.get("basis") == "contextual" and (audit.get(q) or {}).get("answer") != x.get("answer"):
                raise SystemExit(f"REFUSED: {slug} {pmid} {q}: a contextual answer without a matching decision in the audit")
        for q, dec in audit.items():
            x = stored.get(q) or {}
            if dec.get("answer") in cx.CONTEXTUAL:
                if not ((x.get("basis") == "contextual" and x.get("answer") == dec["answer"]
                         and list(x.get("records") or []) == list(dec.get("records") or [])) or x.get("answer") == "NA"):
                    raise SystemExit(f"REFUSED: {slug} {pmid} {q}: the audit's {dec['answer']} decision is not in the answers")
            elif x.get("basis") == "contextual":
                raise SystemExit(f"REFUSED: {slug} {pmid} {q}: the audit decided NI but a contextual answer is stored")
    return n


def pairs_from(dir_, slugs, test):
    keep = cal.OURS
    cal.OURS = dir_
    try:
        pairs, excluded, unmatched, tools, seen = [], [], [], {}, set()
        for s in slugs:
            p, e, u, t = cal.pairs_for(s)
            for x in p:
                k = (x["slug"], x["pmid"], x["domain"])
                if x["pmid"] not in test:
                    raise SystemExit(f"REFUSED: {k} is not a TEST trial")
                if k in seen:
                    raise SystemExit(f"REFUSED: duplicate pair {k}")
                seen.add(k)
            pairs += p
            excluded += e
            unmatched += u
            tools[s] = t
        return pairs, excluded, unmatched, tools
    finally:
        cal.OURS = keep


def _canon(x):
    return json.loads(json.dumps(x, sort_keys=True, ensure_ascii=False))


def check_replay(slug, ctx, regenerated):
    """(codex round 5) The scored objects must be EXACTLY what the frozen pipeline reproduces, in replay mode, from the
    held records and the authoritative trial sources. A record whose prompt was not built from the real sources is not
    fresh there (substituted evidence), and an omitted decision is reproduced (selective restoration): either one
    differs here."""
    if set(ctx["trials"]) != set(regenerated):
        raise SystemExit(f"REFUSED: {slug}: the replay reproduces a different set of trials")
    for pmid, o in ctx["trials"].items():
        if _canon(o) != _canon(regenerated[pmid]):
            raise SystemExit(f"REFUSED: {slug} {pmid}: the scored object is not what the registered pipeline reproduces "
                             "from the held records")


def check_manifest(runs, held):
    """Every held contextual-pass record (made after the pre-registration) is referenced by the run manifest: a record
    the manifest drops would be a recorded decision left out of the replay (codex round 5)."""
    referenced = {x["record_id"] for r in runs.values() for p in r.get("passes") or [] for x in p.values()
                  if isinstance(x, dict) and x.get("record_id")}
    missing = sorted(set(held) - referenced)
    if missing:
        raise SystemExit(f"REFUSED: held records not referenced by the run manifest: {missing}")


def check_consumed(consumed, held):
    """(codex round 6) Every held post-registration RAN_OK record must have been READ by the replay: a decision record
    parked where the replay never reads it (e.g. an unexecuted pass) would be an omission. A RAN_ERROR record is a
    failed attempt (a retry) and carries no decision: it is accounted for, never refused."""
    unread = sorted(rid for rid, state in held.items() if state == "RAN_OK" and rid not in set(consumed))
    if unread:
        raise SystemExit(f"REFUSED: held RAN_OK records not consumed by the replay: {unread}")
    return sorted(rid for rid, state in held.items() if state != "RAN_OK")


def check_consumed_times(consumed, after_iso, record_time=None):
    """(codex round 6) Every record the replay READ -- including records that decided NI -- postdates the
    pre-registration."""
    record_time = record_time or (lambda rid: (load_record(rid) or {}).get("request_utc"))
    for rid in sorted(set(consumed)):
        t = record_time(rid)
        if t is None:
            raise SystemExit(f"REFUSED: consumed record {rid} is missing")
        if _utc(t) <= _utc(after_iso):
            raise SystemExit(f"REFUSED: consumed record {rid} predates the pre-registration")


def replay_all(slugs):
    """{slug: {pmid: object}} regenerated by scripts/rob2_contextual.process in REPLAY mode (no model call), from the
    v3.1 objects, the run manifest, the held records and the authoritative sources (scripts/rob2_dual.items)."""
    import rob2_contextual as rc
    import rob2_dual as rd
    runs = json.load(open(rc.RUNS, encoding="utf-8")) if os.path.exists(rc.RUNS) else {}
    docs = {s: json.load(open(os.path.join(cal.OURS, f"{s}.json"), encoding="utf-8")) for s in slugs}
    rd.prefetch_registry([(s, sorted(docs[s]["trials"])) for s in slugs])
    out, consumed = {}, []
    for s in slugs:
        items = {it["pmid"]: it for it in rd.items(s, sorted(docs[s]["trials"]))}
        out[s] = {}
        for pmid, o in docs[s]["trials"].items():
            new, r, _ = rc.process(items[pmid], o, runs, False, {})
            rd.redact_closed_spans(new, items[pmid])
            out[s][pmid] = new
            consumed += r.get("consumed") or []
    return out, runs, consumed


def main(argv):
    if len(argv) != 1:
        raise SystemExit("REFUSED: the scorer takes the pre-registration SHA only; all four registered comparators are scored")
    sha = check_prereg(argv[0])
    after = prereg_time(sha)
    test = set(json.load(open(os.path.join(ROOT, "outputs", "robgrade", "split.json"), encoding="utf-8"))["test"])
    regen, runs, consumed = replay_all(TOPICS)
    held = {}
    for f in __import__("glob").glob(os.path.join(REC_DIR, "mc-*.json")):
        rec = load_record(os.path.basename(f)[:-5])
        if _utc(rec["request_utc"]) > _utc(after):
            held[os.path.basename(f)[:-5]] = rec["state"]
    failed_attempts = check_consumed(consumed, held)    # every post-registration decision record was READ
    check_consumed_times(consumed, after)               # and everything READ postdates the pre-registration
    counts = collections.Counter()
    for s in TOPICS:
        base = json.load(open(os.path.join(cal.OURS, f"{s}.json"), encoding="utf-8"))
        ctx = json.load(open(os.path.join(CTX_DIR, f"{s}.json"), encoding="utf-8"))
        check_replay(s, ctx, regen[s])
        counts += check_contextual_doc(s, base, ctx, after)
    pairs, excluded, unmatched, tools = pairs_from(CTX_DIR, TOPICS, test)
    t = nip.two_way(pairs)
    t31 = nip.two_way(json.load(open(V31, encoding="utf-8"))["pairs"])
    b = {(p["slug"], p["pmid"], p["domain"]): p for p in json.load(open(V31, encoding="utf-8"))["pairs"]}
    moved = [[p["slug"], p["pmid"], p["domain"], b[k]["ours"], p["ours"], p["theirs"]] for p in pairs
             for k in [(p["slug"], p["pmid"], p["domain"])] if k in b and b[k]["ours"] != p["ours"]]
    res = {"preregistration_commit": sha, "topics": TOPICS, "tools": tools, "two_way": t, "two_way_v31": t31,
           "contextual_answers_by_question": dict(sorted(counts.items())), "moved_from_v31": moved,
           "excluded": len(excluded), "unmatched_trials": len(unmatched), "result_identity": DISCLOSURE,
           "failed_attempts_accounted": failed_attempts, "records_consumed": len(set(consumed))}
    with open(os.path.join(ROOT, "outputs", "robgrade", "ctx_score.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1)
    f = lambda c: f"{c['agree']} / {c['N']}"
    lines = ["# Contextual 'probably' answers on TEST: agreement with the published per-trial judgements, n of N", "",
             f"Pre-registered rule: commit {sha} (outputs/robgrade/CONTEXTUAL_POLICY.md). Only asked NI answers could "
             "change, only to a documented contextual PY/PN (checked against v3.1, answer by answer).", "",
             f"Coverage: {len(excluded)} records excluded, {len(unmatched)} trials unmatched (not in any N).", "", DISCLOSURE, "",
             "| domain | all (contextual) | excl. NI-driven (contextual) | NI-driven only (contextual) | all (v3.1) | "
             "excl. NI-driven (v3.1) | NI-driven only (v3.1) |", "|---|---|---|---|---|---|---|"]
    for d in nip.DOMS + ("all",):
        lines.append(f"| {d} | {f(t['all'][d])} | {f(t['excluding_ni_driven'][d])} | {f(t['ni_driven_only'][d])} | "
                     f"{f(t31['all'][d])} | {f(t31['excluding_ni_driven'][d])} | {f(t31['ni_driven_only'][d])} |")
    lines += ["", "Contextual answers by question: " + (", ".join(f"{q}: {n}" for q, n in sorted(counts.items())) or "none"),
              "", f"Judgements moved from v3.1: {len(moved)}"]
    lines += [f"- {a} {b_} {c}: {o} -> {n} (comparator {th})" for a, b_, c, o, n, th in moved]
    with open(os.path.join(ROOT, "outputs", "robgrade", "CTX_SCORE.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
