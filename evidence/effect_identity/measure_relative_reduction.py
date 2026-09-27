"""Offline reduction census and patch radius; read pinned git objects, never rebuild pages.

The broad lexical inventory intentionally includes qualitative/background statements,
absolute/continuous reductions, endpoint definitions and redundant ratio prose. These
are report-only candidates, not recovered trial effects.
"""
from __future__ import annotations

from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import re
import sys
import types

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from harness import extract  # noqa: E402

spec = importlib.util.spec_from_file_location("reduction_corpus", ROOT / "evidence/fixtures/build_effect_identity_fixture.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
BASELINE_CODE = "32b4f3a314dd0bdc74a9433393930a8bbf0ee342"
CUE = re.compile(r"\breduc(?:e[ds]?|ing|tions?)\b|relative decrease", re.I)


def baseline():
    module = types.ModuleType("harness._reduction_baseline")
    module.__package__ = "harness"
    code = builder.git("show", f"{BASELINE_CODE}:harness/extract.py").decode("utf-8")
    exec(compile(code, "<pinned baseline extract.py>", "exec"), module.__dict__)
    return module


def effects(module, text):
    text = module._norm(text)
    return [{"phrase": m.group(0), "label": m.group(1), "effect": list(effect)}
            for m in module._EFFECT.finditer(text)
            if (effect := module._effect_from_match(m, text))]


def build():
    old = baseline()
    slugs, blobs, paths = builder.pinned_inputs()
    rows, scan, missing, transforms, changes = [], [], [], [], []
    included_n = held_n = outcome_n = 0
    for slug in slugs:
        review = blobs[f"docs/reviews/{slug}/review.json"]
        topic = blobs[f"topics/{slug}.json"]
        specs = [topic["primary_outcome"], *topic.get("secondary_outcomes", []), *topic.get("harm_outcomes", [])]
        records = {str(r["id"]): r for r in blobs[paths[slug]]["records"]} if paths[slug] else {}
        for item in review["screening"]["records"]:
            if item["decision"] != "include":
                continue
            included_n += 1
            pid = str(item["id"])
            abstract = records.get(pid, {}).get("abstract") or ""
            if not abstract:
                missing.append({"slug": slug, "id": pid})
                continue
            held_n += 1
            for sentence in old._sentences(abstract):
                if CUE.search(sentence):
                    found = effects(old, sentence)
                    scan.append({"slug": slug, "id": pid, "sentence": sentence,
                                 "baseline_effects": found,
                                 "captured_reduction": any("reduction" in h["label"].lower() for h in found)})
        for oi, outcome in enumerate(review["outcomes"]):
            outcome_n += 1
            outcome_spec = next(s for s in specs if s["name"] == outcome["name"])
            for ri, row in enumerate(outcome.get("trials") or []):
                pid = str(row.get("id", "")).replace("PMID ", "")
                abstract = records.get(pid, {}).get("abstract") or ""
                identity = dict(slug=slug, outcome=outcome["name"], trial_id=row.get("id"), outcome_index=oi, row_index=ri)
                served = [row.get(k) for k in ("scale", "effect", "ci_low", "ci_high")]
                record = dict(identity, served=served, held_abstract=bool(abstract), reduction_matches=[])
                # Source quotation first, complete held sentences second. Exact
                # Decimal complements independently check the old extractor.
                for origin, text in [("row quotation", row.get("source") or ""), ("held abstract", abstract)]:
                    for sentence in old._sentences(text):
                        for hit in effects(old, sentence):
                            if "reduction" not in hit["label"].lower():
                                continue
                            m = old._EFFECT.search(old._norm(hit["phrase"]))
                            pt, lo, hi = (Decimal(m.group(i)) for i in (2, 3, 4))
                            expected = [float(1 - pt), float(1 - hi), float(1 - lo)]
                            # A quotation explicitly naming reduction is retained
                            # even if incorrect; abstract fallback binds all numbers.
                            if origin == "held abstract" and expected != served[1:]:
                                continue
                            detail = dict(origin=origin, phrase=hit["phrase"], sentence=sentence,
                                          named_measure="RR", expected=expected,
                                          point_exact=served[1] == expected[0],
                                          ci_exact=served[2:] == expected[1:], measure_exact=served[0] == "RR")
                            record["reduction_matches"].append(detail)
                    if record["reduction_matches"]:
                        break
                if record["reduction_matches"]:
                    transforms.append(record)
                # Radius is extraction replay, not sequential source hierarchy,
                # overrides, pooling, or deployment. Every served row stays in N.
                kwargs = dict(declared_composite=extract.declared_is_composite(outcome["name"]),
                              estimand=outcome_spec.get("estimand"))
                args = (abstract, outcome_spec.get("keywords", []),
                        topic.get("intervention_terms", ["colchicine"]),
                        topic.get("comparator_terms", ["placebo", "control"]))
                before, after = old.extract_trial(*args, **kwargs), extract.extract_trial(*args, **kwargs)
                record["extraction_byte_identical"] = json.dumps(before, sort_keys=True) == json.dumps(after, sort_keys=True)
                if not record["extraction_byte_identical"]:
                    changes.append(dict(identity, before=before, after=after))
                # Also compare all phrase extractions, including published-source
                # quotations that were not selected by extract_trial.
                record["source_effects_byte_identical"] = all(
                    json.dumps(effects(old, text), sort_keys=True) == json.dumps(effects(extract, text), sort_keys=True)
                    for text in (row.get("source") or "", abstract))
                rows.append(record)
    return dict(pin=builder.PINNED, baseline_code=BASELINE_CODE, pages=len(slugs), outcomes=outcome_n,
                rows=rows, transforms=transforms, extraction_changes=changes,
                included_records=included_n, held_included_abstracts=held_n,
                missing_included_abstracts=missing, reduction_sentence_scan=scan)


def name(row):
    return (f"{row['slug']} / {row['outcome']} / {row['trial_id']} "
            f"[outcome {row['outcome_index']}, row {row['row_index']}]")


def markdown(data):
    scan = data["reduction_sentence_scan"]
    uncaptured = [s for s in scan if not s["captured_reduction"]]
    lines = ["# Relative-reduction census", "", f"Served data: `{data['pin']}`.",
             f"Pre-patch extractor: `{data['baseline_code']}`. Current extractor used only for patch-radius comparison.", "",
             "| Input | Static vs dynamic / hardcode disclosure |", "|---|---|",
             "| Git pins and lexical scan pattern | Static audit scope, not research data |",
             "| IDs, quotations, values, denominators | Read from pinned review/topic/cache git objects |",
             "| Complements and patch radius | Computed; Decimal arithmetic, no invented effects or CIs |", "",
             f"Inspected {len(data['rows'])} served rows across {data['outcomes']} outcomes and {data['pages']} pages; "
             f"{sum(r['served'][1] is not None for r in data['rows'])} rows carry a reported effect. "
             f"{len(data['transforms'])} rows derive from captured reduction phrases.", "",
             "## Every reduction-derived served row", ""]
    for row in data["transforms"]:
        lines += [f"- **{name(row)}**; served `{row['served']}`."]
        for hit in row["reduction_matches"]:
            lines += [f"  Named measure {hit['named_measure']}; point exact={hit['point_exact']}; "
                      f"CI exact={hit['ci_exact']}; measure exact={hit['measure_exact']}; read from {hit['origin']}.",
                      "", f"> {hit['sentence']}", ""]
    lines += ["## Patch radius", "",
              f"{len(data['extraction_changes'])} of {len(data['rows'])} served-row abstract extractions change. "
              f"{sum(not r['source_effects_byte_identical'] for r in data['rows'])} of {len(data['rows'])} rows "
              "change any source-quotation/held-abstract effect match. This is a parser replay; served JSON/pages are not rebuilt.", ""]
    for row in data["extraction_changes"]:
        lines.append(f"- {name(row)}: `{row['before']}` -> `{row['after']}`")
    lines += ["## Included-trial abstract scan (report only)", "",
              f"{data['held_included_abstracts']} of {data['included_records']} screening-included topic/record pairs have held abstracts; "
              f"{len(data['missing_included_abstracts'])} unavailable pairs remain in N and are listed below. "
              "Repeated trials across topics remain separate pairs. Scope includes included trials with no served effect.", "",
              f"The deliberately broad lexical screen found {len(scan)} sentences: {len(uncaptured)} of {len(scan)} "
              "have no captured reduction complement, and the remainder have a captured complement. "
              "This denominator counts sentences, not quantitative effects or errors. All are quoted below. "
              "A direct ratio in a sentence is separately disclosed; qualitative prose, absolute/continuous changes, "
              "endpoint thresholds and trial names are not asserted to be recoverable ratio effects.", ""]
    for i, row in enumerate(scan, 1):
        state = "CAPTURED_COMPLEMENT" if row["captured_reduction"] else "NO_CAPTURED_COMPLEMENT"
        lines += [f"### {i}. {row['slug']} / {row['id']} — {state}", "", f"> {row['sentence']}", "",
                  f"Baseline effect+CI matches: `{[h['effect'] for h in row['baseline_effects']]}`.", ""]
    lines += ["## Missing included abstracts", ""]
    lines += [f"- {r['slug']} / {r['id']}" for r in data["missing_included_abstracts"]]
    lines += ["", "Reproduce: `python evidence/effect_identity/measure_relative_reduction.py`.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    data = build()
    dest = Path(__file__).resolve().parent
    (dest / "relative_reduction_census.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (dest / "relative_reduction_census.md").write_text(markdown(data), encoding="utf-8")
    print(json.dumps({k: v for k, v in data.items() if k not in
                      ("rows", "transforms", "reduction_sentence_scan", "missing_included_abstracts")}, ensure_ascii=True))
