"""Write docs/source_versions.json for doac-vte-recurrence (DOAC-VTE review, hash 5f9c2b44): Hokusai-VTE original vs
reported CSR erratum (not held) vs FDA labels (held, public domain); J-EINSTEIN original vs journal erratum (held,
CC BY), applied per cell. Every held witness carries its sha256; harness/source_versions.py re-verifies them.
  python outputs/handover/doac_sources/make_source_versions.py"""
import hashlib, json

sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
REC = "cache/doac-vte-recurrence/records.json"
L15 = "evidence/acquisition_cascade/held/Hokusai-VTE/fda_label_2015-01.txt"
L23 = "evidence/acquisition_cascade/held/Hokusai-VTE/fda_label_2023-10.txt"
JE = "evidence/acquisition_cascade/held/J-EINSTEIN/PMC4339301.xml"
JER = "evidence/acquisition_cascade/held/J-EINSTEIN__erratum/PMC4877730.xml"


def W(p, s):
    return {"path": p, "sha256": sha(p), "span": s}


CSR_NOT_HELD = ("the Hokusai-VTE CSR erratum (26 Feb 2015) is hosted on a government clinical-data portal that requires "
                "accepting terms of use / registering; not accessed without the owner's explicit permission. Values as "
                "reported by the reviewer.")
PRIM = "Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death)"
ORIG_VALUE = {"ai": 130, "n1i": 4118, "ci": 146, "n2i": 4122, "effect": 0.89, "ci_low": 0.70, "ci_high": 1.13}

chains = [
    {"chain_id": "Hokusai-VTE:primary:recurrent-VTE", "trial_id": "PMID 23991658", "outcome": PRIM,
     "versions": [
         {"version_id": "v0-article-2013", "kind": "ORIGINAL", "date": "2013-10-10",
          "source": "NEJM 2013 (PMID 23991658) abstract",
          "held": W(REC, "130 patients in the edoxaban group (3.2%) and 146 patients in the warfarin group (3.5%) "
                         "(hazard ratio, 0.89; 95% confidence interval [CI], 0.70 to 1.13"),
          "value": ORIG_VALUE},
         {"version_id": "v0-fda-label-2015-01", "kind": "REGULATORY", "date": "2015-01-08",
          "source": "FDA SAVAYSA label, NDA 206316 original (public domain)",
          "held": W(L15, "recurrent VTE b, 130/4118 (3.2) 146/4122 (3.5) 0.89 (0.70,1.13)"),
          "relation": "REPRODUCES_ORIGINAL", "value": ORIG_VALUE},
         {"version_id": "v1-csr-erratum-2015-02-26", "kind": "CSR_ERRATUM", "date": "2015-02-26",
          "source": "Hokusai-VTE clinical study report erratum, Table 11.2", "not_held_reason": CSR_NOT_HELD,
          "cells": {"edoxaban recurrent VTE events": "131", "HR (95% CI)": "0.90 (0.709-1.136)"},
          "value": {"ai": 131, "n1i": 4118, "ci": 146, "n2i": 4122, "effect": 0.90, "ci_low": 0.709, "ci_high": 1.136}},
         {"version_id": "v0-fda-label-2023-10", "kind": "REGULATORY", "date": "2023-10-19",
          "source": "FDA SAVAYSA label, supplement 19 (public domain)",
          "held": W(L23, "recurrent VTEb 130/4118 (3.2) 146/4122 (3.5) 0.89 (0.70,1.13)"),
          "relation": "REPRODUCES_ORIGINAL (dated after the erratum)", "value": ORIG_VALUE}],
     "governing": {"state": "PENDING", "version_id": "v0-article-2013",
                   "reason": ("a sponsor CSR erratum is reported to move this result to 131/4,118 and HR 0.90 "
                              "(0.709-1.136), but it is not held, and the latest held regulatory document (FDA label, "
                              "October 2023) still carries 130/4,118 and 0.89 (0.70,1.13). A correction that is not held "
                              "cannot govern; the original stays served and the chain is shown. Decision owed to Mahmood.")}},
    {"chain_id": "Hokusai-VTE:safety:major-or-CRNM", "trial_id": "PMID 23991658",
     "outcome": "Major or clinically relevant nonmajor bleeding",
     "versions": [
         {"version_id": "v0-article-2013", "kind": "ORIGINAL", "date": "2013-10-10", "source": "NEJM 2013 abstract",
          "held": W(REC, "The safety outcome occurred in 349 patients (8.5%) in the edoxaban group and 423 patients "
                         "(10.3%) in the warfarin group (hazard ratio, 0.81; 95% CI, 0.71 to 0.94"),
          "value": {"ai": 349, "ci": 423, "effect": 0.81, "ci_low": 0.71, "ci_high": 0.94}},
         {"version_id": "v0-fda-label-2023-10", "kind": "REGULATORY", "date": "2023-10-19",
          "source": "FDA SAVAYSA label s019, Table 6.3",
          "held": W(L23, "(Major/CRNM), n (%) 349 (8.5) 423 (10.3)"), "relation": "REPRODUCES_ORIGINAL",
          "value": {"ai": 349, "ci": 423}},
         {"version_id": "v1-csr-erratum-2015-02-26", "kind": "CSR_ERRATUM", "date": "2015-02-26",
          "source": "Hokusai-VTE CSR erratum", "not_held_reason": CSR_NOT_HELD,
          "cells": {"warfarin major or CRNM events": "424"}, "value": {"ci": 424}}],
     "governing": {"state": "PENDING", "version_id": "v0-article-2013",
                   "reason": ("the reported erratum (warfarin 423 -> 424) is not held, and the October 2023 FDA label still "
                              "carries 423; the served HR is the original analysis until a corrected analysis is held. "
                              "Decision owed to Mahmood.")}},
    {"chain_id": "Hokusai-VTE:safety:major-bleeding", "trial_id": "PMID 23991658", "outcome": "Major bleeding",
     "versions": [
         {"version_id": "v0-fda-label-2015-01", "kind": "REGULATORY", "date": "2015-01-08",
          "source": "FDA SAVAYSA label Table 6.3 (on treatment: during or within three days of stopping study treatment)",
          "held": W(L15, "Major Bleedingb, n (%) 56 (1.4) 66 (1.6)"),
          "value": {"ai": 56, "n1i": 4118, "ci": 66, "n2i": 4122}},
         {"version_id": "v0-fda-label-2023-10", "kind": "REGULATORY", "date": "2023-10-19",
          "source": "FDA SAVAYSA label s019 Table 6.3", "held": W(L23, "Major Bleedingb, n (%) 56 (1.4) 66 (1.6)"),
          "relation": "REPRODUCES", "value": {"ai": 56, "n1i": 4118, "ci": 66, "n2i": 4122}},
         {"version_id": "v1-csr-erratum-2015-02-26", "kind": "CSR_ERRATUM", "date": "2015-02-26",
          "source": "Hokusai-VTE CSR erratum, safety table (on-treatment window)", "not_held_reason": CSR_NOT_HELD,
          "cells": {"major bleeding HR (95% CI)": "0.84 (0.592-1.205)"},
          "value": {"effect": 0.84, "ci_low": 0.592, "ci_high": 1.205}}],
     "governing": {"state": "PENDING", "version_id": "v0-fda-label-2023-10",
                   "reason": ("the held FDA label gives major-bleeding COUNTS (56/4,118 vs 66/4,122, on treatment) but no "
                              "HR; this review's major-bleeding estimand is the published HR (a count-derived RR is "
                              "refused, as for AMPLIFY), and the published HR 0.84 (0.592-1.205) is in the CSR erratum, "
                              "which is not held. Reported, unresolved; decision owed to Mahmood.")}},
    {"chain_id": "J-EINSTEIN:primary:symptomatic-recurrent-VTE", "trial_id": "PMID 25717286", "outcome": PRIM,
     "versions": [
         {"version_id": "v0-article-2015", "kind": "ORIGINAL", "date": "2015",
          "source": "Thrombosis Journal 2015 (PMID 25717286, CC BY)",
          "held": W(JE, "A single patient in the rivaroxaban group (1/78; 1.4%) developed symptomatic recurrent VTE "
                        "compared with none of the 19 patients allocated to control treatment"),
          "cells": {"results: symptomatic recurrent VTE, rivaroxaban %": "1.4%",
                    "abstract: composite, rivaroxaban %": "1.4%",
                    "results: composite absolute risk difference": "3.9% (95% CI -3.4 to 23.8)",
                    "Table 3: rivaroxaban %": "1.4%", "Table 3: unchanged 2/71 %": "2.9%"},
          "value": {"ai": 1, "n1i": 78, "ci": 0, "n2i": 19}},
         {"version_id": "v1-erratum-2016", "kind": "ERRATUM", "date": "2016",
          "source": "Erratum, Thrombosis Journal 2016 (PMID 27222638, CC BY)",
          "held": W(JER, "it is not necessary to replace the number “1.4%” in Table 3 because it was "
                         "calculated by another definition"),
          "cells": {"results: symptomatic recurrent VTE, rivaroxaban %": "1.3%",
                    "abstract: composite, rivaroxaban %": "1.3%",
                    "results: composite absolute risk difference": "absolute risk reduction 4.0% (95% CI -2.9 to 24.0)",
                    "Table 3: unchanged 2/71 %": "2.8%"},
          "value": {"ai": 1, "n1i": 78, "ci": 0, "n2i": 19}}],
     "governing": {"state": "DECIDED", "version_id": "v1-erratum-2016",
                   "reason": ("the journal's own erratum (held, CC BY) governs the cells it lists, cell by cell; the cell "
                              "it explicitly does not list -- Table 3 '1.4%', 'calculated by another definition' -- keeps "
                              "the original. The counts 1/78 vs 0/19 are unchanged.")}},
]

doc = {"_doc": ("Source-version chains per result (harness/source_versions.py): every version with its source, date, held "
                "witness (or why it is not held) and value, and ONE governing decision with its reason. Nothing is "
                "overwritten; a correction applies to the cells it lists. Declared by the evidence lane (Claude Opus 5.5), "
                "2026-09-27, from the DOAC-VTE review (hash 5f9c2b44)."),
       "topics": {"doac-vte-recurrence": chains}}
open("docs/source_versions.json", "w", encoding="utf-8", newline="\n").write(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
print("wrote docs/source_versions.json", len(chains), "chains")
