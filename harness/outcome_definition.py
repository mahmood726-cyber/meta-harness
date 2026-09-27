"""OUTCOME DEFINITION RECORD for a binary single-event endpoint (metformin-PCOS review, 2026-09-27, hash f1643a71).

"Ovulation" is not one thing. Per trial the held text states (or does not state):
  * the CRITERION   -- Ben Ayed: a follicle > 16 mm + estradiol 150-250 pg + endometrium > 8 mm; Vandermolen: serum
                       progesterone >= 4 ng/mL;
  * the DENOMINATOR -- women who ovulated, or ovulatory cycles;
  * the treatment SEQUENCE -- metformin added to clomifene, or given first;
  * the STOPPING rules -- Vandermolen: "completed the study when they had had six ovulatory cycles, became pregnant, or
                       experienced anovulation while receiving 150 mg of CC"; Ben Ayed: "three trials maximum";
  * the OBSERVATION period.
An endpoint label "HOMOGENEOUS" is DERIVED from these records: HOMOGENEOUS only when every declared field is stated for every
trial and the same; a stated difference is DEFINITION_HETEROGENEOUS; a field some trial does not state is
DEFINITION_NOT_DERIVABLE. It is never asserted from the outcome's name or a single component token.
"""
from __future__ import annotations

import re
from typing import Any

FIELDS = ("criterion", "denominator", "sequence", "stopping", "observation")
NOT_STATED = "NOT_STATED"

_CRITERION = (("FOLLICLE_SIZE", re.compile(r"(?i)follicles?\b[^.;]{0,40}?[>≥]?\s*\d{2}\s*mm|\d{2}\s*mm\b[^.;]{0,20}?follic")),
              ("ESTRADIOL", re.compile(r"(?i)\bestradiol\b|\bE2\b")),
              ("ENDOMETRIUM", re.compile(r"(?i)endometri\w*")),
              ("PROGESTERONE", re.compile(r"(?i)\bprogesterone\b|\bserum\s+P\s+level")),
              ("ULTRASOUND", re.compile(r"(?i)ultrasonograph\w*|ultrasound")),
              ("BASAL_BODY_TEMPERATURE", re.compile(r"(?i)basal\s+body\s+temperature")))
_CRITERION_SENTENCE = re.compile(r"(?i)ovulation\s+(?:was\s+)?(?:characteri[sz]ed|defined|confirmed|detect\w*|considered|documented)|"
                                 r"considered\s+to\s+indicate\s+ovulation|indicat\w*\s+ovulation|ovulation\s+detection")
_WOMAN = re.compile(r"(?i)\b\d+\s+of\s+\d+\s+(?:participants|women|patients|subjects)\b[^.;]{0,40}?\bovulated|"
                    r"\b(?:women|participants|patients)\s+(?:who\s+)?ovulated\b")
_CYCLE = re.compile(r"(?i)\bper\s+cycle\b|\bof\s+(?:the\s+)?(?:treatment\s+)?cycles\b|\bovulatory\s+cycles?\s+rate|\bcycles?\s+with\s+ovulation")
_SEQUENCE = re.compile(r"(?i)in\s+addition\s+to\s+clomi\w+[^.;]{0,120}|clomi\w+\s+(?:citrate\s+)?plus\s+(?:metformin|placebo)[^.;]{0,80}|"
                       r"(?:pre-?treat\w*|before|prior\s+to)\s+[^.;]{0,60}clomi\w+[^.;]{0,60}|received\s+placebo\s+or\s+metformin[^.;]{0,80}")
_STOPPING = re.compile(r"(?i)[^.;]{0,120}\b(?:until|completed\s+the\s+study\s+when|maximum|at\s+most|discontinued\s+when|stopped\s+when)\b[^.;]{0,160}")
_OBSERVATION = re.compile(r"(?i)\bfor\s+(?:up\s+to\s+)?\d+\s+(?:weeks?|months?|cycles?)\b|\bwithin\s+\d+\s+months?\b|\b\d+\s+(?:treatment\s+)?cycles\b")


def _sentences(text: str | None) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if s.strip()]


def definition_record(text: str | None) -> dict[str, Any]:
    """Each field with its value and the verbatim span it came from; NOT_STATED when the held text does not state it."""
    sents = _sentences(text)
    rec: dict[str, Any] = {}
    crit_sents = [s for s in sents if _CRITERION_SENTENCE.search(s)]
    elems, spans = [], []
    for s in crit_sents:
        for name, rx in _CRITERION:
            if rx.search(s) and name not in elems:
                elems.append(name)
                spans.append(s)
    rec["criterion"] = ({"value": tuple(sorted(elems)), "span": " | ".join(dict.fromkeys(spans))[:600]} if elems
                        else {"value": NOT_STATED, "span": None})
    woman = next((s for s in sents if _WOMAN.search(s)), None)
    cycle = next((s for s in sents if _CYCLE.search(s)), None)
    if woman and cycle:
        rec["denominator"] = {"value": "AMBIGUOUS", "span": woman[:300] + " | " + cycle[:300]}
    elif woman or cycle:
        rec["denominator"] = {"value": "WOMAN" if woman else "CYCLE", "span": (woman or cycle)[:300]}
    else:
        rec["denominator"] = {"value": NOT_STATED, "span": None}
    for field, rx in (("sequence", _SEQUENCE), ("stopping", _STOPPING), ("observation", _OBSERVATION)):
        # a recruitment window ("Within 7 months, 32 women were recruited") is not the observation period
        hit = next((s for s in sents if rx.search(s) and not (field == "observation" and re.search(r"(?i)\brecruit", s))), None)
        if hit:
            m = rx.search(hit)
            rec[field] = {"value": " ".join(m.group(0).lower().split()), "span": hit[:400]}
        else:
            rec[field] = {"value": NOT_STATED, "span": None}
    return rec


def derive_status(records: dict[str, dict[str, Any]], fields=FIELDS) -> dict[str, Any]:
    """Per field: HOMOGENEOUS (stated for every trial and equal), HETEROGENEOUS (stated, different), NOT_STATED (some trial is
    silent -- named). Overall: DEFINITION_HETEROGENEOUS if any field differs, else DEFINITION_NOT_DERIVABLE if any field is not
    stated, else HOMOGENEOUS."""
    per = {}
    for f in fields:
        vals = {tid: (r.get(f) or {}).get("value", NOT_STATED) for tid, r in records.items()}
        silent = sorted(t for t, v in vals.items() if v == NOT_STATED)
        stated = {t: v for t, v in vals.items() if v != NOT_STATED}
        if len(set(map(str, stated.values()))) > 1:
            per[f] = {"state": "HETEROGENEOUS", "values": {t: v for t, v in stated.items()}, "not_stated": silent}
        elif silent:
            per[f] = {"state": "NOT_STATED", "not_stated": silent, "values": stated}
        else:
            per[f] = {"state": "HOMOGENEOUS", "value": next(iter(stated.values()), None)}
    if any(p["state"] == "HETEROGENEOUS" for p in per.values()):
        status = "DEFINITION_HETEROGENEOUS"
    elif any(p["state"] == "NOT_STATED" for p in per.values()):
        status = "DEFINITION_NOT_DERIVABLE"
    else:
        status = "HOMOGENEOUS"
    return {"status": status, "fields": per,
            "basis": "derived per field from each trial's held text; never asserted from the outcome name"}
