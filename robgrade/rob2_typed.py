"""Typed (deterministic) answers to RoB 2 signalling questions, and the per-trial SOURCE SET every answer cites.

Two kinds of typed answer, each carrying a verbatim span and the sha256 of the source the span is in:
  registry  AACT structured fields (designs.allocation, designs.masking + per-role masked flags) -- the span is the field
            as 'name: value', the sha256 is of the canonical header-keyed AACT row (the method aact_inputs.json pins),
            and the registered-outcome identity the machine D5 signal established (component set / text identity only)
  regex     fixed phrases over the trial's held texts. D8 lets REGEX read any held text, open or not; only a model
            prompt is limited to open text. The span is the matched sentence (<= 300 chars), the sha256 is of the text.

A rule answers only what its evidence states. Silence is not an answer (no rule ever returns NI 'by default' with a
span): an unanswered question goes to the recorded dual reading (scripts/rob2_dual.py), and if no reader can quote an
open source for it, it stays NI.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

from robgrade import rob2_formal as rf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FT_INDEX = os.path.join(ROOT, "outputs", "k_gap", "fulltext_index.json")
SPAN_MAX = 300


def sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()


def canonical_row(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


# ------------------------------------------------------------------------------------------------ the source set

def _ft_licences():
    if not os.path.exists(FT_INDEX):
        return {}
    return {str(p): (e or {}).get("copy_licence") for p, e in json.load(open(FT_INDEX, encoding="utf-8")).items()}


def trial_sources(slug, pmid, nct=None, registry_rows=None, registry_text=None, ft_licences=None):
    """Every held source for one trial: [{id, kind, pmid|nct, text, sha256, open_for_prompt, licence}].
    open_for_prompt: abstract (the existing abstract policy) and registry text (US Government work) are open; a full
    text only when outputs/k_gap/fulltext_index.json marks its copy CC -- the same test the recorder's licence guard
    applies (reproducible_ai/record_licence.py), so a source this marks open is never refused there."""
    out = []
    recs = os.path.join(ROOT, "cache", slug, "records.json")
    rec = None
    if os.path.exists(recs):
        rec = next((r for r in json.load(open(recs, encoding="utf-8")).get("records", []) if str(r.get("id")) == str(pmid)), None)
    if not (rec or {}).get("abstract"):
        # a trial outside this topic's own records (e.g. a calibration trial from the comparator's RoB table): the
        # k-gap member records hold its PubMed record
        mp = os.path.join(ROOT, "outputs", "k_gap", "member_records.json")
        if os.path.exists(mp):
            rec = json.load(open(mp, encoding="utf-8")).get(str(pmid)) or rec
    if rec is not None:
        ab = (rec or {}).get("abstract")
        if ab:
            out.append({"id": f"abstract:PMID {pmid}", "kind": "abstract", "pmid": str(pmid), "text": ab, "sha256": sha(ab),
                        "open_for_prompt": True, "licence": "PubMed abstract (abstract policy)"})
    fp = os.path.join(ROOT, "cache", slug, f"ft_{pmid}.txt")
    if os.path.exists(fp):
        b = open(fp, "rb").read()
        lic = (ft_licences if ft_licences is not None else _ft_licences()).get(str(pmid))
        out.append({"id": f"fulltext:PMID {pmid}", "kind": "fulltext", "pmid": str(pmid),
                    "text": b.decode("utf-8", "replace"), "sha256": sha(b), "open_for_prompt": lic == "CC",
                    "licence": lic or "UNKNOWN (not marked open)"})
    for name, row in (registry_rows or {}).items():
        txt = "\n".join(f"{k}: {v}" for k, v in sorted(row.items()))
        out.append({"id": f"registry:{nct}:{name}", "kind": "registry_row", "nct": nct, "text": txt,
                    "sha256": sha(canonical_row(row)), "open_for_prompt": True,
                    "licence": "ClinicalTrials.gov via AACT (US Government work)", "row": row})
    if registry_text:
        out.append({"id": f"registry:{nct}:description", "kind": "registry_text", "nct": nct, "text": registry_text,
                    "sha256": sha(registry_text), "open_for_prompt": True,
                    "licence": "ClinicalTrials.gov via AACT (US Government work)"})
    return out


# ------------------------------------------------------------------------------------------------ regex rules

def _sentence(text, m):
    """The sentence holding match m, trimmed to SPAN_MAX around the match (verbatim)."""
    a = max(text.rfind(". ", 0, m.start()) + 2, text.rfind("\n", 0, m.start()) + 1, 0)
    b = min([x for x in (text.find(". ", m.end()), text.find("\n", m.end())) if x >= 0] + [len(text)])
    s, e = a, b + 1 if b < len(text) else b
    if e - s > SPAN_MAX:
        s = max(m.start() - SPAN_MAX // 2, 0)
        e = min(s + SPAN_MAX, len(text))
    return text[s:e].strip()


# (qid, answer, rule id, pattern). Order matters within a question: the first rule that matches answers it.
SEQ = r"computer[- ]generated|random(?:ly)? (?:number|sequence) (?:table|generator)|permuted[- ]block|block randomi[sz]|" \
      r"(?:stratified|central(?:ised|ized)?|centrally) randomi[sz]|interactive (?:voice|web|telephone)[- ]?(?:or (?:web|voice)[- ]?)?(?:response|based)|" \
      r"\bI[VWX]R?RS\b|\bIxRS\b|randomi[sz]ation (?:schedule|list|sequence) (?:was |were )?(?:computer|generated)"
CONCEAL = r"central(?:ised|ized|ly)? (?:randomi[sz]ation|allocation|telephone|web)|interactive (?:voice|web|telephone)|" \
          r"\bI[VWX]R?RS\b|\bIxRS\b|sequentially numbered,? (?:sealed,? )?opaque,? (?:sealed )?envelopes|" \
          r"opaque,? sealed envelopes|pharmacy[- ](?:controlled|prepared) (?:randomi|allocation)|allocation (?:was )?concealed"
DOUBLE_BLIND = r"double[- ]blind(?:ed)?|double[- ]mask(?:ed)?|triple[- ]blind|placebo[- ]controlled,? double"
# 'unblinded' / 'not blinded' are NOT here: they do not say WHOSE blinding (assessors? participants?)
OPEN_LABEL = r"open[- ]label|PROBE design|prospective,? randomi[sz]ed,? open"
ITT = r"intention[- ]to[- ]treat|\bITT\b|modified intention|full analysis set|all randomi[sz]ed (?:patients|participants)"
BLIND_ADJ = r"(?:blinded|masked|independent,? blinded|unaware of (?:treatment|group|study)[- ]?(?:assignment|allocation)?)[^.]{0,80}" \
            r"(?:adjudicat|endpoint committee|events? committee|outcome assessor)|" \
            r"adjudicat\w+ (?:by )?(?:an? )?(?:independent )?(?:clinical )?(?:events? |endpoint )?committee[^.]{0,60}(?:blind|mask|unaware)"

REGEX_RULES = [
    ("1.1", "Y", "regex:sequence_generation_v1", SEQ),
    ("1.2", "Y", "regex:allocation_concealment_v1", CONCEAL),
    ("2.1", "Y", "regex:open_label_v1", OPEN_LABEL),
    ("2.2", "Y", "regex:open_label_v1", OPEN_LABEL),
    ("2.1", "PN", "regex:double_blind_v1", DOUBLE_BLIND),
    ("2.2", "PN", "regex:double_blind_v1", DOUBLE_BLIND),
    ("2.6", "PY", "regex:itt_v1", ITT),
    ("4.3", "PN", "regex:blinded_adjudication_v1", BLIND_ADJ),
]


# A sentence about OTHER trials (introduction / discussion: citations, 'these trials', 'previous studies') says nothing
# about this one (CONFIRM-HF 25176939: "These trials, however, suffer from ... open-label vs. placebo-controlled" in its
# introduction read as 'participants aware' of a double-blind trial).
_OTHER_TRIALS = re.compile(r"xref|bibr|\bet al\b|\[\s*\d+(?:\s*[,–-]\s*\d+)*\s*\]|"
                           r"\b(?:previous|prior|other|earlier|these|such|those|several|many|most) (?:\w+ )?(?:trials|studies|reports)\b|"
                           r"\btrials\b", re.I)


def _about_this_trial(sentence):
    return not _OTHER_TRIALS.search(sentence)


_NEG = re.compile(r"\b(?:not|no|non|neither|nor|without|never)\b[\s-]*(?:\w+[\s-]+){0,2}$", re.I)


def _negated(text, m):
    """A phrase preceded (within three words) by a negation states the opposite: 'not double-blind', 'without
    concealment', 'no intention-to-treat analysis'."""
    return bool(_NEG.search(text[max(0, m.start() - 40):m.start()]))


def regex_answers(sources):
    """{qid: answer} from the regex rules over every held TEXT source (abstract, full text, registry description).
    Per question the first rule (in REGEX_RULES order) that matches any source answers it; the open-label rule precedes
    the double-blind rule, so a trial describing itself as both is never read as blinded."""
    out = {}
    texts = [s for s in sources if s["kind"] in ("abstract", "fulltext", "registry_text")]
    for qid, val, rid, pat in REGEX_RULES:
        if qid in out:
            continue
        for s in texts:
            m = next((x for x in re.finditer(pat, s["text"], re.I)
                      if not _negated(s["text"], x) and _about_this_trial(_sentence(s["text"], x))), None)
            if m:
                out[qid] = rf.answer(val, how="typed-regex", span=_sentence(s["text"], m), source_ref=s["id"],
                                     source_sha256=s["sha256"], rule_id=rid,
                                     note=None if s["open_for_prompt"] else "read by regex from a text not open for "
                                                                            "prompts (D8 allows regex)")
                break
    return out


# ------------------------------------------------------------------------------------------------ registry rules

_MASKED = ("DOUBLE", "TRIPLE", "QUADRUPLE")


def registry_answers(sources, machine_d5=None):
    """{qid: answer} from the AACT designs row (and the machine D5 registered-outcome identity, when it was
    established by component set or text identity -- an embedding match is not an identity)."""
    out = {}
    row_src = next((s for s in sources if s["kind"] == "registry_row" and s["id"].endswith(":designs")), None)
    if row_src:
        row = row_src["row"]

        def ans(qid, val, field, rid):
            out[qid] = rf.answer(val, how="typed-registry", span=f"{field}: {row.get(field)}", source_ref=row_src["id"],
                                 source_sha256=row_src["sha256"], rule_id=rid)
        if str(row.get("allocation") or "").upper() == "RANDOMIZED":
            ans("1.1", "PY", "allocation", "registry:allocation_randomized_v1")
        masking = str(row.get("masking") or "").upper()
        if masking == "NONE":
            ans("2.1", "Y", "masking", "registry:masking_none_v1")
            ans("2.2", "Y", "masking", "registry:masking_none_v1")
        # a per-role flag answers only when it is TRUE: registries under-report roles ('f' is not 'unmasked')
        if str(row.get("subject_masked") or "").lower() in ("t", "true"):
            ans("2.1", "N", "subject_masked", "registry:subject_masked_v1")
        if str(row.get("caregiver_masked") or "").lower() in ("t", "true"):
            ans("2.2", "N", "caregiver_masked", "registry:caregiver_masked_v1")
        if str(row.get("outcomes_assessor_masked") or "").lower() in ("t", "true"):
            ans("4.3", "N", "outcomes_assessor_masked", "registry:outcomes_assessor_masked_v1")
    d5 = machine_d5 or {}
    basis = str(d5.get("basis") or "")
    if d5.get("level") == "low" and re.search(r"component set|text identity|identical", basis) and "embedding" not in basis:
        out["5.1"] = rf.answer("PY", how="typed-registry", span=basis[:SPAN_MAX], source_ref="registry:registered outcomes",
                               source_sha256=sha(json.dumps(d5, sort_keys=True)), rule_id="registry:registered_outcome_identity_v1",
                               note="the served outcome is the trial's pre-registered outcome (identity by component set/text)")
    return out


def typed_answers(sources, machine_d5=None):
    """(answers, conflicts). Registry and regex answers merged per question:
      same side (e.g. 1.1 registry PY + regex Y)  -> the more specific one (the regex span that states the method)
      opposite sides (registry 'subject masked' v text 'open-label') -> NO typed answer: the question goes to the
                                                   recorded dual reading, and the contradiction is recorded
    A typed layer never picks a winner between two typed sources that contradict each other."""
    reg = registry_answers(sources, machine_d5)
    rx = regex_answers(sources)
    out, conflicts = {}, []
    for q in sorted(set(reg) | set(rx)):
        a, r = reg.get(q), rx.get(q)
        if a and r and rf.side(a["answer"]) != rf.side(r["answer"]):
            conflicts.append({"question": q, "registry": a, "regex": r})
            continue
        if a and r:
            out[q] = r if r["answer"] in ("Y", "N") and a["answer"] in ("PY", "PN") else a
        else:
            out[q] = a or r
    return out, conflicts
