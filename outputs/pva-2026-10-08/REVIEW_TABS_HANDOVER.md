# Review tabs + audit pack: handover of defects found OUTSIDE the new tabs (pva lane, 8 Oct 2026)

**To: the Captain (v3) and the evidence lane. Report only: none of these is fixed on branch pva/review-tabs.** They were
found by codex (gpt-6-astra, read-only, recorded) while it reviewed the new tabs, rounds 1-2; every quote passed a span
gate against the rendered page and the review's own `review.json`. "Re-checked" = I verified the contradiction against
the data myself, not only the quote.

## Served-number decision needed (Mahmood)
| # | topic | what | re-checked |
|---|---|---|---|
| H1 | noac-vs-warfarin-af-stroke | The PRIMARY pool serves ENGAGE AF-TIMI 48 as HR 0.87 (0.745-1.016), a 95% CI **converted** from the paper's 97.5% CI 0.73-1.04 (provenance `pre_specified_dose`). Decision **D7** (Mahmood, 7 Oct) says a re-expressed CI is for matching only and "NEVER enters a served pool"; D7 was applied to new pool additions and notices, not to this existing row. Enforcing D7 here changes a served primary number. | yes |

## Served wording that contradicts the review object (legacy tabs)
| # | topic | tab | page says | the object says | re-checked |
|---|---|---|---|---|---|
| H2 | dpp4-mace-t2d (and the funding sentence generally) | Risk of bias | "0 with no funding statement in the full text ... and 0 where only the abstract was available", after "(2 unknown)" | funding rows: PMID 30418475 `not stated (full text scanned)`, PMID 28893244 `not stated (abstract only - full text not retrieved)`; the counter does not recognise these type strings (page.py ~2849) | yes |
| H3 | finerenone-ckd-t2d-renal, semaglutide-obesity-weight | Reproduce | "Nothing was pooled on this page, so the canonical-claim contradiction gate has nothing to check" | a pooled point estimate is served (finerenone 0.8407, k 2; CI refused K2_SINGLE_DF). The sentence fires on claims_checked 0 (page.py:2422, limitations.py:1111) | yes |
| H4 | dpp4-mace-t2d | Results | TECOS listed under "Known eligible trials not in this pool" as NOT_IN_COMMITTED_SOURCE | TECOS (PMID 26052984) is in the primary pool (`served_pool_signed_notice`), and the served k 4 result includes it | yes |
| H5 | dpp4-mace-t2d | Changes (notice status) | the TECOS notice is NOT APPLIED (HELD) | TECOS is served via a different signed route; the record should say the hold was overtaken | yes |
| H6 | doac-vte-recurrence | Comparison | "van Es et al. 2014 (PMID 24963045) is a scope-matched open-access pooled analysis" | the comparator panel retired van Es (C1_OPEN_LICENCE FAIL); the adopted comparator is PMID 29795629 | span |
| H7 | sacubitril-valsartan-hfref | Comparison | "k=1 CONTRIBUTING ... PARADIGM-HF supplies the only EXTRACTABLE primary-outcome estimate" | PARALLEL-HF is also extracted (1.0881); the two-trial pool is refused for direction conflict | span |
| H8 | tocilizumab-covid19-mortality | Comparison | "COVACTA gives mortality as a RATE only (... no per-arm counts)" | the COVACTA row holds counts 58/294 vs 28/144 | span |
| H9 | tocilizumab-covid19-mortality; tranexamic-acid-pph; colchicine-recurrent-pericarditis | Comparison | "✓ same question" / intervention-level match True | each review's own scope note records a broader or different comparator (IL-6 class; prevention + treatment; open-label and mixed) -- same family as topic-audit C6 | span |
| H10 | pcsk9-mace | Results | "pooled trials use each trial's OWN primary composite" | FOURIER contributes its 3-component key SECONDARY endpoint (topic audit 27 Sep, C8) | span |
| H11 | metformin-pcos-ovulation | Results | "verified (AACT-derived, cross-checked)" for PMID 19522426, 16769748 | provenance `published_rate` (arm counts recovered from published rates + denominators) | span |
| H12 | melatonin-primary-insomnia-sol | Results | "not in cached source -- no outcome sentence/effect found" for PMID 33157425 | its cached source discusses sleep latency (no poolable numbers) | span |
| H13 | tranexamic-acid-pph | Results | "k = 1: the 1 trial(s) named below were pooled" | k = 1 is the single trial's reported values, verbatim (not pooled) | span |
| H14 | tocilizumab-covid19-mortality, tranexamic-acid-pph | Search | funnel row "unknown -> 0 -> 0" | state RAN_UNRECORDED: yields never recorded; zeros render as measured | span |
| H15 | empagliflozin-hfpef-hosp | Changes (signed notice text) | "a pooled estimate is now served" | k = 1 single-trial estimate. Inside a SIGNED block: the bytes cannot change; a successor notice would be needed | span |
| H16 | metformin-pcos-ovulation (all higher-is-better outcomes) | Conclusions | claim `direction` = "harm" for an ovulation OR > 1 | harness/claim.py defines benefit as < 1 for every ratio; it does not reverse for higher-is-better outcomes. The new tab now states claim.py's definition; the field itself is the defect | yes |

| H17 | finerenone-ckd-t2d-renal, statins-primary-prevention-elderly | Comparison (panel) | k / effect / ci "NOT EXTRACTED from held text" | `comparator.reported` holds the adopted estimate, CI and a located span (finerenone HR 0.84, 0.77-0.92; statins seven trials) -- the panel fields are empty, the extraction exists | span (round 3) |
| H18 | esketamine-trd-madrs | Comparison (panel) | "Trial set NOT ENUMERATED; overlap unknown." | the same panel says the adopted comparator's trial set and pooled result are typed, with spans verified | span (round 3) |
| H19 | iv-iron-hfref-hosp | Results | "k = 2: the 2 trial(s) named below were pooled" | `suppressed_incompatible: true` (HR first event + incidence rate ratio) -- same family as H13 | span (round 3) |

## Accessibility (legacy renderer)
- A1. Results outcome blocks skip from h3 to h5 ("Compatibility key (pooling contract)") on at least 6 topics.

## Not a defect (codex round 2, rejected after checking)
- "Recorded read mc-c2194c9c... / mc-4a328c9d... cannot be verified": both records exist at
  evidence/model_calls/provenance_convert/; the job had not been given that directory. The page links them.
