# LANE XS — a registry "corroboration" must be of the SAME endpoint as the pooled number; sweep every cross-source corroboration for endpoint mismatch

Report file: `LANE-XS-REPORT.md`.

## The failure (external audit, 2026-09-16, confirmed on served bytes at aa8ed28a)

`pcsk9-mace`: the ClinicalTrials.gov corroborating quantity displayed for FOURIER (PMID 28304224, NCT01764633) is ≈0.666, while the primary-endpoint proportions shown on the same page imply ≈ mid-0.8s, consistent with the published HR 0.85. Both cannot corroborate the same endpoint — the registry row is a different outcome measure (a secondary/key-secondary composite, or a different population/timepoint). It does not corrupt the pool (the published HR is what is pooled) but it is presented as corroboration of it.

Where it lives: `harness/pipeline.py::_cross_source` (grep `cross_source`), `harness/ctgov_results.py`, the trial row field `cross_source`, and the rendering in `harness/page.py` (grep `cross_source`, `corroborat`). Also `docs/verified_arms_audit.json` / `scripts/verify_verified_arms.py` if they touch this.

## What to build

1. A cross-source row must carry the registry outcome-measure TITLE, its type (`COUNT_OF_PARTICIPANTS` / hazard ratio / rate…), its timepoint and analysis population, and a typed `endpoint_match` verdict against the pooled outcome: `SAME_ENDPOINT` (title/description matches the pooled outcome's estimand and components; conversion between HR and proportion-RR stated explicitly), `DIFFERENT_ENDPOINT` (with the registry title quoted), `NOT_CHECKABLE`. Only `SAME_ENDPOINT` renders as corroboration; the others render as "registry reports a DIFFERENT measure: <title>" and are excluded from any corroboration count/percentage on the page.
2. Corpus-wide sweep `scripts/cross_source_endpoint_sweep.py` → `docs/cross_source_endpoint_sweep.json`: for all 32 topics, every pooled row with a `cross_source`/registry corroboration; compute the implied effect from the registry numbers and from the pooled row; classify; table in the report: slug, trial_key, pooled value, registry title, registry-implied value, verdict. `n mismatched of N corroborations over 32 topics`.
3. Rebuild affected pages; `reproduce_review.py` each; quote pcsk9's FOURIER row before/after.

## Plant (must fire pre-fix)

`tests/test_cross_source_endpoint.py`: pre-fix fixture copy of `docs/reviews/pcsk9-mace/review.json` → the FOURIER row's `cross_source` is rendered as corroboration while its implied ratio (≈0.666) differs from the pooled 0.85 by more than the tolerance you state → your check returns `DIFFERENT_ENDPOINT`/mismatch (quote the numbers and the registry title from `cache/pcsk9-mace/` CT.gov results); post-fix rebuilt object → the row is labelled as a different measure and excluded from the corroboration count. Synthetic control: a registry row whose proportions reproduce the pooled RR within tolerance → `SAME_ENDPOINT`.

Do not touch: pooling, `harness/synth.py`, `harness/extract.py` (read-only), `harness/rob_sensitivity.py`, `harness/grade.py`, search code, which trials are pooled, network (use the cached CT.gov results only; if a registry result is not cached, the verdict is `NOT_CHECKABLE`, never a fetch).
## Standing rules for this lane (read fully; every line below has cost real time before)

- You are in a fresh clone of `meta-harness` at commit `aa8ed28a` (detached). Work ONLY inside this directory. You cannot and must not commit; the integrator harvests your diff. Do not run `git add`, `git commit`, `git stash`, `git checkout`, `git reset` or `git clean`. Do not touch `.git/`.
- Never stop, kill, or signal any process. Never run `git gc`, `git prune`, or delete files outside this clone.
- Write temp files only under `./.tmp/` (TMP/TEMP already point there).
- Python: `python` (3.13). Run tests with `python -m pytest tests -x -q` (about 3–4 min) and the targeted files you add. Do NOT run `scripts/verify_all.py` (12 min, integrator's job) and do NOT run any script that needs the network unless the brief says so.
- Rebuild a page with `python scripts/build_topic.py <slug> --now 2026-09-11`. That regenerates `docs/reviews/<slug>/` and `docs/m/<token>/` from committed cache (no network). `python scripts/reproduce_review.py <slug>` then checks the page byte-matches a replay. Note `cache/*/snapshots/` is sparse-excluded from this clone; the build does not need it.
- Style: match the surrounding code — same comment density, naming, idiom. Comments say WHY. No marketing words.
- HARD RULES ON EVIDENCE: do NOT re-run any search, do NOT add or remove any trial from any pool except where this brief explicitly names the change, do NOT weaken an endpoint/estimand gate to make a trial poolable, do NOT rebuild the extractor.
- PLANT DISCIPLINE (the whole point): every gate/check you add MUST be shown to FIRE on the pre-fix state of the named page(s). Do that by writing a test that loads the COMMITTED pre-fix object (`git show aa8ed28a:docs/reviews/<slug>/review.json` — read-only `git show` is allowed — or a fixture you copy from it into `tests/fixtures/`) and asserts the check refuses it. Then apply your fix, rebuild the page, and show the same check passes on the rebuilt object. A check that passes post-fix but was never shown to fail pre-fix proves nothing. A fix that makes every failure vanish is a loosened test — say so if it happens.
- Every number in your report is marked MEASURED (you ran it and quote the output), INFERRED (derived, say from what) or CLAIMED (someone else's statement). Use `n of N` with N named. A 100% result is reported as a defect unless you also show the instrument can fail.
- Report file: write `LANE-<LANE>-REPORT.md` in the clone root (name given below). Structure: (1) what was wrong, mechanism, files; (2) the plant — test name, the exact assertion, its output on the pre-fix object (quote it), its output post-fix; (3) every page whose rebuilt bytes changed, with before/after of the specific numbers/sentences; (4) tests: the pytest summary line verbatim; (5) what you did NOT do and why; (6) list every file you changed or added. Finish condition: the report exists and the tests you name pass. If blocked, write the report saying exactly where and stop.
