Read LANE_CONTEXT.md in the parent directory's copy below first; it is binding.

# LANE_CONTEXT -- internal topic audit (pva lane, 27 Sep 2026)

You are one read-only auditor in a programme run by the page-verifier-and-archive lane of the meta-harness project
(living meta-analysis pages; V1 is live at commit 9eacfe09). Your working directory is a READ-ONLY extract of that commit
for ONE topic plus the harness code. Do not write, create, or modify any file. Do not use the network.

## What the files are
- `topics/<slug>.json`                  the topic's configuration (PICO, queries, scope notes, clarifications)
- `protocols/<slug>.md`                 the registered protocol (with labelled retrospective amendments)
- `cache/<slug>/records.json`           HELD source text: `records[].abstract` is the abstract the pipeline read; `ctgov`,
                                          `ctgov_results` are registry data
- `cache/<slug>/ft_<id>.txt`            held full text, when present
- `cache/<slug>/families.json`, `aact_inputs.json`, `comparators.json`, `arm_contrast.json`, `rob2.json`, ...
                                          derived inputs (trial families, registry rows, comparator panels, risk of bias)
- `docs/reviews/<slug>/review.json`     the SERVED review: outcomes, pooled results, per-trial rows, audit blocks
                                          (`reason_code_audit`, `unextracted_outcome_audit`, absence claims)
- `docs/reviews/<slug>/index.html`      the served page;  `BUNDLE.json` where present: the verification bundle
- `harness/*.py`, `docs/scripts/verify_bundle.py`   the code that produced / checks the above (read to understand fields)

## The rule you are held to
Every finding must quote EXACT text that exists, byte for byte (whitespace may differ), in a file in this directory, and name
that file. Quotes are machine-checked against the files; a finding with any quote that is not found is DISCARDED. Do not
paraphrase inside `quote`. Do not quote text from memory of the published trial: only held bytes count. You may state
outside knowledge in `why_wrong`, clearly marked as such, but it cannot be the evidence.

Report only what you can show. "No finding" for a class is a valid, useful answer. Do not pad.


# Your topic: `spironolactone-hfref-mortality`
Audit ONLY this topic. Files: topics/spironolactone-hfref-mortality.json, protocols/spironolactone-hfref-mortality.md, cache/spironolactone-hfref-mortality/, docs/reviews/spironolactone-hfref-mortality/. You may read harness/
to understand what a field means. Use shell tools (rg, python -c with json) to search; files can be large.

## Known facts you do not need to re-derive (measured by the lane against PubMed efetch on 27 Sep)
- 221 held PubMed records in cache/spironolactone-hfref-mortality/records.json; 219 match PubMed today (bytes or whitespace).
- PMID 41955577: ALTERED (held 1771 chars, PubMed 1774); PubMed sentences not in the held text: In HFrEF, mineralocorticoid receptor antagonists (MRAs) constitute a cornerstone of guideline-directed medical therapy (GDMT), reducing both mortality and hospitalization. | We summarize contemporary evidence across multiple domains related to MRA therapy in HFrEF, including pharmacoepidemiology, the role of biomarkers in predicting outcomes and response to MRA, the patho | We searched PubMed with the terms 'MRA, eplerenone, and heart failure with reduced ejection fraction.' Articles published in English with no date restriction were considered. | As a result, this consensus statement advocates proactive, evidence-based approaches to optimize MRA use to improve outcomes.
- PMID 41831311: ALTERED (held 1945 chars, PubMed 1928); PubMed sentences not in the held text: This Bayesian network meta-analysis aimed to compare the efficacy and safety of finerenone, eplerenone, and spironolactone vs placebo in HFpEF/HFmrEF. | METHODS: We searched Pubmed, Cochrane, and Embase for studies focused on MRA treatment in HFpEF and/or HFmrEF. | Eight randomized controlled trials enrolling adults with HFpEF or HFmrEF (LVEF ≥40%) were analysed in a fixed-effects Bayesian network meta-analysis. | Risk ratios (RRs) with 95% credible intervals (CrIs) were estimated for hospitalization for HF, cardiovascular death, and hyperkalaemia. | Heterogeneity was assessed using I2. | RESULTS: Across a network comprising 10 644 patients, mean age 70.2; 48% women; mean LVEF 54.9%, finerenone reduced hospitalization for HF vs placebo (RR 0.84; 95% CrI 0.75-0.93), whereas spironolacto

## Check the topic against each DEFECT CLASS
- **C1 held text vs "absent"**: every served statement that a value/outcome is absent, not reported, NOT_IN_SOURCE,
  NOT_IN_HELD_SOURCES, unextracted, or "not stated" -- search the held text (records.json abstracts, ft_*.txt, ctgov_results)
  for that trial for the value. A finding = the served absence claim + the held sentence that contains the value.
- **C2 effect-measure identity**: a pooled or displayed number labelled HR/RR/OR/risk difference/rate ratio/RRR/percentage
  that the held clause states as a different measure; a one-sided or non-95% interval treated as 95% two-sided; a pool that
  mixes measures under one label; a reversed contrast (placebo vs drug) pooled as drug vs placebo.
- **C3 endpoint relations**: a component pooled as the composite (or the reverse); an explicit exclusion overridden by an
  umbrella term; numbers taken from the wrong row/arm/timepoint; patients vs events confused.
- **C4 population**: a trial included/excluded on a population or comorbidity reading its held text contradicts.
- **C5 report/family/version**: a secondary or subgroup report used as the primary; a platform-trial domain or period
  mixed with another; errata/CSR/updated reports ignored or double-counted; held abstract abridged (see the facts above).
- **C6 comparator records**: a claim that a published meta-analysis answers the same question when its held text shows a
  different population/comparator/period; overlapping trial sets inferred from dates; numbers in the comparator record that
  disagree with its own held text.
- **C7 auditor identity**: an audit/adjudication row whose verdict names a different trial, record, or outcome than the item
  it disposes of (e.g. REASON_TRUE on the wrong key).
- **C8 metadata field-links**: a field copied into the wrong slot -- dosing text used as follow-up, a primary definition
  attached to a secondary result, a year/registry id that belongs to another record.

## Output
Your FINAL message must be ONE JSON object matching the provided schema, nothing else. `classes_checked` must list all eight
classes with what you actually looked at. Each finding: `claim` = the served (or derived) text that is wrong, with its file;
`evidence` = held text proving it, with file; `proposed_fixture` = a minimal deterministic test (input bytes + the assertion)
that fails on the current code and passes when fixed. Quote exactly. At most 12 findings, most consequential first.
