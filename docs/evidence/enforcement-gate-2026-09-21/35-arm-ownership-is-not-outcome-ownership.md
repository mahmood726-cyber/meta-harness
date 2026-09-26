# Arm ownership is not outcome ownership: a foreign-outcome denominator is accepted

Lane HOSTILE-2, `/f/mh-f4`, 2026-09-25. Adversarial lane, no patch, no repair. Nothing landed.

## The finding

> A denominator explicitly belonging to **headache** was accepted for **nausea**, including through the
> real hand-override producer.

Every layer passes it:

    OTHER_OUTCOME_DENOMINATOR           shape=None  replay=None
                                        admission={'admissible': True, 'verdict': 'EXACT_TARGET'}
                                        verify=('verified', 'role-labelled injective count witnesses
                                                 replayed against held source')
    OTHER_OUTCOME_DENOMINATOR_PRODUCER  {'rows': 1, 'codes': []}

For contrast, every other "wrong kind of number" attack **is** refused:
`WRONG_KIND_YEAR`, `WRONG_KIND_PMID`, `WRONG_KIND_PERCENT`, `WRONG_KIND_CI_BOUND` all fail at replay.

## Mechanism, confirmed by reading the code rather than trusting the verdict

    harness/count_observations.py:113   denominators(doc, terms)  -- takes the document and the ARM
                                        TERMS. The outcome is not a parameter.
    harness/count_observations.py:225   the denominator witness carries role and basis, no outcome.
    harness/count_observations.py:227   the "context" witness covers the EVENTS candidate span,
                                        not the denominator's.
    harness/count_observations.py:287   `outcome` is in the compared field list -- but it is only
    harness/count_observations.py:326   checked as a VALUE between supplied and re-extracted objects.
                                        It never constrains where a denominator may be located.

So a denominator stated anywhere in the document for the right arm is admissible, regardless of which
outcome's section states it.

## Why this matters, and why it is the same arrow rather than a new one

This is finding B's shape one level along. The original defect was **occurrence is not ownership** — the
digits being on the page did not prove they belonged to that arm. The repair bound counts to arms. This
says **arm ownership is not outcome ownership** — the denominator now provably belongs to the right arm,
and still need not belong to the right outcome.

The auditor's own schema lists `outcome` as a constituent of the observation, alongside arm, population
and window. The field is carried end to end; it is simply not enforced as a constraint on the
denominator's provenance.

## What HOSTILE-2 confirmed, and one architectural correction

Everything else held, on 34 named probes:

| attack | verdict |
|---|---|
| distinct coordinates, same arm | CONFIRMED refused (`ARM_EVENT_OWNER_MISMATCH`; tables independently refuse duplicate columns) |
| wrong kind of number | **REFUTED** — year/PMID/percent/CI-bound refused, foreign-outcome denominator accepted |
| off-by-one, partial overlap, nested slices | CONFIRMED refused at replay |
| table aliases (same cell via offset or group alias, string column) | CONFIRMED refused; null column fails shape too |
| all three producer routes (hand override, abstract machine, CT.gov machine) | CONFIRMED — each admits its control, each refuses a shared-coordinate mutation with `ARM_WITNESS_NOT_INJECTIVE` |

**The correction worth keeping: shape validation is not the defence — replay is.** Off-by-one, partial
overlap, nested slices and the table aliases all present four *distinct* coordinates and pass the
injectivity shape check; they are caught when the witness is replayed against the held source. So
"four distinct coordinates" is necessary and nowhere near sufficient, and the claim that injectivity
implies non-overlapping intervals is **REFUTED**.

Stated limits from the lane: coverage is 3 of 3 named producer routes, not a corpus census; universal
coverage beyond the exercised paths is UNTESTED; the 34 probes are heterogeneous checks, not 34
independent studies. All newly created fixtures were removed and no pre-existing fixture was overwritten.

## The repair this implies

Bind the denominator to the outcome, not only to the arm: `denominators()` must be given the outcome
context and refuse a candidate whose located span belongs to a different outcome's section, with its own
code rather than a reused one. The same question should then be asked of `population` and `window`, which
are carried in the observation for the same reason and are, on this corpus, still UNEXERCISED.

**Queued, not worked.** This is a repair to code that cannot land without the 32-topic regeneration, and
the scope rule for this cycle is to close findings A and B rather than extend the catalogue.
