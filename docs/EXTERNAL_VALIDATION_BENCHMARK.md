# Prospective external validation benchmark

Status: PROPOSED — not an achieved validation result.

## Objective
Measure end-to-end accuracy separately from deterministic replay. Do not treat the 32 legacy seeded reviews as independent validation examples.

## Frozen protocol
Before collecting test data, commit eligibility criteria, outcomes, estimands, search strings, databases, cutoff dates, statistical methods, tolerances, model/provider versions, and dependency digests. Preserve raw retrieval responses and a tamper-evident run manifest.

## Reference set
Recruit independent evidence-synthesis reviewers to select and adjudicate a diverse set of completed reviews spanning binary, continuous, time-to-event, rare-event, cluster and multi-arm designs. Include negative controls, retractions, duplicate reports, incompatible endpoints, and deliberately planted errors. Keep reference labels inaccessible to pipeline development.

## Endpoints
Report study-identification recall and precision against an independently assembled eligible-study universe; screening sensitivity and specificity; extraction agreement by field and source; outcome/estimand compatibility; numerical parity against version-pinned R packages; correct refusal rate; false assurance rate; and full reproduction from frozen inputs. Provide denominators, confidence intervals, and per-topic failure ledgers.

## Release rule
Do not label any review independently validated until its search, eligibility, extraction, synthesis, and RoB/GRADE assertions have each received the required external assessment. A passing internal CI run is necessary for engineering integrity but not sufficient for scientific accuracy.

## Integration contract
RapidMeta Kit may consume a versioned, signed review object emitted by Meta-Harness, with immutable trial identifiers, source spans, outcomes, estimands, analysis parameters, warnings and refusal decisions. It must not silently reinterpret or override a refusal, or turn an unassessed RoB/GRADE placeholder into a certified judgement.
