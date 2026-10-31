# P3: trial-level extraction contract (`p3/1.0.0`, opt-in)

Before anything says it **matches a published meta-analysis**, every trial-level value it pools must be:

| | requirement | refused when |
|---|---|---|
| **typed** | a declared field (`fields.py`) of the declared type and range, coherent with its siblings | `42.0` or `True` for a count, events > total, a CI that does not bracket its point, a ratio ≤ 0 |
| **sourced** | carries the exact passage it was read from: verbatim quote + character offsets in a document pinned by sha256 | the document changed, the quote is not at its offsets, or **the value is not in the quote** |
| **dual-read** (OUTCOME fields) | read independently by Claude (anthropic) and Codex (openai), each from the document alone | the readers share a family, one saw the other's answer, they disagree with no adjudication, or the served value differs from what they resolved |

A disagreement is **adjudicated by a verified passage**, not by a vote. The decided value must be in its own quote, and the adjudicator may not be one of the readers.

## Use it (one topic, one lane)
```
# 1. dual reading: two recorded model calls (model_call_record/1)
python -m extraction_contract extract --docs-root <dir> --document <ref> --trial <id> --measure binary|continuous|ratio \
    --claude-model claude-opus-5-5 --codex-model gpt-6-astra --out readings.json --records-out <records dir>
# 2. assemble the bundle (served values + the two readings + any adjudications); schema in gate.py
# 3. the gate: exit 0 ALLOW_MATCH_CLAIM, 1 REFUSE, 2 could not execute (never a pass)
python -m extraction_contract check bundle.json --docs-root <dir> --records <records dir> --out p3_report.json
```
Cite `p3_report.json` (verdict + contract version) beside the claim.

**Authoritative fail-closed rule (29 October 2026):** Without `--records`, the report remains useful for metadata/source diagnostics, but always returns REFUSE and exit code 1. A supplied inventory must contain two independently replayable `model_call_record/1` records; their stored prompt/response bytes, record IDs, model pins, document input digests, trial/measure-specific prompts and reconstructed reading items must agree. Missing/empty/tampered records cannot authorize ALLOW_MATCH_CLAIM. Stored-call replay does **not** independently attest a remote model provider, reproduce a fresh model run, or substitute for external blinded scientific adjudication.
- Only open-licensed documents may be sent. Each prompt passes the repo's licence guard (`reproducible_ai.record_licence`) before any call.
- Committing call records follows the repo's model-output rules (`tests/test_model_inventory.py`).

## Versioning
`extraction_contract.CONTRACT_VERSION`. A bundle naming another major version is refused, never coerced. Breaking changes bump the major; added fields or checks bump the minor.

## Deliberately NOT done here (and why)
- **Not wired into `harness/gate.py` or `g1_status`.** That code is in the certificate closure and owned by running lanes. Wiring P3 in would change every page certificate and force a re-certification. It is a separate, coordinated change once a topic has adopted P3.
- **The package lives outside `harness/`** for the same reason: any new `harness/*.py` changes every certificate's scope. `tests/test_extraction_contract.py` fails if anything under `harness/`, `scripts/` or `docs/` imports it.
- **Tested with fake runners.** The live path was smoke-tested once on a synthetic control document (2026-10-21: claude-opus-5-5 and gpt-6-astra both RAN_OK, pins held, all quotes located verbatim, gate ALLOW). It refused when a field only one reader extracted was served. No records from that run are committed.
