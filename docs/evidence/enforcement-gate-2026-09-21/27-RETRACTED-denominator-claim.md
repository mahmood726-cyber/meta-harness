# RETRACTED: the dapagliflozin denominator is registry-attested, and my check was the defect

**This file previously claimed that `dapagliflozin-hfpef-hosp` PMID 34711976 carried a per-arm
denominator of 162 that was "an assumed equal split of 324, stated nowhere". That claim is WITHDRAWN.
It was wrong, and the error was in my check, not in the row.**

Corrected 2026-09-24 in `/f/mh-gate`. Nothing was landed on the strength of the withdrawn claim, and no
served number moved.

## What I did wrong

I inspected the entry's `source` field with a 300-character truncation, saw the quoted prose
("44 (27.2%) versus 38 (23.5%) patients") end without a denominator, separately confirmed that `"162"`
occurs 0 times in the held **abstract**, and concluded the denominator was stated nowhere.

Two failures, both of a kind this project keeps re-deriving:

1. **I reported a property of the whole from a prefix I had looked at.** The `source` span is **645**
   characters, not the 300 I printed. The part I truncated away is:

       AACT denominator source outputs/handover/in3/aact/reported_event_totals.txt:
       227530878|NCT03030235|EG000|serious|Total, serious adverse events|31|162|...
       227530879|NCT03030235|EG001|serious|Total, serious adverse events|22|162|...

   `"162"` occurs **twice** in the span. It is a per-arm-group total (EG000 and EG001) from the trial's
   own registry results posting, with its basis named in the span.

2. **I searched the wrong bytes.** This row's provenance is `abstract_verified_arms`, which is **not** in
   `("abstract", "pmc_fulltext", "abstract_verified")`, so `harness/verify.py:73` sends the check to the
   **source span**, not to the abstract. Whether `162` appears in the abstract is irrelevant for this row.
   I checked a text the verifier never consults.

## The source is real and held

    outputs/handover/in3/aact/reported_event_totals.txt   present in the working tree AND tracked on main
    157 lines; NCT03030235 appears with per-arm-group totals of 162 across several event categories

## Lane F4B was right, and more careful than I was

F4B wrote that the entry "includes `denominator_source` metadata claiming registry rows, but the
referenced registry file is absent **here**", that the basis was therefore **UNMEASURED**, and explicitly:
"This is not a claim that n = 162 is scientifically wrong." All three statements were correct. The file
was absent from F4B's deliberately partial tree and present on main. I read a carefully hedged UNMEASURED
as a confirmed defect and then went looking for support for it — the failure that "test the finding you
are inclined to refute" exists to prevent, arriving from the direction nobody watches: I was inclined to
**accept**, because the finding was mine.

## What survives, and what does not

Nothing about this row. The percentage-wildcard behaviour in `_tuple_in` remains real as a **binder**
defect and is demonstrated by constructed plants through the real producer. But this row is not an
instance of it, and there is now **no hand-confirmed corpus instance** of a denominator absent from the
bytes the verifier checks.

The exposure figure of 7 of 34 therefore still rests on lane F4B's single measurement.

**Consequence for lane F4C, which must be acted on:** F4C's brief names this row as a positive control it
must classify as percentage-only "or your instrument is wrong". That expected answer is now known to be
wrong. A control with a wrong expected answer is worse than no control — it will either force a correct
instrument to be "fixed" until it agrees, or be silently passed for the wrong reason. F4C's result must
be discarded or re-run with the control corrected. See `lessons.md`, "a CONTROL is not data and not a
defect — it is a THIRD thing".
