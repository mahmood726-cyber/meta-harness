"""Pilot of model-call-as-source on two populations. Nothing it writes can admit anything.

  screening  the screened-in records of every committed review page (the denominator scripts/arm_object_sweep.py
             reports as included_refused_by_arm_object.N, read here through that script's own record lookup). The
             model reads each record's held text against the topic's registered question and returns, per axis
             (population, intervention, comparator, design), MET / NOT_MET / NOT_STATED with a verbatim quote. The
             overall decision is DERIVED by reproducible_ai.model_source.verify_screening, never taken from the model.
  estimand   every estimand field the bundle's regex leaves without a statement (state != STATED_IN_OWNING_EVIDENCE)
             on every served BUNDLE.json. The model reads the row's PARSED_SOURCE and returns a value from the rule's
             own vocabulary, or NOT_STATED, with the sentence it read it from.
  outcome_identity / locate   RECORDED re-makes of the model judgments the served gates read from cache
             (outcome_judgments.json, locate_judgments.json), made WITHOUT a record originally; each is compared with
             that unrecorded prior (PRIOR_MODEL_AGREE / PRIOR_MODEL_DISAGREE) and changes nothing served.
  screening_reader2   a second model reads the screening items whose reader-1 proposal needs an individual signature;
             `readers` compares the two (a triage for the human; same vendor, so partially independent at best).
  Re-asks (`stability`) measure the MODEL; an item whose re-ask reaches a different decision needs an individual
  signature.

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
# a second reader must be a different model id; same vendor (OpenAI via codex) -- stated, not hidden
MODEL_BY_TASK = {"screening_reader2": "gpt-5.5", "screening_excluded_reader2": "gpt-5.5", "screening_excluded_x1_reader2": "gpt-5.5", "screening_excluded_agree_reader2": "gpt-5.5", "comparator_k_reader2": "gpt-5.5", "regex_label_reader2": "gpt-5.5", "site_label_v2_reader2": "gpt-5.5", "regex_label_deep_reader2": "gpt-5.5", "site_label_deep_reader2": "gpt-5.5", "site_label_ol_reader2": "gpt-5.5", "site_label_ol2_reader2": "gpt-5.5", "site_label_deep2_reader2": "gpt-5.5"}
EFFORT = "medium"
BATCH = {"screening": 6, "estimand": 3, "outcome_identity": 1, "locate": 1, "screening_reader2": 6, "screening_excluded": 6, "screening_excluded_x1": 6, "screening_excluded_reader2": 6, "screening_excluded_x1_reader2": 6, "screening_excluded_agree_reader2": 6, "regex_label": 8, "comparator_k": 1, "comparator_k_reader2": 1, "site_label": 8, "site_label_v2": 8, "regex_label_reader2": 8, "site_label_v2_reader2": 8, "site_label_ol": 8, "regex_label_deep": 8, "site_label_deep": 8, "regex_label_deep_reader2": 8, "site_label_deep_reader2": 8, "site_label_ol2": 8, "site_label_deep2": 8, "site_label_ol_reader2": 8, "site_label_ol2_reader2": 8, "site_label_deep2_reader2": 8}
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


LOCATE_INSTR = """You are checking whether a trial's abstract reports a meta-analysis's TARGET OUTCOME. Do not run any
commands or read any files. Use only the text given here. Do not estimate or infer any number.

REVIEW: {review}
TARGET OUTCOME: {outcome}
{outcome_detail}
REVIEW POPULATION: {population}

Answer with:
  "span": the ONE sentence of the abstract that reports this outcome, copied EXACTLY, character for character (no
          ellipses, no paraphrase); null if the abstract reports no result for it,
  "is_target_outcome": true only if that sentence reports THIS outcome (same event definition and timepoint), not a
          component, a different endpoint, or a different timepoint,
  "population_matches": whether the trial's population is the review population,
  "both_arms": whether the sentence gives the result for both randomised arms,
  "timepoint": the timepoint the sentence reports, or "unspecified",
  "why": one sentence.
When unsure, is_target_outcome = false. Return only the JSON object.

=== ABSTRACT ===
{abstract}
"""


def _outcome_spec(cfg: dict, name: str) -> dict:
    for key in ("primary_outcome", "secondary_outcomes", "harm_outcomes"):
        v = cfg.get(key)
        for o in (v if isinstance(v, list) else [v] if v else []):
            if isinstance(o, dict) and o.get("name") == name:
                return o
    return {"name": name}


def candidates_outcome_identity() -> list[dict]:
    """Every committed outcome-identity judgment (the served gate's input), re-asked as a RECORDED call with the
    producer's own prompt (scripts/outcome_judgments.py::build_prompt). The prior judgment is kept for comparison."""
    oj = _load_script("outcome_judgments")
    out = []
    for p in sorted((ROOT / "cache").glob("*/outcome_judgments.json")):
        slug = p.parent.name
        prior = json.loads(p.read_text(encoding="utf-8"))
        spec, cands = oj.collect_candidates(slug)
        for c in cands:
            held = f"title: {c['title']}\ntype: {c.get('type')}\nparamType: {c.get('paramType')}"
            pj = (prior.get("judgments") or {}).get(c["title"])
            out.append({"task": "outcome_identity", "slug": slug, "item_id": f"{slug}::OM::{c['title']}",
                        "held_ref": f"cache/{slug}/records.json#ctgov_results[title={c['title']}]",
                        "held_text": held, "held_sha256": _sha(held.encode("utf-8")),
                        "rule_decision": (f"PRIOR {prior.get('model')!r}: is_match={pj.get('is_match')}" if pj else "NO PRIOR"),
                        "prior": {"is_match": pj.get("is_match")} if pj else None,
                        "prompt_text": oj.build_prompt(spec, c),
                        "prompt_digests": [_file_digest(f"topics/{slug}.json"), _file_digest(f"cache/{slug}/records.json")]})
    return sorted(out, key=lambda i: i["item_id"])


def candidates_locate() -> list[dict]:
    """Every committed locate-gate judgment (made in-session on 2026-09-11; its prompt was never recorded), asked again
    as a RECORDED call on a stated task. This is a NEW call, not a replay of the original."""
    out = []
    for p in sorted((ROOT / "cache").glob("*/locate_judgments.json")):
        slug = p.parent.name
        cfg = json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))
        pico = {t["id"]: t for t in json.loads((ROOT / "pico.json").read_text(encoding="utf-8"))["topics"]}.get(slug) or {}
        recs = {str(r.get("id")): r for r in json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8"))["records"]}
        for pmid, outs in json.loads(p.read_text(encoding="utf-8")).items():
            for oname, j in outs.items():
                abstract = (recs.get(str(pmid)) or {}).get("abstract")
                item = {"task": "locate", "slug": slug, "item_id": f"{slug}::PMID {pmid}::{oname}",
                        "held_ref": f"cache/{slug}/records.json#PMID-{pmid} abstract",
                        "rule_decision": (f"PRIOR {j.get('model')!r} {j.get('date')}: is_target_outcome={j.get('is_target_outcome')}, "
                                          f"population_matches={j.get('population_matches')}"),
                        "prior": {k: j.get(k) for k in ("is_target_outcome", "population_matches") if k in j}}
                if not abstract:
                    item["state"] = "NO_HELD_TEXT"
                else:
                    spec = _outcome_spec(cfg, oname)
                    detail = "; ".join(f"{k}: {spec[k]}" for k in ("definition", "timepoint", "population", "estimand") if spec.get(k))
                    item.update(held_text=abstract, held_sha256=_sha(abstract.encode("utf-8")),
                                prompt_text=LOCATE_INSTR.format(review=cfg.get("title"), outcome=oname,
                                                                outcome_detail=detail or "(no further definition registered)",
                                                                population=pico.get("P") or cfg.get("eligibility_summary"),
                                                                abstract=abstract),
                                prompt_digests=[_file_digest(f"topics/{slug}.json"), _file_digest("pico.json")])
                out.append(item)
    return sorted(out, key=lambda i: i["item_id"])


def _reader2_of(source_task: str, task: str) -> list[dict]:
    """The items where reader 1's committed proposal in `source_task` does NOT agree with the rule (cannot tell, or
    disagree): the items a human must sign individually. Same held text; a second model reads them independently."""
    q = Q_DIR / f"{source_task}.json"
    if not q.exists():
        return []
    non_agree = {e["item_id"] for e in json.loads(q.read_text(encoding="utf-8"))["items"]
                 if "verification" in e and ms.needs_individual_signature(e["verification"])}
    return [dict(i, task=task) for i in candidates_screening() if i["item_id"] in non_agree]


def _agreed_of(source_task: str, task: str) -> list[dict]:
    """The items where reader 1 AGREED with the rule. A wrong rule that reader 1 also got wrong is invisible to every
    other queue; a second reader on the agreements is the only place it can surface."""
    q = Q_DIR / f"{source_task}.json"
    if not q.exists():
        return []
    agreed = {e["item_id"] for e in json.loads(q.read_text(encoding="utf-8"))["items"]
              if "verification" in e and str(e["verification"].get("agreement", "")).startswith("RULE_MODEL_AGREE")}
    return [dict(i, task=task) for i in candidates_screening() if i["item_id"] in agreed]


COMPARATOR_K_INSTR = """You are reading the abstract of a published systematic review / meta-analysis. Do not run any
commands or read any files. Use only the text given here. Do not calculate, add up or infer anything.

Question: how many trials (studies) did THIS review INCLUDE in total?

Answer "state":
  STATED     the abstract itself states the total number of included trials/studies. Give "quote": the words of the
             abstract that state it, copied EXACTLY, and "count_text": the count exactly as written inside that quote
             (e.g. "12" or "Eight").
  AMBIGUOUS  the abstract gives more than one candidate count and does not make clear which is the total (for example
             counts for subgroups or outcomes only). Give "quote" (the words that make it ambiguous) and "count_text": null.
  NOT_STATED the abstract does not state the total. Give "quote": null and "count_text": null.
A count of trials for ONE outcome, subgroup or comparison is not the total. Return only the JSON object.
"""


def candidates_comparator_k() -> list[dict]:
    """Every topic's comparator abstract (the text harness/pipeline.py reads for theirs_k). A topic whose config carries
    a source-verified comparator_k is a CONTROL (item_id 'control::<slug>', its known answer in `prior`) -- counted
    apart from the data, never in its denominator."""
    out = []
    for cfgp in sorted((ROOT / "topics").glob("*.json")):
        slug = cfgp.stem
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        rp = ROOT / "cache" / slug / "records.json"
        if not cfg.get("comparator_pmid") or not rp.exists():
            continue
        pmid = str(cfg["comparator_pmid"])
        rec = {str(r.get("id")): r for r in json.loads(rp.read_text(encoding="utf-8")).get("records") or []}.get(pmid)
        control = cfg.get("comparator_k") is not None
        item = {"task": "comparator_k", "slug": slug, "item_id": f"{'control' if control else 'data'}::{slug}",
                "held_ref": f"cache/{slug}/records.json#{pmid} abstract",
                "rule_decision": "legacy auto-extraction (harness.extract._parse_k)",
                "prior": cfg.get("comparator_k") if control else None}
        abstract = (rec or {}).get("abstract") or ""
        if not abstract.strip():
            item["state"] = "NO_HELD_TEXT"
        else:
            item.update(held_text=abstract, held_sha256=_sha(abstract.encode("utf-8")),
                        prompt_text=COMPARATOR_K_INSTR + "\n=== ABSTRACT item=R1 ===\n" + abstract + "\n",
                        prompt_digests=[])
        out.append(item)
    return sorted(out, key=lambda i: i["item_id"])


def candidates_comparator_k_reader2() -> list[dict]:
    """The same comparator abstracts read by a second model; the reader-2 header makes the prompt bytes differ, so the
    two readers' records never share a prompt digest."""
    out = []
    for i in candidates_comparator_k():
        i = dict(i, task="comparator_k_reader2")
        if "prompt_text" in i:
            i["prompt_text"] = READER2_HEADER + i["prompt_text"]
        out.append(i)
    return out


def candidates_site_label() -> list[dict]:
    """R2 for the regex sites outside extract.py (regex_layer/site_measure.py): held abstract sentences or protocol
    lines where the site fires, or only its broad trigger does. `slug` is the SITE so a batch asks about one site; the
    regex and its output are never in the prompt."""
    from regex_layer import site_measure
    out = []
    for c in site_measure.candidates(15):
        out.append({"task": "site_label", "slug": c["site"], "pattern": c["site"], "sample": c["sample"],
                    "item_id": f"{c['site']}::{c['held_sha256'][:16]}", "held_ref": c["held_ref"],
                    "held_text": c["text"], "held_sha256": c["held_sha256"],
                    "rule_decision": f"site sample {c['sample']}"})
    return sorted(out, key=lambda i: i["item_id"])


def candidates_regex_label_deep() -> list[dict]:
    """The SAME sampling rule as regex_label with up to 40 per pool instead of 15: exactly the items after the first 15
    in each pool's sha256 order (the first 15 are regex_label's and are not re-asked)."""
    from regex_layer import measure
    first = {f"{c['pattern']}::{c['held_sha256'][:16]}" for c in measure.candidates(15)}
    out = []
    for c in measure.candidates(40):
        iid = f"{c['pattern']}::{c['held_sha256'][:16]}"
        if iid in first:
            continue
        out.append({"task": "regex_label_deep", "slug": c["pattern"], "pattern": c["pattern"], "sample": c["sample"],
                    "item_id": iid, "held_ref": c["held_ref"], "held_text": c["sentence"], "held_sha256": c["held_sha256"],
                    "rule_decision": f"regex sample {c['sample']}"})
    return sorted(out, key=lambda i: i["item_id"])


def candidates_site_label_deep() -> list[dict]:
    """site_label_v2 / site_label_ol's rule with up to 40 per pool: the items after the first 15 (not re-asked)."""
    from regex_layer import site_measure
    first = {f"{c['site']}::{c['held_sha256'][:16]}" for c in site_measure.candidates(15)}
    out = []
    for c in site_measure.candidates(40):
        iid = f"{c['site']}::{c['held_sha256'][:16]}"
        if iid in first:
            continue
        out.append({"task": "site_label_deep", "slug": c["site"], "pattern": c["site"], "sample": c["sample"],
                    "item_id": iid, "held_ref": c["held_ref"], "held_text": c["text"], "held_sha256": c["held_sha256"],
                    "rule_decision": f"site sample {c['sample']}"})
    return sorted(out, key=lambda i: i["item_id"])


def candidates_regex_label() -> list[dict]:
    """R2 of the regex layer: sampled held sentences per compiled pattern of harness/extract.py (regex_layer.measure).
    `slug` is set to the PATTERN so each batch asks about one pattern; the regex's output is never in the prompt."""
    from regex_layer import measure
    out = []
    for c in measure.candidates(15):
        out.append({"task": "regex_label", "slug": c["pattern"], "pattern": c["pattern"], "sample": c["sample"],
                    "item_id": f"{c['pattern']}::{c['held_sha256'][:16]}", "held_ref": c["held_ref"],
                    "held_text": c["sentence"], "held_sha256": c["held_sha256"],
                    "rule_decision": f"regex sample {c['sample']}"})
    return sorted(out, key=lambda i: i["item_id"])


def candidates_screening_reader2() -> list[dict]:
    return _reader2_of("screening", "screening_reader2")


CANDIDATES = {"screening": candidates_screening, "estimand": candidates_estimand,
              "regex_label": candidates_regex_label, "regex_label_reader2": lambda: [dict(i, task="regex_label_reader2") for i in candidates_regex_label()], "comparator_k": candidates_comparator_k, "comparator_k_reader2": candidates_comparator_k_reader2, "site_label": candidates_site_label, "site_label_v2": lambda: [dict(i, task="site_label_v2") for i in candidates_site_label()],
              "site_label_v2_reader2": lambda: [dict(i, task="site_label_v2_reader2") for i in candidates_site_label()],
              "regex_label_deep": candidates_regex_label_deep, "site_label_deep": candidates_site_label_deep,
              "regex_label_deep_reader2": lambda: [dict(i, task="regex_label_deep_reader2") for i in candidates_regex_label_deep()],
              "site_label_deep_reader2": lambda: [dict(i, task="site_label_deep_reader2") for i in candidates_site_label_deep()],
              "site_label_ol_reader2": lambda: [dict(i, task="site_label_ol_reader2") for i in CANDIDATES["site_label_ol"]()],
              "site_label_ol2_reader2": lambda: [dict(i, task="site_label_ol2_reader2") for i in CANDIDATES["site_label_ol2"]()],
              "site_label_deep2_reader2": lambda: [dict(i, task="site_label_deep2_reader2") for i in CANDIDATES["site_label_deep2"]()],
              "site_label_deep2": lambda: [dict(i, task="site_label_deep2") for i in candidates_site_label_deep()
                                           if i["pattern"].split(":")[0] in ("gate.py", "protocol_compiler.py", "absence.py", "registry_multi.py", "pipeline.py")],
              "site_label_ol2": lambda: [dict(i, task="site_label_ol2") for i in candidates_site_label()
                                         if i["pattern"].split(":")[0] in ("gate.py", "protocol_compiler.py", "absence.py", "registry_multi.py", "pipeline.py")],
              "site_label_ol": lambda: [dict(i, task="site_label_ol") for i in candidates_site_label()
                                        if i["pattern"].split(":")[0] in ("rob2.py", "funding.py", "hand_binding.py")],
              "screening_reader2": candidates_screening_reader2,
              "screening_excluded": lambda: [dict(i, task="screening_excluded") for i in candidates_screening()],
              "screening_excluded_x1": lambda: [dict(i, task="screening_excluded_x1") for i in candidates_screening()],
              "screening_excluded_reader2": lambda: _reader2_of("screening_excluded", "screening_excluded_reader2"),
              "screening_excluded_x1_reader2": lambda: _reader2_of("screening_excluded_x1", "screening_excluded_x1_reader2"),
              "screening_excluded_agree_reader2": lambda: _agreed_of("screening_excluded", "screening_excluded_agree_reader2"),
              "outcome_identity": candidates_outcome_identity, "locate": candidates_locate}
# The selection rule that defines each pilot's population AT FREEZE TIME. After the freeze the population does not
# move: a later rule change (a regex that now reads a field, a record the screen now excludes) is recorded on the
# item as rule_decision_now, never by removing it -- a denominator that shrinks when the rule improves cannot show
# that the rule caught up.
SELECT = {"screening": lambda i: i["rule_decision"] == "include",
          "estimand": lambda i: i["rule_state"] != "STATED_IN_OWNING_EVIDENCE",
          "outcome_identity": lambda i: True, "locate": lambda i: True, "screening_reader2": lambda i: True,
          # phase A: records the KEYWORD rules excluded (X2 population, X3 intervention/comparator, design, contrast,
          # dose, age, dedup); X1 (not an RCT, from publication type) is a separate, later phase
          "screening_excluded": lambda i: i["rule_decision"] == "exclude" and i.get("rule_id") != "X1",
          # phase B: X1 'not an RCT' (publication type / design words); a missing pubtype can wrongly exclude a trial
          "screening_excluded_x1": lambda i: i["rule_decision"] == "exclude" and i.get("rule_id") == "X1",
          "screening_excluded_reader2": lambda i: True, "screening_excluded_x1_reader2": lambda i: True,
          "screening_excluded_agree_reader2": lambda i: True, "regex_label": lambda i: True, "comparator_k": lambda i: True, "comparator_k_reader2": lambda i: True, "site_label": lambda i: True, "site_label_v2": lambda i: True, "regex_label_reader2": lambda i: True, "site_label_v2_reader2": lambda i: True, "site_label_ol": lambda i: True, "regex_label_deep": lambda i: True, "site_label_deep": lambda i: True, "regex_label_deep_reader2": lambda i: True, "site_label_deep_reader2": lambda i: True, "site_label_ol2": lambda i: True, "site_label_deep2": lambda i: True, "site_label_ol_reader2": lambda i: True, "site_label_ol2_reader2": lambda i: True, "site_label_deep2_reader2": lambda i: True}
SELECTION_RULE = {"screening": "screened records with decision == include on the committed review pages",
                  "estimand": "estimand fields whose bundle state != STATED_IN_OWNING_EVIDENCE on the served bundles",
                  "outcome_identity": "every candidate CT.gov outcome measure of every topic with a committed "
                                      "cache/<slug>/outcome_judgments.json (read by the served outcome-identity gate)",
                  "locate": "every judgment in every committed cache/<slug>/locate_judgments.json (read by the served "
                            "locate gate)",
                  "screening_reader2": "screening items whose reader-1 proposal needs an individual signature "
                                       "(registry/model_proposals/screening.json)",
                  "screening_excluded": "screened records the rule EXCLUDED with a keyword rule (every rule_id except "
                                        "X1 not-an-RCT) on the committed review pages",
                  "screening_excluded_x1": "screened records the rule EXCLUDED as X1 (not an RCT) on the committed "
                                           "review pages",
                  "screening_excluded_reader2": "keyword-excluded records whose reader-1 proposal needs an individual "
                                                "signature (registry/model_proposals/screening_excluded.json)",
                  "screening_excluded_x1_reader2": "X1-excluded records whose reader-1 proposal needs an individual "
                                                   "signature (registry/model_proposals/screening_excluded_x1.json)",
                  "screening_excluded_agree_reader2": "keyword-excluded records where reader 1 AGREED with the rule "
                                                      "(registry/model_proposals/screening_excluded.json)",
                  "regex_label": "per compiled pattern of harness/extract.py: up to 15 held sentences where it fires "
                                 "and up to 15 where only its broad trigger fires (sha256 order)",
                  "comparator_k": "every topic with a comparator_pmid; topics with a source-verified comparator_k are "
                                  "CONTROLS (item_id control::), the rest data (item_id data::)",
                  "comparator_k_reader2": "the comparator_k items, read by a second model (gpt-5.5)",
                  "site_label": "per labellable regex site outside extract.py whose text source is held here: up to 15 "
                                "texts where it fires and up to 15 where only its broad trigger fires (sha256 order)",
                  "site_label_v2": "site_label's rule, with protocol lines de-duplicated by text (site_label froze 56 "
                                   "duplicate ids); the output schema is strict",
                  "regex_label_reader2": "the regex_label items, read by a second model (gpt-5.5)",
                  "site_label_v2_reader2": "the site_label_v2 items, read by a second model (gpt-5.5)",
                  "site_label_ol": "site_label's rule for the regex sites of harness/rob2.py, funding.py and hand_binding.py "
                                   "(the other lane's files: measured and planted from regex_layer/ only)",
                  "regex_label_deep": "regex_label's rule with up to 40 per pool: the items after the first 15 in sha256 order",
                  "site_label_deep": "the site label rule with up to 40 per pool: the items after the first 15",
                  "regex_label_deep_reader2": "the regex_label_deep items, read by a second model (gpt-5.5)",
                  "site_label_deep_reader2": "the site_label_deep items, read by a second model (gpt-5.5)",
                  "site_label_ol2": "site_label's rule for the sites of gate.py, protocol_compiler.py, absence.py, "
                                    "registry_multi.py and pipeline.py (the other lane's files; read-only)",
                  "site_label_deep2": "site_label_deep's rule (items 16-40 per pool) for the site_label_ol2 files, whose "
                                      "sites were planted after site_label_deep was frozen",
                  "site_label_ol_reader2": "the site_label_ol items, read by a second model (gpt-5.5)",
                  "site_label_ol2_reader2": "the site_label_ol2 items, read by a second model (gpt-5.5)",
                  "site_label_deep2_reader2": "the site_label_deep2 items, read by a second model (gpt-5.5)"}
FROZEN_KEYS = ("item_id", "slug", "held_ref", "held_sha256", "state", "rule_decision", "rule_id", "field", "rule_state", "prior",
               "pattern", "sample")


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
        for k in ("rule_id", "rule_reason", "rule_state", "rule_value", "prompt_text", "prompt_digests"):
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


TASKS = ("estimand", "screening", "outcome_identity", "locate", "screening_reader2", "screening_excluded",
         "screening_excluded_x1", "screening_excluded_reader2", "screening_excluded_x1_reader2",
         "screening_excluded_agree_reader2", "regex_label", "comparator_k", "comparator_k_reader2", "site_label", "site_label_v2", "regex_label_reader2", "site_label_v2_reader2", "site_label_ol", "regex_label_deep", "site_label_deep",
         "regex_label_deep_reader2", "site_label_deep_reader2", "site_label_ol2", "site_label_deep2",
         "site_label_ol_reader2", "site_label_ol2_reader2", "site_label_deep2_reader2")
# retired: kept as the record of what ran (a frozen population is never edited); never run again
RETIRED_TASKS = ("site_label",)
SCREEN_TASKS = ("screening", "screening_reader2", "screening_excluded", "screening_excluded_x1",
                "screening_excluded_reader2", "screening_excluded_x1_reader2", "screening_excluded_agree_reader2")
N_NAME = {"screening": "screened-in records across committed review pages",
          "estimand": "estimand fields without a stated value across served bundles",
          "outcome_identity": "candidate CT.gov outcome measures under a committed outcome-identity judgment file",
          "locate": "committed locate-gate judgments",
          "screening_reader2": "screening items whose reader-1 proposal needs an individual signature",
          "screening_excluded": "records excluded by a keyword rule (not X1) across committed review pages",
          "screening_excluded_x1": "records excluded as X1 (not an RCT) across committed review pages",
          "screening_excluded_reader2": "keyword-excluded records whose reader-1 proposal needs an individual signature",
          "screening_excluded_x1_reader2": "X1-excluded records whose reader-1 proposal needs an individual signature",
          "screening_excluded_agree_reader2": "keyword-excluded records where reader 1 agreed with the rule",
          "regex_label": "sampled held sentences per compiled pattern of harness/extract.py",
          "comparator_k": "comparator review abstracts, one per topic (controls counted apart)",
          "comparator_k_reader2": "comparator review abstracts, second reader (controls counted apart)",
          "site_label": "sampled held texts per labellable regex site outside extract.py (RETIRED: duplicate ids)",
          "site_label_v2": "sampled held texts per labellable regex site outside extract.py",
          "regex_label_reader2": "sampled held sentences per compiled pattern of harness/extract.py, second reader",
          "site_label_v2_reader2": "sampled held texts per labellable regex site outside extract.py, second reader",
          "site_label_ol": "sampled held texts per labellable regex site of rob2.py / funding.py / hand_binding.py",
          "regex_label_deep": "held sentences 16-40 per pool per compiled pattern of harness/extract.py",
          "site_label_deep": "held texts 16-40 per pool per labellable regex site",
          "regex_label_deep_reader2": "held sentences 16-40 per pool per extract.py pattern, second reader",
          "site_label_deep_reader2": "held texts 16-40 per pool per labellable regex site, second reader",
          "site_label_ol2": "sampled held texts per labellable site of gate / protocol_compiler / absence / registry_multi / pipeline",
          "site_label_deep2": "held texts 16-40 per pool for the site_label_ol2 sites",
          "site_label_ol_reader2": "the site_label_ol texts, second reader",
          "site_label_ol2_reader2": "the site_label_ol2 texts, second reader",
          "site_label_deep2_reader2": "the site_label_deep2 texts, second reader"}


def check_unique_ids(task: str, items: list) -> None:
    """A population whose items share an id cannot be queued without silently collapsing some -- refused."""
    seen, dup = set(), set()
    for i in items:
        (dup if i["item_id"] in seen else seen).add(i["item_id"])
    if dup:
        sys.exit(f"refused: {task} has {len(dup)} duplicated item ids (e.g. {sorted(dup)[:3]}); the queue would collapse "
                 "them and shrink the denominator")


def cmd_freeze(task: str, base: str):
    if task in RETIRED_TASKS:
        sys.exit(f"refused: {task} is retired")
    p = population_path(task)
    if p.exists():
        sys.exit(f"refused: {p.name} exists; a population is frozen once (a new pilot is a new task name)")
    sel = _current_selection(task)
    check_unique_ids(task, sel)
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


READER2_HEADER = ("SECOND READER. Another reader has already assessed these records; you do not see that assessment. "
                  "Assess them independently.\n\n")


REGEX_LABEL_INSTR = """You are labelling sentences from trial abstracts for a test of a text parser. Do not run any
commands or read any files. Use only the text given here. Do not calculate, round, convert or infer anything.

WHAT TO LOOK FOR: {spec}

For EACH sentence answer "states": true only if the sentence itself states this.
{how}
Answer every sentence, using its "item" key exactly. Return only the JSON object.
"""


def site_label_prompt(site: str, keyed: list, strict: bool = False) -> str:
    from regex_layer.site_detects import DETECTS
    how = ('If it does, give "quote": the words of the text that state it, copied EXACTLY. If it does not, give "quote": null.'
           if strict else
           'If it does, give "quote": the words of the text that state it, copied EXACTLY, and "instances": []. '
           'If it does not, give "quote": null and "instances": [].')
    body = REGEX_LABEL_INSTR.format(spec=DETECTS[site]["detects"], how=how).replace("sentences from trial abstracts",
                                                                                    "short texts from trial reports")
    for key, i in keyed:
        body += f"\n=== SENTENCE item={key} ===\n{i['held_text']}\n"
    return body


def regex_label_prompt(pattern: str, keyed: list) -> str:
    from regex_layer.measure import label_fields
    from regex_layer.specs import SPECS
    spec = SPECS[pattern]
    if spec["kind"] == "extractor":
        how = ("If it does, list EVERY instance in \"instances\"; for each instance give \"fields\": one entry per field "
               f"({', '.join(label_fields(pattern))}) with \"quote\" = the characters of that value copied EXACTLY from "
               "the sentence (null if that field is not written for this instance). Give \"quote\": null. If it does "
               "not, give \"instances\": [] and \"quote\": null.")
    else:
        how = ("If it does, give \"quote\": the words of the sentence that state it, copied EXACTLY, and "
               "\"instances\": []. If it does not, give \"quote\": null and \"instances\": [].")
    body = REGEX_LABEL_INSTR.format(spec=spec["spec"], how=how)
    for key, i in keyed:
        body += f"\n=== SENTENCE item={key} ===\n{i['held_text']}\n"
    return body


def _schema(task: str) -> dict:
    if task == "outcome_identity":
        return _load_script("outcome_judgments").OUTCOME_SCHEMA
    if task in ("comparator_k", "comparator_k_reader2"):
        it = {"type": "object", "additionalProperties": False, "required": ["item", "state", "quote", "count_text"],
              "properties": {"item": {"type": "string"}, "state": {"type": "string", "enum": ["STATED", "NOT_STATED", "AMBIGUOUS"]},
                             "quote": {"type": ["string", "null"]}, "count_text": {"type": ["string", "null"]}}}
        return {"type": "object", "additionalProperties": False, "required": ["items"],
                "properties": {"items": {"type": "array", "items": it}}}
    if task in ("site_label_v2", "site_label_v2_reader2", "site_label_ol", "site_label_deep", "site_label_deep_reader2",
                "site_label_ol2", "site_label_deep2", "site_label_ol_reader2", "site_label_ol2_reader2", "site_label_deep2_reader2"):
        it = {"type": "object", "additionalProperties": False, "required": ["item", "states", "quote"],
              "properties": {"item": {"type": "string"}, "states": {"type": "boolean"}, "quote": {"type": ["string", "null"]}}}
        return {"type": "object", "additionalProperties": False, "required": ["items"],
                "properties": {"items": {"type": "array", "items": it}}}
    if task == "site_label":
        it = {"type": "object", "additionalProperties": False, "required": ["item", "states", "quote", "instances"],
              "properties": {"item": {"type": "string"}, "states": {"type": "boolean"}, "quote": {"type": ["string", "null"]},
                             "instances": {"type": "array", "maxItems": 0, "items": {"type": "object"}}}}
        return {"type": "object", "additionalProperties": False, "required": ["items"],
                "properties": {"items": {"type": "array", "items": it}}}
    if task in ("regex_label", "regex_label_reader2", "regex_label_deep", "regex_label_deep_reader2"):
        field = {"type": "object", "additionalProperties": False, "required": ["field", "quote"],
                 "properties": {"field": {"type": "string"}, "quote": {"type": ["string", "null"]}}}
        inst = {"type": "object", "additionalProperties": False, "required": ["fields"],
                "properties": {"fields": {"type": "array", "items": field}}}
        it = {"type": "object", "additionalProperties": False, "required": ["item", "states", "quote", "instances"],
              "properties": {"item": {"type": "string"}, "states": {"type": "boolean"},
                             "quote": {"type": ["string", "null"]}, "instances": {"type": "array", "items": inst}}}
        return {"type": "object", "additionalProperties": False, "required": ["items"],
                "properties": {"items": {"type": "array", "items": it}}}
    if task == "locate":
        props = {"span": {"type": ["string", "null"]}, "is_target_outcome": {"type": "boolean"},
                 "population_matches": {"type": "boolean"}, "both_arms": {"type": "boolean"},
                 "timepoint": {"type": "string"}, "why": {"type": "string"}}
        return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}
    if task in SCREEN_TASKS:
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
            if task in SCREEN_TASKS:
                crit, cd = criteria(slug)
                body = (READER2_HEADER if task.endswith("_reader2") else "") + SCREEN_INSTR + \
                    "\n=== REGISTERED CRITERIA ===\n" + crit + "\n"
                for key, i in keyed:
                    body += f"\n=== RECORD item={key} ===\n{i['held_text']}\n"
                digests = cd + digests
            elif task in ("regex_label", "regex_label_deep"):
                body = regex_label_prompt(slug, keyed)
            elif task in ("regex_label_reader2", "regex_label_deep_reader2"):
                body = READER2_HEADER + regex_label_prompt(slug, keyed)
            elif task in ("site_label", "site_label_v2", "site_label_ol", "site_label_deep", "site_label_ol2", "site_label_deep2"):
                body = site_label_prompt(slug, keyed, strict=(task != "site_label"))
            elif task in ("site_label_v2_reader2", "site_label_deep_reader2", "site_label_ol_reader2", "site_label_ol2_reader2", "site_label_deep2_reader2"):
                body = READER2_HEADER + site_label_prompt(slug, keyed, strict=True)
            elif task == "estimand":
                vocab = "\n".join(f"  {f}: {', '.join(ms.estimand_vocabulary(f))}" for f in ("analysis_set", "analysis_window"))
                body = ESTIMAND_INSTR.format(vocab=vocab)
                for key, i in keyed:
                    body += f"\n=== ITEM item={key} field={i['field']} ===\n{i['held_text']}\n"
            else:   # one-item tasks: the item carries its whole prompt
                (key, i), = keyed
                body = i["prompt_text"]
                digests = i["prompt_digests"] + digests
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


def reasks_of(recs: list[dict], src: dict) -> list[dict]:
    """The re-asks OF `src`: RAN_OK records of the same prompt whose purpose names src, asked of the SAME model. A call
    to a different model on the same prompt is a second reader, never a measure of this model's stability."""
    return [r for r in recs if r["state"] == "RAN_OK"
            and str(r["caller"].get("purpose", "")).startswith(STABILITY_PURPOSE + src["record_id"])
            and r["model"]["id_reported"] == src["model"]["id_reported"]]


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
    if task in RETIRED_TASKS:
        sys.exit(f"refused: {task} is retired")
    from reproducible_ai import model_call_live
    items = pilot_items(task)
    have = _records_by_prompt()
    todo = [b for b in batches(task, items)
            if (source_record(have.get(_sha(b["prompt"]), [])) or {}).get("state") != "RAN_OK"]
    print(f"{task}: {len(todo)} batches without a RAN_OK record; running {min(limit, len(todo))}", flush=True)
    for b in todo[:limit]:
        rec = model_call_live.call(b["prompt"], schema=_schema(task), model=MODEL_BY_TASK.get(task, MODEL), effort=EFFORT,
                                   caller={"file": "scripts/model_source_pilot.py", "line": "cmd_run",
                                           "purpose": f"{task} proposals, batch {b['batch']} ({len(b['keyed'])} items)"},
                                   input_digests=b["digests"])
        path = ms.write_record(rec, REC_DIR)
        print(f"{b['batch']}: {rec['state']} model={rec['model']['id_reported']} -> {path.name}"
              + (f" ERROR {rec.get('error','')[:200]}" if rec["state"] != "RAN_OK" else ""), flush=True)


def decision_of(task: str, claim, verification: dict):
    """What a re-ask must reproduce for the proposal to count as stable: the DERIVED decision, not the wording."""
    if task in ("regex_label", "regex_label_reader2", "site_label", "site_label_v2", "site_label_v2_reader2", "site_label_ol",
                "regex_label_deep", "site_label_deep", "regex_label_deep_reader2", "site_label_deep_reader2",
                "site_label_ol2", "site_label_deep2", "site_label_ol_reader2", "site_label_ol2_reader2", "site_label_deep2_reader2"):
        return verification.get("label")
    if task in ("comparator_k", "comparator_k_reader2"):
        return [(claim or {}).get("state"), verification.get("k")]
    if task in SCREEN_TASKS:
        return verification.get("model_decision")
    if task == "estimand":
        return (claim or {}).get("value")
    if task == "outcome_identity":
        return (claim or {}).get("is_match")
    if task == "locate":
        return [(claim or {}).get("is_target_outcome"), (claim or {}).get("population_matches")]
    return None


CONTEXT_KEYS = ("rule_id", "rule_reason", "field", "rule_state", "rule_value", "rule_decision_at_freeze", "prior",
                "pattern", "sample")


def queue_context(i: dict) -> dict:
    return {k: i[k] for k in CONTEXT_KEYS if k in i}


def cmd_queue(task):
    items = pilot_items(task)
    have = _records_by_prompt()
    qpath = Q_DIR / f"{task}.json"
    old = {e["item_id"]: e for e in json.loads(qpath.read_text(encoding="utf-8"))["items"]} if qpath.exists() else {}
    entries = {i["item_id"]: {"item_id": i["item_id"], "task": task, "state": i["state"], "held_ref": i["held_ref"]}
               for i in items if "held_text" not in i}
    for b in batches(task, items):
        recs_of_prompt = have.get(_sha(b["prompt"]), [])
        rec = source_record(recs_of_prompt)
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
            # ONE context object: what the verifier reads now is exactly what the queue stores for the gate to re-read
            ctx = queue_context(i)
            ver = ms.reverify({"task": task, "claim": claim, "rule_decision": i["rule_decision"], "context": ctx}, i["held_text"])
            e = ms.queue_entry(task=task, item_id=i["item_id"], record=rec, claim=claim, verification=ver,
                               held_ref=i["held_ref"], held_sha256=i["held_sha256"], rule_decision=i["rule_decision"],
                               context=ctx, response_item=key)
            reasks = reasks_of(recs_of_prompt, rec)
            if reasks:
                decs = [decision_of(task, claim, ver)]
                for r in reasks:
                    try:
                        c2 = ms.claim_for_item(ms.extract_claim(task, ms.replay(r)), key)
                        v2 = ms.reverify({"task": task, "claim": c2, "rule_decision": i["rule_decision"], "context": ctx},
                                         i["held_text"])
                        decs.append(decision_of(task, c2, v2))
                    except (ValueError, ms.ReplayRefused):
                        decs.append("UNREADABLE")
                same = len({json.dumps(d, sort_keys=True) for d in decs}) == 1
                e["reask"] = {"records": [r["record_id"] for r in reasks], "decisions": decs, "same_derived_decision": same}
                if not same:
                    e["individual_signature_required"] = True
            prev = old.get(i["item_id"])
            if prev and prev.get("record_id") == rec["record_id"] and isinstance(prev.get("reviewer_countersignature"), dict):
                e["reviewer_countersignature"] = prev["reviewer_countersignature"]   # carried, never created
            e["rendered_sha256"] = __import__("harness.result_changes", fromlist=["x"]).rendered_sha256(ms.render_proposal_block(e, rec))
            entries[i["item_id"]] = e
    doc = {"task": task, "N": len(items), "N_name": N_NAME[task],
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


def contested_batches(task: str) -> list[dict]:
    """TRIAGE sample (outcome-dependent, so never quoted as a stability RATE): the batches holding at least one item
    whose queued proposal is routed to an individual signature."""
    q = json.loads((Q_DIR / f"{task}.json").read_text(encoding="utf-8"))
    hot = {e["item_id"] for e in q["items"] if e.get("status") == "PROPOSED" and ms.individual_required(e, e.get("verification") or {})}
    return [b for b in batches(task, pilot_items(task)) if any(i["item_id"] in hot for _, i in b["keyed"])]


def cmd_stability(task: str, k: int, only_contested: bool = False):
    """Re-ask the model the IDENTICAL prompt bytes for a deterministic sample of batches. Each re-ask is its own
    committed record (caller purpose 'stability re-ask of <source record id>'); none can become a proposal source."""
    from reproducible_ai import model_call_live
    have = _records_by_prompt()
    for b in (contested_batches(task) if only_contested else stability_sample(task, k)):
        recs = have.get(_sha(b["prompt"]), [])
        src = source_record(recs)
        if not src or src["state"] != "RAN_OK":
            print(f"{b['batch']}: no RAN_OK source record; not re-asked", flush=True)
            continue
        if any(str(r["caller"].get("purpose", "")).startswith(STABILITY_PURPOSE + src["record_id"]) and r["state"] == "RAN_OK"
               for r in recs):
            print(f"{b['batch']}: already re-asked", flush=True)
            continue
        # the re-ask must ask the SAME model the source call asked: the one recorded, not the pilot default
        rec = model_call_live.call(b["prompt"], schema=_schema(task), model=src["model"]["id_requested"], effort=EFFORT,
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
        again = reasks_of(recs, src) if src else []
        if not src or src["state"] != "RAN_OK" or not again:
            continue
        a, c = _claims(src, b["keyed"]), _claims(again[0], b["keyed"])
        for key, i in b["keyed"]:
            x, y = a.get(i["item_id"]), c.get(i["item_id"])
            row = {"item_id": i["item_id"], "source_record": src["record_id"], "reask_record": again[0]["record_id"],
                   "identical_claim": x == y}
            if x is not None and y is not None:
                vs = [ms.reverify({"task": task, "claim": c_, "rule_decision": i["rule_decision"],
                                   "context": queue_context(i)}, i["held_text"]) for c_ in (x, y)]
                decs = [decision_of(task, c_, v_) for c_, v_ in zip((x, y), vs)]
                row["same_derived_decision"] = decs[0] == decs[1]
                row["decisions"] = decs
                if task in SCREEN_TASKS:
                    row["axes_same_verdict"] = sum(1 for ax in ms.SCREEN_AXES if ((x.get("axes") or {}).get(ax) or {}).get("verdict")
                                                   == ((y.get("axes") or {}).get(ax) or {}).get("verdict"))
            rows.append(row)
    n = len(rows)
    summary = {"task": task, "N": n, "N_name": "items whose batch has a source call AND a re-ask of the identical prompt bytes",
               "identical_claim": sum(r["identical_claim"] for r in rows),
               "same_derived_decision": sum(bool(r.get("same_derived_decision")) for r in rows)}
    if task in SCREEN_TASKS:
        summary["axis_verdicts_same"] = sum(r.get("axes_same_verdict", 0) for r in rows)
        summary["axis_verdicts_N"] = 4 * n
    summary["what_this_measures"] = ("whether the MODEL reproduces its own answer to identical prompt bytes; the recorded "
                                     "call replays byte-identically regardless -- that is the only reproducibility claimed")
    return {"summary": summary, "rows": rows}


def cmd_stability_report(task: str):
    rep = stability_report(task)
    out = ROOT / "outputs" / "model_source" / f"STABILITY_{task}.json"
    out.write_bytes((json.dumps(rep, indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii"))
    print(json.dumps(rep["summary"], indent=1))


# ------------------------------------------------------------------------------------------------------ two readers
READER_PAIRS = {"screening": "screening_reader2", "screening_excluded": "screening_excluded_reader2",
                "screening_excluded_x1": "screening_excluded_x1_reader2"}


def readers_report(source: str = "screening") -> dict:
    """Reader 1 (`source` queue) vs reader 2 (its _reader2 queue), item by item, from committed queues only.
    A TRIAGE for the human, not a decision: every one of these items still needs an individual signature.
    `both_against_rule` lists the items BOTH readers decide against the rule (INELIGIBLE against an include, or
    ELIGIBLE against an exclusion)."""
    q1p = Q_DIR / f"{source}.json"
    q1 = {e["item_id"]: e for e in json.loads(q1p.read_text(encoding="utf-8"))["items"]} if q1p.exists() else {}
    q2p = Q_DIR / f"{READER_PAIRS[source]}.json"
    q2 = {e["item_id"]: e for e in json.loads(q2p.read_text(encoding="utf-8"))["items"]} if q2p.exists() else {}
    rows = []
    for iid, e2 in sorted(q2.items()):
        e1 = q1.get(iid) or {}
        d1 = (e1.get("verification") or {}).get("model_decision")
        d2 = (e2.get("verification") or {}).get("model_decision")
        rows.append({"item_id": iid, "rule": e1.get("rule_decision"), "reader1": d1, "reader2": d2,
                     "reader2_state": e2.get("state", "PROPOSED"),
                     "reader1_record": e1.get("record_id"), "reader2_record": e2.get("record_id")})
    from collections import Counter
    pairs = Counter(f"{r['reader1']} / {r['reader2']}" for r in rows)
    against = {"include": "INELIGIBLE", "exclude": "ELIGIBLE"}
    both = [r["item_id"] for r in rows if r["reader1"] == r["reader2"] == against.get(r["rule"])]
    # ROBUST: every recorded call -- both readers, each source call AND its re-ask -- decides against the rule.
    # A single call per reader is not enough: on hard items reader 2 reproduces its own decision only ~80-86%.
    robust = []
    for iid in both:
        d1 = (q1[iid].get("reask") or {}).get("decisions") or []
        d2 = (q2[iid].get("reask") or {}).get("decisions") or []
        want = against.get(q1[iid].get("rule_decision"))
        if len(d1) >= 2 and len(d2) >= 2 and all(d == want for d in d1 + d2):
            robust.append(iid)
    return {"summary": {"source": source, "N": len(rows),
                        "N_name": "items whose reader-1 proposal needs an individual signature",
                        "reader1_model": MODEL, "reader2_model": MODEL_BY_TASK[READER_PAIRS[source]],
                        "same_vendor": True,
                        "pairs_reader1_reader2": dict(sorted(pairs.items())),
                        "both_readers_against_the_rule": len(both),
                        "robust_against_the_rule_all_recorded_calls": len(robust),
                        "note": "two models of ONE vendor (OpenAI via codex): partially independent at best. Agreement "
                                "orders the human's reading; it signs nothing and admits nothing."},
            "both_against_rule": both, "robust_against_rule": robust,
            "both_ineligible": both if source == "screening" else [], "rows": rows}


def contested_agreements() -> dict:
    """Keyword exclusions where reader 1 AGREED with the rule but reader 2 (screening_excluded_agree_reader2) reads the
    record ELIGIBLE: the misses no other queue can show. Triage only; each needs an individual signature."""
    from collections import Counter
    q1p, q2p = Q_DIR / "screening_excluded.json", Q_DIR / "screening_excluded_agree_reader2.json"
    if not (q1p.exists() and q2p.exists()):
        return {"summary": {"state": "NOT_YET_RUN"}, "contested": []}
    q1 = {e["item_id"]: e for e in json.loads(q1p.read_text(encoding="utf-8"))["items"]}
    q2 = json.loads(q2p.read_text(encoding="utf-8"))["items"]
    pairs = Counter((e.get("verification") or {}).get("model_decision", e.get("state")) for e in q2)
    contested = sorted(e["item_id"] for e in q2 if (e.get("verification") or {}).get("model_decision") == "ELIGIBLE")
    robust = [i for i in contested
              if all(d == "ELIGIBLE" for d in ((next(x for x in q2 if x["item_id"] == i).get("reask") or {}).get("decisions") or ["-"]))
              and (next(x for x in q2 if x["item_id"] == i).get("reask") or {}).get("decisions")]
    return {"summary": {"N": len(q2), "N_name": "keyword exclusions reader 1 agreed with", "reader2": dict(pairs),
                        "contested_reader2_ELIGIBLE": len(contested),
                        "contested_and_stable_on_reask": len(robust),
                        "by_topic": dict(Counter(i.split("::")[0] for i in contested).most_common())},
            "contested": contested, "contested_stable": robust,
            "reader1_rule_ids": {i: (q1.get(i) or {}).get("context", {}).get("rule_id") for i in contested}}


def cmd_readers(source: str = "screening"):
    if source == "screening_excluded_agree_reader2":
        rep = contested_agreements()
        out = ROOT / "outputs" / "model_source" / "CONTESTED_AGREEMENTS.json"
        out.write_bytes((json.dumps(rep, indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii"))
        print(json.dumps(rep["summary"], indent=1))
        return
    rep = readers_report(source)
    out = ROOT / "outputs" / "model_source" / f"READERS_{source}.json"
    out.write_bytes((json.dumps(rep, indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii"))
    print(json.dumps(rep["summary"], indent=1))


# ------------------------------------------------------------------------------------------------------ adjudicator
def adjudicator_report() -> dict:
    """The served pages render an UNRECORDED adjudicator's flags (cache/<slug>/screen_adjudication.json, advisory).
    Every record it judged also has a RECORDED reader-1 proposal (screening + excluded + X1 cover every screened
    record on the committed pages). Compare them, from committed files only; nothing is called or changed."""
    from collections import Counter
    q = {}
    for t in ("screening", "screening_excluded", "screening_excluded_x1"):
        p = Q_DIR / f"{t}.json"
        if p.exists():
            for e in json.loads(p.read_text(encoding="utf-8"))["items"]:
                q[e["item_id"]] = e
    rows, missing = [], []
    for p in sorted((ROOT / "cache").glob("*/screen_adjudication.json")):
        slug = p.parent.name
        rev = json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))
        idtype = {str(r["id"]): r.get("id_type") for r in (rev.get("screening") or {}).get("records") or []}
        for rid, j in (json.loads(p.read_text(encoding="utf-8")).get("judgments") or {}).items():
            key = f"{slug}::{idtype.get(str(rid))}:{rid}"
            e = q.get(key)
            if e is None or "verification" not in e:
                missing.append(key)
                continue
            rows.append({"item_id": key, "rule": e.get("rule_decision"),
                         "adjudicator_unrecorded": "ELIGIBLE" if j.get("is_eligible") is True else "INELIGIBLE",
                         "recorded_reader": e["verification"].get("model_decision"), "record_id": e.get("record_id")})
    pairs = Counter(f"{r['adjudicator_unrecorded']} / {r['recorded_reader']}" for r in rows)
    opposed = [r["item_id"] for r in rows if {r["adjudicator_unrecorded"], r["recorded_reader"]} == {"ELIGIBLE", "INELIGIBLE"}]
    return {"summary": {"N": len(rows) + len(missing), "matched": len(rows), "not_matched": missing,
                        "pairs_adjudicator_recorded": dict(sorted(pairs.items())), "opposed": len(opposed),
                        "note": "the adjudicator's judgments carry no prompt, no response and no model id ('adjudicator'); "
                                "the recorded reader's do. Advisory on the served pages; nothing here changes them."},
            "opposed": opposed, "rows": rows}


def cmd_adjudicator():
    rep = adjudicator_report()
    out = ROOT / "outputs" / "model_source" / "ADJUDICATOR_VS_RECORDED.json"
    out.write_bytes((json.dumps(rep, indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii"))
    print(json.dumps(rep["summary"], indent=1))


# ------------------------------------------------------------------------------------------------------ signing guide
def signing_guide() -> str:
    """What waits for the reviewer, in priority order, computed from the committed queues (never hand-counted)."""
    def load(task):
        p = Q_DIR / f"{task}.json"
        return json.loads(p.read_text(encoding="utf-8"))["items"] if p.exists() else []

    def open_(e):
        return "claim" in e and (e.get("reviewer_countersignature") or {}).get("state") == "OPEN"

    lines = ["# What waits for your signature (generated by `model_source_pilot.py signing-guide`)", "",
             "Nothing below changes a served number when signed: a countersigned proposal is review material "
             "(`admits_into_build: false`). Sign with `python scripts/countersign_model_proposal.py sign <task> <item_id> "
             "--by \"...\" --basis \"...\"`; `sign-batch` signs only what the gate allows in a batch.", ""]
    served = [(t, e) for t in ("outcome_identity", "locate") for e in load(t) if open_(e)]
    dis = [(t, e) for t, e in served if "DISAGREE" in e["verification"].get("agreement", "")]
    lines += ["## 1. Served-path judgments re-made as recorded calls (disagreements with the unrecorded original first)", ""]
    for t, e in dis + [x for x in served if x not in dis]:
        lines.append(f"- `{t}` `{e['item_id']}` -- {e['verification'].get('agreement')} "
                     f"({'INDIVIDUAL' if ms.individual_required(e, e['verification']) else 'batchable'})")
    r = readers_report() if (Q_DIR / "screening_reader2.json").exists() else {"both_ineligible": []}
    lines += ["", f"## 2. Screening: both readers INELIGIBLE against the rule's include ({len(r['both_ineligible'])})", ""]
    lines += [f"- `screening` `{i}`" for i in r["both_ineligible"]]
    scr = [e for e in load("screening") if open_(e)]
    ind = [e for e in scr if ms.individual_required(e, e["verification"])]
    lines += ["", f"## 3. Screening: the rest needing an individual signature ({len(ind) - len(r['both_ineligible'])} "
              f"more; {len(ind)} of {len(scr)} open in all)", "",
              "Packet: `outputs/model_source/screening_individual_signature_required.html`; reader 2's view of each: "
              "`outputs/model_source/READERS_screening.json`.", "",
              f"## 4. Batch-signable agreements ({len(scr) - len(ind)} screening; "
              f"{sum(1 for e in load('estimand') if open_(e) and not ms.individual_required(e, e['verification']))} estimand)", "",
              "`python scripts/countersign_model_proposal.py sign-batch screening --by \"...\" --basis \"...\" --batch <id>` -- "
              "refuses, by construction, every item whose verdict disagrees or whose re-ask did not reproduce.", ""]
    for task, what in (("screening_excluded", "a KEYWORD rule"), ("screening_excluded_x1", "X1 (not an RCT)")):
        exc = [e for e in load(task) if open_(e)]
        if not exc:
            continue
        flip = [e for e in exc if e["verification"].get("model_decision") == "ELIGIBLE"]
        read2 = (Q_DIR / f"{READER_PAIRS[task]}.json").exists()
        rr = readers_report(task) if read2 else {"both_against_rule": [], "robust_against_rule": []}
        both, robust = set(rr["both_against_rule"]), set(rr["robust_against_rule"])
        flip.sort(key=lambda e: (e["item_id"] not in robust, e["item_id"] not in both, e["item_id"]))
        second = (f"both readers ELIGIBLE: {len(both)}; ROBUST (both readers, source and re-ask, all 4 calls): "
                  f"{len(robust)} -- robust first" if read2
                  else "reader 2 NOT YET RUN on these -- no second reading, which is not the same as zero")
        lines += [f"## 5{'a' if task == 'screening_excluded' else 'b'}. Records excluded by {what} that the model reads "
                  f"as ELIGIBLE ({len(flip)} of {len(exc)}; {second})", ""]
        lines += [f"- {'**robust** ' if e['item_id'] in robust else ('both readers ' if e['item_id'] in both else '')}"
                  f"`{task}` `{e['item_id']}` (rule {e.get('context', {}).get('rule_id')})" for e in flip]
        lines.append("")
    est = [e for e in load("estimand") if open_(e) and ms.individual_required(e, e["verification"])]
    lines += [f"## 6. Estimand fields needing an individual signature ({len(est)})", ""]
    lines += [f"- `estimand` `{e['item_id']}` -- {e['verification'].get('agreement')}" for e in est]
    return "\n".join(lines) + "\n"


def cmd_signing_guide():
    out = ROOT / "outputs" / "model_source" / "SIGNING_GUIDE.md"
    out.write_bytes(signing_guide().encode("utf-8"))
    print(f"wrote {out.relative_to(ROOT).as_posix()}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["items", "freeze", "run", "queue", "status", "stability", "stability-report", "readers", "signing-guide", "adjudicator"])
    ap.add_argument("--base", help="freeze: the commit the population is selected from")
    ap.add_argument("task", choices=TASKS)
    ap.add_argument("--limit", type=int, default=10 ** 6)
    ap.add_argument("--sample", type=int, default=10, help="stability: how many batches to re-ask")
    ap.add_argument("--only-contested", action="store_true",
                    help="stability: re-ask only batches holding an item routed to an individual signature (triage)")
    a = ap.parse_args(argv)
    {"items": lambda: cmd_items(a.task), "run": lambda: cmd_run(a.task, a.limit),
     "queue": lambda: cmd_queue(a.task), "status": lambda: cmd_status(a.task),
     "freeze": lambda: cmd_freeze(a.task, a.base or sys.exit("freeze needs --base <commit>")),
     "stability": lambda: cmd_stability(a.task, a.sample, a.only_contested),
     "stability-report": lambda: cmd_stability_report(a.task),
     "readers": lambda: cmd_readers(a.task), "signing-guide": cmd_signing_guide, "adjudicator": cmd_adjudicator}[a.cmd]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
