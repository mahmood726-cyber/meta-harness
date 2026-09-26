"""Write the held-source manifest for Mashayekhi 2020 (colchicine-postop-af): SOURCE_INTERNALLY_INCONSISTENT, every
inconsistency a verbatim span at its offset in the committed text extraction (universal newlines)."""
import hashlib, json, os, sys
ROOT = sys.argv[1]
D = "outputs/handover/colchicine_poaf_sources"
PDF = f"{D}/held/ipp-6-e11.pdf"
TXT = f"{D}/ipp-6-e11.pdf.txt"
raw = open(os.path.join(ROOT, TXT), "rb").read()
text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
sha = lambda p: hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()

WANT = [  # kind, verbatim anchor (must occur exactly once), what it states
    ("key_point_240_patients", "Key point In a double-blind clinical trial study conducted on 240 patients", "randomised total stated as 240"),
    ("methods_120_per_arm", "120 subjects in  the experimental group", "120 per arm (colchicine)"),
    ("methods_120_control", "and 120 subjects in the control group", "120 per arm (placebo)"),
    ("flow_randomized_81", "Randomized (n= 81)", "flow diagram: 81 randomised"),
    ("flow_allocated_colchicine_29", "Allocated to intervention (n=29)", "flow diagram: 29 allocated to colchicine"),
    ("flow_allocated_placebo_52", "Allocated to control (n= 52)", "flow diagram: 52 allocated to placebo"),
    ("table_headings_29_52", "Comparison of quantitative variables at the beginning of research in two groups Variable Colchicine (n=29) Placebo (n=52)", "baseline tables headed n=29 / n=52"),
    ("pps_counts_equal_group_sizes", "was 12.1 percent (n = 29) in colchicine group", "PPS events 29 (12.1%) = the whole colchicine group size"),
    ("af_row_7_vs_13_under_29_52", "Atrial fibrillation 7(23.9%) 13(25.7%)", "AF 7 vs 13; 23.9%/25.7% fit neither 29/52 nor 120/120"),
]
spans = {}
import re
for kind, anchor, _ in WANT:
    # whitespace in the extraction (line breaks, doubled spaces) is not known in advance: match the anchor's words
    # with \s+ between them, require exactly ONE match, and record the EXACT matched bytes and offset
    pat = re.compile(r"\s+".join(re.escape(w) for w in anchor.split()))
    ms = list(pat.finditer(text))
    if len(ms) != 1:
        sys.exit(f"REFUSED: anchor {anchor!r} matches {len(ms)} times")
    spans[kind] = {"span": ms[0].group(0), "offset": ms[0].start()}
manifest = {
    "slug": "colchicine-postop-af",
    "contract": "held source: document identity + sha256, verbatim spans at offsets in the committed text extraction; "
                "a decision of SOURCE_INTERNALLY_INCONSISTENT means the document is HELD and read, and its own numbers "
                "cannot be reconciled into one set of arm denominators: not pooled, and not 'not retrieved'",
    "acquired_by": "evidence lane (Claude Opus 5.5), 2026-09-26, from the external review of colchicine-postop-af",
    "sources": [{
        "source_id": "MASHAYEKHI_2020_IPP", "kind": "JOURNAL_ARTICLE_OA", "source_level": 1,
        "query": "https://doi.org/10.15171/ipp.2020.11 -> https://immunopathol.com/PDF/ipp-6-e11.pdf",
        "licence": "CC BY 4.0 (creativecommons.org/licenses/by/4.0/, stated on the article page)",
        "fetched_utc": "2026-09-26T20:50:38Z", "extractor": "pypdf 6.13.1, '### PAGE n' markers",
        "document_path": PDF, "document_sha256": sha(PDF),
        "extracted_text_path": TXT, "extracted_text_sha256": sha(TXT), "state": "RAN_OK",
        "decisions": [{
            "trial": "Mashayekhi 2020", "trial_key": "DOI 10.15171/ipp.2020.11",
            "outcome": "postoperative atrial fibrillation (reported as a postpericardiotomy-syndrome component)",
            "decision": "SOURCE_INTERNALLY_INCONSISTENT", "rule_id": "source-state:internal-consistency-v1",
            "reason": ("The held article states 240 randomised / 120 per arm in its text, 81 randomised with 29 vs 52 "
                       "allocated in its flow diagram and table headings, and reports atrial fibrillation as 7 (23.9%) vs "
                       "13 (25.7%): the percentages fit neither denominator set. No single pair of arm denominators can "
                       "be read from the document, so no effect can be extracted. Held; not pooled; not 'not retrieved'."),
            "inconsistencies": {k: why for k, _, why in WANT},
            "source_conflict": {"state": "SOURCE_INTERNALLY_INCONSISTENT", "spans_preserved": spans},
        }],
    }],
}
out = os.path.join(ROOT, D, "regulatory_sources_colchicine_poaf.json")
open(out, "w", encoding="utf-8", newline="\n").write(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
print("wrote", out, len(spans), "spans")
