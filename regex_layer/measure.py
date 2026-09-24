"""R2 -- candidate sentences from held sources, the regex's own output on them, and precision / recall per pattern
against labelled spans.

Candidates: every sentence of every held abstract (cache/<slug>/records.json, split by harness.extract._sentences after
harness.extract._norm -- the extractor's own view of the text). For each pattern, a sentence is a candidate when the
pattern fires on it (a true or false positive) or when only its broad TRIGGER fires (a possible false negative). A
deterministic sample (sha256 order) of each kind is labelled; the label never sees the regex or its output.

Label (a recorded, replayable model PROPOSAL, or a human's): does the sentence STATE the thing the spec describes; for an
extractor, every instance with each field quoted verbatim from the sentence (so the label supplies no number of its
own -- every digit is the source's). Measurement compares the pattern's own output with the label:
  extractor   TP = labelled instances the pattern produced exactly; FP = produced, not labelled; FN = labelled, not
              produced. precision = TP / (TP + FP), recall = TP / (TP + FN), each reported as n of N.
  classifier  per sentence: TP fires & states, FP fires & not, FN states & not fired.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from harness import extract
from regex_layer.specs import SPECS

ROOT = Path(__file__).resolve().parents[1]

# how a regex match maps onto the label's fields (most are the groups in order)
LABEL_FIELDS = {"_MEAN_SD": ["mean", "sd"]}
# value fields that may carry a '%' unit (a count never does: '9%' quoted as a count is a different thing)
PERCENT_UNIT_FIELDS = ("percent", "mean", "sd")


def project(name: str, m: re.Match) -> tuple:
    g = m.groups()
    if name == "_MEAN_SD":
        return (g[0], g[1] if g[1] is not None else g[2])
    return tuple(g)


def label_fields(name: str) -> list[str]:
    return LABEL_FIELDS.get(name, SPECS[name].get("fields", []))


def norm_value(name: str, field: str, v):
    if v is None:
        return None
    s = extract._norm(str(v)).strip()
    if field == "measure":
        return s.lower()
    if field in PERCENT_UNIT_FIELDS:           # a '%' unit on a value field is typography, not part of the value
        s = re.sub(r"\s*%$", "", s)
    return s


def canon(name: str, t: tuple) -> tuple:
    """Typography that belongs to the PAIR, not to one field: a rate's '%' may be written on the rate ('3.64%',
    'per year') or read onto the unit ('3.64', '% per year') -- the same statement either way."""
    if name == "_RATE_UNIT" and len(t) == 2 and t[0] is not None:
        rate, unit = t
        pct = rate.endswith("%") or (unit or "").lstrip().startswith("%")
        unit = (unit or "").strip().lstrip("%").strip().lower()
        return (rate.rstrip("%").strip(), f"% {unit}" if pct else unit)
    return t


def regex_output(name: str, sentence: str) -> list[tuple]:
    rx = getattr(extract, name)
    fields = label_fields(name)
    if SPECS[name]["kind"] == "classifier":
        return [("FIRES",)] if rx.search(sentence) else []
    return sorted({canon(name, tuple(norm_value(name, f, v) for f, v in zip(fields, project(name, m))))
                   for m in rx.finditer(sentence)})


def label_output(name: str, claim: dict) -> list[tuple]:
    if SPECS[name]["kind"] == "classifier":
        return [("FIRES",)] if claim.get("states") else []
    fields = label_fields(name)
    return sorted({canon(name, tuple(norm_value(name, f, inst.get(f)) for f in fields))
                   for inst in (claim.get("instances") or []) if claim.get("states")})


def held_sentences():
    """(slug, record id, sentence index, sentence) for every held abstract sentence, in a fixed order."""
    for p in sorted((ROOT / "cache").glob("*/records.json")):
        for r in json.loads(p.read_text(encoding="utf-8")).get("records") or []:
            a = extract._norm(r.get("abstract") or "")
            for k, s in enumerate(extract._sentences(a)):
                s = s.strip()
                if 20 <= len(s) <= 1200:
                    yield p.parent.name, str(r.get("id")), k, s


def candidates(per_kind: int = 15) -> list[dict]:
    """Per pattern: up to `per_kind` sentences where the pattern FIRES and up to `per_kind` where only the trigger fires,
    chosen by sha256(pattern + sentence) -- deterministic and blind to content."""
    sents = list(held_sentences())
    seen_text = {}
    for slug, rid, k, s in sents:
        seen_text.setdefault(s, (slug, rid, k))
    out = []
    for name, spec in SPECS.items():
        rx, trig = getattr(extract, name), re.compile(spec["trigger"], re.I)
        fires, near = [], []
        for s, (slug, rid, k) in seen_text.items():
            key = hashlib.sha256(f"{name}\0{s}".encode("utf-8")).hexdigest()
            if rx.search(s):
                fires.append((key, s, slug, rid, k))
            elif trig.search(s):
                near.append((key, s, slug, rid, k))
        for kind, pool in (("FIRES", fires), ("TRIGGER_ONLY", near)):
            for key, s, slug, rid, k in sorted(pool)[:per_kind]:
                out.append({"pattern": name, "sample": kind, "sentence": s,
                            "held_ref": f"cache/{slug}/records.json#{rid} abstract sentence {k}",
                            "held_sha256": hashlib.sha256(s.encode("utf-8")).hexdigest(),
                            "pool_sizes": {"FIRES": len(fires), "TRIGGER_ONLY": len(near)}})
    return out


def label_claim(claim: dict) -> dict:
    """The recorded response's shape -> {states, quote, instances: [{field: quote}]}."""
    inst = [{f.get("field"): f.get("quote") for f in (i.get("fields") or []) if isinstance(f, dict)}
            for i in (claim.get("instances") or []) if isinstance(i, dict)]
    return {"states": claim.get("states"), "quote": claim.get("quote"), "instances": inst}


def verify_label(claim, held_text: str, pattern: str) -> dict:
    """Deterministic check of a label proposal: typed; every quote is a substring of the held sentence; field names are
    the spec's; a 'does not state' label carries no quote and no instance. Then the pattern's own output on the same
    sentence is compared with the label and the agreement recorded (never resolved)."""
    problems = []
    spec = SPECS.get(pattern)
    out = {"task": "regex_label", "pattern": pattern}
    if spec is None:
        return {**out, "state": "VERIFIER_REFUSED", "problems": [f"PATTERN_UNKNOWN: {pattern!r}"]}
    if not isinstance(claim, dict) or not isinstance(claim.get("states"), bool):
        return {**out, "state": "VERIFIER_REFUSED", "problems": ["NOT_TYPED: states must be a bool"]}
    c = label_claim(claim)
    fields = set(label_fields(pattern))
    if spec["kind"] == "classifier":
        if c["states"] and (not isinstance(c["quote"], str) or c["quote"] not in held_text):
            problems.append("SPAN_NOT_IN_SOURCE: the quote is not in the sentence")
        if not c["states"] and c["quote"] not in (None, ""):
            problems.append("NOT_STATED_WITH_SPAN")
    else:
        if not c["states"] and c["instances"]:
            problems.append("NOT_STATED_WITH_INSTANCES")
        if c["states"] and not c["instances"]:
            problems.append("STATED_WITHOUT_INSTANCES")
        for inst in c["instances"]:
            if set(inst) - fields:
                problems.append(f"FIELD_UNKNOWN: {sorted(set(inst) - fields)}")
            for f, q in inst.items():
                if q is not None and (not isinstance(q, str) or q not in held_text):
                    problems.append(f"SPAN_NOT_IN_SOURCE: {f}={q!r}")
    out["problems"] = problems
    out["state"] = "VERIFIER_REFUSED" if problems else "VERIFIER_PASS"
    if not problems:
        r, lab = regex_output(pattern, held_text), label_output(pattern, c)
        out["regex"], out["label"] = r, lab
        out["agreement"] = "RULE_MODEL_AGREE" if r == lab else f"RULE_MODEL_DISAGREE(regex={r}, label={lab}, adjudication=OWED)"
    return out


def measure(labelled: list[tuple[str, str, dict]]) -> dict:
    """labelled: (pattern, sentence, claim). Returns per-pattern counts with n of N."""
    per = {}
    for name, sentence, claim in labelled:
        r, lab = set(regex_output(name, sentence)), set(label_output(name, label_claim(claim)))
        c = per.setdefault(name, {"sentences": 0, "tp": 0, "fp": 0, "fn": 0, "fp_examples": [], "fn_examples": []})
        c["sentences"] += 1
        c["tp"] += len(r & lab)
        c["fp"] += len(r - lab)
        c["fn"] += len(lab - r)
        if r - lab and len(c["fp_examples"]) < 5:
            c["fp_examples"].append({"sentence": sentence[:300], "regex": sorted(r - lab), "label": sorted(lab)})
        if lab - r and len(c["fn_examples"]) < 5:
            c["fn_examples"].append({"sentence": sentence[:300], "label": sorted(lab - r), "regex": sorted(r)})
    for name, c in per.items():
        c["precision"] = f"{c['tp']} of {c['tp'] + c['fp']}"
        c["recall"] = f"{c['tp']} of {c['tp'] + c['fn']}"
    return per
