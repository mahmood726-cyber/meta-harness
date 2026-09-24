# Regex layer — where R1–R4 stand (2026-09-24 evening)

Everything here is measured against a population the code derives itself. No number is copied from memory.

| | what | state | evidence |
|---|---|---|---|
| **Inventory** | every regex site in `harness/*.py`, found by AST | **399 sites**: 148 compiled, 251 inline literals | `python -m regex_layer.inventory` |
| **R3** plants | a named accept/refuse plant per site; a permissive mutant and a dead mutant must each fail ≥1 | all 74 sites of the owned files: extract.py 32, target_endpoint.py 31, eligibility_chain.py 8, compat_check.py 3; harness-wide **74 of 399** | `tests/test_regex_plants.py` |
| R3 ratchet | owned files' unplanted sites may only shrink | **0 left** | `regex_layer/sites_without_plants.json` |
| **R2** precision / recall | per pattern of extract.py against 641 recorded, replayable, verifier-gated labels | **23 of 23 patterns measured** | `MEASUREMENT.md` |
| **R4** partial numbers | matches that read a fragment of a number (grouped, decimal, digit run) | found in all 35,673 held sentences: `_NEQ` 91, `_ARMP` 39, `_RATE_EVPT` 15, `_ARM` 1, `_MEAN_SD` 1 (and `_DOSE_ARM` 17, which has no reader) | `PARTIAL_NUMBERS.json` |
| R4 radius | refusing those matches in the served producer's entry point | **0 of 10,098** extractions change; 0 served. This covers 69 of 127 served rows. The other 58 come from producers that do not call `extract_trial` (hand-verified, ct.gov results, published rate, pre-specified dose). Those are listed by provenance and not counted as radius | `RADIUS_refuse_partial.json` |
| **R1** typed values + **R4** refusal in the served code | NamedTuples for the bare tuples; 11 in-module extractors refuse number fragments | a handover patch for the main lane's next re-certification; the whole-corpus extraction snapshot is **byte-identical** to main (10,098 extractions) | `regex_layer/pending/` |

## Located defects (strict xfail, so a fix flips them)
- **RX-D1** `_DENOM_EACH` misses "patients were randomly assigned to each". Latent: 0 held abstracts.
- **RX-TE1** target_endpoint: "death from any cause or cardiovascular hospitalization" is read as naming CV death. The phrasing occurs in held text; its effect on a served row is not measured.
- **RX-TE2** target_endpoint: `\bvascular death` fires inside "non-vascular death". The phrasing occurs in held text; not measured.
- **RX-TE3** target_endpoint: `\bfatal\b` fires inside "non-fatal". Latent for this wording.
- **RX-EC1** eligibility_chain: '**Population:**' (colon inside the bold) is never read. Reachable in held protocols; no criterion lost today.
- **RX-EC2** eligibility_chain: an em-dash separator is not read. **Consequential**: colchicine-recurrent-pericarditis gets no follow-up-window criterion (reproduced by hand).
- **RX-EC3** compat_check: 'children and adults' is read as an adult-only comparator. Phrase in held comparator bytes; reach not measured.
- **R4 class** `_NEQ` has no word boundary: "P for interactio**n = 0**.92" gives n = 0. `_RATE_EVPT` reads a rate's decimals as counts: "7.**3** events per 100 person-years" gives 3.

## Read before quoting a number
- The labels are model **proposals**, not countersigned. Every precision/recall figure says it is measured against recorded proposals.
- Recall is **sampled** recall. Sentences with no trigger word are never examined.
- `_DEF_CUE` is read only together with `_ANCHOR_RX`, so its standalone precision (1 of 15) is not its contract. Four patterns have **no reader** in `harness/` (`_DOSE_ARM`, `_RATE_UNIT`, `_MORT_Y`, `_MORT_D`): their numbers cannot move a served value.
