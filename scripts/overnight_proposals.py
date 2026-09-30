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
         "trial_identity_reader2": "gpt-5.5", "comparator_membership": "gpt-6-astra",
         "comparator_membership_reader2": "gpt-5.5", "comparator_trial_names": "gpt-6-astra",
         "comparator_trial_names_reader2": "gpt-5.5",
         # V1.0.1 round 13 (Mahmood 2026-09-29: "use codex. hard")
         "screen_eligibility": "gpt-6-astra", "screen_eligibility_reader2": "gpt-5.5",
         "d5_identity_v2": "gpt-6-astra", "d5_identity_v2_reader2": "gpt-5.5",
         "overlap_identity": "gpt-6-astra", "overlap_identity_reader2": "gpt-5.5",
         "screen_x1": "gpt-6-astra", "screen_x1_reader2": "gpt-5.5",
         "d5_adjudicate": "gpt-6-astra",
         # round 14
         "registry_measure_identity": "gpt-6-astra", "registry_measure_identity_reader2": "gpt-5.5",
         "condition_role_screen": "gpt-6-astra", "condition_role_screen_reader2": "gpt-5.5",
         "screen_population": "gpt-6-astra", "screen_population_reader2": "gpt-5.5",
         "row_binding": "gpt-6-astra", "row_binding_reader2": "gpt-5.5"}
BASE_V3 = "7ade54d0"   # round-14 populations: the served pages at round 13 (CI green, run 36626489776)
CONDROLE = ("condition_role_reader2", "condition_role_screen", "condition_role_screen_reader2")
EFFORT_BY_TASK = {"d5_adjudicate": "high"}
BASE_V2 = "834c6d83"   # round-13 populations are drawn from the served pages at round 12 (CI green, run 36599704573)
KGAP_REF = "a9b2b12b"
KGAP_SEED_REF = "e1e7d3e4"  # origin/acq/k-gap: seeding after the resolved-report fix (counterfactual_members + member_records)  # origin/acq/k-gap: outputs/k_gap/screen_audit.json (the 55 confirmed-member screening exclusions)


def base_task(task):
    if task == "d5_adjudicate":
        return "d5_identity"
    if task in ("screen_population", "screen_population_reader2"):
        return "screen_eligibility"
    t = task[:-len("_reader2")] if task.endswith("_reader2") and task != "condition_role_reader2" else task
    return t[:-len("_v2")] if t.endswith("_v2") else t
EFFORT, BATCH = "medium", 6
CODEX_LOG = Path("C:/mh-lanes/evid2-scratch/codex/codex_calls.jsonl")
QDIR = ROOT / ms.PROPOSAL_DIR

INSTR = {
    "comparator_trial_names": """You read a published meta-analysis (its text, figure captions and alt text). Our question's
primary outcome is named below. Find its analysis of THAT outcome (or the closest one it reports) and list the trials
IN that analysis by the names the text prints (acronym or first author and year).
Return: analysis {label, quote} -- words copied exactly from the text that report that analysis; trials -- one
{name, quote} per trial, where quote is words copied exactly from the text that show the trial is in that analysis and
contain the name. List only trials the text places in that analysis. Never guess.""",
    "comparator_membership": """You read a published meta-analysis (its text, figure captions and figure alt text) and the
list of ROWS of its included-trial table. Our question's primary outcome is named below. Find the meta-analysis's
analysis of THAT outcome (or the closest one it reports) and say which table rows are in it.
Return: analysis {label, quote} -- the words, copied exactly from the text, that report that analysis; members -- one
{row, quote} per table row IN that analysis, where row is the ROW id exactly as listed and quote is words copied exactly
from the text or figure text that show this trial is in that analysis; excluded -- rows you can show are NOT in it, same
form. Leave a row out of both lists when the text does not say. Never guess.""",
    "d5_identity": """Each item gives a POOLED OUTCOME and ONE outcome a trial registered. Decide whether the registered
outcome is the SAME outcome as the pooled one -- the same components, not merely a related one (a bleeding outcome is
never the same as a death/MI/stroke composite; 'death from vascular causes' counts as cardiovascular death).
verdict: SAME_OUTCOME | DIFFERENT_OUTCOME | NOT_STATED. quote: words copied exactly from the REGISTERED outcome that
show it (null for NOT_STATED).""",
    "comparator_arm": """Each item is a trial record. Decide whether the trial randomised the intervention against a
control arm of placebo, usual care, standard care / standard of care (however written: 'standard-of-care', 'SOC' once
defined), best supportive care, or no treatment. verdict: COMPARATOR_PRESENT | NO_COMPARATOR | NOT_STATED. quote: words
copied exactly from the record that show it (null for NOT_STATED).""",
    "screen_eligibility": """Each item is a trial RECORD that our screening rule EXCLUDED, with the review question, the
protocol terms, and the criterion the rule found the record does NOT meet (its own words). Decide from the RECORD alone
whether the record in fact MEETS that criterion -- e.g. the population is the one the question asks about although the
record words it differently (a synonym, an abbreviation, a broader or narrower phrase), or the comparator is present
under another name. verdict: MEETS_CRITERION | FAILS_CRITERION | NOT_STATED. quote: words copied exactly from the RECORD
that show it -- for MEETS_CRITERION the record's own words that satisfy the criterion (null for NOT_STATED). Judge the
criterion as the protocol states it; never widen the protocol.""",
    "condition_role_screen": """Each item is a trial RECORD our screening excluded because its title or registered
conditions mention the CONDITION named in the item header. Decide that condition's role in THIS trial:
ENTRY_POPULATION -- participants have it at entry (they are enrolled because of it); PREVENTED_OUTCOME -- the trial tries
to prevent it, or measures it as an outcome, in people who do not have it at entry; NOT_STATED. quote: words copied
exactly from the RECORD that show the role AND contain the condition's words (null for NOT_STATED).""",
    "registry_measure_identity": """Each item gives a review's POOLED OUTCOME and ONE outcome measure a trial reported on
ClinicalTrials.gov. Decide whether the registry measure IS the pooled outcome -- the same components (a composite is
the same composite, not one of its components and not a larger composite), not merely a related one.
verdict: SAME_OUTCOME | DIFFERENT_OUTCOME | NOT_STATED. quote: words copied exactly from the REGISTRY MEASURE that show
it (null for NOT_STATED).""",
    "row_binding": """Each item gives ONE trial as a published meta-analysis lists it (its row and the reference it cites)
and the list of OUR TRIALS (id, acronym, registrations, report titles). Say which of OUR TRIALS it is the SAME randomised
trial as (a report of it, including a secondary report), or NONE when it is none of them. family: the id exactly as
listed, or "NONE". quote: words copied exactly from the item's text that show the identity (an acronym, registration,
first author and year, or title shared by both); null for NONE. Never guess.""",
    "screen_x1": """Each item is a trial RECORD (title, abstract, publication types) that our screening rule excluded as
"not a randomized controlled trial". Decide from the RECORD alone whether it reports a trial in which participants were
RANDOMLY ALLOCATED to the compared groups (a report or sub-study of such a trial counts; a trial that only randomised
something else, or no allocation at all, does not). verdict: RANDOMISED_TRIAL | NOT_RANDOMISED | NOT_STATED. quote:
words copied exactly from the RECORD that show it (null for NOT_STATED).""",
    "overlap_identity": """Each item gives a trial as a published meta-analysis cites it (its row and the reference it
cites) and a trial in our review (its registration and report titles). Decide whether they are the SAME randomised
trial (a report of it, including a secondary or companion report), not merely a similar one.
verdict: SAME_TRIAL | DIFFERENT_TRIALS | NOT_STATED. quote: words copied exactly from the item's text that show it (an
acronym, registration number, first author and year, or title shared by both; null for NOT_STATED).""",
    "trial_identity": """Each item gives TWO rows of a meta-analysis, each with the report it cites. Decide whether the two
rows are reports of the SAME randomised trial, and if so whether one row's patients are a SUBGROUP of the other's.
verdict: SAME_TRIAL_SUBGROUP | SAME_TRIAL_SAME_POPULATION | DIFFERENT_TRIALS | NOT_STATED. quote: words copied exactly
from the item's text that show it (null for NOT_STATED).""",
}


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _show(path: str, ref: str = BASE):
    try:
        return json.loads(subprocess.check_output(["git", "-C", str(ROOT), "show", f"{ref}:{path}"],
                                                  stderr=subprocess.DEVNULL).decode("utf-8"))
    except subprocess.CalledProcessError:
        return None


def _slugs():
    return sorted(p.name for p in (ROOT / "docs" / "reviews").iterdir())


# ------------------------------------------------------------------------------------------------------ populations
def items_d5_identity(ref: str = BASE):
    from harness import rob2
    out = []
    for slug in _slugs():
        r = _show(f"docs/reviews/{slug}/review.json", ref) or {}
        for tid, t in ((r.get("rob2") or {}).get("trials") or {}).items():
            inp = ((t.get("domains") or {}).get("D5_selective_reporting") or {}).get("inputs") or {}
            if "pooled_outcome" not in inp:
                continue
            regs = [("primary", o) for o in inp.get("registered_primary_outcomes") or []] + \
                   [("secondary", o) for o in inp.get("registered_secondary_outcomes") or []]
            for j, (kind, o) in enumerate(regs):
                held = f"POOLED OUTCOME: {inp['pooled_outcome']}\nREGISTERED ({kind}): {rob2._registered_text(o)}"
                out.append({"item_id": f"{slug}::{tid}::{kind}{j}", "held_text": held, "held_sha256": _sha(held.encode()),
                            "held_ref": f"docs/reviews/{slug}/review.json@{ref}#rob2/{tid}/D5",
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
        a = comparator_analysis.assess(doc, json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8")))
        nest = comparator_nesting.assess(ROOT, slug, a, panel, []) or {"nested": []}
        pairs = {(x["parent"]["label"], x["row"]["label"]) for x in nest["nested"] if x["relation"] == "SUBGROUP_OF"}
        rows = doc["membership"]["rows"]
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                ra, rb = rows[i], rows[j]

                def txt(r):
                    ps = alias.get(r.get("panel_row") or "") or []
                    body = " ".join((held.get(p) or {}).get("text", "")[:1500] for p in ps)
                    n = f"n = {r['counts'][1] + r['counts'][3]}" if r.get("counts") else "n not plotted"
                    return f"ROW {r['label']} ({n}): {body or '(no held report)'}"
                text = txt(ra) + "\n" + txt(rb)
                rule = ("SAME_TRIAL_SUBGROUP" if (ra["label"], rb["label"]) in pairs or (rb["label"], ra["label"]) in pairs
                        else "DIFFERENT_TRIALS")
                out.append({"item_id": f"{slug}::{ra['label']}||{rb['label']}", "held_text": text,
                            "held_sha256": _sha(text.encode()), "held_ref": f"cache/{slug}/comparator_analysis.json",
                            "rule_decision": rule})
    return out


def items_comparator_membership():
    """G1: every topic whose comparator panel has an included-trial table but no membership for OUR primary outcome.
    Held text = the comparator's held full text + its figure captions and alt text (from the held JATS), so a quote
    from a forest plot's description is locatable; the rows are listed in the prompt by their panel ids."""
    import html as _h
    out = []
    for slug in _slugs():
        cp, ft = ROOT / "cache" / slug / "comparators.json", ROOT / "cache" / slug / "comparator_fulltext.txt"
        if not cp.exists() or not ft.exists() or (ROOT / "cache" / slug / "comparator_analysis.json").exists():
            continue
        panel = next(iter(json.loads(cp.read_text(encoding="utf-8"))), None) or {}
        rows = panel.get("trial_set") or []
        if len(rows) < 2:
            continue
        text = ft.read_text(encoding="utf-8")
        jx = ROOT / "cache" / slug / "comparator_pmc_jats.xml"
        if jx.exists():
            x = jx.read_text(encoding="utf-8")
            figs = []
            for m in re.finditer(r"<fig\b.*?</fig>", x, re.S):
                parts = re.findall(r"<caption>(.*?)</caption>|<alt-text[^>]*>(.*?)</alt-text>", m.group(0), re.S)
                figs += [_h.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", a or b))).strip() for a, b in parts]
            text += "\n\nFIGURE CAPTIONS AND ALT TEXT:\n" + "\n".join(f for f in figs if f)
        review = json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))
        prim = next((o for o in review.get("outcomes") or [] if o.get("primary")), {})
        listing = "\n".join(f"ROW {t['family_id']}: " + _h.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ",
                             t["span"]["quote"])))[:220] for t in rows)
        out.append({"item_id": f"{slug}::membership", "held_text": text, "held_sha256": _sha(text.encode("utf-8")),
                    "held_ref": f"cache/{slug}/comparator_fulltext.txt (+ figure captions/alt text of the held JATS)",
                    "rule_decision": "NO_RULE", "rows": [t["family_id"] for t in rows],
                    "outcome": prim.get("name"), "listing": listing})
    return out


def items_comparator_trial_names():
    """G1: topics whose comparator text is held but has NO included-trial table and no bound membership."""
    import html as _h
    out = []
    for slug in _slugs():
        cp, ft = ROOT / "cache" / slug / "comparators.json", ROOT / "cache" / slug / "comparator_fulltext.txt"
        if not ft.exists() or (ROOT / "cache" / slug / "comparator_analysis.json").exists():
            continue
        panel = next(iter(json.loads(cp.read_text(encoding="utf-8"))), None) if cp.exists() else {}
        if (panel or {}).get("trial_set"):
            continue
        text = ft.read_text(encoding="utf-8")
        review = json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))
        prim = next((o for o in review.get("outcomes") or [] if o.get("primary")), {})
        out.append({"item_id": f"{slug}::trial_names", "held_text": text, "held_sha256": _sha(text.encode("utf-8")),
                    "held_ref": f"cache/{slug}/comparator_fulltext.txt", "rule_decision": "NO_RULE",
                    "outcome": prim.get("name"), "listing": "(no included-trial table)", "rows": []})
    return out


def _record_text(rec: dict) -> str:
    parts = [f"TITLE: {rec.get('title') or ''}", f"ABSTRACT: {rec.get('abstract') or ''}"]
    for k in ("pubtypes", "conditions", "interventions", "allocation", "masking", "study_type"):
        v = rec.get(k)
        if v:
            parts.append(f"{k.upper()}: {'; '.join(map(str, v)) if isinstance(v, list) else v}")
    return "\n".join(parts)


def _records_by_id(slug: str) -> dict:
    out = {}
    for v in json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8")).values():
        if isinstance(v, list):
            out.update({str(x.get("id")): x for x in v if isinstance(x, dict)})
    return out


_CRITERION_TERMS = {"X1": (), "X2": ("population_any", "population_none"), "X3": ("comparator_any", "comparator_any_extra"),
                    "X-DESIGN": ("design_double_blind",)}


def items_screen_eligibility():
    """Round 13 (screening normalisation; feeds the k-gap lane's 55-exclusion audit, origin/acq/k-gap @ KGAP_REF): every
    comparator member our screening excluded, with the rule's own reason. The held text is the RECORD only, so a quote
    can only come from it; the question, the protocol terms and the rule's reason travel in the item header."""
    audit = json.loads(subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"{KGAP_REF}:outputs/k_gap/screen_audit.json"]).decode("utf-8"))
    out = []
    for r in audit["rows"]:
        if not r.get("rule_id"):
            continue
        slug = r["slug"]
        recs = _records_by_id(slug)
        rec = next((recs[p] for p in r["pmids"] if p in recs), None)
        if not rec:
            continue
        cfg = json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))
        inc = cfg.get("include") or {}
        review = json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))
        terms = {k: inc.get(k) for k in _CRITERION_TERMS.get(r["rule_id"], ()) if inc.get(k) not in (None, [], "")}
        header = (f"QUESTION: {review.get('question') or cfg.get('question') or ''}\n"
                  f"RULE {r['rule_id']} EXCLUDED IT: {r.get('reason') or ''}\n"
                  f"PROTOCOL TERMS: {json.dumps(terms, ensure_ascii=False)}")
        held = _record_text(rec)
        out.append({"item_id": f"{slug}::{r['label']}::{rec.get('id')}", "held_text": held,
                    "held_sha256": _sha(held.encode("utf-8")), "held_ref": f"cache/{slug}/records.json#{rec.get('id')}",
                    "header": header, "rule_decision": "FAILS_CRITERION",
                    "kgap": {"ref": KGAP_REF, "class": r.get("class"), "confirmed_member": r.get("confirmed_member")}})
    return out


def items_screen_x1():
    """Round 13: every report the k-gap seeding sent to screening that X1 excluded (origin/acq/k-gap @ KGAP_SEED_REF).
    Record text from that branch's member_records.json (the records the seeding fetched; not in our caches)."""
    show = lambda p: json.loads(subprocess.check_output(  # noqa: E731
        ["git", "-C", str(ROOT), "show", f"{KGAP_SEED_REF}:outputs/k_gap/{p}"]).decode("utf-8"))
    funnel, recs = show("counterfactual_members.json"), show("member_records.json")
    out = []
    for slug in sorted(funnel):
        s = funnel[slug]
        if not isinstance(s, dict):
            continue
        for pmid, r in sorted((s.get("funnel") or {}).items()):
            if not (isinstance(r, dict) and r.get("rule_id") == "X1") or pmid not in recs:
                continue
            held = _record_text(dict(recs[pmid], id=pmid))
            out.append({"item_id": f"{slug}::{pmid}", "held_text": held, "held_sha256": _sha(held.encode("utf-8")),
                        "held_ref": f"origin/acq/k-gap@{KGAP_SEED_REF}:outputs/k_gap/member_records.json#{pmid}",
                        "rule_decision": "NOT_RANDOMISED", "kgap": {"ref": KGAP_SEED_REF, "reason": r.get("reason")}})
    return out


def items_d5_adjudicate():
    """The d5_identity_v2 items still contested after round 13: both readers against the CURRENT rule, or the two
    readers split. A third reading, never a vote that enters a build."""
    pop = json.loads((QDIR / "d5_identity_v2.population.json").read_text(encoding="utf-8"))["items"]
    r1 = {e["item_id"]: e for e in json.loads((QDIR / "d5_identity_v2.json").read_text(encoding="utf-8"))["items"]}
    r2 = {e["item_id"]: e for e in json.loads((QDIR / "d5_identity_v2_reader2.json").read_text(encoding="utf-8"))["items"]}
    dec = lambda e: (e.get("verification") or {}).get("model_decision")  # noqa: E731
    out = []
    for i in pop:
        a, b = dec(r1.get(i["item_id"], {})), dec(r2.get(i["item_id"], {}))
        if a != b or (a not in (None, "NOT_STATED") and a != rule_decision("d5_identity", i)):
            out.append(i)
    return out


def _topic_spec(slug):
    t = json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))
    s = dict(t.get("primary_outcome") or t["outcomes"][0])
    s.pop("withdrawn", None)
    return t, s


def items_registry_measure_identity():
    """Round 14: every held registry outcome measure keyword-matched to a topic's componentised primary outcome -- the
    population target_endpoint._classify decides at extraction (EXACT = the registry row may be served as the result)."""
    from harness import target_endpoint as te
    out = []
    for slug in _slugs():
        _, spec = _topic_spec(slug)
        if not te.canonical_components(spec):
            continue
        ct = json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf-8")).get("ctgov_results") or {}
        for nct, oms in sorted(ct.items()):
            for j, om in enumerate(oms or []):
                text = " ".join(str(om.get(k) or "") for k in ("title", "description")).strip()
                if not te._keyword_family_match(spec, text):
                    continue
                held = f"POOLED OUTCOME: {spec.get('name')}\nREGISTRY MEASURE ({om.get('type')}): {text}"
                out.append({"item_id": f"{slug}::{nct}::om{j}", "held_text": held, "held_sha256": _sha(held.encode("utf-8")),
                            "held_ref": f"cache/{slug}/records.json#ctgov_results/{nct}/{j}",
                            "rule_input": {"slug": slug, "text": text}})
    return out


def _x2_rows(kind):
    for slug in _slugs():
        r = _show(f"docs/reviews/{slug}/review.json", BASE_V3) or {}
        recs = _records_by_id(slug)
        for d in (r.get("screening") or {}).get("records") or []:
            if d.get("rule_id") != "X2":
                continue
            reason = str(d.get("reason") or "")
            if (kind == "mention") != reason.startswith("wrong population"):
                continue
            rid = str(d["id"]).split("·")[-1].strip()
            if rid in recs:
                yield slug, rid, recs[rid], reason


def items_condition_role_screen():
    """Round 14 (condition-as-outcome in screening): every served X2 'wrong population: title/conditions mention T'."""
    out = []
    for slug, rid, rec, reason in _x2_rows("mention"):
        m = re.search(r"mention '([^']+)'", reason)
        if not m:
            continue
        held = _record_text(rec)
        out.append({"item_id": f"{slug}::{rid}", "held_text": held, "held_sha256": _sha(held.encode("utf-8")),
                    "held_ref": f"cache/{slug}/records.json#{rid}", "term": m.group(1),
                    "rule_decision": "ENTRY_POPULATION"})
    return out


def items_screen_population():
    """Round 14: every served X2 'population not on-topic' exclusion, with the question and the population terms."""
    out = []
    for slug, rid, rec, reason in _x2_rows("absent"):
        cfg, _ = _topic_spec(slug)
        review = _show(f"docs/reviews/{slug}/review.json", BASE_V3) or {}
        inc = cfg.get("include") or {}
        terms = {k: inc.get(k) for k in ("population_any", "population_none") if inc.get(k)}
        header = (f"QUESTION: {review.get('question') or cfg.get('question') or ''}\n"
                  f"RULE X2 EXCLUDED IT: {reason[:300]}\nPROTOCOL TERMS: {json.dumps(terms, ensure_ascii=False)}")
        held = _record_text(rec)
        out.append({"item_id": f"{slug}::{rid}", "held_text": held, "held_sha256": _sha(held.encode("utf-8")),
                    "held_ref": f"cache/{slug}/records.json#{rid}", "header": header, "rule_decision": "FAILS_CRITERION"})
    return out


def items_row_binding():
    """Round 14 (comparator trial identity): every comparator member the served overlap relation bound to no family."""
    import html as _h
    out = []
    for slug in _slugs():
        r = _show(f"docs/reviews/{slug}/review.json", BASE_V3) or {}
        o = (r.get("comparator") or {}).get("overlap_relation") or {}
        th = o.get("theirs") or {}
        members = [m for m in (th.get("members") or th.get("in_scope") or []) if not m.get("family")]
        if not members:
            continue
        recs = _records_by_id(slug)
        fams = []
        for f in r.get("trial_families") or []:
            al = f.get("aliases") or {}
            ids = [str(x) for x in (al.get("report_ids") or []) + (al.get("registry_ids") or [])]
            titles = sorted({str((recs.get(i) or {}).get("title") or "")[:160] for i in ids} - {""})
            fams.append((f["family_id"], f"{f['family_id']}: acronym {al.get('acronym') or []}; registrations "
                                         f"{al.get('registry_ids') or []}; titles {titles}"))
        cited = {}
        cp = ROOT / "cache" / slug / "comparators.json"
        for t in (next(iter(json.loads(cp.read_text(encoding="utf-8"))), None) or {}).get("trial_set") or [] if cp.exists() else []:
            cited[t["family_id"]] = [_h.unescape(re.sub(r"<[^>]+>", " ", x)).strip() for a in t.get("aliases") or []
                                     for x in re.findall(r"<article-title>(.*?)</article-title>", (a.get("span") or {}).get("quote") or "", re.S)]
        ours = "\n".join(line for _, line in fams)
        for m in members:
            span = _h.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(m.get("span") or ""))))[:500]
            # the row as the comparator PRINTS it -- never its cross-referenced citation: a table's cross-references can be
            # numbered off by one (omega-3: the GISSI-HF row's reference is JELIS), which would steer the reading
            text = f"THEIR ROW {m.get('name')}: {span}\nOUR TRIALS:\n{ours}"
            out.append({"item_id": f"{slug}::{m.get('name')}", "held_text": text, "held_sha256": _sha(text.encode("utf-8")),
                        "held_ref": f"docs/reviews/{slug}/review.json@{BASE_V3}#comparator/overlap_relation",
                        "families": [fid for fid, _ in fams], "rule_decision": "UNBOUND"})
    return out


def items_d5_identity_v2():
    return items_d5_identity(BASE_V2)


def items_overlap_identity():
    """Round 13 (G1 comparator trial-identity overlap): every pair the served overlap relation decided -- each SHARED
    member against the family it was bound to (rule SAME_TRIAL), and every only-theirs member against every only-ours
    family of the same review (rule DIFFERENT_TRIALS: a missed match would hide here)."""
    import html as _h
    out = []
    for slug in _slugs():
        r = _show(f"docs/reviews/{slug}/review.json", BASE_V2) or {}
        o = (r.get("comparator") or {}).get("overlap_relation") or {}
        th = o.get("theirs") or {}
        members = th.get("members") or th.get("in_scope") or []
        if not members or o.get("relation") in (None, "NOT_ENUMERABLE"):
            continue
        fams = {f["family_id"]: f for f in r.get("trial_families") or []}
        recs = _records_by_id(slug)

        def ours(fid):
            f = fams.get(fid) or {}
            al = f.get("aliases") or {}
            ids = [str(x) for x in al.get("report_ids") or []] + [str(x) for x in al.get("registry_ids") or []]
            titles = sorted({str((recs.get(i) or {}).get("title") or "")[:200] for i in ids} - {""})
            return (f"OUR TRIAL {fid}: acronym {al.get('acronym') or []}; registrations {al.get('registry_ids') or []}; "
                    f"reports {al.get('report_ids') or []}; titles {titles}")

        cited = {}
        cp = ROOT / "cache" / slug / "comparators.json"
        for t in (next(iter(json.loads(cp.read_text(encoding="utf-8"))), None) or {}).get("trial_set") or [] if cp.exists() else []:
            cited[t["family_id"]] = [_h.unescape(re.sub(r"<[^>]+>", " ", x)).strip() for a in t.get("aliases") or []
                                     for x in re.findall(r"<article-title>(.*?)</article-title>", (a.get("span") or {}).get("quote") or "", re.S)]

        def theirs(m):
            span = _h.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(m.get("span") or ""))))[:600]
            return (f"THEIR ROW {m.get('name')}: cites {m.get('alias_ids') or []}; cited titles {cited.get(m.get('name')) or []}; "
                    f"row text: {span}")
        pairs = [(m, m["family"], "SAME_TRIAL") for m in members if m.get("family") in (o.get("shared") or [])]
        only_t = [m for m in members if m.get("name") in (o.get("only_theirs") or [])]
        pairs += [(m, fid, "DIFFERENT_TRIALS") for m in only_t for fid in o.get("only_ours") or []]
        for m, fid, rule in pairs:
            text = theirs(m) + "\n" + ours(fid)
            out.append({"item_id": f"{slug}::{m.get('name')}||{fid}", "held_text": text,
                        "held_sha256": _sha(text.encode("utf-8")),
                        "held_ref": f"docs/reviews/{slug}/review.json@{BASE_V2}#comparator/overlap_relation",
                        "rule_decision": rule})
    return out


def items_condition_role_reader2():
    pop = json.loads((QDIR / "condition_role.population.json").read_text(encoding="utf-8"))["items"]
    return [dict(i, rule_decision="ENTRY_POPULATION") for i in pop]


ITEMS = {"comparator_trial_names": items_comparator_trial_names, "comparator_membership": items_comparator_membership, "d5_identity": items_d5_identity,
         "comparator_arm": items_comparator_arm,
         "trial_identity": items_trial_identity, "condition_role_reader2": items_condition_role_reader2,
         "screen_eligibility": items_screen_eligibility, "d5_identity_v2": items_d5_identity_v2,
         "overlap_identity": items_overlap_identity, "screen_x1": items_screen_x1,
         "d5_adjudicate": items_d5_adjudicate,
         "registry_measure_identity": items_registry_measure_identity,
         "condition_role_screen": items_condition_role_screen, "screen_population": items_screen_population,
         "row_binding": items_row_binding}
for _t in ("d5_identity", "comparator_arm", "trial_identity", "comparator_membership", "comparator_trial_names",
           "screen_eligibility", "d5_identity_v2", "overlap_identity", "screen_x1", "registry_measure_identity",
           "condition_role_screen", "screen_population", "row_binding"):
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
    if task == "registry_measure_identity":
        from harness import target_endpoint as te
        _, spec = _topic_spec(i["rule_input"]["slug"])
        return ("SAME_OUTCOME" if te._classify(spec, i["rule_input"]["text"])["target_endpoint_class"] == te.EXACT_TARGET
                else "DIFFERENT_OUTCOME")
    if task == "comparator_arm":
        from harness import screen, term_normal
        return "COMPARATOR_PRESENT" if screen._has(term_normal.comparator_text(i["held_text"], i["rule_input"]["terms"]), i["rule_input"]["terms"])             else "NO_COMPARATOR"
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
    elif task in CONDROLE:
        instr = INSTR[base_task(task)]
        head = lambda i: f"CONDITION={i['term']!r}"  # noqa: E731
    else:
        instr = INSTR[base_task(task)]
        head = lambda i: ""  # noqa: E731
    size = 1 if base_task(task) in ("comparator_membership", "comparator_trial_names") else BATCH
    if base_task(task) in ("comparator_membership", "comparator_trial_names"):
        head = lambda i: f"outcome={i['outcome']!r}\nTABLE ROWS:\n{i['listing']}\n=== TEXT ==="  # noqa: E731
    if any(i.get("header") for i in items):
        head = lambda i: "\n" + i.get("header", "") + "\nRECORD:"  # noqa: E731
    for k in range(0, len(items), size):
        chunk = items[k:k + size]
        keyed = [(f"R{j + 1}", i) for j, i in enumerate(chunk)]
        prompt = instr + "".join(f"\n=== ITEM item={key} {head(i)} ===\n{i['held_text']}\n" for key, i in keyed)
        yield {"batch": k // size + 1, "keyed": keyed, "prompt": prompt.encode("utf-8"),
               "digests": [{"ref": i["held_ref"], "sha256": i["held_sha256"], "what": "held text"} for _, i in keyed]}


def _schema(task):
    if base_task(task) == "comparator_trial_names":
        tq = {"type": "object", "additionalProperties": False, "required": ["name", "quote"],
              "properties": {"name": {"type": "string"}, "quote": {"type": "string"}}}
        it = {"type": "object", "additionalProperties": False, "required": ["item", "analysis", "trials"],
              "properties": {"item": {"type": "string"},
                             "analysis": {"type": "object", "additionalProperties": False, "required": ["label", "quote"],
                                          "properties": {"label": {"type": "string"}, "quote": {"type": "string"}}},
                             "trials": {"type": "array", "items": tq}}}
        return {"type": "object", "additionalProperties": False, "required": ["items"],
                "properties": {"items": {"type": "array", "items": it}}}
    if base_task(task) == "comparator_membership":
        rq = {"type": "object", "additionalProperties": False, "required": ["row", "quote"],
              "properties": {"row": {"type": "string"}, "quote": {"type": "string"}}}
        it = {"type": "object", "additionalProperties": False, "required": ["item", "analysis", "members", "excluded"],
              "properties": {"item": {"type": "string"},
                             "analysis": {"type": "object", "additionalProperties": False, "required": ["label", "quote"],
                                          "properties": {"label": {"type": "string"}, "quote": {"type": "string"}}},
                             "members": {"type": "array", "items": rq}, "excluded": {"type": "array", "items": rq}}}
        return {"type": "object", "additionalProperties": False, "required": ["items"],
                "properties": {"items": {"type": "array", "items": it}}}
    if base_task(task) == "row_binding":
        it = {"type": "object", "additionalProperties": False, "required": ["item", "family", "quote"],
              "properties": {"item": {"type": "string"}, "family": {"type": "string"},
                             "quote": {"type": ["string", "null"]}}}
        return {"type": "object", "additionalProperties": False, "required": ["items"],
                "properties": {"items": {"type": "array", "items": it}}}
    if task in CONDROLE:
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
        rec = model_call_live.call(b["prompt"], schema=_schema(task), model=MODEL[task],
                                   effort=EFFORT_BY_TASK.get(task, EFFORT),
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
            ctx = ({"term": i["term"]} if task in CONDROLE else
                   {"families": i["families"]} if base_task(task) == "row_binding" else
                   {"rows": i["rows"]} if base_task(task) == "comparator_membership" else None)
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
