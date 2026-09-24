"""Pilot of model-call-as-source on two populations. Nothing it writes can admit anything.

  screening  the screened-in records of every committed review page (the denominator scripts/arm_object_sweep.py
             reports as included_refused_by_arm_object.N, read here through that script's own record lookup). The
             model reads each record's held text against the topic's registered question and returns, per axis
             (population, intervention, comparator, design), MET / NOT_MET / NOT_STATED with a verbatim quote. The
             overall decision is DERIVED by reproducible_ai.model_source.verify_screening, never taken from the model.
  estimand   every estimand field the bundle's regex leaves without a statement (state != STATED_IN_OWNING_EVIDENCE)
             on every served BUNDLE.json. The model reads the row's PARSED_SOURCE and returns a value from the rule's
             own vocabulary, or NOT_STATED, with the sentence it read it from.

  python scripts/model_source_pilot.py freeze <task> --base SHA   freeze the population ONCE (registry/model_proposals/
                                                                 <task>.population.json); afterwards it never shrinks
  python scripts/model_source_pilot.py items  <task>              the item list, each with its held-text digest
  python scripts/model_source_pilot.py run    <task> [--limit K]  make the calls that have no RAN_OK record (live;
                                                                 one call at a time; each call -> registry/model_calls/)
  python scripts/model_source_pilot.py queue  <task>              replay every record, verify, write the queue
                                                                 registry/model_proposals/<task>.json (keeps any
                                                                 countersignature already there; never adds one)
  python scripts/model_source_pilot.py status <task>              n of N by state, from the queue as re-gated now

Every item of the denominator appears in the queue with a state: PROPOSED (a claim exists), or NO_HELD_TEXT /
RAN_ERROR / RESPONSE_NOT_A_CLAIM / NOT_YET_CALLED. The denominator is never shrunk by a failure.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproducible_ai import model_source as ms  # noqa: E402

MODEL = "gpt-6-astra"
EFFORT = "medium"
BATCH = {"screening": 6, "estimand": 3}
REC_DIR = ROOT / ms.RECORD_DIR
Q_DIR = ROOT / ms.PROPOSAL_DIR


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _load_script(name):
    spec = importlib.util.spec_from_file_location(f"_mh_{name}", ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _file_digest(rel: str) -> dict:
    return {"ref": rel, "sha256": _sha((ROOT / rel).read_bytes()), "what": "raw bytes of the committed file"}


# ------------------------------------------------------------------------------------------------------ items
def held_text_screening(rec: dict) -> str:
    """The held text a screening proposal must quote from: fixed fields of the committed cache record, in a fixed order."""
    if rec.get("id_type") == "nct":
        keys = (("TITLE", "title"), ("ACRONYM", "acronym"), ("STUDY TYPE", "study_type"), ("ALLOCATION", "allocation"),
                ("MASKING", "masking"), ("CONDITIONS", "conditions"), ("INTERVENTIONS", "interventions"), ("SUMMARY", "abstract"))
    else:
        keys = (("TITLE", "title"), ("PUBLICATION TYPES", "pubtypes"), ("ABSTRACT", "abstract"))
    return "\n".join(f"{label}: {rec.get(k) if rec.get(k) not in (None, '') else '(none)'}" for label, k in keys)


def criteria(slug: str) -> tuple[str, list[dict]]:
    cfg = json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))
    pico = {t["id"]: t for t in json.loads((ROOT / "pico.json").read_text(encoding="utf-8"))["topics"]}.get(slug) or {}
    lines = [f"Review: {cfg.get('title')}", f"Question: {cfg.get('question')}",
             f"Eligibility (registered): {cfg.get('eligibility_summary')}"]
    for k, lab in (("P", "Population"), ("I", "Intervention"), ("C", "Comparator")):
        if pico.get(k):
            lines.append(f"{lab} (pico.json): {pico[k]}")
    digests = [_file_digest(f"topics/{slug}.json")] + ([_file_digest("pico.json")] if pico else [])
    return "\n".join(lines), digests


def candidates_screening() -> list[dict]:
    """EVERY screened record on every committed page (any decision): the superset the population is selected from."""
    sweep = _load_script("arm_object_sweep")
    out = []
    for cfg in sorted((ROOT / "topics").glob("*.json")):
        slug = cfg.stem
        rev_p = ROOT / "docs" / "reviews" / slug / "review.json"
        if not rev_p.exists():
            continue
        review = json.loads(rev_p.read_text(encoding="utf-8"))
        recs = sweep._records(slug)
        for row in sweep._screened_records(review):
            rec = recs.get(sweep._norm(row.get("id")))
            item = {"task": "screening", "slug": slug, "item_id": f"{slug}::{row.get('id_type')}:{row.get('id')}",
                    "rule_decision": row.get("decision"), "rule_id": row.get("rule_id"), "rule_reason": row.get("reason"),
                    "held_ref": f"cache/{slug}/records.json#{row.get('id_type')}:{row.get('id')}"}
            if rec is None:
                item["state"] = "NO_HELD_TEXT"
            else:
                t = held_text_screening(rec)
                item.update(held_text=t, held_sha256=_sha(t.encode("utf-8")))
            out.append(item)
    return sorted(out, key=lambda i: i["item_id"])


def candidates_estimand() -> list[dict]:
    """EVERY estimand field the bundle's rule reads, on every served bundle, whatever its state: the superset."""
    out = []
    for bpath in sorted((ROOT / "docs" / "reviews").glob("*/BUNDLE.json")):
        slug = bpath.parent.name
        bundle = json.loads(bpath.read_text(encoding="utf-8"))
        records = {str(r.get("id")): r for r in json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8"))["records"]}
        for row in bundle.get("verification_rows") or []:
            src = row.get("source") or {}
            for field, ev in sorted((row.get("estimand_evidence") or {}).items()):
                if not ms.estimand_vocabulary(field):
                    continue
                sel = ((src.get("selector") or {}).get("selected_identifier") or {}).get("id")
                item = {"task": "estimand", "slug": slug, "field": field, "rule_state": ev.get("state"),
                        "rule_value": ev.get("value") or ev.get("values"),
                        "item_id": f"{slug}::{row['trial']['id']}::{field}",
                        "held_ref": f"{src.get('document_ref')} PARSED_SOURCE (abstract)",
                        "rule_decision": f"{ev.get('state')}: {ev.get('value') or ev.get('values')}"}
                rec = records.get(str(sel))
                text = (rec or {}).get("abstract")
                if not text:
                    item["state"] = "NO_HELD_TEXT"
                elif _sha(text.encode("utf-8")) != src.get("representation_sha256"):
                    item["state"] = "HELD_TEXT_DRIFT"   # the cache is not the bytes the bundle row names: fail closed
                else:
                    item.update(held_text=text, held_sha256=_sha(text.encode("utf-8")))
                out.append(item)
    return sorted(out, key=lambda i: i["item_id"])


CANDIDATES = {"screening": candidates_screening, "estimand": candidates_estimand}
# The selection rule that defines each pilot's population AT FREEZE TIME. After the freeze the population does not
# move: a later rule change (a regex that now reads a field, a record the screen now excludes) is recorded on the
# item as rule_decision_now, never by removing it -- a denominator that shrinks when the rule improves cannot show
# that the rule caught up.
SELECT = {"screening": lambda i: i["rule_decision"] == "include",
          "estimand": lambda i: i["rule_state"] != "STATED_IN_OWNING_EVIDENCE"}
SELECTION_RULE = {"screening": "screened records with decision == include on the committed review pages",
                  "estimand": "estimand fields whose bundle state != STATED_IN_OWNING_EVIDENCE on the served bundles"}
FROZEN_KEYS = ("item_id", "slug", "held_ref", "held_sha256", "state", "rule_decision", "rule_id", "field", "rule_state")


def population_path(task: str) -> Path:
    return Q_DIR / f"{task}.population.json"


def _current_selection(task: str) -> list[dict]:
    return sorted((i for i in CANDIDATES[task]() if SELECT[task](i)), key=lambda i: i["item_id"])


def pilot_items(task: str) -> list[dict]:
    """The pilot's items: the FROZEN population when one is committed (held text re-read and re-digested now; a
    changed digest is HELD_TEXT_DRIFT, a vanished candidate is LEFT_THE_TREE), else the current selection."""
    p = population_path(task)
    if not p.exists():
        return _current_selection(task)
    frozen = json.loads(p.read_text(encoding="utf-8"))
    now = {i["item_id"]: i for i in CANDIDATES[task]()}
    out = []
    for f in frozen["items"]:
        cur = now.get(f["item_id"])
        it = {k: v for k, v in f.items()}
        it["task"] = task
        it["rule_decision_at_freeze"] = f.get("rule_decision")
        if cur is None:
            it["state"] = "LEFT_THE_TREE"
            out.append(it)
            continue
        it["rule_decision"] = cur.get("rule_decision")          # what the rule says NOW (rendered beside the freeze)
        for k in ("rule_id", "rule_reason", "rule_state", "rule_value"):
            if k in cur:
                it[k] = cur[k]
        if "held_text" in cur and "held_sha256" in f:
            if cur["held_sha256"] == f["held_sha256"]:
                it["held_text"] = cur["held_text"]
                it.pop("state", None)
            else:
                it["state"] = "HELD_TEXT_DRIFT"
        out.append(it)
    return out


TASKS = ("estimand", "screening")


def cmd_freeze(task: str, base: str):
    p = population_path(task)
    if p.exists():
        sys.exit(f"refused: {p.name} exists; a population is frozen once (a new pilot is a new task name)")
    sel = _current_selection(task)
    doc = {"task": task, "selection_rule": SELECTION_RULE[task], "frozen_from_commit": base, "N": len(sel),
           "note": "Frozen pilot population. Held text is NOT copied (it is re-read from the tree and must match "
                   "held_sha256); the rule's later decisions are recorded per item, never by dropping one.",
           "items": [{k: i[k] for k in FROZEN_KEYS if k in i} for i in sel]}
    Q_DIR.mkdir(parents=True, exist_ok=True)
    p.write_bytes((json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii"))
    print(f"froze {task}: N = {len(sel)} from {base}")


def population_drift(task: str) -> dict:
    """What the current selection rule would pick now vs the frozen population -- reported, never applied."""
    p = population_path(task)
    if not p.exists():
        return {}
    frozen = {i["item_id"] for i in json.loads(p.read_text(encoding="utf-8"))["items"]}
    now = {i["item_id"] for i in _current_selection(task)}
    return {"frozen_not_selected_now": sorted(frozen - now), "selected_now_not_frozen": sorted(now - frozen)}


# ------------------------------------------------------------------------------------------------------ prompts
SCREEN_INSTR = """You are checking whether each record below meets a systematic review's registered eligibility criteria.
Do not run any commands or read any files. Use only the text given here.

For EACH record and EACH axis (population, intervention, comparator, design) answer:
  MET        the record's text states that this criterion is satisfied,
  NOT_MET    the record's text states something that violates this criterion,
  NOT_STATED the record's text does not say enough to decide.
For MET and NOT_MET you MUST give "quote": a short passage copied EXACTLY, character for character, from that record's
text (no ellipses, no paraphrase, no changed punctuation) that shows it. For NOT_STATED give "quote": null.
design = a randomised controlled trial of the kind the question asks for (e.g. placebo-controlled where it says so).
Answer every record, using its "item" key exactly. Return only the JSON object.
"""

ESTIMAND_INSTR = """You are reading trial abstracts to find how the primary analysis was defined. Do not run any commands
or read any files. Use only the text given here.

For EACH item you are given one FIELD. Answer with "value" chosen from the allowed values for that field, or
"NOT_STATED" if the abstract does not say. For any value other than NOT_STATED you MUST give "quote": one sentence
copied EXACTLY, character for character, from that item's abstract that states it; for NOT_STATED give "quote": null.
Do not infer from what is usual for such trials: only what this abstract says.
Allowed values:
{vocab}
Answer every item, using its "item" key and its field exactly. Return only the JSON object.
"""


def _schema(task: str) -> dict:
    if task == "screening":
        axis = {"type": "object", "additionalProperties": False, "required": ["verdict", "quote"],
                "properties": {"verdict": {"type": "string", "enum": list(ms.SCREEN_VERDICTS)},
                               "quote": {"type": ["string", "null"]}}}
        props = {"item": {"type": "string"},
                 "axes": {"type": "object", "additionalProperties": False, "required": list(ms.SCREEN_AXES),
                          "properties": {a: axis for a in ms.SCREEN_AXES}}}
    else:
        fields = ["analysis_set", "analysis_window"]
        vals = sorted({v for f in fields for v in ms.estimand_vocabulary(f)} | {"NOT_STATED"})
        props = {"item": {"type": "string"}, "field": {"type": "string", "enum": fields},
                 "value": {"type": "string", "enum": vals}, "quote": {"type": ["string", "null"]}}
    it = {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}
    return {"type": "object", "additionalProperties": False, "required": ["items"],
            "properties": {"items": {"type": "array", "items": it}}}


def batches(task: str, items: list[dict]) -> list[dict]:
    """Deterministic batching: callable items in item_id order, grouped by slug, chunked. Each batch -> exact prompt bytes."""
    callable_items = [i for i in items if "held_text" in i]
    by_slug: dict[str, list] = {}
    for i in callable_items:
        by_slug.setdefault(i["slug"], []).append(i)
    out = []
    for slug in sorted(by_slug):
        group = by_slug[slug]
        for k in range(0, len(group), BATCH[task]):
            chunk = group[k:k + BATCH[task]]
            keyed = [(f"R{n + 1}", i) for n, i in enumerate(chunk)]
            digests = [{"ref": i["held_ref"], "sha256": i["held_sha256"], "what": "held text quoted by the item"} for _, i in keyed]
            if task == "screening":
                crit, cd = criteria(slug)
                body = SCREEN_INSTR + "\n=== REGISTERED CRITERIA ===\n" + crit + "\n"
                for key, i in keyed:
                    body += f"\n=== RECORD item={key} ===\n{i['held_text']}\n"
                digests = cd + digests
            else:
                vocab = "\n".join(f"  {f}: {', '.join(ms.estimand_vocabulary(f))}" for f in ("analysis_set", "analysis_window"))
                body = ESTIMAND_INSTR.format(vocab=vocab)
                for key, i in keyed:
                    body += f"\n=== ITEM item={key} field={i['field']} ===\n{i['held_text']}\n"
            out.append({"slug": slug, "batch": f"{slug}#{k // BATCH[task] + 1}", "prompt": body.encode("utf-8"),
                        "keyed": keyed, "digests": digests})
    return out


STABILITY_PURPOSE = "stability re-ask of "


def _records_by_prompt() -> dict[str, list[dict]]:
    """Records grouped by prompt digest, each group in (request_utc, record_id) order -- never file-name order, which is
    a hash and would make 'which record is the source' arbitrary once a prompt has been asked twice."""
    out: dict[str, list[dict]] = {}
    for p in sorted(REC_DIR.glob("mc-*.json")):
        r = ms.load_record(p)
        out.setdefault(r["prompt"]["sha256"], []).append(r)
    for recs in out.values():
        recs.sort(key=lambda r: (r["request_utc"], r["record_id"]))
    return out


def source_record(recs: list[dict]) -> dict | None:
    """The record a proposal comes from: the EARLIEST RAN_OK call that is not a stability re-ask. A re-ask measures the
    model; it never replaces the answer that was proposed (and possibly signed). With no RAN_OK call, the latest error
    is returned so the item is listed as RAN_ERROR."""
    ordered = sorted(recs, key=lambda r: (r["request_utc"], r["record_id"]))
    ok = [r for r in ordered if r["state"] == "RAN_OK" and not str(r["caller"].get("purpose", "")).startswith(STABILITY_PURPOSE)]
    if ok:
        return ok[0]
    errs = [r for r in ordered if not str(r["caller"].get("purpose", "")).startswith(STABILITY_PURPOSE)]
    return errs[-1] if errs else None


# ------------------------------------------------------------------------------------------------------ commands
def cmd_items(task):
    items = pilot_items(task)
    states = {}
    for i in items:
        states[i.get("state", "CALLABLE")] = states.get(i.get("state", "CALLABLE"), 0) + 1
    print(json.dumps({"task": task, "N": len(items), "by_state": states,
                      "batches": len(batches(task, items))}, indent=1))


def cmd_run(task, limit):
    from reproducible_ai import model_call_live
    items = pilot_items(task)
    have = _records_by_prompt()
    todo = [b for b in batches(task, items)
            if (source_record(have.get(_sha(b["prompt"]), [])) or {}).get("state") != "RAN_OK"]
    print(f"{task}: {len(todo)} batches without a RAN_OK record; running {min(limit, len(todo))}", flush=True)
    for b in todo[:limit]:
        rec = model_call_live.call(b["prompt"], schema=_schema(task), model=MODEL, effort=EFFORT,
                                   caller={"file": "scripts/model_source_pilot.py", "line": "cmd_run",
                                           "purpose": f"{task} proposals, batch {b['batch']} ({len(b['keyed'])} items)"},
                                   input_digests=b["digests"])
        path = ms.write_record(rec, REC_DIR)
        print(f"{b['batch']}: {rec['state']} model={rec['model']['id_reported']} -> {path.name}"
              + (f" ERROR {rec.get('error','')[:200]}" if rec["state"] != "RAN_OK" else ""), flush=True)


def cmd_queue(task):
    items = pilot_items(task)
    have = _records_by_prompt()
    qpath = Q_DIR / f"{task}.json"
    old = {e["item_id"]: e for e in json.loads(qpath.read_text(encoding="utf-8"))["items"]} if qpath.exists() else {}
    entries = {i["item_id"]: {"item_id": i["item_id"], "task": task, "state": i["state"], "held_ref": i["held_ref"]}
               for i in items if "held_text" not in i}
    for b in batches(task, items):
        rec = source_record(have.get(_sha(b["prompt"]), []))
        for key, i in b["keyed"]:
            if rec is None:
                entries[i["item_id"]] = {"item_id": i["item_id"], "task": task, "state": "NOT_YET_CALLED"}
                continue
            if rec["state"] != "RAN_OK":
                entries[i["item_id"]] = {"item_id": i["item_id"], "task": task, "state": "RAN_ERROR", "record_id": rec["record_id"]}
                continue
            try:
                claim = ms.claim_for_item(ms.extract_claim(task, ms.replay(rec)), key)
            except (ValueError, ms.ReplayRefused) as exc:
                entries[i["item_id"]] = {"item_id": i["item_id"], "task": task, "state": "RESPONSE_NOT_A_CLAIM",
                                         "record_id": rec["record_id"], "why": str(exc)}
                continue
            ver = (ms.verify_screening(claim, i["held_text"], i["rule_decision"]) if task == "screening"
                   else ms.verify_estimand(claim, i["held_text"]))
            ctx = {k: i[k] for k in ("rule_id", "rule_reason", "field", "rule_state", "rule_value", "rule_decision_at_freeze") if k in i}
            e = ms.queue_entry(task=task, item_id=i["item_id"], record=rec, claim=claim, verification=ver,
                               held_ref=i["held_ref"], held_sha256=i["held_sha256"], rule_decision=i["rule_decision"],
                               context=ctx, response_item=key)
            prev = old.get(i["item_id"])
            if prev and prev.get("record_id") == rec["record_id"] and isinstance(prev.get("reviewer_countersignature"), dict):
                e["reviewer_countersignature"] = prev["reviewer_countersignature"]   # carried, never created
            e["rendered_sha256"] = __import__("harness.result_changes", fromlist=["x"]).rendered_sha256(ms.render_proposal_block(e, rec))
            entries[i["item_id"]] = e
    doc = {"task": task, "N": len(items), "N_name": ("screened-in records across committed review pages" if task == "screening"
                                                     else "estimand fields without a stated value across served bundles"),
           "note": "Every entry is PROPOSED or a non-call state. Nothing here is read by any producer. A signature is "
                   "written only by scripts/countersign_model_proposal.py sign, run by the reviewer.",
           "items": [entries[k] for k in sorted(entries)]}
    Q_DIR.mkdir(parents=True, exist_ok=True)
    qpath.write_bytes((json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii"))
    cmd_status(task)


def gated(task):
    """Re-gate every queued entry NOW from the committed record and the held text (never trusting the queue's verdict)."""
    items = {i["item_id"]: i for i in pilot_items(task)}
    doc = json.loads((Q_DIR / f"{task}.json").read_text(encoding="utf-8"))
    out = []
    for e in doc["items"]:
        if "record_id" not in e or "claim" not in e:
            out.append((e, e.get("state"), None))
            continue
        rec_p = REC_DIR / f"{e['record_id']}.json"
        rec = ms.load_record(rec_p) if rec_p.exists() else {}
        held = items.get(e["item_id"], {}).get("held_text")
        st = ms.status_of(e, rec, held) if held is not None else "PROPOSED"
        out.append((e, st, ms.gate_problems(e, rec, held) if held is not None else ["HELD_TEXT_GONE"]))
    return doc, out


def cmd_status(task):
    doc, rows = gated(task)
    from collections import Counter
    st, agree, ver = Counter(), Counter(), Counter()
    for e, s, _ in rows:
        st[s] += 1
        if "verification" in e:
            ver[e["verification"]["state"]] += 1
            agree[str(e["verification"].get("agreement", "-")).split("(")[0]] += 1
    N = doc["N"]
    print(f"{task}: N = {N} ({doc['N_name']}); queue entries {len(rows)} of {N}")
    for k, v in sorted(st.items()):
        print(f"  status {k}: {v} of {N}")
    for k, v in sorted(ver.items()):
        print(f"  verifier {k}: {v} of {sum(ver.values())} proposals")
    for k, v in sorted(agree.items()):
        print(f"  rule/model {k}: {v} of {sum(agree.values())} proposals")


# ------------------------------------------------------------------------------------------------------ stability
def stability_sample(task: str, k: int) -> list[dict]:
    """A deterministic sample of k batches: every (n // k)-th batch in batch order, starting at the first."""
    bs = batches(task, pilot_items(task))
    step = max(1, len(bs) // max(1, k))
    return bs[::step][:k]


def cmd_stability(task: str, k: int):
    """Re-ask the model the IDENTICAL prompt bytes for a deterministic sample of batches. Each re-ask is its own
    committed record (caller purpose 'stability re-ask of <source record id>'); none can become a proposal source."""
    from reproducible_ai import model_call_live
    have = _records_by_prompt()
    for b in stability_sample(task, k):
        recs = have.get(_sha(b["prompt"]), [])
        src = source_record(recs)
        if not src or src["state"] != "RAN_OK":
            print(f"{b['batch']}: no RAN_OK source record; not re-asked", flush=True)
            continue
        if any(str(r["caller"].get("purpose", "")).startswith(STABILITY_PURPOSE + src["record_id"]) and r["state"] == "RAN_OK"
               for r in recs):
            print(f"{b['batch']}: already re-asked", flush=True)
            continue
        rec = model_call_live.call(b["prompt"], schema=_schema(task), model=MODEL, effort=EFFORT,
                                   caller={"file": "scripts/model_source_pilot.py", "line": "cmd_stability",
                                           "purpose": f"{STABILITY_PURPOSE}{src['record_id']} ({task} batch {b['batch']})"},
                                   input_digests=b["digests"])
        path = ms.write_record(rec, REC_DIR)
        print(f"{b['batch']}: re-ask {rec['state']} -> {path.name}", flush=True)


def _claims(rec: dict, keyed: list) -> dict:
    out = {}
    obj = ms.extract_claim(None, ms.replay(rec))
    for key, i in keyed:
        try:
            out[i["item_id"]] = ms.claim_for_item(obj, key)
        except ValueError:
            out[i["item_id"]] = None
    return out


def stability_report(task: str) -> dict:
    """Source call vs its re-ask(s), item by item, from committed records only (no model call)."""
    have = _records_by_prompt()
    rows = []
    for b in batches(task, pilot_items(task)):
        recs = have.get(_sha(b["prompt"]), [])
        src = source_record(recs)
        again = [r for r in recs if r["state"] == "RAN_OK" and src
                 and str(r["caller"].get("purpose", "")).startswith(STABILITY_PURPOSE + src["record_id"])]
        if not src or src["state"] != "RAN_OK" or not again:
            continue
        a, c = _claims(src, b["keyed"]), _claims(again[0], b["keyed"])
        for key, i in b["keyed"]:
            x, y = a.get(i["item_id"]), c.get(i["item_id"])
            row = {"item_id": i["item_id"], "source_record": src["record_id"], "reask_record": again[0]["record_id"],
                   "identical_claim": x == y}
            if task == "screening" and x and y:
                vx = ms.verify_screening(x, i["held_text"], i["rule_decision"])
                vy = ms.verify_screening(y, i["held_text"], i["rule_decision"])
                row["same_derived_decision"] = vx.get("model_decision") == vy.get("model_decision")
                row["decisions"] = [vx.get("model_decision"), vy.get("model_decision")]
                row["axes_same_verdict"] = sum(1 for ax in ms.SCREEN_AXES
                                               if (x["axes"].get(ax) or {}).get("verdict") == (y["axes"].get(ax) or {}).get("verdict"))
            elif task == "estimand" and x and y:
                row["same_value"] = x.get("value") == y.get("value")
                row["values"] = [x.get("value"), y.get("value")]
            rows.append(row)
    n = len(rows)
    summary = {"task": task, "N": n, "N_name": "items whose batch has a source call AND a re-ask of the identical prompt bytes",
               "identical_claim": sum(r["identical_claim"] for r in rows)}
    if task == "screening":
        summary["same_derived_decision"] = sum(bool(r.get("same_derived_decision")) for r in rows)
        summary["axis_verdicts_same"] = sum(r.get("axes_same_verdict", 0) for r in rows)
        summary["axis_verdicts_N"] = 4 * n
    else:
        summary["same_value"] = sum(bool(r.get("same_value")) for r in rows)
    summary["what_this_measures"] = ("whether the MODEL reproduces its own answer to identical prompt bytes; the recorded "
                                     "call replays byte-identically regardless -- that is the only reproducibility claimed")
    return {"summary": summary, "rows": rows}


def cmd_stability_report(task: str):
    rep = stability_report(task)
    out = ROOT / "outputs" / "model_source" / f"STABILITY_{task}.json"
    out.write_bytes((json.dumps(rep, indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii"))
    print(json.dumps(rep["summary"], indent=1))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["items", "freeze", "run", "queue", "status", "stability", "stability-report"])
    ap.add_argument("--base", help="freeze: the commit the population is selected from")
    ap.add_argument("task", choices=TASKS)
    ap.add_argument("--limit", type=int, default=10 ** 6)
    ap.add_argument("--sample", type=int, default=10, help="stability: how many batches to re-ask")
    a = ap.parse_args(argv)
    {"items": lambda: cmd_items(a.task), "run": lambda: cmd_run(a.task, a.limit),
     "queue": lambda: cmd_queue(a.task), "status": lambda: cmd_status(a.task),
     "freeze": lambda: cmd_freeze(a.task, a.base or sys.exit("freeze needs --base <commit>")),
     "stability": lambda: cmd_stability(a.task, a.sample),
     "stability-report": lambda: cmd_stability_report(a.task)}[a.cmd]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
