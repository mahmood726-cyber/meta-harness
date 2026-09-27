Read LANE_CONTEXT.md in the parent directory's copy below first; it is binding.

{LANE_CONTEXT}

# Your topic: `{SLUG}`
Audit ONLY this topic. Files: topics/{SLUG}.json, protocols/{SLUG}.md, cache/{SLUG}/, docs/reviews/{SLUG}/. You may read harness/
to understand what a field means. Use shell tools (rg, python -c with json) to search; files can be large.

## Known facts you do not need to re-derive (measured by the lane against PubMed efetch on 27 Sep)
{CENSUS}

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
