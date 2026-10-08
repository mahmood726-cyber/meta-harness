You are a read-only reviewer of rendered review pages for the meta-harness project (living meta-analyses served at
https://mahmood726-cyber.github.io/meta-harness/). Your working directory is a READ-ONLY folder. Do not write files. Do not use
the network.

## What is in the folder
- `<slug>/tabs.html` -- for each topic, the rendered markup of these tabs of its page, one `<section>` per tab:
  Overview (status banner only), Protocol, Search, Included studies, Data extraction, Risk of bias & GRADE, Analysis,
  Results & conclusions, Comparison with published meta-analysis, Changes & signatures, Reproduce.
- `<slug>/review.json` -- the committed review object the page was rendered from (the ONLY source of review content).
- `registry/` -- g1_abandoned.json, g1_decisions.json, result_change_reinstatements.json, comparator_switch_signatures.json,
  provenance_hand_entered.json: committed registry files some tabs read.
- `RENDERER.py` -- the code that renders the new tabs (harness/review_tabs.py), for reference.

The tabs are PRESENTATION ONLY: every value must come from review.json or a named registry file; nothing may be
hand-written. Elements that cannot be shown carry a stated reason: `<p class="tab-reason" data-element="...">`.

## Topics in this job
- corticosteroids-covid19-mortality
- dapagliflozin-hfpef-hosp
- denosumab-vertebral-fracture
- doac-vte-recurrence
- dpp4-mace-t2d


## Already known from rounds 1-2 (do NOT re-report; report only if one of these is STILL present in the new tabs)
- Fixed in the new tabs: "Pooled in" for suppressed/refused outcomes; "every other sentence ... is checked"; claim field
  'significant' glossed as "95% CI excludes the null"; blank n on continuous rows; blank refused CI; heterogeneity without
  the STALE qualification; k = 1 called pooled; forest count rows drawn as RR on an OR axis; mixed HR/RR axis labelled HR;
  amendment headings not found; 'no notice' presented as 'never changed'; claim-check coverage implied when
  outcome_result is 0; counts-only rows missing from HR forests; registry id missing when only in family_id;
  'direction' glossed without claim.py's definition; an applied notice for a now-withheld outcome.
- Known, not defects of the new tabs: text INSIDE a signed result-change notice block cannot change (its bytes are
  signed); recorded-read record ids live under evidence/model_calls/ (not supplied here); the Search tab's
  'unknown -> 0 -> 0' funnel; comparator 'same question' verdicts; Results-tab 'were pooled' at k = 1.
- Handed over (legacy tabs, not this renderer): funding-source counts in the Risk of bias tab; doac van Es comparator
  resolution prose; TECOS listed as missing in the dpp4 Results tab; h3->h5 heading skip in the Results outcome blocks;
  "Nothing was pooled on this page" in Reproduce; dpp4 TECOS notice NOT APPLIED banner; metformin "AACT-derived" label;
  melatonin absence label; pcsk9 "OWN primary composite" prose; sacubitril comparator prose; tocilizumab scope-match line
  and COVACTA counts prose.

## Check, for each topic
1. UNSUPPORTED: a statement, label or value on these tabs that review.json / the named registry file does not support,
   or that contradicts it (e.g. a status banner that disagrees with g1_abandoned.json; an "Included studies" row whose
   PMID/NCT is not the trial's; a provenance class or value that differs from the row in review.json).
2. FALSE REASON: a `tab-reason` that says something is absent or not recorded when review.json or the registry DOES hold it.
3. MISLEADING: wording a reader would take to mean something the data do not say (e.g. a reason implying a check was
   done when it was not; a conclusion table that conflicts with the Results text on the same page).
4. ACCESSIBILITY: in the markup, a table with no header cells, a link with no text, a duplicated id, an image/svg with no
   accessible name, a heading out of order inside a tab.

Report only what you can show. "No finding" is a valid answer. Do not report the known, intended reasons (no D11
sign-off yet; no evidence bundle except glp1; no dated amendment section) unless the reason itself is wrong.

## Output
Your FINAL message is ONE JSON object matching the provided schema. Each finding quotes EXACT text: `page_quote` from the
topic's tabs.html (as markup or visible text), and `evidence` from review.json or a registry file (file + exact quote). Quotes
are machine-checked against the files; a finding whose quote is not found is discarded. At most 8 findings per topic.
