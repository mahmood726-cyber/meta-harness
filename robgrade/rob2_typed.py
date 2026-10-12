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


def trial_sources(slug, pmid, nct=None, registry_rows=None, registry_text=None, ft_licences=None, local_store=False):
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
    from robgrade import prompt_licence as _pl
    use_store = bool(local_store) and (not os.path.exists(fp) or local_store == "open_cc")
    store_added = False
    if use_store:
        # an OA full text acquired for REGEX reading into the local store outside the repository (scripts/
        # rob2_fulltext_acquire.py; Mahmood 12 Oct 'extend'): never open for a prompt, and NOT in the bundle -- a span
        # from it cites the text's sha256, but an outsider needs the same OA copy to check it
        import sys as _sys
        _sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import rob2_fulltext_acquire as _acq
        txt, meta = _acq.held(pmid)
        if txt:
            store_added = True
            # open_cc (DEV silver-label runs only, scripts/rob2_dual.py --dev): a PMC copy whose OWN permissions are
            # CC BY / CC0 (robgrade/prompt_licence: NC/ND/SA never -- 2026-10-12 D8 incident), that the tracked audit
            # does not rate NOT_CC, AND that the shared index registers CC (the recorder's guard reads the index) may
            # enter a prompt; any other local text stays regex-only. Under open_cc this copy is used even when the repo
            # caches one: its permissions are the ones this lane read
            idx_cc = (ft_licences if ft_licences is not None else _ft_licences()).get(str(pmid)) == "CC"
            opened = (local_store == "open_cc" and meta.get("licence") == "CC" and not meta.get("via") and idx_cc
                      and _pl.open_for_prompt(pmid, os.path.join(_acq.store_path(pmid), "pmc.xml")))
            out.append({"id": f"fulltext:PMID {pmid}", "kind": "fulltext", "pmid": str(pmid), "text": txt,
                        "sha256": meta["text_sha256"], "open_for_prompt": opened, "local_store": True,
                        "licence": "CC" if opened else
                        f"{meta.get('licence')} -- LOCAL STORE, not in the bundle ({meta.get('via') or 'PMC'})"})
    if not store_added and os.path.exists(fp):
        b = open(fp, "rb").read()
        lic = (ft_licences if ft_licences is not None else _ft_licences()).get(str(pmid))
        # the index's 'CC' counts ANY Creative Commons licence: a repo copy opens only when the tracked audit says
        # KEEP_CC (never NOT_CC), and a stored PMC copy, if held, is CC BY / CC0 (robgrade/prompt_licence)
        sx = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
        import sys as _sys
        if sx not in _sys.path:
            _sys.path.insert(0, sx)
        import rob2_fulltext_acquire as _acq
        px = os.path.join(_acq.store_path(pmid), "pmc.xml")
        strict = _pl.open_for_prompt(pmid, px) if os.path.exists(px) else _pl.tracked_verdict(pmid) == "KEEP_CC"
        out.append({"id": f"fulltext:PMID {pmid}", "kind": "fulltext", "pmid": str(pmid),
                    "text": b.decode("utf-8", "replace"), "sha256": sha(b),
                    "open_for_prompt": lic == "CC" and _pl.tracked_verdict(pmid) != "NOT_CC" and strict,
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

# --- extension (Mahmood 12 Oct, 'extend'): the phrases full texts use for what abstracts omit ---
SEQ2 = r"random(?:ly)? generated|computer[- ]generated random|random number|blocks? of (?:\d+|four|six|eight|ten)|" \
       r"\bminimi[sz]ation\b"
CONCEAL2 = r"concealed (?:allocation|randomi[sz]ation)|allocation (?:sequence )?(?:was |were )?concealed|" \
           r"web[- ]based randomi[sz]ation|central (?:telephone|computer)|randomi[sz]ation (?:was )?(?:performed|done|carried out) " \
           r"(?:centrally|by (?:an )?independent)|independent (?:pharmacist|statistician|pharmacy)[^.]{0,60}(?:prepared|generated|held|kept)"
BASELINE_OK = r"baseline characteristics (?:were|was) (?:similar|well[- ]balanced|balanced|comparable)|" \
              r"groups were (?:similar|comparable|well[- ]balanced) at baseline|no (?:significant )?(?:differences|imbalances?) " \
              r"(?:in|at|between)[^.]{0,30}baseline"
ITT_STRONG = r"analys[ie]s (?:was|were) (?:performed |conducted |done )?(?:according to|on|by|using) (?:the |an )?intention[- ]to[- ]treat|" \
             r"intention[- ]to[- ]treat (?:principle|analysis|population)"
COMPLETE_FU = r"no (?:patients?|participants?|subjects?) (?:were |was )?lost to follow[- ]up|follow[- ]up was complete|" \
              r"complete follow[- ]up (?:was|for) (?:obtained|available|achieved|all)|all (?:randomi[sz]ed )?(?:patients|participants) " \
              r"(?:were )?(?:included in|analy[sz]ed)"
ASSESSOR_BLIND = r"outcome assessors? (?:were|was) (?:blinded|masked|unaware)|blinded (?:outcome )?assessors?|" \
                 r"assessors? (?:were |was )?blinded to|(?:assess|evaluat)\w* by (?:an? )?(?:blinded|masked|independent,? blinded) " \
                 r"(?:investigator|assessor|physician|observer|committee)"
ASSESSOR_AWARE = r"outcome assessors? (?:were|was) not (?:blinded|masked)|assessors? (?:were|was) aware of (?:the )?" \
                 r"(?:treatment|group|allocation|assignment)"
SAP_BEFORE = r"statistical analysis plan (?:was |were )?(?:finali[sz]ed|approved|completed|signed|locked|published|registered|submitted) " \
             r"(?:before|prior to) (?:unblinding|database lock|breaking the blind|the database was locked|(?:the )?(?:conclusion|completion|end) " \
             r"of (?:enrol?lment|recruitment|the trial|the study))"
# phrasings found in the calibration full texts (12 Oct): a concealment clause after the generator, a blinded-roles list,
# a pre-defined analysis plan, a lost/total fraction
CONCEAL3 = r"allocation sequence[^.]{0,100}\bconcealed\b|concealed from (?:any|all|the) (?:participants?|investigators?|" \
           r"members? of the study team|study (?:team|staff))"
ASSESSOR_BLIND2 = r"outcome assessors?[^.]{0,60}\b(?:were|was) (?:blinded|masked|unaware)\b"
SAP_PREDEF = r"(?:pre-?defined|pre-?specified|prespecified) statistical analysis plan|statistical analysis plan \(SAP\)[^.]{0,40}pre-?specified|" \
             r"according to (?:a |the )?(?:pre-?defined|pre-?specified|prespecified) (?:statistical )?analysis plan"
PREDEF_PRIMARY = r"primary (?:end ?point|outcome) (?:was )?(?:pre-?specified|prespecified|defined in the (?:trial )?protocol)|" \
                 r"pre-?specified primary (?:end ?point|outcome)"

REGEX_RULES = [
    ("1.1", "Y", "regex:sequence_generation_v1", SEQ),
    ("1.1", "Y", "regex:sequence_generation_v2", SEQ2),
    ("1.2", "Y", "regex:allocation_concealment_v1", CONCEAL),
    ("1.2", "Y", "regex:allocation_concealment_v2", CONCEAL2),
    ("1.2", "Y", "regex:allocation_concealment_v3", CONCEAL3),
    ("1.3", "N", "regex:baseline_balanced_v1", BASELINE_OK),
    ("2.1", "Y", "regex:open_label_v1", OPEN_LABEL),
    ("2.2", "Y", "regex:open_label_v1", OPEN_LABEL),
    ("2.1", "PN", "regex:double_blind_v1", DOUBLE_BLIND),
    ("2.2", "PN", "regex:double_blind_v1", DOUBLE_BLIND),
    ("2.6", "Y", "regex:itt_stated_v2", ITT_STRONG),
    ("2.6", "PY", "regex:itt_v1", ITT),
    ("3.1", "Y", "regex:complete_follow_up_v1", COMPLETE_FU),
    ("4.3", "Y", "regex:assessors_aware_v1", ASSESSOR_AWARE),
    ("4.3", "N", "regex:assessors_blinded_v1", ASSESSOR_BLIND),
    ("4.3", "N", "regex:assessors_blinded_v2", ASSESSOR_BLIND2),
    ("4.3", "PN", "regex:blinded_adjudication_v1", BLIND_ADJ),
    ("5.1", "Y", "regex:sap_before_unblinding_v1", SAP_BEFORE),
    ("5.1", "PY", "regex:sap_predefined_v1", SAP_PREDEF),
    ("5.2", "PN", "regex:prespecified_primary_v1", PREDEF_PRIMARY),
    # an analysis fixed in advance by a pre-specified plan is not one chosen among several on the results (RoB 2 5.3)
    ("5.3", "PN", "regex:sap_fixes_the_analysis_v1", SAP_BEFORE),
    ("5.3", "PN", "regex:sap_fixes_the_analysis_v1", SAP_PREDEF),
]

# 3.1 from a STATED loss to follow-up: percentage thresholds stated, not inferred (the Handbook gives none; these are
# the lane's, recorded with every answer): <= 2% lost -> Y, <= 5% -> PY; more -> no typed answer (whether missingness
# matters is outcome-specific: the reading decides). Counts without a percentage are not divided here.
LOST_PCT = re.compile(r"(\d+(?:\.\d+)?) ?% (?:of (?:the )?(?:patients|participants|subjects) )?(?:were |was )?lost to follow[- ]up|"
                      r"lost to follow[- ]up[^.]{0,40}?\(?(\d+(?:\.\d+)?) ?%\)?|"
                      r"(\d+) ?/ ?(\d+) (?:patients |participants |subjects )?(?:were |was )?lost to follow[- ]up", re.I)


def attrition_answers(sources):
    for s in [x for x in sources if x["kind"] in ("abstract", "fulltext")]:
        for m in LOST_PCT.finditer(s["text"]):
            if _negated(s["text"], m) or not _about_this_trial(_sentence(s["text"], m)):
                continue
            if m.group(3) and m.group(4):                     # a stated lost / total fraction
                if int(m.group(4)) == 0:
                    continue
                pct = 100.0 * int(m.group(3)) / int(m.group(4))
            else:
                pct = float(m.group(1) or m.group(2))
            val = "Y" if pct <= 2 else "PY" if pct <= 5 else None
            if val:
                return {"3.1": rf.answer(val, how="typed-regex", span=_sentence(s["text"], m), source_ref=s["id"],
                                         source_sha256=s["sha256"], rule_id="regex:lost_to_follow_up_pct_v1",
                                         note=f"{pct}% lost to follow-up (lane thresholds: <=2% Y, <=5% PY)")}
    return {}


# All-cause mortality: measured without error and not open to assessor influence (RoB 2 guidance, D4). The span is the
# served outcome definition the assessment is for; cause-specific death (adjudicated) is NOT covered.
ALL_CAUSE = re.compile(r"^(?:all[- ]cause )?mortality$|all[- ]cause (?:mortality|death)|death from any cause|^death$", re.I)


def outcome_answers(outcome):
    if not outcome or not ALL_CAUSE.search(outcome.strip()):
        return {}
    src = sha(outcome)
    mk = lambda v: rf.answer(v, how="typed-outcome", span=outcome, source_ref="served outcome definition",  # noqa: E731
                             source_sha256=src, rule_id="outcome:all_cause_mortality_v1",
                             note="all-cause mortality: objective; ascertainment cannot differ or be influenced")
    return {"4.1": mk("N"), "4.2": mk("PN"), "4.4": mk("N")}


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


# Sentence-scoped rules (v3, 2026-10-12): each pattern is anchored \A...\Z to ONE sentence and carries its own
# whole-sentence exclusion guard (a negation, a hedge, or another trial anywhere in the sentence -> no match).
# Proposed by codex from DEV recall gaps only (record mc-98d7ef55af2c4774d435f7d5d3d8dd50, outputs/robgrade/dev/rule_proposals_r2.json),
# reviewed and planted (tests/test_rob2_sentence_rules.py); tried only for questions REGEX_RULES leave open.
SENTENCE_RULES = [
    ('1.3', 'PN', 'regex:baseline_qualified_or_demographic_balance_v1',
     '\\A(?=[^\\r\\n]{1,1000}\\Z)(?![^\\r\\n]{0,1000}\\b(?:no|not|never|neither|without|except|but|however|although|despite|only|partially|some|unblinded|unmasked|previous|prior|earlier|other|another|separate|published|historical|external|pilot|protocol|planned|expected|assumed|hypothetical|if|whether|would|could|should|might|may|reportedly|claimed|suggested|denied|incorrectly|falsely)\\b)(?![^\\r\\n]{0,1000}(?:\\bet al\\b|(?<!this )\\b(?:trials?|stud(?:y|ies))\\b))[^\\r\\n]{0,300}?\\b(?:baseline characteristics were generally (?:well[- ]balanced|balanced|similar|comparable)|(?:baseline )?demographic and anthropometric characteristics of (?:the )?randomi[sz]ed (?:patients|participants) were (?:similar|comparable|(?:generally )?well[- ]balanced)) between the (?:two )?(?:treatment |intervention )?groups\\b'),
    ('1.3', 'N', 'regex:baseline_demographic_clinical_comparison_v1',
     '\\A(?=[^\\r\\n]{1,1000}\\Z)(?![^\\r\\n]{0,1000}\\b(?:no|not|never|neither|without|except|but|however|although|despite|only|partially|some|unblinded|unmasked|previous|prior|earlier|other|another|separate|published|historical|external|pilot|protocol|planned|expected|assumed|hypothetical|if|whether|would|could|should|might|may|reportedly|claimed|suggested|denied|incorrectly|falsely)\\b)(?![^\\r\\n]{0,1000}(?:\\bet al\\b|(?<!this )\\b(?:trials?|stud(?:y|ies))\\b))[^\\r\\n]{0,300}?\\bat baseline,? the (?:[a-z0-9][a-z0-9-]{0,24} ){1,3}and (?:[a-z0-9][a-z0-9-]{0,24} ){1,3}groups were (?:similar|comparable|well[- ]balanced) (?:with respect to|in terms of) (?:their )?demographic and clinical characteristics\\b'),
    ('4.3', 'N', 'regex:assessors_blinded_relative_clause_v1',
     '\\A(?=[^\\r\\n]{1,1000}\\Z)(?![^\\r\\n]{0,1000}\\b(?:no|not|never|neither|without|except|but|however|although|despite|only|partially|some|unblinded|unmasked|previous|prior|earlier|other|another|separate|published|historical|external|pilot|protocol|planned|expected|assumed|hypothetical|if|whether|would|could|should|might|may|reportedly|claimed|suggested|denied|incorrectly|falsely)\\b)(?![^\\r\\n]{0,1000}(?:\\bet al\\b|(?<!this )\\b(?:trials?|stud(?:y|ies))\\b))[^\\r\\n]{0,300}?\\b(?:assessed|evaluated|adjudicated) by (?:the|two|three|four|[2-9]) (?:independent )?(?:cardiologists|adjudicators|(?:clinical events |endpoint )?committee members) (?:who )?were (?:blinded to(?: \\(unaware of\\))?|masked to|unaware of) (?:the )?(?:treatment|intervention) (?:allocation|assignment)\\b'),
]

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def sentence_answers(sources, answered=()):
    """{qid: answer} from SENTENCE_RULES over each sentence of every held TEXT source, for questions not in
    `answered`. A sentence is matched on its own (re.search, case-insensitive): the patterns' \\A...\\Z guards
    see the whole sentence and nothing else."""
    out = {}
    texts = [s for s in sources if s["kind"] in ("abstract", "fulltext", "registry_text")]
    for qid, val, rid, pat in SENTENCE_RULES:
        if qid in out or qid in answered:
            continue
        for s in texts:
            hit = next((x.strip() for x in _SENT_SPLIT.split(s["text"]) if x.strip() and re.search(pat, x.strip(), re.I)), None)
            if hit:
                out[qid] = rf.answer(val, how="typed-regex", span=hit[:SPAN_MAX], source_ref=s["id"],
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


def typed_answers(sources, machine_d5=None, outcome=None):
    """(answers, conflicts). Registry and regex answers merged per question:
      same side (e.g. 1.1 registry PY + regex Y)  -> the more specific one (the regex span that states the method)
      opposite sides (registry 'subject masked' v text 'open-label') -> NO typed answer: the question goes to the
                                                   recorded dual reading, and the contradiction is recorded
    A typed layer never picks a winner between two typed sources that contradict each other. The stated-attrition rule
    (3.1) answers only where no phrase rule did; the all-cause-mortality rule (4.1, 4.2, 4.4) reads the served outcome."""
    reg = dict(registry_answers(sources, machine_d5), **outcome_answers(outcome))
    rx = regex_answers(sources)
    for q, a in attrition_answers(sources).items():
        rx.setdefault(q, a)
    for q, a in sentence_answers(sources, answered=rx).items():
        rx.setdefault(q, a)
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
