# IN4 fail-closed findings

No gate bypass or ratchet acknowledgement. The full standard is recorded in LANE-IN4-REPORT.md and `.tmp/standard-final/`; separate post-repair checks are in `.tmp/followup-final/`.

## Verification boundary

The complete standard measured 1048 tests passed, 26 failed, with 7 of 11 limbs not PASS. Subsequent bounded source fixes restored deterministic rendering and offline replay (32 of 32), removed the legacy-strand gate exception without accepting untyped members, suppressed invalid aggregate GRADE statistics, and inventoried three new gates without inventing validation events. Seventeen targeted tests pass; the full suite was not repeated and is not declared green.

Final follow-up: publication gate executed on all 32 pages, with 0 of 32 passing; index, leak scan and scorecard PASS; search completeness and ratchet REFUSED. Retraction survival remains 32 of 32. Full details and exact refusals are retained in LANE-IN4-REPORT.md and `.tmp/followup-final/limbs.txt`. The all-PASS-except-ratchet finish condition was not attained.

## Search measurement currency

The unchanged search-completeness gate refuses the old engine measurement after integration changed `harness/search_v2.py`. The measured and current blobs are `a57dc45d6824` and `d278c2f7f852` respectively. The run driver requires a new measured search. No network is authorized in this lane; changing the old recorded hash would misrepresent old results as a new measurement. The refusal is retained.

## FACT source contract

The integrated FACT gate refuses legacy pooled rows without its complete held-document provenance. Mechanical coverage currently measures 7 of 135 pooled outcome rows across 32 review pages. In GLP-1 the two non-primary harm rows lack UTC retrieval metadata. The held records and retrieval ledger give `2026-09-11` only; an exact UTC retrieval instant must not be invented. Other pages retain visible UNVERIFIED_FACT marks as required by the protocol-binding contract. Rendering/pooling under a protocol with no binding axes is not a full publication-gate PASS.

Representative verbatim refusal:

```text
L1: UNVERIFIED_FACT PMID 31189511 in 'Gastrointestinal adverse events': missing retrieved_utc in UTC
L1: UNVERIFIED_FACT PMID 27295427 in 'Adverse events leading to discontinuation': missing retrieved_utc in UTC
```

## Unresolved source-reporting harm

```text
L1: HARMS_INCOMPLETE -- Gastrointestinal adverse events: HARMS_INCOMPLETE -- 1 known reported outcome(s) unresolved (FREEDOM-CVO) among 9 source-reporting trial(s); extracted k=1. The page must not render this as harm absence.
```

No missing source value is filled, and this is not relabelled as absent to pass.

## Typed-prose coverage

The final GLP-1 scope scan measures 848 registered of 2,749 visible nonstructural units, with 1,901 SENTENCE_WITHOUT_OBJECT refusals. Much of the new family and statistical-layer rendering is not registered with the CGX whole-page registry. No blanket registration or structural exemption was added. These are real integration coverage debts, not a PASS. Exact units: `.tmp/final-glp1-scope.json`.

## Eligibility discrepancy

The held colchicine protocol retains design/masking eligibility, explicitly excluding open-label END-AF. The measured compatibility primary has k=3 and strict sensitivity k=0. The prompt's historical k=4/k=1 requires a different eligibility decision. This lane does not make that policy change.
