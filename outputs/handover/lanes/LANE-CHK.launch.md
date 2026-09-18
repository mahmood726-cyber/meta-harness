# LANE CHK — one defect, one increment on the served harness (base 237e9094): assurance counters overstate ("Claims checked: N" with fewer real checker calls). Counts come from RECEIPTS (planned / attempted / completed / failed; an exception is FAILED), never from strand arithmetic. Plant proven pre-fix.

Report file: `LANE-CHK-REPORT.md`. Fresh checkout of main at 237e9094 (served tonight). Record `git rev-parse HEAD`. Never
reset/checkout/stash. No commit. No network. Extend `harness/census.py`, `harness/page.py` (the "Claims checked" block near
page.py:2159), `scripts/verify_all.py` (limb receipts) -- existing modules only; no parallel framework.

## The defect (URGENT audit, defect 5; memorandum: counts from receipts)
On the candidate tree, lane AUD2 (`C:\mh-r-AUD2\LANE-AUD2-REPORT.md`, section "Measured plants", and its `harness/census.py`,
`scripts/verify_all.py` diffs -- read them; you may reuse the design, not copy blindly: that tree is ~740 paths away from this base)
measured on IV-iron: "claims checked: 4" while actual calls to the cross-surface significance checker were 0; the census summed strand
counts without running strand checks and suppressed rendering exceptions while still reporting surfaces as checked; the interval-
provenance checker accepted an unverified provenance label. Establish whether each of these holds on THIS base (237e9094) by
measurement (a spy around the actual checker; a mutation that raises inside a check), not by reading the report.

## Required end state
1. Every check the census/page reports is backed by a receipt object {check_id, surface, state in PLANNED|ATTEMPTED|COMPLETED|FAILED,
   reason or exception text, inputs digest}; the rendered "Claims checked: N" (and any "surfaces checked", "checks passed" number on
   any page or in the certificate) is `len(receipts with state COMPLETED)` and renders beside it `failed: F, not attempted: P` when
   nonzero. A check that raises is FAILED and renders as such -- never silently dropped, never counted as checked.
2. `scripts/verify_all.py` emits a limb receipt per limb with the same four states; its overall verdict derives from the receipts
   (any FAILED or unattended PLANNED => refuse). No limb is weakened.
3. The interval-provenance label `source-reported-CI:k=1-verbatim` (or whatever this base calls it) on a k>1 pool is rejected.

## Plants (FIRST, on the untouched tree; save to `.tmp/chk/prefix_pytest.txt`) -- `tests/test_check_counts_from_receipts.py`
- spy on the significance checker while building IV-iron's census: assert rendered N == number of real calls that completed (FIRES if
  the served N is 4 with 0 calls);
- inject a check that raises: the count must fall by one and the page must show `failed: 1` (FIRES if the exception is swallowed);
- the k=8 glp1 pool carrying a k=1-verbatim provenance label is rejected (FIRES if accepted);
- a page with zero completed checks renders the failing "Claims checked: 0" state, not a neutral one (may already HOLD -- record it).
Record FIRED / HELD per case. A fix that clears every failure is a loosened test: re-read each assertion after the fix.

## Then
- rebuild `iv-iron-hfref-hosp` and `glp1-ra-mace-t2d` (`--now 2026-09-11`), then all 32 if the census path is shared (it is);
  record which `review_sha256`/`html_sha256` moved and the new counts per page as a table (old N -> new completed/failed/planned);
- `python scripts/retraction_survival.py 237e9094` => 32 of 32 or STOP;
- targeted pytest counts; `python scripts/verify_all.py` if time allows, with the limb receipts it now emits pasted verbatim.

## Report (MEASURED / INFERRED / CLAIMED; `n of N`)
Plants pre/post; per-page count table; the diff summary; what the increment does NOT establish (GRADE NOT_ASSESSABLE is a separate
increment; certificate binding is a separate increment). Never a backslash escape through a heredoc; write regexes to files. No commit.
