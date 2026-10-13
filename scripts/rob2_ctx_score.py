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


AMENDMENTS = os.path.join(ROOT, "outputs", "robgrade", "AMENDMENTS.json")


# The ONLY frozen files an amendment may change (codex A2 review): the code A2 fixes. The rule text, the inputs (split,
# comparators, the v3.1 objects and calibration), the tests and every other frozen file can never be amended this way.
AMENDABLE = ("robgrade/contextual.py", "scripts/rob2_contextual.py", "scripts/rob2_ctx_score.py", "scripts/rob2_dual.py",
             "robgrade/rob2_tab.py")                    # A3 (candidate 4): the served label of a closed decision
VARIANT = None                                         # a PRE-REGISTERED variant being scored (parse_args), else None
VARIANT_DOC = "outputs/robgrade/CONTEXTUAL_VARIANT_{}.md"
# the per-declaration supersession test (A3): A2 proved its records defect-caused; A3 proves the amended RULE shows the
# adjudicator different readings. A declaration without the field is A2's.
SUPERSESSION_TESTS = ("defect_caused", "rule_changed")


def supersession_test(entry):
    t = entry.get("superseded_test", "defect_caused")
    if t not in SUPERSESSION_TESTS:
        raise SystemExit(f"REFUSED: {entry.get('id')}: unknown supersession test {t!r}")
    return t


def parse_args(argv):
    """(base pre-registration sha, variant name or None, variant pre-registration sha or None)."""
    if len(argv) == 1:
        return argv[0], None, None
    if len(argv) == 4 and argv[1] == "--variant" and argv[2] in cx.VARIANTS:
        return argv[0], argv[2], argv[3]
    raise SystemExit("REFUSED: usage: rob2_ctx_score.py <pre-registration sha> [--variant <registered name> "
                     "<the variant's pre-registration sha>]; no subset: all four registered comparators are scored")


def check_variant_manifest(vruns, base_runs):
    """A variant's manifest only ADDS entries (codex A3 r16): an entry for a reader may not stand in for a base reader
    of the same prompt -- the base's fresh records are read, never replaced or omitted."""
    for key, r in vruns.items():
        bp = list((base_runs.get(key) or {}).get("passes") or [])
        for k, p in enumerate(r.get("passes") or []):
            b = bp[k] if k < len(bp) else {}
            for w, x in p.items():
                # (codex/agy A3 r17) in ANY role (readers and the adjudicator) and whatever its id or state: an entry
                # for a prompt the base already answered would shadow the base's record
                if w in b and (b.get(w) or {}).get("prompt_sha256") == (x or {}).get("prompt_sha256"):
                    raise SystemExit(f"REFUSED: {key} pass {k}: the variant shadows the base {w} entry of the same prompt")


def check_variant_prereg(name, sha):
    """A variant is scored only from the commit that ADDED its pre-registration document, an ancestor of HEAD, with
    every frozen file unchanged since (in history and in the working tree)."""
    full = _git("rev-parse", sha).stdout.strip()
    doc = VARIANT_DOC.format(name)
    added = [x for x in _git("log", "--diff-filter=A", "--format=%H", "--", doc).stdout.split() if x]
    if not full or not added or full != added[-1]:
        raise SystemExit(f"REFUSED: {sha} is not the commit that added {doc}")
    if _git("merge-base", "--is-ancestor", full, "HEAD").returncode != 0:
        raise SystemExit(f"REFUSED: {sha} is not an ancestor of HEAD")
    files = POLICY_FILES + INPUT_FILES + [doc]
    changed = [f for f in files if _git("diff", "--quiet", full, "--", f).returncode != 0]
    if changed:
        raise SystemExit(f"REFUSED: files changed since the variant {name} was registered at {sha}: {changed}")
    return full
SIGNER = "Mahmood"


AMENDMENTS_REL = "outputs/robgrade/AMENDMENTS.json"


def _signed_amendments(sha):
    """The amendment entries against this pre-registration SIGNED BY MAHMOOD, read from the COMMITTED history (HEAD),
    never from the editable working tree (codex A2 review, round 9): an amendment exists only once it has passed the
    hook into a commit."""
    out = _git("show", f"HEAD:{AMENDMENTS_REL}")
    if out.returncode != 0:
        return []
    return [a for a in json.loads(out.stdout)["amendments"]
            if a.get("prereg") == sha and (a.get("signed") or {}).get("by") == SIGNER]


def declared(sha, f):
    """(amendment A2, signed 13 Oct) An AMENDABLE frozen file may differ from the pre-registration ONLY by a declared
    amendment signed by Mahmood naming it, the pre-registration, its git blob there and its git blob now, AND the sha256
    of exactly the reviewed change (the file's git diff from the pre-registration; codex A2 review, round 8). Residual,
    stated: a signature here is a record in the repository, not a cryptographic one."""
    import hashlib
    if f not in AMENDABLE:
        return False
    if _git("diff", "--quiet", "HEAD", "--", f).returncode != 0:     # the file in use IS the committed one (round 9)
        return False
    old = _git("rev-parse", f"{sha}:{f}").stdout.strip()
    cur = _git("rev-parse", f"HEAD:{f}").stdout.strip()
    patch = hashlib.sha256(_git("diff", sha, "HEAD", "--", f).stdout.encode("utf-8")).hexdigest()
    return any(a.get("file") == f and a.get("from_blob") == old and a.get("to_blob") == cur
               and a.get("patch_sha256") == patch for a in _signed_amendments(sha))


def _legacy_strict(text):
    """The pre-A2 pipeline parser (scripts/rob2_dual.parse before A2): strict JSON, optionally in one code fence."""
    import re
    t = (text or "").strip()
    m = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", t, re.S)
    try:
        d = json.loads(m.group(1) if m else t)
    except ValueError:
        return None
    return d if isinstance(d, dict) and isinstance(d.get("answers"), list) else None


UNREAD = {"answer": "NI", "rationale": None}           # what the old pipeline's verify(None) gave an unread reader


def defect_caused(rid, load, held_ids):
    """(codex A2 review, round 8) True only when this adjudication was CAUSED by the parser defect: its recorded
    prompt shows one reader as the unread signature on EVERY question it decided, and that reader's held record for
    the same trial and outcome is unreadable to the old strict parser yet readable to the A2 parser."""
    rec = load(rid)
    reg = registered(rec, "adjudicator") if rec else None
    if not reg or not reg[1]:
        return False
    targets, readings = reg
    for slot, role in (("reader 1", "codex"), ("reader 2", "agy")):
        if not all((readings.get(q) or {}).get(slot) == UNREAD for q in targets):
            continue
        h = _pass_reader(rec, targets, role, load, held_ids)
        if h is None:
            continue
        for h in (h,):
            if _legacy_strict(h["reply"]) is not None or cx.parse_reply(h["reply"]) is None:
                continue
            # ... and under A2 that reader really SAID something on these questions (codex A2 r9): a reader that gave
            # no answer is unread under both parsers, so its adjudication was genuine, not the defect's
            # (codex A2 r10) compared by ANSWER: the defect turned a verified PY/PN into the unread NI; a reply whose
            # verified answer is NI anyway (explicit, or failing verification) was NI under both parsers
            # judged under A2's rule (codex A3 r16): A3's later unseen-source check cannot unmake a defect proof
            now = cx.verify(cx.parse_reply(h["reply"]), _sources(h), targets, check_unseen=False)
            if any(now[q]["answer"] != "NI" for q in targets):
                return True
    return False


def _pass_reader(rec, targets, role, load, held_ids):
    """The held reader record of `role` that this adjudication's pass showed it, or None: the UNIQUE held RAN_OK call of
    that role about the same trial and outcome, whose registered targets cover the adjudicated ones, made before the
    adjudication, on the same evidence block (codex A2 rounds 9, 10, 13 -- two candidates leave it unproven)."""
    import re
    import rob2_contextual as rc
    t = rec["prompt_text"]
    evidence = t[t.index(rc.EVIDENCE_MARK):]
    trial = re.search(r"^TRIAL: (\S+)", t, re.M).group(1)
    outcome = re.search(r"^OUTCOME: (.*)$", t, re.M).group(1)
    cands = []
    for hid in held_ids:
        h = load(hid)
        if not (h and h["caller"]["line"] == f"call:{role}" and h["state"] == "RAN_OK" and _bound_to(h, trial, outcome)):
            continue
        reg_h = registered(h, "reader")
        if not reg_h or not set(targets) <= set(reg_h[0]):
            continue
        if _utc(h["request_utc"]) >= _utc(rec["request_utc"]):
            continue
        ht = h["prompt_text"]
        if rc.EVIDENCE_MARK not in ht or ht[ht.index(rc.EVIDENCE_MARK):] != evidence:
            continue
        cands.append(h)
    return cands[0] if len(cands) == 1 else None


def rule_changed(rid, load, held_ids):
    """(A3) True only when the AMENDED rule would show this adjudication different readings: its pass's two unique
    reader records, re-verified under the rule in force (and the variant being scored), disagree on a different set of
    questions or with different readings from those its prompt shows. A genuine adjudication -- the same readings under
    the amended rule -- is never superseded."""
    rec = load(rid)
    reg = registered(rec, "adjudicator") if rec else None
    if not reg or not reg[1]:
        return False
    targets, shown = reg
    h1 = _pass_reader(rec, targets, "codex", load, held_ids)
    h2 = _pass_reader(rec, targets, "agy", load, held_ids)
    if h1 is None or h2 is None:
        return False
    rt = registered(h1, "reader")[0]
    if registered(h2, "reader")[0] != rt:
        return False
    v1 = cx.verify(cx.parse_reply(h1["reply"]), _sources(h1), rt, variant=VARIANT)
    v2 = cx.verify(cx.parse_reply(h2["reply"]), _sources(h2), rt, variant=VARIANT)
    now = {q: {"reader 1": v1[q], "reader 2": v2[q]} for q in rt if v1[q]["answer"] != v2[q]["answer"]}
    return now != shown


def check_superseded(superseded, held, roles, times, amended_iso, defect=None):
    """(codex A2 review) A superseded record must be HELD, RAN_OK, an ADJUDICATOR record, made BEFORE the amendment was
    applied, and (round 8) PROVEN caused by the parser defect (`defect`): supersession can never exempt a reader, a
    missing id, a later decision, or a genuine adjudication."""
    for rid in sorted(superseded):
        if defect is not None and rid in held and not defect(rid):
            raise SystemExit(f"REFUSED: superseded record {rid} is not shown to be caused by the parser defect")
        if rid not in held:
            raise SystemExit(f"REFUSED: superseded record {rid} is not held")
        if held[rid] != "RAN_OK" or roles.get(rid) != "adjudicator":
            raise SystemExit(f"REFUSED: superseded record {rid} is not a RAN_OK adjudicator record")
        if _utc(times[rid]) >= _utc(amended_iso):
            raise SystemExit(f"REFUSED: superseded record {rid} was made after the amendment was applied")


def superseded_records(sha):
    """(A2) Records made under a defect and SUPERSEDED by a signed amendment: kept, listed, never read."""
    return {rid for a in _signed_amendments(sha) for rid in a.get("superseded_records") or []}


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
    changed = [f for f in POLICY_FILES + INPUT_FILES if _git("diff", "--quiet", sha, "--", f).returncode != 0
               and not declared(full, f)]
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
    p = next((x for x in (os.path.join(d, rid + ".json") for d in _rec_dirs()) if os.path.exists(x)), None)
    if p is None:
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
    return [{"id": s["id"], "kind": s.get("kind"), "nct": s.get("nct"), "text": s.get("text") or s.get("abstract") or "",
             "sha256": sha.get(s["id"]), "open_for_prompt": True} for s in block["sources"]]   # kind: A3


def _rec_dirs():
    """The record stores read: a variant's own, then the base's (its reused readers); the base alone otherwise."""
    return ([REC_DIR + f"_{VARIANT}"] if VARIANT else []) + [REC_DIR]


def _bound_to(rec, trial, outcome):
    """The TRIAL and OUTCOME a recorded prompt was about (codex round 2: a record is bound to its assessment)."""
    import re
    t = re.search(r"^TRIAL: (\S+)", rec["prompt_text"], re.M)
    o = re.search(r"^OUTCOME: (.*)$", rec["prompt_text"], re.M)
    return (t.group(1) if t else None) == str(trial) and (o.group(1).strip() if o else None) == str(outcome).strip()


def _verified(rec, qid):
    """The recorded reply put through the SAME verify() as the pipeline (codex round 2): an empty quote, a generic or
    unreferenced rationale, a quote not in the shown source -- all NI here as there (under the variant being scored)."""
    return cx.verify(cx.parse_reply(rec["reply"]), _sources(rec), [qid], variant=VARIANT)[qid]   # A2: THE parser


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


def check_consumed(consumed, held, superseded=frozenset()):
    """(codex round 6) Every held post-registration RAN_OK record must have been READ by the replay: a decision record
    parked where the replay never reads it (e.g. an unexecuted pass) would be an omission. A RAN_ERROR record is a
    failed attempt (a retry) and carries no decision: it is accounted for, never refused.
    (A2) A record SUPERSEDED by a signed amendment is accounted for too -- kept and listed -- but it must NOT be read."""
    read_superseded = sorted(set(consumed) & set(superseded))
    if read_superseded:
        raise SystemExit(f"REFUSED: superseded records were read by the replay: {read_superseded}")
    unread = sorted(rid for rid, state in held.items()
                    if state == "RAN_OK" and rid not in set(consumed) and rid not in set(superseded))
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
    base_runs = None
    if rc.VARIANT is not None:                         # a variant overlays the base manifest (codex A3 r16)
        base_runs = json.load(open(rc.BASE_RUNS, encoding="utf-8")) if os.path.exists(rc.BASE_RUNS) else {}
        check_variant_manifest(runs, base_runs)
    docs = {s: json.load(open(os.path.join(cal.OURS, f"{s}.json"), encoding="utf-8")) for s in slugs}
    rd.prefetch_registry([(s, sorted(docs[s]["trials"])) for s in slugs])
    out, consumed = {}, []
    for s in slugs:
        items = {it["pmid"]: it for it in rd.items(s, sorted(docs[s]["trials"]))}
        out[s] = {}
        for pmid, o in docs[s]["trials"].items():
            new, r, _ = rc.process(items[pmid], o, runs, False, {}, base_runs)
            rd.redact_closed_spans(new, items[pmid])
            out[s][pmid] = new
            consumed += r.get("consumed") or []
    return out, runs, consumed


def _held(rec_dir, after):
    """{rid: state}, {rid: role}, {rid: request time} of the records in `rec_dir` made after `after`; and the ids made
    at or before it."""
    held, roles, times, early = {}, {}, {}, []
    for f in __import__("glob").glob(os.path.join(rec_dir, "mc-*.json")):
        rid = os.path.basename(f)[:-5]
        rec = load_record(rid)
        if _utc(rec["request_utc"]) > _utc(after):
            held[rid], roles[rid], times[rid] = rec["state"], rec["caller"]["line"].split(":")[-1], rec["request_utc"]
        else:
            early.append(rid)
    return held, roles, times, early


def _checked_objects(ctx_dir, regen, after):
    """Every scored object is what the pipeline reproduces and every contextual answer stands on its records."""
    counts = collections.Counter()
    for s in TOPICS:
        base = json.load(open(os.path.join(cal.OURS, f"{s}.json"), encoding="utf-8"))
        ctx = json.load(open(os.path.join(ctx_dir, f"{s}.json"), encoding="utf-8"))
        check_replay(s, ctx, regen[s])
        counts += check_contextual_doc(s, base, ctx, after)
    return counts


def main(argv):
    global VARIANT
    import rob2_contextual as rc
    base_sha, variant, vsha = parse_args(argv)
    sha = check_prereg(base_sha)
    after = prereg_time(sha)
    vfull = check_variant_prereg(variant, vsha) if variant else None
    test = set(json.load(open(os.path.join(ROOT, "outputs", "robgrade", "split.json"), encoding="utf-8"))["test"])
    amendments = sorted({a.get("id") for a in _signed_amendments(sha)})
    # ---- the base (the rule as amended by every signed declaration): always replayed and checked in full
    VARIANT = None
    rc.configure(None)
    regen, runs, consumed = replay_all(TOPICS)
    held, roles, times, _ = _held(REC_DIR, after)
    superseded = set()                                 # kept, listed, never read -- each by its declaration's own test
    for a in _signed_amendments(sha):
        recs = set(a.get("superseded_records") or [])
        if not recs:
            continue
        if not a.get("applied_utc"):
            raise SystemExit(f"REFUSED: {a.get('id')}: superseded records are declared without the amendment's applied_utc")
        fn = defect_caused if supersession_test(a) == "defect_caused" else rule_changed
        check_superseded(recs, held, roles, times, a["applied_utc"],
                         defect=lambda rid, fn=fn: fn(rid, load_record, list(held)))
        superseded |= recs
    failed_attempts = check_consumed(consumed, held, superseded)    # every other post-registration decision record was READ
    check_consumed_times(consumed, after)               # and everything READ postdates the pre-registration
    counts = _checked_objects(CTX_DIR, regen, after)
    pairs, excluded, unmatched, tools = pairs_from(CTX_DIR, TOPICS, test)
    t = nip.two_way(pairs)
    f = lambda c: f"{c['agree']} / {c['N']}"
    if variant is None:
        t31 = nip.two_way(json.load(open(V31, encoding="utf-8"))["pairs"])
        b = {(p["slug"], p["pmid"], p["domain"]): p for p in json.load(open(V31, encoding="utf-8"))["pairs"]}
        moved = [[p["slug"], p["pmid"], p["domain"], b[k]["ours"], p["ours"], p["theirs"]] for p in pairs
                 for k in [(p["slug"], p["pmid"], p["domain"])] if k in b and b[k]["ours"] != p["ours"]]
        res = {"preregistration_commit": sha, "amendments": amendments, "topics": TOPICS, "tools": tools,
               "two_way": t, "two_way_v31": t31,
               "contextual_answers_by_question": dict(sorted(counts.items())), "moved_from_v31": moved,
               "excluded": len(excluded), "unmatched_trials": len(unmatched), "result_identity": DISCLOSURE,
               "failed_attempts_accounted": failed_attempts, "records_consumed": len(set(consumed)),
               "superseded_records": sorted(superseded)}
        out_json, out_md = "ctx_score.json", "CTX_SCORE.md"
        title = "# Contextual 'probably' answers on TEST: agreement with the published per-trial judgements, n of N"
        rule_line = (f"Pre-registered rule: commit {sha} (outputs/robgrade/CONTEXTUAL_POLICY.md), as amended by the signed "
                     f"declarations {', '.join(amendments) or 'none'} (outputs/robgrade/AMENDMENTS.json). Only asked NI "
                     "answers could change, only to a documented contextual PY/PN (checked against v3.1, answer by answer).")
        heads, other, against = ("contextual", "v3.1"), t31, "v3.1"
        n_ctx = counts
    else:
        # ---- the PRE-REGISTERED variant, scored separately, beside the base just checked
        VARIANT = variant
        rc.configure(variant)
        try:
            vregen, _, vconsumed = replay_all(TOPICS)
            vafter = prereg_time(vfull)
            vheld, _, _, vearly = _held(REC_DIR + f"_{variant}", vafter)
            if vearly:
                raise SystemExit(f"REFUSED: variant records made before the variant was registered: {sorted(vearly)}")
            vfailed = check_consumed(vconsumed, vheld)     # every variant record was READ by the variant replay
            check_consumed_times(vconsumed, after)
            for rid in set(vconsumed) - set(vheld):    # a reused BASE record: held, RAN_OK, never superseded
                if rid in superseded or held.get(rid) != "RAN_OK":
                    raise SystemExit(f"REFUSED: the variant read {rid}, which is not a held, unsuperseded base record")
            vctx = CTX_DIR + f"_{variant}"
            n_ctx = _checked_objects(vctx, vregen, after)
            vpairs, vexcluded, vunmatched, vtools = pairs_from(vctx, TOPICS, test)
        finally:
            VARIANT = None
            rc.configure(None)
        tv = nip.two_way(vpairs)
        b = {(p["slug"], p["pmid"], p["domain"]): p for p in pairs}
        moved = [[p["slug"], p["pmid"], p["domain"], b[k]["ours"], p["ours"], p["theirs"]] for p in vpairs
                 for k in [(p["slug"], p["pmid"], p["domain"])] if k in b and b[k]["ours"] != p["ours"]]
        res = {"preregistration_commit": sha, "amendments": amendments, "variant": variant,
               "variant_preregistration_commit": vfull, "topics": TOPICS, "tools": vtools,
               "two_way": tv, "two_way_base": t, "contextual_answers_by_question": dict(sorted(n_ctx.items())),
               "contextual_answers_by_question_base": dict(sorted(counts.items())), "moved_from_base": moved,
               "excluded": len(vexcluded), "unmatched_trials": len(vunmatched), "result_identity": DISCLOSURE,
               "failed_attempts_accounted": vfailed, "records_consumed": len(set(vconsumed)),
               "variant_records": sorted(vheld)}
        out_json, out_md = f"ctx_score_{variant}.json", f"CTX_SCORE_{variant}.md"
        title = (f"# Pre-registered variant {variant} on TEST: agreement with the published per-trial judgements, n of N")
        rule_line = (f"Variant pre-registered at commit {vfull} (outputs/robgrade/CONTEXTUAL_VARIANT_{variant}.md), "
                     f"scored separately beside the base: the rule pre-registered at {sha} as amended by "
                     f"{', '.join(amendments) or 'none'}. The variant is never the default.")
        heads, other, against = (variant, "base"), t, "the base"
        t, excluded, unmatched = tv, vexcluded, vunmatched
    with open(os.path.join(ROOT, "outputs", "robgrade", out_json), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1)
    lines = [title, "", rule_line, "",
             f"Coverage: {len(excluded)} records excluded, {len(unmatched)} trials unmatched (not in any N).", "",
             DISCLOSURE, "",
             f"| domain | all ({heads[0]}) | excl. NI-driven ({heads[0]}) | NI-driven only ({heads[0]}) | all ({heads[1]}) | "
             f"excl. NI-driven ({heads[1]}) | NI-driven only ({heads[1]}) |", "|---|---|---|---|---|---|---|"]
    for d in nip.DOMS + ("all",):
        lines.append(f"| {d} | {f(t['all'][d])} | {f(t['excluding_ni_driven'][d])} | {f(t['ni_driven_only'][d])} | "
                     f"{f(other['all'][d])} | {f(other['excluding_ni_driven'][d])} | {f(other['ni_driven_only'][d])} |")
    lines += ["", "Contextual answers by question: " + (", ".join(f"{q}: {n}" for q, n in sorted(n_ctx.items())) or "none"),
              "", f"Judgements moved from {against}: {len(moved)}"]
    lines += [f"- {a} {b_} {c}: {o} -> {n} (comparator {th})" for a, b_, c, o, n, th in moved]
    with open(os.path.join(ROOT, "outputs", "robgrade", out_md), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
