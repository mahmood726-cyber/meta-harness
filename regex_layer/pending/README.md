# Pending: R1 + R4 in `harness/extract.py` — handover to the main lane's next re-certification

`R1_R4_extract.patch` (sha256 `a271f64a791530bdc2ec35577431dc37ab313fb66a71700dcb6613175706d02e`) is based on main
`4d712dfa`. It changes five files:

- `harness/extract.py` gets two groups of edits:
  - **R1:** the bare tuples become `ArmCounts`, `Effect`, `ContinuousArms` and `RateArms`, plus the internal `ArmHit`,
    `MeanSDHit` and `RateHit`.
  - **R4:** the 11 extractor patterns read only inside extract.py are wrapped in `whole_numbers()`.
- `harness/extract_values.py` (new) holds the NamedTuples. They are equal to the bare tuples, unpack the same and
  serialise to identical JSON.
- `harness/whole_numbers.py` (new) holds the single definition of a number fragment. `regex_layer/partial.py` imports
  it once this lands.
- `tests/test_extract_values.py` and `tests/test_whole_numbers.py` hold the plants. Each fragment plant is proven to
  contain a fragment before the served pattern is asked to refuse it.

`_EFFECT` is deliberately **not** wrapped: `harness/absence.py` and `harness/reason_audit.py` also read it. It has 0
fragment matches in the held sentences.

## Why it is not on main as code
extract.py is in every page's certificate closure, and `docs/harness/` is a byte mirror of `harness/`. So the change
lands only with the mirror update and a re-certification of every page. That is the main lane's process
(`scripts/rebuild_invariance.py`). A hook bypass is not an option.

## Radius (measured, not argued)
| change | instrument | result |
|---|---|---|
| R1 alone | whole-corpus snapshot of `extract.extract_trial` (every cached record × every declared outcome, abstract + PMC full text; 10,098 extractions) on main vs patched | **byte-identical** |
| R4 (refusal, in-process) | `python -m regex_layer.radius refuse_partial` | **0 of 10,098 differ; 0 served**. It reaches 69 of 127 served rows. The other 58 are hand-verified, ct.gov-results, published-rate or pre-specified-dose rows, which never call `extract_trial` |
| R1 + R4 as patched | the same snapshot: the patched harness package (a copy of `harness/` with this patch applied, data read via `REGEX_LAYER_DATA_ROOT`) vs main | **byte-identical** (10,098 extractions, `cmp` equal) |

Proof the instrument can move: the planted change `plant_dead_extractors` moves 27 of 198 extractions on one topic,
3 of them served.

## What the re-certification must still check
- `absence.py` / `reason_audit.py` are untouched by the patch. Confirm that no page renders a repr of an extract tuple:
  a NamedTuple's repr differs from a tuple's. The offline-reproduction limb covers this.
- Mirror `harness/extract.py`, `extract_values.py` and `whole_numbers.py` into `docs/harness/`.
- This patch fixes none of the located defects: RX-D1, RX-TE1..3 and RX-EC1..3 stay strict xfails. Their fixes change
  what matches, so each needs its own measured radius.
