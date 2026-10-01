"""Read-only corpus audit: real producer/checker calls with in-memory DATA overlays.

No certificates, signatures, source bytes or served files are regenerated.
Run: python -X utf8 -m scripts.freedom2_acceptance
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import re
from unittest.mock import patch
import xml.etree.ElementTree as ET

from scripts import build_bundle as producer, verify_bundle as verifier
from harness import gate

ROOT = Path(__file__).resolve().parents[1]
SLUG = "glp1-ra-mace-t2d"
PREFIX = f"reviews/{SLUG}/"
EXPECTED = {
    "baseline": None, "reorder_records": None, "reorder_pool_records": None,
    "freedom_decimal_normalisation": None,
    "freedom_wrong_row": "ANALYSIS_IDENTITY_MISMATCH",
    "freedom_mixed_row": "TUPLE_NOT_IN_ANY_CANDIDATE_SPAN",
    "freedom_numeric_prefix": "TUPLE_NOT_IN_ANY_CANDIDATE_SPAN",
    "sustain6_mi_as_mace": "ENDPOINT_INCOMPATIBLE",
    "amplitudeo_renal_as_mace": "ENDPOINT_INCOMPATIBLE",
}


def mutate(case, review, records, bundle):
    evidence = {}
    if case == "reorder_records":
        records["records"].reverse()
    elif case == "reorder_pool_records":
        bundle["pooled_reference"]["inputs"].reverse()
    elif case.startswith("freedom_"):
        fact = next(f for f in review["held_regulatory_facts"] if f["trial"] == "FREEDOM-CVO")
        triples = re.findall(r"(\d+\.\d+) \((\d+\.\d+), (\d+\.\d+)\)", fact["decision"]["span"])
        assert len(triples) == 2, "Held table shape changed"
        correct, wrong = [tuple(map(float, t)) for t in triples]
        assert correct != wrong and correct[2] != wrong[2]
        values = {"freedom_wrong_row": wrong,
                  "freedom_mixed_row": (correct[0], correct[1], wrong[2]),
                  "freedom_numeric_prefix": (float(str(correct[0])[:-1]), *correct[1:]),
                  "freedom_decimal_normalisation": correct}[case]
        effect = fact["decision"]["effect"]
        evidence = {"before": copy.deepcopy(effect), "source_span": fact["decision"]["span"]}
        effect.update(zip(("estimate", "ci_low", "ci_high"), values))
        if case == "freedom_decimal_normalisation":
            lexeme = json.dumps(effect).replace(str(correct[0]), f"{correct[0]:.3f}", 1)
            assert json.loads(lexeme) == effect
            fact["decision"]["effect"] = json.loads(lexeme)
            evidence["numeric_lexeme"] = lexeme
        evidence["after"] = copy.deepcopy(effect)
    elif case in ("sustain6_mi_as_mace", "amplitudeo_renal_as_mace"):
        name, clause_pattern = {
            "sustain6_mi_as_mace": ("SUSTAIN-6", r"Nonfatal myocardial infarction occurred.*?\)"),
            "amplitudeo_renal_as_mace": ("AMPLITUDE-O", r"A composite renal outcome event.*?hazard ratio.*?\)"),
        }[case]
        matches = [r for r in records["records"] if name in r.get("abstract", "")]
        assert len(matches) == 1, "Trial evidence changed: selector must remain unique"
        record = matches[0]
        clauses = re.findall(clause_pattern, record["abstract"])
        assert len(clauses) == 1, "Alternate result clause missing or ambiguous"
        clause = clauses[0]
        tuples = re.findall(r"hazard ratio, (\d+\.\d+); 95% CI, (\d+\.\d+) to (\d+\.\d+)", clause)
        assert len(tuples) == 1, "Alternate tuple missing or ambiguous"
        primary = next(o for o in review["outcomes"] if o.get("primary"))
        source_id = "PMID " + str(record["id"]).removeprefix("PMID ")
        trials = [t for t in primary["trials"] if t["id"] == source_id]
        assert len(trials) == 1
        trial = trials[0]
        pmid = trial["id"].removeprefix("PMID ")
        acquisitions = list((ROOT / "docs/acquisitions" / SLUG).glob(f"*/{pmid}.xml"))
        assert len(acquisitions) == 1
        xml = ET.fromstring(acquisitions[0].read_bytes())
        assert xml.findtext(".//MedlineCitation/PMID") == pmid
        acquired = " ".join("".join(e.itertext()) for e in xml.findall(".//AbstractText"))
        assert verifier.normalize(clause) in verifier.normalize(acquired), "Clause not in acquired abstract"
        evidence = {"source_id": source_id, "acquired_ref": acquisitions[0].relative_to(ROOT).as_posix(),
                    "clause": clause, "before": {k: trial[k] for k in ("effect", "ci_low", "ci_high", "endpoint_result_span")}}
        values = tuple(map(float, tuples[0]))
        assert values != tuple(trial[k] for k in ("effect", "ci_low", "ci_high"))
        trial.update(zip(("effect", "ci_low", "ci_high"), values))
        trial["endpoint_result_span"] = clause
        evidence["after"] = {k: trial[k] for k in evidence["before"]}
    return evidence


def run_case(case):
    store = verifier.Store(str(ROOT / "docs"), None)
    review = store.json(PREFIX + "review.json")
    bundle = store.json(PREFIX + "BUNDLE.json")
    records = store.json(f"cache/{SLUG}/records.json")
    original_cache = dict(store.cache)
    evidence = mutate(case, review, records, bundle)
    read_json = producer._read_json

    def read_data(path):
        if path == ROOT / "docs" / PREFIX / "review.json":
            return copy.deepcopy(review)
        if path == ROOT / "cache" / SLUG / "records.json":
            return copy.deepcopy(records)
        return read_json(path)

    with patch.object(producer, "_read_json", side_effect=read_data):
        generated, problems = producer.build(SLUG, check_only=True)
    integrity_prefixes = ("harness/", "scripts/", "docs/", "cache/", "certificate input", "outputs/",
                          "review.json does not hash to the certificate's review_sha256")
    integrity = [p for p in problems if p.startswith(integrity_prefixes)]
    semantic = [p for p in problems if p not in integrity]
    # Propagate only generated witness DATA. Keep the release/certificate bytes and
    # declared digests intact, so mutations are also honestly visible to integrity.
    bundle["regulatory_facts"] = generated["regulatory_facts"]
    bundle["verification_rows"] = generated["verification_rows"]
    if case == "reorder_pool_records":
        generated["pooled_reference"]["inputs"].reverse()
        _, extra = verifier.check_pool_contract(review, json.loads(json.dumps(generated, allow_nan=False)), records)
        semantic.extend(extra)
    for path, value in ((PREFIX + "review.json", review), (PREFIX + "BUNDLE.json", bundle),
                        ):
        # Preserve unchanged originals exactly; do not create formatting-only digest failures.
        if json.loads(original_cache[path]) != value:
            store.cache[path] = (json.dumps(value, ensure_ascii=False) + "\n").encode("utf-8")
    # Permute iteration at the records deserialization boundary, as in F6's
    # producer input control; retain original source bytes and all digest checks.
    original_json = store.json
    if case == "reorder_records":
        store.json = lambda path: copy.deepcopy(records) if path == f"cache/{SLUG}/records.json" else original_json(path)
    report = verifier.run(store, SLUG, None)
    # The real publication bundle gate consumes the same data; no gate is mocked.
    with patch.object(verifier, "Store", return_value=store):
        reasons = gate.check_bundle_pool(ROOT / "docs" / PREFIX)
    store.cache = original_cache
    store.json = original_json
    restored = all(store.get(p) == raw for p, raw in original_cache.items())
    result = {"case": case, "expected": EXPECTED[case], "mutation": evidence,
              "producer": {"verdict": "REFUSE" if problems else "PASS", "integrity": integrity, "semantics": semantic,
                           "bindings": [{"trial": f["trial"], "binding": f["tuple_to_identity_binding"]} for f in generated["regulatory_facts"]]},
              "independent_verifier": {k: report.get(k) for k in ("verdict", "verdicts", "failure_categories", "regulatory_facts")},
              "publication_bundle_gate": {"verdict": "REFUSE" if reasons else "PASS", "reasons": reasons},
              "full_producer_renderer_publication_route": "NOT_REACHED (served rebuild/signing prohibited)",
              "restore_byte_identical": restored}
    first = report["failure_categories"]["semantics"]
    result["first_semantic"] = {"producer": semantic[0] if semantic else None, "verifier": first[0] if first else None}
    expected = EXPECTED[case]
    result["intended_semantics_credited"] = (all(s is not None and s.startswith(expected + " ") for s in result["first_semantic"].values())
                                               if expected else not semantic and not first)
    print(json.dumps({"case": case, "producer": result["producer"]["verdict"], "verifier": report["verdict"],
                      "publication_bundle_gate": result["publication_bundle_gate"]["verdict"],
                      "first_semantic": result["first_semantic"], "credited": result["intended_semantics_credited"]}, ensure_ascii=False), flush=True)
    return result


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cases", nargs="+", choices=list(EXPECTED))
    ap.add_argument("--served-mirror", action="store_true",
                    help="Measure the unchanged served verifier against the recorded mutations")
    args = ap.parse_args()
    if args.served_mirror:
        audit_served_mirror()
        return
    # Hash the served corpus without copying it. Nothing in this runner writes there.
    def hashes():
        return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (ROOT / "docs").rglob("*") if p.is_file()}
    before = hashes()
    old = json.loads((ROOT / "freedom2.json").read_text(encoding="utf-8")) if args.cases else None
    results = []
    for case in args.cases or EXPECTED:
        try:
            results.append(run_case(case))
        except Exception as exc:
            import traceback
            results.append({"case": case, "verdict": "NOT_REACHED", "error": str(exc), "traceback": traceback.format_exc()})
            print(case, "NOT_REACHED", repr(exc), flush=True)
    if old:
        replacements = {r["case"]: r for r in results}
        previous = [r for r in old["cases"] if r["case"] in replacements]
        results = [replacements.get(r["case"], r) for r in old["cases"]]
    output = {"command": "python -X utf8 -m scripts.freedom2_acceptance" + (" --cases " + " ".join(args.cases) if args.cases else ""), "cases": results,
              "served_corpus_byte_identical": before == hashes(), "served_files_checked": len(before),
              "scope": "producer check-only emission boundary, independent verifier, publication bundle gate; no full rebuild"}
    if old:
        output["previous_attempts"] = old.get("previous_attempts", []) + previous
        output["served_corpus_byte_identical"] &= old["served_corpus_byte_identical"]
    data = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    assert len(data.encode("utf-8")) < 20_000_000
    (ROOT / "freedom2.json").write_text(data, encoding="utf-8", newline="\n")


def audit_served_mirror():
    import importlib.util
    spec = importlib.util.spec_from_file_location("freedom2_served_verifier", ROOT / "docs/scripts/verify_bundle.py")
    served = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(served)
    output = json.loads((ROOT / "freedom2.json").read_text(encoding="utf-8"))
    comparisons = []
    for case in EXPECTED:
        store = served.Store(str(ROOT / "docs"), None)
        review, bundle = store.json(PREFIX + "review.json"), store.json(PREFIX + "BUNDLE.json")
        records = store.json(f"cache/{SLUG}/records.json")
        original = dict(store.cache)
        mutate(case, review, records, bundle)
        # Legacy bundle witness DATA remains legacy; the old route must independently
        # bind a changed decision even without a newly emitted row decomposition.
        for fact in bundle["regulatory_facts"]:
            owner = next(f for f in review["held_regulatory_facts"] if f["trial"] == fact["trial"])
            fact["decision"]["effect"] = owner["decision"]["effect"]
        for path, obj in ((PREFIX + "review.json", review), (PREFIX + "BUNDLE.json", bundle)):
            if json.loads(original[path]) != obj:
                store.cache[path] = json.dumps(obj).encode("utf-8")
        original_json = store.json
        if case == "reorder_records":
            store.json = lambda path: copy.deepcopy(records) if path == f"cache/{SLUG}/records.json" else original_json(path)
        report = served.run(store, SLUG, None)
        result = {"case": case, "verdict": report["verdict"], "failures": report["failures"],
                  "bindings": [{"trial": f["trial"], "binding": f["binding"]} for f in report["regulatory_facts"]]}
        comparisons.append(result)
        print(json.dumps(result, ensure_ascii=False), flush=True)
    output["served_mirror_comparison"] = {"command": "python -X utf8 -m scripts.freedom2_acceptance --served-mirror",
                                           "sha256": hashlib.sha256((ROOT / "docs/scripts/verify_bundle.py").read_bytes()).hexdigest(),
                                           "cases": comparisons}
    data = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    assert len(data.encode("utf-8")) < 20_000_000
    (ROOT / "freedom2.json").write_text(data, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
