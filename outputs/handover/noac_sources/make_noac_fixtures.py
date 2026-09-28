"""NOAC-AF review fixtures (2026-09-28). Every span below is asserted against held bytes before it is written.
 (1) RE-LY stroke/SE VERSION CHAIN: NEJM 2009 (134 vs 199 relayed; RR 0.66 (0.53-0.82) in the held abstract) -> FDA
     label Oct 2010 (134 vs 202, HR 0.65 (0.52, 0.81)) -> the investigators' 'Newly identified events in the RE-LY
     trial' (NEJM 2010, PMID 21047252: NOT held, publisher 403, not open access) -> FDA label Jan 2024 Table 11 and EMA
     Pradaxa SmPC Table 22 (135 vs 203, HR 0.65 (0.52, 0.81), randomised ITT). GOVERNING: DECIDED on the final
     randomised-ITT result held in both regulators' current documents. The served RE-LY row (dose_selection, the
     approved 150 mg arm) moves 0.66 -> 0.65: a served change (notice; Mahmood's signature).
 (2) MAJOR BLEEDING: RE-LY bound to the FDA Oct 2010 label Table 2 (399 vs 421, HR 0.93 (0.81, 1.07), randomised);
     its chain is PENDING (the NEJM 2009 Table 3 original 375 vs 397 is relayed; the EMA SmPC gives 409 vs 426 with no
     HR; FDA 2024 Table 3 350 vs 374, HR 0.97 is a DIFFERENT population -- treated, on treatment + 2 days). ROCKET-AF
     bound to the FDA label Table 5, 395 vs 386, HR 1.04 (0.90, 1.20), ON TREATMENT PLUS 2 DAYS (N 7111 vs 7125) --
     never the major + non-major clinically relevant composite 1.03 (0.96-1.11).
 (3) Edoxaban phase II publications linked to their registry-only entries (docs/registry_publications.json).
 (4) J-ROCKET AF (NCT00494871): an independent phase III trial absent from the inventory, entered as a known eligible
     trial with all three held analyses; not pooled pending the Japan-specific dose / INR compatibility decisions.
  PYTHONPATH=. python outputs/handover/noac_sources/make_noac_fixtures.py"""
import hashlib, json, os, re


def dump(path, data):
    # keep the file's own indentation, so a rewrite diffs only what changed
    ind = 1
    if os.path.exists(path):
        raw = open(path, encoding="utf-8").read()
        m = re.match(r"\{\n( +)\"", raw)
        ind = len(m.group(1)) if m else 1
    open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(data, indent=ind, ensure_ascii=False) + "\n")


SLUG = "noac-vs-warfarin-af-stroke"
D = "outputs/handover/noac_sources"
H = "evidence/acquisition_cascade/held"
X = "evidence/acquisition_cascade/excerpts"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
flat = lambda s: re.sub(r"\s+", " ", s).strip()
W = lambda p, s: {"path": p, "sha256": sha(p), "span": s}
SSE, MB = "Stroke or systemic embolism", "Major bleeding"
os.makedirs(D, exist_ok=True)


def present(text, span, where):
    # the EMA product information carries some tables twice (two formulations); a witness needs presence only
    assert flat(span) in flat(text), f"{where}: span not held: {span!r}"
    return flat(span)


def once(text, span, where):
    n = flat(text).count(flat(span))
    assert n == 1, f"{where}: span occurs {n} times: {span!r}"
    return flat(span)


# ------------------------------------------------------------------ held regulatory text (public domain: committed)
FDA10 = f"{H}/RE-LY-regulatory/fda_label_2010-10.txt"
FDA11 = f"{H}/RE-LY-regulatory/fda_label_2011-03.txt"
FDA24 = f"{H}/RE-LY-regulatory/fda_label_2024-01.txt"
RKT22 = f"{H}/ROCKET-AF-regulatory/fda_label_2022-03.txt"
RKT11 = f"{H}/ROCKET-AF-regulatory/fda_label_2011-11.txt"
T = {p: open(p, encoding="utf-8").read() for p in (FDA10, FDA11, FDA24, RKT22, RKT11)}

# EMA SmPC (EMA public document, reuse with acknowledgement): committed as a page-collapsed text extraction
EMA_PDF = f"{H}/RE-LY-regulatory/ema_pradaxa_product_information.pdf"
EMA_HELD = f"{H}/RE-LY-regulatory/ema_pradaxa_product_information.txt"
EMA = f"{D}/ema_pradaxa_product_information_en.txt"
pages = re.split(r"^### PAGE (\d+)\s*$", open(EMA_HELD, encoding="utf-8").read(), flags=re.M)
open(EMA, "w", encoding="utf-8", newline="\n").write(
    "# EMA Pradaxa (dabigatran etexilate) product information, English: text extraction (pypdf 6, whitespace collapsed "
    "within each page). Source: https://www.ema.europa.eu/en/documents/product-information/pradaxa-epar-product-"
    f"information_en.pdf (EMA public document, reproduced with acknowledgement). PDF sha256: {sha(EMA_PDF)}\n"
    + "".join(f"### PAGE {pages[i]}\n{flat(pages[i + 1])}\n" for i in range(1, len(pages) - 1, 2)))
T[EMA] = open(EMA, encoding="utf-8").read()

REC = f"cache/{SLUG}/records.json"
recs = {str(r["id"]): r for r in json.load(open(REC, encoding="utf-8"))["records"]}

# ------------------------------------------------------------------ (1) RE-LY stroke/SE spans
S_ABS = once(recs["19717844"]["abstract"], "150 mg of dabigatran (relative risk, 0.66; 95% CI, 0.53 to 0.82", "RE-LY abstract")
S10_N = once(T[FDA10], "Patients (%) with events 134 (2.2%) 183 (3%) 202 (3.4%)", "FDA 2010 Table 4")
S10_HR = once(T[FDA10], "Hazard ratio vs. warfarin (95% CI) 0.65 (0.52, 0.81) 0.90 (0.74,1.10)", "FDA 2010 Table 4")
S10_CAP = once(T[FDA10], "Table 4 First Occurrence of Stroke or Systemic Embolism in the RE-LY Study", "FDA 2010")
S24_N = once(T[FDA24], "Patients (% per yr) with events 135 (1.12%) 183 (1.54%) 203 (1.72%)", "FDA 2024 Table 11")
S24_HR = once(T[FDA24], "Hazard ratio vs warfarin (95% CI) 0.65 (0.52, 0.81) 0.89 (0.73, 1.09)", "FDA 2024 Table 11")
S24_CAP = once(T[FDA24], "Table 11 First Occurrence of Stroke or Systemic Embolism in the RE-LY Study* PRADAXA", "FDA 2024")
S24_ITT = "* Randomized ITT"
assert flat(S24_ITT) in flat(T[FDA24])
SEMA_N = present(T[EMA], "Incidences (%) 183 (1.54) 135 (1.12) 203 (1.72)", "EMA Table 22")
SEMA_HR = present(T[EMA], "0.89 (0.73, 1.09) 0.65 (0.52, 0.81)", "EMA Table 22")
SEMA_CAP = present(T[EMA], "Table 22: Analysis of first occurrence of stroke or systemic embolism (primary endpoint) during the study period in RE-LY", "EMA")

# ------------------------------------------------------------------ (2) major bleeding spans
B10 = once(T[FDA10], "Major bleed 399 (3.3) 421 (3.6) 0.93 (0.81, 1.07)", "FDA 2010 Table 2")
B10_N = once(T[FDA10], "Randomized patients 6076 6022", "FDA 2010 Table 2")
B11 = once(T[FDA11], "Major bleed 399 (3.3) 421 (3.6) 0.93 (0.81, 1.07)", "FDA 2011 Table 2")
B24 = once(T[FDA24], "Major Bleedingc 350 (3.47) 374 (3.58) 0.97 (0.84, 1.12)", "FDA 2024 Table 3")
B24_POP = once(T[FDA24], "aPatients during treatment or within 2 days of stopping study treatment.", "FDA 2024 Table 3")
BEMA = "Major bleeding 347 (2.92 %) 409 (3.40 %) 426 (3.61 %)"
assert flat(T[EMA]).count(BEMA) == 2, "EMA Table 14 row"               # section 4.8 and 5.1 both carry Table 14
BEMA_CAP = "Table 14: Bleeding events in a study testing the prevention of thromboembolic stroke and systemic embolism in patients with atrial fibrillation"
assert BEMA_CAP in flat(T[EMA])
R22 = once(T[RKT22], "Major Bleeding† 395 (3.6) 386 (3.5) 1.04 (0.90, 1.20)", "Xarelto FDA 2022 Table 5")
R22_CAP = once(T[RKT22], "Table 5: Bleeding Events in ROCKET AF*- On Treatment Plus 2 Days", "Xarelto FDA 2022")
R11 = once(T[RKT11], "Major bleeding† 395 (5.6) 3.6 386 (5.4) 3.5", "Xarelto FDA 2011 Table 1")
R_ABS_COMPOSITE = "hazard ratio, 1.03; 95% CI, 0.96 to 1.11"
assert R_ABS_COMPOSITE in recs["21830957"]["abstract"], "ROCKET abstract: the major + CRNM composite"

# binder excerpts (tables): the counts row with its caption and population, one table per file
RELY_MB_TAB = f"{X}/RELY_FDA2010_Table2_major_bleeding.tables.txt"
RELY_MB_ROW = "Major bleed | 399 (3.3) | 421 (3.6) | 0.93 (0.81, 1.07)"
open(RELY_MB_TAB, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT of the FDA PRADAXA label (NDA 022512, October 2010; US government work, public domain), section 6.1 "
    f"Table 2. Every value is verbatim from the committed text extraction {FDA10} (sha256 {sha(FDA10)}); the CELL "
    "BOUNDARIES are this excerpt's segmentation of that text run.\n"
    "# population (verbatim): Randomized patients 6076 6022\n\n"
    "=== TABLES (excerpt) ===\nTABLE Table 2 Bleeding Events (per 100 Patient-Years)\n"
    "Event | PRADAXA 150 mg twice daily N (%) | Warfarin N (%) | Hazard Ratio (95% CI)\n"
    "Randomized patients | 6076 | 6022\n" + RELY_MB_ROW + "\n")
RKT_TAB = f"{X}/ROCKET_FDA2022_Table5_major_bleeding.tables.txt"
RKT_ROW = "Major Bleeding† | 395 (3.6) | 386 (3.5) | 1.04 (0.90, 1.20)"
open(RKT_TAB, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT of the FDA XARELTO label (NDA 022406 / 202439, March 2022; US government work, public domain), Table 5. "
    f"Every value is verbatim from the committed text extraction {RKT22} (sha256 {sha(RKT22)}); the CELL BOUNDARIES are "
    "this excerpt's segmentation of that text run.\n"
    "# population (verbatim, caption): On Treatment Plus 2 Days; XARELTO N=7111, Warfarin N=7125\n"
    "# NOT this row: 'Major and nonmajor clinically relevant bleeding' HR 1.03 (0.96-1.11) (the article's principal "
    "safety composite) is a different outcome\n\n"
    "=== TABLES (excerpt) ===\nTABLE Table 5: Bleeding Events in ROCKET AF*- On Treatment Plus 2 Days\n"
    "Parameter | XARELTO N=7111 n (%/year) | Warfarin N=7125 n (%/year) | XARELTO vs. Warfarin HR (95% CI)\n"
    + RKT_ROW + "\n")

vp = f"cache/{SLUG}/verified_effects.json"
raw = open(vp, encoding="utf-8").read()
ve = json.loads(raw)
as_list = lambda v: v if isinstance(v, list) else ([v] if v else [])


def put(pid, entry):
    old = next((r for r in as_list(ve.get(pid)) if r.get("outcome") == entry["outcome"]), None)
    if old and not (old.get("document_ref") or "").startswith(X):
        entry["supersedes"] = {k: old.get(k) for k in ("provenance", "effect", "ci_low", "ci_high", "scale", "source") if old.get(k) is not None}
    elif old and old.get("supersedes"):
        entry["supersedes"] = old["supersedes"]
    rows = [r for r in as_list(ve.get(pid)) if r.get("outcome") != entry["outcome"]]
    ve[pid] = rows + [entry] if rows else entry


put("19717844", {"outcome": MB, "effect": 0.93, "ci_low": 0.81, "ci_high": 1.07, "scale": "HR",
                 "kind": "extracted_effect", "provenance": "fulltext_verified", "source_level": 2,
                 "document_ref": RELY_MB_TAB, "document_sha256": sha(RELY_MB_TAB), "source_span": RELY_MB_ROW,
                 "analysis_population": "randomised (Randomized patients 6076 vs 6022)",
                 "version_chain": "RE-LY:major-bleeding:150mg",
                 "reason": ("RE-LY major bleeding, dabigatran 150 mg vs warfarin, from the FDA PRADAXA label (October 2010) "
                            "Table 2: 399 (3.3) vs 421 (3.6), HR 0.93 (0.81, 1.07), randomised patients 6076 vs 6022. The "
                            "effect tuple equals the NEJM 2009 Table 3 original's, but the counts differ (375 vs 397 there): "
                            "an identical effect never establishes an identical version. Version chain PENDING (see "
                            "docs/source_versions.json).")})
put("21830957", {"outcome": MB, "effect": 1.04, "ci_low": 0.90, "ci_high": 1.20, "scale": "HR",
                 "kind": "extracted_effect", "provenance": "fulltext_verified", "source_level": 2,
                 "document_ref": RKT_TAB, "document_sha256": sha(RKT_TAB), "source_span": RKT_ROW,
                 "analysis_set": "On Treatment Plus 2 Days",
                 "safety_population": "on-treatment safety population (on treatment plus 2 days): 7111 rivaroxaban vs 7125 warfarin",
                 "version_chain": "ROCKET-AF:major-bleeding",
                 "reason": ("ROCKET-AF major bleeding from the FDA XARELTO label Table 5: 395 (3.6) vs 386 (3.5), HR 1.04 "
                            "(0.90, 1.20), ON TREATMENT PLUS 2 DAYS (safety population, 7111 vs 7125). Distinct from the "
                            "article's principal safety composite, major and non-major clinically relevant bleeding, HR 1.03 "
                            "(0.96-1.11), which is not this outcome.")})
dump(vp, ve)

# ------------------------------------------------------------------ (1b) the served RE-LY row: the governing version
dp = f"cache/{SLUG}/dose_selection.json"
dsel = json.load(open(dp, encoding="utf-8"))
old = dsel["19717844"]
DOSE = old["dose"]
if old.get("version_chain"):                     # idempotent: a rerun keeps what the first run superseded
    old = old["supersedes"]
dsel["19717844"] = {
    "outcome": SSE, "dose": DOSE, "effect": 0.65, "ci_low": 0.52, "ci_high": 0.81, "scale": "HR",
    "source": ("RE-LY, dabigatran 150 mg vs warfarin, the GOVERNING version of the chain RE-LY:stroke-SE:150mg "
               "(docs/source_versions.json): FDA PRADAXA label (January 2024) Table 11, verbatim '" + S24_N + "' / '"
               + S24_HR + "' ('" + S24_ITT + "'), reproduced by the EMA Pradaxa SmPC Table 22. Approved-dose rule "
               "(protocol amendment 2026-09-12, post-hoc; the marketed dose, matching the standard-dose comparator): the "
               "150 mg regimen. Supersedes the NEJM 2009 abstract's relative risk 0.66 (0.53-0.82), which predates the "
               "investigators' newly identified events."),
    "document_ref": FDA24, "document_sha256": sha(FDA24), "source_span": S24_HR,
    "version_chain": "RE-LY:stroke-SE:150mg",
    "supersedes": {k: old.get(k) for k in ("effect", "ci_low", "ci_high", "scale", "source")},
    "verification": "effect 0.65 (0.52, 0.81) present in the committed FDA label text; the same tuple in the EMA SmPC"}
dump(dp, dsel)

# ------------------------------------------------------------------ version chains
chains = [
    {"chain_id": "RE-LY:stroke-SE:150mg", "trial_id": "PMID 19717844", "outcome": SSE,
     "versions": [
        {"version_id": "v0-article-2009", "kind": "ORIGINAL", "date": "2009-09-17",
         "source": "NEJM 2009 (PMID 19717844): abstract (held); Table 2 counts relayed", "held": W(REC, S_ABS),
         "value": {"effect": 0.66, "ci_low": 0.53, "ci_high": 0.82},
         "relayed_value": {"ai": 134, "ci": 199, "note": "Table 2 counts 134 vs 199, relayed; the full text is not open (publisher 403)"}},
        {"version_id": "v1-fda-label-2010-10", "kind": "REGULATORY", "date": "2010-10-19",
         "source": "FDA PRADAXA label, NDA 022512 original, Table 4 (public domain)", "held": W(FDA10, S10_N),
         "cells": {"caption": S10_CAP, "hazard ratio row": S10_HR},
         "relation": "the warfarin count already moves 199 -> 202",
         "value": {"ai": 134, "n1i": 6076, "ci": 202, "n2i": 6022, "effect": 0.65, "ci_low": 0.52, "ci_high": 0.81}},
        {"version_id": "v2-correspondence-2010-11", "kind": "CORRECTION", "date": "2010-11-04",
         "source": "Connolly et al., 'Newly identified events in the RE-LY trial', NEJM 2010;363:1875-6 (PMID 21047252)",
         "not_held_reason": ("the investigators' correspondence is not open: publisher PDF 403 (twice, recorded), Europe PMC "
                             "not open access, no abstract; recorded in evidence/acquisition_cascade/ATTEMPTS.jsonl "
                             "(target RE-LY-newly-identified). Its values are not relied on: the regulators' later tables are held."),
         "value": None},
        {"version_id": "v3-fda-label-2024-01", "kind": "REGULATORY", "date": "2024-01-12",
         "source": "FDA PRADAXA label, supplement 47, Table 11 'Randomized ITT' (public domain)", "held": W(FDA24, S24_N),
         "cells": {"caption": S24_CAP, "hazard ratio row": S24_HR, "population": S24_ITT},
         "value": {"ai": 135, "n1i": 6076, "ci": 203, "n2i": 6022, "effect": 0.65, "ci_low": 0.52, "ci_high": 0.81}},
        {"version_id": "v3b-ema-smpc", "kind": "REGULATORY", "date": "EMA Pradaxa product information (current)",
         "source": "EMA Pradaxa SmPC section 5.1, Table 22 (subjects randomised 6 076 vs 6 022)", "held": W(EMA, SEMA_N),
         "cells": {"caption": SEMA_CAP, "hazard ratio row": SEMA_HR},
         "relation": "REPRODUCES v3 (an independent regulator's current document)",
         "value": {"ai": 135, "n1i": 6076, "ci": 203, "n2i": 6022, "effect": 0.65, "ci_low": 0.52, "ci_high": 0.81}}],
     "governing": {"state": "DECIDED", "version_id": "v3-fda-label-2024-01",
                   "reason": ("the final randomised-ITT result: the same estimand as the original (first stroke or systemic "
                              "embolism, 150 mg vs warfarin, as randomised) after the investigators' newly identified events, "
                              "held verbatim in two regulators' current documents that agree (FDA 2024 Table 11, EMA SmPC "
                              "Table 22: 135 vs 203, HR 0.65 (0.52, 0.81)). A correction of the same analysis supersedes the "
                              "original; the 2009 relative risk is shown, never served. Diagnostic pool: 0.8069 with the "
                              "original, 0.8040 with the governing version (interval stays below 1).")}},
    {"chain_id": "RE-LY:major-bleeding:150mg", "trial_id": "PMID 19717844", "outcome": MB,
     "versions": [
        {"version_id": "v0-article-2009", "kind": "ORIGINAL", "date": "2009-09-17",
         "source": "NEJM 2009 (PMID 19717844) Table 3",
         "not_held_reason": "the full text is not open (publisher 403); the abstract gives rates only (3.11% vs 3.36% per year)",
         "value": None, "relayed_value": {"ai": 375, "ci": 397, "effect": 0.93, "ci_low": 0.81, "ci_high": 1.07, "scale": "RR"}},
        {"version_id": "v1-fda-label-2010-10", "kind": "REGULATORY", "date": "2010-10-19",
         "source": "FDA PRADAXA label, NDA 022512 original, Table 2 (randomised patients 6076 vs 6022)", "held": W(FDA10, B10),
         "cells": {"population": B10_N},
         "relation": "same effect tuple as the original, DIFFERENT counts (399/421 vs 375/397)",
         "value": {"ai": 399, "n1i": 6076, "ci": 421, "n2i": 6022, "effect": 0.93, "ci_low": 0.81, "ci_high": 1.07}},
        {"version_id": "v1b-fda-label-2011-03", "kind": "REGULATORY", "date": "2011-03-07",
         "source": "FDA PRADAXA label, supplement 4, Table 2", "held": W(FDA11, B11), "relation": "REPRODUCES v1",
         "value": {"ai": 399, "n1i": 6076, "ci": 421, "n2i": 6022, "effect": 0.93, "ci_low": 0.81, "ci_high": 1.07}},
        {"version_id": "v2-ema-smpc", "kind": "REGULATORY", "date": "EMA Pradaxa product information (current)",
         "source": "EMA Pradaxa SmPC Table 14 (subjects randomised; no hazard ratio given)", "held": W(EMA, BEMA),
         "cells": {"caption": BEMA_CAP},
         "relation": "LATER COUNTS, NO EFFECT: 409 vs 426 (a count-derived ratio would differ from 0.93)",
         "value": {"ai": 409, "n1i": 6076, "ci": 426, "n2i": 6022}},
        {"version_id": "x-fda-label-2024-01-treated", "kind": "REGULATORY", "date": "2024-01-12",
         "source": "FDA PRADAXA label, supplement 47, Table 3 'Adjudicated Major Bleeding Events in Treated Patients'",
         "held": W(FDA24, B24), "cells": {"population": B24_POP},
         "relation": "DIFFERENT ANALYSIS POPULATION (treated, during treatment or within 2 days of stopping): not a version of the randomised row",
         "value": {"ai": 350, "n1i": 6059, "ci": 374, "n2i": 5998, "effect": 0.97, "ci_low": 0.84, "ci_high": 1.12}}],
     "governing": {"state": "PENDING", "version_id": "v1-fda-label-2010-10",
                   "reason": ("served: HR 0.93 (0.81, 1.07), held in the FDA label Table 2 (399 vs 421, randomised). Pending "
                              "because the latest held randomised version (EMA SmPC, 409 vs 426) gives counts without an "
                              "effect, and the only later effect (FDA 2024, 0.97) is an on-treatment analysis of treated "
                              "patients. Decision for Mahmood: keep the randomised 0.93, or adopt the on-treatment 0.97 to "
                              "match the on-treatment safety populations of ROCKET-AF, ARISTOTLE and ENGAGE AF.")}},
    {"chain_id": "ROCKET-AF:major-bleeding", "trial_id": "PMID 21830957", "outcome": MB,
     "versions": [
        {"version_id": "v0-article-2011", "kind": "ORIGINAL", "date": "2011-09-08",
         "source": "NEJM 2011 (PMID 21830957) abstract: states no significant difference in major bleeding; no major-bleeding effect",
         "held": W(REC, R_ABS_COMPOSITE),
         "cells": {"NOT this outcome": "the abstract's 1.03 (0.96-1.11) is major + non-major clinically relevant bleeding"},
         "value": None},
        {"version_id": "v1-fda-label-2011-11", "kind": "REGULATORY", "date": "2011-11-04",
         "source": "FDA XARELTO label (AF approval) Table 1: counts and rates, no hazard ratio", "held": W(RKT11, R11),
         "value": {"ai": 395, "n1i": 7111, "ci": 386, "n2i": 7125}},
        {"version_id": "v2-fda-label-2022-03", "kind": "REGULATORY", "date": "2022-03-02",
         "source": "FDA XARELTO label Table 5 'On Treatment Plus 2 Days'", "held": W(RKT22, R22),
         "cells": {"caption": R22_CAP}, "relation": "same counts as v1, with the hazard ratio",
         "value": {"ai": 395, "n1i": 7111, "ci": 386, "n2i": 7125, "effect": 1.04, "ci_low": 0.90, "ci_high": 1.20}}],
     "governing": {"state": "DECIDED", "version_id": "v2-fda-label-2022-03",
                   "reason": ("the held regulatory table carries the major-bleeding effect with its population (on treatment "
                              "plus 2 days, the safety population); the counts agree with the 2011 label")}}]
sp = "docs/source_versions.json"
sv = json.load(open(sp, encoding="utf-8"))
sv["topics"][SLUG] = chains
dump(sp, sv)

# ------------------------------------------------------------------ (3) edoxaban phase II publications
def rec_of(t, pmid):
    p = f"{H}/{t}/europepmc_record_{pmid}.json"
    r = json.load(open(p, encoding="utf-8"))["resultList"]["result"][0]
    assert r["pmid"] == pmid
    return p, r


def local_once(path, pattern, where):
    text = flat(open(path, encoding="utf-8").read())
    m = [x.group(0) for x in re.finditer(pattern, text)]
    assert len(m) == 1, f"{where}: {len(m)} matches"
    return m[0]


def excerpt(name, source, pdf, lines):
    p = f"{X}/{name}"
    open(p, "w", encoding="utf-8", newline="\n").write(
        "# EXCERPT (verbatim quotations of our pypdf text of a held PDF; the document itself is not redistributed)\n"
        f"# source: {source}\n# held PDF (local, gitignored): {pdf} sha256 {sha(pdf)}\n"
        "# each line: <kind>\\t<verbatim text, located exactly once in the whitespace-collapsed text>\n\n"
        + "".join(f"{k}\t{v}\n" for k, v in lines))
    return p


pw, rw = rec_of("Weitz2010", "20694273")
pc, rc = rec_of("Chung2011", "21136011")
py, ry = rec_of("Yamashita2012", "22664798")
C_ZERO = "No thromboembolic events occurred in any treatment group."
assert C_ZERO in rc["abstractText"]
Y_TXT = f"{H}/Yamashita2012/unpaywall.local.txt"
Y_TE = local_once(Y_TXT, r"There was only 1 thromboem ?- ?bolic event in the edoxaban 45-mg group\.", "Yamashita TE")
Y_MB = local_once(Y_TXT, r"Table 2\. Incidence of Bleeding Events During the Treatment Period Warfarin \(n=125\) Edoxaban 30 mg QD "
                         r"\(n=130\) 45 mg QD \(n=134\) 60 mg QD \(n=130\) Major bleeding n \(%\) 0 \(0\.0\) 0 \(0\.0\) 3 \(2\.2\) 2 \(1\.5\)",
                  "Yamashita Table 2")
Y_EX = excerpt("Yamashita2012_TE_and_major_bleeding.txt",
               "Yamashita et al., Circ J 2012;76:1840 (PMID 22664798), J-STAGE publisher PDF (free to read, no licence stated)",
               f"{H}/Yamashita2012/unpaywall.pdf", [("thromboembolic_events", Y_TE), ("table2_major_bleeding", Y_MB)])
pubs = [
    {"registration": "NCT00504556", "pmid": "20694273", "label": "Weitz 2010 (Thromb Haemost)",
     "coverage": "ABSTRACT_ONLY", "record_witness": W(pw, "1,146 patients with AF and risk of stroke were randomised to edoxaban 30 mg qd, 30 mg bid, 60 mg qd, or 60 mg bid or warfarin"),
     "identity_check": "registry actual enrolment 1146 = publication 1,146 randomised; four fixed-dose regimens + warfarin; 12 weeks (both)",
     "per_outcome": {
        SSE: {"statement": ("the held abstract reports bleeding and hepatic safety only; stroke/SE is not in it and the full "
                            "text (Thromb Haemost) is not open -- an abstract's silence is not absence")},
        MB: {"statement": ("the held abstract gives major PLUS clinically relevant non-major bleeding (3.2% warfarin; 10.6%, "
                           "7.8%, 3.8%, 3.0% by regimen), not major bleeding alone; the full text is not open")}}},
    {"registration": "NCT00806624", "pmid": "21136011", "label": "Chung 2011 (Thromb Haemost)",
     "coverage": "ABSTRACT_ONLY", "record_witness": W(pc, "a total of 235 patients from four Asian countries were randomly assigned to edoxaban 30 mg qd, 60 mg qd or warfarin"),
     "identity_check": "publication 235 randomised vs registry actual enrolment 234 (one-patient discrepancy, recorded, not resolved); edoxaban 30 / 60 mg qd vs warfarin; three months",
     "per_outcome": {
        SSE: {"zero_events_span": C_ZERO, "zero_events_scope": "every arm (edoxaban 30 mg, 60 mg and warfarin)",
              "witness": W(pc, C_ZERO)},
        MB: {"statement": "the held abstract gives ALL bleeding (major, clinically relevant non-major and minor) only; the full text is not open"}}},
    {"registration": "NCT00829933", "pmid": "22664798", "label": "Yamashita 2012 (Circ J)",
     "coverage": "FULL_TEXT_LOCAL (J-STAGE PDF, read locally; excerpt committed)",
     "record_witness": W(py, "A total of 536 NVAF patients (CHADS2 ≥1) were randomized to receive double-blinded edoxaban 30, 45, or 60 mg QD or open-label warfarin"),
     "identity_check": "registry actual enrolment 536 = publication 536 randomised; edoxaban 30 / 45 / 60 mg qd vs warfarin; 12 weeks",
     "per_outcome": {
        SSE: {"zero_events_span": Y_TE, "zero_events_scope": "the compared arms (edoxaban 60 mg, the approved dose, and warfarin); the one event was in the 45 mg arm, which is not compared",
              "witness": W(Y_EX, Y_TE)},
        MB: {"held_out_row": {"ai": 2, "n1i": 130, "ci": 0, "n2i": 125}, "witness": W(Y_EX, Y_MB),
             "not_admitted_because": ("a 12-week phase II dose-ranging trial; 60 mg (the approved dose) vs warfarin, 2/130 "
                                      "vs 0/125 (Table 2, treated patients). Admitting it is a served change and waits for "
                                      "Mahmood's decision on the phase II edoxaban trials")}}}]
rp = "docs/registry_publications.json"
rpd = json.load(open(rp, encoding="utf-8")) if os.path.exists(rp) else {
    "_doc": ("Registry-only entries linked to their journal publications (read by harness/registry_publications.py): the "
             "publication is a REPORT of the registration, never a second trial. Per-outcome states carry held witnesses."),
    "topics": {}}
rpd["topics"][SLUG] = pubs
dump(rp, rpd)

# ------------------------------------------------------------------ (4) J-ROCKET AF: known eligible, not in the inventory
J_TXT = f"{H}/J-ROCKET-AF/unpaywall.local.txt"
J_PP = local_once(J_TXT, r"In the primary efficacy analysis in the per-protocol population, while on treatment, stroke or "
                         r"non-CNS systemic embolism oc- ?curred at a rate of 1\.26% per year.*?\(HR 0\.49; 95% CI 0\.24–1\.00; P=0\.050; Figure 3A, Table 3\)\.", "J-ROCKET PP")
J_ITT30 = local_once(J_TXT, r"In the ITT population analysis including 30-day follow-up, the primary efficacy endpoint occurred "
                            r"at a rate of 2\.38% per year and 2\.91% per year.*?\(HR 0\.82; 95% CI 0\.46–1\.45; Figure S2\)\.", "J-ROCKET ITT30")
J_ITTOT = local_once(J_TXT, r"In the on-treatment analysis of the ITT population, the primary efficacy endpoint occurred at a "
                            r"rate of 1\.26% per year and 2\.60% per year.*?\(HR 0\.48; 95% CI 0\.23–1\.00\)\.", "J-ROCKET ITT on-treatment")
J_T3 = local_once(J_TXT, r"Primary efficacy endpoint \(stroke plus non-CNS systemic embolism\), n \(% per year\) 11 \(1\.26\) 22 \(2\.61\) 0\.49 \(0\.24–1\.00\)", "J-ROCKET Table 3")
J_DOSE = local_once(J_TXT, r"either oral rivaroxaban 15 mg o\.d\. \(10 mg o\.d\. in patients with.{0,120}?\)", "J-ROCKET dose")
J_INR = local_once(J_TXT, r"to a target INR of 2\.0–3\.0 in patients aged <70 years, or a re- ?duced INR of 1\.6–2\.6 in patients aged ≥70 years", "J-ROCKET INR")
J_EX = excerpt("J-ROCKET-AF_efficacy_analyses.txt",
               "Hori et al., Circ J 2012;76:2104-11 (PMID 22664783), J-STAGE publisher PDF (free to read, no licence stated)",
               f"{H}/J-ROCKET-AF/unpaywall.pdf",
               [("pp_on_treatment", J_PP), ("itt_including_30_day_follow_up", J_ITT30), ("itt_on_treatment", J_ITTOT),
                ("table3_primary_efficacy_row", J_T3), ("dose", J_DOSE), ("inr_target", J_INR)])
JREG = f"{H}/J-ROCKET-AF-registration/NCT00494871.json"
kp = "docs/known_eligible_missing.json"
kd = json.load(open(kp, encoding="utf-8"))
kd["topics"][SLUG] = [e for e in kd["topics"].get(SLUG) or [] if e.get("trial") != "J-ROCKET AF"] + [{
    "trial": "J-ROCKET AF", "registration": "NCT00494871", "pmid": "22664783",
    "mechanism": "inventory (absent from the committed registry inventory and search); an independent phase III trial, not a ROCKET AF subgroup",
    "status": "source_held_analyses_declared",
    "acquisition": {"route": ("acquisition cascade: Unpaywall publisher location (J-STAGE PDF, read locally, not redistributed; "
                              "committed as an excerpt) + ClinicalTrials.gov registration with posted results"),
                    "held_path": J_EX, "held_sha256": sha(J_EX), "registration_path": JREG, "registration_sha256": sha(JREG)},
    "design": "phase III, randomised, double-blind, double-dummy; 1,280 randomised (registry actual enrolment 1280); Japan",
    "comparisons": "one family (NCT00494871): rivaroxaban 15 mg od (Japan-specific dose) vs warfarin (Japanese INR targets)",
    "design_note": ("COMPATIBILITY DECISIONS PENDING (Mahmood): (a) the Japan-specific rivaroxaban dose, 15 mg od (10 mg od "
                    "with CrCl 30-49), vs the 20 mg od in ROCKET AF; (b) the warfarin INR target 1.6-2.6 for patients aged "
                    ">=70 (2.0-3.0 below 70) vs 2.0-3.0 in the pooled trials. Until decided it is not pooled; the page is "
                    "STALE for it (a known eligible trial outside the pool)."),
    "result_states": {SSE: {
        "state": "EXTRACTED_NOT_ADMITTED",
        "span": J_ITT30,
        "witness": W(J_EX, J_ITT30),
        "basis": ("three analyses held, all kept: per-protocol on treatment 11 vs 22, HR 0.49 (0.24-1.00); ITT including "
                  "30-day follow-up HR 0.82 (0.46-1.45); ITT on treatment HR 0.48 (0.23-1.00). The ITT analysis including "
                  "30-day follow-up is the candidate for this review's ITT question; not admitted pending the dose and INR "
                  "compatibility decisions"),
        "analyses": [{"analysis": "per-protocol, on treatment (the trial's primary efficacy analysis)", "effect": 0.49, "ci_low": 0.24, "ci_high": 1.00, "span": J_PP},
                     {"analysis": "ITT including 30-day follow-up (candidate for an ITT question)", "effect": 0.82, "ci_low": 0.46, "ci_high": 1.45, "span": J_ITT30},
                     {"analysis": "ITT, on treatment", "effect": 0.48, "ci_low": 0.23, "ci_high": 1.00, "span": J_ITTOT}]}}}]
dump(kp, kd)
print("NOAC fixtures written: excerpts, 2 major-bleeding entries, RE-LY governing row, 3 chains, 3 publication links, J-ROCKET AF")
