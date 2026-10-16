# Lane L2 — independent oracle + differential test for the A7 rule (meta-harness, coverage lane)

You are a SECOND, INDEPENDENT implementation. Do NOT open `harness/extract.py` or `harness/absence.py` except to read
the two function SIGNATURES named below (one line each). Write your oracle from THIS spec only, then compare.

## The rule (spec)
`reported_vs_count_derived(arms, rep, rep_span, count_span)`:
- `arms = (ai, n1i, ci, n2i)` event counts / arm sizes (intervention first). `rep = (scale, point, ci_low, ci_high)`,
  scale in {"RR","OR","HR"}. `rep_span` is the sentence the reported value is printed in.
- derived = OR from the 2x2 if scale == "OR", else RR = (ai/n1i)/(ci/n2i). No continuity correction is applied here; if
  derived is None/<=0 (a zero cell) -> return None.
- GROSS mismatch (the historical round trip): for RR/OR, gross iff derived/point < 0.5 or > 2.0; for HR (or any other
  scale), gross iff (derived-1)*(point-1) < 0 and |derived-1| > 0.11 and |point-1| > 0.11. A gross mismatch returns
  the typed result with gross=True, terminal=False.
- otherwise (not gross): if scale not in {RR, OR} -> None. If the reported value's own clause names a different estimand
  -> None. "Own clause" = text from the previous ';' (at most 160 chars back) to the value, plus forward to the next
  ';', sentence end ('. ' or '.' at end), or the start of the next estimate label (RR/OR/HR/IRR/relative risk/risk
  ratio/odds ratio/hazard ratio/rate ratio, optionally preceded by adjusted/unadjusted/crude). Different-estimand words:
  'adjusted' (but NOT 'unadjusted'), aOR/aRR/aHR, multivariable, multivariate, covariate, regression, 'control for' /
  'controlled for' / 'controlling for', 'rate ratio', IRR.
- the reported value's printed decimals d come from the occurrence printed right after a label OF ITS SCALE (RR-scale
  labels: RR, relative risk, risk ratio, rate ratio, IRR; OR: OR, odds ratio; HR: HR, hazard ratio), with up to 30
  non-digit chars (no ';', '(', ')', '.') between label and value; values may be printed with no leading zero ('.50').
  If no labelled occurrence: the first equal number in the span; else the float repr's decimals.
- agree iff |derived - point| <= 0.5 * 10**(-d) (+1e-9). Agree -> None. Else typed result: state
  "SOURCE_REPORTED_AND_COUNT_DERIVED_DISAGREE", gross=False, terminal=True.

`percentage_implied_counts(abstract, sentences, interv_terms, comp_terms)` (consistency check only):
- needs both arm sizes from the abstract (use the real `harness.extract._arm_ns` for that part — it is not under test);
- declines (None) if the abstract or the sentence contains estimate/rate/model wording (kaplan, estimat, cumulative,
  probabilit, 'per <digit>', person, annualised/annualized, incidence rate, model, predicted, adjusted, weighted,
  standardised/standardized, imputed);
- the sentence must hold a percentage pair 'X% vs/versus/and/compared with/compared to Y%'; it declines if the sentence
  holds any other digit (a p value 'p = .375' / 'p<0.05' excepted) or names a population (among, safety, evaluable,
  subgroup, per-protocol, completer(s), population, analysed/analyzed, intention, ITT, mITT);
- arm order: from the arm terms (whole words, case-insensitive) AFTER the pair up to the next ';', or BEFORE it back to the
  previous ';' only if the sentence says 'respectively'; exactly one side must name both arms, else decline;
- each count k must be the UNIQUE integer in [0, n] that prints as the percentage p at p's printed decimals by rounding
  (|100k/n - p| <= half a unit) or truncation (p <= 100k/n < p + one unit); otherwise decline.

## What to do
1. Write `tests/test_a7_oracle.py`: your oracle functions (pure Python, in the test file), then
   - >= 40 hand-built edge cases with the expected answer stated in a comment (rounding boundaries, '.50', '1.00',
     adjacent adjusted/unadjusted estimates, rate ratio, HR direction, zero cells, the 0.5/2.0 boundary, truncation
     like 5/9 = 55.56% printed '55.5%', non-unique counts for large n);
   - a seeded (random.Random(20261014)) generator of >= 3000 synthetic sentences/arms comparing your oracle with
     `harness.extract.reported_vs_count_derived` and `harness.extract.percentage_implied_counts` on (state, gross,
     terminal, derived counts). Generated text is synthetic: never read anything under cache/ or docs/.
2. Run `python -m pytest -q tests/test_a7_oracle.py -p no:cacheprovider` and the repo's
   `tests/test_reported_vs_derived.py tests/test_a7_picu.py`.
3. Do NOT change harness/. If the real code and your oracle disagree, KEEP the disagreeing cases as
   `@pytest.mark.xfail(strict=True, reason="ORACLE DISAGREES: ...")` tests and list each in the report with both
   answers and which one you believe follows the spec and why.

## Finish condition / artefact
Write `LANE_REPORT.md` (counts: cases n of N agreeing, every disagreement with input, oracle answer, real answer, your
judgement), and `git diff > lane.patch` (including the untracked test via `git add -N tests/test_a7_oracle.py` first).
Do not commit. Do not push. Do not run the full suite.
