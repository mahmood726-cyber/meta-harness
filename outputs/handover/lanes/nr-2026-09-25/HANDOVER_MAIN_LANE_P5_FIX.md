# Handover to the main lane (release captain): the P5 check defect behind 13 of the 41 notices, the fix for the V1 candidate, and what is clear to land

From lane NR, 2026-09-25. Branch `nr/notice-anchors`. Nothing here is applied to `harness/`: the fix below is a
patch file for you to apply, because every harness blob is in the certificates' code closure and the change needs
your re-certification.

## 0. Signature status, verified rather than assumed
**0 of 41 result-change notices are signed.** I searched:
- every branch on GitHub, after a fresh fetch;
- every local clone on C:, read-only, including the main lane's refs and stash;
- every commit since 24 Sep 12:00;
- every JSON file modified since 24 Sep that mentions a countersignature.

The only ledgers holding the 41 notices (`enforcement-gate` and `nr/notice-anchors`) show 41 OPEN. The valid set
is empty, so **no result-change notice is clear to land with the V1 candidate today.** Mahmood's instructions are
in `FINAL_SIGNING_LIST.md`: laptop clone `C:\mh-sign`, branch `sign/mahmood-2026-09-25`.

## 1. The defect: harness/trial_family.py at `1fa77f2c` (sha256 9ed66d66…)
Every notice's "why" says a departing trial's family eligibility is "not established by the held record". For 34
of the 78 departing memberships that is false: the held rows establish it, and the check misreads them. There are
two code defects and one data gap.

### D1: `randomised_contrasts()`, line 99, cannot represent an active comparator
```
99:  if bool(aa) == bool(bb) or av-aa != bv-bb:
         continue
```
A contrast is recorded only when two arms differ by the agent alone, which is the placebo or add-on shape. When
the review's comparator is another drug, the non-agent sets always differ, so **no drug-vs-active-drug trial can
ever pass P5**, and `screen_family` (line 349) returns INTERVENTION_CONTRAST_NOT_PROVEN. The protocols already
declare the comparators (`include.comparator_any`); line 171 simply never passes them. Held rows, from the page's
`trial_families` nodes:

| notice | trial | arm A (linked active interventions) | arm B |
|---|---|---|---|
| N25 | RE-LY NCT00262600 | dabigatran dose 1 / 2 | warfarin |
| N25 | ROCKET AF NCT00403767 | rivaroxaban | warfarin |
| N25 | ARISTOTLE NCT00412984 | apixaban | warfarin |
| N25 | ENGAGE AF NCT00781391 | edoxaban tablets (high / low) | warfarin tablets |
| N15 | NCT00439777 | rivaroxaban | enoxaparin overlapping with and followed by VKA |
| N15 | NCT00986154 | edoxaban + LMWH/UFH | LMWH/UFH + warfarin |
| N32 | NCT01035255, NCT02468232 | LCZ696 | enalapril |
| N39, N40 | PLATO NCT00391872 | ticagrelor | clopidogrel |
| N39, N40 | NCT01294462 | ASA + ticagrelor | ASA + clopidogrel |

### D2: `screen_family()`, line 345, a literal substring test on the registry conditions
```
345: if inc.get('population_any') and not any(t.lower() in text for t in inc['population_any']):
         return cell(code='ENTRY_POPULATION_NOT_ESTABLISHED')
```
It fails in three ways:
- It does not fold as screening folds. Screening passes the same terms through `lexicon.fold`, in
  `acquisition.py:415`.
- A protocol term ending in `*` is the protocol's truncation, which PubMed honours at search time. Here it is
  tested literally, so `antibiotic-associated diarr*` never matches "Antibiotic-associated Diarrhea".
- A MeSH-inverted condition misses the natural word order.

| notice | trial | registry conditions (held) | protocol term it misses |
|---|---|---|---|
| N17, N18, N19 | CARMELINA NCT01897532 | Diabetes Mellitus, Type 2 | type 2 diabetes |
| N20, N21 | NCT02422186, NCT03434041 | Depressive Disorder, Treatment-Resistant | treatment-resistant depression |
| N09 | DELIVER NCT03030235 | Chronic Heart Failure With Preserved Systolic Function | preserved ejection fraction |
| N29, N30 | NCT03334604, NCT05607056 | Antibiotic-associated Diarrhea | antibiotic-associated diarr* |

### D3: protocol data. This is Mahmood's scientific call, not code
The code fix handles inversion and `*`. Three departures also need the registry's own wording added to a protocol:
- `esketamine-trd-madrs` population += `depressive disorder, treatment-resistant`;
- `dapagliflozin-hfpef-hosp` population += `preserved systolic function`;
- `dpp4-mace-t2d` agents += `omarigliptin`. Omarigliptin is a DPP-4 inhibitor (NCT01703208, N17), and the topic
  already lists the class term `DPP-4`.

**Not fixed by D1 to D3:**
- **N08:** the saline control is registered as the active intervention "sodium chloride 9mg/ml".
- **N23:** the FCM arm is registered as plain "iron".

These are registry-coding rulings for Mahmood; they are section C of his list.

## 2. The fix: `nr-2026-09-25/p5-fix/trial_family.patch`
The patch is +51/−3 against `1fa77f2c`, and adds no new dependency:
- **D1:** `randomised_contrasts(..., comparators=())` also accepts an arm pair where one arm differs by the agent
  and the other by a **declared** comparator, with identical background. Line 171 passes
  `include.comparator_any`.
- **D2:** a new `population_matches()` folds both sides with `lexicon.fold`, treats a trailing `*` as a prefix and
  reads `X, Y` as `Y X`. It replaces line 345's substring test. The `population_none` line is unchanged.

**How it was proven.** All of this was executed against the held pages at `1fa77f2c`:

| check | result |
|---|---|
| Control: the original function re-derives the stored contrasts | 0 mismatches over 2,393 families in 24 reviews |
| Patched module against the in-memory sweep | 2,393 of 2,393 identical |
| Monotone: no ELIGIBLE family loses eligibility | 0 lost |
| The repo's own tests (7 files: trial_family, _contract, _ui, publication_unit, admission_routes, admission_enforced, known_missing_panel), original against patched | original: 15 failed, 58 passed. Patched: 14 failed, 59 passed. **0 new failures**: all 14 patched failures also fail on the original. Almost all are missing-file errors because the sparse clone does not check out `cache/` or `docs/*.json`. One asserts "control has at least one ADMISSIBLE row to plant on", and fails identically on both. The 15th original failure, a live-browser UI test, failed only on the original run (`p5-fix/tf_tests_*.log`). **Run the full suite on a full checkout before V1** |
| Every readmitted departing trial fails admission on P5 alone, or on P5 plus P8 with an `unbound_legacy` binding | all readmitted trials qualify: 9 are P5+P8, all 9 `unbound_legacy`. All are pooled (`admission.py:100`, MIGRATION_STATE) |
| The patch applies to `harness/trial_family.py` at `1fa77f2c` | `git apply` is clean and reproduces the tested module byte-for-byte (with `core.autocrlf=false`) |
| Every sign command on Mahmood's list, replayed as printed (test signer, temporary ledger copy) | 19 of 19 write a signature the gate's `signature_problem` accepts, bound to the named judgement and hash; the repository ledger is unchanged |

**Effect on the 41:**

| effect | notices |
|---|---|
| **Vanish:** every departing trial is readmitted, so the pool equals what main serves today (7 need code only; 4 also need D3) | N15, N18, N19, N25, N32, N39, N40; with D3: N09, N17, N20, N21 |
| **Change:** some trials are readmitted, or a departing trial's absence code changes, so the rendered reason changes. Regenerate these and re-judge with `scripts/notice_rejudge.py packets` then `append` | N01, N13, N14, N26, N29, N30, N35 |
| **Unchanged** (same hash after the fix) | the 23 others |

**One NEW notice will appear after the fix.** In `noac-vs-warfarin-af-stroke / Major bleeding`, which has no
audited notice today, ENGAGE AF (PMID 24251359) and ARISTOTLE (PMID 21870978) are set aside on P5 and would
re-enter. The ratchet will require a notice for that outcome.

Families outside the 41 that the fix also moves are listed in `p5-fix/fix_sweep.txt` (85 with code only, 93 with
D3). None of them is a pooled candidate on an outcome other than the NOAC Major bleeding case above; I checked
every P5 set-aside on all 32 pages.

## 3. What to do for V1
1. Apply `p5-fix/trial_family.patch`, and decide D3 with Mahmood. **Main's `trial_family.py` differs from the
   gate's** (+7/−24), so apply the patch on the gate lineage you are releasing.
2. Re-certify and rebuild.
3. Handle the notices:
   - Withdraw from the candidate the 11 OPEN notices whose transitions will no longer happen.
   - Regenerate the 7 that change.
   - Generate the NOAC Major bleeding notice.
4. Re-judge the regenerated notices: `python scripts/notice_rejudge.py packets --served <main> --proposed <release>
   --out DIR`, review, then `append`.
5. **The 17 notices in section A of Mahmood's list are unchanged by the fix.** Signatures he makes now stay valid
   through your rebuild. `notice_anchor.guard` tolerates page churn, and it still refuses if a served number, the
   pool, or the rendered block moves.

**Clear to land with the V1 candidate right now: none. The valid set is empty.** Once he pushes
`sign/mahmood-2026-09-25`, I verify each signature from the fetched bytes and hand you the valid set.
