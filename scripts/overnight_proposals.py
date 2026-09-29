"""Blind model readings, recorded and gated, against the harness rules of the ticagrelor / tocilizumab / statins reviews
(V1.0.1). Every call is a reproducible_ai record; every reading is a PROPOSED queue entry whose agreement with the
RULE is derived by model_source (never taken from the model); nothing here enters a build.

  task              item (population, frozen once)                               rule decision compared
  d5_identity       every (served D5 signal, registered outcome) pair           rob2._outcome_match_detail(...)["matched"]
  comparator_arm    every served X3 "no eligible comparator" exclusion           comparator rule on term_normal.comparator_text
  trial_identity    every pair of rows in a comparator's analysis membership    comparator_nesting (same registration + n of N)
  condition_role_reader2  the frozen condition_role items, second model         model_source.verify_condition_role

  python scripts/overnight_proposals.py freeze <task> | run <task> | queue <task> | status <task> | all
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
from reproducible_ai import model_source as ms  # noqa: E402

BASE = "6e26839a"      # the served pages the populations are drawn from (CI green, run 36469190915)
MODEL = {"d5_identity": "gpt-6-astra", "comparator_arm": "gpt-6-astra", "trial_identity": "gpt-6-astra",
         "condition_role_reader2": "gpt-5.5", "d5_identity_reader2": "gpt-5.5", "comparator_arm_reader2": "gpt-5.5",
         "trial_identity_reader2": "gpt-5.5"}


def base_task(task):
    return task[:-len("_reader2")] if task.endswith("_reader2") and task != "condition_role_reader2" else task
EFFORT, BATCH = "medium", 6
CODEX_LOG = Path("C:/mh-lanes/evid2-scratch/codex/codex_calls.jsonl")
QDIR = ROOT / ms.PROPOSAL_DIR

INSTR = {
    "d5_identity": """Each item gives a POOLED OUTCOME and ONE outcome a trial registered. Decide whether the registered
outcome is the SAME outcome as the pooled one -- the same components, not merely a related one (a bleeding outcome is
never the same as a death/MI/stroke composite; 'death from vascular causes' counts as cardiovascular death).
verdict: SAME_OUTCOME | DIFFERENT_OUTCOME | NOT_STATED. quote: words copied exactly from the REGISTERED outcome that
show it (null for NOT_STATED).""",
    "comparator_arm": """Each item is a trial record. Decide whether the trial randomised the intervention against a
control arm of placebo, usual care, standard care / standard of care (however written: 'standard-of-care', 'SOC' once
defined), best supportive care, or no treatment. verdict: COMPARATOR_PRESENT | NO_COMPARATOR | NOT_STATED. quote: words
copied exactly from the record that show it (null for NOT_STATED).""",
    "trial_identity": """Each item gives TWO rows of a meta-analysis, each with the report it cites. Decide whether the two
rows are reports of the SAME randomised trial, and if so whether one row's patients are a SUBGROUP of the other's.
verdict: SAME_TRIAL_SUBGROUP | SAME_TRIAL_SAME_POPULATION | DIFFERENT_TRIALS | NOT_STATED. quote: words copied exactly
from the item's text that show it (null for NOT_STATED).""",
}


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _show(path: str):
    try:
        return json.loads(subprocess.check_output(["git", "-C", str(ROOT), "show", f"{BASE}:{path}"],
                                                  stderr=subprocess.DEVNULL).decode("utf-8"))
    except subprocess.CalledProcessError:
        return None


def _slugs():
    return sorted(p.name for p in (ROOT / "docs" / "reviews").iterdir())


# ------------------------------------------------------------------------------------------------------ populations
def items_d5_identity():
    from harness import rob2
    out = []
    for slug in _slugs():
        r = _show(f"docs/reviews/{slug}/review.json") or {}
        for tid, t in ((r.get("rob2") or {}).get("trials") or {}).items():
            inp = ((t.get("domains") or {}).get("D5_selective_reporting") or {}).get("inputs") or {}
            if "pooled_outcome" not in inp:
                continue
            regs = [("primary", o) for o in inp.get("registered_primary_outcomes") or []] + \
                   [("secondary", o) for o in inp.get("registered_secondary_outcomes") or []]
            for j, (kind, o) in enumerate(regs):
                held = f"POOLED OUTCOME: {inp['pooled_outcome']}\nREGISTERED ({kind}): {rob2._registered_text(o)}"
                out.append({"item_id": f"{slug}::{tid}::{kind}{j}", "held_text": held, "held_sha256": _sha(held.encode()),
                            "held_ref": f"docs/reviews/{slug}/review.json@{BASE}#rob2/{tid}/D5",
                            "rule_input": {"pooled": inp["pooled_outcome"], "registered": o, "kind": kind}})
    return out


def items_comparator_arm():
    out = []
    for slug in _slugs():
        r = _show(f"docs/reviews/{slug}/review.json") or {}
        cfg = json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))
        inc = cfg.get("include") or {}
        terms = list(inc.get("comparator_any") or []) + list(inc.get("comparator_any_extra") or [])
        recs = {str(x.get("id")): x for v in json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8")).values()
                if isinstance(v, list) for x in v if isinstance(x, dict)}
        for d in (r.get("screening") or {}).get("records") or []:
            if d.get("rule_id") != "X3" or not str(d.get("reason") or "").startswith("no eligible comparator"):
                continue
            rid = str(d["id"]).split("·")[-1].strip()
            rec = recs.get(rid)
            if not rec:
                continue
            text = " ".join(str(rec.get(k) or "") for k in ("title", "abstract"))
            if rec.get("id_type") == "nct":
                text += " INTERVENTIONS: " + "; ".join(map(str, rec.get("interventions") or []))
            held = text.strip()
            out.append({"item_id": f"{slug}::{rid}", "held_text": held, "held_sha256": _sha(held.encode()),
                        "held_ref": f"cache/{slug}/records.json#{rid}", "rule_input": {"terms": terms}})
    return out


def items_trial_identity():
    from harness import comparator_analysis, comparator_nesting
    out = []
    for slug in _slugs():
        doc = comparator_analysis.load(ROOT, slug)
        if not doc or not doc.get("membership"):
            continue
        panel = next(iter(json.loads((ROOT / "cache" / slug / "comparators.json").read_text(encoding="utf-8"))), None)
        held = comparator_nesting._held_pubmed(ROOT, slug)
        alias = {t["family_id"]: [a["id"] for a in t.get("aliases") or [] if str(a.get("id")).isdigit()]
                 for t in (panel or {}).get("trial_set") or []}
        a = comparator_analysis.assess(doc, {"outcomes": []})
        nest = comparator_nesting.assess(ROOT, slug, a, panel, []) or {"nested": []}
        pairs = {(x["parent"]["label"], x["row"]["label"]) for x in nest["nested"] if x["relation"] == "SUBGROUP_OF"}
        rows = doc["membership"]["rows"]
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                ra, rb = rows[i], rows[j]

                def txt(r):
                    ps = alias.get(r.get("panel_row") or "") or []
                    body = " ".join((held.get(p) or {}).get("text", "")[:1500] for p in ps)
                    return f"ROW {r['label']} (n = {r['counts'][1] + r['counts'][3]}): {body or '(no held report)'}"
                text = txt(ra) + "\n" + txt(rb)
                rule = ("SAME_TRIAL_SUBGROUP" if (ra["label"], rb["label"]) in pairs or (rb["label"], ra["label"]) in pairs
                        else "DIFFERENT_TRIALS")
                out.append({"item_id": f"{slug}::{ra['label']}||{rb['label']}", "held_text": text,
                            "held_sha256": _sha(text.encode()), "held_ref": f"cache/{slug}/comparator_analysis.json",
                            "rule_decision": rule})
    return out


def items_condition_role_reader2():
    pop = json.loads((QDIR / "condition_role.population.json").read_text(encoding="utf-8"))["items"]
    return [dict(i, rule_decision="ENTRY_POPULATION") for i in pop]


ITEMS = {"d5_identity": items_d5_identity, "comparator_arm": items_comparator_arm,
         "trial_identity": items_trial_identity, "condition_role_reader2": items_condition_role_reader2}
for _t in ("d5_identity", "comparator_arm", "trial_identity"):
    # the second reader reads the FIRST reader's frozen population, never a re-derived one
    ITEMS[f"{_t}_reader2"] = (lambda t: lambda: json.loads((QDIR / f"{t}.population.json").read_text(encoding="utf-8"))["items"])(_t)


def rule_decision(task, i):
    """The RULE's decision for an item, computed now by the harness under test (never frozen with the item)."""
    task = base_task(task)
    if task == "d5_identity":
        from harness import rob2
        ri = i["rule_input"]
        d = rob2._outcome_match_detail(ri["pooled"], ri["registered"], None,
                                       allow_secondary_component_subset=(ri["kind"] == "secondary"))
        return "SAME_OUTCOME" if d["matched"] else "DIFFERENT_OUTCOME"
    if task == "comparator_arm":
        from harness import screen, term_normal
        return "COMPARATOR_PRESENT" if screen._has(term_normal.comparator_text(i["held_text"]), i["rule_input"]["terms"])             else "NO_COMPARATOR"
    return i.get("rule_decision")


def _pop(task):
    return QDIR / f"{task}.population.json"


def cmd_freeze(task):
    if _pop(task).exists():
        print(task, "already frozen"); return
    items = ITEMS[task]()
    _pop(task).write_text(json.dumps({"task": task, "frozen_from": BASE, "items": items}, indent=1, ensure_ascii=False) + "\n",
                          encoding="utf-8", newline="\n")
    print(task, "froze", len(items))


def _batches(task):
    items = json.loads(_pop(task).read_text(encoding="utf-8"))["items"]
    if task == "condition_role_reader2":
        sys.path.insert(0, str(ROOT / "scripts"))
        import condition_role_proposals as crp
        instr = crp.INSTR
        head = lambda i: f"condition_term={i['term']!r}"  # noqa: E731
    else:
        instr = INSTR[base_task(task)]
        head = lambda i: ""  # noqa: E731
    for k in range(0, len(items), BATCH):
        chunk = items[k:k + BATCH]
        keyed = [(f"R{j + 1}", i) for j, i in enumerate(chunk)]
        prompt = instr + "".join(f"\n=== ITEM item={key} {head(i)} ===\n{i['held_text']}\n" for key, i in keyed)
        yield {"batch": k // BATCH + 1, "keyed": keyed, "prompt": prompt.encode("utf-8"),
               "digests": [{"ref": i["held_ref"], "sha256": i["held_sha256"], "what": "held text"} for _, i in keyed]}


def _schema(task):
    if task == "condition_role_reader2":
        verdict = {"role": {"type": "string", "enum": list(ms.CONDITION_ROLES)}}
        req = ["item", "role", "quote"]
    else:
        verdict = {"verdict": {"type": "string", "enum": list(ms.CATEGORICAL_TASKS[task])}}
        req = ["item", "verdict", "quote"]
    it = {"type": "object", "additionalProperties": False, "required": req,
          "properties": dict({"item": {"type": "string"}, "quote": {"type": ["string", "null"]}}, **verdict)}
    return {"type": "object", "additionalProperties": False, "required": ["items"],
            "properties": {"items": {"type": "array", "items": it}}}


def _records():
    """{(prompt sha256, model requested): [records]} -- a second reader's prompt is byte-identical to the first's, so
    the model is part of the key (keying by prompt alone skipped every second-reader call)."""
    by = {}
    for p in (ROOT / ms.RECORD_DIR).glob("mc-*.json"):
        r = ms.load_record(p)
        by.setdefault((r["prompt"]["sha256"], (r.get("model") or {}).get("id_requested")), []).append(r)
    return by


def cmd_run(task):
    from reproducible_ai import model_call_live
    have = _records()
    for b in _batches(task):
        if any(r["state"] == "RAN_OK" for r in have.get((_sha(b["prompt"]), MODEL[task]), [])):
            continue
        rec = model_call_live.call(b["prompt"], schema=_schema(task), model=MODEL[task], effort=EFFORT,
                                   caller={"file": "scripts/overnight_proposals.py", "lane": "evid2", "line": "cmd_run",
                                           "purpose": f"{task} proposals, batch {b['batch']} ({len(b['keyed'])} items)"},
                                   input_digests=b["digests"])
        path = ms.write_record(rec, ROOT / ms.RECORD_DIR)
        with CODEX_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"lane": "evid2", "task": task, "batch": b["batch"], "record": path.name, "state": rec["state"],
                                "model_reported": rec["model"].get("id_reported"), "prompt_sha256": rec["prompt"]["sha256"]}) + "\n")
        print(task, b["batch"], rec["state"], rec["model"].get("id_reported"), flush=True)


def cmd_queue(task):
    have = _records()
    qp = QDIR / f"{task}.json"
    old = {e["item_id"]: e for e in json.loads(qp.read_text(encoding="utf-8"))["items"]} if qp.exists() else {}
    entries = []
    for b in _batches(task):
        rec = next((r for r in have.get((_sha(b["prompt"]), MODEL[task]), []) if r["state"] == "RAN_OK"), None)
        for key, i in b["keyed"]:
            if rec is None:
                entries.append({"item_id": i["item_id"], "task": task, "state": "NOT_YET_CALLED"})
                continue
            try:
                claim = ms.claim_for_item(ms.extract_claim(task, ms.replay(rec)), key)
            except ValueError as exc:
                entries.append({"item_id": i["item_id"], "task": task, "state": "RESPONSE_NOT_A_CLAIM", "why": str(exc)})
                continue
            ctx = {"term": i["term"]} if task == "condition_role_reader2" else None
            e = ms.queue_entry(task=task, item_id=i["item_id"], record=rec, claim=claim,
                               verification={}, held_ref=i["held_ref"], held_sha256=i["held_sha256"],
                               rule_decision=rule_decision(task, i), context=ctx, response_item=key)
            e["verification"] = ms.reverify(e, i["held_text"])
            e["individual_signature_required"] = ms.needs_individual_signature(e["verification"])
            if i["item_id"] in old and old[i["item_id"]].get("reviewer_countersignature"):
                e["reviewer_countersignature"] = old[i["item_id"]]["reviewer_countersignature"]
            e["status"] = ms.status_of(e, rec, i["held_text"])
            entries.append(e)
    qp.write_text(json.dumps({"task": task, "admits_into_build": False, "items": entries}, indent=1, ensure_ascii=False) + "\n",
                  encoding="utf-8", newline="\n")
    cmd_status(task)


def cmd_status(task):
    q = json.loads((QDIR / f"{task}.json").read_text(encoding="utf-8"))["items"]
    st, ag = {}, {}
    for e in q:
        k = e.get("status") or e.get("state")
        st[k] = st.get(k, 0) + 1
        a = str((e.get("verification") or {}).get("agreement") or "-").split("(")[0]
        ag[a] = ag.get(a, 0) + 1
    print(task, f"N={len(q)}", st, ag, flush=True)


if __name__ == "__main__":
    cmd, task = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else None)
    if cmd == "all":
        for t in ITEMS:
            cmd_freeze(t); cmd_run(t); cmd_queue(t)
    else:
        {"freeze": cmd_freeze, "run": cmd_run, "queue": cmd_queue, "status": cmd_status}[cmd](task)
