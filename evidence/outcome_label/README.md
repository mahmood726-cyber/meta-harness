# The served OUTCOME label is derived from the pooled inputs; PRIMARY and EXPLORATORY tiers (branch only; label changes are notices)

External review of colchicine-postop-af, 2026-09-26. The primary pool is labelled "ITT, in-hospital / index-admission AF", but its
inputs differ: END-AF is >=5 min until discharge, COPPS-2 is >30 s over 1- and 3-month visits, and the third is a 14-day
available-case analysis.

## How many served labels match their inputs (`measure_outcome_label.py` -> `outcome_label_3876a62d.json`)

Every pooled input carries `compat_dimensions`: a value and the `source` it came from.
- **COPIED:** a value whose source is the label itself -- `outcome.timepoint`, `outcome.name`, or
  `study_effect.analysis_population` (the pipeline fills it from the declared population). It cannot confirm the label.
- **DERIVED:** a value from the input's own committed text, registry timeframe or definition audit.

Across the 81 primary inputs, copied values dominate: window 55 copied, analysis set 64, definition 35.

**26 of 27 served primary labels do not match their inputs.**

| state | pools |
|---|---|
| CONTRADICTED: the harness's own verdict says an input FAILS the declared window / analysis set | 1 (colchicine-postop-af) |
| ASSERTED: at least one dimension of the label is copied onto an input, not shown by it | 25 |
| DERIVED_MATCH: every dimension derived and consistent | 1 (melatonin, k=1) |

Beyond "asserted", derived values also differ under one label in 8 dimension instances:
- windows: esketamine, finerenone;
- definitions: colchicine-secondary, pcsk9, semaglutide-weight, sglt2-ckd, sglt2-hfref, spironolactone.

## The fix (`harness/outcome_tiers.py`; wired in `pipeline.py` after `compat_key` is final; `page.py`)

- **Derived label.** Per dimension (window, analysis set, definition) it takes the harness's own per-input derivation where one
  exists (`compat_key` per_trial, `trial_defined_dimensions`), and otherwise the input's `compat_dimensions`.
  - The page's Timepoint and Analysis-population rows state the DERIVED label: the single derived value, `mixed: a | b | c`, or
    `declared X: not shown for n of k inputs`. Never the bare declared value.
  - The declared name, timepoint and population stay in the review as the REGISTRATION. Other code matches specs by name.
- **PRIMARY tier.** It exists only under a PREDECLARED per-outcome `common_outcome_policy` (allowed values per dimension,
  predeclared, decided_by, decided_on, rationale). It holds only the inputs whose DERIVED values satisfy every constrained
  dimension; a copied value never satisfies a policy. It gets its own pool from the same pooler.
- **EXPLORATORY tier.** It holds every eligible input, titled "Exploratory: trial-defined <name> across windows ..." with
  derived windows only.
  - Without a policy, the served pool is titled EXPLORATORY. The number is unchanged; the label changes.
- A trial stays eligible when its result is outside the primary tier: eligibility is not re-decided.

## Verified end to end (real `build_topic` of colchicine-postop-af, throwaway tree)

- Served tier EXPLORATORY, titled "Exploratory: trial-defined Postoperative atrial fibrillation across windows 14 days /
  postoperative admission; 3 months; in-hospital / until discharge".
- Timepoint `mixed: ...`; analysis set `declared intention-to-treat: not shown for 2 of 3 inputs`; definitions mixed (>=5 min vs
  >=30 s). The number is unchanged at 0.6509.
- Under a throwaway policy (window = until discharge), PRIMARY = END-AF only (k=1), and the other two stay eligible as EXPLORATORY.
  This is shown on real served rows in `tests/test_outcome_tiers.py`. It was not rebuilt, because C: sat below the 3 GB floor.

## Known remaining surfaces (named, not fixed here)

Two older per-trial renderers on the page still print a label-copied window as if it were the trial's observed value:
- the per-dimension table (`follow_up_window 32720823 in-hospital / index-admission ...`);
- the "compatibility row fields" line.
They should mark copied values as "declared; not shown by this input". The compatibility-direction audit table is correct: it
shows observed against contract, with FAIL verdicts.

## Notices if landed (for Mahmood)

Every served primary pool without a policy (27 of 27 today, since no topic declares one) is re-titled EXPLORATORY, and its window /
analysis-set rows change to the derived label. No number moves unless a topic predeclares a `common_outcome_policy` that excludes
inputs. Declaring such policies is a protocol decision per topic.
