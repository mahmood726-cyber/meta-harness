# Meta-harness: evidence-bounded outreach description

Prepared 11 October 2026. This document specifies the description for author outreach. It does not certify a release, report a fresh numerical validation, or establish that the generated public homepage has already been corrected.

## Description for authors

Meta-harness is a research-stage, open-source workflow for making the inputs, analytical decisions and outputs of a meta-analysis easier to inspect and rerun. It connects committed protocols, cached source material, screening and extraction records, analysis settings and generated review pages.

Internal replay checks on the legacy corpus demonstrate conditional computational recomputability from committed analysis inputs. They do not establish reproduction from a protocol-only registration commit, independent literature-search completeness, correctness of the evidence set, or autonomous systematic-review validity. The legacy corpus is an adversarial regression corpus, not a prospective validation set.

The proposed author collaboration is a reproducibility demonstration for one published review outcome, using publicly available or voluntarily shared study-level extraction data. The output would document inputs, source locations where available, software version and analysis settings, a regenerated plot, and a comparison with the published estimate. Differences in data or methods must be identified explicitly. No email may state that a particular review has been reproduced or audited unless that work has actually been completed and checked.

AllMeta is the related collection of browser-based evidence-synthesis tools. Synthesis is the related evidence-synthesis course collection. These are separate resources, not evidence that the harness has been validated. Publication analyses require method-appropriate checks against established statistical software. Do not describe the apps as universally validated, equivalent to every estimator in another package, or suitable for unreviewed clinical decisions.

## Claims to remove or replace on public-facing surfaces

| Unsupported or overbroad wording | Evidence-bounded replacement |
| --- | --- |
| The whole review regenerates from the protocol commit. | Internal replay uses committed analysis inputs and cached sources; registration-time reproduction is not established for the legacy corpus. |
| Every number is traceable and any hand-edit breaks the gate. | The workflow exposes committed inputs and provenance records for inspection. Coverage and enforcement depend on the specific release and recorded checks; a successful replay does not prove source correctness. |
| Independently verified superiority, the most auditable synthesis, or no published review makes this claim. | The project aims to improve auditability. No general superiority claim is established; any comparison must state its sample, methods, evidence and limitations. |
| A reader cannot check a Cochrane review number-by-number. They can check ours. | The project's attempted comparison did not recover every required value in machine-readable text. This is a limitation of that attempt, not proof that the published review cannot be checked from its figures, supplements, data or code. |
| A different model family is genuinely independent validation. | A different-model-family comparison is an additional consistency check; it does not by itself establish independent human adjudication or external validation. |
| A matching pooled estimate validates the review. | Agreement on identical inputs is arithmetic replication, not independent corroboration or evidence of complete study identification. |

## Source passages identified for the correction

The default-branch `harness/index.py` inspected for this task had blob SHA `6a43112322529eb2e80219180764be61e62974b2`. Its `_FRONT` banner, thesis/stance narrative, provenance and error-coverage text, and cross-family comparison text require review against the wording above. The default-branch README inspected had blob SHA `c6cc5c1c3d3e4e6183c96a9cf0eed9afae741f7f` and already distinguishes committed-input replay from registration-time reproduction, but some universal traceability/enforcement language also needs qualification.

## Requirements before the expanded author mailing

1. Correct the source generator, not just the generated homepage, so the next rebuild cannot restore the overclaims.
2. Regenerate the affected served files through the existing build process. Preserve scientific inputs, numerical methods, audit evidence, and negative findings.
3. Add regression checks for the removed claims and the required limitations; run the applicable existing checks. Do not bypass a failing verification or deployment gate.
4. Verify the deployed page and record the actual commit/status. A branch, pull request, or successful file write is not a verified live correction.
5. Verify the AllMeta and Synthesis destination pages and keep the invitation consistent with their actual features and limitations.
6. Build a sourced professional-author recipient ledger; deduplicate prior outreach and check objections, opt-outs, bounces, and applicable contact permissions before sending. Do not infer a private address from an institutional naming pattern.
7. Count only successful send receipts as sent. Existing introductory emails do not count as delivery of the new three-resource message. Never report that 1,000 authors have been reached without that many verified unique recipients and successful sends.

## Status when this document was created

The original 30-author AllMeta introduction batch was confirmed in Gmail. Those messages did not constitute the proposed combined Meta-harness, AllMeta and Synthesis campaign. No expanded-campaign messages were sent during this check. The public harness homepage was not successfully fetched by the web tool, so its currently served wording and deployment identity remain unverified in this check.
