# Target assertion 2026-09-14

**Fix state (five-state rule): LANDED** - every listed check names its target or refuses.

Finding closed: a check that does not print the commit, tree state, and file/URL set it examined can be mistaken for a check run against the intended target. The lane adds a shared `TARGET` line to every touched check and makes unresolved refs or unnamed file sets stop as `COULD-NOT-EXECUTE`.

| check | target line printed | refuses when unnamed: plant shown |
|---|---|---|
| `scripts/verify_all.py` | Top-level `TARGET verify_all` plus one `TARGET verify_all.<limb>` per limb. | `tests/test_verify_all_target.py` runs from a non-git cwd with `GIT_CEILING_DIRECTORIES`; output starts `TARGET verify_all: COULD-NOT-EXECUTE`. |
| `harness.honest_ratchet` | `TARGET honest_ratchet` names HEAD, base, base-resolution method, page count, and block-floor refs. | `python -m harness.honest_ratchet --base no-such-ref` refuses before comparison. |
| `harness.gate_scorecard` | `TARGET gate_scorecard` names registry, served view, and enumerator files. | `tests/test_gate_scorecard.py::test_missing_registry_path_refuses_as_unnamed_target`. |
| `harness.fixstate` | `TARGET fixstate` names registry, generated ledger, renderer, and baseline ref. | `tests/test_fixstate.py::test_downgrade_to_reported_requires_detector_or_stale_reason`. |
| `scripts/build_evidence_index.py --check` | `TARGET evidence_index` names `CAPTIONS.json` plus evidence captures. | Missing captions or empty file set refuses before index comparison. |
| `harness.heldout` | `TARGET heldout` names sealed registry, regression measurement, and acquisition engine. | Missing registry refuses before key-dependent scan. |
| `harness.leakscan` | `TARGET leakscan` names served aggregate JSON and review objects. | Empty scan set refuses. |
| `scripts/measure_regression_corpus_recall.py` | `TARGET regression_corpus_recall` names regression registry, engine, topic configs, and review objects. | Unreadable registry refuses before live search. |
| `scripts/production_record.py` | `TARGET production_record.manifest/check_artifact/attest` names the docs set, manifest commit, tar, or served URL set. | Missing manifest refuses before artifact or URL comparison. |

## Captures

- `01-prefix-checks-silent-on-target.txt`: prefix outputs at base commit `a3872489` showed pass/fail summaries without any `TARGET` line.
- `02-postfix-target-lines.txt`: final target lines from the touched checks.
- `03-refusals-planted.txt`: planted unresolvable target refusals.
- `04-ratchet-state-down.txt`: fix-state transition for `TRANCHE-retrieval-states-and-ratchet` from `LANDED` to `REPORTED`.
