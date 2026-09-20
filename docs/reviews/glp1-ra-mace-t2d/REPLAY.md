# Replaying the GLP-1 RA / MACE / T2D review from a clone — what reproduces, and how exactly

This is the outsider's procedure for milestone M1: obtain one frozen release and replay it without anyone filling in anything.
It states, **per output**, whether the replay reproduces the served bytes **exactly** or a value **within a declared numerical
tolerance**. Nothing below is "equivalent" without a number attached. "Cached execution, zero failures" in our CI is internal
evidence and is **not** what this document claims.

## What you are replaying

| item | identity | how to check you hold it |
|---|---|---|
| release commit | `main` at the commit named in the attestation you are replaying (currently `316d2e48`) | `git ls-remote origin refs/heads/main`; `git rev-parse <commit>` |
| served bytes = committed bytes | `production-records` branch, entry `production record <commit>: ATTESTED (n/n served files equal)` | `git log origin/production-records` |
| certificate | `docs/reviews/glp1-ra-mace-t2d/CERTIFICATE.json`, `release_sha256` | recomputed by `scripts/verify_bundle.py` (below) |
| analysis code | `CERTIFICATE.json.analysis_code_blobs`: 80 Git blob ids + 1 declared absence (`harness/effect_type.py = NOT_PRESENT`) | `git hash-object -- <path>` at the release commit equals each pin |
| held sources | `cache/glp1-ra-mace-t2d/` (records.json, ft_*.txt, aact_*.json, verified_*.json); acquisitions under `docs/acquisitions/glp1-ra-mace-t2d/` | sha256 per file is in `BUNDLE.json.artefacts` and `CERTIFICATE.json.held_documents` |
| recorded human/AI judgments | `cache/glp1-ra-mace-t2d/verified_arms.json`, `verified_effects.json` (hand-verified overrides, each with source and reason) | pinned by `extraction_objects_sha256` in the certificate |

**Generating tree.** For the release at `316d2e48` the tree that ran the generator is **UNRECORDED**: the generator wrote no
execution record, and no artefact names it. We do not reconstruct it. What *is* established: the served bytes equal the committed
bytes of `316d2e48` (attestation), and the tree of `316d2e48` contains all 80 pinned modules at the pinned blob ids. Releases built
after `scripts/execution_record.py` landed carry `docs/reviews/<slug>/EXECUTION_RECORD.json` (generating commit, branch, tree state
with dirty paths listed, host, UTC, interpreter, installed distributions, command, input and output digests, and the
`release_sha256` it accompanies); `verify_bundle.py` recomputes the record's sha256 against `BUNDLE.json.review_files` and its
`release_sha256` against the certificate, so a swapped record is refused. The ordering that forbids the reverse link: the
certificate is computed before the record exists.

## Commands (stdlib Python 3.11+, git; no network)

```
git clone --filter=blob:none <repo> && cd <repo> && git checkout <release commit>   # a full clone is ~67 GB of archive history
git status --porcelain                                        # must print nothing before you start
python scripts/build_topic_recorded.py glp1-ra-mace-t2d --now 2026-09-11   # the certified generator, then EXECUTION_RECORD.json
python scripts/build_bundle.py glp1-ra-mace-t2d               # re-stamps manifest.json `source` and rebuilds BUNDLE.json
python scripts/verify_bundle.py --root docs --slug glp1-ra-mace-t2d --json > verify.json
python scripts/verify_bundle.py --root docs --slug glp1-ra-mace-t2d --corrupt 27633186 effect --json   # a control: must refuse
python -m pytest tests/test_bundle.py tests/test_bundle_verifier.py tests/test_exclusion_relation.py tests/test_execution_record.py -q
```

`--now 2026-09-11` is the build date the served `manifest.json.build_utc` records; it is a label, not a clock. The wrapper
`scripts/build_topic_recorded.py` exists because `scripts/build_topic.py` is a pinned root of the certificate: changing a byte of it
is a release change, so until a new release is cut the record is written by the unpinned wrapper after the certified generator
returns. The record's `command.argv` says which.

**Measured on 2026-09-20 in a fresh local clone of `4b9dd46b`** (branch head carrying this document; the review directory there is
byte-identical to `316d2e48`'s): the wrapper ran in 50 s and reproduced `review_sha256 d3f33833…`, `html_sha256 91d15b51…` and
`release_sha256 747612a8…` exactly. Two files legitimately differ after the generator step and are not part of the release claim:
`manifest.json` lacks the `source` block until `build_bundle.py` re-stamps it (then identical), and `registry/blind_map.json` is a
"last topic built" side file (the committed copy names another topic). One trap found the same day: **placing any new `.py` file
under `harness/` changes `certificate_scope.not_covered` and therefore `release_sha256`, even if nothing imports it** — the scope
list is part of the certificate by design. Replay helpers live under `scripts/` for that reason.

## Per-output reproduction claims

| output | claim | how it is checked | what a difference means |
|---|---|---|---|
| `review.json` (review core, canonical JSON) | **EXACT** — `review_sha256` equal | `reproduce_review.py` replays from `cache/` and compares `review_sha256` to `manifest.json`/`CERTIFICATE.json` | any difference is a failure of the replay, not a tolerance |
| `CERTIFICATE.json` | **EXACT** — `release_sha256` recomputed over every other field | `verify_bundle.py` (`certificate.release_sha256_recomputed`) and `harness/certificate.verify` | a differing byte in any pinned module or input moves it |
| `index.html` | **EXACT** — `html_sha256` in `manifest.json` | `harness/census.py` on a fresh clone | renderer or review core differs |
| pooled primary estimate HR 0.8559934175939847 (0.8086248326603205–0.9061368157018077), τ² 4.4479725e-05 | **EXACT under the certified path** (pure stdlib float arithmetic, Paule–Mandel + HKSJ with floor; `verify_bundle.py` reimplements it independently and reproduces every digit) | `verify.json` → `pool` | **for a third-party implementation** (e.g. metafor `rma(method="PM", test="knha")` with the same floor) the declared tolerance is **|Δ log(HR)| ≤ 1e-6 and |Δ τ²| ≤ 1e-8**. The tolerance exists **only** because a different implementation sums the weighted terms in a different order, stops the Paule–Mandel root search at a different iterate, and evaluates the t-quantile by a different routine — floating-point effects of order 1e-12 to 1e-9, which the bound covers with margin. It is **not** latitude on the method: the estimator (PM τ²), the interval (HKSJ, t with k−1 df, variance floor max(1, Q/(k−1))) and the inputs are fixed; a difference outside the bound is a method difference, and you should state which floor and which t-quantile you used |
| per-row admission (`verification_rows[].admission.final`) | **EXACT** — 7 ADMISSIBLE, 1 INADMISSIBLE (Harmony, P5 eligibility UNKNOWN) | `verify_bundle.py` recomputes P1–P14 from served bytes; `rows[].agrees_with_bundle` | a disagreement is `ROW_VERDICT_DISAGREES`, printed |
| `BUNDLE.json` | **EXACT at the same commit**, except `source.content_commit` (informational; names the latest commit holding the served blobs and moves with history) and `build_utc` | `python scripts/build_bundle.py glp1-ra-mace-t2d` then `git diff` | any difference outside those two fields is a failure |
| retained EFetch XML vs the cached abstract (anchor) | **EXACT** for the 11 retained acquisitions (`anchors[].xml_digest_ok`, units preserved) | `verify_bundle.py`; `--anchor live` re-fetches PubMed **now** and compares — that is an *external observation of the current record*, not a replay, and PubMed `DateRevised` can move | a live difference is a fact about PubMed today (SOUL's record was revised 2026-02-02), not about the release |

## Explicitly out of scope of the replay claim

- **Fresh internet searches.** The build reads the committed cache (`from_cache=True`); the page declares known-item retrieval,
  not a systematic search. Re-running the searches is a different claim and is not made here.
- **Regenerating AI or human judgments.** Hand-verified overrides are *recorded* inputs (pinned digests); they are replayed, not
  re-derived. No claim is made that they would be reproduced identically by re-running any model or person.
- **Completeness.** Eligible-but-unpooled evidence, incomplete RoB 2 / GRADE and the unbound harms rows are disclosed on the page
  and in `BUNDLE.json.limits` (L1–L15). Disclosure does not complete a search; this document does not claim it does.
- **The producer's `verified` label.** `harness/verify.py` (blob `e5187ea9cc8e`, pinned) checks the point estimate's digits only,
  accepts the RRR complement unconditionally (line 58), uses the hand-written `source` field as its own haystack for non-abstract
  provenances (lines 68/73) and never compares the effect measure. `BUNDLE.json` carries that label as a **producer assertion**
  (`producer_labels`), not as verification; the bundle's own P1–P14 are what the replay checks.

## Reading a difference

1. `git status` must be clean at the release commit before you start; if it is not, you are not replaying the release.
2. A digest mismatch names the file; a numerical difference must be reported with the tolerance above beside it.
3. `verify_bundle.py` prints `NOT checked:` — those are the limits of what this replay establishes, and they apply to you too.
