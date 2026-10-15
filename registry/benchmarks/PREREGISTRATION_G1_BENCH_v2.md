# PRE-REGISTRATION v2: G1/G2 benchmark set — open-access metas whose included trials are ALL recent and prospectively registered

- Registered by the captain on 2026-10-15, on Dispatch's ruling D1 (decided on Mahmood's explicit delegation, 15 Oct).
  Committed and pushed **before any v2 screening**.
- **v1 stays on the record unchanged.** That covers its pre-registration (4adf8793ab88), its candidate list, its
  instrument audit, and the v1.1 re-screen and validation (b4842f04d8b8). v1.1 qualified 2 of 800. Both are built
  end to end as v1 qualifiers; they are not v2 results.
- **Why v2 exists.** Two things were measured before any match rate was looked at.
  - The binding v1 criterion was C4, "the meta prints a registry id for every included trial" (300 of 800
    excluded). That is a property of how a meta is written, not of whether its trials were registered.
  - The regex instrument for design (C2) and trial count (C3) misclassified 6 of 20 and 8 of 30 on a fresh sample.
- **v2 changes only those three criteria (C2, C3, C4).** The scope, the source query, the ordering, the budget and
  every other criterion are as in v1.

## Scope sentence (unchanged, mandatory on every claim)
**"Open-access meta-analyses whose included trials are all recent (started 2010 or later) and prospectively
registered."**

## 1–2. Source, ordering and budget: identical to v1
- The same Europe PMC query string (sha256 e2026ceb7eee…), so the same seed 3791809771.
- The same ordered hit list: the committed `hits_v1_ids.json`. It is not re-run, so no new hits enter.
- Screening in that order, stopping at **20** QUALIFIES or **800** screened.
- Every verdict is recorded with its evidence.

## 3. Criteria (C1, C5–C9 as in v1; C2, C3, C4 replaced)

### C2 and C3 (design, and k): recorded two-reader model reads
- **Readers.** Codex reader A and a second reader B answer two questions from the meta's own abstract and methods.
  The text is CC BY / CC0 only, which C1 guarantees. Until agy returns, B is a Claude Sonnet reader; after that, the
  Gemini family.
  1. Is this a pairwise meta-analysis of randomised controlled trials? NMA-only, IPD-only, DTA, umbrella,
     observational-only and retracted reviews are excluded. A pairwise synthesis alongside an NMA counts as pairwise.
  2. How many randomised trials are included (k)? Ongoing and excluded trials are not counted; mixed designs count
     only the RCTs.
- **Recording.** Each call is a recorded model call, with prompt, response and hashes. Each answer must quote a
  verbatim span that is found in the cached full-text XML.
- **Agreement rule.** When both readers agree, that answer stands. When they disagree, or either quote fails the span
  check, the captain adjudicates from the two quotes. Every adjudication is recorded with its reason.
- **Size.** As in v1: 3 ≤ k ≤ 25.

### C4: every included trial resolved to a registry record from the trial's OWN records
For each included trial (from the meta's included-studies table or reference list), its registry id is found by the
first route that succeeds, in this order:
  1. a registry id printed in the meta for that trial (v1 C4's evidence);
  2. the trial report's own PubMed record (PMID from the meta's reference): `DataBankList` / secondary source ids
     (ClinicalTrials.gov, ISRCTN, EudraCT, and so on);
  3. the trial report's own open full text, if open (Europe PMC): a registration statement naming an id;
  4. a registry search by the trial's acronym or title (CT.gov v2 query; WHO ICTRP), accepted only when exactly one
     record matches the trial's intervention, comparator, sponsor and start year.

**C4 rules:**
- Each resolution records its route and evidence.
- **C4 passes only when every included trial resolves to exactly one registry record.** Zero matches, or several,
  means EXCLUDED.

### C5, C6, C7, C8, C9: unchanged from v1
Registry dates are read from the registry, at month precision (the same month counts as prospective). Per-trial rows
must be printed. No overlap with the existing topics. At most 3 per area, by condition first.

## 4. Validation before the v2 result is used
- **Seed fixed in this file:** 20261017.
- Before any v2 build, a sample of 40 v2 verdicts is drawn (20 EXCLUDED, 20 random, all QUALIFIES included) and
  re-checked independently.
- Error rates are reported per criterion next to the v2 count.
- The v1 audit sample and the v1.1 validation sample are both burned and are excluded from this draw.

## 5. After the v2 candidate list is pushed
The same as v1 §4:
- a FORECAST per qualifier (n of N trials with a reachable open per-arm source);
- builds only through the standard workflow, protocol sha first;
- scoring on G1 and G2 strict, where **DONE = G1 pass AND G2 strict pass**;
- reported as "DONE n of M started", with every topic listed and the scope sentence on every claim.
