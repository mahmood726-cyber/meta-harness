"""DPP-4 review fixtures (2026-09-27): bind OMNeON HHF (verbatim source, not the abridged record), CARMELINA HHF (results
sentence of the accepted manuscript, committed as an excerpt), and TECOS 3-point MACE (EMA Januvia SmPC Table 3: ITT,
Cox model stratified by region; distinct from the 4-point primary). Writes the hand entries into
cache/dpp4-mace-t2d/verified_effects.json and the TECOS version chain into docs/source_versions.json.
  python outputs/handover/dpp4_sources/make_dpp4_rows.py"""
import hashlib, json, os, re, shutil

D = "outputs/handover/dpp4_sources"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
OMN = "evidence/acquisition_cascade/held/OMNeON/PMC5594521.xml"
CAR_TXT = "evidence/acquisition_cascade/held/CARMELINA/unpaywall.txt"          # local only (manuscript, other-oa)
CAR_PDF = "evidence/acquisition_cascade/held/CARMELINA/unpaywall.pdf"
EMA_TXT_HELD = "evidence/acquisition_cascade/held/TECOS/ema_januvia_product_information_en.txt"
EMA_PDF = "evidence/acquisition_cascade/held/TECOS/ema_januvia_product_information_en.pdf"
EMA_TXT = f"{D}/ema_januvia_product_information_en.txt"
CAR_EX = f"{D}/CARMELINA_HHF_results_sentence.txt"
MACE3 = "3-point major adverse cardiovascular events"
HHF = "Hospitalization for heart failure"
os.makedirs(D, exist_ok=True)

# --- EMA SmPC text extraction (EMA public document; reuse with acknowledgement), committed with its PDF's sha256.
# pypdf text, whitespace collapsed WITHIN each page (a table row wraps across lines in the raw extraction)
pages = re.split(r"^### PAGE (\d+)\s*$", open(EMA_TXT_HELD, encoding="utf-8").read(), flags=re.M)
out_pages = [f"### PAGE {pages[i]}\n{re.sub(r'[ \t\r\n]+', ' ', pages[i + 1]).strip()}\n" for i in range(1, len(pages) - 1, 2)]
open(EMA_TXT, "w", encoding="utf-8", newline="\n").write(
    "# EMA Januvia (sitagliptin) product information, English: text extraction (pypdf 6, whitespace collapsed within "
    f"each page). Source: https://www.ema.europa.eu/en/documents/product-information/januvia-epar-product-information_en.pdf "
    f"(EMA public document, reproduced with acknowledgement). PDF sha256: {sha(EMA_PDF)}\n" + "".join(out_pages))
ema_flat = open(EMA_TXT, encoding="utf-8").read()

# --- CARMELINA: ONE verbatim sentence of the accepted manuscript (not redistributed), located exactly once
car = re.sub(r"\s+", " ", open(CAR_TXT, encoding="utf-8").read())
m = re.search(r"Hospitalization for heart failure occurred in 209 of 3494 patients randomized to linagliptin.*?"
              r"\(HR, 0\.90; 95% CI, 0\.74-1\.08;", car)
assert m and car.count(m.group(0)) == 1, "CARMELINA sentence not located exactly once"
open(CAR_EX, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT (one verbatim sentence) of a held document that is not redistributed\n"
    "# source: accepted manuscript, Rosenstock et al. JAMA 2019 (CARMELINA), repository copy "
    "http://publicatio.bibl.u-szeged.hu/27237/1/Rosenstock.pdf (licence other-oa, via Unpaywall)\n"
    f"# held_sha256 (PDF, local): {sha(CAR_PDF)}\n\n" + m.group(0) + "\n")

OMN_SPAN = ("The hHF outcome occurred in 20/2092 patients in the omarigliptin group (0.96%; 0.51/100 patient-years) and "
            "33/2100 patients in the placebo group (1.57%; 0.85/100 patient-years), with an HR of 0.60 (95% CI 0.35, 1.05)")
TECOS_SPAN = ("Secondary Composite Endpoint (Cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke) "
              "745 (10.2) 3.6 746 (10.2) 3.6 0.99 (0.89–1.10)")
assert TECOS_SPAN in ema_flat, "TECOS row not in the EMA text"
POP = "Analysis in the Intention -to- Treat Population Number of patients 7,332 7,339"
MODEL = "Based on a Cox model stratified by region"
assert POP in ema_flat and MODEL in ema_flat

# --- TECOS Table 3 as a TABLE (each row on its own, with its headings), so the 3-point row cannot borrow the 4-point
# row's definition: in the flattened page text the whole table is one run and the binder rightly refused to choose.
PRIMARY_ROW = ("Primary Composite Endpoint (Cardiovascular death, nonfatal myocardial infarction, nonfatal stroke, or "
               "hospitali sation for unstable angina) 839 (11.4) 4.1 851 (11.6) 4.2")
assert PRIMARY_ROW in ema_flat, "4-point row not in the EMA text"
TAB = f"{D}/TECOS_EMA_SmPC_table3.tables.txt"
T3_ROW = ("Secondary Composite Endpoint (Cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke) | "
          "745 (10.2) | 3.6 | 746 (10.2) | 3.6 | 0.99 (0.89–1.10) | <0.001")
open(TAB, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT of EMA Januvia SmPC section 5.1 Table 3 (TECOS). Every value is verbatim from the committed text extraction "
    f"{EMA_TXT} (sha256 {sha(EMA_TXT)}); the CELL BOUNDARIES are this excerpt's segmentation of that text run.\n"
    f"# footnote (verbatim): '† {MODEL}.'\n\n"
    "=== TABLES (excerpt) ===\n"
    "TABLE Table 3. Rates of Composite Cardiovascular Outcomes and Key Secondary Outcomes\n"
    "Outcome | Sitagliptin 100 mg N (%) | Incidence rate per 100 patient-years | Placebo N (%) | "
    "Incidence rate per 100 patient-years | Hazard Ratio (95% CI) | p-value\n"
    "Analysis in the Intention-to-Treat Population\n"
    "Number of patients | 7,332 | | 7,339\n"
    "Primary Composite Endpoint (Cardiovascular death, nonfatal myocardial infarction, nonfatal stroke, or "
    "hospitalisation for unstable angina) | 839 (11.4) | 4.1 | 851 (11.6) | 4.2 | 0.98 (0.89–1.08) | <0.001\n"
    + T3_ROW + "\n")

vp = "cache/dpp4-mace-t2d/verified_effects.json"
raw = open(vp, encoding="utf-8").read()
ve = json.loads(raw)


def as_list(v):
    return v if isinstance(v, list) else ([v] if v else [])


def put(pid, entry):
    rows = [r for r in as_list(ve.get(pid)) if r.get("outcome") != entry["outcome"]]
    old = next((r for r in as_list(ve.get(pid)) if r.get("outcome") == entry["outcome"]), None)
    if old:
        entry["supersedes"] = {k: old.get(k) for k in ("provenance", "kind", "reason", "document_ref") if old.get(k)}
    ve[pid] = rows + [entry]


put("28893244", {"outcome": HHF, "effect": 0.60, "ci_low": 0.35, "ci_high": 1.05, "scale": "HR",
                 "kind": "extracted_effect", "provenance": "fulltext_verified", "source_level": 1,
                 "document_ref": OMN, "document_sha256": sha(OMN), "source_span": OMN_SPAN,
                 "reason": ("OMNeON hospitalisation for heart failure, from the VERBATIM publication (open access, CC BY): "
                            "20/2092 vs 33/2100, HR 0.60 (0.35-1.05). The committed record abstract is an ALTERED "
                            "abridgement that omits this result, so 'not found in the abstract' was said of text that "
                            "is not the abstract.")})
put("30418475", {"outcome": HHF, "effect": 0.90, "ci_low": 0.74, "ci_high": 1.08, "scale": "HR",
                 "kind": "extracted_effect", "provenance": "fulltext_verified", "source_level": 1,
                 "document_ref": CAR_EX, "document_sha256": sha(CAR_EX), "source_span": m.group(0),
                 "reason": ("CARMELINA hospitalisation for heart failure, 209 of 3494 vs 226 of 3485, HR 0.90 (0.74-1.08), "
                            "from the results of the accepted manuscript (Table 2 carries the same row); bound to a "
                            "committed one-sentence excerpt.")})
put("26052984", {"outcome": MACE3, "effect": 0.99, "ci_low": 0.89, "ci_high": 1.10, "scale": "HR",
                 "kind": "extracted_effect", "provenance": "fulltext_verified", "source_level": 1,
                 "document_ref": TAB, "document_sha256": sha(TAB), "source_span": T3_ROW,
                 "analysis_population": "intention-to-treat, 7,332 vs 7,339", "analysis_model": "Cox model stratified by region",
                 # the abstract's headline value is the 4-POINT primary: this entry overrides it for THIS outcome only
                 "override": True,
                 "reason": ("TECOS 3-point MACE (CV death, nonfatal MI, nonfatal stroke) from the EMA Januvia SmPC Table 3, "
                            "745/7,332 vs 746/7,339, HR 0.99 (0.89-1.10), intention-to-treat, Cox model stratified by "
                            "region. This is TECOS's SECONDARY composite, distinct from its 4-point primary (839 vs 851, "
                            "HR 0.98 (0.89-1.08)), which is not this review's estimand.")})
open(vp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(ve, indent=1 if raw.startswith('{\n "') else 2, ensure_ascii=False) + ("\n" if raw.endswith("\n") else ""))

# --- the TECOS 3-point MACE version chain
sp = "docs/source_versions.json"
sv = json.load(open(sp, encoding="utf-8"))
W = lambda p, s: {"path": p, "sha256": sha(p), "span": s}
sv["topics"]["dpp4-mace-t2d"] = [{
    "chain_id": "TECOS:3-point-MACE", "trial_id": "PMID 26052984", "outcome": MACE3,
    "versions": [
        {"version_id": "v0-article-2015", "kind": "ORIGINAL", "date": "2015-07-16",
         "source": "NEJM 2015 (PMID 26052984): the verbatim abstract reports the 4-point primary only",
         "not_held_reason": "the full text (where the 3-point secondary composite is tabulated) is not open: publisher 403",
         "value": None},
        {"version_id": "v1-ema-smpc", "kind": "REGULATORY", "date": "EMA Januvia product information (current)",
         "source": "EMA Januvia SmPC section 5.1, Table 3 (intention-to-treat; Cox model stratified by region)",
         "held": W(EMA_TXT, TECOS_SPAN),
         "cells": {"population": POP, "model": MODEL,
                   "not this row": "Primary Composite Endpoint 839 (11.4) vs 851 (11.6), HR 0.98 (0.89-1.08) (4-point)"},
         "value": {"ai": 745, "n1i": 7332, "ci": 746, "n2i": 7339, "effect": 0.99, "ci_low": 0.89, "ci_high": 1.10}}],
    "governing": {"state": "DECIDED", "version_id": "v1-ema-smpc",
                  "reason": ("the regulator's table is the held source of TECOS's 3-point MACE (the article's abstract "
                             "gives only the 4-point primary; its full text is not open); bound with its population "
                             "(ITT) and model (Cox stratified by region)")}}]
open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(sv, indent=1, ensure_ascii=False) + "\n")
print("wrote CARMELINA excerpt, EMA text, 3 hand entries, TECOS version chain")
