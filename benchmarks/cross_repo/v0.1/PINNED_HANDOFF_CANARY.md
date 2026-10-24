# Pinned synthetic RapidMeta refusal canary (research-stage)

This is a separately executable Meta-Harness producer → strict raw-JSON transport validator → archived source-span/trial/estimand gate → **actual pinned RapidMeta JS** smoke check. It is NOT clinical validation, independent study discovery, general quantitative extraction, statistical R parity or a four-repository benchmark.

## Frozen inputs and dependencies

RapidMeta checkout must have Git HEAD `368137dc437543c721b98be39c14282c338f7797` (the existing benchmark pin). Node loads its production `template/assets/vendor/pairwise-pool.js` unmodified. The input `synthetic-binary-arms.txt` has immutable SHA-256 `666a0354b2668dd0f90780becff303eab28a007fa895650ba09793732d374398`. Runtime pins: Python 3.13.7 and Node 22.14.0. GitHub checkout/setup/upload actions use full Git commit SHAs. No third-party Python dependencies are installed.

**Important:** the Meta-Harness integration runner is checked out at the new PR's actual head, which is recorded in the output. It is NOT the older `a62cbc...` Meta-Harness source pin declared in the v0.1 manifest. The original 15 benchmark cases therefore remain NOT_RUN. Counts, trial identities and source spans in the canary are deliberately fictional simulation data, not published clinical evidence.

## Reproduce

With both repositories cloned side by side and RapidMeta checked out at the above SHA, run from their common parent directory:

    python meta-harness/benchmarks/cross_repo/v0.1/pinned_pairwise_canary.py --rapidmeta rapidmeta-kit --output a-new-empty-evidence-directory

The output path must not exist. The script checks the exact RapidMeta SHA, the source file's SHA-256, the Python schema/locator/refusal gate and the real RapidMeta production Node entry point. It writes all six exact raw JSON inputs, six result JSON outputs and a digest index. It never rewrites the existing fixture or source manifest. For CI, see .github/workflows/pinned-refusal-handoff.yml, which uses a clean Ubuntu 24.04 runner and archives the raw inputs, outputs and SHA-256 index for independent inspection.

## Negative cases and honest coverage

A positive ALLOW control loads the **real, pinned RapidMeta module** once with two explicitly source-spanned synthetic count rows; it reports only a limited smoke result, not R parity. REFUSE, MANUAL_REVIEW, a duplicate shadowed decision field, source digest tampering and an inconsistent trial identity each refuse **before Node is invoked**. A separate CI step recomputes every input/output hash and checks all five negative results and the one synthetic control.

The temporary count-line grammar is **canary-only** and hard restricted to the exact fixture's two trials and RR/ITT synthetic outcome; it is not a general extraction schema or a pathway to pool real data. The versioned v0.1 exchange schema does not encode numerical effects; production clinical pooling remains unsupported at this boundary until independently specified and validated.

The common benchmark cases CROSS-EXCH-001 through -015 remain NOT_RUN without runs of their own frozen inputs and commits. The reserved proposed ASReview-learning case CROSS-EXCH-016 is untouched. This new bounded canary should not be represented as four-repository CI, Windows installation, signature verification, prospective discovery, independent adjudication, independent R oracle or external usability validation.