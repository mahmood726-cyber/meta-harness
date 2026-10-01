"""Safety outcome taxonomy (from the colchicine-secondary-CV review): one set of GI harm outcomes applied IDENTICALLY to every trial.

The defect it closes: a result was admitted or refused by comparing it to ONE loosely named harm ("GI adverse effects"), so the
same kind of number got opposite treatment across trials -- Akrami's 15/120 vs 3/129, which its full text labels DIARRHOEA, was
admitted as "GI adverse effects", while COLCOT's and CLEAR's diarrhoea results were refused as "narrower than GI".

The rule here:
  * four separate outcomes -- GI_ANY (any GI adverse event), DIARRHOEA, GI_HOSPITALISATION, GI_DISCONTINUATION;
  * every result is bound by its SOURCE LABEL into exactly one of them (most specific label wins; a composition note such as
    'mostly diarrhoea' does not relabel an any-GI total);
  * admission is the same test everywhere: exact per-arm counts (or an effect with its CI) are admissible; percentages alone are a
    RECONSTRUCTED candidate, never pooled, until exact counts are held; GI_ANY additionally needs a unique-patient total, because
    symptom counts can hold one patient twice and are never summed;
  * a result bound to one outcome is never used for, nor refused as 'narrower than', another.
Nothing here writes a served page: the corpus re-binding (scripts/rebind_safety_outcomes.py) turns changes into NOTICES.
"""
from __future__ import annotations

import re
from typing import Any

from harness import extract

GI_ANY, DIARRHOEA, GI_HOSPITALISATION, GI_DISCONTINUATION = "GI_ANY", "DIARRHOEA", "GI_HOSPITALISATION", "GI_DISCONTINUATION"
OUTCOMES = (GI_ANY, DIARRHOEA, GI_HOSPITALISATION, GI_DISCONTINUATION)
SPECIFICITY = (GI_DISCONTINUATION, GI_HOSPITALISATION, DIARRHOEA, GI_ANY)          # most specific first

EXACT, EFFECT_CI, RECONSTRUCTED = "EXACT_COUNTS", "EFFECT_WITH_CI", "RECONSTRUCTED"

_GI_WORD = r"(?:gastro-?intestinal|\bGI\b|digestive)"
_DIARRHOEA = re.compile(r"\bdiarrh(?:o)?ea\w*|\bdiarrh(?:o)?eal\b|\bloose stools?\b", re.I)
_HOSP = re.compile(r"hospitali[sz]\w*|admitted to hospital|hospital admission", re.I)
_DISC = re.compile(r"discontinu\w*|withdr[ae]w\w*|\bstopp\w*|left the study|drop(?:ped)?[- ]out|leading to (?:study[- ]drug )?cessation", re.I)
_INTOLERANCE = re.compile(_GI_WORD + r"[^.;]{0,40}\bintoleran\w*|\bintoleran\w*[^.;]{0,40}" + _GI_WORD, re.I)
_GI_ANY = re.compile(_GI_WORD + r"[\s-]+(?:\w+[\s-]+){0,2}?(?:adverse|side|symptom|event|effect|disorder|intoleran|complaint|discomfort|toxicit)",
                     re.I)
# a composition note ('adverse events, mostly diarrhoea') describes an any-GI total; it does not relabel it
_COMPOSITION = re.compile(r"\b(?:mostly|mainly|predominantly|primarily|chiefly|especially|particularly|including|such as|notably|"
                          r"most commonly|most often)\b[^.;]{0,25}\bdiarrh", re.I)
_NOT_IN_TAXONOMY = re.compile(r"bleed|haemorrh|hemorrh|ulcer|perforat|pancreat|hepat|liver", re.I)
_PATIENT = re.compile(r"\b(?:patients?|participants?|subjects?|individuals?|people|persons?)\b", re.I)
_EPISODES = re.compile(r"\bepisodes?\b|\b(?:number|total) of (?:events|episodes)\b|\bevents per\b", re.I)

# per-arm value tokens, most informative form first; a percentage printed inside a count token is part of that token
_TOKENS = (("of", re.compile(r"(\d[\d,]*)\s*(?:of|/|out of)\s*(\d[\d,]*)(?:\s*(?:patients|participants))?(?:\s*\(\s*\d+(?:\.\d+)?\s*%\s*\))?", re.I)),
           ("cnt", re.compile(r"(\d[\d,]*)\s*\(\s*(\d+(?:\.\d+)?)\s*%\s*\)")),
           ("pct", re.compile(r"(\d+(?:\.\d+)?)\s*%(?!\s*(?:CI|Cl|confidence|credible))")))
_ARM_CONNECTOR = re.compile(r"compared with|in compare with|versus|\bvs\b\.?|\band\b|\bwhile\b|\bwhereas\b|\bthan\b", re.I)
# a clause boundary: a pair may not straddle one (it would pair two OUTCOMES, not two arms), and a result's label is read
# only from its own clause
_CLAUSE = re.compile(r"[;:]|,\s+and\b|,\s+but\b")
_EFFECT = re.compile(r"\b(hazard ratio|risk ratio|relative risk|odds ratio|HR|RR|OR)\b[,:;\s]*(?:was\s*)?(\d+(?:\.\d+)?)\s*[;,(\s]*"
                     r"(?:95\s*%\s*(?:C[Il]|confidence interval)[,:\s]*)?(\d+(?:\.\d+)?)\s*(?:to|–|-|—)\s*(\d+(?:\.\d+)?)", re.I)


def _int(s: str) -> int:
    return int(s.replace(",", ""))


def label_outcome(label: str) -> str | None:
    """The ONE taxonomy outcome a source label names, most specific first; None when it names none (or a GI outcome the taxonomy
    does not cover, e.g. bleeding)."""
    text = label or ""
    if _NOT_IN_TAXONOMY.search(text) and not (_DIARRHOEA.search(text) or _INTOLERANCE.search(text)):
        return None
    gi_named = bool(re.search(_GI_WORD, text, re.I))
    diarrhoea = bool(_DIARRHOEA.search(text)) and not _COMPOSITION.search(text)
    if _DISC.search(text) and (_INTOLERANCE.search(text) or gi_named or diarrhoea):
        return GI_DISCONTINUATION
    if _HOSP.search(text) and (gi_named or diarrhoea):
        return GI_HOSPITALISATION
    if diarrhoea:
        return DIARRHOEA
    if _GI_ANY.search(text) or _INTOLERANCE.search(text):
        return GI_ANY
    return None


def outcome_of_name(outcome_name: str) -> str | None:
    """Which taxonomy outcome a SERVED outcome name stands for ('Gastrointestinal adverse effects' -> GI_ANY)."""
    return label_outcome(outcome_name or "")


def _tokens(sentence: str) -> list[dict[str, Any]]:
    toks, taken = [], []
    for kind, rx in _TOKENS:
        for m in rx.finditer(sentence):
            if any(m.start() < e and s < m.end() for s, e in taken):
                continue
            taken.append(m.span())
            if kind == "of":
                arm = {"events": _int(m.group(1)), "n": _int(m.group(2))}
                if arm["events"] > arm["n"]:
                    continue
            elif kind == "cnt":
                arm = {"events": _int(m.group(1)), "n": None, "pct": float(m.group(2))}
            else:
                arm = {"pct": float(m.group(1))}
            toks.append({"kind": kind, "arm": arm, "start": m.start(), "end": m.end()})
    return sorted(toks, key=lambda t: t["start"])


def _results_in(sentence: str) -> list[dict[str, Any]]:
    """Every two-arm result a sentence states, each with its OWN label: the text of its clause before it, the words between its
    two arms, and its tail up to the next clause boundary or result. Two values pair only if they are the same kind of number,
    joined by an arm connector, with no clause boundary between them (else they are two outcomes, not two arms)."""
    toks, out, i = _tokens(sentence), [], 0
    while i + 1 < len(toks):
        a, b = toks[i], toks[i + 1]
        between = sentence[a["end"]:b["start"]]
        if (a["kind"] == b["kind"] and len(between) <= 200 and _ARM_CONNECTOR.search(between) and not _CLAUSE.search(between)
                and not re.search(r"\d", between)):
            out.append({"a": a, "b": b, "between": between})
            i += 2
        else:
            i += 1
    results = []
    for k, r in enumerate(out):
        prev_end = out[k - 1]["b"]["end"] if k else 0
        head = sentence[prev_end:r["a"]["start"]]
        cuts = list(_CLAUSE.finditer(head))
        head = head[cuts[-1].end():] if cuts else head
        nxt = out[k + 1]["a"]["start"] if k + 1 < len(out) else len(sentence)
        raw_tail = sentence[r["b"]["end"]:nxt]                  # an effect + CI may sit past a ';' ('hazard ratio, 1.06; 95% CI ...')
        stop = _CLAUSE.search(raw_tail)
        tail = raw_tail[:stop.start()] if stop else raw_tail
        kind = r["a"]["kind"]
        res = {"status": RECONSTRUCTED if kind == "pct" else EXACT, "arms": [r["a"]["arm"], r["b"]["arm"]],
               "label": re.sub(r"\s+", " ", f"{head}{sentence[r['a']['start']:r['b']['end']]}{tail}").strip(),
               "span": sentence[r["a"]["start"]:r["b"]["end"]]}
        eff = _EFFECT.search(raw_tail)
        if eff:
            est, lo, hi = float(eff.group(2)), float(eff.group(3)), float(eff.group(4))
            if lo <= est <= hi:
                res["effect"] = {"measure": eff.group(1), "estimate": est, "ci": [lo, hi]}
                if res["status"] == RECONSTRUCTED:
                    res["status"] = EFFECT_CI
        results.append(res)
    return results


def unique_patient_total(sentence: str) -> bool:
    """A GI_ANY count is a unique-patient total only if it counts PEOPLE (not events or episodes)."""
    return bool(_PATIENT.search(sentence)) and not _EPISODES.search(sentence)


def admissible(outcome: str, status: str, unique_patients: bool) -> tuple[bool, str]:
    """The one admission rule, identical for every trial and every outcome."""
    if status == RECONSTRUCTED:
        return False, "RECONSTRUCTED: percentages only -- a candidate, not pooled, until exact counts are held"
    if outcome == GI_ANY and status == EXACT and not unique_patients:
        return False, "GI_ANY needs a unique-patient total; these counts are not shown to count distinct patients (never summed)"
    return True, "ADMISSIBLE: exact per-arm counts" if status == EXACT else "ADMISSIBLE: effect with confidence interval"


def bind_results(sources: list[dict[str, Any]], trial: str) -> list[dict[str, Any]]:
    """Every GI result in a trial's held sources, each bound by its own source label into exactly one taxonomy outcome. When two
    sentences state the SAME per-arm counts under different labels (an abstract's 'gastrointestinal symptom' and the full text's
    'diarrhea' for 15 vs 3), the most specific label that states those counts wins -- the numbers belong to what they count."""
    found: dict[tuple, dict[str, Any]] = {}
    for src in sources or []:
        for sentence in extract._sentences(src.get("text") or ""):
            for res in _results_in(sentence):
                outcome = label_outcome(res["label"])            # the result's OWN label, never the whole sentence's
                if outcome is None:
                    continue
                key = tuple((a.get("events"), a.get("pct")) if res["status"] != EXACT else (a.get("events"),)
                            for a in res["arms"])
                uniq = unique_patient_total(res["label"])
                ok, why = admissible(outcome, res["status"], uniq)
                cand = {"trial": trial, "outcome": outcome, "status": res["status"], "arms": res.get("arms"),
                        "effect": res.get("effect"), "unique_patient_total": uniq, "admissible": ok, "admission": why,
                        "source_id": src.get("source_id"), "label": res["label"][:300], "label_sentence": sentence.strip()[:400]}
                prior = found.get(key)
                if prior is None or SPECIFICITY.index(outcome) < SPECIFICITY.index(prior["outcome"]):
                    if prior is not None:
                        cand["relabelled_from"] = {"outcome": prior["outcome"], "source_id": prior["source_id"]}
                    found[key] = cand
    return list(found.values())


def served_numbers(row: dict[str, Any]) -> tuple | None:
    if row.get("ai") is None or row.get("ci") is None:
        return None
    return ((int(row["ai"]),), (int(row["ci"]),))


def rebind_row(outcome_name: str, row: dict[str, Any], included: bool, bound: list[dict[str, Any]]) -> dict[str, Any]:
    """What the taxonomy does to one served harm row. Never edits it: returns the before/after for a notice."""
    target = outcome_of_name(outcome_name)
    before = {"outcome": target, "state": "INCLUDED" if included else "REFUSED", "reason_code": row.get("reason_code")}
    if target is None:
        return {"rebound": False, "before": before, "after": None, "why": "served outcome not in the GI safety taxonomy"}
    if included:
        nums = served_numbers(row)
        hit = next((b for b in bound if b["status"] == EXACT and nums and tuple((a["events"],) for a in b["arms"]) == nums), None)
        if hit is None:
            return {"rebound": False, "before": before, "after": None,
                    "why": "served numbers not re-found under any taxonomy label in held sources (left as served)"}
        if hit["outcome"] == target:
            return {"rebound": False, "before": before, "after": hit, "why": "source label names the served outcome"}
        return {"rebound": True, "before": before, "after": hit,
                "why": f"source label names {hit['outcome']}, not {target}: the result moves to {hit['outcome']} and leaves {target}"}
    if not bound:
        return {"rebound": False, "before": before, "after": None, "why": "no GI result under any taxonomy label in held sources"}
    same = [b for b in bound if b["outcome"] == target]
    after = same[0] if same else bound[0]
    return {"rebound": True, "before": before, "after": after, "all_bindings": bound,
            "why": (f"a {target} result is held under its own label ({after['admission']})" if same else
                    f"not 'narrower than {target}': the result is {after['outcome']} and is bound there ({after['admission']})")}


def harms_only_rob_flags(review: dict[str, Any], canonical_trial_id) -> list[dict[str, Any]]:
    """A trial that contributes ONLY to harm outcomes must carry an outcome-specific RoB entry for each harm it contributes to;
    otherwise it is flagged (trial-level RoB judged on an efficacy endpoint does not cover a harm's measurement and reporting)."""
    rob = (review.get("rob2") or {}).get("trials") or {}
    rob_ids = {}
    for k, e in rob.items():
        rob_ids[canonical_trial_id(k)] = e
        if isinstance(e, dict) and e.get("nct"):
            rob_ids[canonical_trial_id(e["nct"])] = e
    efficacy, harms = set(), {}
    for o in review.get("outcomes") or []:
        for t in o.get("trials") or []:
            tid = canonical_trial_id(t.get("id") or t.get("label"))
            (harms.setdefault(tid, []).append(o.get("name")) if o.get("kind") == "harm" else efficacy.add(tid))
    flags = []
    for tid, names in sorted(harms.items()):
        if tid in efficacy:
            continue
        entry = rob_ids.get(tid)
        for name in names:
            specific = isinstance(entry, dict) and isinstance(entry.get("outcomes"), dict) and name in entry["outcomes"]
            if not specific:
                flags.append({"trial": tid, "outcome": name,
                              "flag": "HARMS_ONLY_NO_ROB_ENTRY" if entry is None else "HARMS_ONLY_ROB_NOT_OUTCOME_SPECIFIC"})
    return flags
