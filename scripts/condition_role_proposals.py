"""CONDITION-AS-OUTCOME across the corpus: the regex first, a model only where the regex cannot decide (V1.0.1,
statins-older-adults review; harness/condition_role.py).

  python scripts/condition_role_proposals.py sweep    n of N: of every X2 exclusion of a registry record that rests
                                                       only on a REGISTERED CONDITION (the term is in its conditions,
                                                       not its title), how many are prevention targets. The population
                                                       is the served screening at the PRE-FIX commit (a pinned control,
                                                       never a live ref), so the fix cannot shrink its own denominator.
                                                       -> evidence/v101_integrated/condition_role_sweep.json
  python scripts/condition_role_proposals.py freeze   the items the regex cannot decide (CRITERIA_SILENT: the criteria
                                                       never mention the condition) with their held registry text
                                                       -> registry/model_proposals/condition_role.population.json
  python scripts/condition_role_proposals.py run      one recorded model call per batch (reproducible_ai.model_call_live)
  python scripts/condition_role_proposals.py queue    replay, verify (model_source.verify_condition_role), write the
                                                       queue registry/model_proposals/condition_role.json; every entry
                                                       is PROPOSED until countersigned, and nothing reads it into a build
  python scripts/condition_role_proposals.py status   n of N by state, re-gated now
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import condition_role as cr, lexicon, population_witness as pw, trial_family as tf  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

PRE_FIX = "1801d205"    # the served head before harness/condition_role.py existed (CI green, run 36435509699)
TASK = "condition_role"
MODEL, EFFORT, BATCH = "gpt-6-astra", "medium", 5
SWEEP = ROOT / "evidence" / "v101_integrated" / "condition_role_sweep.json"
POP = ROOT / ms.PROPOSAL_DIR / f"{TASK}.population.json"
QUEUE = ROOT / ms.PROPOSAL_DIR / f"{TASK}.json"
CODEX_LOG = Path("C:/mh-lanes/evid2-scratch/codex/codex_calls.jsonl")
X2 = re.compile(r"^wrong population: title/conditions mention '([^']+)'\.$")

INSTR = """You read ClinicalTrials.gov registry text. Each item names one REGISTERED CONDITION TERM. Decide, from the
registry text only, what that condition is for this trial:
  ENTRY_POPULATION   participants HAVE the condition when they enter (it is whom the trial enrols)
  PREVENTED_OUTCOME  participants do NOT have it at entry; it is something the trial measures, prevents or follows up
  NOT_STATED         the text does not say either way
For ENTRY_POPULATION or PREVENTED_OUTCOME give "quote": words copied EXACTLY from the item's text that show it, and
the quote must contain the condition term. For NOT_STATED give "quote": null. Answer every item.
"""


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _show(ref: str, path: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "show", f"{ref}:{path}"], stderr=subprocess.DEVNULL).decode("utf-8")


def _registry_view(slug, nct, reg, rec):
    pop = (reg.get(nct) or {}).get("population") or {}
    conds = (pop.get("conditions") or {}).get("value") or rec.get("conditions") or []
    crit = (pop.get("criteria") or {}).get("value")
    outs = [f"{o.get('outcome_type')}: {o.get('measure')}" for o in (reg.get(nct) or {}).get("design_outcomes") or []]
    held = "\n".join([f"TITLE: {rec.get('title') or '(none)'}", f"CONDITIONS: {'; '.join(map(str, conds)) or '(none)'}",
                      f"ELIGIBILITY CRITERIA: {crit or '(none)'}", "REGISTERED OUTCOMES: " + (" | ".join(outs) or "(none)")])
    return conds, crit, held


def sweep_items() -> list[dict]:
    out = []
    for cfgp in sorted((ROOT / "topics").glob("*.json")):
        slug = cfgp.stem
        try:
            review = json.loads(_show(PRE_FIX, f"docs/reviews/{slug}/review.json"))
        except subprocess.CalledProcessError:
            continue
        none = (json.loads(cfgp.read_text(encoding="utf-8")).get("include") or {}).get("population_none") or []
        reg = tf.load_registry(ROOT, slug)
        recs = {str(r.get("id")): r for r in json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8")).get("ctgov") or []}
        for d in review["screening"]["records"]:
            m = X2.match(d.get("reason") or "")
            if d.get("rule_id") != "X2" or not m or d.get("id_type") != "nct":
                continue
            nct, term = d["id"].split("·")[-1].strip(), m.group(1)
            rec = recs.get(nct) or {}
            conds, crit, held = _registry_view(slug, nct, reg, rec)
            if not any(not h[3] for c in conds for h in pw._hits(lexicon.fold(str(c)), [term])):
                continue                          # the term came from the title, not a registered condition
            if pw._hits(lexicon.fold(rec.get("title") or ""), [term]):
                continue
            if any(t["term"] == term for t in cr.prevention_targets(crit, conds, rec.get("title") or "", none)):
                cls = "PREVENTION_TARGET"
            elif not crit:
                cls = "NO_CRITERIA_HELD"
            else:
                inc, exc, _ = pw.split_criteria(crit)
                if any(not h[3] for i in inc for h in pw._hits(lexicon.fold(i), [term])):
                    cls = "INCLUSION_NAMES_IT"
                elif any(pw._hits(lexicon.fold(i), [term]) for i in exc):
                    cls = "EXCLUSION_NAMES_IT_QUALIFIED"
                else:
                    cls = "CRITERIA_SILENT"
            out.append({"slug": slug, "nct": nct, "term": term, "class": cls, "item_id": f"{slug}::{nct}::{term}",
                        "held_text": held, "held_sha256": _sha(held.encode("utf-8")),
                        "held_ref": f"cache/{slug}/family_registry.json#{nct} (title, conditions, criteria, outcomes)"})
    return out


def cmd_sweep():
    items = sweep_items()
    by = {}
    for i in items:
        by[i["class"]] = by.get(i["class"], 0) + 1
    doc = {"schema": "condition-role-sweep-v1", "population_commit": PRE_FIX,
           "N": len(items), "n_prevention_target": by.get("PREVENTION_TARGET", 0), "by_class": by,
           "definition": "every X2 exclusion of a registry record, on the served screening at the pre-fix commit, whose "
                         "matched term is in its registered conditions and not its title",
           "classes": {"PREVENTION_TARGET": "an exclusion criterion names the registered condition itself, unqualified, and "
                                            "no inclusion criterion names it: the X2 is withdrawn (harness/condition_role.py)",
                       "INCLUSION_NAMES_IT": "an inclusion criterion names it: the condition is the entry population; X2 stands",
                       "EXCLUSION_NAMES_IT_QUALIFIED": "an exclusion names it only qualified or incidentally: X2 stands",
                       "CRITERIA_SILENT": "the criteria never name it: the regex cannot decide; a recorded model proposal "
                                          "(registry/model_proposals/condition_role.json), inert until countersigned",
                       "NO_CRITERIA_HELD": "no criteria held: silence is not evidence; X2 stands"},
           "items": [{k: i[k] for k in ("slug", "nct", "term", "class")} for i in items]}
    SWEEP.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"n of N = {doc['n_prevention_target']} of {doc['N']}", by)


def cmd_freeze():
    if POP.exists():
        raise SystemExit(f"{POP} is frozen; a population never moves")
    items = [i for i in sweep_items() if i["class"] == "CRITERIA_SILENT"]
    POP.write_text(json.dumps({"task": TASK, "frozen_from": PRE_FIX, "selection": "sweep class CRITERIA_SILENT",
                               "items": items}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("froze", len(items))


def _batches():
    items = json.loads(POP.read_text(encoding="utf-8"))["items"]
    for k in range(0, len(items), BATCH):
        chunk = items[k:k + BATCH]
        keyed = [(f"R{j + 1}", i) for j, i in enumerate(chunk)]
        prompt = INSTR + "".join(f"\n=== REGISTRY item={key} condition_term={i['term']!r} ===\n{i['held_text']}\n"
                                 for key, i in keyed)
        yield {"batch": k // BATCH + 1, "keyed": keyed, "prompt": prompt.encode("utf-8"),
               "digests": [{"ref": i["held_ref"], "sha256": i["held_sha256"], "what": "held registry text"} for _, i in keyed]}


def _schema():
    it = {"type": "object", "additionalProperties": False, "required": ["item", "role", "quote"],
          "properties": {"item": {"type": "string"}, "role": {"type": "string", "enum": list(ms.CONDITION_ROLES)},
                         "quote": {"type": ["string", "null"]}}}
    return {"type": "object", "additionalProperties": False, "required": ["items"],
            "properties": {"items": {"type": "array", "items": it}}}


def _records():
    by = {}
    for p in (ROOT / ms.RECORD_DIR).glob("mc-*.json"):
        r = ms.load_record(p)
        by.setdefault(r["prompt"]["sha256"], []).append(r)
    return by


def cmd_run():
    from reproducible_ai import model_call_live
    have = _records()
    for b in _batches():
        if any(r["state"] == "RAN_OK" for r in have.get(_sha(b["prompt"]), [])):
            continue
        rec = model_call_live.call(b["prompt"], schema=_schema(), model=MODEL, effort=EFFORT,
                                   caller={"file": "scripts/condition_role_proposals.py", "lane": "evid2", "line": "cmd_run",
                                           "purpose": f"condition_role proposals, batch {b['batch']} ({len(b['keyed'])} items)"},
                                   input_digests=b["digests"])
        path = ms.write_record(rec, ROOT / ms.RECORD_DIR)
        CODEX_LOG.parent.mkdir(parents=True, exist_ok=True)
        with CODEX_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"lane": "evid2", "task": TASK, "batch": b["batch"], "record": path.name, "state": rec["state"],
                                "model_reported": rec["model"].get("id_reported"), "prompt_sha256": rec["prompt"]["sha256"]}) + "\n")
        print(b["batch"], rec["state"], rec["model"].get("id_reported"), path.name, flush=True)


def cmd_queue():
    have = _records()
    old = {e["item_id"]: e for e in json.loads(QUEUE.read_text(encoding="utf-8"))["items"]} if QUEUE.exists() else {}
    entries = []
    for b in _batches():
        rec = next((r for r in have.get(_sha(b["prompt"]), []) if r["state"] == "RAN_OK"), None)
        for key, i in b["keyed"]:
            if rec is None:
                entries.append({"item_id": i["item_id"], "task": TASK, "state": "NOT_YET_CALLED"})
                continue
            try:
                claim = ms.claim_for_item(ms.extract_claim(TASK, ms.replay(rec)), key)
            except ValueError as exc:
                entries.append({"item_id": i["item_id"], "task": TASK, "state": "RESPONSE_NOT_A_CLAIM", "why": str(exc)})
                continue
            v = ms.verify_condition_role(claim, i["held_text"], i["term"])
            e = ms.queue_entry(task=TASK, item_id=i["item_id"], record=rec, claim=claim, verification=v,
                               held_ref=i["held_ref"], held_sha256=i["held_sha256"],
                               rule_decision="exclude X2", context={"term": i["term"], "slug": i["slug"], "nct": i["nct"]},
                               response_item=key)
            if i["item_id"] in old and old[i["item_id"]].get("reviewer_countersignature"):
                e["reviewer_countersignature"] = old[i["item_id"]]["reviewer_countersignature"]
            e["status"] = ms.status_of(e, rec, i["held_text"])
            entries.append(e)
    QUEUE.write_text(json.dumps({"task": TASK, "admits_into_build": False, "items": entries}, indent=1,
                                ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    cmd_status()


def cmd_status():
    q = json.loads(QUEUE.read_text(encoding="utf-8"))["items"]
    st, dec = {}, {}
    for e in q:
        st[e.get("status") or e.get("state")] = st.get(e.get("status") or e.get("state"), 0) + 1
        d = (e.get("verification") or {}).get("model_decision")
        if d:
            dec[d] = dec.get(d, 0) + 1
    print(f"N={len(q)}", st, "model roles:", dec)


if __name__ == "__main__":
    {"sweep": cmd_sweep, "freeze": cmd_freeze, "run": cmd_run, "queue": cmd_queue, "status": cmd_status}[sys.argv[1]]()
