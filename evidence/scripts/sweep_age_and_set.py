"""Two uniform, mechanical sweeps over all adjudicated rows (the second adjudication showed the lane applied them
row by row, inconsistently):
  AGE   for questions that say 'adults': is an adult age floor stated in ANY held source of the row? (regex over
        the same rendered text; the matching span is recorded) -> STATED / NOT_STATED. The clinical entry ruling
        is kept; age is reported as a separate component, never folded in silently.
  SET   served analysis_set label vs what the bound span says: a served 'intention-to-treat' label is
        SUPPORTED (span states ITT/all randomised without restriction), CONTRADICTED (span states another set),
        or UNSUPPORTED (no span states a set)."""
import json, os, re, sys, glob, collections
sys.path.insert(0, os.path.dirname(__file__))
import textrep, verify_records as V
from draft_from_extraction import set_reading
ROOT = textrep.ROOT
AGE = re.compile(r"minimum age (1[89]|[2-9]\d) Years|\badults?\b|aged (?:≥ ?)?(1[89]|[2-9]\d)(?:[–-]\d+)? (?:years|yr)|(?:≥|>=|at least|over) ?(1[89]|[2-9]\d) ?(?:years|yr)"
                 r"|(1[89]|[2-9]\d) years (?:of age )?(?:or|and) (?:older|over)|older than (1[789]|[2-9]\d)|[Aa]ge ?\?> ?(1[78]|[2-9]\d)|between (1[89]|[2-9]\d) and \d+ years", re.I)


EYE_OVERRIDES = {
    "P53-05": ("FLOOR_REMOVED", "RECOVERY: the matched sentence says recruitment was limited to >=18 years 'but the age limit was removed' -- "
                                "the opposite of an adult floor (the entry ruling is already PARTLY for this reason)"),
}


def main():
    out, c = {}, collections.Counter()
    for p in sorted(glob.glob(os.path.join(ROOT, "evidence/adjudication/*.json"))):
        a = json.load(open(p, encoding="utf-8")); k = a["key"]
        pk = json.load(open(os.path.join(ROOT, f"evidence/packets/{k}.json"), encoding="utf-8"))
        q = pk.get("question") or ""
        row = {}
        if re.search(r"\badults?\b", q, re.I):
            hit = None
            # 1. the registry's structured minimum age is authoritative when present
            for s in pk["sources"]:
                if "/registry/" in s["ref"]:
                    m = re.search(r"ELIGIBILITY AGE/SEX: minimum age (\d+) Years[^\n]*", textrep.render(s["ref"]))
                    if m and int(m.group(1)) >= 16:
                        hit = {"ref": s["ref"], "span": m.group(0), "kind": "REGISTRY_MINIMUM_AGE"}; break
            # 2. otherwise a text statement, excluding reference lists, citations and background/risk-factor contexts
            if not hit:
                for s in pk["sources"]:
                    t = textrep.render(s["ref"])
                    for m in AGE.finditer(t):
                        ctx = t[max(0, m.start() - 300): m.start()]
                        if re.search(r"<ref|article-title|element-citation|BACKGROUND:|risk factor|especially among", ctx, re.I):
                            continue
                        hit = {"ref": s["ref"], "span": t[max(0, m.start() - 60): m.end() + 40], "kind": "TEXT_MATCH_NEEDS_EYE"}; break
                    if hit:
                        break
            row["age"] = "STATED" if hit else "NOT_STATED"; row["age_span"] = hit
            if k in EYE_OVERRIDES:   # a text match read by eye and found to say the opposite
                row["age"], row["age_override"] = EYE_OVERRIDES[k]
            c["age_" + row["age"]] += 1
        served = V.served_row(pk).get("analysis_set") or ""
        ev_ = a.get("evidence") or {}
        span = (ev_.get("gap_analysis_set") or ev_.get("analysis_set") or {}).get("span")   # full-text gap span first
        if re.search(r"intention|ITT", served, re.I) and not re.search(r"modified|mITT", served, re.I):
            r = set_reading(span)
            row["served_itt_label"] = {"ITT_STATED": "SUPPORTED", "OTHER_SET_STATED": "CONTRADICTED", "NOT_STATED": "UNSUPPORTED"}[r]
            src = (a.get("gap_scope") or {}).get("analysis_set_source") if ev_.get("gap_analysis_set") else None
            if src and src != "OWN_REPORT" and row["served_itt_label"] == "SUPPORTED":
                row["served_itt_label"] = "SUPPORTED_BY_OTHER_REPORT" + ("_PLANNED" if src.endswith("PLANNED") else "")
            c["itt_" + row["served_itt_label"]] += 1
        out[k] = row
    n_adult = c["age_STATED"] + c["age_NOT_STATED"] + c["age_FLOOR_REMOVED"]
    n_itt = sum(v for k, v in c.items() if k.startswith("itt_"))
    summ = {"age": {"N": n_adult, "denominator": "adjudicated rows whose question says 'adults'", "STATED": c["age_STATED"], "NOT_STATED": c["age_NOT_STATED"], "FLOOR_REMOVED": c["age_FLOOR_REMOVED"]},
            "served_itt_label": {"N": n_itt, "denominator": "adjudicated rows whose served analysis_set says intention-to-treat (not modified)",
                                 "SUPPORTED": c["itt_SUPPORTED"], "SUPPORTED_BY_OTHER_REPORT": c["itt_SUPPORTED_BY_OTHER_REPORT"],
                                 "SUPPORTED_BY_OTHER_REPORT_PLANNED": c["itt_SUPPORTED_BY_OTHER_REPORT_PLANNED"],
                                 "CONTRADICTED": c["itt_CONTRADICTED"], "UNSUPPORTED": c["itt_UNSUPPORTED"]}}
    json.dump({"summary": summ, "rows": out}, open(os.path.join(ROOT, "evidence/sweeps/entry_age_and_analysis_set.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(json.dumps(summ, indent=1))
    print("age not STATED:", {k: v["age"] for k, v in out.items() if v.get("age") not in (None, "STATED")})


if __name__ == "__main__":
    main()
