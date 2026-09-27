"""Pinned held-label census; current parser output and independently authored readings.

Run from any directory: python evidence/fixtures/build_armparse_fixture.py
No network, current cache reads, screening reruns, or parser modifications.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from harness import arm_parse, lexicon  # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
HERE = Path(__file__).resolve().parent
MARK = "another intervention: "
TRIGGER = re.compile(r"placebo|sham|dummy|matching", re.I)

# Manual label readings, NOT generated from arm_parse, regex matches to topic
# keywords, or the served decisions. Unknown labels fail closed for new review.
# Generic/inert or explicitly off-topic interventions in the enumerated topics.
ABSENT_LABELS = {
    "Placebo", "placebo", "Placebo Oral Tablet", "Placebo oral tablet",
    "Placebo Tablet", "Placebo Tablets", "Spironolactone-Placebo",
    "EG-009A Placebo", "Placebo + SOC", "Sham procedure",
    "Empagliflozin placebo", "LY2403021 placebo", "Placebo DPI",
    "Mazdutide Placebo", "Placebo of Dapagliflozin", "Placebo KI1001",
    "sham acupuncture", "placebo warfarin", "Placebo soybean oil",
    "Placebo (matching oil drops)", "Placebo - Microcrystalline Cellulose",
    "placebo Intervention", "Placebo of Enalapril", "Placebo to Enalapril",
    "enalapril matching placebo", "GIP placebo", "Placebo (liraglutide)",
    "Placebo (administered by PDS290 pen-injector)",
    "Placebo 1.5 ml, prefilled pen-injector for subcutaneous injection solution",
    "Balcinrenone 100mg matching Placebo", "Balcinrenone 50mg matching Placebo",
    "Matching placebo", "Placebo (unspecified)", "Placebo (0.9% saline)",
    "Placebo; Normal Saline",
}
MATCHED_LABELS = {
    "Colchicine-Placebo", "Dapagliflozin matching placebo",
    "Linagliptin placebo", "Potassium Chloride + Placebo for Empagliflozin",
    "Finerenone Placebo", "placebo Circadin", "placebo circadin",
    "Placebo metformin", "placebo edoxaban", "Placebo of LCZ696",
    "Placebo of LCZ696 (Sacubitril/Valsartan)", "Placebo to LCZ696",
    "sacubitril/valsartan (LCZ696) matching placebo",
    "Placebo (semaglutide)", "Placebo semaglutide",
    "Semaglutide 1.34 mg/ml placebo", "Dapagliflozin matching Placebo",
    "Placebo (for Atorvastatin)",
}
SPECIAL_READINGS = {
    "Placebo plus metformin": ("ACTIVE", "Metformin is co-administered with a placebo, not replaced by it."),
    "Vitamin D3 + fish oil/fish oil placebo": ("VARIES_WITHIN_ARM", "Fish oil and its placebo are alternative levels inside the listed label."),
    "Vitamin D3 placebo + fish oil/fish oil placebo": ("VARIES_WITHIN_ARM", "Fish oil and its placebo are alternative levels; vitamin D assignment does not resolve them."),
    "Balcinrenone/dapagliflozin 15 mg/10 mg and matching placebo for dapagliflozin 10 mg": ("ACTIVE", "The fixed combination supplies dapagliflozin; the additional matching placebo does not remove that exposure. Slashes denote ingredients and doses, not allocation levels."),
    "Balcinrenone/dapagliflozin 40 mg/10 mg and matching placebo for dapagliflozin 10 mg": ("ACTIVE", "The fixed combination supplies dapagliflozin; the additional matching placebo does not remove that exposure. Slashes denote ingredients and doses, not allocation levels."),
    "Dapagliflozin 10 mg and matching placebo for balcinrenone/dapa gliflozin": ("ACTIVE", "Active dapagliflozin is explicitly co-administered with placebo for the combination."),
    "Placebo of Iron Carboxymaltose": ("MATCHED_PLACEBO", "The label identifies placebo for iron carboxymaltose, read as the topic's ferric carboxymaltose; this is a semantic reading, not an additional parser keyword."),
    "Placebo CagriSema": ("UNCERTAIN", "A placebo is explicit, so no active exposure is stated; the label alone does not expand CagriSema into the topic agent. Matching identity is unresolved without importing external product knowledge."),
}


def reading(label):
    if label in SPECIAL_READINGS:
        state, basis = SPECIAL_READINGS[label]
    elif label in MATCHED_LABELS:
        state, basis = "MATCHED_PLACEBO", "A placebo replaces the named topic agent; slash in a fixed combination or mg/ml dose does not denote randomized levels."
    elif label in ABSENT_LABELS:
        state, basis = "ABSENT", "Generic/inert control or placebo/sham for an off-topic intervention; no active topic exposure is stated."
    else:
        raise ValueError(f"Unreviewed placebo/sham/dummy/matching label: {label!r}")
    return {"exposure": state, "basis": basis}


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True).stdout


def sources():
    git("cat-file", "-e", PINNED + "^{commit}")
    reviews = sorted(p for p in git("ls-tree", "-r", "--name-only", PINNED, "docs/reviews").decode().splitlines()
                     if p.count("/") == 3 and p.endswith("/review.json"))
    if len(reviews) != 32:
        raise ValueError(f"Expected 32 pinned served topics, got {len(reviews)}")
    slugs = [p.split("/")[2] for p in reviews]
    paths = sorted(reviews + [p for s in slugs for p in
                   (f"cache/{s}/records.json", f"cache/{s}/registry_designs.json", f"topics/{s}.json")])
    # One git process; read exact byte lengths (including embedded newlines).
    data = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT,
                          input="".join(f"{PINNED}:{p}\n" for p in paths).encode(),
                          capture_output=True, check=True).stdout
    pos, objects, hashes = 0, {}, {}
    for path in paths:
        end = data.index(b"\n", pos)
        header = data[pos:end].split()
        if len(header) != 3 or header[1] != b"blob":
            raise ValueError(f"Missing pinned blob: {path}")
        size = int(header[2])
        raw = data[end + 1:end + 1 + size]
        pos = end + size + 2
        objects[path] = json.loads(raw)
        hashes[path] = hashlib.sha256(raw).hexdigest()
    return slugs, objects, hashes


def decision_for(rec, decisions):
    # Display IDs can be 'ACRONYM <separator> NCT########'. Never join by title,
    # arbitrary substring, or family ID (which could join a secondary report).
    rid = str(rec["id"])
    matches = [d for d in decisions if str(d["id"]) == rid or
               (rec.get("id_type") == "nct" and rid in re.findall(r"\bNCT\d{8}\b", str(d["id"])))]
    if len(matches) > 1:
        raise ValueError(f"Ambiguous served decision for {rid}")
    return matches[0] if matches else None


def controls():
    out = []
    for i, label in enumerate([
        "placebo for empagliflozin", "placebo empagliflozin", "empagliflozin placebo",
        "empagliflozin-matching placebo", "matching placebo for empagliflozin",
        "placebo (empagliflozin)", "placebo to match empagliflozin",
        "placebo Circadin", "fish oil placebo",
    ]):
        kws = ["Circadin"] if "Circadin" in label else ["fish oil"] if "fish oil" in label else ["empagliflozin"]
        out.append({"id": f"__control_matched_{i}", "labels": [label], "interest": kws,
                    "expected_exposures": ["MATCHED_PLACEBO"]})
    out.extend([
        {"id": "__control_collapsed", "labels": ["fish oil/fish oil placebo"], "interest": ["fish oil"], "expected_exposures": ["VARIES_WITHIN_ARM"]},
        {"id": "__control_plain", "labels": ["Placebo"], "interest": ["empagliflozin"], "expected_exposures": ["ABSENT"]},
        {"id": "__control_miro", "labels": ["Balcinrenone 15 mg + Dapagliflozin 10 mg", "Placebo + Dapagliflozin 10 mg"], "interest": ["dapagliflozin"], "expected_every": True},
        {"id": "__control_doac", "labels": ["Dabigatran Etexilate Oral Capsule", "Rivaroxaban Oral Tablet"], "interest": ["dabigatran", "rivaroxaban"], "expected_every": True},
        {"id": "__control_design_phrase", "labels": ["Placebo-controlled empagliflozin 10 mg"], "interest": ["empagliflozin"], "READING": "Design phrase, not an arm; arm exposure is not determinable from this phrase. Observed output only, no desired parser assertion."},
    ])
    for c in out:
        c["parses"] = [arm_parse.parse_arm(l) for l in c["labels"]]
        c["exposures"] = [arm_parse.exposure(a, c["interest"]) for a in c["parses"]]
        c["interest_in_every_arm"] = arm_parse.interest_in_every_arm(c["labels"], c["interest"])
    return out


def tally(values):
    values = list(values)
    return {"fires": sum(bool(v) for v in values), "of": len(values)}


def build():
    slugs, src, hashes = sources()
    rows, topics, served = [], [], []
    for slug in slugs:
        topic = src[f"topics/{slug}.json"]
        cache = src[f"cache/{slug}/records.json"]
        registry = src[f"cache/{slug}/registry_designs.json"]
        decisions = src[f"docs/reviews/{slug}/review.json"]["screening"]["records"]
        kws = topic.get("intervention_terms") or topic.get("include", {}).get("intervention_any") or []
        contrast_kws = topic.get("arm_object", {}).get("contrast", {}).get("drug_any") or kws
        screen_kws = topic.get("include", {}).get("intervention_any") or []
        served.extend(dict(d, slug=slug) for d in decisions)
        counts = {}
        for collection in ("records", "ctgov"):
            if collection not in cache or not isinstance(cache[collection], list):
                raise ValueError(f"Missing collection {slug}/{collection}")
            selected = 0
            for index, rec in enumerate(cache[collection]):
                labels = rec.get("interventions") or []
                if len(labels) < 2:
                    continue
                if not all(isinstance(l, str) and l.strip() for l in labels):
                    raise ValueError(f"Invalid listed label: {slug}/{rec['id']}")
                selected += 1
                d = decision_for(rec, decisions)
                nct = str(rec.get("nct") or rec["id"]).upper()
                reg = registry.get(nct) if re.fullmatch(r"NCT\d{8}", nct) else None
                design = arm_parse.design_object(reg)
                arms = []
                for label in labels:
                    parsed = arm_parse.parse_arm(label)
                    state = arm_parse.exposure(parsed, kws)
                    rd = reading(label) if TRIGGER.search(label) else None
                    arms.append({"parse": parsed, "exposure": state, "READING": rd,
                                 "reading_disagrees": rd is not None and rd["exposure"] != state})
                every = arm_parse.interest_in_every_arm(labels, kws)
                rows.append({"slug": slug, "id": rec["id"], "id_type": rec.get("id_type"),
                             "title": rec.get("title"), "acronym": rec.get("acronym"),
                             "source": f"cache/{slug}/records.json", "collection": collection, "index": index,
                             "interest": kws, "include_intervention_any": screen_kws,
                             "arms": arms, "interest_in_every_arm": every,
                             "screen_fallback_every_arm": arm_parse.interest_in_every_arm(
                                 [lexicon.fold(l).lower() for l in labels], [lexicon.fold(k).lower() for k in kws]),
                             "registry_source": f"cache/{slug}/registry_designs.json", "registry_key": nct,
                             "registry_design": reg, "design": design,
                             "ordered_contrast_interest": contrast_kws,
                             "ordered_contrasts": arm_parse.ordered_contrasts(labels, contrast_kws, design),
                             "served_screening": d,
                             "served_x_contrast_disagrees": d is not None and (d["rule_id"] == "X-CONTRAST") != every})
            counts[collection] = {"fires": selected, "of": len(cache[collection])}
        topics.append({"slug": slug, "interest": kws, "include_intervention_any": screen_kws, "held_records_with_multiple_interventions": counts})
    arms = [a for r in rows for a in r["arms"]]
    contrasts = [c for r in rows for c in r["ordered_contrasts"]]
    readings = [a for a in arms if a["READING"] is not None]
    xs = [d for d in served if d["rule_id"] == "X-CONTRAST"]
    fallback = [d for d in xs if MARK in (d.get("reason") or "")]
    fallback_rows = []
    for d in fallback:
        matches = [r for r in rows if r["slug"] == d["slug"] and r["served_screening"] and r["served_screening"]["id"] == d["id"]]
        if len(matches) != 1:
            raise ValueError(f"Fallback decision lacks unique held multi-label row: {d['slug']} {d['id']}")
        r = matches[0]
        fallback_rows.append({"slug": r["slug"], "id": r["id"], "interest_in_every_arm": r["interest_in_every_arm"],
                              "broken_by": sorted({a["exposure"] for a in r["arms"] if a["exposure"] != "ACTIVE"})})
    totals = {
        "held_records_with_multiple_interventions": {"fires": len(rows), "of": sum(v["of"] for t in topics for v in t["held_records_with_multiple_interventions"].values())},
        "interest_in_every_arm": tally(r["interest_in_every_arm"] for r in rows),
        "served_decision_available": tally(r["served_screening"] is not None for r in rows),
        "served_x_contrast_disagrees": tally(r["served_x_contrast_disagrees"] for r in rows if r["served_screening"] is not None),
        "reading_required": tally(a["READING"] is not None for a in arms),
        "reading_disagrees": tally(a["reading_disagrees"] for a in readings),
        "reading_uncertain": tally(a["READING"]["exposure"] == "UNCERTAIN" for a in readings),
        **{f"exposure_{s}": tally(a["exposure"] == s for a in arms) for s in ("ACTIVE", "MATCHED_PLACEBO", "VARIES_WITHIN_ARM", "ABSENT")},
        **{f"contrast_{s}": tally(c["state"] == s for c in contrasts) for s in ("CLEAN", "CONFOUNDED")},
        "served_x_contrast_all_topics": tally(d["rule_id"] == "X-CONTRAST" for d in served),
        "arm_list_fallback_of_x_contrast": {"fires": len(fallback), "of": len(xs)},
        "fallback_not_every_arm": tally(not r["interest_in_every_arm"] for r in fallback_rows),
        "fallback_matched_placebo": tally("MATCHED_PLACEBO" in r["broken_by"] for r in fallback_rows),
    }
    expected = {"served_x_contrast_all_topics": 15, "arm_list_fallback_of_x_contrast": 7,
                "fallback_not_every_arm": 6, "fallback_matched_placebo": 2}
    return {"pinned_commit": PINNED, "source_sha256": hashes, "topics": topics,
            "records": rows, "totals": totals, "served_x_contrast_decisions": xs,
            "fallback_records": fallback_rows,
            "readme_comparison": {k: {"readme": v, "observed": totals[k]["fires"], "agrees": v == totals[k]["fires"]} for k, v in expected.items()},
            "controls_excluded_from_totals": controls()}


def report(f):
    lines = ["# Arm parser pinned corpus fixture", "", f"Source commit: `{PINNED}`. Parser: current worktree `harness/arm_parse.py` (unchanged).", "",
             "All 32 served topics are enumerated, including topics with no qualifying records. The unit is a held occurrence in `records[]` or `ctgov[]` with at least two listed interventions; repeated studies across topics/collections remain separate. These are intervention lists, not guaranteed randomized arms. No inferred arm expansion is performed.", "",
             "Served decisions come only from `screening.records`. Exact IDs or bounded NCT identifiers in display IDs are joined; missing decisions are null. Registry rows and source SHA-256 hashes are retained. No live registry lookup or screening rerun is used.", "",
             "| Static input | Dynamic computation |", "|---|---|",
             "| Pinned commit, 32-topic coverage contract | Git blobs and SHA-256 manifest |",
             "| Explicit independently authored label-reading tables and rationales | Coverage checked; unknown triggered labels fail closed |",
             "| Synthetic control labels and expected invariants | Actual parser output, excluded from every corpus total |",
             "| README comparison values 15 / 7 / 6 / 2 | Held-record recomputation; disagreement reported, never tuned |", "",
             "Interest uses `intervention_terms`, falling back to `include.intervention_any`, matching the README measurement and screen caller. Both source term lists are retained; `screen_fallback_every_arm` separately uses folded interest terms. Ordered contrasts use the arm-object caller's `arm_object.contrast.drug_any` override when present, otherwise the primary interest; the effective list is retained as `ordered_contrast_interest`. Each contrast carries the held registry design. The reading column is manually authored independently of parser output; generic placebo is ABSENT, named topic placebo MATCHED_PLACEBO, actual co-administration ACTIVE. UNCERTAIN is a non-equivalent reading, included in disagreement totals. It is not a validated clinical truth label.", "",
             "## Totals and denominators", "", "| Property | fires | of (N) |", "|---|---:|---:|"]
    for k, v in f["totals"].items():
        lines.append(f"| {k} | {v['fires']} | {v['of']} |")
    lines += ["", "N definitions: held-record selection uses all held records; every-arm and availability use qualifying records; decision disagreement uses qualifying records with a served decision; exposure and reading-required use all listed label occurrences; reading disagreements/uncertainty use triggered label occurrences; contrast states use emitted ordered pairs. Served X-CONTRAST uses all served screening records; fallback uses all X-CONTRAST decisions; fallback causes use fallback decisions. Controls are excluded throughout.", "",
              "## README measurement comparison", ""]
    for k, c in f["readme_comparison"].items():
        lines.append(f"- {k}: README {c['readme']}; observed {c['observed']}; {'agrees' if c['agrees'] else 'DISAGREES'}.")
    lines += ["", "The measurement's six 'wrong' exclusions refer only to the arm-list route. Other-route disagreement with the every-arm predicate does not establish a wrong screening decision. The collapsed fish-oil case is separately VARIES_WITHIN_ARM, not counted as MATCHED_PLACEBO.", "", "## Every served-decision / every-arm disagreement", "",
              "Both directions are listed: served X-CONTRAST with every-arm false, and other served rules with every-arm true. These are predicate comparisons, not new screening verdicts.", ""]
    for r in f["records"]:
        if r["served_x_contrast_disagrees"]:
            d = r["served_screening"]
            lines.append(f"- **{r['slug']} / {r['id']}** ({r['collection']}[{r['index']}]): {d['decision']} / {d['rule_id']}; every-arm={r['interest_in_every_arm']}. Served reason: {d['reason']}")
    lines += ["", "## Every independent READING disagreement", ""]
    for r in f["records"]:
        for a in r["arms"]:
            if a["reading_disagrees"]:
                lines.append(f"- **{r['slug']} / {r['id']}** ({r['collection']}[{r['index']}]): `{a['parse']['label']}` — parser **{a['exposure']}**, READING **{a['READING']['exposure']}**. {a['READING']['basis']}")
    lines += ["", "## Held records without a served record decision", "",
              "No same-record screening decision exists for these identifiers in the pinned `screening.records`. A PMID decision sharing a trial family is not substituted for a CT.gov record decision. These records remain in label/contrast totals, with `served_screening: null`, and are excluded only from decision-disagreement denominators.", ""]
    for r in f["records"]:
        if r["served_screening"] is None:
            lines.append(f"- {r['slug']} / {r['id']} ({r['collection']}[{r['index']}]).")
    lines += ["", "## Controls and limitations", ""]
    for c in f["controls_excluded_from_totals"]:
        lines.append(f"- `{c['id']}`: {json.dumps(c['labels'], ensure_ascii=False)} → {', '.join(c['exposures'])}; every-arm={c['interest_in_every_arm']}.")
    lines += ["", "The design-phrase control is not an arm: its observed result is recorded without asserting a desired answer. The simplified MIRO control stays True, whereas the held MIRO fixed-combination slash labels need separate scrutiny (see readings above). Source labels, topic vocabularies, and parser output have not been repaired to make this fixture pass.", "",
              "Regenerate: `python evidence/fixtures/build_armparse_fixture.py`.", "Validate: `python -m pytest -q tests/test_armparse_corpus_fixture.py tests/test_matched_placebo.py`.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    fixture = build()
    (HERE / "armparse_corpus.json").write_text(json.dumps(fixture, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (HERE / "ARMPARSE_FIXTURE.md").write_text(report(fixture), encoding="utf-8", newline="\n")
    print(json.dumps(fixture["totals"], indent=2))
