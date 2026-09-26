# evid2 Q1–Q3 decisions, and the ELIXA estimand dispute to disclose

All four decided by **Dispatch under Mahmood's delegation, 2026-09-25**;
`how_it_reached_the_reviewer: "Dispatch chat relay"`. Two of them move a served number and
therefore need a notice on Mahmood's signing list; two do not.

## Q1 — EMPA-KIDNEY, diabetic ketoacidosis → **option A**

Serve the **registry's diabetic-only counts**, `5/3,304 vs 1/3,305`, under the label
**"Diabetic ketoacidosis"**, with a note recording the paper's `6 vs 1`.

- **SERVED-NUMBER CHANGE → notice required.**
- The note is not optional decoration: the two sources disagree on the numerator, and a reader who
  finds the paper's 6 must be able to see why we serve 5 without concluding we mis-transcribed it.

## Q2 / Q2a — COVACTA, serious adverse events → **option B**

Keep the **paper's day-28 counts** `103/295 vs 55/143`, **label the 28-day window explicitly**, and
show the **registry's day-60 counts** `116/295 vs 64/143` beside them.

- **No served number changes.** No notice.
- The window label is the substance of this decision. The same trial reports two different SAE
  totals because they cover different follow-up; an unlabelled count invites the reader to compare
  it with a day-60 count from another trial. Both are shown so the difference is visible rather
  than hidden by a choice.

## Q3 — COVID STEROID → **option A**

Rename the outcome to
**"Serious adverse reactions (septic shock, invasive fungal infection, GI bleeding, anaphylaxis;
day 14)"**, keep `1/16 vs 0/14` visible, and **remove it from the SAE pool**.

- **SERVED-NUMBER CHANGE → notice required** (the SAE pool loses a contributing row).
- The trial's "serious adverse reactions" is a named four-component composite at day 14, not the
  all-cause SAE count the pool aggregates. Pooling it with all-cause SAE counts compares different
  quantities. Keeping the row visible while removing it from the pool is the honest handling: the
  evidence is not suppressed, it is declared non-poolable for a stated reason.

**Metformin full texts remain local** (not redistributable), unchanged by these decisions.

## ELIXA — the estimand dispute is disclosed, and the inclusion stands

pva's finding: ELIXA's 3-point MACE is described as a **"prespecified secondary"** endpoint in one
FDA review and as a **"sensitivity analysis"** in the FDA summary review, and the **registry lists
neither**.

**The inclusion stands.** The protocol accepts the exact three components, and the value we pool is
unchanged: `HR 1.02 (0.887–1.172)`, `400 vs 392`, ITT on-study — identified by its definition
sentence and its event counts, never by its number. (That identification matters here: the 4-point
MACE+ primary rounds to the same 1.02 (0.89–1.17) but is `406 vs 399`, so a number-based match
would have picked the wrong row.)

**What must appear, on the page and in the k=10 notice:**

1. the two FDA characterisations, quoted and attributed to their documents;
2. that the registry records neither;
3. that the pooled value is unaffected by which label is correct;
4. the **RoB "some concerns"** flag carried on ELIXA's row.

A trial whose estimand status is disputed between two documents from the same regulator is not a
clean inclusion, and the page should not present it as one. Disclosing this costs nothing in the
result and is the difference between a defensible inclusion and a quiet one.

## Consequence for the signing list

Notices required, in addition to the k=10 primary change which goes first:

    Q1  EMPA-KIDNEY DKA        5/3,304 vs 1/3,305 served; paper's 6 vs 1 noted
    Q3  COVID STEROID          renamed, removed from the SAE pool, row still visible

No notice:

    Q2  COVACTA SAE            day-28 kept and labelled; day-60 shown beside it
