# Reviewer B — independent extraction for the GLP-1 RA vs placebo, 3-point MACE in type 2 diabetes review

You are an independent second reviewer. You have NOT seen, and must not look for, any other reviewer's extraction. Work only from the files in this folder: `PROTOCOL.md` (the registered protocol with its 2026-09-16 amendment "B-prime" at the end — read the amendment; it governs) and `sources/` (13 PubMed records as `PMID_<id>.txt`, plus two FDA review texts `FDA_NDA208471_StatR.txt` (lixisenatide / ELIXA) and `FDA_NDA209053_EMDAC_2023.txt` (ITCA 650 / FREEDOM-CVO)). Do not use any other source, memory or the internet for values. Do not read anything outside this folder.

## What to produce
Write `F:\claude-temp\revB\reviewB_extraction.json` — a JSON object `{"reviewer": "B", "model": "<the model you are>", "records": [...]}` with one entry per PMID in `sources/`:
```
{
 "pmid": "...", "trial_acronym": "...", "nct": "...",
 "eligible_under_amendment": true|false, "eligibility_reason": "one sentence citing the protocol amendment's rule and the span in the record",
 "randomised_contrast": "drug X vs placebo (background ...)" or "NOT a randomised drug-vs-placebo contrast: <why>",
 "target_outcome_status": "REPORTED_3POINT" | "REPORTED_4POINT_ONLY" | "REPORTED_BOTH" | "NOT_REPORTED_IN_HELD_SOURCES" | "NOT_APPLICABLE",
 "three_point_mace": {"components": ["...","...","..."], "hr": number|null, "ci_low": number|null, "ci_high": number|null,
                      "events_treat": int|null, "n_treat": int|null, "events_control": int|null, "n_control": int|null,
                      "analysis_set": "ITT|mITT|on-treatment|unstated", "timepoint": "...", "estimator": "Cox PH / unstated / ...",
                      "source_file": "PMID_....txt | FDA_....txt", "source_level": 1|2|3|4|5,
                      "span": "VERBATIM sentence(s) or table row(s) from the source file containing EVERY digit you used"},
 "four_point_mace_if_reported": {same shape or null},
 "undetermined_death_counted_as_cv": "yes|no|unstated (span)",
 "primary_endpoint_of_trial": "...",
 "notes": "anything that made this record hard: co-primary endpoints, extension, relabelled endpoints, etc."
}
```
Rules: (1) a value with no verbatim span in the named source file is null, never inferred; (2) 3-point MACE = CV death + nonfatal MI + nonfatal stroke ONLY — a composite that includes unstable angina is 4-point and goes in the other field; do not relabel; (3) where a record is a meta-analysis or systematic review, mark it NOT_APPLICABLE with the reason and take no numbers from it; (4) where a record's population fails the amendment (e.g. no diabetes), mark eligible false with the reason; (5) the source hierarchy is 1 = the trial's own publication, 2 = FDA/EMA review, 3 = registry results, 4 = HTA, 5 = another meta-analysis (pointer only — never the number); if both an abstract and an FDA document give the same trial's 3-point value, record the FDA value as a separate field `three_point_mace_regulatory` with its own span and level 2, and keep the abstract value (if any) at level 1.
Finish by writing the JSON file and printing `DONE <n records>`. Do not print the values in chat beyond that line.
