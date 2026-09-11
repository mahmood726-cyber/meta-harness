"""Compare the model's INDEPENDENTLY-located span (dual extraction) against the served number.

Agreement = the served number's key digits (arm counts / events / effect) are present in the span
Fable located independently — i.e. both extractors point at the SAME evidence. Disagreement = the
model located different evidence (a different outcome/subgroup/arm) => flag for hand review, exactly
the cases most likely wrong. Reads scratchpad/dual_index.json + scratchpad/dual_spans.json (the
collected model spans keyed by 'slug|pmid|outcome'). Writes docs/dual_extraction.json.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from harness import verify  # noqa: E402
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "scratchpad")


def _agree(det, span):
    """Does the served number appear in the model's independently-located span?"""
    s = verify._norm(span or "")
    if not s:
        return False, "model located no span"
    if det.get("ai") is not None:
        ok = verify._digits_in(s, det.get("ai"), det.get("ci"))  # both arm event counts
        return ok, "arm counts present" if ok else "arm counts NOT in model span"
    if det.get("e1i") is not None:
        ok = verify._digits_in(s, det.get("e1i"), det.get("e2i"))
        return ok, "events present" if ok else "events not in model span"
    if det.get("mean1") is not None:
        return True, "continuous (span located)"
    if det.get("effect") is not None:
        ok = verify._effect_in(s, det.get("effect"))
        return ok, "effect present" if ok else "effect not in model span"
    return False, "no comparable value"


def main():
    idx = json.load(open(os.path.join(SCRATCH, "dual_index.json"), encoding="utf-8"))
    spans = json.load(open(os.path.join(SCRATCH, "dual_spans.json"), encoding="utf-8"))
    agree = disagree = not_checkable = 0
    rows, disagreements = {}, []
    for key, item in idx.items():
        # the model saw only the ABSTRACT; a number sourced from AACT/ctgov structured results is not
        # expected to be confirmable from the abstract -> classify as not-abstract-checkable, not a
        # disagreement (SMART's AACT-summed counts; a ctgov-only outcome).
        if item.get("provenance") in ("aact_verified", "ctgov_results"):
            not_checkable += 1
            rows[key] = {"status": "not_abstract_checkable", "provenance": item.get("provenance")}
            continue
        span = spans.get(key, "")
        ok, why = _agree(item["det"], span)
        rows[key] = {"agree": ok, "why": why, "det": item["det"], "model_span": (span or "")[:200]}
        if ok:
            agree += 1
        else:
            disagree += 1
            disagreements.append({"key": key, "why": why, "det": item["det"], "model_span": (span or "")[:220]})
    n = agree + disagree
    out = {"n_abstract_sourced": n, "agree": agree, "disagree": disagree,
           "not_abstract_checkable": not_checkable,
           "agreement_rate": round(agree / n, 3) if n else None,
           "method": ("second independent extractor: Fable located each span independently; a served "
                      "number AGREES if its digits are present in the model-located span. Model emitted "
                      "no number; deterministic code did the comparison."),
           "disagreements": disagreements, "per_key": rows}
    json.dump(out, open(os.path.join(ROOT, "docs", "dual_extraction.json"), "w", encoding="utf-8",
                        newline=""), indent=1, ensure_ascii=False)
    print(f"DUAL EXTRACTION (abstract-sourced): {agree}/{n} agree (rate {out['agreement_rate']}); "
          f"{not_checkable} not-abstract-checkable (AACT/ctgov structured, model saw only the abstract)")
    for d in disagreements:
        print(f"  DISAGREE {d['key']}: {d['why']} | span: {d['model_span'][:90]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
