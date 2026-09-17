# Lane GS report

Status: machinery and GRADE repair implemented and tested; the requested fully computable GLP-1 finish condition is BLOCKED by missing committed FACT provenance. No commit, push, deployment, or external network action. All new artifacts remain local and uncommitted, as instructed.

Base HEAD: `e3b70bfa36dc65a3920b20fd4e2d628a270e7d28`, matching the prompt. `LANE_BASE.txt` is absent.

## Delivered and measured coverage

- `harness/envelope.py`: PM through the unchanged canonical engine, REML sensitivity, floored HKSJ/Wald, fixed/random, formal low-RoB restriction, GLP-1 membership and endpoint/timepoint alternatives. Every input is checked by `claimgraph.verify_fact`; missing or altered committed evidence refuses computation. The enumeration is explicitly one axis at a time, not an exhaustive Cartesian specification search. Duplicate trial identities and mixed effect scales refuse.
- `harness/fragility.py`: separate point-direction and CI-null-crossing changes for leave-one-out, single eligible endpoint swaps, RoB exclusions, and hypothetical null studies. Median size means median observed SE; largest means maximum inverse-variance information (minimum SE), not largest participant count. Hypothetical rows are labelled transformations, never observed FACTs. Search is limited to one change; no global minimum across larger combinations is claimed.
- `harness/decomposer.py`: general source-gated progressive replay and adjacent-step log-effect deltas; missing intermediate tables do not become zero deltas. The GLP-1 held comparator is Giugliano 2021. Its text specifies empirical Bayes/Paule-Mandel and Hartung-Knapp, but not the variance-floor convention, and its per-trial numerical table is not available in held text. Step 0 renders `NOT REPRODUCIBLE FROM HELD TEXT`; later unavailable steps render `NOT_COMPUTABLE`. Hasebe 2025 renders `COMPARATOR NOT HELD`. No numerical attribution or replication is asserted. Endpoint-definition and effect-estimate changes remain a combined extraction step unless separately identifiable inputs exist.
- `harness/grade.py`: category arithmetic includes upgrades and explicitly bounds the four-level ordinal scale. Unassessed domains produce `provisional` with names, instead of an implicit MODERATE cap. `imprecision_basis` explicitly identifies the observed-evidence CI. The D3 coverage join now uses trial identity, so the acronym-labelled SOUL is counted correctly.
- `page.py`, `gate.py`, `claimgraph.py`, and the pipeline consume these objects. The GS gate re-derives objects and requires exact rendered tables; mutated and additional unbound envelope/fragility sentences refuse. Canonical GRADE rendering supports upgrades. Original trial membership, screening, search, comparator data, and `synth.py` are unchanged.
- `scripts/grade_arithmetic_sweep.py --write` writes `envelope.json`, `fragility.json`, and `decomposer.json` under each of 32 topic caches, updates the 32 local review objects/pages, and refreshes their local content hashes. It does not claim a new release census or Overmind PASS.

**MEASURED:** [GRADE sweep](docs/grade_arithmetic_sweep.json) found **14 categorical arithmetic mismatches among 32 review pages before, zero among 32 after**. Of the 32 after-state pages, 31 are provisional and one remains not rateable because its estimands are incompatible. Eight of the 32 before-state pages carried the D3 cap flag. The prompt's historical 19-of-31 and 11-cap counts were not reproduced at this base and were not copied into results.

**MEASURED:** [validation audit](docs/gs_validation.json) found **zero computable envelope specifications among 170 enumerated across the 32 current review objects**. GLP-1 has zero computable specifications among 15 enumerated. All eight served GLP-1 rows lack the complete CGX provenance required for certified computation. This is an input-contract finding, not evidence that effects are unstable or that all possible source recovery routes have been exhausted. The cache objects and page tables record the refusals; no ordinal robustness score is assigned.

## Source and statistical review

Three of three recovered regulatory alternative rows pass CGX verification against committed document and extracted-text bytes, including exact spans and SHA-256 digests:

| Held source / alternative | Source-reported HR and CI | Provenance |
|---|---|---|
| ELIXA strict 3-point, on-study | 1.02 [0.887, 1.172] | FDA statistical review; `regulatory_sources_glp1.json` decision and literal extracted paragraph |
| FREEDOM-CVO strict 3-point, end of study | 1.24 [0.90, 1.70] | FDA ITCA650 review, Table 19, FREEDOM-only |
| FREEDOM-CVO strict 3-point, end of treatment | 1.36 [0.96, 1.92] | Same committed FDA review, Table 24, FREEDOM-only |

See the exact located spans, identifiers, retrieval timestamps (verified by CGX), and digests in [the source registry](outputs/handover/glp1_regulatory/regulatory_sources_glp1.json), the generated envelope alternatives, and [the audit](docs/gs_validation.json). EOT and EOS are alternatives for the same trial and cannot be pooled as independent studies. FLOW and ELIXA's four-point abstract alternative remain explicit unsupported inputs under the current held-document contract. Regulatory controls do not repair the eight primary rows' provenance.

**MEASURED numerical diagnostic, conditional on the legacy extraction:** calling the unchanged synthesis engine on the eight served GLP-1 rows gives HR `0.8559934175939847`, tau2 `0.000044479725147539284`, I2 `0.8599857615190106%`, observed-evidence CI `[0.8086248326603205, 0.9061368157018077]`, and PI `[0.8068929729560542, 0.9080816855795524]`. Eight of the eight typed input estimates are below one. These are computational checks of legacy rows, **not newly FACT-certified clinical findings**. Imprecision uses the observed-evidence CI, not the PI; overall GRADE is provisional because indirectness, publication bias, and D3 are unassessed. D3 coverage is eight of eight after the identity-join correction.

The numerical kernel reproduces `synth.pool` to `1e-6` and reproduces the stored page value after its four-decimal rounding. However, the raw result differs from the stored `0.856` by `6.582406015254172e-6`: the literal unrounded `1e-6` page criterion is not met. It was not hidden with a looser tolerance or by changing primary output. The source-gated served specification correctly remains uncomputable.

For positive tau2, PIs use `t_(k-1)` and differ from their CIs. When tau2 is zero, the prescribed floored HKSJ formula would collapse the PI onto the CI; the envelope emits an explicit unavailable PI instead of displaying an identical interval or altering `synth.py`. A fixed-effect specification also has no random-effects PI.

**INFERRED limitation:** missing FACT inputs and unidentified comparator steps prevent a certified robustness, fragility, coincidence, or disagreement attribution conclusion. No clinical stability claim is made from the refusal count.

## Hardcode disclosure

| Component | Static policy or assumption | Dynamic source / validation |
|---|---|---|
| Specifications | Named axes; one-axis-at-a-time scope; lower MACE HR is favourable | Current primary rows, known-missing object, formal RoB domains, committed regulatory decisions |
| Statistical methods | PM/REML; HKSJ floor; Wald; `t_(k-1)` PI | Recomputed effects, variances, tau2, I2, CIs; PM agrees with unchanged engine; REML checked against equal-variance analytic solution |
| Null studies | Explicit counterfactual HR=1 | SE derived from median/minimum observed SE; never an observed research row |
| GRADE | Four-level scale and existing stated domain rules | Domain arithmetic and unassessed names; before-state read from HEAD, not memory |
| Comparator | Progressive replay order | Held text, comparator-truth/parity modules, source-gated intermediate tables; unidentified deltas stay null |
| Research outputs | No fixed research estimates, rankings, or stability verdicts | Generated from inputs or explicitly refused; all fabricated pools are test fixtures only |

## Verification and remaining finish blockers

The combined affected-module regression run passed **111 tests** (`68.72s`), covering GS, GRADE, provenance, synthesis, page, claimgraph, comparator, parity, RoB, and gate modules. The GS suite includes an HTTP E2E contract at `http://127.0.0.1:8000/`, all 32 cached-object/render/hash comparisons, real regulatory controls, tamper plants, duplicate refusal, and analytic REML/fixed-effect controls. An additional GS run after extending the unbound-sentence gate passed 11 tests. The final GRADE identity-join recheck is recorded below. `git diff --check` passed.

Two old CGX tests expected stale working-tree HTML; their pre-fix plants now read the immutable base commit. The old gate-fixture test expected a source-less synthetic page to pass; its failure was reproduced with the base renderer and its assertion was corrected to require the CGX refusal. Four legacy GRADE assertions were updated from implicit caps to named provisional status. Existing gate tests' unrelated `effect_types.json` rewrites were restored to their initial committed bytes.

The full requested finish remains blocked, as recorded in [STUCK_FAILURES.md](STUCK_FAILURES.md): primary GLP-1 FACT provenance is absent; comparator intermediate inputs/method detail are insufficient; and the raw page precision criterion differs from its stored rounding. Completing those requires a separately authorized source-ingestion/commit step or a clarified precision contract. The current no-network/no-commit instruction was preserved. No project status, submission state, index, workbook, or release status was promoted.

Final targeted recheck after the D3 identity correction: **36 passed in 13.27s**, including GRADE, GS corpus/HTTP contracts, FACT provenance, and synthesis tests. Reproduce artifacts with `python scripts/grade_arithmetic_sweep.py --write` (before-state pinned to the lane base; override with `--baseline`), then `python scripts/gs_validation.py`. All source statistics and audit counts above are measured outputs of those commands; local hash refresh is not a release approval.

## Required pre-fix plants (verbatim output)

The envelope and fragility plants failed by module absence. The arithmetic plant failed because no validator existed. These failures were run before implementation.

```text
FFF                                                                      [100%]
================================== FAILURES ===================================
_______________________ test_unsourced_envelope_refused _______________________

    def test_unsourced_envelope_refused():
>       module = importlib.import_module('harness.envelope')
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_gs_layers.py:7: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
C:\Users\mahmo\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1395: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

name = 'harness.envelope'
import_ = <function _gcd_import at 0x000001D2853004A0>

>   ???
E   ModuleNotFoundError: No module named 'harness.envelope'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
_______________________ test_fragility_direction_plant ________________________

    def test_fragility_direction_plant():
>       module = importlib.import_module('harness.fragility')
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_gs_layers.py:15: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
C:\Users\mahmo\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1395: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

name = 'harness.fragility'
import_ = <function _gcd_import at 0x000001D2853004A0>

>   ???
E   ModuleNotFoundError: No module named 'harness.fragility'

<frozen importlib._bootstrap>:1324: ModuleNotFoundError
_________________________ test_grade_arithmetic_plant _________________________

    def test_grade_arithmetic_plant():
        from harness import grade
        with pytest.raises(ValueError, match='REFUSED'):
>           grade.validate_arithmetic({'start': 'high', 'downgrades': 2,
            ^^^^^^^^^^^^^^^^^^^^^^^^^
                                       'certainty': 'moderate'})
E           AttributeError: module 'harness.grade' has no attribute 'validate_arithmetic'

tests\test_gs_layers.py:28: AttributeError
=========================== short test summary info ===========================
FAILED tests/test_gs_layers.py::test_unsourced_envelope_refused - ModuleNotFo...
FAILED tests/test_gs_layers.py::test_fragility_direction_plant - ModuleNotFou...
FAILED tests/test_gs_layers.py::test_grade_arithmetic_plant - AttributeError:...
3 failed in 3.44s
```
