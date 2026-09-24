# Model call as a source — design as built (lane `rai`, 2026-09-23)

**What this is.** A way to RECORD a model's answer, REPLAY it byte-for-byte offline, and keep it INERT until a
deterministic verifier and a named human both accept it. It does not make the harness depend on a model. Nothing it
produces can change a served number or satisfy a predicate: no producer imports it (tested over every `harness/*.py`,
`scripts/build_topic.py` and `scripts/reproduce_review.py`), and even a fully countersigned proposal is returned with
`admits_into_build: false`. Connecting a countersigned proposal to the build is a separate, future landing.

## The contract, as the repo states it (the repo wins over any summary)

`outputs/handover/lanes/REPRODUCIBLE_MODEL_CONTRACT.md:3` — Mahmood, 2026-09-16: *"we can use some ai in harness as
long as reproducible."* Six conditions (`:6`–`:11`), and `:26`: *"The rule 'a model never supplies a number' stands."*

The standing instruction in the lane brief — "use a model only where the answer is not in the data" — is the OLD rule
that `:3` says the contract replaces ("looser on placement, tighter on evidence"). Both pilots here are placed where
the rule *cannot* answer: screening judgements the keyword rule makes by presence/veto, and estimand fields the
bundle's regex found no statement for. So the pilots satisfy either reading.

| # | Condition (`REPRODUCIBLE_MODEL_CONTRACT.md`) | Where it is met | Not met / limit |
|---|---|---|---|
| 1 | call is a SOURCE: verbatim prompt, date, funnel, per-record decision + rule id, four states, `RAN_ERROR` ≠ `RAN_ZERO` | `reproducible_ai/model_source.py::build_record` (prompt bytes, timestamps, caller, input digests); queue entries carry the rule decision + rule id; every item of N is listed with a state (`PROPOSED` / `NO_HELD_TEXT` / `RAN_ERROR` / `RESPONSE_NOT_A_CLAIM` / `NOT_YET_CALLED`); an empty answer is `RAN_ERROR` (`model_call_live.call`) | the ledger lives in `registry/model_calls/`, not in `harness/acquisition.py`'s retrieval ledger (that file is certificate-pinned; extending it re-certifies 32 pages) |
| 2 | pinned identity and decoding | record `model.{id_requested,id_reported,provider}`; the call is `RAN_ERROR` when the client reports a different model or effort; `params` lists every parameter set | the client does not expose temperature / top_p / seed or its system instructions; these are listed in `not_controllable`, not invented. `id_reported` is the client's header, not a server attestation |
| 3 | response cached and committed; replay never re-calls | `registry/model_calls/<record_id>.json`, response as base64 inside JSON (immune to `* text=auto eol=lf`); `replay()` re-derives every digest and the content-addressed id | — |
| 4 | rebuild from the protocol SHA is byte-identical | trivially: nothing here enters a page | not exercised — no page reads a proposal in this landing |
| 5 | deterministic post-check; `SPAN_NOT_IN_SOURCE` refuses | `verify_screening` / `verify_estimand` use `scripts/build_bundle.py::locate` (the bundle's own span ladder) and, for estimand, the bundle's own `_ESTIMAND` vocabulary | a located span proves the words are there, not that they mean what the model says — that is what the human signs |
| 6 | disagreement recorded, never resolved silently | `agreement` = `RULE_MODEL_AGREE` / `RULE_MODEL_DISAGREE(rule=…, model=…, adjudication=OWED)` / `MODEL_CANNOT_TELL(…)` / `RULE_SILENT_ON_SPAN(…)`; a non-agreeing proposal **refuses a batch signature** | `ADJUDICATED(by, date)` is the countersignature itself |

## The five things the handover said the design must get right

1. **The record.** Model id requested and reported, provider, every set parameter, the parameters we cannot set,
   exact prompt bytes + sha256, exact response bytes + sha256, request/response UTC, caller (file, line, purpose),
   input digests (held text, topic config, `pico.json`, the output schema, and the user's global `~/.codex/AGENTS.md`
   by digest only). `record_id = "mc-" + sha256(canonical(record without id))[:32]` — editing any field renames it.
2. **Replay.** `replay(record)` returns the stored bytes after checking base64, sha256, length and the id; a
   `RAN_ERROR` record never replays. `reproducible_ai/model_source.py` imports no network or process module (AST
   test); the replay tests run with every credential variable unset and `socket`/`subprocess` replaced by tripwires.
3. **A proposal is not an answer.** `Proposal` is immutable; truth-testing, numeric conversion, indexing,
   iteration, length, formatting, `str`, hashing, comparison, arithmetic, JSON and ANY attribute read raise
   `ProposalNotAdmissible`. Planted into the real consumers — `harness.synth.pool` (the canonical pooling path), a
   `synth.Study` carrying a proposal as a count, and `harness.screen.screen_record` — each raises.
4. **Three conditions, all of them.** `status_of(entry, record, held_text)` is `COUNTERSIGNED` only when (a) the
   verifier, re-run NOW on the held text, passes and equals the stored verdict; (b) the record replays AND the queued
   claim is exactly the claim the stored response decodes to; (c) `harness.result_changes.signature_problem` —
   **reused as-is** — accepts the countersignature over `rendered_sha256(render_proposal_block(...))`, with a
   non-agreement passed as `conclusion_changed` so it accepts `SEEN_AND_SIGNED` only. No sibling was needed: the one
   weakness of that digest (it collapses whitespace) is covered by (b) — a whitespace-only edit of the claim is refused
   as `CLAIM_NOT_THE_RECORDED_ONE` although the signature digest still matches (tested). There is no timeout, no
   default and no "assume accepted"; an `OPEN` signature with an aged queue entry stays `PROPOSED` (tested).
5. **Limits** — below.

## Where the code lives, and why not in `harness/`

Every served `CERTIFICATE.json` carries `certificate_scope.not_covered.in_tree_modules_not_imported_by_any_root`,
computed from `harness/*.py` (`harness/certificate.py:114`). A new module in `harness/` therefore moves the
`release_sha256` of all 32 pages (observed: `tests/test_certificate.py` and `tests/test_certificate_code_closure.py`
went red with the modules in `harness/`, green with them moved). The modules are in a top-level package
`reproducible_ai/` — outside the page code, as `scripts/verify_bundle.py` is — and the placement is made honest by a
test, not by the directory: no `harness/*.py` and neither build entry point imports the package or names the proposal
store, and a plant proves that scan fires. **The certificate's in-tree scan does not see `reproducible_ai/` (nor
`scripts/`)**; that is a scope fact about the certificate, recorded here rather than worked around.

## Limits, plainly

- **The model is not made reproducible.** Only THIS call's recorded output is. Re-asking tomorrow may answer
  differently; the server-side revision behind `gpt-6-astra` is not reported to us. **Measured** (2026-09-24,
  `model_source_pilot.py stability`, identical prompt bytes re-asked, every re-ask a committed record that can never
  become a source): estimand 9 of 9 claims identical; screening, every one of the 269 items re-asked:
  **123 of 269 claims byte-identical** (quote wording varies), 1061 of 1076 axis verdicts and **260 of 269 derived
  decisions** the same. `outputs/model_source/STABILITY_*.json`.
- **So a single call is not enough to batch-sign.** One of the 9 flips (LEADER, PMID 27295427) was an agreement
  with the rule — batch-signable on its source call — that came back CANNOT_TELL on re-ask. Rule: when a recorded
  re-ask of the identical prompt reaches a different derived decision, the item needs an INDIVIDUAL signature. The
  queue computes this from the re-ask records, the signed block shows it, and the gate treats it as binding.
- **The prompt bytes are not the whole context.** The client prepends its own instructions: a 5-word probe prompt
  cost 15,923 input tokens (codex-cli 0.153.4, measured 2026-09-23). The user's `~/.codex/AGENTS.md` is recorded by
  sha256; the client's built-in instructions are named in `not_controllable`.
- **Storage.** Prompt and response are stored as base64 (4·⌈B/3⌉ characters) inside a pretty-printed JSON envelope;
  the per-call cost is measured on the pilot records in the lane report, not estimated here.
- **A lost stored response** means the record cannot replay and its proposals can never be countersigned. The only
  honest recovery is a NEW call under a NEW record id; `write_record` refuses to overwrite a stored record whose
  bytes differ.
- **A signature is a JSON object, not an identity proof.** It records who, when, over which bytes and how the bytes
  reached them; it does not authenticate the signer. The tool that writes it (`scripts/countersign_model_proposal.py`)
  is for the reviewer to run; this lane never runs `sign`.
