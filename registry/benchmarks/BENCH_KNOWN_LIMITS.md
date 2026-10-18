# Benchmark known limits

## 18 Oct 2026 — review closed after three rounds

1. harm_grade refuses the held Mitja negated serious-event sentence and three adversarial all-event clauses. Held PMID 33289973: The incidence of adverse events was higher in the hydroxychloroquine group than in the usual-care group (56.1% vs. 5.9%), but no treatment-related serious adverse events were reported. Explicit adversarial inputs: `adverse events 30 vs 20 (none serious)`; `adverse events 30 vs 20, none of which were severe`; `Adverse events 30 vs 20; serious adverse events in 3 vs 2`. The hyphenated negation is not recognized.
2. extracted_cell_span has no production producer.
3. comparator-selected record bypasses registry-contrast EXCLUDE and overwrites its reason.
4. Rajasingham registry SECONDARY outcome binding is not cross-checked against held PMC7665393 Table 2. Registry title `Number of Confirmed SARS-CoV-2 Detection` is admitted via `primary_outcome.keywords` and `harness/verify.py`; `outcome_type` is unchecked. Held row `PCR positive or probable COVID-19` has events 39/29/29 (placebo/once-weekly/twice-weekly), read directly from XML. The strict-xfail mutates that row using other held cells and requires binding to abstain.
5. CASTOR QoL exclusion reason says companion/duplicate report of None.

Executable coverage: `tests/test_bench_known_limits.py`; strict xfails preserve these unresolved limits. Production code remains frozen.

| Static declarations | Dynamic evidence |
|---|---|
| Limit descriptions, endpoint locators, explicit adversarial phrases and verdict | Abstract sentence, registry outcome type, report identities, and trial-table cells read from held files |
