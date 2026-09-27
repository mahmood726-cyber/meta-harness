# BND1 and POOL cannot be merged by patch application: they were built on different trees

Measured 2026-09-24. Nothing landed. The integration tree was restored with zero residue and re-verified.

## The instruction
"Merge BND1 with POOL properly" — on the understanding that they conflict textually, both editing
`harness/gate.py` and `scripts/verify_bundle.py`.

## What is actually true
They do not conflict as two edits to the same lines. They are patches against **different baselines**:

    a4e556e3 (main)              harness/gate.py  "def admission_scope"  ->  0
    1fa77f2c (enforcement-gate)  harness/gate.py  "def admission_scope"  ->  1

- **POOL** was built on `origin/main` (`a4e556e3`) — because my lane brief said so, verbatim: *"Check out the
  CURRENT `origin/main`, not the branch."*
- **BND1** was built on the `enforcement-gate` branch (`1fa77f2c`), and its central addition
  `estimand_audit()` is written to sit beside `admission_scope()`, which exists only on that branch. It was
  introduced by the enforcement-gate landing `b25027e3` ("the build reads the admission decision at pooling").

So `git apply` fails not because the changes disagree but because BND1 depends on code that is not present in
the tree POOL targets. Applying it there produced a **half-applied patch**: 5 hunks clean, hunk 6 rejected,
`verify_bundle.py` taking content while `gate.py` and the tests did not — the state in which a patch looks
installed and is not.

## The cause is a briefing fault, and it is mine
I directed the POOL lane to main while BND1 already existed on the branch. Two repairs to the same two files,
aimed at two different trees, cannot be combined afterwards by patching.

## What "merge properly" therefore requires
Not a merge — a **choice of common base**, and then a rebuild of one side on it:
- **(a) Rebase POOL onto `enforcement-gate`**, where BND1 already fits and where the admission work lives.
  This is the practical route: the branch is where this entire body of work sits, and POOL's changes
  (`check_pool_contract`, the five-verdict split, the selected set) do not depend on anything main-only.
- **(b) Land the branch's admission work to main first**, then apply both on main. This is blocked by the
  same 41-notice question that Decision B is answering, and by the branch being RED by design.

**(a) is the recommendation.** It also removes the mismatch for everything downstream: `MASKING`, `ARM_final`
and `REGSPAN` were all built on main and would need the same treatment if the branch is the destination.

## A consequence that must not be lost
Whichever base is chosen, BND1 must NOT be merged in its measured form. Its `ESTIMAND_UNOBSERVED` behaviour
abstains 42 of 46 served occurrences and empties 29 of 29 result objects, which is the §F.5 violation ruled on
in `21-decision-estimand-repair-under-F5.md`. **Merge first, then apply the §F.5 restructure** — merging and
landing in one step reimports the corpus-emptying.

## State after this investigation
Integration tree restored from backups; `estimand_audit`, `estimand_check`, `duration_value_swap` all absent
from `gate.py`, `verify_bundle.py` and `build_bundle.py`; F.2 (`input_linkage`) and F.3 (`selected_set`)
intact; the four-patch landing stack still applies to pristine `a4e556e3` and passes 95 tests together.
