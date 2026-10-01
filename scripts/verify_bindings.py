"""Verify the UNBOUND_LEGACY binding proposals BY ARTEFACT (never by the job's report).
For each campaign snapshot (argv[1:]): every row of rows.json has exactly one proposal; binding kind and admissibility are valid;
every quote is an EXACT substring of the named held text; the result span contains the row's served numbers; a bound row has a
definition span. Prints n of N per check and per outcome, and writes verify_bindings.json beside this script."""
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
KINDS = {"named_endpoint_resolved_to_definition_span", "result_span_enumerates_components", "registry_outcome_measure", "REMAINS_UNBOUND"}
ADMS = {"EXACT_TARGET", "NEAR_MATCH_DECLARED", "DIFFERENT_ENDPOINT", "UNBOUND"}


def held_text(root: Path, ref: str) -> str | None:
    """Text of 'cache/<slug>/ft_<id>.txt' (raw file) or 'cache/<slug>/records.json#<id>' (every string field of that record, plus
    its fulltext_by_pmid entry)."""
    if "#" in ref:
        path, rid = ref.split("#", 1)
        f = root / path
        if not f.exists():
            return None
        d = json.loads(f.read_text(encoding="utf-8"))
        recs = d.get("records") if isinstance(d, dict) else d
        rec = next((r for r in recs or [] if str(r.get("id")) == rid), None)
        parts = [v for v in (rec or {}).values() if isinstance(v, str)]
        ft = (d.get("fulltext_by_pmid") or {}).get(rid) if isinstance(d, dict) else None
        return "\n".join(parts + ([ft] if ft else [])) if (rec or ft) else None
    f = root / ref
    return f.read_text(encoding="utf-8") if f.exists() else None


def _norm(s: str) -> str:
    return " ".join((s or "").split())


def registry_tie_problems(snap: Path, p: dict, row: dict) -> list:
    m = re.search(r"ctgov/(NCT\d{8})__\d+\.txt$", (p.get("endpoint_result_span") or {}).get("file") or "")
    if not m:
        return ["registry binding whose result is not a ctgov/<NCT>__<i>.txt file"]
    nct, own = m.group(1), re.sub(r"\s", "", str(row.get("trial_id") or ""))
    if own == nct:
        return []
    tie = p.get("registry_tie") or {}
    if not tie:
        return [f"registry binding to {nct} without a registry_tie"]
    probs = []
    pmid = re.sub(r"\D", "", own)
    f, _, rid = (tie.get("file") or "").partition("#")
    if rid and rid == pmid and f.endswith("records.json") and (snap / f).exists():
        d = json.loads((snap / f).read_text(encoding="utf-8"))
        rec = next((r for r in d.get("records") or [] if str(r.get("id")) == rid), {})
        if str(rec.get("nct") or "").upper() == nct:
            return []                                  # PubMed DataBank accession on the trial's own record
    text = held_text(snap, tie.get("file") or "")
    if text is None or _norm(tie.get("quote")) not in _norm(text):
        probs.append("registry_tie quote not an exact substring of its file")
    if nct not in (tie.get("quote") or ""):
        probs.append(f"registry_tie does not name {nct}")
    if not pmid or not re.search(rf"(records\.json#{pmid}$|ft_{pmid})", tie.get("file") or ""):
        probs.append(f"registry_tie is not from this trial's own record (PMID {pmid or '?'})")
    return probs


def has_served_number(row: dict) -> bool:
    nums = row.get("served_numbers") or {}
    return any(isinstance(v, (int, float)) and not isinstance(v, bool) for v in nums.values()) or         isinstance((row.get("served_effect") or {}).get("effect_estimate"), (int, float))


def numbers_in(quote: str, row: dict) -> bool:
    quote = (quote or "").replace("·", ".")        # Lancet decimals: '0·85'
    nums = row.get("served_numbers") or {}
    ints = [nums[k] for k in ("ai", "ci") if isinstance(nums.get(k), (int, float))]
    if ints:
        toks = set(re.findall(r"\d[\d,]*", quote or ""))
        return all(str(int(v)) in {t.replace(",", "") for t in toks} for v in ints)
    quote = quote.replace("−", "-")
    se = row.get("served_effect") or {}
    eff = se.get("effect_estimate")
    if isinstance(eff, (int, float)):
        if any(abs(float(t) - eff) < 0.006 for t in re.findall(r"\d+\.\d+", quote)):
            return True
        if se.get("estimand") == "MD":                 # the MD is served; the span holds the two arm means it is the difference of
            vals = [float(t) for t in re.findall(r"-?\d+(?:\.\d+)?", quote)]
            return any(abs((a - b) - eff) < 0.06 for i, a in enumerate(vals) for b in vals[i + 1:])
        return False
    means = [nums[k] for k in ("m1i", "m2i") if isinstance(nums.get(k), (int, float))]
    return bool(means) and all(any(abs(float(t) - m) < 0.051 for t in re.findall(r"-?\d+(?:\.\d+)?", quote or "")) for m in means)


report, problems, tally = [], [], Counter()
for snap in map(Path, sys.argv[1:]):
    rows = {r["row_key"]: r for r in json.loads((snap / "rows.json").read_text(encoding="utf-8"))}
    bf = snap / "bindings.json"
    props = json.loads(bf.read_text(encoding="utf-8")) if bf.exists() else []
    seen = Counter(p.get("row_key") for p in props)
    for key in rows:
        if seen[key] != 1:
            problems.append((snap.name, key, f"proposals for this row: {seen[key]}"))
    for p in props:
        key, row = p.get("row_key"), rows.get(p.get("row_key"))
        rec = {"snap": snap.name, "row_key": key, "binding": p.get("binding"), "admissibility": p.get("admissibility"), "problems": []}
        if row is None:
            rec["problems"].append("row_key not in rows.json")
        if p.get("binding") not in KINDS:
            rec["problems"].append(f"binding kind {p.get('binding')!r}")
        if p.get("admissibility") not in ADMS:
            rec["problems"].append(f"admissibility {p.get('admissibility')!r}")
        for field in ("endpoint_result_span", "endpoint_definition_span"):
            span = p.get(field)
            if not span:
                continue
            text = held_text(snap, span.get("file") or "")
            if text is None:
                rec["problems"].append(f"{field}: file not found {span.get('file')}")
            elif _norm(span.get("quote")) not in _norm(text):
                rec["problems"].append(f"{field}: quote not an exact substring of {span.get('file')}")
        if p.get("binding") != "REMAINS_UNBOUND":
            if p.get("binding") == "named_endpoint_resolved_to_definition_span" and not p.get("endpoint_definition_span"):
                rec["problems"].append("named endpoint without a definition span")
            if p.get("binding") == "registry_outcome_measure":
                rec["problems"] += registry_tie_problems(snap, p, row or {})
            if p.get("binding") == "result_span_enumerates_components" and not p.get("components"):
                rec["problems"].append("enumerates components but lists none")
            if row and not has_served_number(row):
                rec["uncheckable"] = "row carries no served number to find in the result span"
            elif row and not numbers_in((p.get("endpoint_result_span") or {}).get("quote"), row):
                rec["problems"].append("result span does not contain the served numbers")
        tally["failed" if rec["problems"] else ("uncheckable" if rec.get("uncheckable") else "verified")] += 1
        report.append(rec)
N = sum(len(json.loads((Path(s) / "rows.json").read_text(encoding="utf-8"))) for s in sys.argv[1:])
ok = [r for r in report if not r["problems"] and not r.get("uncheckable")]
unchk = [r for r in report if not r["problems"] and r.get("uncheckable")]
print(f"proposals: {len(report)} for {N} rows; coverage problems: {len(problems)}")
print(f"verified by artefact: {len(ok)} of {len(report)}")
print("verified, by binding:", dict(Counter(r["binding"] for r in ok)))
print("verified, by admissibility:", dict(Counter(r["admissibility"] for r in ok)))
print(f"uncheckable (quotes exact, but the row carries no served number): {len(unchk)}")
for r in unchk:
    print("  UNCHECKABLE", r["snap"], r["row_key"][:90], "|", r["binding"], r["admissibility"])
for s, k, m in problems:
    print("  COVERAGE", s, k, m)
for r in report:
    if r["problems"]:
        print("  FAIL", r["snap"], r["row_key"][:90], "|", "; ".join(r["problems"]))
Path(__file__).with_name("verify_bindings.json").write_text(json.dumps({"N": N, "report": report, "coverage": problems}, indent=1,
                                                                      ensure_ascii=False) + "\n", encoding="utf-8")
