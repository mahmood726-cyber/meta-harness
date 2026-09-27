"""Held-source manifest for Akrami 2021 (colchicine-secondary-cv-prevention, PMID 34876021): the ANALYSIS POPULATION is
internally inconsistent for the SAFETY denominator. Scoped to the topic's harm outcomes; the efficacy rows are judged
on their own grounds (refused: estimand mismatch, docs/refusals.json).

Text spans are verbatim at offsets in a committed text extraction of the CC BY 4.0 JATS XML (Europe PMC PMC8650300).
The CONSORT diagram is an IMAGE: its labels are carried as a declared MODEL TRANSCRIPTION pinned to the image sha256,
never as verbatim spans; the transcribed numbers (122, 129, 120) are each corroborated by a verbatim text span, the
diagram's 'Lost to follow-up (n=2)' and 'Randomized (n=251)' are image-only.
  python outputs/handover/colchicine_secondary_cv_sources/make_manifest.py <repo root>"""
import hashlib, html, json, os, re, sys

ROOT = sys.argv[1]
D = "outputs/handover/colchicine_secondary_cv_sources"
XML = "evidence/acquisition_cascade/held/Akrami/PMC8650300.xml"
FIG = "evidence/acquisition_cascade/held/Akrami/Fig1_CONSORT.png"
TXT = f"{D}/PMC8650300.txt"
sha = lambda p: hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()

# text extraction: JATS has no pages; one '### PAGE 1' marker covers the article (the loader requires a marker)
xml = open(os.path.join(ROOT, XML), encoding="utf-8").read()
body = re.sub(r"</?[A-Za-z][A-Za-z0-9:.-]*(?:\s[^<>]*)?/?>", " ", xml)
body = re.sub(r"[ \t\r\f\v]+", " ", html.unescape(body))
body = re.sub(r"\s*\n\s*", "\n", body).strip()
os.makedirs(os.path.join(ROOT, D), exist_ok=True)
open(os.path.join(ROOT, TXT), "w", encoding="utf-8", newline="\n").write(
    "### PAGE 1\n(text extraction of the JATS XML; tags stripped, entities unescaped, whitespace collapsed)\n" + body + "\n")
text = open(os.path.join(ROOT, TXT), encoding="utf-8").read()

WANT = [  # kind, verbatim anchor (exactly one match), what it states
    ("results_allocated_122_vs_129", "122 and 129 subjects were assigned to colchicine and the placebo groups",
     "Results text: 122 colchicine / 129 placebo assigned"),
    ("abstract_assigned_120_vs_129", "120 assigned to the colchicine group and 129 assigned to the placebo group",
     "Abstract: 120 colchicine / 129 placebo assigned"),
    ("abstract_total_249", "A total of 249 patients were recruited", "Abstract: 249 recruited (120 + 129)"),
    ("table1_headings_120_vs_129", "Colchicine (n = 120) Placebo (n = 129)", "Table 1 headings: n = 120 / n = 129"),
    ("discussion_two_left_for_intolerance", "two patients left the study due to drug intolerance",
     "Discussion: the two colchicine exclusions were for drug INTOLERANCE (an adverse effect)"),
    ("discussion_excluded_for_intolerance", "did not tolerate the effects, thereby were excluded from the study",
     "Discussion: excluded because they did not tolerate colchicine"),
    ("abstract_gi_15_vs_3", "15 (12.5%) in the colchicine group and 3 (2.5%) in the controls",
     "Abstract GI: 15 (12.5%) vs 3 (2.5%); 3/129 = 2.3%, 3/120 = 2.5%: the placebo percentage fits 120, not the 129 randomised"),
]
spans = {}
for kind, anchor, _ in WANT:
    pat = re.compile(r"\s+".join(re.escape(w) for w in anchor.split()))
    ms = list(pat.finditer(text))
    if len(ms) != 1:
        sys.exit(f"REFUSED: anchor {anchor!r} matches {len(ms)} times")
    spans[kind] = {"span": ms[0].group(0), "offset": ms[0].start()}

FIGURE = {  # model transcription of the image, label -> as printed
    "randomized_251": "Randomized (n=251)",
    "allocated_colchicine_122": "Allocated to receive colchicine (n=122)",
    "allocated_placebo_129": "Allocated to receive placebo (n=129)",
    "colchicine_lost_to_follow_up_2": "*Lost to follow-up (n=2)",
    "placebo_lost_to_follow_up_0": "*Lost to follow-up (n=0)",
    "analyzed_colchicine_120": "Analyzed (n=120)",
    "analyzed_placebo_129": "Analyzed (n=129)",
}
manifest = {
    "slug": "colchicine-secondary-cv-prevention",
    "contract": ("held source: document identity + sha256, verbatim spans at offsets in the committed text extraction; "
                 "SOURCE_INTERNALLY_INCONSISTENT with scope_outcomes: the document is HELD and read, and its own numbers "
                 "cannot be reconciled into one denominator FOR THOSE ENDPOINTS: held out of those pools, other "
                 "endpoints untouched"),
    "acquired_by": "evidence lane (Claude Opus 5.5), 2026-09-27, acquisition cascade (ATTEMPTS.jsonl target 'Akrami')",
    "sources": [{
        "source_id": "AKRAMI_2021_BMC_CVD", "kind": "JOURNAL_ARTICLE_OA", "source_level": 1,
        "query": "Europe PMC fullTextXML PMC8650300 (DOI 10.1186/s12872-021-02393-9)",
        "licence": "CC BY 4.0 (creativecommons.org/licenses/by/4.0/, stated in the JATS <license>)",
        "extractor": "JATS tag strip + html.unescape; single '### PAGE 1' marker (XML has no pages)",
        "document_path": XML, "document_sha256": sha(XML),
        "extracted_text_path": TXT, "extracted_text_sha256": sha(TXT), "state": "RAN_OK",
        "decisions": [{
            "trial": "Akrami 2021", "trial_key": "PMID 34876021",
            "outcome": "safety denominator (harm outcomes)",
            "decision": "SOURCE_INTERNALLY_INCONSISTENT", "rule_id": "source-state:internal-consistency-v1",
            "scope_outcomes": ["Gastrointestinal adverse effects", "Non-cardiovascular death"],
            "scope_basis": ("the conflict is in the SAFETY denominator: two colchicine patients left for drug "
                            "intolerance (an adverse effect) and are outside the analysed 120, and the flow diagram "
                            "files them as lost to follow-up. Harm outcomes are in scope; the efficacy composite is "
                            "refused on its own grounds (estimand mismatch)."),
            "reason": ("The held article gives the colchicine arm as 122 randomised (Results) and 120 (abstract, Table 1 "
                       "headings, 'Analyzed'), with 249 recruited in the abstract against 251 randomised in the flow "
                       "diagram. The two colchicine exclusions are 'lost to follow-up' in the CONSORT diagram but left "
                       "'due to drug intolerance' in the Discussion, and the placebo GI percentage 3 (2.5%) fits 120 "
                       "rather than the 129 randomised. Patients excluded for intolerance are safety events outside the "
                       "safety denominator, so the GI count 15/120 vs 3/129 cannot be taken as one consistent set. "
                       "Held; not pooled for harm outcomes; not 'not retrieved'."),
            "inconsistencies": {k: why for k, _, why in WANT},
            "source_conflict": {"state": "SOURCE_INTERNALLY_INCONSISTENT", "spans_preserved": spans},
            "figure_transcription": {
                "image_path": FIG, "image_sha256": sha(FIG),
                "licence": "CC BY 4.0 (figure of the same article; fetched from the publisher's static host)",
                "method": ("MODEL VISUAL TRANSCRIPTION (Claude Opus 5.5, 2026-09-27) of the CONSORT image; NOT a "
                           "verbatim-verified span. Corroborated in text: 122, 129 and 120 each occur in a verbatim span "
                           "above. Image-only: 'Lost to follow-up (n=2)' and 'Randomized (n=251)'."),
                "labels": FIGURE,
                "corroborated_by_text": {"allocated_colchicine_122": "results_allocated_122_vs_129",
                                         "allocated_placebo_129": "results_allocated_122_vs_129",
                                         "analyzed_colchicine_120": "table1_headings_120_vs_129",
                                         "analyzed_placebo_129": "table1_headings_120_vs_129"},
                "image_only": ["colchicine_lost_to_follow_up_2", "placebo_lost_to_follow_up_0", "randomized_251"],
            },
        }],
    }],
}
out = os.path.join(ROOT, D, "regulatory_sources_colchicine_secondary_cv.json")
open(out, "w", encoding="utf-8", newline="\n").write(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
print("wrote", os.path.relpath(out, ROOT), len(spans), "verbatim spans")
