"""D11 REPRODUCIBLE-AI SIGN-OFF of RoB 2 and GRADE (decision 7 Oct, Mahmood: sign-off by reproducible AI; open sources
only). For every SERVED trial x outcome of the active G1 topics (not abandoned under G1-ABANDON-v1):

  RoB 2   two INDEPENDENT recorded Codex readers (A gpt-6-astra, B gpt-5.5) judge each RoB 2 domain (D1-D5; effect of
          assignment) for that trial and outcome, each judgement with a verbatim quote from a named OPEN source shown in
          the prompt: the trial's PubMed abstract and its ClinicalTrials.gov registry record (US public domain, read from
          the AACT snapshot). A CC-licensed full text would be added when held (none is held for these trials today).
          A quote is VERIFIED only when it is found in the very source text it names (the same bytes shown); otherwise
          the domain is UNVERIFIED (treated as cannot_tell, the problem recorded). The overall is DERIVED by the RoB 2
          algorithm, never taken from a model. An adjudicator (gpt-6-astra, effort high) reads every domain where the
          two readers' verified judgements differ.
  GRADE   per served outcome, the same panel rates the five GRADE domains (downgrade 0/1/2 with a verbatim quote from
          a named source: the pooled result, the per-trial effects, the panel's own RoB 2 finals, the registry
          census text, the trials' abstracts); certainty is DERIVED (high minus downgrades).
  Agreement Cohen's kappa reader A vs B, and Codex final vs the RULE ratings (cache/<slug>/rob2.json -- primary outcome
          only, domains D1/D2/D4/D5; review.json grade -- primary outcome, assessed domains only). Every decided
          disagreement is a FINDING; a page change is drafted as an UNSIGNED notice for Mahmood, never applied here.

  python scripts/g1_d11_rob_grade.py --build                 (local: AACT + caches -> items, outside the tree)
  python scripts/g1_d11_rob_grade.py --run rob|grade [--shard i/n] [--workers 5]
  python scripts/g1_d11_rob_grade.py --derive                -> outputs/d11/D11_SIGNOFF.json + .md + NOTICES_DRAFT.md
Items (the source texts shown) live in MH_D11_ITEMS (a directory outside the tree); each source's sha256 is recorded
in every call's input digests and in the committed outputs.
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from reproducible_ai import model_source as ms  # noqa: E402

OUT = ROOT / "outputs" / "d11"
REC_DIR = ROOT / ms.RECORD_DIR
ITEMS = Path(os.environ.get("MH_D11_ITEMS", str(Path.home() / "mh-d11-items")))
IDX = OUT / "records_index.json"
MODEL_A, MODEL_B, MODEL_ADJ = "gpt-6-astra", "gpt-5.5", "gpt-6-astra"
LANE = "d11-rob-grade"
DOMAINS = ("D1_randomisation", "D2_deviations", "D3_missing_outcome_data", "D4_outcome_measurement",
           "D5_selective_reporting")
LEVELS = ("low", "some_concerns", "high", "cannot_tell")
GDOMAINS = ("risk_of_bias", "inconsistency", "imprecision", "indirectness", "publication_bias")
B_HEADER = "INDEPENDENT READER. Other readers assess this trial; you do not see their assessment.\n\n"


def _sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()


def _j(p):
    return json.load(open(p, encoding="utf-8"))


# ---------------------------------------------------------------- build (local: needs AACT + caches)

def active_topics():
    ab = set(_j(ROOT / "outputs" / "k_gap" / "g1_abandon_rank.json")["abandon"])
    return sorted(s for s in os.listdir(ROOT / "docs" / "reviews")
                  if (ROOT / "docs" / "reviews" / s / "review.json").exists() and s not in ab)


def registry_texts(ncts, aact):
    """{nct: the ClinicalTrials.gov record from the AACT snapshot as labelled plain text (public domain)}; one pass
    over each table for all trials."""
    want = {n.upper() for n in ncts if n}
    tabs = {}
    for name in ("studies", "designs", "brief_summaries", "design_outcomes", "drop_withdrawals"):
        tabs[name] = {}
        for r in aact._iter_rows(aact._table(name)):
            n = (r.get("nct_id") or "").upper()
            if n in want:
                tabs[name].setdefault(n, []).append(r)
    att = aact.attrition(sorted(want))
    out = {}
    for n in want:
        rows = {k: (tabs[k].get(n) or [None])[0] for k in ("studies", "designs", "brief_summaries")}
        txt = _registry_text(n, rows, tabs["design_outcomes"].get(n) or [], tabs["drop_withdrawals"].get(n) or [], att.get(n))
        if txt:
            out[n] = txt
    return out


def _registry_text(nct, rows, outs, drops, att):
    if not rows.get("studies"):
        return None
    s, d = rows["studies"], rows.get("designs") or {}
    L = [f"NCT number: {nct}", f"Official title: {s.get('official_title') or s.get('brief_title')}",
         f"Study type: {s.get('study_type')}; phase: {s.get('phase')}; overall status: {s.get('overall_status')}",
         f"Enrollment: {s.get('enrollment')} ({s.get('enrollment_type')})",
         f"First submitted: {s.get('study_first_submitted_date')}; start date: {s.get('start_date')}; primary completion "
         f"date: {s.get('primary_completion_date')}; results first submitted: {s.get('results_first_submitted_date')}",
         f"Allocation: {d.get('allocation')}; intervention model: {d.get('intervention_model')}; primary purpose: "
         f"{d.get('primary_purpose')}",
         f"Masking: {d.get('masking')}; masked roles: subject={d.get('subject_masked')}, caregiver={d.get('caregiver_masked')}, "
         f"investigator={d.get('investigator_masked')}, outcomes assessor={d.get('outcomes_assessor_masked')}"]
    for o in outs:
        L.append(f"Registered {o.get('outcome_type')} outcome: {o.get('measure')} | time frame: {o.get('time_frame')}"
                 + (f" | {o.get('description')}" if o.get("description") else ""))
    agg = {}
    for r in drops:
        k = (r.get("result_group_id") or r.get("ctgov_group_code") or "?", r.get("reason") or "?")
        try:
            agg[k] = agg.get(k, 0) + int(float(r.get("count") or 0))
        except ValueError:
            pass
    for (g, why), n in sorted(agg.items()):
        L.append(f"Participant flow, withdrawal (group {g}): {why}: {n}")
    if att:
        L.append(f"Participant flow summary: overall attrition {att.get('overall_pct')}%, between-arm differential "
                 f"{att.get('differential_pct')}%, (started, completed) by group {att.get('groups')}")
    if (rows.get("brief_summaries") or {}).get("description"):
        L.append("Brief summary: " + " ".join(rows["brief_summaries"]["description"].split()))
    return "\n".join(L)


def build():
    from harness import aact
    fti = _j(ROOT / "outputs" / "k_gap" / "fulltext_index.json")
    rob_items, grade_items, src_store = [], [], {}
    snap = os.path.basename(aact.snapshot_dir() or "")
    all_ncts = set()
    for slug in active_topics():
        rev = _j(ROOT / "docs" / "reviews" / slug / "review.json")
        recs = {str(r["id"]): r for r in _j(ROOT / "cache" / slug / "records.json").get("records", [])}
        for o in rev.get("outcomes") or []:
            for t in o.get("trials") or []:
                pid = str(t.get("id", "")).replace("PMID ", "")
                all_ncts.add(((recs.get(pid) or {}).get("nct") or (pid if pid.startswith("NCT") else "") or "").upper())
    reg = registry_texts(all_ncts - {""}, aact)
    for slug in active_topics():
        rev = _j(ROOT / "docs" / "reviews" / slug / "review.json")
        recs = {str(r["id"]): r for r in _j(ROOT / "cache" / slug / "records.json").get("records", [])}
        for o in rev.get("outcomes") or []:
            trials = [t for t in o.get("trials") or [] if t.get("effect") is not None]
            if not trials or not o.get("result"):
                continue
            okey = f"{slug}::{o['name']}"
            for t in trials:
                pid = str(t["id"]).replace("PMID ", "")
                rec = recs.get(pid) or {}
                nct = (rec.get("nct") or (pid if pid.startswith("NCT") else "") or "").upper()
                srcs = {}
                if rec.get("abstract"):
                    srcs[f"pubmed:{pid}"] = (f"Title: {rec.get('title')}\nPublication types: {', '.join(rec.get('pubtypes') or [])}\n"
                                             f"Abstract: {rec['abstract']}")
                if nct and reg.get(nct):
                    srcs[f"ctgov:{nct}"] = reg[nct]
                if (fti.get(pid) or {}).get("copy_licence") == "CC":
                    p = ROOT / "cache" / slug / f"ft_{pid}.txt"
                    if p.exists():
                        srcs[f"pmc-cc:{pid}"] = p.read_text(encoding="utf-8")
                for k, v in srcs.items():
                    src_store[k] = v
                rob_items.append({"item_id": f"{okey}::{pid}", "slug": slug, "outcome": o["name"], "primary": bool(o.get("primary")),
                                  "trial": pid, "nct": nct or None, "effect": {k: t.get(k) for k in ("effect", "ci_low", "ci_high", "scale")},
                                  "effect_source": t.get("source"), "timepoint": o.get("timepoint"), "estimand": o.get("estimand"),
                                  "sources": {k: _sha(v) for k, v in srcs.items()}})
            grade_items.append({"item_id": okey, "slug": slug, "outcome": o["name"], "primary": bool(o.get("primary")),
                                "estimand": o.get("estimand"), "timepoint": o.get("timepoint"), "kind": o.get("kind"),
                                "result": o["result"], "trials": [str(t["id"]).replace("PMID ", "") for t in trials],
                                "trial_effects": [{k: t.get(k) for k in ("id", "effect", "ci_low", "ci_high", "scale")} for t in trials],
                                "publication_bias_basis": ((rev.get("grade") or {}).get("domains", {}).get("publication_bias") or {}).get("basis")
                                if o.get("primary") else None})
    ITEMS.mkdir(parents=True, exist_ok=True)
    json.dump({"aact_snapshot": snap, "rob": rob_items, "grade": grade_items}, open(ITEMS / "items.json", "w", encoding="utf-8"), indent=1)
    json.dump(src_store, open(ITEMS / "sources.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(f"rob items {len(rob_items)}, grade items {len(grade_items)}, sources {len(src_store)} (AACT {snap})")


# ---------------------------------------------------------------- prompts

ROB_INSTR = """You are a systematic reviewer applying the Cochrane RoB 2 tool (effect of ASSIGNMENT to intervention,
intention-to-treat) to ONE trial for ONE outcome. Do not run any commands or read any files. Use only the sources below.
For each domain give a judgement -- low, some_concerns, high, or cannot_tell (the sources do not address it) -- and, for
low / some_concerns / high, ONE verbatim quote (copied exactly, 5-60 words) from ONE source that supports it, naming
that source's id exactly as written after 'SOURCE'. cannot_tell carries an empty quote and an empty source.
  D1 randomisation process: random sequence, allocation concealment, baseline balance.
  D2 deviations from intended interventions: blinding of participants and carers/personnel; ITT-type analysis.
  D3 missing outcome data: completeness of outcome data for THIS outcome (registry participant flow counts here).
  D4 measurement of the outcome: blinded/independent assessment, or an outcome not open to assessor judgement (death).
  D5 selection of the reported result: THIS outcome against the registered outcomes and the registration date.
Judge from the sources only; do not use what you may remember about the trial. Return only the JSON object.
"""

GRADE_INSTR = """You are a GRADE methodologist rating the certainty of evidence for ONE outcome of a systematic review of
randomised trials (start: high). Do not run any commands or read any files. Use only the sources below. For each GRADE
domain give a downgrade of 0, 1 or 2 levels, a one-sentence reason, and ONE verbatim quote (copied exactly, 3-60 words)
from ONE source supporting it, naming that source's id exactly as written after 'SOURCE'.
  risk_of_bias: from the per-trial RoB 2 judgements given (weighted by the trials' contribution).
  inconsistency: heterogeneity of the trial effects (I2, tau2, prediction interval, overlap of CIs); k=1 is not a reason.
  imprecision: width of the 95% CI against no effect and plausible decision thresholds; sample size / events.
  indirectness: population, intervention, comparator and outcome of the trials against the review question.
  publication_bias: registry evidence of unpublished trials; small number of trials alone is not a reason.
Judge from the sources only. Return only the JSON object.
"""


# v2 (8 Oct, memo 5 option b, approved): WRITTEN DECISION RULES per domain -- in v1 the readers agreed at kappa
# 0.00-0.37 because each supplied its own threshold for the same text (one read 'randomised' as low, the other asked for
# concealment) -- and TWO adjudicators from different model families; a disputed domain is accepted only when both agree.
ROB_RULES_V2 = """
DECISION RULES (apply them exactly; they replace your own thresholds):
  D1 low: a source states how the sequence was generated (computer / random number table / central / block or stratified
     randomisation by a central system) AND that allocation was concealed (central, web or telephone (IVRS/IWRS)
     assignment, pharmacy-controlled, sealed opaque envelopes, or a double-dummy / identical placebo supplied by sponsor
     with central allocation). some_concerns: randomisation is stated but concealment is not described. high: allocation
     was not random, alternating, or concealment was broken. A registry 'Allocation: RANDOMIZED' alone is some_concerns.
  D2 low: participants AND carers/personnel were blinded (double-blind, placebo-controlled, or masking roles listing the
     subject and the caregiver/investigator). some_concerns: open-label or blinding of personnel not stated, with no
     reported deviations. high: open-label AND deviations from the intended intervention are reported as frequent or
     unbalanced.
  D3 low: outcome data for THIS outcome are available for >= 95% of randomised participants, or the outcome is death /
     a registry-verified event with complete follow-up stated. some_concerns: 5-20% missing, or completeness not
     reported. high: > 20% missing, or missingness that differs between arms for reasons related to the outcome.
  D4 low: the outcome assessor was blinded, OR the outcome is death from any cause. some_concerns: assessor blinding not
     stated and the outcome needs judgement. high: an unblinded assessor judged a subjective outcome.
  D5 low: THIS outcome appears among the trial's registered primary or secondary outcomes AND registration
     (first submitted) precedes the primary completion date. some_concerns: the outcome is not registered, or the record
     was first submitted after the primary completion date. high: a source shows the reported result was selected
     from several (e.g. a changed primary outcome).
  cannot_tell only when no source addresses the domain at all.
"""

GRADE_RULES_V2 = """
DECISION RULES (apply them exactly):
  risk_of_bias: downgrade 1 when trials carrying most of the information (most participants) are 'some_concerns' or
     worse; 2 when most are 'high'; 0 when most are 'low'.
  inconsistency: 0 for one trial; otherwise downgrade 1 when I2 >= 50% AND the trials' confidence intervals do not all
     overlap or the prediction interval crosses no effect while the pooled estimate does not; 2 only for opposite,
     non-overlapping effects.
  imprecision: downgrade 1 when the 95% CI crosses no effect OR crosses a 25% relative effect (ratio 0.75 or 1.25; for a
     mean difference, half a standard deviation); 2 when it crosses both no effect and an appreciable benefit and harm.
  indirectness: downgrade 1 only when the trials' population, intervention, comparator or outcome differ from the
     review question in a way the sources show; 0 otherwise.
  publication_bias: downgrade 1 only when a source shows unpublished completed trials of this question; 0 otherwise.
"""
# v3 (8 Oct): three clarifications from the RoB 2 guidance, WRITTEN AFTER READING v2's outputs (stated, not hidden):
# 7-9 of v2's 9 'high' verdicts were registry fields read as something they are not -- a per-role masking Boolean read as
# an unblinded assessor in a double-blind trial, treatment discontinuation read as missing outcome data, and AACT's
# known allocation error (EMPHASIS-HF 'NON_RANDOMIZED') preferred to the abstract's 'randomly assigned'.
ROB_RULES_V3 = """
CLARIFICATIONS (they take precedence over the rules above):
  - When the registry and the trial's own report disagree on allocation or masking, the trial's own report wins (a
    registry field is a data-entry summary; a published 'randomly assigned' / 'double-blind' describes the trial).
  - A registry per-role masking flag that is false or empty does not show an unblinded assessor when the trial is
    described as double-blind / placebo-controlled; judge D4 from the trial's description and the outcome's nature.
  - Participant-flow withdrawals or treatment discontinuations are NOT missing outcome data: participants who stop the
    drug usually stay in follow-up. Judge D3 from statements about outcome ascertainment (vital status, lost to
    follow-up, complete follow-up); if none is given, D3 is some_concerns, not high.
"""
VERSION = 1


def _instr(kind):
    if kind == "rob":
        return ROB_INSTR + (ROB_RULES_V2 if VERSION >= 2 else "") + (ROB_RULES_V3 if VERSION >= 3 else "")
    return GRADE_INSTR + (GRADE_RULES_V2 if VERSION >= 2 else "")


def _schema(kind):
    if kind == "rob":
        dom = {"type": "object", "additionalProperties": False, "required": ["judgement", "quote", "source"],
               "properties": {"judgement": {"type": "string", "enum": list(LEVELS)}, "quote": {"type": "string"},
                              "source": {"type": "string"}}}
        return {"type": "object", "additionalProperties": False, "required": ["domains", "rationale"],
                "properties": {"rationale": {"type": "string"},
                               "domains": {"type": "object", "additionalProperties": False, "required": list(DOMAINS),
                                           "properties": {d: dom for d in DOMAINS}}}}
    dom = {"type": "object", "additionalProperties": False, "required": ["downgrade", "reason", "quote", "source"],
           "properties": {"downgrade": {"type": "integer", "enum": [0, 1, 2]}, "reason": {"type": "string"},
                          "quote": {"type": "string"}, "source": {"type": "string"}}}
    return {"type": "object", "additionalProperties": False, "required": ["domains"],
            "properties": {"domains": {"type": "object", "additionalProperties": False, "required": list(GDOMAINS),
                                       "properties": {d: dom for d in GDOMAINS}}}}


def _review_question(slug):
    cfg = _j(ROOT / "topics" / f"{slug}.json")
    pico = {t["id"]: t for t in _j(ROOT / "pico.json")["topics"]}.get(slug) or {}
    return "\n".join([f"Review question: {cfg.get('question')}"] + [f"{lab}: {pico[k]}" for k, lab in
                                                                       (("P", "Population"), ("I", "Intervention"), ("C", "Comparator"), ("O", "Outcome")) if pico.get(k)])


def rob_prompt(it, srcs, reader="A"):
    body = [_instr("rob"), "=== REVIEW ===", _review_question(it["slug"]), "", "=== OUTCOME ===",
            f"Outcome: {it['outcome']} (estimand {it['estimand']}; timepoint {it['timepoint']})", "", ]
    dig = [{"ref": f"topics/{it['slug']}.json + pico.json", "sha256": _sha((ROOT / "topics" / f"{it['slug']}.json").read_bytes()),
            "what": "review question and PICO"}]
    for sid in sorted(it["sources"]):
        body += [f"=== SOURCE {sid} ===", srcs[sid], ""]
        dig.append({"ref": sid + (" (PubMed record)" if sid.startswith("pubmed:") else " (ClinicalTrials.gov via AACT)"
                                  if sid.startswith("ctgov:") else " (PMC, CC licence)"), "sha256": it["sources"][sid],
                    "what": "open source text shown to the reader"})
    pb = "\n".join(body).encode("utf-8")
    if reader == "B":
        pb = B_HEADER.encode("utf-8") + pb
    return pb, dig


def adj_rob_prompt(it, srcs, va, vb, disputed):
    def fmt(v):
        return "\n".join(f"  {d}: {v['domains'].get(d, {}).get('judgement')} -- quote ({v['domains'].get(d, {}).get('source')}): "
                         f"{v['domains'].get(d, {}).get('quote')}" for d in disputed)
    pb, dig = rob_prompt(it, srcs)
    head = ("ADJUDICATOR. Two independent readers disagree on the domains listed. Read the sources yourself and give your "
            "own judgement for EVERY domain (the undisputed ones too), with quotes as instructed.\n=== READER A ===\n"
            + fmt(va) + "\n=== READER B ===\n" + fmt(vb) + "\n\n")
    return head.encode("utf-8") + pb, dig


def grade_srcs(it, rob_final, srcs):
    r = it["result"]
    res = (f"Pooled ({r.get('scale')}): k = {r.get('k')}; estimate {r.get('estimate')}; 95% CI {r.get('ci_low')} to "
           f"{r.get('ci_high')}; tau2 {r.get('tau2')}; I2 {r.get('i2')}%; Q {r.get('Q')}; prediction interval "
           f"{r.get('pi_low')} to {r.get('pi_high')}; method {r.get('ci_provenance')}")
    tr = "\n".join(f"Trial {t['id']}: {t.get('scale')} {t.get('effect')} (95% CI {t.get('ci_low')} to {t.get('ci_high')})"
                   for t in it["trial_effects"])
    rb = "\n".join(f"Trial {p}: RoB 2 overall {((rob_final.get(f'{it['item_id']}::{p}') or {}).get('overall') or 'not available')}; "
                   + "; ".join(f"{d} {v}" for d, v in ((rob_final.get(f"{it['item_id']}::{p}") or {}).get("domains") or {}).items())
                   for p in it["trials"])
    out = {"review:result": res, "review:trial_effects": tr, "d11:rob2_finals": rb}
    if it.get("publication_bias_basis"):
        out["review:registry_census"] = it["publication_bias_basis"]
    for p in it["trials"]:
        if f"pubmed:{p}" in srcs:
            out[f"pubmed:{p}"] = srcs[f"pubmed:{p}"]
    return out


def grade_prompt(it, gs, reader="A"):
    body = [_instr("grade"), "=== REVIEW ===", _review_question(it["slug"]), "", "=== OUTCOME ===",
            f"Outcome: {it['outcome']} ({it['kind']}; estimand {it['estimand']}; timepoint {it['timepoint']})", ""]
    dig = [{"ref": f"docs/reviews/{it['slug']}/review.json", "sha256": _sha((ROOT / "docs" / "reviews" / it["slug"] / "review.json").read_bytes()),
            "what": "served outcome: pooled result and per-trial effects"}]
    for sid in sorted(gs):
        body += [f"=== SOURCE {sid} ===", gs[sid], ""]
        dig.append({"ref": sid, "sha256": _sha(gs[sid]), "what": "source text shown to the reader"})
    pb = "\n".join(body).encode("utf-8")
    return (B_HEADER.encode("utf-8") + pb if reader == "B" else pb), dig


# ---------------------------------------------------------------- verification

def _norm(s):
    return " ".join(str(s or "").split()).lower()


def verify(kind, claim, shown):
    """Per domain: the judgement stands only if its quote is found in the source it NAMES (the bytes shown)."""
    doms = DOMAINS if kind == "rob" else GDOMAINS
    out, problems = {}, []
    d = (claim or {}).get("domains") or {}
    for k in doms:
        v = d.get(k) or {}
        val = v.get("judgement") if kind == "rob" else v.get("downgrade")
        if kind == "rob" and val == "cannot_tell":
            out[k] = "cannot_tell"
            continue
        src, q = v.get("source") or "", v.get("quote") or ""
        if src not in shown:
            problems.append(f"{k}: SOURCE_NOT_SHOWN {src!r}")
            out[k] = "UNVERIFIED"
            continue
        loc = ms._locate(q, shown[src]) if q.strip() else {"match": "EMPTY"}
        if loc.get("match") not in ("VERBATIM", "NORMALISED"):
            problems.append(f"{k}: QUOTE_NOT_IN_SOURCE ({src})")
            out[k] = "UNVERIFIED"
            continue
        out[k] = val
    return {"domains": out, "problems": problems}


def rob_overall(doms):
    v = [doms.get(d) for d in DOMAINS]
    if "high" in v:
        return "high"
    if any(x in ("cannot_tell", "UNVERIFIED", "UNRESOLVED", None) for x in v):
        return "some_concerns" if "some_concerns" in v else "not_determined"
    return "some_concerns" if "some_concerns" in v else "low"


def certainty(gd):
    if any(not isinstance(gd.get(d), int) for d in GDOMAINS):
        return "not_determined"
    n = 4 - sum(gd[d] for d in GDOMAINS)
    return {4: "high", 3: "moderate", 2: "low"}.get(n, "very_low")


# ---------------------------------------------------------------- calls

def _index():
    return _j(IDX) if IDX.exists() else {}


def _load(name):
    rec = ms.load_record(REC_DIR / name)
    return rec, json.loads(ms.replay(rec).decode("utf-8"))


def _call(pb, dg, model, kind, purpose, effort="medium"):
    from reproducible_ai import model_call_live
    rec = model_call_live.call(pb, schema=_schema(kind), model=model, effort=effort,
                               caller={"file": "scripts/g1_d11_rob_grade.py", "lane": LANE, "line": "call", "purpose": purpose},
                               input_digests=dg)
    return ms.write_record(rec, REC_DIR).name, rec


def _batch(todo, workers):
    idx = _index()
    with cf.ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(_call, *t): t[0] for t in todo}
        for f in cf.as_completed(futs):
            try:
                name, rec = f.result()
                if rec.get("state") == "RAN_OK":
                    idx[_sha(futs[f])] = name
                print(f"  {rec['state']} {name}", flush=True)
            except Exception as exc:  # noqa: BLE001 -- reported; the item stays uncalled
                print(f"  FAILED {exc}", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    cur = _index()
    cur.update(idx)
    json.dump(cur, open(IDX, "w", encoding="utf-8", newline="\n"), indent=0, sort_keys=True)


def _shard(xs, argv):
    if "--shard" not in argv:
        return xs
    i, n = map(int, argv[argv.index("--shard") + 1].split("/"))
    return xs[i::n]


def readers(kind, items, prompt_fn, workers, argv):
    idx = _index()
    todo = []
    for it in _shard(items, argv):
        for reader, model in (("A", MODEL_A), ("B", MODEL_B)):
            pb, dg = prompt_fn(it, reader)
            if _sha(pb) not in idx:
                todo.append((pb, dg, model, kind, f"D11 {kind} reader {reader}, {it['item_id']}"))
    print(f"{kind} readers: {len(todo)} calls", flush=True)
    _batch(todo, workers)


def panel(kind, items, prompt_fn, adj_fn, shown_fn, workers, argv, live):
    """Readers' verified verdicts, the adjudication of disputed domains, and the final per domain."""
    idx = _index()
    rows = []
    for it in items:
        row = {"item_id": it["item_id"], "slug": it["slug"]}
        shown = shown_fn(it)
        for reader in ("A", "B"):
            pb, _ = prompt_fn(it, reader)
            name = idx.get(_sha(pb))
            if name:
                _, claim = _load(name)
                row[f"reader_{reader}"] = {"record": name, "claim": claim, "v": verify(kind, claim, shown)}
        rows.append(row)
    doms = DOMAINS if kind == "rob" else GDOMAINS
    todo = []
    for it, row in zip(items, rows):
        if not (row.get("reader_A") and row.get("reader_B")):
            continue
        a, b = row["reader_A"]["v"]["domains"], row["reader_B"]["v"]["domains"]
        row["disputed"] = [d for d in doms if a.get(d) != b.get(d) or a.get(d) == "UNVERIFIED"]
        if row["disputed"]:
            base_pb, dg = adj_fn(it, row["reader_A"]["claim"], row["reader_B"]["claim"], row["disputed"])
            for key, model, seat in _seats():
                pb = (seat.encode("utf-8") + base_pb) if seat else base_pb
                name = idx.get(_sha(pb))
                if name:
                    _, claim = _load(name)
                    # THIS item's sources (a stale loop variable verified every adjudicator against the last item's;
                    # plant tests/test_d11_verifier.py::test_the_adjudicator_is_verified_against_its_own_items_sources)
                    row[key] = {"record": name, "model": model, "v": verify(kind, claim, shown_fn(it))}
                elif live and it in _shard(items, argv):
                    todo.append((pb, dg, model, kind, f"D11 {kind} {key}, {it['item_id']}", "high"))
    if live and todo:
        print(f"{kind} adjudicator: {len(todo)} calls", flush=True)
        _batch(todo, workers)
        return panel(kind, items, prompt_fn, adj_fn, shown_fn, workers, argv, False)
    for row in rows:
        if not (row.get("reader_A") and row.get("reader_B")):
            continue
        a, b = row["reader_A"]["v"]["domains"], row["reader_B"]["v"]["domains"]
        adjs = [((row.get(key) or {}).get("v") or {}).get("domains") or {} for key, _, _ in _seats()]
        fin = {}
        for d in doms:
            votes = [x.get(d) for x in adjs]
            if d not in row["disputed"]:
                fin[d] = a[d]
            elif all(v not in (None, "UNVERIFIED") for v in votes) and len(set(votes)) == 1:
                fin[d] = votes[0]                  # v2: accepted only when BOTH adjudicators (two families) agree
            else:
                fin[d] = "UNRESOLVED"
        row["final"] = fin
        row["final_overall"] = rob_overall(fin) if kind == "rob" else certainty(fin)
    return rows


def _sfx():
    return f"_v{VERSION}" if VERSION >= 2 else ""


def _seats():
    """(row key, model, prompt header): v1 one adjudicator (reader A's family); v2 two, one per model family."""
    if VERSION >= 2:
        return [("adjudicator", MODEL_ADJ, "ADJUDICATOR SEAT 1 of 2.\n"), ("adjudicator_2", MODEL_B, "ADJUDICATOR SEAT 2 of 2.\n")]
    return [("adjudicator", MODEL_ADJ, "")]


# ---------------------------------------------------------------- derive

def kappa(pairs, cats):
    pairs = [(a, b) for a, b in pairs if a in cats and b in cats]
    n = len(pairs)
    if not n:
        return None, 0
    po = sum(a == b for a, b in pairs) / n
    pe = sum((sum(a == c for a, _ in pairs) / n) * (sum(b == c for _, b in pairs) / n) for c in cats)
    return (None if pe == 1 else round((po - pe) / (1 - pe), 4)), n


RULE_MAP = {"low": "low", "some concerns": "some_concerns", "high": "high"}
RULE_DOMS = ("D1_randomisation", "D2_deviations", "D4_outcome_measurement", "D5_selective_reporting")


def main(argv):
    global VERSION
    VERSION = 3 if "--v3" in argv else 2 if "--v2" in argv else 1
    if "--build" in argv:
        return build()
    data = _j(ITEMS / "items.json")
    srcs = _j(ITEMS / "sources.json")
    workers = int(argv[argv.index("--workers") + 1]) if "--workers" in argv else 5
    rob_items, grade_items = data["rob"], data["grade"]
    rp = lambda it, r="A": rob_prompt(it, srcs, r)  # noqa: E731
    shown_rob = lambda it: {k: srcs[k] for k in it["sources"]}  # noqa: E731
    adj_rob = lambda it, ca, cb, dis: adj_rob_prompt(it, srcs, ca, cb, dis)  # noqa: E731
    live = "--run" in argv
    phase = argv[argv.index("--run") + 1] if live else None
    if live and phase == "rob":
        readers("rob", rob_items, rp, workers, argv)
    rob_rows = panel("rob", rob_items, rp, adj_rob, shown_rob, workers, argv, live and phase == "rob")
    rob_final = {r["item_id"]: {"overall": r.get("final_overall"), "domains": r.get("final")} for r in rob_rows if r.get("final")}
    gsrc = {it["item_id"]: grade_srcs(it, rob_final, srcs) for it in grade_items}
    gp = lambda it, r="A": grade_prompt(it, gsrc[it["item_id"]], r)  # noqa: E731

    def adj_g(it, ca, cb, dis):
        pb, dg = gp(it)
        fmt = lambda v: "\n".join(f"  {d}: downgrade {v['domains'].get(d, {}).get('downgrade')} -- {v['domains'].get(d, {}).get('reason')} "  # noqa: E731
                                  f"(quote, {v['domains'].get(d, {}).get('source')}: {v['domains'].get(d, {}).get('quote')})" for d in dis)
        return (("ADJUDICATOR. Two independent raters disagree on the domains listed. Rate EVERY domain yourself, with "
                 "quotes as instructed.\n=== RATER A ===\n" + fmt(ca) + "\n=== RATER B ===\n" + fmt(cb) + "\n\n").encode("utf-8")
                + pb), dg
    grade_rows = []
    if phase == "grade" or not live:
        complete = all(r.get("final") for r in rob_rows)
        if live and not complete:
            raise SystemExit("REFUSED: GRADE reads the RoB 2 finals; the RoB panel is not complete")
        if live:
            readers("grade", grade_items, gp, workers, argv)
        grade_rows = panel("grade", grade_items, gp, adj_g, lambda it: gsrc[it["item_id"]], workers, argv,
                           live and phase == "grade")
    if live:
        return 0
    derive(data, rob_items, rob_rows, grade_items, grade_rows)
    return 0


def derive(data, rob_items, rob_rows, grade_items, grade_rows):
    OUT.mkdir(parents=True, exist_ok=True)
    byid = {it["item_id"]: it for it in rob_items}
    findings, notices = [], []
    # RoB: kappa A vs B per domain; Codex final vs rule (primary outcome, rule domains)
    kab = {}
    for d in DOMAINS:
        kab[d] = kappa([(r["reader_A"]["v"]["domains"][d], r["reader_B"]["v"]["domains"][d]) for r in rob_rows
                        if r.get("reader_A") and r.get("reader_B")], ("low", "some_concerns", "high"))
    vs_rule, rule_abstains = {d: [] for d in RULE_DOMS}, {d: 0 for d in RULE_DOMS}
    for r in rob_rows:
        it = byid[r["item_id"]]
        if not r.get("final") or not it["primary"]:
            continue
        rule = (_j(ROOT / "cache" / it["slug"] / "rob2.json").get("trials") or {}).get(it["trial"])
        r["rule"] = {d: ((rule or {}).get("domains") or {}).get(d, {}).get("level") for d in DOMAINS} if rule else None
        if not rule:
            findings.append({"kind": "RULE_ROB_ABSENT", "item": r["item_id"], "codex": r["final"]})
            continue
        for d in RULE_DOMS:
            rl = RULE_MAP.get(str(r["rule"].get(d) or "").lower())
            cf_ = r["final"][d]
            if rl is None:
                rule_abstains[d] += 1
                continue
            vs_rule[d].append((rl, cf_))
            if cf_ in ("low", "some_concerns", "high") and cf_ != rl:
                dom = rule["domains"][d]
                findings.append({"kind": "ROB_DISAGREES", "item": r["item_id"], "domain": d, "rule": rl, "codex": cf_,
                                 "rule_basis": dom.get("basis"), "rule_id": dom.get("rule_id"),
                                 "readers": {x: (r[f"reader_{x}"]["claim"]["domains"][d]) for x in "AB"},
                                 "adjudicator": ((r.get("adjudicator") or {}).get("v") or {}).get("domains", {}).get(d)})
    k_rule = {d: kappa(vs_rule[d], ("low", "some_concerns", "high")) for d in RULE_DOMS}
    # kappa collapses when the rule is near-constant (it rates almost every D1 'low'): state raw agreement beside it
    agree_rule = {d: {"agree": sum(1 for a, b in vs_rule[d] if a == b), "decided": sum(1 for a, b in vs_rule[d]
                      if b in ("low", "some_concerns", "high")), "rule_levels": dict(__import__("collections").Counter(a for a, _ in vs_rule[d]))}
                  for d in RULE_DOMS}
    # the adjudicator shares a model family with reader A: how often it sided with each, and the finals under each
    # reader alone (sensitivity), so the panel's dependence on that choice is visible
    side = {"A": 0, "B": 0, "neither": 0}
    for r in rob_rows:
        for d in r.get("disputed") or []:
            if not r.get("adjudicator"):
                continue
            a, b, j = (r["reader_A"]["v"]["domains"][d], r["reader_B"]["v"]["domains"][d],
                       r["adjudicator"]["v"]["domains"][d])
            side["A" if j == a and j != b else "B" if j == b and j != a else "neither"] += 1
    import collections as _c
    sens = {"rob_overall_reader_A_only": dict(_c.Counter(rob_overall(r["reader_A"]["v"]["domains"]) for r in rob_rows if r.get("reader_A"))),
            "rob_overall_reader_B_only": dict(_c.Counter(rob_overall(r["reader_B"]["v"]["domains"]) for r in rob_rows if r.get("reader_B"))),
            "grade_reader_A_only": dict(_c.Counter(certainty(r["reader_A"]["v"]["domains"]) for r in grade_rows if r.get("reader_A"))),
            "grade_reader_B_only": dict(_c.Counter(certainty(r["reader_B"]["v"]["domains"]) for r in grade_rows if r.get("reader_B"))),
            "adjudicator_sided_with": side}
    # GRADE: Codex final vs the rule's assessed domains (primary outcome)
    g_vs = []
    for r in grade_rows:
        if not r.get("final"):
            continue
        it = next(x for x in grade_items if x["item_id"] == r["item_id"])
        if not it["primary"]:
            continue
        rg = (_j(ROOT / "docs" / "reviews" / it["slug"] / "review.json").get("grade") or {})
        r["rule"] = {"certainty": rg.get("certainty"), "domains": {d: {k: (rg.get("domains") or {}).get(d, {}).get(k)
                                                                         for k in ("assessed", "downgrade", "state")} for d in GDOMAINS}}
        for d in GDOMAINS:
            rd = (rg.get("domains") or {}).get(d) or {}
            if rd.get("assessed") and isinstance(r["final"][d], int):
                g_vs.append((str(rd.get("downgrade")), str(r["final"][d])))
                if rd.get("downgrade") != r["final"][d]:
                    findings.append({"kind": "GRADE_DISAGREES", "item": r["item_id"], "domain": d, "rule": rd.get("downgrade"),
                                     "codex": r["final"][d]})
        if r["final_overall"] != "not_determined":
            notices.append({"item": r["item_id"], "kind": "GRADE_CERTAINTY_AVAILABLE", "rule": rg.get("certainty"),
                            "codex": r["final_overall"]})
    kg = kappa(g_vs, ("0", "1", "2"))
    for f in findings:
        if f["kind"] == "ROB_DISAGREES":
            notices.append({"item": f["item"], "kind": "ROB_DOMAIN_CHANGE", "domain": f["domain"], "from": f["rule"], "to": f["codex"]})
    tally = lambda rows: {k: sum(1 for r in rows if r.get("final_overall") == k)  # noqa: E731
                          for k in sorted({r.get("final_overall") for r in rows if r.get("final_overall")})}
    out = {"schema": 1, "aact_snapshot": data["aact_snapshot"], "models": {"reader_A": MODEL_A, "reader_B": MODEL_B,
           "adjudicator": f"{MODEL_ADJ} (effort high)"}, "n_rob_items": len(rob_items), "n_grade_items": len(grade_items),
           "sensitivity": sens,
           "rob": {"kappa_A_vs_B": kab, "kappa_final_vs_rule": k_rule, "agreement_final_vs_rule": agree_rule,
                   "rule_abstains": rule_abstains,
                   "overall_final": tally(rob_rows), "adjudicated": sum(1 for r in rob_rows if r.get("adjudicator")),
                   "disputed": sum(1 for r in rob_rows if r.get("disputed")),
                   "unverified_quotes": sum(len(r[f"reader_{x}"]["v"]["problems"]) for r in rob_rows for x in "AB" if r.get(f"reader_{x}"))},
           "grade": {"kappa_A_vs_B": {d: kappa([(str(r["reader_A"]["v"]["domains"][d]), str(r["reader_B"]["v"]["domains"][d]))
                                                for r in grade_rows if r.get("reader_A") and r.get("reader_B")], ("0", "1", "2"))
                                      for d in GDOMAINS},
                     "kappa_final_vs_rule_assessed_domains": kg, "certainty_final": tally(grade_rows),
                     "adjudicated": sum(1 for r in grade_rows if r.get("adjudicator"))},
           "findings": findings, "notices_draft": notices,
           "rob_rows": [{k: v for k, v in r.items() if k != "claim"} | {f"reader_{x}": {"record": r[f"reader_{x}"]["record"], "v": r[f"reader_{x}"]["v"]}
                         for x in "AB" if r.get(f"reader_{x}")} for r in rob_rows],
           "grade_rows": [{k: v for k, v in r.items()} | {f"reader_{x}": {"record": r[f"reader_{x}"]["record"], "v": r[f"reader_{x}"]["v"]}
                           for x in "AB" if r.get(f"reader_{x}")} for r in grade_rows]}
    json.dump(out, open(OUT / f"D11_SIGNOFF{_sfx()}.json", "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    open(OUT / f"D11_SIGNOFF{_sfx()}.md", "w", encoding="utf-8", newline="\n").write(render(out))
    open(OUT / f"NOTICES_DRAFT{_sfx()}.md", "w", encoding="utf-8", newline="\n").write(render_notices(out))
    print(json.dumps({k: out[k] for k in ("n_rob_items", "n_grade_items", "rob", "grade")}, indent=1)[:3000])
    print(len(findings), "findings;", len(notices), "draft notices")


def render(o):
    r, g = o["rob"], o["grade"]
    L = ["# D11 reproducible-AI sign-off: RoB 2 and GRADE", "",
         f"Generated by scripts/g1_d11_rob_grade.py from recorded model calls. Readers {o['models']['reader_A']} and "
         f"{o['models']['reader_B']} (independent), adjudicator {o['models']['adjudicator']}. Open sources only: PubMed "
         f"abstracts and ClinicalTrials.gov records (AACT {o['aact_snapshot']}). A judgement counts only when its quote "
         f"is found in the source it names; overall RoB 2 and GRADE certainty are derived in code.", "",
         f"## RoB 2 ({o['n_rob_items']} trial x outcome items)", "",
         f"- Domains disputed between the readers on {r['disputed']} items; adjudicated {r['adjudicated']}. Reader quotes "
         f"that did not verify: {r['unverified_quotes']}.",
         f"- Overall (derived): {r['overall_final']}.", "",
         "| Domain | kappa A vs B (n) | kappa final vs rule (n) | rule abstains |", "|---|---|---|---|"]
    for d in DOMAINS:
        kr = r["kappa_final_vs_rule"].get(d)
        ag = r["agreement_final_vs_rule"].get(d)
        vs = (f"{kr[0]} ({kr[1]}); raw agreement {ag['agree']}/{ag['decided']}; rule levels {ag['rule_levels']}"
              if kr else "rule does not rate this domain")
        L.append(f"| {d} | {r['kappa_A_vs_B'][d][0]} ({r['kappa_A_vs_B'][d][1]}) | {vs} | {r['rule_abstains'].get(d, '-')} |")
    sv = o["sensitivity"]
    L += ["", f"Adjudicator (same model family as reader A) sided with A {sv['adjudicator_sided_with']['A']}, with B "
              f"{sv['adjudicator_sided_with']['B']}, neither {sv['adjudicator_sided_with']['neither']}. Sensitivity -- RoB 2 overall "
              f"under reader A alone {sv['rob_overall_reader_A_only']}, under reader B alone {sv['rob_overall_reader_B_only']}."]
    L += ["", f"## GRADE ({o['n_grade_items']} served outcomes)", "",
          f"- Sensitivity: certainty under reader A alone {sv['grade_reader_A_only']}, under reader B alone {sv['grade_reader_B_only']}.",
          f"- Certainty (derived): {g['certainty_final']}; adjudicated {g['adjudicated']}.",
          f"- kappa final vs the rule's ASSESSED domains: {g['kappa_final_vs_rule_assessed_domains']}.", "",
          "| Domain | kappa A vs B (n) |", "|---|---|"]
    for d in GDOMAINS:
        L.append(f"| {d} | {g['kappa_A_vs_B'][d][0]} ({g['kappa_A_vs_B'][d][1]}) |")
    fk = {}
    for f in o["findings"]:
        fk[f["kind"]] = fk.get(f["kind"], 0) + 1
    L += ["", f"## Findings ({len(o['findings'])}: {fk})", ""]
    for f in o["findings"]:
        if f["kind"] == "ROB_DISAGREES":
            L.append(f"- **{f['item']}** {f['domain']}: rule {f['rule']} ({f['rule_id']}; {str(f['rule_basis'])[:160]}) vs Codex "
                     f"final {f['codex']}. Reader A: {f['readers']['A'].get('judgement')} \"{str(f['readers']['A'].get('quote'))[:140]}\" "
                     f"({f['readers']['A'].get('source')}).")
        else:
            L.append(f"- **{f['item']}** {f['kind']} {f.get('domain', '')}: rule {f.get('rule')} vs Codex {f.get('codex')}.")
    return "\n".join(L) + "\n"


def render_notices(o):
    L = ["# DRAFT notices from the D11 sign-off -- UNSIGNED", "",
         "Each line is a proposed change to a served page. None is applied. Each needs Mahmood's signature before a rebuild "
         "carries it (we never sign for him).", ""]
    for n in o["notices_draft"]:
        if n["kind"] == "ROB_DOMAIN_CHANGE":
            L.append(f"- [ ] {n['item']}: RoB 2 {n['domain']} {n['from']} -> {n['to']} (recorded panel: D11_SIGNOFF.json)")
        else:
            L.append(f"- [ ] {n['item']}: GRADE certainty, served '{n['rule']}' -> panel '{n['codex']}'")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
