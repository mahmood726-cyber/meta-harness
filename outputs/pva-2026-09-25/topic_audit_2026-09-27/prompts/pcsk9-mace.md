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


# Your topic: `pcsk9-mace`
Audit ONLY this topic. Files: topics/pcsk9-mace.json, protocols/pcsk9-mace.md, cache/pcsk9-mace/, docs/reviews/pcsk9-mace/. You may read harness/
to understand what a field means. Use shell tools (rg, python -c with json) to search; files can be large.

## Known facts you do not need to re-derive (measured by the lane against PubMed efetch on 27 Sep)
- 9 held PubMed records in cache/pcsk9-mace/records.json; 6 match PubMed today (bytes or whitespace).
- PMID 41211925: ABRIDGED (held 2070 chars, PubMed 2110); PubMed sentences not in the held text: BACKGROUND: The proprotein convertase subtilisin-kexin type 9 (PCSK9) inhibitor evolocumab reduces the risk of major adverse cardiovascular events (MACE) among patients with a previous myocardial infa | METHODS: We conducted an international, double-blind, randomized, placebo-controlled trial of evolocumab in patients with atherosclerosis or diabetes and without a previous myocardial infarction or st | RESULTS: A total of 12,257 patients were randomly assigned to receive evolocumab (6129 patients) or placebo (6128) and were included in the efficacy analyses. | CONCLUSIONS: PCSK9 inhibition with evolocumab led to a lower risk of first cardiovascular events than placebo among patients with atherosclerosis or diabetes and without a previous myocardial infarcti
- PMID 25773378: ABRIDGED (held 2140 chars, PubMed 2180); PubMed sentences not in the held text: BACKGROUND: Alirocumab, a monoclonal antibody that inhibits proprotein convertase subtilisin-kexin type 9 (PCSK9), has been shown to reduce low-density lipoprotein (LDL) cholesterol levels in patients | METHODS: We conducted a randomized trial involving 2341 patients at high risk for cardiovascular events who had LDL cholesterol levels of 70 mg per deciliter (1.8 mmol per liter) or more and were rece | RESULTS: At week 24, the difference between the alirocumab and placebo groups in the mean percentage change from baseline in calculated LDL cholesterol level was -62 percentage points (P<0.001); the t | CONCLUSIONS: Over a period of 78 weeks, alirocumab, when added to statin therapy at the maximum tolerated dose, significantly reduced LDL cholesterol levels.
- PMID 27846344: ALTERED (held 2656 chars, PubMed 2806); PubMed sentences not in the held text: IMPORTANCE: Reducing levels of low-density lipoprotein cholesterol (LDL-C) with intensive statin therapy reduces progression of coronary atherosclerosis in proportion to achieved LDL-C levels. | OBJECTIVE: To determine the effects of PCSK9 inhibition with evolocumab on progression of coronary atherosclerosis in statin-treated patients. | DESIGN, SETTING, | PARTICIPANTS: The GLAGOV multicenter, double-blind, placebo-controlled, randomized clinical trial (enrollment May 3, 2013, to January 12, 2015) conducted at 197 academic and community hospitals in Nor | INTERVENTIONS: Participants with angiographic coronary disease were randomized to receive monthly evolocumab (420 mg) (n = 484) or placebo (n = 484) via subcutaneous injection for 76 weeks, in additio | MAIN

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
