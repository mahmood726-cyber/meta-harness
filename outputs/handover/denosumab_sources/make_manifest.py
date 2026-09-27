"""Held-source manifest for Koh 2016 (denosumab-vertebral-fracture; PMID 27189284, NCT01457950): the report is
internally inconsistent for SERIOUS ADVERSE EVENTS ONLY -- narrative 6 (9%) vs 2 (3%), Table 3 double-blind phase
2 (3) vs 1 (2) under n=69 / n=66 -- and the trial's own registry results give a third value, 7/69 vs 2/66. Scoped to
the SAE outcome; every other endpoint is untouched. Text spans verbatim at offsets in a committed text extraction of
the CC BY-NC 3.0 JATS XML (Europe PMC PMC4951467). The reviewer cites journal pages 910 (narrative) and 912 (Table 3);
the XML carries no page numbers, so those are recorded as the reviewer's citation, not verified here.
  python outputs/handover/denosumab_sources/make_manifest.py <repo root>"""
import hashlib, html, json, os, re, sys

ROOT = sys.argv[1]
D = "outputs/handover/denosumab_sources"
XML = "evidence/acquisition_cascade/held/Koh2016/PMC4951467.xml"
REG = "evidence/acquisition_cascade/held/Koh2016/NCT01457950.json"
TXT = f"{D}/PMC4951467.txt"
sha = lambda p: hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()

xml = open(os.path.join(ROOT, XML), encoding="utf-8").read()
body = re.sub(r"<\?[^>]*\?>", " ", xml)                                  # processing instructions (image metadata)
body = re.sub(r"</?[A-Za-z][A-Za-z0-9:.-]*(?:\s[^<>]*)?/?>", " ", body)
body = re.sub(r"[ \t\r\f\v]+", " ", html.unescape(body))
body = re.sub(r"\s*\n\s*", "\n", body).strip()
os.makedirs(os.path.join(ROOT, D), exist_ok=True)
open(os.path.join(ROOT, TXT), "w", encoding="utf-8", newline="\n").write(
    "### PAGE 1\n(text extraction of the JATS XML; tags and processing instructions stripped, entities unescaped)\n"
    + body + "\n")
text = open(os.path.join(ROOT, TXT), encoding="utf-8").read()

WANT = [
    ("narrative_sae_6_vs_2", "SAEs occurred in 6 subjects (9%) in the denosumab group and 2 subjects (3%) in the placebo group",
     "Results narrative: SAEs 6 (9%) denosumab vs 2 (3%) placebo"),
    ("table3_phase_headings", "Double-blind phase Open-label extension Denosumab (n=69) Placebo (n=66)",
     "Table 3 headings: double-blind phase denosumab n=69, placebo n=66 (then the open-label extension)"),
    ("table3_sae_row", "Serious AEs (SAEs) 2 (3) 1 (2) 1 (2) 3 (5)",
     "Table 3 SAE row: double-blind 2 (3) vs 1 (2); open-label extension 1 (2) vs 3 (5)"),
]
spans = {}
for kind, anchor, _ in WANT:
    pat = re.compile(r"\s+".join(re.escape(w) for w in anchor.split()))
    ms = list(pat.finditer(text))
    if len(ms) != 1:
        sys.exit(f"REFUSED: anchor {anchor!r} matches {len(ms)} times")
    spans[kind] = {"span": ms[0].group(0), "offset": ms[0].start()}

reg = json.load(open(os.path.join(ROOT, REG), encoding="utf-8"))
eg = {g["id"]: g for g in reg["resultsSection"]["adverseEventsModule"]["eventGroups"]}
registry_value = {"path": REG, "sha256": sha(REG),
                  "randomized_phase_denosumab": f"{eg['EG000']['seriousNumAffected']}/{eg['EG000']['seriousNumAtRisk']}",
                  "randomized_phase_placebo": f"{eg['EG001']['seriousNumAffected']}/{eg['EG001']['seriousNumAtRisk']}",
                  "event_group_titles": [eg["EG000"]["title"], eg["EG001"]["title"]]}

manifest = {
    "slug": "denosumab-vertebral-fracture",
    "contract": ("held source: document identity + sha256, verbatim spans at offsets in the committed text extraction; "
                 "SOURCE_INTERNALLY_INCONSISTENT with scope_outcomes: held, and its own numbers cannot be reconciled "
                 "for THOSE endpoints; other endpoints untouched"),
    "acquired_by": "evidence lane (Claude Opus 5.5), 2026-09-27, acquisition cascade (ATTEMPTS.jsonl target 'Koh2016')",
    "sources": [{
        "source_id": "KOH_2016_YMJ", "kind": "JOURNAL_ARTICLE_OA", "source_level": 1,
        "query": "Europe PMC fullTextXML PMC4951467 (DOI 10.3349/ymj.2016.57.4.905)",
        "licence": "CC BY-NC 3.0 (stated in the JATS <license>)",
        "extractor": "JATS tag + processing-instruction strip; single '### PAGE 1' marker (XML has no pages)",
        "document_path": XML, "document_sha256": sha(XML),
        "extracted_text_path": TXT, "extracted_text_sha256": sha(TXT), "state": "RAN_OK",
        "decisions": [{
            "trial": "Koh 2016", "trial_key": "PMID 27189284", "nct": "NCT01457950",
            "outcome": "serious adverse events (double-blind phase)",
            "decision": "SOURCE_INTERNALLY_INCONSISTENT", "rule_id": "source-state:internal-consistency-v1",
            "scope_outcomes": ["Serious adverse events"],
            "scope_basis": "the conflict is in the SAE counts only; the phase split and denominators agree across locations",
            "reason": ("The held article reports serious adverse events as 6 (9%) denosumab vs 2 (3%) placebo in its results "
                       "narrative, but its Table 3 gives the double-blind phase as 2 (3) vs 1 (2) under n=69 / n=66; no "
                       "phase or combination of phases in Table 3 gives 6 vs 2. The trial's own registry results give a "
                       "third value for the randomised phase, 7/69 vs 2/66. Held; not pooled for SAEs; other endpoints "
                       "untouched."),
            "reviewer_page_citation": "narrative p910, Table 3 p912 (journal pagination; not verifiable from the XML)",
            "inconsistencies": {k: why for k, _, why in WANT},
            "source_conflict": {"state": "SOURCE_INTERNALLY_INCONSISTENT", "spans_preserved": spans},
            "other_source_values": {"registry_results": registry_value, "state": "SOURCE_EFFECT_CONFLICT"},
        }],
    }],
}
out = os.path.join(ROOT, D, "regulatory_sources_denosumab.json")
open(out, "w", encoding="utf-8", newline="\n").write(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
print("wrote", os.path.relpath(out, ROOT), len(spans), "verbatim spans; registry", registry_value["randomized_phase_denosumab"],
      "vs", registry_value["randomized_phase_placebo"])
